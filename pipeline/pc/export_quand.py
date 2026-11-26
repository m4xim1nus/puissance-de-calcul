"""Table horaire → data/export/quand.json, et chiffres calculés du référentiel (« Quand ? »).

Le calcul est dans `pc/quand.py` (Python pur, implémentation de référence). Ici : découpage
par année, arrondis identiques à ceux des CSV publiés (`horaire/AAAA.csv`, MW à l'unité : le
simulateur du site, qui lira ces CSV, doit retrouver les mêmes résultats), vérification des
colonnes d'éCO2mix utilisées, écriture du JSON et production des chiffres que le texte cite
(`chiffres_calcules`), insérés dans `chiffres.json` avec le même schéma que le référentiel
saisi (`produit_par: pc build`).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import polars as pl

from . import quand
from .chiffres import PRODUIT_PAR_PIPELINE

TZ_PARIS = "Europe/Paris"

#: Colonnes lues dans `systeme_horaire.parquet` (nom dans la table → nom attendu par pc/quand.py),
#: avec leurs décimales, comme `build.COLONNES_CSV`.
COLONNES = {
    "consommation": ("consommation", 0),
    "eolien": ("eolien", 0),
    "solaire": ("solaire", 0),
    "nucleaire": ("nucleaire", 0),
    "nucleaire_disponible": ("nucleaire_disponible", 0),
    "nucleaire_disponible_flamanville3": ("nucleaire_disponible_flamanville3", 0),
    "prix_eur_mwh": ("prix", 4),
    **{c: (c, 0) for c in quand.COMPOSANTES},
}

#: Années de la matrice jour × heure : 2022 (année de crise : disponibilité nucléaire à 54,2 %,
#: BE2025 fig. 2.5) et la plus récente année pleine.
ANNEE_CRISE = 2022

#: Années dont les chiffres entrent dans `chiffres.json` : 2022 et les années pleines depuis 2023.
PREMIERE_ANNEE_CHIFFRES = 2023

#: Source des chiffres calculés (clé du référentiel fusionné).
SOURCE_QUAND = "pdc-quand"
URL_QUAND = "https://github.com/m4xim1nus/puissance-de-calcul/blob/main/data/export/quand.json"

#: Modulation nucléaire publiée (TWh), pour le recoupement d'ordre de grandeur de Σ J (pas une
#: égalité attendue). Identifiants du référentiel saisi.
MODULATION_PUBLIEE = {2023: "modulation_nucleaire_2023_bp", 2024: "modulation_nucleaire_2024_bp",
                      2025: "modulation_nucleaire_2025_bp"}

PERIMETRE = ("France continentale hors Corse (éCO2mix national) ; nucléaire disponible déclaré par EDF au titre "
             "de REMIT, Flamanville 3 comprise à partir du 18/12/2024 ; année civile en heure de Paris")


# --------------------------------------------------------------------------
# Préparation
# --------------------------------------------------------------------------


def _avec_annee(table: pl.DataFrame) -> pl.DataFrame:
    return table.with_columns(pl.col("heure_utc").dt.convert_time_zone(TZ_PARIS).dt.year().alias("_an"))


#: Heures sans consommation tolérées dans une année pleine : les trous structurels que
#: `pc check` explique un à un (2 au passage à l'heure d'hiver, 1 par raccord de natures).
TROUS_ADMIS = 6


def annees_pleines(table: pl.DataFrame) -> tuple[list[int], dict[int, str]]:
    """Années civiles (heure de Paris) complètes (toutes les heures de la grille, au plus
    `TROUS_ADMIS` heures sans consommation, aucune donnée temps réel) ; les autres, avec le motif
    d'exclusion."""
    t = _avec_annee(table)
    pleines, exclues = [], {}
    for (an,), d in t.group_by("_an", maintain_order=True):
        attendu = 8784 if (an % 4 == 0 and (an % 100 != 0 or an % 400 == 0)) else 8760
        trous = d["consommation"].null_count()
        natures = sorted(set(d["nature"].drop_nulls().to_list()))
        if d.height == attendu and trous <= TROUS_ADMIS and "temps_reel" not in natures:
            pleines.append(int(an))
        else:
            fin = d.drop_nulls("consommation")["heure_utc"].max()
            exclues[int(an)] = (f"année incomplète : {d.height} heures sur {attendu}, consommation jusqu'au "
                                f"{fin:%Y-%m-%d %H:%M} UTC ; natures {', '.join(natures)} (le temps réel est une "
                                "puissance instantanée, moins précise) ; à calculer quand l'année sera close")
    return sorted(pleines), exclues


def table_annee(table: pl.DataFrame, an: int) -> dict[str, list]:
    """Colonnes d'une année au format de pc/quand.py, arrondies comme les CSV publiés."""
    d = _avec_annee(table).filter(pl.col("_an") == an).sort("heure_utc")
    exprs = [pl.col("heure_utc").dt.convert_time_zone("UTC").dt.strftime("%Y-%m-%dT%H:%MZ").alias("heure_utc")]
    for src, (nom, dec) in COLONNES.items():
        e = pl.col(src).round(dec)
        exprs.append((e.cast(pl.Int64) if dec == 0 else e).alias(nom))
    return d.select(exprs).to_dict(as_series=False)


def verifier_colonnes_eco2mix(table: pl.DataFrame, annees: list[int]) -> dict:
    """Ce que contiennent les colonnes d'éCO2mix dont on tire une phrase (constaté, pas supposé).

    - `hydraulique` = fil de l'eau et éclusées + lacs + turbinage des STEP ;
    - `gaz` = cycles combinés + TAC + cogénération + autres ;
    - bilan : consommation = Σ filières + pompage (négatif) + solde des échanges (positif = import).
      Si `consommation` comprenait le pompage, ou si le signe du solde était inverse, l'écart
      serait de l'ordre du GW ; on le mesure.
    """
    t = _avec_annee(table).filter(pl.col("_an").is_in(annees))
    filieres = ["fioul", "charbon", "gaz", "nucleaire", "eolien", "solaire", "hydraulique", "bioenergies"]
    r = (t.with_columns(
            (pl.col("hydraulique") - pl.col("hydraulique_fil_eau_eclusee") - pl.col("hydraulique_lacs")
             - pl.col("hydraulique_step_turbinage")).alias("e_hydro"),
            (pl.col("gaz") - pl.col("gaz_ccg") - pl.col("gaz_tac") - pl.col("gaz_cogen") - pl.col("gaz_autres"))
            .alias("e_gaz"),
            (pl.col("consommation") - pl.sum_horizontal(filieres) - pl.col("pompage") - pl.col("ech_physiques"))
            .alias("e_bilan"))
          .group_by("_an").agg(pl.col("e_hydro").abs().max(), pl.col("e_gaz").abs().max(),
                               pl.col("e_bilan").mean().alias("bilan_moy"), pl.col("e_bilan").abs().max().alias("bilan_max"),
                               pl.col("pompage").max().alias("pompage_max"))
          .sort("_an"))
    par_an = {int(a): {"hydraulique_moins_sous_filieres_max_mw": round(h, 1), "gaz_moins_sous_filieres_max_mw": round(g, 1),
                       "ecart_bilan_moyen_mw": round(bm, 1), "ecart_bilan_max_mw": round(bx, 1),
                       "pompage_max_mw": round(p, 1)}
              for a, h, g, bm, bx, p in r.iter_rows()}
    return {
        "constats": [
            "hydraulique = fil de l'eau et éclusées + lacs + turbinage des STEP (écart horaire maximal par année "
            "ci-dessous : arrondis) ; le turbinage des STEP est donc DANS l'hydraulique, et rendu à part ici",
            "gaz = cycles combinés + turbines à combustion + cogénération + autres (écart : arrondis des sous-filières)",
            "consommation = Σ des filières + pompage + solde des échanges physiques, à quelques dizaines de MW près "
            "(écart moyen ci-dessous) : la consommation éCO2mix EXCLUT le pompage (sinon l'écart serait du GW), et le "
            "solde est positif à l'import",
            "pompage ≤ 0 à toutes les heures (consommation des STEP, comptée négative)",
            "écart de bilan moyen de quelques MW jusqu'en 2020, de −65 à −80 MW depuis 2021 (même saut, de 2 à "
            "environ 22 MW, pour le gaz contre ses sous-filières) : cause non établie (hypothèse non vérifiée : "
            "stockage par batteries, sans colonne dans le jeu définitif) ; l'écart est rendu tel quel dans la "
            "couverture des heures tendues (`ecart_bilan_eco2mix`)",
        ],
        "par_annee": par_an,
    }


# --------------------------------------------------------------------------
# Arrondis et écriture
# --------------------------------------------------------------------------


def arrondir(o, cle: str = ""):
    """Arrondis de l'export (le calcul n'arrondit rien) : MW à l'unité, TWh et parts à 4 décimales."""
    if isinstance(o, dict):
        return {k: arrondir(v, cle if cle.endswith("_mw") else str(k)) for k, v in o.items()}
    if isinstance(o, list):
        return [arrondir(v, cle) for v in o]
    if isinstance(o, float):
        if cle.endswith("_twh") or cle.startswith("part"):
            return round(o, 4) + 0.0
        if cle.endswith("_mw") or cle in ("monotone", "heures", "valeurs"):
            return int(round(o))
    return o


def _dumps(o, indent: int = 0) -> str:
    """JSON lisible en diff : objets sur plusieurs lignes, listes de scalaires sur une ligne,
    listes de listes une sous-liste par ligne."""
    pad, pad2 = " " * indent, " " * (indent + 1)
    if isinstance(o, dict):
        if not o:
            return "{}"
        items = [f"{pad2}{json.dumps(str(k), ensure_ascii=False)}: {_dumps(v, indent + 1)}" for k, v in o.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(o, list):
        if o and all(isinstance(x, list) for x in o):
            return "[\n" + ",\n".join(pad2 + json.dumps(x, ensure_ascii=False) for x in o) + "\n" + pad + "]"
        if all(not isinstance(x, (dict, list)) for x in o):
            return json.dumps(o, ensure_ascii=False)
        return "[\n" + ",\n".join(pad2 + _dumps(x, indent + 1) for x in o) + "\n" + pad + "]"
    return json.dumps(o, ensure_ascii=False)


# --------------------------------------------------------------------------
# quand.json
# --------------------------------------------------------------------------

DEFINITIONS = {
    "charge_residuelle": "RN = consommation − éolien − solaire − nucléaire DISPONIBLE déclaré (REMIT), MW moyens sur "
                         "l'heure : ce que doivent fournir l'hydraulique, le thermique, les bioénergies, les échanges, "
                         "le stockage et les effacements. Carte des heures tendues, PAS une marge : la capacité "
                         "disponible de ces moyens n'est pas observée heure par heure",
    "jeu_nucleaire": "J = max(0, nucléaire disponible déclaré − nucléaire produit), MW moyens ; Σ J en TWh = Σ des MW "
                     "moyens horaires × 1 h / 10⁶. Nucléaire déclaré disponible et non produit : borne haute, voir "
                     "`limites.jeu_nucleaire` ; ce n'est PAS la « modulation » publiée par EDF",
    "charges_plates": "consommation supplémentaire constante de X MW toute l'année. energie_ajoutee_twh = X × heures "
                      "de l'année ; part_dans_j = Σ min(X, J) / (X × heures où J est renseigné) ; "
                      "heures_j_superieur_ou_egal_x = heures où J ≥ X ; heures_rn_plus_x_au_dessus_du_max = heures où "
                      "RN + X > RN maximal observé de l'année (strictement) ; rn_max_plus_x_mw = RN max + X",
    "heures_tendues": "les N heures de RN la plus élevée de l'année (RN décroissant, puis heure UTC croissante) ; "
                      "répartition par mois et par heure de Paris de début ; couverture_moyenne_mw = moyenne, sur ces "
                      "heures, de chaque terme de RN = hydraulique (3 sous-filières) + gaz + charbon + fioul + "
                      "bioénergies + pompage + solde des échanges + (nucléaire produit − disponible) + écart de bilan "
                      "éCO2mix ; la somme des termes redonne rn_moyenne_mw",
    "prix": "heures à prix day-ahead France strictement négatif (heures_negatif) et nul ou négatif "
            "(heures_nul_ou_negatif) ; après le 01/10/2025, prix horaire = moyenne des 4 quarts d'heure (convention "
            "RTE) ; RN et J moyens à ces heures",
}

SIGNES = {
    "ech_physiques": "solde des échanges physiques : POSITIF = import (l'étranger contribue à couvrir RN), NÉGATIF = "
                     "export (les moyens français couvrent RN et, en plus, les exports : le terme est retranché)",
    "pompage": "consommation des STEP en pompage, NÉGATIVE (elle s'ajoute à ce qu'il faut couvrir)",
    "hydraulique_step_turbinage": "turbinage des STEP, positif ; compris dans la colonne `hydraulique` d'éCO2mix",
    "nucleaire_produit_moins_disponible": "nucléaire produit − disponible déclaré, en général NÉGATIF (−J), parfois "
                                          "positif de quelques centaines de MW (eau froide, déclarations en escalier)",
    "ecart_bilan_eco2mix": "consommation − Σ filières − pompage − solde des échanges, tel que publié (cause non établie)",
}

LIMITES = {
    "charge_residuelle": [
        "observé, pas simulé : 2015-2025 ne contient aucune vague de froid du type de février 2012 ; une monotone "
        "observée n'est pas une distribution de risque (RTE simule des centaines de scénarios climatiques)",
        "éolien et solaire observés = après écrêtement : aux heures de prix négatif, RN est surestimée",
        "nucléaire disponible DÉCLARÉ (REMIT), pas une capacité physique garantie ; réserves de services système "
        "comprises",
        "hydraulique de lac et STEP : contraintes d'énergie (stock) ; leur puissance n'est pas disponible à toute heure",
        "les imports ne sont pas une marge ferme (vagues de froid communes à l'Europe)",
        "pointe horaire ≠ pointe à la demi-heure ou au quart d'heure ; consommation hors Corse",
    ],
    "jeu_nucleaire": list(quand.LIMITES_J),
    "charges_plates": [
        "heures_rn_plus_x_au_dessus_du_max compte des heures au-delà du maximum OBSERVÉ de l'année : un écart à "
        "l'observé, pas une défaillance ni un risque de défaillance",
        "part_dans_j est un plafond (voir limites.jeu_nucleaire) ; le reste de l'énergie viendrait d'autres moyens "
        "ou de moins d'exports",
        "une charge plate ne représente pas un data center réel (montée en charge, profil, effacement possible) ; "
        "RTE n'écrit pas qu'un GW de consommation à la pointe retire un GW de marge (contre-vérification du "
        "26/11/2026, n° 13)",
    ],
}


def encadrement_flamanville3(t: dict[str, list]) -> dict | None:
    """Σ J hors Flamanville 3, encadré : la production de l'EPR n'est pas publiée à part.

    J hors EPR = max(0, (disponible − disponible EPR) − (production − production EPR)) est
    au moins `somme_j_sans_disponible_epr_twh` = Σ max(0, disponible − disponible EPR − production)
    (on retranche aussi la production de l'EPR) et au plus Σ J (tant que l'EPR ne produit pas plus
    que son disponible déclaré). None avant la mise en service de l'EPR.
    """
    epr = t.get("nucleaire_disponible_flamanville3") or []
    if not any(epr):
        return None
    bas = [max(0.0, d - e - p) for d, e, p in zip(t["nucleaire_disponible"], epr, t["nucleaire"])
           if None not in (d, e, p)]
    return {
        "disponible_declare_epr_twh": sum(e for e in epr if e is not None) / 1e6,
        "somme_j_sans_disponible_epr_twh": sum(bas) / 1e6,
        "lecture": "Σ J hors Flamanville 3 est compris entre somme_j_sans_disponible_epr_twh et somme_twh : "
                   "la production de l'EPR (en essais en 2025) n'est pas publiée à part dans éCO2mix",
    }


def construire_quand(table: pl.DataFrame, extractions: dict) -> dict:
    """Contenu de quand.json (arrondi) à partir de la table horaire exportée."""
    pleines, exclues = annees_pleines(table)
    annees = {}
    for an in pleines:
        t = table_annee(table, an)
        a = quand.indicateurs_annee(t)
        f3 = encadrement_flamanville3(t)
        if f3:
            a["jeu_nucleaire"]["flamanville3"] = f3
        annees[str(an)] = arrondir(a)
    matrices = {}
    for an in sorted({ANNEE_CRISE, pleines[-1]} & set(pleines)):
        t = table_annee(table, an)
        rn = [quand.charge_residuelle(*v) for v in zip(t["consommation"], t["eolien"], t["solaire"],
                                                         t["nucleaire_disponible"])]
        matrices[str(an)] = arrondir(quand.matrice_jour_heure(t["heure_utc"], rn))
    return {
        "description": "Indicateurs de l'enquête « Quand ? » : à quelles heures le système électrique français a de "
                       "la marge, à quelles heures il n'en a pas, et ce qu'une consommation supplémentaire plate de "
                       "X GW change à ces heures. Calcul : pipeline/pc/quand.py (implémentation de référence), "
                       "cas de test partagés : pipeline/tests/cas_quand.json. Généré par `pc build`, ne pas modifier.",
        "donnees": {
            "entree": "systeme_horaire.parquet, colonnes arrondies comme horaire/AAAA.csv (MW à l'unité, prix à 4 "
                      "décimales) : les CSV publiés redonnent exactement ces résultats",
            "sources": "éCO2mix national (RTE, ODRÉ, Licence Ouverte 2.0) ; indisponibilités REMIT d'EDF "
                       "(opendata.edf.fr, Licence Ouverte 2.0) ; prix day-ahead France (energy-charts, CC BY 4.0)",
            "extractions": extractions,
        },
        "unites": "puissances en MW moyens sur l'heure (= MWh de l'heure) ; énergies en TWh ; parts entre 0 et 1 ; "
                  "heures en nombre d'heures ; `heure_utc` = début de l'heure en UTC ; `debut_paris` = même instant "
                  "en heure légale de Paris ; mois et heures de Paris indexés à partir de 0 (janvier = 0, 0 h = 0)",
        "definitions": DEFINITIONS,
        "signes": SIGNES,
        "limites": LIMITES,
        "parametres": {
            "charges_plates_mw": list(quand.CHARGES_PLATES_MW),
            "heures_tendues": quand.N_HEURES_TENDUES,
            "monotone": f"{quand.N_MONOTONE_EXACT} premiers rangs exacts, puis un rang sur {quand.PAS_MONOTONE}, et "
                        "le dernier ; [rang, MW], rang 1 = heure de RN la plus élevée",
            "quantiles": "interpolation linéaire entre rangs (type 7 de Hyndman et Fan), sur les heures valides",
            "hiver": "novembre à mars (heure de Paris) ; part_dec_fev : décembre à février",
            "plages_7_11_17_21": "heures de Paris de début 7, 8, 9, 10, 17, 18, 19 et 20 ([7 h, 11 h[ et [17 h, 21 h[)",
            "plages_pp_rte": "[7 h, 10 h[ et [17 h, 20 h[ (plages PP du mécanisme de capacité 2026/2027, BP2025, "
                             "« Fonctionnement », note 38 p. 30)",
        },
        "colonnes_eco2mix": verifier_colonnes_eco2mix(table, pleines),
        "annees_exclues": {str(a): m for a, m in exclues.items()},
        "annees": annees,
        "matrices_rn": {"description": "RN (MW) par jour (lignes, dates de Paris) et heure de Paris de début "
                                       "(24 colonnes) ; null = heure inexistante ou donnée absente ; l'heure répétée "
                                       "du passage à l'heure d'hiver = moyenne de ses occurrences renseignées",
                        **matrices},
    }


def ecrire_quand(contenu: dict, chemin: Path) -> None:
    chemin.write_text(_dumps(contenu) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Chiffres calculés
# --------------------------------------------------------------------------


def source_quand(date_extraction: str) -> dict:
    return {
        "editeur": "Puissance de calcul (calcul du site)",
        "titre": "Indicateurs « Quand ? » (data/export/quand.json), calculés par `pc build` sur éCO2mix (RTE), les "
                 "indisponibilités REMIT d'EDF et les prix day-ahead (energy-charts)",
        "date_publication": date_extraction,
        "url": URL_QUAND,
        "consulte_le": date_extraction,
        "note": "date = dernière extraction des données sources ; recalculé à chaque `pc build`, contrôlé par `pc check`",
    }


def _fr(x: float, dec: int) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def _paris(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


def chiffres_calcules(q: dict, modulation: dict[int, dict] | None = None) -> dict[str, dict]:
    """Chiffres que le texte cite, lus dans quand.json (déjà arrondi), au schéma du référentiel.

    `modulation` : chiffres saisis de la modulation publiée, par année (recoupement d'ordre de
    grandeur de Σ J, non indépendant et d'une autre grandeur).
    """
    modulation = modulation or {}
    pleines = sorted(int(a) for a in q["annees"])
    annees = [a for a in pleines if a == ANNEE_CRISE or a >= PREMIERE_ANNEE_CHIFFRES]
    commun = {"source": SOURCE_QUAND, "page": "data/export/quand.json", "confiance": "B",
              "verification": "pc check", "produit_par": PRODUIT_PAR_PIPELINE, "perimetre": PERIMETRE}
    out: dict[str, dict] = {}
    for an in annees:
        a = q["annees"][str(an)]
        cr, jeu, td = a["charge_residuelle"], a["jeu_nucleaire"], a["heures_tendues"]
        cp = {c["x_mw"]: c for c in a["charges_plates"]}
        p = _paris(cr["max"]["debut_paris"])
        out[f"quand_rn_max_{an}"] = {
            **commun,
            "libelle": "Charge résiduelle nette du nucléaire disponible, maximum horaire de l'année",
            "valeur": round(cr["max"]["valeur_mw"] / 1000, 3), "unite": "GW", "grandeur": "charge_residuelle",
            "periode": f"{p:%Y-%m-%d}, {p.hour} h-{p.hour + 1} h (heure de Paris)",
            "citation": f"annees.{an}.charge_residuelle.max (heure UTC {cr['max']['heure_utc']})",
            "calcul": "consommation − éolien − solaire − nucléaire disponible déclaré (REMIT), MW moyens horaires ; "
                      f"maximum sur les {cr['heures_valides']} heures valides de l'année",
            "note": "carte des heures tendues, pas une marge ; valeur observée, pas un risque ; moyenne horaire, "
                    "donc inférieure à une pointe à la demi-heure",
        }
        recoupements = []
        if an in modulation:
            m = modulation[an]
            recoupements.append({
                "source": m["source"], "valeur": f"modulation nucléaire {m['valeur']} TWh (toutes causes, chiffre EDF)",
                "note": "autre grandeur (frontière modulation / indisponibilité fixée par EDF) : ordre de grandeur "
                        "seulement, l'écart est affiché par `pc check`", "independant": False})
        f3 = jeu.get("flamanville3")
        note_f3 = (f" ; comprend Flamanville 3 (EPR en essais, {_fr(f3['disponible_declare_epr_twh'], 2)} TWh "
                   f"déclarés disponibles) : hors EPR, entre {_fr(f3['somme_j_sans_disponible_epr_twh'], 1)} et "
                   f"{_fr(jeu['somme_twh'], 1)} TWh") if f3 else ""
        out[f"quand_j_{an}"] = {
            **commun,
            "libelle": "Nucléaire déclaré disponible et non produit, somme annuelle (borne haute)",
            "valeur": round(jeu["somme_twh"], 1), "unite": "TWh", "grandeur": "energie", "periode": str(an),
            "citation": f"annees.{an}.jeu_nucleaire.somme_twh",
            "calcul": "Σ max(0, nucléaire disponible déclaré − nucléaire produit) sur les heures de l'année, MW moyens "
                      "horaires × 1 h",
            **({"recoupements": recoupements} if recoupements else {}),
            "note": "au plus : réserves de services système, économie de combustible et baisse des exports non "
                    "déduites ; ce n'est pas la modulation publiée par EDF" + note_f3,
        }
        for gw in (1, 5, 10):
            c = cp[gw * 1000]
            out[f"quand_part_j_{gw}gw_{an}"] = {
                **commun,
                "libelle": f"Part de l'énergie d'une consommation plate de {gw} GW qui tiendrait dans le nucléaire "
                           "disponible non produit (au plus)",
                "valeur": round(c["part_dans_j"] * 100, 1), "unite": "%", "grandeur": "part", "periode": str(an),
                "citation": f"annees.{an}.charges_plates[x_mw = {gw * 1000}].part_dans_j",
                "calcul": f"Σ min({gw} 000 MW, J) / ({gw} 000 MW × heures où J est renseigné), "
                          "J = max(0, nucléaire disponible − produit)",
                "note": f"borne haute ; énergie ajoutée {_fr(c['energie_ajoutee_twh'], 2)} TWh sur l'année ; une "
                        "charge ajoutée serait d'abord servie en partie par moins d'exports",
            }
        for gw in (5, 10):
            c = cp[gw * 1000]
            out[f"quand_heures_rn_sup_max_{gw}gw_{an}"] = {
                **commun,
                "libelle": f"Heures où la charge résiduelle augmentée de {gw} GW dépasse son maximum observé de l'année",
                "valeur": c["heures_rn_plus_x_au_dessus_du_max"], "unite": "heures", "grandeur": "nombre",
                "periode": str(an),
                "citation": f"annees.{an}.charges_plates[x_mw = {gw * 1000}].heures_rn_plus_x_au_dessus_du_max",
                "calcul": f"nombre d'heures où RN + {gw} 000 MW > RN maximal de l'année "
                          f"({cr['max']['valeur_mw']} MW)",
                "note": "un écart à l'observé, pas une défaillance ni un risque de défaillance",
            }
        out[f"quand_top100_hiver_{an}"] = {
            **commun,
            "libelle": f"Part des {td['n']} heures de charge résiduelle la plus élevée tombant entre novembre et mars",
            "valeur": round(td["part_hiver_nov_mars"] * 100, 1), "unite": "%", "grandeur": "part", "periode": str(an),
            "citation": f"annees.{an}.heures_tendues.part_hiver_nov_mars",
            "calcul": f"heures tendues = les {td['n']} heures de RN la plus élevée ; mois en heure de Paris",
        }
        out[f"quand_top100_plages_{an}"] = {
            **commun,
            "libelle": f"Part des {td['n']} heures de charge résiduelle la plus élevée tombant entre 7 h et 11 h ou "
                       "entre 17 h et 21 h (heure de Paris)",
            "valeur": round(td["part_plages_7_11_17_21"] * 100, 1), "unite": "%", "grandeur": "part",
            "periode": str(an),
            "citation": f"annees.{an}.heures_tendues.part_plages_7_11_17_21",
            "calcul": "heures de Paris de début 7, 8, 9, 10, 17, 18, 19 et 20",
            "note": f"plages PP du mécanisme de capacité ([7 h, 10 h[ et [17 h, 20 h[) : "
                    f"{_fr(td['part_plages_pp_rte'] * 100, 1)} %",
        }
    return out
