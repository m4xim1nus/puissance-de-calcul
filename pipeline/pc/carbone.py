"""Intensité carbone MOYENNE (« Quel carbone ? ») → data/export/carbone.json, et chiffres calculés.

Deux séries horaires, toutes deux des intensités **moyennes** d'émissions **directes** (combustion),
en gCO2eq/kWh. Aucune n'est un facteur marginal : elles répartissent les émissions observées sur
l'énergie produite ou consommée, elles ne disent pas ce que changerait une consommation ajoutée.

- **production** : `taux_co2` d'éCO2mix (RTE ; France continentale hors Corse ; importations
  exclues ; facteur du combustible × rendement moyen de la filière, page « éCO2 emissions » de
  RTE). Valeur horaire = moyenne des demi-heures pondérée par la production (`build.vers_horaire`) ;
  moyenne d'une période = moyenne horaire pondérée par la production (Σ des filières) ;
- **consommation** : jeu ODRÉ `part-enr-intensite-ges-conso-tr` (RTE ; France continentale hors
  Corse ; échanges compris par « traçage des flux » sur 15 pays ; facteurs de l'annexe des Bilans
  électriques ; depuis 2021), pondéré par la consommation éCO2mix de la même heure. Hypothèse, non
  documentée par RTE : `date_heure_utc` marque le début de l'heure (même hypothèse que `pc check`,
  `controle_intensite` ; sans effet sur une moyenne annuelle pondérée, effet d'une heure au plus
  sur un profil horaire).

Années : années civiles en heure de Paris, pleines au sens de « Quand ? »
(`export_quand.annees_pleines`) et dont la série couvre au moins toutes les heures moins
`export_quand.TROUS_ADMIS`. Le calcul n'arrondit rien ; l'export arrondit (g/kWh à 4 décimales,
parts à 4 décimales) ; les chiffres cités par le texte sont arrondis au dixième de g/kWh et au
pour cent (`PRECISION`), valeur non arrondie gardée (`valeur_calculee`).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import polars as pl

from .chiffres import PRODUIT_PAR_PIPELINE, arrondi_publie
from .export_quand import TROUS_ADMIS, annees_pleines

TZ_PARIS = "Europe/Paris"

#: Filières dont la somme pondère `taux_co2` (identiques à `build.FILIERES`, vérifié par un test ;
#: pas d'import de build ici, qui importe ce module).
FILIERES = ["fioul", "charbon", "gaz", "nucleaire", "eolien", "solaire", "hydraulique", "bioenergies"]

SOURCE_CARBONE = "pdc-carbone"
URL_CARBONE = "https://github.com/m4xim1nus/puissance-de-calcul/blob/main/data/export/carbone.json"

#: Seuil de l'« intensité de fond » de RTE : « Près de la moitié du temps, l'intensité de la
#: production comme de la consommation s'est située en dessous de 15 gCO2éq/kWh » (Bilan électrique
#: 2025, p. 105). Part des heures strictement en dessous.
SEUIL_FOND_G = 15.0

#: Hiver = novembre à mars (heure de Paris), comme « Quand ? » ; été = avril à octobre.
MOIS_HIVER = (11, 12, 1, 2, 3)

#: Année de crise (disponibilité nucléaire basse, importations) mise à côté de la dernière année
#: pleine dans les matrices mois × heure.
ANNEE_CRISE = 2022

#: Années dont les chiffres entrent dans chiffres.json.
ANNEES_CHIFFRES = (2022, 2024, 2025)

#: Références RTE saisies au référentiel (recoupements de même éditeur, affichés par `pc check`).
REFERENCES_RTE = {
    "production": {2024: "intensite_prod_rte_2024", 2025: "intensite_prod_rte_2025"},
    "consommation": {2025: "intensite_conso_rte_2025"},
}

UNITE = "gCO2eq/kWh"
PRECISION = {UNITE: 0.1, "%": 1}

SERIES = {
    "production": {
        "libelle": "intensité moyenne de la production française",
        "perimetre": "production d'électricité de la France continentale hors Corse (éCO2mix national), émissions "
                     "directes de combustion, importations exclues ; année civile en heure de Paris",
        "definition": "taux_co2 d'éCO2mix (gCO2eq/kWh), valeur horaire pondérée par la production des demi-heures ; "
                      "moyennes de période pondérées par la production horaire (Σ des filières éCO2mix)",
    },
    "consommation": {
        "libelle": "intensité moyenne de la consommation française",
        "perimetre": "consommation d'électricité de la France continentale hors Corse, échanges compris (traçage des "
                     "flux, méthode RTE d'avril 2026), émissions directes ; année civile en heure de Paris",
        "definition": "intensite_emissions_conso du jeu ODRÉ part-enr-intensite-ges-conso-tr (gCO2eq/kWh, entiers), "
                      "pondérée par la consommation éCO2mix de la même heure ; date_heure_utc lue comme début de l'heure "
                      "(hypothèse)",
    },
}

LIMITES = [
    "intensités MOYENNES : émissions observées ÷ énergie observée. Elles répartissent des émissions existantes ; elles "
    "ne mesurent pas ce que changerait une consommation ajoutée (facteur marginal), ni à court terme ni à long terme",
    "émissions directes seulement (combustion) : ni amont des combustibles, ni construction (cycle de vie : RTE publie "
    "29,0 gCO2éq/kWh pour la production 2025, référentiel intensite_prod_acv_rte_2025)",
    "Corse exclue des deux séries ; le Bilan électrique l'inclut (production au fioul) : la moyenne annuelle de la "
    "production éCO2mix est inférieure de 6 à 8 % à celle du Bilan (contrôle `pc check`)",
    "deux jeux de facteurs d'émission chez RTE : éCO2mix (facteur du combustible de l'ADEME × rendement moyen) pour la "
    "production, annexe des Bilans électriques pour la consommation et les Bilans ; ne pas mélanger les deux séries dans "
    "un même calcul sans le dire",
    "consommation : jeu « temps réel » recalculé par RTE (données historiques calculées en mars 2026 sur des données "
    "consolidées, facteurs constants) ; valeurs entières ; horodatage non documenté",
]


# --------------------------------------------------------------------------
# Séries horaires
# --------------------------------------------------------------------------


def lire_ges_conso(chemin: Path) -> pl.DataFrame:
    """Jeu ODRÉ `part-enr-intensite-ges-conso-tr` → (heure_utc, intensite_conso) ; une valeur par
    heure (les doublons éventuels d'un même instant sont refusés plutôt que moyennés)."""
    g = pl.read_parquet(chemin)
    g = (g.select(pl.col("date_heure_utc").dt.convert_time_zone("UTC").cast(pl.Datetime("us", "UTC"))
                  .alias("heure_utc"),
                  pl.col("intensite_emissions_conso").cast(pl.Float64).alias("intensite_conso"))
          .drop_nulls())
    doublons = g.height - g["heure_utc"].n_unique()
    if doublons:
        raise ValueError(f"odre_ges_conso : {doublons} heure(s) en double")
    return g.sort("heure_utc")


def series_horaires(table: pl.DataFrame, ges: pl.DataFrame | None) -> pl.DataFrame:
    """Une ligne par heure : année, mois et heure de Paris (début), intensité et poids de chaque série.
    Une heure n'entre dans une série que si l'intensité et le poids sont renseignés et le poids > 0."""
    t = table.select(
        "heure_utc", "taux_co2", "consommation",
        pl.sum_horizontal([pl.col(f) for f in FILIERES]).alias("production"),
        pl.any_horizontal([pl.col(f).is_null() for f in FILIERES]).alias("_trou"),
    )
    t = t.with_columns(pl.when(pl.col("_trou")).then(None).otherwise(pl.col("production")).alias("production"))
    if ges is not None:
        t = t.join(ges, on="heure_utc", how="left")
    else:
        t = t.with_columns(pl.lit(None, dtype=pl.Float64).alias("intensite_conso"))
    p = pl.col("heure_utc").dt.convert_time_zone(TZ_PARIS)
    return t.select(
        "heure_utc",
        p.dt.year().alias("an"), p.dt.month().alias("mois"), p.dt.hour().alias("heure"),
        p.dt.strftime("%Y-%m-%dT%H:%M%:z").alias("debut_paris"),
        pl.col("taux_co2").alias("i_production"), pl.col("production").alias("w_production"),
        pl.col("intensite_conso").alias("i_consommation"), pl.col("consommation").alias("w_consommation"),
    )


def _valides(d: pl.DataFrame, serie: str) -> pl.DataFrame:
    i, w = f"i_{serie}", f"w_{serie}"
    return (d.filter(pl.col(i).is_not_null() & pl.col(w).is_not_null() & (pl.col(w) > 0))
             .select("heure_utc", "an", "mois", "heure", "debut_paris", pl.col(i).alias("i"), pl.col(w).alias("w")))


def _pond(d: pl.DataFrame) -> float:
    return float((d["i"] * d["w"]).sum() / d["w"].sum())


def moyenne_ponderee(intensites: list[float], poids: list[float]) -> float:
    """Σ i·w / Σ w (implémentation de référence, pour les tests)."""
    s = sum(w for w in poids)
    return sum(i * w for i, w in zip(intensites, poids)) / s


def stats_annee(d: pl.DataFrame) -> dict:
    """Statistiques d'une série sur une année (heures valides `d` : colonnes i, w, mois, heure)."""
    imax = d.sort(["i", "heure_utc"], descending=[True, False]).row(0, named=True)
    imin = d.sort(["i", "heure_utc"]).row(0, named=True)
    mensuel = (d.group_by("mois").agg(((pl.col("i") * pl.col("w")).sum() / pl.col("w").sum()).alias("v"))
                .sort("mois"))
    horaire = (d.group_by("heure").agg(((pl.col("i") * pl.col("w")).sum() / pl.col("w").sum()).alias("v"))
                .sort("heure"))
    hiver = d.filter(pl.col("mois").is_in(MOIS_HIVER))
    ete = d.filter(~pl.col("mois").is_in(MOIS_HIVER))
    q = {f"p{int(k * 100):02d}": float(d["i"].quantile(k, interpolation="linear")) for k in (0.1, 0.5, 0.9)}
    return {
        "heures_valides": d.height,
        "moyenne_ponderee": _pond(d),
        "moyenne_simple": float(d["i"].mean()),
        "max": {"valeur": float(imax["i"]), "debut_paris": imax["debut_paris"],
                "heure_utc": imax["heure_utc"].strftime("%Y-%m-%dT%H:%MZ")},
        "min": {"valeur": float(imin["i"]), "debut_paris": imin["debut_paris"],
                "heure_utc": imin["heure_utc"].strftime("%Y-%m-%dT%H:%MZ")},
        "quantiles": q,
        "part_heures_sous_seuil_fond": float((d["i"] < SEUIL_FOND_G).mean()),
        "moyenne_hiver": _pond(hiver) if hiver.height else None,
        "moyenne_ete": _pond(ete) if ete.height else None,
        "profil_mensuel": [None if m not in mensuel["mois"].to_list() else
                           float(mensuel.filter(pl.col("mois") == m)["v"][0]) for m in range(1, 13)],
        "profil_horaire": [None if h not in horaire["heure"].to_list() else
                           float(horaire.filter(pl.col("heure") == h)["v"][0]) for h in range(24)],
    }


def matrice_mois_heure(d: pl.DataFrame) -> dict:
    """Moyenne pondérée par case mois (lignes, janvier = 0) × heure de Paris de début (24 colonnes) ;
    case extrême haute et basse."""
    m = (d.group_by(["mois", "heure"]).agg(((pl.col("i") * pl.col("w")).sum() / pl.col("w").sum()).alias("v"),
                                         pl.len().alias("n")))
    valeurs: list[list[float | None]] = [[None] * 24 for _ in range(12)]
    for mois, heure, v, _ in m.iter_rows():
        valeurs[mois - 1][heure] = float(v)
    haut = m.sort(["v", "mois", "heure"], descending=[True, False, False]).row(0, named=True)
    bas = m.sort(["v", "mois", "heure"]).row(0, named=True)
    return {
        "valeurs": valeurs,
        "case_max": {"mois": int(haut["mois"]) - 1, "heure": int(haut["heure"]), "valeur": float(haut["v"]),
                     "heures": int(haut["n"])},
        "case_min": {"mois": int(bas["mois"]) - 1, "heure": int(bas["heure"]), "valeur": float(bas["v"]),
                     "heures": int(bas["n"])},
    }


def _attendu(an: int) -> int:
    return 8784 if (an % 4 == 0 and (an % 100 != 0 or an % 400 == 0)) else 8760


def annees_serie(h: pl.DataFrame, serie: str, pleines: list[int]) -> list[int]:
    """Années pleines (« Quand ? ») où la série couvre au moins toutes les heures moins TROUS_ADMIS."""
    v = _valides(h, serie).group_by("an").len()
    n = dict(v.iter_rows())
    return [a for a in pleines if n.get(a, 0) >= _attendu(a) - TROUS_ADMIS]


# --------------------------------------------------------------------------
# carbone.json
# --------------------------------------------------------------------------


def arrondir(o, cle: str = ""):
    """Arrondis de l'export : intensités à 4 décimales de g/kWh, parts à 4 décimales, émissions au millième
    de Mt. Le texte cite le dixième de g/kWh, arrondi depuis ces valeurs : un double arrondi ne change le
    dixième que si la valeur exacte tombe à moins de 0,00005 g d'un demi-dixième ; `pc check`
    (`controle_carbone_chiffres`) compare donc aussi chaque chiffre à l'arrondi de la valeur NON arrondie.
    (Avec 3 décimales, 20,14978 devenait 20,150 puis 20,2 au lieu de 20,1 : constaté le 26/11/2026.)"""
    if isinstance(o, dict):
        return {k: arrondir(v, str(k)) for k, v in o.items()}
    if isinstance(o, list):
        return [arrondir(v, cle) for v in o]
    if isinstance(o, float):
        if cle.startswith("part"):
            return round(o, 4) + 0.0
        if cle.endswith("_mt"):
            return round(o, 3) + 0.0
        return round(o, 4) + 0.0
    return o


def construire_carbone(table: pl.DataFrame, ges: pl.DataFrame | None, extractions: dict,
                       arrondi: bool = True) -> dict:
    """Contenu de carbone.json (arrondi) à partir de la table horaire exportée et du jeu ODRÉ ;
    `arrondi=False` : mêmes valeurs non arrondies (contrôle du double arrondi par `pc check`)."""
    h = series_horaires(table, ges)
    pleines, _ = annees_pleines(table)
    annees: dict[str, dict] = {}
    couvertes: dict[str, list[int]] = {}
    matrices: dict[str, dict] = {}
    for serie in SERIES:
        couvertes[serie] = annees_serie(h, serie, pleines)
        v = _valides(h, serie)
        for an in couvertes[serie]:
            d = v.filter(pl.col("an") == an)
            s = stats_annee(d)
            if serie == "production":
                # émissions directes (hors Corse) = Σ intensité horaire × production horaire :
                # g/kWh × MWh = kg ; / 1e9 → Mt
                s["emissions_directes_mt"] = float((d["i"] * d["w"]).sum() / 1e9)
                s["production_twh"] = float(d["w"].sum() / 1e6)
            annees.setdefault(str(an), {})[serie] = s
        dernieres = sorted({ANNEE_CRISE, couvertes[serie][-1]} & set(couvertes[serie])) if couvertes[serie] else []
        matrices[serie] = {str(an): matrice_mois_heure(v.filter(pl.col("an") == an)) for an in dernieres}
    exclues = {str(a): "année incomplète (voir quand.json, annees_exclues)" for a in
               sorted(set(h["an"].unique().to_list()) - set(pleines))}
    contenu = {
        "description": "Intensité carbone MOYENNE de la production et de la consommation d'électricité en France "
                       "(enquête « Quel carbone ? »), année par année, mois par mois et heure par heure. Ni l'une ni "
                       "l'autre n'est un facteur marginal. Calcul : pipeline/pc/carbone.py. Généré par `pc build`, "
                       "ne pas modifier.",
        "donnees": {
            "entree": "systeme_horaire.parquet (taux_co2, filières, consommation) ; ODRÉ "
                      "part-enr-intensite-ges-conso-tr (data/raw, non republié en série horaire)",
            "sources": "éCO2mix national (RTE, ODRÉ, Licence Ouverte 2.0) ; intensité GES de la consommation (RTE, "
                       "ODRÉ, Licence Ouverte 2.0)",
            "extractions": extractions,
        },
        "unites": "intensités en gCO2eq/kWh (émissions directes) ; parts entre 0 et 1 ; émissions en Mt ; production "
                  "en TWh ; mois indexés à partir de 0 dans les matrices (janvier = 0), heures de Paris de début (0 h = "
                  "0) ; profil_mensuel : janvier en premier",
        "series": SERIES,
        "parametres": {
            "seuil_fond_g": SEUIL_FOND_G,
            "seuil_fond": "part_heures_sous_seuil_fond = part des heures valides où l'intensité est strictement "
                          "inférieure au seuil (« intensité de fond » de RTE, Bilan électrique 2025, p. 105)",
            "hiver": "novembre à mars (heure de Paris) ; été : avril à octobre",
            "quantiles": "distribution des heures (non pondérée), interpolation linéaire",
            "moyennes": "pondérées par la production (série production) ou par la consommation (série consommation)",
        },
        "limites": LIMITES,
        "annees_couvertes": {k: v for k, v in couvertes.items()},
        "annees_exclues": exclues,
        "annees": dict(sorted(annees.items())),
        "matrices_mois_heure": matrices,
    }
    return arrondir(contenu) if arrondi else contenu


def ecrire_carbone(contenu: dict, chemin: Path) -> None:
    from .export_quand import _dumps
    chemin.write_text(_dumps(contenu) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Chiffres calculés
# --------------------------------------------------------------------------

NOMS_MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
             "novembre", "décembre"]


def source_carbone(date_extraction: str) -> dict:
    return {
        "editeur": "Puissance de calcul (calcul du site)",
        "titre": "Indicateurs « Quel carbone ? » (data/export/carbone.json), calculés par `pc build` sur éCO2mix (RTE) "
                 "et l'intensité GES de la consommation publiée par RTE sur ODRÉ",
        "date_publication": date_extraction,
        "url": URL_CARBONE,
        "consulte_le": date_extraction,
        "note": "date = dernière extraction des données sources ; recalculé à chaque `pc build`, contrôlé par `pc check`",
    }


def _valeur(x: float, unite: str) -> dict:
    pas = PRECISION[unite]
    x = round(x, 6)
    return {"valeur": arrondi_publie(x, pas), "valeur_calculee": x, "precision": pas, "unite": unite}


def _fr(x: float, dec: int) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def _heure_paris(iso: str) -> str:
    p = datetime.fromisoformat(iso)
    return f"{p.day} {NOMS_MOIS[p.month - 1]} {p.year}, {p.hour} h-{p.hour + 1} h (heure de Paris)"


NOTE_MOYEN = ("intensité MOYENNE, pas un facteur marginal : elle ne dit pas ce que changerait une consommation "
              "ajoutée")
#: Les valeurs horaires dépendent de la convention d'horodatage d'éCO2mix (build.HORODATAGE_ECO2MIX = « fin »,
#: établie par le spike et sa contre-vérification) : avec la convention inverse, la décimale de certaines
#: valeurs change (relecture adverse du 26/11/2026, f11 : 62,1 → 62,0 g pour la consommation 2022 ; 57,5 →
#: 57,0 g pour le maximum de la production 2025).
NOTE_HORODATAGE = ("décimale sensible à la convention d'horodatage d'éCO2mix (point horodaté t = période qui se termine "
                   "à t), qui fixe les heures et les poids")

#: Maximum horaire publié par RTE, par série et par année (recoupement de même éditeur).
MAX_RTE = {"consommation": {2025: "intensite_max_rte_2025"}}


def chiffres_calcules(c: dict, saisis: dict[str, dict] | None = None) -> dict[str, dict]:
    """Chiffres que le texte cite, lus dans carbone.json (déjà arrondi), au schéma du référentiel."""
    saisis = saisis or {}
    out: dict[str, dict] = {}
    base = {"source": SOURCE_CARBONE, "page": "data/export/carbone.json", "confiance": "B",
            "verification": "pc check", "produit_par": PRODUIT_PAR_PIPELINE, "grandeur": "intensite_moyenne"}
    for serie, prefixe in (("production", "carbone_prod"), ("consommation", "carbone_conso")):
        meta = SERIES[serie]
        commun = {**base, "perimetre": meta["perimetre"]}
        for an in ANNEES_CHIFFRES:
            s = c["annees"].get(str(an), {}).get(serie)
            if s is None:
                continue
            recoupements = []
            cle_ref = REFERENCES_RTE[serie].get(an)
            if cle_ref and cle_ref in saisis:
                ref = saisis[cle_ref]
                recoupements.append({
                    "source": ref["source"], "valeur": f"{_fr(ref['valeur'], 1)} {ref['unite']} (RTE, {ref['page']})",
                    "note": ("même éditeur (RTE) ; le Bilan électrique inclut la Corse (production au fioul) et applique "
                             "les facteurs de son annexe, éCO2mix non : écart contrôlé par `pc check`"
                             if serie == "production" else
                             "même éditeur (RTE), même méthode : écart contrôlé par `pc check` (± 2 %)"),
                    "independant": False})
            out[f"{prefixe}_moyenne_{an}"] = {
                **commun,
                "libelle": f"Intensité carbone moyenne de la {serie} (émissions directes), moyenne annuelle",
                **_valeur(s["moyenne_ponderee"], UNITE), "periode": str(an),
                "citation": f"annees.{an}.{serie}.moyenne_ponderee",
                "calcul": meta["definition"] + f" ; {s['heures_valides']} heures valides",
                **({"recoupements": recoupements} if recoupements else {}),
                "note": NOTE_MOYEN + f" ; moyenne simple des heures, non pondérée (à ne pas prendre pour la moyenne annuelle) : "
                        f"{_fr(s['moyenne_simple'], 1)} g ; " + NOTE_HORODATAGE,
            }
            rec_max = []
            cle_max = MAX_RTE.get(serie, {}).get(an)
            if cle_max and cle_max in saisis:
                ref = saisis[cle_max]
                rec_max.append({
                    "source": ref["source"], "valeur": f"{_fr(ref['valeur'], 0)} {ref['unite']} (RTE, {ref['page']})",
                    "note": "même éditeur ; RTE calcule sur sa série du Bilan, la série ODRÉ a été recalculée en mars 2026 "
                            "avec les facteurs actuels : écart contrôlé par `pc check` (± 3 g)",
                    "independant": False})
            out[f"{prefixe}_max_{an}"] = {
                **commun, **({"recoupements": rec_max} if rec_max else {}),
                "libelle": f"Intensité carbone moyenne de la {serie}, maximum horaire de l'année",
                **_valeur(s["max"]["valeur"], UNITE), "periode": _heure_paris(s["max"]["debut_paris"]),
                "citation": f"annees.{an}.{serie}.max (heure UTC {s['max']['heure_utc']})",
                "calcul": meta["definition"] + " ; maximum des valeurs horaires",
                "note": NOTE_MOYEN + " ; l'heure la plus carbonée en moyenne n'est pas l'heure où une consommation "
                        "ajoutée émettrait le plus ; " + NOTE_HORODATAGE,
            }
        an = ANNEES_CHIFFRES[-1]
        s = c["annees"].get(str(an), {}).get(serie)
        if s is None:
            continue
        out[f"{prefixe}_part_sous_15_{an}"] = {
            **commun, "grandeur": "part",
            "libelle": f"Part des heures où l'intensité moyenne de la {serie} est inférieure à "
                       f"{_fr(SEUIL_FOND_G, 0)} gCO2eq/kWh",
            **_valeur(s["part_heures_sous_seuil_fond"] * 100, "%"), "periode": str(an),
            "citation": f"annees.{an}.{serie}.part_heures_sous_seuil_fond",
            "calcul": f"heures où l'intensité horaire est strictement inférieure à {_fr(SEUIL_FOND_G, 0)} g / heures "
                      f"valides ({s['heures_valides']})",
            "note": "seuil de l'« intensité de fond » de RTE (Bilan électrique 2025, p. 105 : « près de la moitié du "
                    "temps ») ; " + NOTE_MOYEN,
        }
    # Variations saisonnières et horaires de la production (dernière année et année de crise)
    commun = {**base, "perimetre": SERIES["production"]["perimetre"]}
    for an in (ANNEE_CRISE, ANNEES_CHIFFRES[-1]):
        s = c["annees"].get(str(an), {}).get("production")
        if s is None:
            continue
        for saison, nom, mois in (("hiver", "hiver (novembre à mars)", "novembre à mars"),
                                  ("ete", "été (avril à octobre)", "avril à octobre")):
            out[f"carbone_prod_{saison}_{an}"] = {
                **commun,
                "libelle": f"Intensité carbone moyenne de la production, {nom}",
                **_valeur(s[f"moyenne_{saison}"], UNITE), "periode": f"{an}, {mois} (heure de Paris)",
                "citation": f"annees.{an}.production.moyenne_{saison}",
                "calcul": SERIES["production"]["definition"] + f", sur les heures de {mois}",
                "note": NOTE_MOYEN,
            }
        m = c["matrices_mois_heure"]["production"].get(str(an))
        if m is None:
            continue
        for extremite, sens in (("max", "la plus élevée"), ("min", "la plus basse")):
            k = m[f"case_{extremite}"]
            out[f"carbone_prod_mh_{extremite}_{an}"] = {
                **commun,
                "libelle": f"Intensité carbone moyenne de la production, case mois × heure {sens} de l'année",
                **_valeur(k["valeur"], UNITE),
                "periode": f"{NOMS_MOIS[k['mois']]} {an}, {k['heure']} h-{k['heure'] + 1} h (heure de Paris), "
                           f"moyenne de {k['heures']} heures",
                "citation": f"matrices_mois_heure.production.{an}.case_{extremite}",
                "calcul": SERIES["production"]["definition"] + " ; moyenne pondérée par case mois × heure de Paris, "
                          f"case {sens} des 288",
                "note": NOTE_MOYEN,
            }
    return out

