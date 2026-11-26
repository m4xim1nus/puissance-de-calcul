"""ENTSO-E : XML bruts (data/raw/entsoe/) → séries normalisées et vue horaire (data/derive/entsoe/).

Appelé par `pc build` si `data/raw/entsoe/` existe ; sinon ignoré (le reste du build n'en
dépend pas). Rapport : docs/spike/entsoe-pipeline.md.

**Pourquoi `data/derive/` et pas `data/export/`** : aucune page du site ne lit ces données
pour l'instant ; la vue horaire (≈ 150 colonnes × 104 000 heures) pèserait à elle seule
plusieurs fois la marge restante sous la limite de 15 Mo des exports versionnés
(`tests/test_donnees.py`) ; et la licence d'une partie des données (prix, production,
charge) n'est pas CC BY 4.0 (voir `entsoe.LICENCES`). `data/derive/` n'est pas versionné ;
il se régénère par `pc build` depuis `data/raw/` (qui demande le jeton pour être
téléchargé). Quand une page en aura besoin, on exportera un agrégat propre à la page,
comme `quand.json`.

Sorties :

- `natif.parquet` : une ligne par point publié ou répété (A03), au pas natif ;
- `horaire.parquet` : une colonne par série, heure UTC de début (`heure_utc`), MW moyens
  sur l'heure ou EUR/MWh (moyenne des quarts d'heure) ; heure incomplète → vide ;
- `meta.json` : définitions des colonnes, unités, règles de lecture, rapport de
  normalisation, licences, extractions.
"""

from __future__ import annotations

import json
import multiprocessing
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from . import entsoe

DATETIME_UTC = pl.Datetime("us", "UTC")

#: Codes de filière ENTSO-E (psrType) → libellé.
FILIERES = {
    "B01": "biomasse", "B02": "lignite", "B03": "gaz de houille", "B04": "gaz", "B05": "houille",
    "B06": "fioul", "B07": "schiste bitumineux", "B08": "tourbe", "B09": "géothermie",
    "B10": "hydraulique STEP", "B11": "hydraulique fil de l'eau et éclusée", "B12": "hydraulique réservoir (lacs)",
    "B13": "marin", "B14": "nucléaire", "B15": "autres renouvelables", "B16": "solaire", "B17": "déchets",
    "B18": "éolien en mer", "B19": "éolien terrestre", "B20": "autres", "B25": "stockage",
}

#: Colonnes texte en `Enum` (valeurs connues d'avance) : mémoire et tris de 24 millions de lignes
#: raisonnables (≈ 1 Go au lieu de 14), et une valeur imprévue (psrType inconnu…) fait échouer le cast.
ENUM_CLE = pl.Enum(list(entsoe.CLES))
ENUM_SERIE = pl.Enum(sorted({s.nom for v in entsoe.CATALOGUE.values() for s in v}))
ENUM_FILIERE = pl.Enum(list(FILIERES))
ENUM_SENS = pl.Enum(["production", "consommation"])
ENUM_UNITE = pl.Enum(["MW", "EUR/MWh", "GBP/MWh"])
SCHEMA_NATIF = {
    "cle": ENUM_CLE, "serie": ENUM_SERIE, "filiere": ENUM_FILIERE, "sens": ENUM_SENS, "debut_utc": DATETIME_UTC,
    "pas_min": pl.Int16, "valeur": pl.Float64, "publie": pl.Boolean, "unite": ENUM_UNITE, "annee_fichier": pl.Int16,
}
CLES_SERIE = ["cle", "serie", "filiere", "sens"]


# --------------------------------------------------------------------------
# Un fichier → lignes normalisées
# --------------------------------------------------------------------------


def _unite(cle: str, meta: dict) -> str:
    if cle == "entsoe_prix":
        devise, mesure = meta.get("currency_Unit.name"), meta.get("price_Measure_Unit.name")
        if mesure != "MWH" or devise not in ("EUR", "GBP"):
            raise ValueError(f"unité de prix inattendue : {devise}/{mesure}")
        return f"{devise}/MWh"
    if meta.get("quantity_Measure_Unit.name") != "MAW":
        raise ValueError(f"unité inattendue : {meta.get('quantity_Measure_Unit.name')}")
    return "MW"


def _sequence(meta: dict) -> str | None:
    return meta.get("classificationSequence_AttributeInstanceComponent.position") or None


def selection_sdac(d: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    """Prix A44 : ne garder, à chaque instant, que le prix du couplage day-ahead (SDAC).

    Plusieurs TimeSeries peuvent couvrir le même instant, distinguées par
    `classificationSequence_AttributeInstanceComponent.position` (colonne `sequence` ; constaté le
    2026-11-26) :
    - ES depuis le 05/09/2025 : une série **sans** séquence, égale au prix ES d'energy-charts (écart nul
      les 02/11/2025 et 03/01/2026), et des séquences 1, 2, 3 qui s'en écartent de 9 à 55 EUR/MWh (la 3
      ne couvre que 12:00-24:00, heure de Madrid : enchères infrajournalières, identification non
      documentée par ENTSO-E) ;
    - DE-LU depuis 2018 : séquences 1 et 2, sans série non classée ; la 1 égale le prix DE-LU
      d'energy-charts (écart nul les 11/03/2024 et 16/11/2026), la 2 s'en écarte de 38 à 125 EUR/MWh.
    Règle : à chaque instant, la série sans séquence si elle existe, sinon la séquence 1 ; les autres sont
    écartées (comptées). La comparaison se fait par quart d'heure couvert (un point PT60M non classé
    couvre quatre quarts d'une séquence 1 au pas de 15 min). Un instant couvert seulement par des
    séquences ≥ 2 n'a pas de prix SDAC : écarté.
    """
    sans = d.filter(pl.col("sequence").is_null())
    couverts = (sans.select(pl.datetime_ranges(pl.col("debut_utc"),
                                               pl.col("debut_utc") + pl.duration(minutes=pl.col("pas_min") - 15),
                                               "15m").alias("q")).explode("q").unique())
    un = d.filter(pl.col("sequence") == "1").join(couverts, left_on="debut_utc", right_on="q", how="anti")
    garde = pl.concat([sans, un])
    ecartes = d.join(garde.select("ts", "debut_utc"), on=["ts", "debut_utc"], how="anti")
    return garde, {"sequences_ecartees": ecartes["ts"].n_unique(), "points_sequences_ecartees": ecartes.height}


def normaliser_document(doc: dict, cle: str, serie: str, annee: int) -> tuple[pl.DataFrame, dict]:
    """Lignes normalisées d'un document lu par `entsoe.lire_document` ; rapport (séquences écartées)."""
    series = doc["series"]
    rapport = {"series": len(series), "sequences_ecartees": 0, "points_sequences_ecartees": 0}
    meta = []
    for i, ts in enumerate(series):
        m = ts["meta"]
        filiere = sens = None
        if cle == "entsoe_production":
            filiere = m.get("psrType") or None
            if "inBiddingZone_Domain.mRID" in m:
                sens = "production"
            elif "outBiddingZone_Domain.mRID" in m:
                sens = "consommation"
            else:
                raise ValueError("A75 sans inBiddingZone ni outBiddingZone")
        meta.append((i, _sequence(m), filiere, sens, _unite(cle, m)))
    M = pl.DataFrame(meta, schema={"ts": pl.Int32, "sequence": pl.Utf8, "filiere": pl.Utf8, "sens": pl.Utf8,
                                   "unite": pl.Utf8}, orient="row")
    d = entsoe.deplier(series).join(M, on="ts", how="left")
    if cle == "entsoe_prix":
        d, r = selection_sdac(d)
        rapport.update(r)
    d = d.with_columns(pl.lit(cle).alias("cle"), pl.lit(serie).alias("serie"),
                       pl.lit(annee, pl.Int16).alias("annee_fichier"))
    return d.select([pl.col(c).cast(t, strict=True) for c, t in SCHEMA_NATIF.items()]), rapport


def lire_fichier(args: tuple) -> tuple[pl.DataFrame, dict]:
    """(chemin, clé, série, année) → (lignes, rapport). Exécuté dans un processus fils."""
    chemin, cle, serie, annee = args
    doc = entsoe.lire_document(chemin)
    df, rapport = normaliser_document(doc, cle, serie, annee)
    rapport["vide"] = doc["vide"] if not doc["series"] else None
    return df, rapport


def fichiers_bruts(raw: Path) -> list[tuple]:
    """Fichiers présents dans data/raw/entsoe/, rangés par (clé, série, année)."""
    out = []
    for cle in entsoe.CLES:
        for p in sorted((raw / "entsoe" / cle).glob("*/[0-9][0-9][0-9][0-9].xml.gz")):
            out.append((p, cle, p.parent.name, int(p.name[:4])))
    return out


# --------------------------------------------------------------------------
# Règles sur l'ensemble
# --------------------------------------------------------------------------


def ramener_quarts_repetes(df: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    """Prix publiés en PT15M avant la bascule SDAC (01/10/2025 00:00 Paris) : une heure dont les quatre
    quarts sont présents et égaux devient un point horaire ; sinon les quarts restent et sont comptés."""
    est = ((pl.col("cle") == "entsoe_prix") & (pl.col("pas_min") == 15)
           & (pl.col("debut_utc") < entsoe.BASCULE_SDAC_15MIN))
    autres = df.filter(pl.col("cle") != "entsoe_prix")  # seuls les prix sont concernés : on travaille à part
    df = df.filter(pl.col("cle") == "entsoe_prix")
    cand = df.filter(est).with_columns(pl.col("debut_utc").dt.truncate("1h").alias("_h"))
    if cand.height == 0:
        return pl.concat([autres, df]), {"heures_ramenees": 0, "heures_quarts_differents": 0}
    g = cand.group_by(CLES_SERIE + ["_h"]).agg(
        pl.len().alias("n"), pl.col("valeur").n_unique().alias("k"), pl.col("valeur").first(),
        pl.col("publie").any(), pl.col("unite").first(), pl.col("annee_fichier").max())
    egales = g.filter((pl.col("n") == 4) & (pl.col("k") == 1))
    horaires = egales.select(*CLES_SERIE, pl.col("_h").alias("debut_utc"), pl.lit(60, pl.Int16).alias("pas_min"),
                             "valeur", "publie", "unite", "annee_fichier").select(list(SCHEMA_NATIF))
    a_retirer = egales.select(*CLES_SERIE, "_h")
    reste = (df.with_columns(pl.col("debut_utc").dt.truncate("1h").alias("_h"), est.alias("_est"))
               .join(a_retirer.with_columns(pl.lit(True).alias("_ret")), on=CLES_SERIE + ["_h"], how="left",
                     nulls_equal=True)
               .filter(~(pl.col("_est") & pl.col("_ret").fill_null(False)))
               .drop("_h", "_est", "_ret"))
    differentes = g.filter(~((pl.col("n") == 4) & (pl.col("k") == 1)))
    rapport = {
        "heures_ramenees": egales.height,
        "heures_ramenees_par_serie": {f"{s}": int(n) for s, n in
                                      egales.group_by("serie").len().sort("serie").iter_rows()},
        "jours_ramenes_par_serie": {
            str(srie): {"jours": int(n), "premier": str(a), "dernier": str(b)}
            for srie, n, a, b in egales.with_columns(pl.col("_h").dt.convert_time_zone("Europe/Paris").dt.date()
                                                     .alias("_j"))
                                       .group_by("serie").agg(pl.col("_j").n_unique().alias("n"),
                                                              pl.col("_j").min().alias("a"),
                                                              pl.col("_j").max().alias("b")).sort("serie").iter_rows()},
        "heures_quarts_differents": differentes.height,
        "heures_quarts_differents_par_serie": {f"{s}": int(n) for s, n in
                                               differentes.group_by("serie").len().sort("serie").iter_rows()},
    }
    return pl.concat([autres, reste, horaires]), rapport


def dedoublonner(df: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    """Un (série, filière, sens, instant) lu deux fois : on garde le fichier le plus récent ; on compte les
    conflits (valeurs différentes)."""
    cle = CLES_SERIE + ["debut_utc"]
    df = df.sort(cle + ["annee_fichier"], nulls_last=True)
    meme = pl.all_horizontal([pl.col(c).eq_missing(pl.col(c).shift(1)) for c in cle])
    df = df.with_columns(meme.fill_null(False).alias("_dup"))
    suivant = pl.col("_dup").shift(-1).fill_null(False)
    dup = df.filter(pl.col("_dup") | suivant)
    conflits = (dup.group_by(cle).agg(pl.col("valeur").n_unique().alias("k"), pl.len().alias("n"))
                   .filter(pl.col("k") > 1))
    out = df.filter(~suivant).drop("_dup")  # garde la dernière ligne de chaque groupe (fichier le plus récent)
    exemples = [f"{r['cle']}/{r['serie']}/{r['filiere']}/{r['sens']} {r['debut_utc']:%Y-%m-%d %H:%M}Z"
                for r in conflits.head(5).iter_rows(named=True)]
    return out, {"lignes_en_double": df.height - out.height, "conflits": conflits.height,
                 "exemples_conflits": exemples}


def chevauchements(df: pl.DataFrame) -> pl.DataFrame:
    """Points dont la période empiète sur la suivante de la même série (résolutions mêlées au même
    instant) : doit être vide."""
    return (df.sort(CLES_SERIE + ["debut_utc"], nulls_last=True)
              .with_columns(pl.col("debut_utc").shift(-1).over(CLES_SERIE).alias("_suivant"))
              .filter(pl.col("_suivant") < pl.col("debut_utc") + pl.duration(minutes=pl.col("pas_min")))
              .drop("_suivant"))


def charger_natif(raw: Path, processus: int = 6) -> tuple[pl.DataFrame, dict]:
    """Tous les XML ENTSO-E → table native normalisée ; rapport de lecture."""
    fichiers = fichiers_bruts(raw)
    if not fichiers:
        raise FileNotFoundError(f"aucun fichier ENTSO-E dans {raw / 'entsoe'}")
    morceaux, par_fichier = [], {}
    # « spawn » et non « fork » : après usage de polars (pool de threads) dans le processus parent, comme
    # dans `pc build`, des fils créés par fork restent bloqués (constaté le 2026-11-26 ; mise en garde de
    # la documentation de polars sur le multiprocessing).
    with ProcessPoolExecutor(processus, mp_context=multiprocessing.get_context("spawn")) as ex:
        for (p, cle, serie, annee), (df, r) in zip(fichiers, ex.map(lire_fichier, fichiers)):
            morceaux.append(df)
            par_fichier[f"{cle}/{serie}/{annee}"] = {**r, "points": df.height}
    df = pl.concat(morceaux)
    rapport = {
        "fichiers": len(fichiers),
        "fichiers_vides": sorted(k for k, r in par_fichier.items() if r["vide"]),
        "points_lus": df.height,
        "points_repetes_a03": int((~df["publie"]).sum()),
        "sequences_ecartees": {k: r["points_sequences_ecartees"] for k, r in par_fichier.items()
                               if r["sequences_ecartees"]},
    }
    df, rapport["quarts_repetes"] = ramener_quarts_repetes(df)
    df, rapport["doublons"] = dedoublonner(df)
    ch = chevauchements(df)
    rapport["chevauchements"] = ch.height
    if ch.height:
        rapport["exemples_chevauchements"] = [
            f"{r['cle']}/{r['serie']}/{r['filiere']} {r['debut_utc']:%Y-%m-%d %H:%M}Z pas {r['pas_min']}"
            for r in ch.head(5).iter_rows(named=True)]
    df = df.sort(CLES_SERIE + ["debut_utc"], nulls_last=True)
    return df, rapport


# --------------------------------------------------------------------------
# Vue horaire
# --------------------------------------------------------------------------


def _slug(x: str) -> str:
    return x.lower().replace("-", "_")


def nom_colonne(cle: str, serie: str, filiere: str | None, sens: str | None) -> str:
    if cle == "entsoe_prix":
        return f"prix_{_slug(serie)}"
    if cle == "entsoe_production":
        return f"{'production' if sens == 'production' else 'consommation'}_{_slug(serie)}_{filiere.lower()}"
    if cle == "entsoe_flux":
        return f"flux_{_slug(serie)}"
    if cle == "entsoe_capacites":
        return f"ntc_{_slug(serie)}"
    if cle == "entsoe_charge":
        return f"charge_{_slug(serie)}"
    raise ValueError(cle)


def vers_horaire_long(natif: pl.DataFrame) -> pl.DataFrame:
    """Moyenne pondérée par la durée sur l'heure UTC [h, h+1) des points dont la période commence dans
    l'heure ; renseignée seulement si les points couvrent exactement 60 min (sinon null, jamais imputée).
    MW moyens sur l'heure (= MWh de l'heure) ; prix : moyenne simple des quarts (= pondérée)."""
    pas = pl.col("pas_min").cast(pl.Int32)
    return (natif.group_by(*CLES_SERIE, pl.col("debut_utc").dt.truncate("1h").alias("heure_utc"))
                 .agg(pas.sum().alias("couverture_min"), ((pl.col("valeur") * pas).sum() / 60).alias("valeur"))
                 .with_columns(pl.when(pl.col("couverture_min") == 60).then(pl.col("valeur")).otherwise(None)
                               .alias("valeur")))


def vers_horaire(natif: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    """Vue horaire large : `heure_utc` + une colonne par série (+ `solde_physique_fr`). Renvoie aussi la
    description des colonnes."""
    long = vers_horaire_long(natif)
    series = (natif.group_by(CLES_SERIE).agg(pl.col("unite").first(), pl.col("debut_utc").min().alias("debut"),
                                            pl.col("debut_utc").max().alias("fin"), pl.len().alias("points"))
                   .sort(CLES_SERIE, nulls_last=True))
    noms = series.select(*CLES_SERIE).with_columns(pl.Series("col", [
        nom_colonne(*r) for r in series.select(*CLES_SERIE).iter_rows()], dtype=pl.Utf8))
    long = long.join(noms, on=CLES_SERIE, how="left", nulls_equal=True)
    incompletes = (long.filter(pl.col("valeur").is_null()).group_by("col").len().sort("col"))
    debut, fin = long["heure_utc"].min(), long["heure_utc"].max()
    grille = pl.DataFrame({"heure_utc": pl.datetime_range(debut, fin, "1h", time_zone="UTC", eager=True)
                                         .cast(DATETIME_UTC)})
    large = long.pivot(on="col", index="heure_utc", values="valeur", aggregate_function=None)
    colonnes = {}
    for r in series.iter_rows(named=True):
        c = nom_colonne(r["cle"], r["serie"], r["filiere"], r["sens"])
        colonnes[c] = {"cle": r["cle"], "serie": r["serie"], "filiere": r["filiere"],
                       "libelle_filiere": FILIERES.get(r["filiere"]) if r["filiere"] else None,
                       "sens": r["sens"], "unite": r["unite"] if r["unite"] != "MW" else "MW moyens sur l'heure",
                       "premier_point_utc": r["debut"].isoformat(), "dernier_point_utc": r["fin"].isoformat()}
    ordre = sorted(colonnes)
    large = grille.join(large, on="heure_utc", how="left").select("heure_utc", *[c for c in ordre if c in large.columns])
    # Solde physique de la France (+ = import, comme `ech_physiques` d'éCO2mix) : Σ (voisin → FR) − Σ (FR → voisin),
    # seulement si les douze sens sont renseignés.
    entrants = [f"flux_{_slug(v)}_fr" for v in entsoe.VOISINS_FLUX]
    sortants = [f"flux_fr_{_slug(v)}" for v in entsoe.VOISINS_FLUX]
    if all(c in large.columns for c in entrants + sortants):
        large = large.with_columns((pl.sum_horizontal(entrants) - pl.sum_horizontal(sortants)).alias("_s"),
                                   pl.any_horizontal([pl.col(c).is_null() for c in entrants + sortants]).alias("_n"))
        large = large.with_columns(pl.when(pl.col("_n")).then(None).otherwise(pl.col("_s"))
                                   .alias("solde_physique_fr")).drop("_s", "_n")
        colonnes["solde_physique_fr"] = {
            "cle": "entsoe_flux", "serie": "FR", "unite": "MW moyens sur l'heure",
            "definition": "Σ flux (voisin → FR) − Σ flux (FR → voisin), voisins " + ", ".join(entsoe.VOISINS_FLUX)
                          + " ; positif = import ; vide si l'un des douze sens manque"}
    info = {"colonnes": colonnes,
            "heures_incompletes_par_colonne": dict(incompletes.iter_rows())}
    return large, info


# --------------------------------------------------------------------------
# Construction
# --------------------------------------------------------------------------


def construire(raw: Path, derive: Path) -> dict | None:
    """data/raw/entsoe/ → data/derive/entsoe/. Renvoie le rapport, ou None si aucune donnée ENTSO-E."""
    if not (raw / "entsoe").is_dir() or not fichiers_bruts(raw):
        print("ENTSO-E : data/raw/entsoe/ absent, ignoré (`pc download entsoe_…` avec jeton)", file=sys.stderr)
        return None
    from .sources import lire_manifeste
    t0 = datetime.now()
    natif, rapport = charger_natif(raw)
    horaire, info = vers_horaire(natif)
    dossier = derive / "entsoe"
    dossier.mkdir(parents=True, exist_ok=True)
    natif.write_parquet(dossier / "natif.parquet", compression="zstd", compression_level=9)
    horaire.write_parquet(dossier / "horaire.parquet", compression="zstd", compression_level=9)
    manifeste = lire_manifeste(raw)
    extraits = [v["extrait_le"] for k, v in manifeste.items() if k.startswith("entsoe_")]
    meta = {
        "genere_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "conventions": {
            "heure_utc": "début de l'heure décrite, UTC",
            "debut_utc": "début de la période du point natif, UTC (timeInterval/start + (position − 1) × pas)",
            "unites": "puissances en MW moyens sur le pas (horaire : sur l'heure, = MWh de l'heure) ; prix en EUR/MWh "
                      "(GB : GBP/MWh, à ne pas mélanger) ; heure incomplète laissée vide, jamais imputée",
            "prix_horaire": "moyenne simple des quarts d'heure après le 01/10/2025 (convention RTE)",
            "flux": "flux physiques bruts par sens (jamais négatifs) ; flux_fr_be = de la France vers la Belgique",
            "ntc": "capacité d'échange prévue jour-1 (A61, contrat A01), par sens ; absente pour FR↔BE et FR↔DE "
                   "(flow-based)",
            "production": "production_<zone>_<filière> (inBiddingZone) ; consommation_<zone>_<filière> = pompage ou "
                          "stockage (outBiddingZone), à ne pas additionner à la production",
            "zones": "DE = zone de contrôle allemande (production, flux) ; prix DE-AT-LU jusqu'au 30/09/2018 puis "
                     "DE-LU ; IT = Italie entière (production, flux), IT-Nord (prix, NTC)",
        },
        "filieres": FILIERES,
        "regles_lecture": entsoe.REGLES_LECTURE,
        "rapport": rapport,
        **info,
        "licences": {cle: entsoe.LICENCES[cle] for cle in entsoe.CLES},
        "extraction": {"premiere": min(extraits) if extraits else None, "derniere": max(extraits) if extraits else None,
                       "fichiers": len(extraits)},
    }
    (dossier / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False, default=str) + "\n")
    taille = sum(p.stat().st_size for p in dossier.iterdir() if p.is_file())
    print(f"ENTSO-E : {natif.height} points natifs, {horaire.height} heures × {horaire.width - 1} colonnes, "
          f"{taille / 1e6:.1f} Mo dans {dossier} ({(datetime.now() - t0).total_seconds():.0f} s)", file=sys.stderr)
    return rapport


def charger_horaire(derive: Path) -> pl.DataFrame | None:
    p = derive / "entsoe" / "horaire.parquet"
    return pl.read_parquet(p) if p.exists() else None


def charger_natif_derive(derive: Path) -> pl.DataFrame | None:
    p = derive / "entsoe" / "natif.parquet"
    return pl.read_parquet(p) if p.exists() else None
