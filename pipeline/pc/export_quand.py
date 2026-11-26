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
from .chiffres import PRODUIT_PAR_PIPELINE, arrondi_publie

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
    "nucleaire_disponible_reintegre": (quand.COLONNE_REINTEGRE, 0),
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

#: Production éolienne et solaire renoncée lors des prix négatifs, publiée par RTE (TWh), et
#: production écrêtée à la demande de RTE (recouvrement probable avec la première) : identifiants du
#: référentiel saisi, par année. Servent à `quand_ecretement_prix_negatif_AAAA` (limite « écrêtement »).
ECRETEMENT_PUBLIE = {2025: ("enr_renoncees_prix_negatifs_2025", "enr_ecretees_rte_2025")}
#: Détail de la production renoncée donné par RTE en note (TWh) : BE2025, note 19, « 1,3 TWh de
#: production éolienne terrestre et 1,6 TWh de production solaire », soit 2,9 TWh, que le texte
#: arrondit à « environ 3 TWh » (citation du référentiel, `enr_renoncees_prix_negatifs_2025`).
DETAIL_RENONCEE_TWH = {2025: (1.3, 1.6)}



#: Repères du réglage de froid du simulateur : gradient hivernal de RTE et pointe de consommation
#: estimée par RTE pour un froid comparable à ceux du début des années 2010 (identifiants du
#: référentiel saisi). Servent à `quand_froid_100gw_AAAA`.
FROID_PUBLIE = ("thermosensibilite_hiver_rte", "pointe_froids_2010_hiver_2026_2027")


def froid_du_referentiel(chiffres_saisis: dict[str, dict]) -> tuple[dict, dict] | None:
    """(gradient, pointe repère) du référentiel saisi, avec leur identifiant, ou None."""
    if not all(c in chiffres_saisis for c in FROID_PUBLIE):
        return None
    return tuple({**chiffres_saisis[c], "id": c} for c in FROID_PUBLIE)


def ecretement_du_referentiel(chiffres_saisis: dict[str, dict]) -> dict[int, tuple[dict, dict]]:
    """Paires (production renoncée, production écrêtée par RTE) du référentiel saisi, par année."""
    return {an: ({**chiffres_saisis[a], "id": a}, {**chiffres_saisis[b], "id": b})
            for an, (a, b) in ECRETEMENT_PUBLIE.items() if a in chiffres_saisis and b in chiffres_saisis}


#: Disponibilité déclarée de l'EPR au-delà de laquelle Σ J hors EPR est publié à part (TWh).
SEUIL_EPR_TWH = 0.1

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
                     "moyens horaires × 1 h / 10⁶. Nucléaire déclaré disponible et non produit : borne haute AVEC LA "
                     "DISPONIBILITÉ DÉCLARÉE PAR EDF, voir `limites.jeu_nucleaire` et `jeu_nucleaire_reintegre` ; ce "
                     "n'est PAS la « modulation » publiée par EDF",
    "jeu_nucleaire_reintegre": "J_r = max(0, nucléaire disponible réintégré − nucléaire produit), MW moyens : même calcul "
                               "que J, avec une disponibilité reconstruite en ignorant les arrêts et baisses COURTS "
                               "(moins de 7 jours, sans mention du combustible) qu'EDF déclare indisponibles POUR "
                               "MODULATION (arrêts économiques décidés au jour le jour ; règle : pc/remit.py, "
                               "MOTIF_MODULATION, DUREE_MAX_COURT_H ; aucun avant 2019) ; les arrêts longs pour "
                               "modulation, qui peuvent relever de la gestion du combustible, restent retranchés. J_r ≥ J à toute heure. "
                               "arrets_modulation_courts_twh = Σ (disponible réintégré − disponible déclaré) : énergie "
                               "que les arrêts courts retirent de la disponibilité déclarée, chevauchements traités ; "
                               "arrets_modulation_longs_twh : même chose pour les arrêts longs (calculé par le build "
                               "sur la reconstruction REMIT ; la série qui les réintègre n'est pas exportée). "
                               "charges_plates : part_dans_j et "
                               "part_dans_j_plancher recalculées avec J_r. Sensibilité au choix d'EDF, pas une capacité "
                               "physique : la contrainte d'énergie (combustible, calendrier des arrêts) reste la limite "
                               "nette",
    "charges_plates": "consommation supplémentaire constante de X MW toute l'année. energie_ajoutee_twh = X × heures "
                      "de l'année ; part_dans_j = Σ min(X, J) / (X × heures où J est renseigné) ; "
                      "heures_j_superieur_ou_egal_x = heures où J ≥ X ; heures_rn_plus_x_au_dessus_du_max = heures où "
                      "RN + X > RN maximal observé de l'année (strictement) ; rn_max_plus_x_mw = RN max + X ; "
                      "solde_echanges_moyen_heures_j_ge_x_mw = solde moyen des échanges physiques (positif = import, "
                      "négatif = export) aux heures où J ≥ X",
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
        "éolien et solaire observés = après écrêtement : aux heures de prix négatif, RN est plus haute que sans la "
        "production renoncée",
        "nucléaire disponible DÉCLARÉ (REMIT), pas une capacité physique garantie ; réserves de services système "
        "comprises",
        "hydraulique de lac et STEP : contraintes d'énergie (stock) ; leur puissance n'est pas disponible à toute heure",
        "les imports ne sont pas une marge ferme (vagues de froid communes à l'Europe)",
        "pointe horaire ≠ pointe à la demi-heure ou au quart d'heure ; consommation hors Corse",
    ],
    "jeu_nucleaire": list(quand.LIMITES_J),
    "charges_plates": [
        "heures_rn_plus_x_au_dessus_du_max compte des heures au-delà du maximum OBSERVÉ de l'année : un écart à "
        "l'observé, pas une défaillance ni un risque de défaillance. Le seuil est UNE heure : le compte vaut au "
        "moins 1 (l'heure du maximum se dépasse elle-même) et dépend de la forme du sommet de la monotone, pas de la "
        "tension ; d'où le seuil pluriannuel (heures_rn_plus_x_au_dessus_du_max_reference, maximum 2015-2025, "
        "`rn_max_pluriannuel`), que le système a couvert avec d'autres moyens (charbon, imports massifs, prix "
        "extrêmes)",
        "part_dans_j est un plafond AVEC LA DISPONIBILITÉ DÉCLARÉE PAR EDF (voir limites.jeu_nucleaire), lâche : "
        "part_dans_j_plancher en donne la sensibilité à un plancher non mobilisable (hypothèse du site) ; "
        "jeu_nucleaire_reintegre.charges_plates, la valeur en réintégrant les arrêts qu'EDF déclare indisponibles pour "
        "modulation ; qui servirait le reste de l'énergie dépend de la saturation des interconnexions, non "
        "déterminable sans les données des voisins",
        "une charge plate ne représente pas un data center réel (montée en charge, profil, effacement possible) ; "
        "RTE n'écrit pas qu'un GW de consommation à la pointe retire un GW de marge (contre-vérification du "
        "26/11/2026, n° 13)",
    ],
}


def encadrement_flamanville3(t: dict[str, list]) -> dict | None:
    """Σ J hors Flamanville 3, encadré : la production de l'EPR n'est pas séparée dans éCO2mix.

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
                   "la production de l'EPR (en essais en 2025) n'est pas séparée dans éCO2mix (elle l'est par groupe chez RTE et ENTSO-E, avec un compte)",
    }


def froid_annee(t: dict[str, list]) -> dict | None:
    """Épisode de froid du simulateur pour une année (`quand.episode_froid`, sur la RN des colonnes
    arrondies) et consommation horaire maximale dans l'épisode et hors de l'épisode (MW moyens, hors
    Corse). Avec un froid de F °C et un gradient G, la consommation maximale du scénario vaut
    max(consommation_max_episode_mw + F × G, consommation_max_hors_episode_mw)."""
    rn = [quand.charge_residuelle(*v) for v in zip(t["consommation"], t["eolien"], t["solaire"],
                                                     t["nucleaire_disponible"])]
    ep = quand.episode_froid(rn)
    if not ep:
        return None
    dedans = set(ep)
    c = t["consommation"]
    cep = [c[i] for i in ep if c[i] is not None]
    hors = [c[i] for i in range(len(c)) if i not in dedans and c[i] is not None]
    return {
        "episode_debut_utc": t["heure_utc"][ep[0]],
        "episode_fin_utc": t["heure_utc"][ep[-1]],
        "heures": len(ep),
        "consommation_max_episode_mw": max(cep) if cep else None,
        "consommation_max_hors_episode_mw": max(hors) if hors else None,
    }


#: Pas du réglage de froid du simulateur (°C), pour `froid_pour_depasser`.
PAS_FROID_C = 0.5


def froid_pour_depasser(f: dict, seuil_mw: float, gradient_mw_par_c: float, pas: float = PAS_FROID_C) -> float:
    """Plus petit froid réglable (multiple de `pas`, ≥ 0) qui porte la consommation horaire maximale
    du scénario strictement au-delà de `seuil_mw` (0 si l'année observée le dépasse déjà)."""
    if max(f["consommation_max_episode_mw"], f["consommation_max_hors_episode_mw"] or 0) > seuil_mw:
        return 0.0
    k = int((seuil_mw - f["consommation_max_episode_mw"]) // (pas * gradient_mw_par_c)) + 1
    return k * pas


def limites_chiffrees(annees: dict[str, dict]) -> list[str]:
    """Les limites de J, chiffrées sur la dernière année pleine (quand.json arrondi)."""
    an = max(annees)
    a = annees[an]
    pc = a["jeu_nucleaire"]["prix_chers"]
    c5 = next(c for c in a["charges_plates"] if c["x_mw"] == 5000)
    prod = a["production_nucleaire_twh"]
    lignes = []
    if pc["j_moyenne_mw"] is not None:
        lignes.append(f"plancher, chiffré ({an}) : J moyen {_fr(pc['j_moyenne_mw'] / 1000, 2)} GW aux {pc['heures']} "
                      f"heures où le prix day-ahead dépasse {pc['seuil_eur_mwh']} EUR/MWh (seuil choisi par le site) ; "
                      f"avec un plancher de {_fr(c5['plancher_mw'] / 1000, 1)} GW, la part tenue pour 5 GW passe de "
                      f"{_fr(c5['part_dans_j'] * 100, 0)} % à {_fr(c5['part_dans_j_plancher'] * 100, 0)} %")
    r = a.get("jeu_nucleaire_reintegre")
    if r:
        c5r = next(c for c in r["charges_plates"] if c["x_mw"] == 5000)
        lignes.append(f"disponibilité déclarée, chiffrée ({an}) : les arrêts qu'EDF déclare indisponibles pour modulation "
                      f"retirent {_fr(r['arrets_modulation_courts_twh'], 1)} TWh à la disponibilité pour les arrêts "
                      f"courts, {_fr(r.get('arrets_modulation_longs_twh', 0.0), 1)} TWh pour les arrêts longs (gestion "
                      f"du combustible, non réintégrés) ; en réintégrant les courts, Σ J "
                      f"passe de {_fr(a['jeu_nucleaire']['somme_twh'], 1)} à {_fr(r['somme_twh'], 1)} TWh et la part "
                      f"tenue pour 5 GW de {_fr(c5['part_dans_j'] * 100, 0)} % à {_fr(c5r['part_dans_j'] * 100, 0)} % "
                      f"({_fr(c5['part_dans_j_plancher'] * 100, 0)} % à {_fr(c5r['part_dans_j_plancher'] * 100, 0)} % "
                      "avec le plancher)")
    lignes.append(f"énergie, chiffrée ({an}) : 5 GW plats tenus dans J, ce serait {_fr(c5['energie_dans_j_twh'], 1)} TWh "
                  f"de nucléaire en plus de la production observée ({_fr(prod, 1)} TWh, somme éCO2mix), soit "
                  f"{_fr(prod + c5['energie_dans_j_twh'], 0)} TWh sur l'année, à comparer aux prévisions de production "
                  "(référentiel : prod_nucleaire_prevision_*)"
                  + (f" ; en réintégrant les arrêts courts pour modulation, {_fr(c5r['energie_dans_j_twh'], 1)} TWh en plus, "
                     f"soit {_fr(prod + c5r['energie_dans_j_twh'], 0)} TWh : la contrainte d'énergie reste la limite nette"
                     if r else ""))
    return lignes


def construire_quand(table: pl.DataFrame, extractions: dict, arrets_longs: dict[int, float] | None = None) -> dict:
    """Contenu de quand.json (arrondi) à partir de la table horaire exportée.

    `arrets_longs` : énergie (TWh) que les arrêts longs pour modulation retirent de la disponibilité
    déclarée, par année (calculée par le build sur la reconstruction REMIT, `build.arrets_modulation` ;
    la série qui les réintègre n'est pas exportée) ; recopiée dans
    `jeu_nucleaire_reintegre.arrets_modulation_longs_twh`, recalculée par `pc check`."""
    pleines, exclues = annees_pleines(table)
    tables = {an: table_annee(table, an) for an in pleines}
    # 1. maximum pluriannuel de RN (seuil extérieur à chaque année)
    pluri = quand.max_pluriannuel({str(an): quand.max_charge_residuelle(t) for an, t in tables.items()})
    reference = pluri["valeur_mw"] if pluri else None
    conso_pluri = quand.max_pluriannuel({str(an): quand.max_consommation(t) for an, t in tables.items()})
    # 2. indicateurs de chaque année
    annees = {}
    for an, t in tables.items():
        a = quand.indicateurs_annee(t, rn_max_reference_mw=reference)
        f3 = encadrement_flamanville3(t)
        if f3:
            a["jeu_nucleaire"]["flamanville3"] = f3
        prod = [v for v in t["nucleaire"] if v is not None]
        a["production_nucleaire_twh"] = sum(prod) / 1e6
        a["froid"] = froid_annee(t)
        if "jeu_nucleaire_reintegre" in a and arrets_longs is not None and an in arrets_longs:
            a["jeu_nucleaire_reintegre"]["arrets_modulation_longs_twh"] = arrets_longs[an]
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
        "limites": {**LIMITES, "jeu_nucleaire": LIMITES["jeu_nucleaire"] + limites_chiffrees(annees)},
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
            "plancher_j_mw": f"{quand.PLANCHER_J_MW} : HYPOTHÈSE DU SITE, retranchée à J pour part_dans_j_plancher et "
                             "energie_dans_j_plancher_twh (J' = max(0, J − plancher))",
            "seuil_prix_cher_eur_mwh": f"{quand.SEUIL_PRIX_CHER_EUR_MWH} : CHOISI PAR LE SITE ; jeu_nucleaire.prix_chers "
                                       "= J moyen aux heures où le prix day-ahead est strictement supérieur",
            "rn_max_reference": "maximum de RN sur les années pleines (rn_max_pluriannuel) ; "
                                "heures_rn_plus_x_au_dessus_du_max_reference = heures où RN + X le dépasse (strictement)",
            "production_nucleaire_twh": "somme de la production nucléaire éCO2mix de l'année (MW moyens horaires × 1 h)",
            "froid": "épisode de froid du simulateur (quand.episode_froid : les 168 heures consécutives de charge "
                     "résiduelle observée moyenne la plus élevée) et consommation horaire maximale dans l'épisode et "
                     "hors de l'épisode ; avec F °C et un gradient G, maximum du scénario = max(épisode + F × G, hors "
                     "épisode)",
            "consommation_max_pluriannuelle": "consommation horaire maximale (MW moyens sur l'heure, hors Corse) sur "
                                              "les années pleines ; repère de la limite « froid extrême », à comparer "
                                              "à la pointe historique de février 2012, publiée à la demi-heure",
        },
        "rn_max_pluriannuel": {**arrondir(pluri), "annees": f"{pleines[0]}-{pleines[-1]}"} if pluri else None,
        "consommation_max_pluriannuelle": ({**arrondir(conso_pluri), "annees": f"{pleines[0]}-{pleines[-1]}"}
                                           if conso_pluri else None),
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


#: Précision des valeurs publiées dans chiffres.json (décision du 26/11/2026) : GW à 0,1, TWh à
#: 0,1, % à l'entier, heures à l'unité. La valeur non arrondie, lue dans quand.json, est gardée
#: dans `valeur_calculee` ; `pc check` vérifie que `valeur` en est l'arrondi.
PRECISION = {"GW": 0.1, "TWh": 0.1, "%": 1, "heures": 1, "°C": 0.1}


def _valeur(x: float, unite: str) -> dict:
    pas = PRECISION[unite]
    x = round(x, 6)  # bruit flottant (30,349999… → 30,35) ; quand.json est lui-même arrondi
    return {"valeur": arrondi_publie(x, pas), "valeur_calculee": x, "precision": pas, "unite": unite}


def _fr(x: float, dec: int) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def _paris(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


def chiffres_calcules(q: dict, modulation: dict[int, dict] | None = None,
                      ecretement: dict[int, tuple[dict, dict]] | None = None,
                      froid: tuple[dict, dict] | None = None) -> dict[str, dict]:
    """Chiffres que le texte cite, lus dans quand.json (déjà arrondi), au schéma du référentiel.

    `modulation` : chiffres saisis de la modulation publiée, par année (recoupement d'ordre de
    grandeur de Σ J, non indépendant et d'une autre grandeur).
    `ecretement` : par année, les chiffres saisis (production renoncée lors des prix négatifs,
    production écrêtée à la demande de RTE), pour `ecretement_reparti`.
    `froid` : (gradient hivernal, pointe repère) saisis (`froid_du_referentiel`), pour
    `quand_froid_100gw_AAAA`.
    """
    modulation = modulation or {}
    ecretement = ecretement or {}
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
            **_valeur(cr["max"]["valeur_mw"] / 1000, "GW"), "grandeur": "charge_residuelle",
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
        f3 = f3 if f3 and f3["disponible_declare_epr_twh"] >= SEUIL_EPR_TWH else None  # sinon encadrement trivial
        note_f3 = (f" ; comprend Flamanville 3 (EPR en essais, {_fr(f3['disponible_declare_epr_twh'], 2)} TWh "
                   f"déclarés disponibles) : hors EPR, entre {_fr(f3['somme_j_sans_disponible_epr_twh'], 1)} et "
                   f"{_fr(jeu['somme_twh'], 1)} TWh") if f3 else ""
        jr = a.get("jeu_nucleaire_reintegre")
        cpr = {c["x_mw"]: c for c in jr["charges_plates"]} if jr else {}
        note_jr = (f" ; en réintégrant les arrêts courts qu'EDF déclare indisponibles pour modulation, "
                   f"{_fr(jr['somme_twh'], 1)} TWh") if jr else ""
        out[f"quand_j_{an}"] = {
            **commun,
            "libelle": "Nucléaire déclaré disponible et non produit, somme annuelle (borne haute, avec la disponibilité "
                       "déclarée par EDF)",
            **_valeur(jeu["somme_twh"], "TWh"), "grandeur": "energie", "periode": str(an),
            "citation": f"annees.{an}.jeu_nucleaire.somme_twh",
            "calcul": "Σ max(0, nucléaire disponible déclaré − nucléaire produit) sur les heures de l'année, MW moyens "
                      "horaires × 1 h",
            **({"recoupements": recoupements} if recoupements else {}),
            "note": "au plus, avec la disponibilité déclarée par EDF : réserves de services système (plancher non "
                    "mobilisable) et contrainte d'énergie (combustible, calendrier des arrêts) non déduites ; ce n'est pas "
                    "la modulation publiée par EDF" + note_jr + note_f3,
        }
        for gw in (1, 5, 10):
            c = cp[gw * 1000]
            out[f"quand_part_j_{gw}gw_{an}"] = {
                **commun,
                "libelle": f"Part de l'énergie d'une consommation plate de {gw} GW qui tiendrait dans le nucléaire "
                           "disponible non produit (au plus, avec la disponibilité déclarée par EDF)",
                **_valeur(c["part_dans_j"] * 100, "%"), "grandeur": "part", "periode": str(an),
                "citation": f"annees.{an}.charges_plates[x_mw = {gw * 1000}].part_dans_j",
                "calcul": f"Σ min({gw} 000 MW, J) / ({gw} 000 MW × heures où J est renseigné), "
                          "J = max(0, nucléaire disponible − produit)",
                "note": f"borne haute avec la disponibilité déclarée par EDF, lâche : avec un plancher non mobilisable "
                        f"de {_fr(c['plancher_mw'] / 1000, 0)} GW (hypothèse du site), "
                        f"{_fr(c['part_dans_j_plancher'] * 100, 0)} % ; "
                        + (f"en réintégrant les arrêts courts qu'EDF déclare indisponibles pour modulation, "
                           f"{_fr(cpr[gw * 1000]['part_dans_j'] * 100, 0)} % ; " if cpr else "")
                        + f"énergie ajoutée "
                        f"{_fr(c['energie_ajoutee_twh'], 2)} TWh sur l'année ; qui servirait le reste dépend de la "
                        "saturation des interconnexions, non déterminable sans les données des voisins",
            }
        for gw in (5, 10):
            c = cp[gw * 1000]
            out[f"quand_heures_rn_sup_max_{gw}gw_{an}"] = {
                **commun,
                "libelle": f"Heures où la charge résiduelle augmentée de {gw} GW dépasse son maximum observé de l'année",
                **_valeur(c["heures_rn_plus_x_au_dessus_du_max"], "heures"), "grandeur": "nombre",
                "periode": str(an),
                "citation": f"annees.{an}.charges_plates[x_mw = {gw * 1000}].heures_rn_plus_x_au_dessus_du_max",
                "calcul": f"nombre d'heures où RN + {gw} 000 MW > RN maximal de l'année "
                          f"({cr['max']['valeur_mw']} MW)",
                "note": "un écart à l'observé, pas une défaillance ni un risque de défaillance",
            }
        out[f"quand_top100_hiver_{an}"] = {
            **commun,
            "libelle": f"Part des {td['n']} heures de charge résiduelle la plus élevée tombant entre novembre et mars",
            **_valeur(td["part_hiver_nov_mars"] * 100, "%"), "grandeur": "part", "periode": str(an),
            "citation": f"annees.{an}.heures_tendues.part_hiver_nov_mars",
            "calcul": f"heures tendues = les {td['n']} heures de RN la plus élevée ; mois en heure de Paris",
        }
        out[f"quand_top100_plages_{an}"] = {
            **commun,
            "libelle": f"Part des {td['n']} heures de charge résiduelle la plus élevée tombant entre 7 h et 11 h ou "
                       "entre 17 h et 21 h (heure de Paris)",
            **_valeur(td["part_plages_7_11_17_21"] * 100, "%"), "grandeur": "part",
            "periode": str(an),
            "citation": f"annees.{an}.heures_tendues.part_plages_7_11_17_21",
            "calcul": "heures de Paris de début 7, 8, 9, 10, 17, 18, 19 et 20",
            "note": f"plages PP du mécanisme de capacité ([7 h, 10 h[ et [17 h, 20 h[) : "
                    f"{_fr(td['part_plages_pp_rte'] * 100, 0)} %",
        }
        out[f"quand_top100_plages_pp_{an}"] = {
            **commun,
            "libelle": f"Part des {td['n']} heures de charge résiduelle la plus élevée tombant dans les plages PP du "
                       "mécanisme de capacité, de 7 h à 10 h et de 17 h à 20 h (heure de Paris)",
            **_valeur(td["part_plages_pp_rte"] * 100, "%"), "grandeur": "part", "periode": str(an),
            "citation": f"annees.{an}.heures_tendues.part_plages_pp_rte",
            "calcul": "heures de Paris de début 7, 8, 9, 17, 18 et 19 ([7 h, 10 h[ et [17 h, 20 h[, plages PP 2026/2027, "
                      "BP2025, « Fonctionnement », note 38 p. 30)",
            "note": "une part du nombre d'heures tendues observées, pas du volume de défaillance simulé par RTE",
        }
        # Solde des échanges aux heures où J ≥ 5 GW
        c5 = cp[5000]
        if c5["solde_echanges_moyen_heures_j_ge_x_mw"] is not None:
            out[f"quand_solde_j5_{an}"] = {
                **commun,
                "libelle": "Solde moyen des échanges physiques aux heures où au moins 5 GW de nucléaire déclaré "
                           "disponible ne sont pas produits (positif = import, négatif = export)",
                **_valeur(c5["solde_echanges_moyen_heures_j_ge_x_mw"] / 1000, "GW"), "grandeur": "puissance_moyenne",
                "periode": str(an),
                "citation": f"annees.{an}.charges_plates[x_mw = 5000].solde_echanges_moyen_heures_j_ge_x_mw",
                "calcul": "moyenne de `ech_physiques` d'éCO2mix sur les heures où J = max(0, nucléaire disponible "
                          "− produit) ≥ 5 000 MW ; signe d'éCO2mix conservé (positif = import)",
                "note": f"sur {c5['heures_j_superieur_ou_egal_x']} heures de l'année ; négatif : à ces heures la "
                        "France exporte déjà ; qui servirait une charge ajoutée (nucléaire inemployé ou moins "
                        "d'exports) dépend de la saturation des interconnexions, non déterminable sans les données "
                        "des voisins",
            }
        out[f"quand_heures_j5_{an}"] = {
            **commun,
            "libelle": "Heures où au moins 5 GW de nucléaire déclaré disponible ne sont pas produits",
            **_valeur(c5["heures_j_superieur_ou_egal_x"], "heures"), "grandeur": "nombre", "periode": str(an),
            "citation": f"annees.{an}.charges_plates[x_mw = 5000].heures_j_superieur_ou_egal_x",
            "calcul": "nombre d'heures où J = max(0, nucléaire disponible déclaré − produit) ≥ 5 000 MW",
            "note": "heures où une consommation plate de 5 GW tiendrait entièrement dans J (borne haute, avec la "
                    "disponibilité déclarée par EDF)",
        }
        # Couverture moyenne des heures tendues (termes de RN, MW moyens → GW)
        cm = td["couverture_moyenne_mw"]
        heures_td = f"les {td['n']} heures de charge résiduelle la plus élevée de l'année"
        commun_couv = {**commun, "grandeur": "puissance_moyenne", "periode": str(an),
                       "note": "moyenne observée, pas une capacité disponible ; la somme des termes de couverture "
                               f"(quand.json) redonne la charge résiduelle moyenne de ces heures, "
                               f"{_fr(td['rn_moyenne_mw'] / 1000, 1)} GW"}
        out[f"quand_top100_solde_{an}"] = {
            **commun_couv,
            "libelle": f"Solde moyen des échanges physiques sur {heures_td} (positif = import, négatif = export)",
            **_valeur(cm["ech_physiques"] / 1000, "GW"),
            "citation": f"annees.{an}.heures_tendues.couverture_moyenne_mw.ech_physiques",
            "calcul": "moyenne de `ech_physiques` d'éCO2mix sur ces heures ; signe d'éCO2mix conservé : positif = "
                      "la France importe, négatif = elle exporte (ses moyens couvrent alors aussi les exports)",
        }
        out[f"quand_top100_gaz_{an}"] = {
            **commun_couv,
            "libelle": f"Production au gaz moyenne sur {heures_td}",
            **_valeur(cm["gaz"] / 1000, "GW"),
            "citation": f"annees.{an}.heures_tendues.couverture_moyenne_mw.gaz",
            "calcul": "moyenne de `gaz` d'éCO2mix (cycles combinés, TAC, cogénération, autres) sur ces heures",
        }
        out[f"quand_top100_lacs_step_{an}"] = {
            **commun_couv,
            "libelle": f"Hydraulique de lacs et turbinage des STEP, production moyenne sur {heures_td}",
            **_valeur((cm["hydraulique_lacs"] + cm["hydraulique_step_turbinage"]) / 1000, "GW"),
            "citation": f"annees.{an}.heures_tendues.couverture_moyenne_mw.hydraulique_lacs + "
                        "hydraulique_step_turbinage",
            "calcul": "moyenne de `hydraulique_lacs` + moyenne de `hydraulique_step_turbinage` d'éCO2mix sur ces "
                      "heures ; le pompage des STEP (consommation) n'est pas déduit, il figure à part dans quand.json "
                      f"({_fr(cm['pompage'] / 1000, 2)} GW)",
        }
        out[f"quand_top100_fil_eau_{an}"] = {
            **commun_couv,
            "libelle": f"Hydraulique au fil de l'eau et éclusées, production moyenne sur {heures_td}",
            **_valeur(cm["hydraulique_fil_eau_eclusee"] / 1000, "GW"),
            "citation": f"annees.{an}.heures_tendues.couverture_moyenne_mw.hydraulique_fil_eau_eclusee",
            "calcul": "moyenne de `hydraulique_fil_eau_eclusee` d'éCO2mix sur ces heures",
        }
        # Borne basse de Σ J hors EPR, quand l'EPR pèse (≥ 0,1 TWh déclaré disponible)
        if f3 and f3["disponible_declare_epr_twh"] >= SEUIL_EPR_TWH:
            out[f"quand_j_{an}_hors_epr"] = {
                **commun,
                "libelle": "Nucléaire déclaré disponible et non produit, hors disponibilité de l'EPR de Flamanville 3 "
                           "(borne basse)",
                **_valeur(f3["somme_j_sans_disponible_epr_twh"], "TWh"), "grandeur": "energie", "periode": str(an),
                "citation": f"annees.{an}.jeu_nucleaire.flamanville3.somme_j_sans_disponible_epr_twh",
                "calcul": "Σ max(0, nucléaire disponible déclaré − disponible déclaré de l'EPR − nucléaire produit) ; "
                          "la production de l'EPR, non séparée dans éCO2mix, est retranchée avec le reste : c'est une borne "
                          "basse de Σ J hors EPR",
                "note": f"Σ J hors EPR est compris entre cette valeur et Σ J ({_fr(jeu['somme_twh'], 1)} TWh, EPR "
                        f"compris) ; EPR en essais, {_fr(f3['disponible_declare_epr_twh'], 2)} TWh déclarés "
                        "disponibles sur l'année",
            }
    out.update(chiffres_calcules_toutes_annees(q, commun))
    if froid:
        out.update(chiffres_froid(q, froid, commun))
    for an, (renoncee, ecretee) in sorted(ecretement.items()):
        if str(an) in q["annees"]:
            out[f"quand_ecretement_prix_negatif_{an}"] = ecretement_reparti(q, an, renoncee, ecretee, commun)
    return out


def chiffres_froid(q: dict, froid: tuple[dict, dict], commun: dict) -> dict[str, dict]:
    """Repère du réglage de froid (relecture adverse du 26/11/2026, F1) : pour chaque année pleine, le
    plus petit froid réglable (pas de 0,5 °C) qui porte la consommation horaire maximale du scénario
    au-delà de la pointe que RTE estime pour un froid comparable à ceux du début des années 2010."""
    gradient, pointe = froid
    if gradient["unite"] != "MW/°C" or pointe["unite"] != "GW":
        raise ValueError("froid : unités attendues MW/°C et GW")
    g, seuil = float(gradient["valeur"]), float(pointe["valeur"]) * 1000
    out: dict[str, dict] = {}
    for an_s, a in q["annees"].items():
        f = a.get("froid")
        if not f or f["consommation_max_episode_mw"] is None:
            continue
        x = froid_pour_depasser(f, seuil, g)
        ep0, ep1 = _paris_utc(f["episode_debut_utc"]), _paris_utc(f["episode_fin_utc"])
        out[f"quand_froid_100gw_{an_s}"] = {
            **commun,
            "libelle": f"Froid supplémentaire du simulateur à partir duquel la consommation horaire maximale de {an_s} "
                       f"dépasse {_fr(seuil / 1000, 0)} GW",
            **_valeur(x, "°C"), "grandeur": "ecart_temperature", "periode": an_s,
            "perimetre": f"épisode de froid du simulateur de {an_s} : les {f['heures']} heures consécutives de charge "
                         f"résiduelle observée la plus élevée, du {ep0:%d/%m} au {ep1:%d/%m/%Y} ; consommation hors Corse, "
                         "moyenne horaire ; degrés AJOUTÉS au froid de ces jours, pas un écart aux normales",
            "citation": f"annees.{an_s}.froid (consommation maximale dans l'épisode "
                        f"{f['consommation_max_episode_mw']} MW, hors de l'épisode {f['consommation_max_hors_episode_mw']} "
                        f"MW) ; gradient {gradient['id']} ; seuil {pointe['id']}",
            "calcul": f"plus petit multiple de {_fr(PAS_FROID_C, 1)} °C tel que consommation maximale de l'épisode + froid × "
                      f"{_fr(g, 0)} MW/°C > {_fr(seuil, 0)} MW (strictement)",
            "note": f"repère : RTE estime que les pointes de l'hiver 2026-2027 resteraient « sensiblement inférieures » à "
                    f"{_fr(seuil / 1000, 0)} GW avec des froids comparables à ceux du début des années 2010 ; le même "
                    "réglage ne représente pas le même froid d'une année à l'autre (l'épisode a déjà son propre froid)",
        }
    return out


def _paris_utc(iso: str) -> datetime:
    """Heure UTC ISO (« 2025-01-13T07:00Z ») → même instant en heure de Paris."""
    from zoneinfo import ZoneInfo
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ZoneInfo(TZ_PARIS))


def ecretement_reparti(q: dict, an: int, renoncee: dict, ecretee: dict, commun: dict) -> dict:
    """Limite « écrêtement » de « Quand ? » (niveau « estimer », décision du 26/11/2026) : la production
    éolienne et solaire renoncée lors des prix négatifs, publiée par RTE pour l'année, répartie sur
    les heures à prix day-ahead strictement négatif de la même année. MWh ÷ heures = MW moyens.

    Sens de la borne : à ces heures, l'éolien et le solaire observés sont nets de la production
    renoncée, donc RN observée = RN sans écrêtement + production renoncée de l'heure ≥ RN sans
    écrêtement. La moyenne de l'écart sur ces heures est au plus la production renoncée ÷ heures,
    si l'estimation de RTE est complète : une partie a pu être renoncée hors de ces heures (quarts
    d'heure négatifs d'une heure positive depuis le passage au pas de 15 min), ce qui ne peut que
    baisser la moyenne. Ce n'est pas une borne heure par heure.
    """
    if renoncee["unite"] != "TWh" or ecretee["unite"] != "TWh":
        raise ValueError("production renoncée ou écrêtée : unité attendue TWh")
    a = q["annees"][str(an)]
    n = a["prix"]["heures_negatif"]
    e_twh = float(renoncee["valeur"])
    gw = e_twh * 1e6 / n / 1000
    rn_neg = a["prix"]["rn_moyenne_prix_negatif_mw"]
    return {
        **commun,
        "libelle": "Écart moyen de la charge résiduelle observée aux heures à prix négatif dû à la production "
                   "éolienne et solaire renoncée (borne haute)",
        **_valeur(gw, "GW"), "grandeur": "puissance_moyenne", "periode": str(an),
        "perimetre": f"heures à prix day-ahead France strictement négatif de {an} ; production renoncée estimée par "
                     "RTE (éolien terrestre et solaire) ; charge résiduelle du site (France continentale hors Corse)",
        "citation": f"{renoncee['libelle']} ({_fr(e_twh, 1)} TWh, référentiel {renoncee['id']}) ; "
                    f"annees.{an}.prix.heures_negatif ({n} h)",
        "calcul": f"production éolienne et solaire renoncée lors des épisodes de prix négatifs (estimation RTE, "
                  f"{_fr(e_twh, 1)} TWh, × 10⁶ en MWh) ÷ {n} heures à prix day-ahead strictement négatif "
                  "de l'année = MW moyens sur ces heures ; la charge résiduelle observée est plus haute d'autant, en "
                  "moyenne, que sans la production renoncée",
        "note": "borne haute d'une moyenne, pas une valeur heure par heure (la production renoncée se concentre sur les "
                "heures de forte production) ; borne si toute la production renoncée tombe à ces heures : une partie a "
                "pu l'être à des quarts d'heure négatifs d'heures dont la moyenne ne l'est pas, ce qui baisse la "
                f"moyenne ; RTE donne « environ » {f'{e_twh:g}'.replace('.', ',')} TWh : 0,1 TWh de plus ou de moins déplace la "
                f"moyenne de {_fr(0.1e6 / n / 1000, 1)} GW"
                + (f" ; le détail de la note 19 de RTE ({' + '.join(_fr(x, 1) for x in DETAIL_RENONCEE_TWH[an])} TWh, "
                   f"éolien terrestre et solaire) donne {_fr(sum(DETAIL_RENONCEE_TWH[an]), 1)} TWh, soit "
                   f"{_fr(sum(DETAIL_RENONCEE_TWH[an]) * 1e6 / n / 1000, 1)} GW ; l'éolien en mer n'est pas dans "
                   "l'estimation de RTE, alors qu'il est dans l'éolien observé (effet probablement négligeable)"
                   if an in DETAIL_RENONCEE_TWH else "")
                + f" ; les {_fr(float(ecretee['valeur']), 1)} TWh "
                "écrêtés à la demande de RTE, qui recouvrent probablement en partie ce volume, ajouteraient au plus "
                f"{_fr(float(ecretee['valeur']) * 1e6 / n / 1000, 1)} GW ; charge résiduelle moyenne observée à ces "
                f"heures : {_fr(rn_neg / 1000, 1).replace('-', '−')} GW, soit de l'ordre de "
                f"{_fr(rn_neg / 1000 - gw, 1).replace('-', '−')} GW sans la "
                "production renoncée : le surplus réel de ces heures est plus grand que celui que montre la charge "
                "résiduelle, pas plus petit",
    }


def chiffres_calcules_toutes_annees(q: dict, commun: dict) -> dict[str, dict]:
    """Chiffres calculés pour chaque année pleine (2015-2025) et le maximum pluriannuel (relecture
    adverse de « Quand ? », 26/11/2026, F1 à F3 et P3)."""
    out: dict[str, dict] = {}
    pluri = q.get("rn_max_pluriannuel")
    if pluri:
        p = _paris(pluri["debut_paris"])
        out["quand_rn_max_pluri"] = {
            **commun,
            "libelle": f"Charge résiduelle nette du nucléaire disponible, maximum horaire sur {pluri['annees']}",
            **_valeur(pluri["valeur_mw"] / 1000, "GW"), "grandeur": "charge_residuelle",
            "periode": f"{p:%Y-%m-%d}, {p.hour} h-{p.hour + 1} h (heure de Paris)",
            "perimetre": PERIMETRE.replace("année civile en heure de Paris", f"années pleines {pluri['annees']}"),
            "citation": f"rn_max_pluriannuel (heure UTC {pluri['heure_utc']})",
            "calcul": "maximum des maxima annuels de RN = consommation − éolien − solaire − nucléaire disponible "
                      "déclaré ; à égalité, l'heure la plus ancienne",
            "note": "couvert à l'époque avec d'autres moyens que ceux d'aujourd'hui (charbon, imports, prix) ; une "
                    "valeur observée, pas un risque",
        }
    cmax = q.get("consommation_max_pluriannuelle")
    if cmax:
        p = _paris(cmax["debut_paris"])
        out["quand_conso_max_pluri"] = {
            **commun,
            "libelle": f"Consommation d'électricité, maximum horaire sur {cmax['annees']}",
            **_valeur(cmax["valeur_mw"] / 1000, "GW"), "grandeur": "pointe_consommation",
            "periode": f"{p:%Y-%m-%d}, {p.hour} h-{p.hour + 1} h (heure de Paris)",
            "perimetre": PERIMETRE.replace("année civile en heure de Paris", f"années pleines {cmax['annees']}"),
            "citation": f"consommation_max_pluriannuelle (heure UTC {cmax['heure_utc']})",
            "calcul": "maximum des consommations horaires éCO2mix (moyenne des deux demi-heures de l'heure) sur les "
                      "années pleines ; à égalité, l'heure la plus ancienne",
            "note": "moyenne horaire : une pointe à la demi-heure est plus haute (la pointe historique de février 2012 "
                    "est publiée à la demi-heure) ; consommation hors Corse",
        }
    for an_s, a in q["annees"].items():
        an = int(an_s)
        cr, jeu, td = a["charge_residuelle"], a["jeu_nucleaire"], a["heures_tendues"]
        cp = {c["x_mw"]: c for c in a["charges_plates"]}
        out[f"quand_top100_rn_moyenne_{an}"] = {
            **commun,
            "libelle": f"Charge résiduelle nette du nucléaire disponible, moyenne des {td['n']} heures les plus tendues "
                       "de l'année",
            **_valeur(td["rn_moyenne_mw"] / 1000, "GW"), "grandeur": "charge_residuelle", "periode": an_s,
            "citation": f"annees.{an}.heures_tendues.rn_moyenne_mw",
            "calcul": f"moyenne de RN sur les {td['n']} heures de RN la plus élevée de l'année",
            "note": "mesure moins dépendante d'une seule heure que le maximum",
        }
        if pluri:
            for gw in (5, 10):
                c = cp[gw * 1000]
                out[f"quand_heures_rn_sup_max_pluri_{gw}gw_{an}"] = {
                    **commun,
                    "libelle": f"Heures où la charge résiduelle augmentée de {gw} GW dépasse son maximum observé sur "
                               f"{pluri['annees']}",
                    **_valeur(c["heures_rn_plus_x_au_dessus_du_max_reference"], "heures"), "grandeur": "nombre",
                    "periode": an_s,
                    "citation": f"annees.{an}.charges_plates[x_mw = {gw * 1000}]"
                                ".heures_rn_plus_x_au_dessus_du_max_reference",
                    "calcul": f"nombre d'heures de {an} où RN + {gw} 000 MW > {pluri['valeur_mw']} MW (maximum de RN sur "
                              f"{pluri['annees']}, atteint le {_paris(pluri['debut_paris']):%d/%m/%Y})",
                    "note": "un écart à l'observé, pas une défaillance ; ce maximum (février 2018) a été couvert avec "
                            "du charbon, du fioul et des importations importantes",
                }
        pc = jeu["prix_chers"]
        out[f"quand_heures_prix_chers_{an}"] = {
            **commun,
            "libelle": f"Heures où le prix day-ahead dépasse {pc['seuil_eur_mwh']} €/MWh (seuil choisi par le site)",
            **_valeur(pc["heures"], "heures"), "grandeur": "nombre", "periode": an_s,
            "citation": f"annees.{an}.jeu_nucleaire.prix_chers.heures",
            "calcul": f"heures où le prix day-ahead France est strictement supérieur à {pc['seuil_eur_mwh']} €/MWh et "
                      "où J est renseigné",
        }
        if pc["j_moyenne_mw"] is not None:
            out[f"quand_j_heures_cheres_{an}"] = {
                **commun,
                "libelle": "Nucléaire déclaré disponible et non produit, moyenne aux heures où le prix day-ahead "
                           f"dépasse {pc['seuil_eur_mwh']} €/MWh",
                **_valeur(pc["j_moyenne_mw"] / 1000, "GW"), "grandeur": "puissance_moyenne", "periode": an_s,
                "citation": f"annees.{an}.jeu_nucleaire.prix_chers.j_moyenne_mw",
                "calcul": f"moyenne de J = max(0, nucléaire disponible − produit) sur les {pc['heures']} heures où le "
                          f"prix est strictement supérieur à {pc['seuil_eur_mwh']} €/MWh (seuil choisi par le site)",
                "note": "J ne tombe pas à zéro même quand l'énergie est chère : réserves, rampes, fins de cycle, "
                        "décalage entre déclaration et puissance réelle ; cette part n'est pas mobilisable",
            }
        jr = a.get("jeu_nucleaire_reintegre")
        cpr = {c["x_mw"]: c for c in jr["charges_plates"]} if jr else {}
        for gw in (5, 10):
            c = cp[gw * 1000]
            out[f"quand_part_j_plancher_{gw}gw_{an}"] = {
                **commun,
                "libelle": f"Part de l'énergie d'une consommation plate de {gw} GW qui tiendrait dans le nucléaire "
                           f"disponible non produit, après un plancher non mobilisable de "
                           f"{_fr(c['plancher_mw'] / 1000, 0)} GW (hypothèse du site)",
                **_valeur(c["part_dans_j_plancher"] * 100, "%"), "grandeur": "part", "periode": an_s,
                "citation": f"annees.{an}.charges_plates[x_mw = {gw * 1000}].part_dans_j_plancher",
                "calcul": f"Σ min({gw} 000 MW, max(0, J − {c['plancher_mw']} MW)) / ({gw} 000 MW × heures où J est "
                          "renseigné)",
                "note": f"sans plancher : {_fr(c['part_dans_j'] * 100, 0)} % ; avec la disponibilité déclarée par EDF"
                        + (f" (en réintégrant les arrêts courts qu'EDF déclare indisponibles pour modulation : "
                           f"{_fr(cpr[gw * 1000]['part_dans_j_plancher'] * 100, 0)} %)" if cpr else "")
                        + " ; le plancher est une hypothèse du site, pas une donnée publiée",
            }
            out[f"quand_energie_j_{gw}gw_{an}"] = {
                **commun,
                "libelle": f"Énergie d'une consommation plate de {gw} GW qui tiendrait dans le nucléaire disponible non "
                           "produit (nucléaire produit en plus, au plus, avec la disponibilité déclarée par EDF)",
                **_valeur(c["energie_dans_j_twh"], "TWh"), "grandeur": "energie", "periode": an_s,
                "citation": f"annees.{an}.charges_plates[x_mw = {gw * 1000}].energie_dans_j_twh",
                "calcul": f"Σ min({gw} 000 MW, J) sur les heures de l'année, MW moyens horaires × 1 h",
                "note": f"production nucléaire observée {_fr(a['production_nucleaire_twh'], 1)} TWh (somme éCO2mix) : "
                        f"ce serait {_fr(a['production_nucleaire_twh'] + c['energie_dans_j_twh'], 0)} TWh sur l'année, "
                        "si le combustible et le calendrier des arrêts le permettaient",
            }
        if jr:
            out.update(chiffres_reintegres(an, a, jr, commun))
    return out


#: Formule commune des chiffres réintégrés (définition de J_r).
J_REINTEGRE = ("J_r = max(0, nucléaire disponible réintégré − nucléaire produit), le disponible réintégré étant reconstruit "
               "depuis REMIT avec les mêmes règles que le disponible déclaré, en ignorant les arrêts et baisses de moins "
               "de 7 jours, sans mention du combustible, qu'EDF déclare pour modulation (pc/remit.py, MOTIF_MODULATION, "
               "DUREE_MAX_COURT_H)")
NOTE_REINTEGRE = ("EDF déclare ces arrêts courts, décidés au jour le jour, comme indisponibles (le plus souvent : « la "
                  "tranche sera redémarrée si les conditions économiques le justifient ») ; les arrêts longs pour "
                  "modulation, qui peuvent relever de la gestion du combustible, restent retranchés ; réintégrer les courts "
                  "mesure la sensibilité au choix de déclaration d'EDF, ce n'est pas une capacité physique : le "
                  "combustible et le calendrier des arrêts limitent toujours l'énergie")


def chiffres_reintegres(an: int, a: dict, jr: dict, commun: dict) -> dict[str, dict]:
    """Variantes réintégrant les arrêts courts pour modulation (quand.json, `jeu_nucleaire_reintegre`) :
    Σ J_r, énergie retirée par les arrêts courts et par les arrêts longs (non réintégrés), parts et
    énergie d'une charge plate de 5 et 10 GW. Les chiffres avec la disponibilité déclarée ne changent pas."""
    an_s = str(an)
    cp = {c["x_mw"]: c for c in a["charges_plates"]}
    cpr = {c["x_mw"]: c for c in jr["charges_plates"]}
    jeu = a["jeu_nucleaire"]
    out: dict[str, dict] = {
        f"quand_arrets_modulation_courts_{an}": {
            **commun,
            "libelle": "Énergie retirée de la disponibilité nucléaire déclarée par les arrêts et baisses courts (moins de "
                       "7 jours) qu'EDF déclare indisponibles pour modulation",
            **_valeur(jr["arrets_modulation_courts_twh"], "TWh"), "grandeur": "energie", "periode": an_s,
            "citation": f"annees.{an}.jeu_nucleaire_reintegre.arrets_modulation_courts_twh",
            "calcul": "Σ (disponible réintégré − disponible déclaré) sur les heures de l'année, MW moyens horaires × 1 h ; "
                      "chevauchements traités (règle du minimum d'EDF) ; identification : pc/remit.py, MOTIF_MODULATION, "
                      "DUREE_MAX_COURT_H",
            "note": "déclarés comme indisponibilités planifiées ; aucun avant 2019 ; réintégrés dans J_r ; "
                    + (f"arrêts longs de la même année, non réintégrés : {_fr(jr['arrets_modulation_longs_twh'], 1)} TWh ; "
                       if "arrets_modulation_longs_twh" in jr else "")
                    + NOTE_REINTEGRE,
        },
    }
    if "arrets_modulation_longs_twh" in jr:
        out[f"quand_arrets_modulation_longs_{an}"] = {
            **commun,
            "libelle": "Énergie retirée de la disponibilité nucléaire déclarée par les arrêts longs (7 jours ou plus, ou "
                       "parlant de combustible) qu'EDF déclare indisponibles pour modulation",
            **_valeur(jr["arrets_modulation_longs_twh"], "TWh"), "grandeur": "energie", "periode": an_s,
            "citation": f"annees.{an}.jeu_nucleaire_reintegre.arrets_modulation_longs_twh",
            "calcul": "Σ (disponible réintégrant tous les arrêts pour modulation − disponible réintégrant les arrêts courts) "
                      "sur les heures de l'année, MW moyens horaires × 1 h ; chevauchements traités ; calculé par `pc "
                      "build` sur la reconstruction REMIT (meta.json, nucleaire_disponible.arrets_modulation), "
                      "recalculé par `pc check`",
            "note": "non réintégrés dans J_r : ces arrêts, d'une semaine à plusieurs mois et souvent annoncés des semaines "
                    "ou des mois à l'avance, peuvent relever de la gestion du combustible (contrainte d'énergie), comme les "
                    "arrêts « pour économie de combustible » ; aucun avant 2019",
        }
    out[f"quand_j_reintegre_{an}"] = {
        **commun,
        "libelle": "Nucléaire disponible non produit, en réintégrant les arrêts courts qu'EDF déclare indisponibles "
                   "pour modulation, somme annuelle",
        **_valeur(jr["somme_twh"], "TWh"), "grandeur": "energie", "periode": an_s,
        "citation": f"annees.{an}.jeu_nucleaire_reintegre.somme_twh",
        "calcul": f"Σ J_r sur les heures de l'année, MW moyens horaires × 1 h ; {J_REINTEGRE}",
        "note": f"avec la disponibilité déclarée : {_fr(jeu['somme_twh'], 1)} TWh ; " + NOTE_REINTEGRE
                + " ; ce n'est pas la modulation publiée par EDF",
    }
    for gw in (5, 10):
        c, cr = cp[gw * 1000], cpr[gw * 1000]
        out[f"quand_part_j_reintegre_{gw}gw_{an}"] = {
            **commun,
            "libelle": f"Part de l'énergie d'une consommation plate de {gw} GW qui tiendrait dans le nucléaire "
                       "disponible non produit, en réintégrant les arrêts courts qu'EDF déclare indisponibles pour modulation "
                       "(au plus)",
            **_valeur(cr["part_dans_j"] * 100, "%"), "grandeur": "part", "periode": an_s,
            "citation": f"annees.{an}.jeu_nucleaire_reintegre.charges_plates[x_mw = {gw * 1000}].part_dans_j",
            "calcul": f"Σ min({gw} 000 MW, J_r) / ({gw} 000 MW × heures où J_r est renseigné) ; {J_REINTEGRE}",
            "note": f"avec la disponibilité déclarée : {_fr(c['part_dans_j'] * 100, 0)} % ; avec un plancher non "
                    f"mobilisable de {_fr(c['plancher_mw'] / 1000, 0)} GW (hypothèse du site) : "
                    f"{_fr(cr['part_dans_j_plancher'] * 100, 0)} % ; " + NOTE_REINTEGRE,
        }
        out[f"quand_part_j_plancher_reintegre_{gw}gw_{an}"] = {
            **commun,
            "libelle": f"Part de l'énergie d'une consommation plate de {gw} GW qui tiendrait dans le nucléaire "
                       "disponible non produit, en réintégrant les arrêts courts qu'EDF déclare indisponibles pour modulation, "
                       f"après un plancher non mobilisable de {_fr(c['plancher_mw'] / 1000, 0)} GW (hypothèse du site)",
            **_valeur(cr["part_dans_j_plancher"] * 100, "%"), "grandeur": "part", "periode": an_s,
            "citation": f"annees.{an}.jeu_nucleaire_reintegre.charges_plates[x_mw = {gw * 1000}].part_dans_j_plancher",
            "calcul": f"Σ min({gw} 000 MW, max(0, J_r − {c['plancher_mw']} MW)) / ({gw} 000 MW × heures où J_r est "
                      f"renseigné) ; {J_REINTEGRE}",
            "note": f"avec la disponibilité déclarée : {_fr(c['part_dans_j_plancher'] * 100, 0)} % ; le plancher est une "
                    "hypothèse du site, pas une donnée publiée ; " + NOTE_REINTEGRE,
        }
        out[f"quand_energie_j_reintegre_{gw}gw_{an}"] = {
            **commun,
            "libelle": f"Énergie d'une consommation plate de {gw} GW qui tiendrait dans le nucléaire disponible non "
                       "produit, en réintégrant les arrêts courts qu'EDF déclare indisponibles pour modulation (nucléaire "
                       "produit en plus, au plus)",
            **_valeur(cr["energie_dans_j_twh"], "TWh"), "grandeur": "energie", "periode": an_s,
            "citation": f"annees.{an}.jeu_nucleaire_reintegre.charges_plates[x_mw = {gw * 1000}].energie_dans_j_twh",
            "calcul": f"Σ min({gw} 000 MW, J_r) sur les heures de l'année, MW moyens horaires × 1 h ; {J_REINTEGRE}",
            "note": f"production nucléaire observée {_fr(a['production_nucleaire_twh'], 1)} TWh (somme éCO2mix) : ce "
                    f"serait {_fr(a['production_nucleaire_twh'] + cr['energie_dans_j_twh'], 0)} TWh sur l'année, si le "
                    "combustible et le calendrier des arrêts le permettaient",
        }
    return out
