"""data/raw/ → data/export/ : séries horaires nationales (spécification : docs/spike/systeme.md).

Chaîne :

1. éCO2mix (cons-def + temps réel) → série native normalisée (`normaliser_eco2mix`) :
   cast explicite des colonnes typées texte, lignes renseignées seulement,
   dédoublonnage UTC des jours de passage à l'heure d'été, colonne `nature` ;
2. → vue horaire UTC (`vers_horaire`), selon la convention d'horodatage
   `HORODATAGE_ECO2MIX` ; une heure incomplète est laissée vide (pas
   d'imputation) ;
3. prix day-ahead energy-charts → série native (60 puis 15 min) et vue
   horaire (moyenne des quarts d'heure, convention RTE) ;
4. indisponibilités nucléaires déclarées par EDF (REMIT) → puissance nucléaire
   disponible horaire (`pc/remit.py`) ;
5. exports : `systeme_horaire.parquet`, `horaire/AAAA.csv`,
   `prix_quart_horaire.csv`, `meta.json`.

Unités : les colonnes de puissance sont des **MW moyens** sur le pas de
temps. Une heure de MW moyens vaut des MWh (× 1 h) ; une demi-heure, × 0,5 h.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from . import remit
from .sources import (ANNEE_DEBUT, LICENCE_EDF, LICENCE_ODRE, LICENCE_PRIX, fichier, fichier_edf, fichiers_annuels,
                      lire_manifeste)

TZ_PARIS = "Europe/Paris"
DATETIME_UTC = pl.Datetime("us", "UTC")

# --------------------------------------------------------------------------
# Convention d'horodatage éCO2mix
# --------------------------------------------------------------------------

#: Ce que l'horodatage `date_heure` d'un point éCO2mix désigne dans la période qu'il décrit.
#:
#: - `"fin"` : le point horodaté t décrit la période (t − pas, t]. L'heure UTC h = [h, h+1)
#:   est donc la moyenne des points h:30 et h+1:00 (pas de 30 min), ou h:15, h:30, h:45 et
#:   h+1:00 (pas de 15 min) ;
#: - `"debut"` : le point t décrit [t, t + pas) ; l'heure h = points h:00 et h:30.
#:
#: Non documenté par RTE. Établi pour le consolidé et le définitif par le spike
#: (docs/spike/systeme.md, piège 1) et par la contre-vérification
#: (docs/spike/contre-verification.md, tests 1 et 2 : nucléaire ODRÉ « convention débutante »
#: à 0,2 MW près en « fin » contre 258 MW en « début » ; balayage contre energy-charts).
#:
#: Temps réel (15 min) : la spécification RTE parle de « puissance instantanée ». On applique
#: la **même convention par analogie** (le point t représente le quart d'heure (t − 15 min, t]),
#: sans preuve : `pc check` la teste contre `production-nette-nucleaire` sur leur période
#: commune et affiche le résultat (contrôle informatif). La moyenne horaire de quatre valeurs
#: instantanées n'est qu'une approximation de la puissance moyenne de l'heure.
#:
#: C'est le **seul** endroit où la convention intervient : la changer ici suffit.
HORODATAGE_ECO2MIX = "fin"

# Pas natif (minutes) selon la nature des données éCO2mix.
PAS_MIN = {"definitif": 30, "consolide": 30, "temps_reel": 15}

# Libellés ODRÉ → codes courts ; ordre = du plus figé au moins figé.
NATURES = {
    "Données définitives": "definitif",
    "Données consolidées": "consolide",
    "Données temps réel": "temps_reel",
}
RANG_NATURE = {"definitif": 0, "consolide": 1, "temps_reel": 2}

# Colonnes de puissance retenues (MW ; `pompage` négatif ; `ech_physiques` : solde, + = import).
FILIERES = ["fioul", "charbon", "gaz", "nucleaire", "eolien", "solaire", "hydraulique", "bioenergies"]
COLONNES_MW = (
    ["consommation"] + FILIERES + ["pompage", "ech_physiques"]
    + ["ech_comm_angleterre", "ech_comm_espagne", "ech_comm_italie", "ech_comm_suisse",
       "ech_comm_allemagne_belgique"]
    + ["gaz_ccg", "gaz_tac", "gaz_cogen", "gaz_autres",
       "hydraulique_fil_eau_eclusee", "hydraulique_lacs", "hydraulique_step_turbinage"]
)
# Valeurs textuelles admises dans une colonne numérique typée `text` par ODRÉ (→ null).
# Toute autre valeur non numérique fait échouer le cast : on veut le savoir.
MARQUEURS_ABSENCE = ["ND", ""]

# Prix : passage du couplage day-ahead (SDAC) au pas de 15 min, livraison du 2025-10-01
# (00:00 heure de Paris). Sources : NEMO Committee, EPEX SPOT (docs/spike/systeme.md § 4a).
BASCULE_PRIX_15MIN = datetime(2025, 9, 30, 22, 0, tzinfo=timezone.utc)


# --------------------------------------------------------------------------
# Utilitaires d'unités
# --------------------------------------------------------------------------


def mw_vers_mwh(puissance_mw: pl.Expr | float, pas_h: float) -> pl.Expr | float:
    """Énergie (MWh) d'un pas de temps à partir de la puissance **moyenne** (MW) sur ce pas.

    Pas de 30 min → × 0,5 ; pas horaire → × 1. Ne jamais sommer des MW sans ce facteur.
    """
    return puissance_mw * pas_h


def annee_paris(col: str | pl.Expr) -> pl.Expr:
    """Année civile en heure de Paris d'un instant UTC (comme les bilans RTE)."""
    e = pl.col(col) if isinstance(col, str) else col
    return e.dt.convert_time_zone(TZ_PARIS).dt.year()


# --------------------------------------------------------------------------
# éCO2mix
# --------------------------------------------------------------------------


def caster_colonnes(df: pl.DataFrame, colonnes: list[str]) -> pl.DataFrame:
    """Cast explicite en Float64 des colonnes numériques, y compris celles qu'ODRÉ type `text`.

    Les marqueurs d'absence (`ND`, vide) deviennent null ; toute autre valeur non numérique
    lève une erreur (cast strict) plutôt que de disparaître en silence.
    """
    exprs = []
    for c in colonnes:
        if c not in df.columns:
            exprs.append(pl.lit(None, dtype=pl.Float64).alias(c))
        elif df.schema[c] == pl.Utf8:
            s = pl.col(c).str.strip_chars()
            exprs.append(pl.when(s.is_in(MARQUEURS_ABSENCE)).then(None).otherwise(s)
                         .cast(pl.Float64, strict=True).alias(c))
        else:
            exprs.append(pl.col(c).cast(pl.Float64, strict=True))
    return df.with_columns(exprs)


def normaliser_eco2mix(df: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    """Série native normalisée : une ligne par point renseigné, horodatage UTC unique.

    Entrée : lignes brutes d'un export ODRÉ `eco2mix-national-cons-def` ou `-tr`.
    Sortie : `ts_utc`, `nature`, `pas_min`, `taux_co2` (gCO2eq/kWh), colonnes `COLONNES_MW`
    (Float64), triées par `ts_utc`. Rapport : décomptes des lignes écartées.
    """
    rapport = {"lignes_brutes": df.height}
    df = caster_colonnes(df, COLONNES_MW + ["taux_co2"])
    inconnues = set(df["nature"].unique().to_list()) - set(NATURES)
    if inconnues:
        raise ValueError(f"nature éCO2mix inconnue : {inconnues}")
    df = df.with_columns(
        pl.col("nature").replace_strict(NATURES).alias("nature"),
        pl.col("date_heure").dt.convert_time_zone("UTC").cast(DATETIME_UTC).alias("ts_utc"),
    ).with_columns(pl.col("nature").replace_strict(PAS_MIN, return_dtype=pl.Int32).alias("pas_min"))

    # Lignes futures du temps réel et quarts d'heure « prévision seule » du cons-def : vides.
    n = df.height
    df = df.filter(pl.col("consommation").is_not_null())
    rapport["lignes_vides"] = n - df.height
    # Le consolidé et le définitif sont au pas de 30 min : on n'en garde que :00 et :30.
    n = df.height
    df = df.filter((pl.col("pas_min") == 15) | pl.col("ts_utc").dt.minute().is_in([0, 30]))
    rapport["lignes_hors_pas"] = n - df.height

    # Passage à l'heure d'été : ODRÉ convertit les heures locales inexistantes (02:00, 02:30)
    # vers le même instant UTC que 03:00 et 03:30. On garde la ligne dont l'heure locale
    # déclarée correspond à l'instant UTC ; à défaut, la première.
    heure_locale = pl.col("ts_utc").dt.convert_time_zone(TZ_PARIS).dt.strftime("%H:%M")
    df = df.with_columns((pl.col("heure") == heure_locale).alias("_coherente"))
    n = df.height
    df = (df.sort(["ts_utc", "_coherente"], descending=[False, True])
            .unique(subset="ts_utc", keep="first", maintain_order=True))
    rapport["doublons_utc"] = n - df.height
    cols = ["ts_utc", "nature", "pas_min", "taux_co2"] + COLONNES_MW
    return df.select(cols).sort("ts_utc"), rapport


def charger_eco2mix(raw: Path) -> tuple[pl.DataFrame, dict]:
    """cons-def (toutes années) + temps réel, normalisés. En cas de recouvrement, le plus figé gagne."""
    morceaux, rapports = [], {}
    for p in fichiers_annuels(raw, "eco2mix_cons_def"):
        d, r = normaliser_eco2mix(pl.read_parquet(p))
        morceaux.append(d)
        rapports[f"cons_def/{p.stem}"] = r
    tr = fichier(raw, "eco2mix_tr")
    if tr.exists():
        d, r = normaliser_eco2mix(pl.read_parquet(tr))
        morceaux.append(d)
        rapports["tr"] = r
    if not morceaux:
        raise SystemExit("aucune donnée éCO2mix dans data/raw/ : lancer `pc download` d'abord")
    df = pl.concat(morceaux, how="vertical")
    n = df.height
    df = (df.with_columns(pl.col("nature").replace_strict(RANG_NATURE).alias("_rang"))
            .sort(["ts_utc", "_rang"]).unique(subset="ts_utc", keep="first", maintain_order=True)
            .drop("_rang"))
    rapports["recouvrement_natures"] = n - df.height
    return df, rapports


def debut_periode(ts: pl.Expr, pas_min: pl.Expr) -> pl.Expr:
    """Début de la période décrite par un point éCO2mix, selon `HORODATAGE_ECO2MIX`."""
    if HORODATAGE_ECO2MIX == "fin":
        return ts - pl.duration(minutes=pas_min)
    if HORODATAGE_ECO2MIX == "debut":
        return ts
    raise ValueError(HORODATAGE_ECO2MIX)


def vers_horaire(natif: pl.DataFrame, colonnes: list[str] | None = None) -> pl.DataFrame:
    """Vue horaire UTC d'une série éCO2mix native normalisée.

    Chaque point couvre `pas_min` minutes ; l'heure `heure_utc` = [h, h+1) reçoit les points
    dont la période commence dans [h, h+1) (`debut_periode`). Valeur = moyenne pondérée par la
    durée (MW moyens sur l'heure = MWh de l'heure). Une heure n'est renseignée, colonne par
    colonne, que si les points non nuls couvrent les 60 minutes : sinon null (heure manquante
    du passage à l'heure d'hiver, raccord définitif/consolidé…), jamais imputée.

    `taux_co2` est pondéré par la production (Σ filières), pas moyenné simplement.
    `nature` : la moins figée des natures de l'heure. `couverture_min` : minutes couvertes.
    """
    colonnes = colonnes or COLONNES_MW
    d = natif.with_columns(
        debut_periode(pl.col("ts_utc"), pl.col("pas_min")).dt.truncate("1h").alias("heure_utc"),
        pl.sum_horizontal(FILIERES).alias("_production"),
        pl.col("nature").replace_strict(RANG_NATURE).alias("_rang"),
    )
    pas = pl.col("pas_min")

    def moyenne(c: str) -> pl.Expr:
        couvert = (pl.col(c).is_not_null().cast(pl.Int32) * pas).sum()
        return pl.when(couvert == 60).then((pl.col(c) * pas).sum() / 60).otherwise(None).alias(c)

    poids = pl.col("_production") * pas
    co2_couvert = (pl.col("taux_co2").is_not_null() & pl.col("_production").is_not_null()).cast(pl.Int32) * pas
    h = d.group_by("heure_utc").agg(
        pas.sum().alias("couverture_min"),
        pl.col("_rang").max().alias("_rang"),
        *[moyenne(c) for c in colonnes],
        pl.when(co2_couvert.sum() == 60)
          .then((pl.col("taux_co2") * poids).sum() / poids.sum()).otherwise(None).alias("taux_co2"),
    )
    inverse = {v: k for k, v in RANG_NATURE.items()}
    return (h.with_columns(pl.col("_rang").replace_strict(inverse, return_dtype=pl.Utf8).alias("nature"))
             .drop("_rang").sort("heure_utc"))


# --------------------------------------------------------------------------
# Prix day-ahead
# --------------------------------------------------------------------------


def prix_depuis_json(documents: list[dict]) -> pl.DataFrame:
    """Série native des prix : `debut_utc` (début de période), `pas_min` (60 ou 15), `prix_eur_mwh`."""
    morceaux = [pl.DataFrame({"t": d["unix_seconds"], "prix_eur_mwh": d["price"]},
                             schema={"t": pl.Int64, "prix_eur_mwh": pl.Float64})
                for d in documents if d.get("unix_seconds")]
    df = (pl.concat(morceaux) if morceaux else pl.DataFrame(schema={"t": pl.Int64, "prix_eur_mwh": pl.Float64}))
    df = (df.with_columns(pl.from_epoch("t", time_unit="s").dt.replace_time_zone("UTC").cast(DATETIME_UTC).alias("debut_utc"))
            .unique(subset="debut_utc", keep="last").sort("debut_utc"))
    return df.select(
        "debut_utc",
        pl.when(pl.col("debut_utc") >= BASCULE_PRIX_15MIN).then(15).otherwise(60).cast(pl.Int32).alias("pas_min"),
        "prix_eur_mwh",
    )


def prix_horaire(natif: pl.DataFrame) -> pl.DataFrame:
    """Vue horaire UTC des prix : moyenne simple des quarts d'heure de l'heure (convention RTE,
    BE2025 note 10), ou la valeur horaire avant le 2025-10-01. Heure incomplète → null.

    Colonnes : `heure_utc`, `prix_eur_mwh`, `quarts_negatifs` (nombre de valeurs natives < 0
    dans l'heure : l'heure masque des quarts d'heure négatifs).
    """
    pas = pl.col("pas_min")
    couvert = (pl.col("prix_eur_mwh").is_not_null().cast(pl.Int32) * pas).sum()
    return (natif.group_by(pl.col("debut_utc").dt.truncate("1h").alias("heure_utc"))
                 # Arrondi à 4 décimales (exact pour une moyenne de 4 prix au centime) puis + 0.0 :
                 # supprime le bruit flottant et le zéro négatif (−0.0), qui faisait passer pour
                 # négative une heure de moyenne nulle (signalé par l'agent du site, 2026-11-26).
                 .agg(pl.when(couvert == 60).then(pl.col("prix_eur_mwh").mean().round(4) + 0.0).otherwise(None)
                        .alias("prix_eur_mwh"),
                      (pl.col("prix_eur_mwh") < 0).sum().cast(pl.Int32).alias("quarts_negatifs"))
                 .sort("heure_utc"))


def heures_negatives(prix_h: pl.DataFrame) -> dict[int, int]:
    """Nombre d'heures à prix horaire strictement négatif par année civile (heure de Paris)."""
    r = (prix_h.filter(pl.col("prix_eur_mwh") < 0)
               .group_by(annee_paris("heure_utc").alias("annee")).len().sort("annee"))
    return {int(a): int(n) for a, n in r.iter_rows()}


def charger_prix(raw: Path) -> pl.DataFrame:
    return prix_depuis_json([json.loads(p.read_text()) for p in fichiers_annuels(raw, "prix_fr")])


# --------------------------------------------------------------------------
# Assemblage et exports
# --------------------------------------------------------------------------

# CSV annuels du site : (colonne source, en-tête, décimales).
COLONNES_CSV = [
    ("consommation", "consommation", 0),
    ("nucleaire", "nucleaire", 0),
    ("nucleaire_disponible", "nucleaire_disponible", 0),
    ("eolien", "eolien", 0),
    ("solaire", "solaire", 0),
    ("hydraulique", "hydraulique", 0),
    ("gaz", "gaz", 0),
    ("ech_physiques", "solde_echanges", 0),
    ("pompage", "pompage", 0),
    ("prix_eur_mwh", "prix", 4),  # moyenne de quarts d'heure au centime : exacte à 4 décimales
    ("taux_co2", "taux_co2", 1),
]


def grille_horaire(debut: datetime, fin: datetime) -> pl.DataFrame:
    return pl.DataFrame({"heure_utc": pl.datetime_range(debut, fin, "1h", time_zone="UTC", eager=True)
                                      .cast(DATETIME_UTC)})


def debut_grille() -> datetime:
    """Première heure UTC de la grille : 1er janvier de `ANNEE_DEBUT`, 00:00 heure de Paris."""
    return pl.Series([datetime(ANNEE_DEBUT, 1, 1)]).dt.replace_time_zone(TZ_PARIS).dt.convert_time_zone("UTC")[0]


def assembler(eco_h: pl.DataFrame, prix_h: pl.DataFrame, nuc_h: pl.DataFrame | None = None) -> pl.DataFrame:
    """Table horaire complète (grille sans trou depuis le 1er janvier de la première année, heure
    de Paris) : éCO2mix horaire + prix horaire + nucléaire disponible déclaré (REMIT). Les heures
    sans donnée restent présentes, vides."""
    debut = debut_grille()
    fin = max(eco_h["heure_utc"].max(), prix_h["heure_utc"].max())
    g = grille_horaire(debut, fin)
    if nuc_h is None:
        nuc_h = pl.DataFrame(schema={"heure_utc": DATETIME_UTC, "nucleaire_disponible": pl.Float64,
                                     "nucleaire_puissance_max": pl.Float64})
    t = (g.join(eco_h, on="heure_utc", how="left")
          .join(prix_h.select("heure_utc", "prix_eur_mwh", "quarts_negatifs"), on="heure_utc", how="left")
          .join(nuc_h.select("heure_utc", "nucleaire_disponible", "nucleaire_puissance_max"), on="heure_utc",
                how="left"))
    cols_mw = [c for c in COLONNES_MW if c in t.columns]
    cols_nuc = ["nucleaire_disponible", "nucleaire_puissance_max"]
    return t.select(
        "heure_utc", "nature", *cols_mw, *cols_nuc, "taux_co2", "prix_eur_mwh", "quarts_negatifs",
        pl.col("couverture_min").fill_null(0).cast(pl.Int32),
    ).with_columns([pl.col(c).round(1) for c in cols_mw + cols_nuc + ["taux_co2"]]
                   + [pl.col("prix_eur_mwh").round(4)])


def nucleaire_disponible(raw: Path, fin: datetime) -> tuple[pl.DataFrame | None, dict]:
    """Série nationale REMIT (`remit.serie_nationale`) sur la grille, et ses métadonnées.

    Absente (source non téléchargée) : None, avec un avertissement ; `pc check` échoue alors.
    """
    if not fichier_edf(raw, "historique").exists():
        print("AVERTISSEMENT : data/raw/edf_remit/ absent (`pc download edf_remit`) : "
              "nucleaire_disponible reste vide", file=sys.stderr)
        return None, {}
    brut, ev, bornes = remit.depuis_raw(raw)
    horizon = min(bornes["horizon"], fin + timedelta(hours=1))
    par_tranche = remit.disponible_horaire(ev, debut_grille(), horizon)
    nat = remit.national(par_tranche).rename({"nucleaire_pmax": "nucleaire_puissance_max"})
    taux = remit.taux_annuels(par_tranche, remit.HORS_TAUX_RTE)
    info = {
        "evenements_retenus": ev.height,
        "tranches": sorted(ev["tranche"].unique().to_list()),
        "fin_historique_utc": bornes["fin_historique"].isoformat(),
        "debut_liste_courante_utc": bornes["debut_courante"].isoformat() if bornes["debut_courante"] else None,
        "trou_entre_fichiers": bornes["trou"],
        "derniere_heure_utc": (horizon - timedelta(hours=1)).isoformat(),
        "taux_disponibilite_hors_flamanville3": {
            int(a): round(float(x) * 100, 2) for a, x, h in taux.iter_rows() if h >= 8760},
    }
    return nat, info


def _fmt_heure(col: str) -> pl.Expr:
    return pl.col(col).dt.convert_time_zone("UTC").dt.strftime("%Y-%m-%dT%H:%MZ")


def ecrire_csv_annuels(table: pl.DataFrame, dossier: Path) -> dict[int, dict]:
    """Un CSV par année civile (heure de Paris), colonnes arrondies. Renvoie un résumé par année."""
    dossier.mkdir(parents=True, exist_ok=True)
    for ancien in dossier.glob("[0-9][0-9][0-9][0-9].csv"):
        ancien.unlink()
    t = table.with_columns(annee_paris("heure_utc").alias("annee"))
    resume = {}
    for (annee,), d in t.group_by("annee", maintain_order=True):
        sortie = d.select(
            _fmt_heure("heure_utc").alias("heure_utc"),
            *[(pl.col(src).round(dec).cast(pl.Int64) if dec == 0 else pl.col(src).round(dec)).alias(nom)
              for src, nom, dec in COLONNES_CSV],
        )
        sortie.write_csv(dossier / f"{annee}.csv", null_value="")
        natures = {str(k): int(v) for k, v in d.drop_nulls("nature").group_by("nature").len().sort("nature").iter_rows()}
        resume[int(annee)] = {
            "heures": d.height,
            "natures": natures,
            "premiere_heure_utc": d["heure_utc"].min().isoformat(),
            "derniere_heure_utc": d["heure_utc"].max().isoformat(),
        }
    return dict(sorted(resume.items()))


#: Description de la série `nucleaire_disponible` pour meta.json (méthode : pc/remit.py).
NUCLEAIRE_DISPONIBLE_META = {
    "definition": "puissance nucléaire disponible déclarée par EDF au titre de REMIT, MW moyens sur l'heure UTC, "
                  "somme des tranches en exploitation (Flamanville 3 comprise à partir du 18/12/2024 13:50)",
    "source": "EDF, indisponibilités des moyens de production d'EDF SA (REMIT), opendata.edf.fr (data-fair) : "
              "historique depuis 2015 + liste courante ; tranches nucléaires françaises seulement (le jeu contient "
              "aussi des unités belges de Luminus, sans nucléaire)",
    "methode": [
        "dernière version de chaque événement Planifié ou Fortuit ; retenu si elle est Active (annulées et "
        "supprimées écartées, sauf une suppression documentée : Golfech 1, 15/08-12/12/2020, voir remit.py)",
        "chroniques PMIN et aFRR ignorées (ce ne sont pas des indisponibilités)",
        "superposition d'événements : puissance disponible minimale (règle d'EDF) ; hors événement : puissance "
        "maximale déclarée de la tranche",
        "moyenne exacte sur l'heure (escalier intégré, pas d'échantillonnage)",
        "Fessenheim 1 et 2 comptées jusqu'à leur arrêt définitif (22/02/2020 02:00 et 29/06/2020 23:30, heure de "
        "Paris, fin de leur dernier événement REMIT) ; Flamanville 3 à partir de son premier événement REMIT",
        "dates REMIT lues en heure de Paris (testé par `pc check` : chute de production éCO2mix à l'heure "
        "déclarée des arrêts fortuits, hiver comme été ; aucune heure inexistante du passage à l'heure d'été)",
    ],
    "limites": [
        "puissance DÉCLARÉE disponible, pas une capacité physique garantie : réserves pour services système, "
        "modulation économique et baisses non déclarées n'y figurent pas",
        "la production peut dépasser le disponible déclaré : surcroît de puissance nette par eau froide en hiver "
        "(jusqu'à environ 2 % du parc), déclarations en escalier (grèves, essais) alors que la puissance varie "
        "en rampe ; voir `pc check`",
        "frontière modulation / indisponibilité fixée par EDF et invisible de l'extérieur (RTE, BE2025, fig. 2.5)",
        "les dernières heures reflètent les déclarations au moment de l'extraction, révisables ; aucune heure "
        "postérieure à l'extraction de la liste courante (pas de prévision)",
        "l'historique n'est publié que par exports ponctuels (trimestriels) : si la liste courante (trois mois "
        "glissants) ne remonte plus jusqu'à cet export, des événements manquent (`pc check` le détecte)",
        "heure répétée du passage à l'heure d'hiver : ambiguë dans la source, lue comme la première (heure d'été)",
    ],
    "unites": "MW moyens sur l'heure (= MWh de l'heure)",
    "nucleaire_puissance_max": "somme des puissances maximales déclarées des tranches en exploitation (MW moyens "
                               "sur l'heure) : dénominateur d'un taux de disponibilité",
}


LISEZMOI_HORAIRE = """\
# Séries horaires nationales — un fichier par année

Un fichier `AAAA.csv` par **année civile en heure de Paris** (comme les bilans RTE) :
le fichier 2024 commence à `2023-12-31T23:00Z`. Généré par `pc build` ; ne pas
modifier à la main. Métadonnées (dates d'extraction, natures, licences) :
`../meta.json`.

| Colonne | Unité | Définition |
|---|---|---|
| `heure_utc` | ISO 8601, UTC | **début** de l'heure décrite : `2024-06-01T10:00Z` = de 10:00 à 11:00 UTC |
| `consommation` | MW moyen sur l'heure | consommation France continentale **hors Corse**, pertes comprises, pompage exclu (éCO2mix) |
| `nucleaire` | MW moyen | production nucléaire |
| `nucleaire_disponible` | MW moyen | puissance nucléaire **disponible déclarée** par EDF au titre de REMIT (somme des tranches en exploitation, Flamanville 3 comprise depuis le 18/12/2024) ; ce n'est **pas** une production. Voir la note ci-dessous |
| `eolien` | MW moyen | production éolienne (terrestre + en mer) |
| `solaire` | MW moyen | production photovoltaïque |
| `hydraulique` | MW moyen | production hydraulique (dont turbinage des STEP) |
| `gaz` | MW moyen | production des centrales au gaz |
| `solde_echanges` | MW moyen | solde des échanges physiques ; **positif = import**, négatif = export (`ech_physiques`) |
| `pompage` | MW moyen | consommation des STEP en pompage, **négative** |
| `prix` | EUR/MWh | prix day-ahead zone France ; après le 2025-10-01, moyenne simple des 4 quarts d'heure (convention RTE) |
| `taux_co2` | gCO2eq/kWh | intensité **moyenne de la production** française (émissions directes, imports exclus), moyenne des demi-heures pondérée par la production. **Pas un facteur marginal**, pas l'intensité de la consommation |

- Une puissance moyenne horaire en MW vaut l'énergie de l'heure en MWh (× 1 h) :
  pour un total annuel en TWh, sommer la colonne et diviser par 10⁶.
- Cellule vide = donnée absente, **jamais imputée** : heure répétée du passage à
  l'heure d'hiver (absente des fichiers RTE), raccord entre deux natures de
  données, heures pas encore publiées.
- Arrondis : MW à l'unité, prix à 4 décimales (moyenne exacte de 4 quarts d'heure au centime ; une heure négative s'écrit donc avec son signe, jamais `-0.0`), `taux_co2` au dixième.
- Les autres filières (charbon, fioul, bioénergies), les échanges commerciaux par
  frontière et les sous-filières sont dans `../systeme_horaire.parquet`.
- Agrégation horaire de l'éCO2mix : un point horodaté t décrit la demi-heure
  **qui se termine** à t (convention établie empiriquement, non documentée par
  RTE) ; l'heure h est la moyenne des points h:30 et h+1:00. Au pas de 15 min
  (données temps réel), même convention : points h:15, h:30, h:45, h+1:00.
- `nucleaire_disponible` : reconstruit depuis les indisponibilités REMIT d'EDF
  (opendata.edf.fr, Licence Ouverte 2.0). Pour chaque tranche, dernière version
  active des arrêts et limitations planifiés ou fortuits ; si plusieurs se
  superposent, la puissance disponible la plus faible (règle d'EDF) ; sinon la
  puissance maximale. Moyenne exacte sur l'heure. Dates de la source lues en
  heure de Paris (vérifié). Vide après l'heure d'extraction (pas de prévision).
  La production peut le dépasser de quelques centaines de MW (eau froide en
  hiver, déclarations en escalier pendant les grèves ou les essais). Méthode,
  limites et taux annuels : `../meta.json`, clé `nucleaire_disponible`.
- Les données de l'année en cours mêlent **consolidé** et **temps réel**
  (puissance instantanée, moins précise) : voir `natures` dans `../meta.json`.
"""


def build(raw: Path, export: Path) -> None:
    export.mkdir(parents=True, exist_ok=True)
    eco, rapports = charger_eco2mix(raw)
    print(f"éCO2mix natif : {eco.height} points, {eco['ts_utc'].min()} → {eco['ts_utc'].max()}", file=sys.stderr)
    eco_h = vers_horaire(eco)
    prix = charger_prix(raw)
    prix_h = prix_horaire(prix)
    fin = max(eco_h["heure_utc"].max(), prix_h["heure_utc"].max())
    nuc_h, nuc_info = nucleaire_disponible(raw, fin)
    table = assembler(eco_h, prix_h, nuc_h)

    table.write_parquet(export / "systeme_horaire.parquet", compression="zstd", compression_level=19)
    resume = ecrire_csv_annuels(table, export / "horaire")
    (export / "horaire" / "LISEZMOI.md").write_text(LISEZMOI_HORAIRE)

    qh = prix.filter(pl.col("pas_min") == 15)
    qh.select(_fmt_heure("debut_utc").alias("debut_utc"), pl.col("prix_eur_mwh").round(2)).write_csv(
        export / "prix_quart_horaire.csv", null_value="")

    manifeste = lire_manifeste(raw)
    meta = {
        "genere_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "conventions": {
            "heure_utc": "début de l'heure décrite, UTC ; années civiles en heure de Paris",
            "horodatage_eco2mix": HORODATAGE_ECO2MIX,
            "horodatage_eco2mix_detail": (
                "un point éCO2mix horodaté t décrit la période qui se termine à t ; heure h = moyenne "
                "des points h:30 et h+1:00 (30 min) ou h:15…h+1:00 (15 min, temps réel, par analogie, "
                "valeurs instantanées)"),
            "unites": "puissances en MW moyens sur l'heure (= MWh de l'heure) ; prix en EUR/MWh ; "
                      "taux_co2 en gCO2eq/kWh (intensité moyenne de la production, pas marginale)",
            "heures_incompletes": "laissées vides, jamais imputées",
            "prix_horaire": "moyenne simple des quarts d'heure après le 2025-10-01 (convention RTE)",
            "perimetre": "France continentale hors Corse (éCO2mix national)",
        },
        "natures": {
            "definitif": "Données définitives (comptages, MW moyens par demi-heure)",
            "consolide": "Données consolidées (comptages, MW moyens par demi-heure), révisables",
            "temps_reel": "Données temps réel (télé-informations et estimations, puissance instantanée "
                          "au pas de 15 min), remplacées par le consolidé dans les mois suivants",
        },
        "annees": resume,
        "couverture": {
            "eco2mix": {"debut_utc": eco["ts_utc"].min().isoformat(), "fin_utc": eco["ts_utc"].max().isoformat()},
            "prix": {"debut_utc": prix["debut_utc"].min().isoformat(), "fin_utc": prix["debut_utc"].max().isoformat(),
                     "premier_quart_heure_utc": BASCULE_PRIX_15MIN.isoformat()},
        },
        "normalisation_eco2mix": rapports,
        "nucleaire_disponible": {**NUCLEAIRE_DISPONIBLE_META, **nuc_info,
                                 "extractions": {k: {c: v.get(c) for c in ("extrait_le", "mis_a_jour_source",
                                                                           "fichier_source", "url")}
                                                 for k, v in manifeste.items() if k.startswith("edf_remit/")}},
        "attributions": [
            {"donnees": "consommation, production, échanges, taux_co2", **LICENCE_ODRE},
            {"donnees": "prix day-ahead France", **LICENCE_PRIX},
            {"donnees": "nucleaire_disponible, nucleaire_puissance_max", **LICENCE_EDF},
        ],
        "sources": {k: {c: v[c] for c in ("url", "extrait_le", "nature", "sha256", "lignes", "natures",
                                          "mis_a_jour_source", "fichier_source")
                        if c in v} for k, v in sorted(manifeste.items())},
        "fichiers": {
            "systeme_horaire.parquet": "toutes années, toutes colonnes (MW moyens horaires, prix, taux_co2, nature, "
                                       "nucleaire_disponible, nucleaire_puissance_max)",
            "horaire/AAAA.csv": "colonnes principales par année civile (heure de Paris), voir horaire/LISEZMOI.md",
            "prix_quart_horaire.csv": "prix day-ahead natifs au pas de 15 min depuis le 2025-10-01 (début de période, UTC)",
        },
    }
    (export / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    taille = sum(p.stat().st_size for p in export.rglob("*") if p.is_file())
    print(f"exports : {table.height} heures, {len(resume)} années, {taille / 1e6:.1f} Mo dans {export}",
          file=sys.stderr)

