"""Contrôles de cohérence ENTSO-E (appelés par `pc check`, pc/check.py).

Ces contrôles détectent une **rupture du pipeline** (lecture XML, règle A03, horodatage, signe,
série oubliée), ils ne « valident » pas ENTSO-E : chaque tolérance est calée sur l'écart
mesuré entre deux sources indépendantes, avec une marge, et sur l'effet qu'aurait une erreur
de lecture typique (décalage d'une heure, frontière manquante, signe inversé). Mesures et
justifications : docs/spike/entsoe-pipeline.md § Contrôles.

Sans données ENTSO-E (pas de jeton, CI) : un seul résultat INFO, pas d'échec.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from . import entsoe, entsoe_derive
from .build import annee_paris, charger_prix
from .sources import lire_manifeste

# --------------------------------------------------------------------------
# Références et tolérances
# --------------------------------------------------------------------------

#: Prix FR : ENTSO-E et energy-charts publient le même résultat SDAC au centime ; tout écart
#: au-delà de l'arrondi est une erreur de lecture ou d'horodatage (spike : écart maximal nul).
TOLERANCE_PRIX_EUR = 0.005

#: Solde des flux physiques (A11, six frontières, deux sens) contre `ech_physiques` d'éCO2mix
#: (+ = import), par année civile (heure de Paris). Mesure du 2026-11-26 : écart moyen (ENTSO-E −
#: éCO2mix) de +600 à +640 MW de 2015 à 2017, +424 MW en 2018 (il tombe à ≈ 0 en octobre 2018, mois de
#: la scission DE-AT-LU), +117 à +239 MW de 2019 à 2023, +804 MW en 2024 (+700 à +1 300 MW de janvier à
#: octobre, ≈ 0 ensuite), +36 et +41 MW en 2025 et 2026 ; corrélation horaire 0,9846 à 0,9984. Cause des
#: écarts non établie : les frontières à courant continu (GB) et ES suivent les échanges commerciaux
#: d'éCO2mix mois par mois ; le reste (BE, DE, CH, IT) ne se compare pas frontière par frontière (flux
#: de bouclage). Tolérance : 1 200 MW (une frontière ou un sens perdu, un signe inversé dépassent
#: largement ce seuil ; le décalage d'une heure est attrapé par l'alignement).
TOLERANCE_SOLDE_BIAIS_MW = 1200.0  # |moyenne(ENTSO-E − éCO2mix)|
CORRELATION_SOLDE_MIN = 0.98       # corrélation horaire minimale (mesurée : ≥ 0,9846)

#: Charge FR (A65) contre `consommation` d'éCO2mix, par année. Écart de niveau connu et non
#: expliqué (spike : −1,6 % sur une semaine de 2019, +0,26 % en 2026) : on borne l'écart relatif
#: moyen et on exige la corrélation et l'alignement horaire, qui ne dépendent pas du périmètre.
#: Mesure du 2026-11-26, hors fenêtres de décalage : −0,4 à −0,9 % de 2015 à 2021, −1,2 % en 2022,
#: −2,1 à −2,4 % de 2023 à 2025 ; contre le seul temps réel éCO2mix (sept.-nov. 2026) : +0,2 à +0,3 %.
#: Hypothèse (non confirmée par RTE) : la charge publiée sur ENTSO-E est l'estimation temps réel, non
#: révisée par le consolidé. Corrélation horaire ≥ 0,994 hors fenêtres de décalage (2023 : 0,9906 avec).
TOLERANCE_CHARGE_RELATIVE = 0.03
CORRELATION_CHARGE_MIN = 0.99

#: Nucléaire FR (A75, B14) contre `nucleaire` d'éCO2mix : même grandeur publiée par RTE. Mesure du
#: 2026-11-26 hors fenêtre de décalage : −0,22 % à −0,50 % par an, corrélation ≥ 0,9996.
TOLERANCE_NUCLEAIRE_RELATIVE = 0.02
CORRELATION_NUCLEAIRE_MIN = 0.99

#: Décalages d'une heure **dans la source** (constatés le 2026-11-26) : sur ces fenêtres, la charge (A65)
#: et la production (A75 : nucléaire et solaire testés) FR d'ENTSO-E sont en retard d'une heure sur
#: éCO2mix (la valeur ENTSO-E de h+1 égale celle d'éCO2mix de h ; corrélation hebdomadaire 0,99 à +1 h
#: contre 0,87 à 0,98 à 0 h). Côté éCO2mix, la convention d'horodatage est vérifiée chaque année contre
#: ODRÉ nucléaire (`check.controle_convention_cons_def`) : le décalage est donc côté ENTSO-E.
#: Délimitation au jour près, par minimisation de l'écart quotidien : A75 par intermittence du
#: 31/05/2023 au 14/09/2023 puis en continu du 15/09/2023 au 01/04/2024 ; A65 du 31/05 au 02/06/2023,
#: du 21/07 au 31/10/2023 et du 01/02 au 31/03/2024. Une seule fenêtre englobante est exclue des
#: recoupements (et reportée à part) ; la donnée n'est PAS corrigée dans data/derive/.
DECALAGES_SOURCE = [
    # Les flux A11 ne sont pas décalés (dans la fenêtre : corrélation du solde 0,985 à 0 h, 0,954 à +1 h).
    (("charge_fr", "production_fr_b14"),
     datetime(2023, 5, 30, 22, tzinfo=timezone.utc), datetime(2024, 4, 2, 22, tzinfo=timezone.utc),
     "décalage d'une heure de la charge A65 et de la production A75 FR (ENTSO-E en retard sur éCO2mix), "
     "31/05/2023 → 02/04/2024 (heure de Paris)"),
]

#: Bornes physiques ou réglementaires.
#: Prix : plancher harmonisé SDAC −500 EUR/MWh ; plafond 3 000 puis 4 000 EUR/MWh (2022) puis
#: relèvements automatiques : on borne large à 5 000. GB (GBP) n'est pas borné en EUR.
PRIX_MIN_EUR, PRIX_MAX_EUR = -500.0, 5000.0

#: Complétude des séries FR (`controle_completude`). Une plage d'heures vides est expliquée :
#: - si elle compte au plus 2 h et touche l'heure répétée du passage à l'heure d'hiver (dernier dimanche
#:   d'octobre, 00:00 UTC) : RTE ne la publie pas plus sur ENTSO-E que dans éCO2mix ;
#: - si elle figure dans `LACUNES_ENTSOE` (plages de 3 h et plus, relevées le 2026-11-26 ; pour chacune,
#:   aucun point natif ou des heures seulement partiellement couvertes : la Period publiée s'interrompt) ;
#: - si elle est courte (1 ou 2 h) : tolérée dans la limite de `BUDGET_TROUS_COURTS_H` heures par série et
#:   par année (mesuré le 2026-11-26 : au plus 17 h, production nucléaire 2016 ; 12 h pour la charge en
#:   2022 ; 15 h pour le solde en 2016). Une erreur de lecture (résolution, A03) produirait des milliers
#:   d'heures vides.
BUDGET_TROUS_COURTS_H = 24
_AUCUN = "aucun point publié sur la plage (réponse ENTSO-E du 2026-11-26)"
_PARTIEL = "Period publiée interrompue (heures partiellement couvertes, réponse ENTSO-E du 2026-11-26)"
_UTC = timezone.utc
LACUNES_ENTSOE = [
    ("prix_fr", datetime(2026, 11, 20, 23, tzinfo=_UTC), 24,
     "livraison du 21/11/2026 absente chez ENTSO-E comme chez energy-charts (spike, constaté le 2026-11-26) ; "
     "année en cours, à revérifier"),
    ("charge_fr", datetime(2017, 2, 5, 19, tzinfo=_UTC), 13, _AUCUN),
    ("charge_fr", datetime(2018, 8, 12, 7, tzinfo=_UTC), 5, _AUCUN),
    ("charge_fr", datetime(2018, 10, 4, 1, tzinfo=_UTC), 3, _AUCUN),
    ("charge_fr", datetime(2018, 12, 14, 4, tzinfo=_UTC), 3, _AUCUN),
    ("charge_fr", datetime(2019, 7, 25, 0, tzinfo=_UTC), 5, _AUCUN),
    ("charge_fr", datetime(2022, 1, 10, 10, tzinfo=_UTC), 6, _AUCUN),
    ("charge_fr", datetime(2022, 8, 5, 19, tzinfo=_UTC), 3, _AUCUN),
    ("charge_fr", datetime(2025, 12, 10, 14, tzinfo=_UTC), 5, _PARTIEL + " ; même plage en production A75"),
    ("production_fr_b14", datetime(2025, 12, 10, 14, tzinfo=_UTC), 5, _PARTIEL + " ; même plage en charge A65"),
    ("production_fr_b14", datetime(2026, 1, 1, 0, tzinfo=_UTC), 26,
     "Period du 31/12/2025 23:00Z limitée à 4 quarts d'heure, reprise le 02/01/2026 01:45Z (réponse du "
     "2026-11-26) ; année en cours, à revérifier"),
    ("solde_physique_fr", datetime(2016, 5, 30, 16, tzinfo=_UTC), 15, "sens manquants : FR→GB, GB→FR, IT→FR"),
    ("solde_physique_fr", datetime(2016, 10, 1, 1, tzinfo=_UTC), 494, "sens manquants : FR→GB, GB→FR, IT→FR"),
    ("solde_physique_fr", datetime(2016, 11, 22, 8, tzinfo=_UTC), 4, "sens manquants : FR→GB, GB→FR"),
    ("solde_physique_fr", datetime(2016, 11, 24, 8, tzinfo=_UTC), 5, "sens manquants : FR→GB, GB→FR"),
    ("solde_physique_fr", datetime(2016, 11, 28, 9, tzinfo=_UTC), 6, "sens manquants : FR→GB, GB→FR"),
    ("solde_physique_fr", datetime(2016, 11, 29, 6, tzinfo=_UTC), 3, "sens manquants : FR→GB, GB→FR"),
    ("solde_physique_fr", datetime(2017, 3, 29, 1, tzinfo=_UTC), 4, "sens manquants : FR→GB, GB→FR, IT→FR"),
    ("solde_physique_fr", datetime(2021, 2, 17, 23, tzinfo=_UTC), 12, "sens manquants : FR→GB, GB→FR"),
    ("solde_physique_fr", datetime(2021, 5, 8, 12, tzinfo=_UTC), 5, "sens manquants : FR→GB, GB→FR"),
    ("solde_physique_fr", datetime(2021, 6, 13, 22, tzinfo=_UTC), 72, "sens manquants : FR→GB, GB→FR"),
    ("solde_physique_fr", datetime(2023, 6, 14, 15, tzinfo=_UTC), 17, "sens manquants : FR→GB, GB→FR"),
    ("solde_physique_fr", datetime(2023, 6, 17, 18, tzinfo=_UTC), 4, "sens manquants : FR→DE, DE→FR"),
    ("solde_physique_fr", datetime(2025, 4, 28, 10, tzinfo=_UTC), 36,
     "sens manquant : ES→FR ; coïncide avec la panne générale de la péninsule Ibérique du 28/04/2025"),
    ("solde_physique_fr", datetime(2026, 10, 11, 13, tzinfo=_UTC), 9, "sens manquants : FR→GB, GB→FR"),
]
#: Séries FR dont la complétude est exigée (les voisins sont seulement décomptés).
SERIES_COMPLETUDE = ("prix_fr", "charge_fr", "production_fr_b14", "solde_physique_fr")


# --------------------------------------------------------------------------
# Outils
# --------------------------------------------------------------------------


def _f(x: float, dec: int = 1) -> str:
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


def _pct(x: float, dec: int = 2) -> str:
    return f"{x * 100:+.{dec}f} %".replace(".", ",")


def _dans_fenetres(col: str) -> pl.Expr:
    e = pl.lit(False)
    for cols, a, b, _ in DECALAGES_SOURCE:
        if col in cols:
            e = e | ((pl.col("heure_utc") >= a) & (pl.col("heure_utc") < b))
    return e


def comparer_par_an(a: pl.DataFrame, b: pl.DataFrame, col_a: str, col_b: str, exclues: bool = False) -> pl.DataFrame:
    """Statistiques annuelles (heure de Paris) de a − b sur les heures communes renseignées, et
    corrélations à décalage 0 et ±1 h (alignement horaire). Les fenêtres `DECALAGES_SOURCE` de `col_a`
    sont écartées ; `exclues=True` renvoie au contraire les statistiques de ces seules fenêtres."""
    j = (a.select("heure_utc", pl.col(col_a).alias("x")).join(b.select("heure_utc", pl.col(col_b).alias("y")),
                                                               on="heure_utc", how="inner")
          .sort("heure_utc")
          .with_columns(pl.col("x").shift(1).alias("x_m1"), pl.col("x").shift(-1).alias("x_p1"),
                        annee_paris("heure_utc").alias("an")))
    f = _dans_fenetres(col_a)
    v = j.filter(f if exclues else ~f).drop_nulls(["x", "y"])
    if exclues:
        v = v.with_columns(pl.lit(0).alias("an"))
    return (v.group_by("an")
             .agg(pl.len().alias("heures"), pl.col("y").mean().alias("ref"), (pl.col("x") - pl.col("y")).mean()
                  .alias("biais"), (pl.col("x") - pl.col("y")).abs().mean().alias("mae"),
                  (pl.col("x") - pl.col("y")).abs().max().alias("max"),
                  pl.corr("x", "y").alias("corr"), pl.corr("x_m1", "y").alias("corr_m1"),
                  pl.corr("x_p1", "y").alias("corr_p1"))
             .sort("an"))


def _plages(heures: list) -> list[tuple]:
    plages: list[list] = []
    for h in sorted(heures):
        if plages and (h - plages[-1][1]).total_seconds() == 3600:
            plages[-1][1] = h
            plages[-1][2] += 1
        else:
            plages.append([h, h, 1])
    return [(a, n) for a, _, n in plages]


# --------------------------------------------------------------------------
# Contrôles
# --------------------------------------------------------------------------


def controle_lecture(meta: dict, raw: Path) -> "Resultat":
    """Rapport de lecture : aucun chevauchement de périodes, aucun conflit de valeurs entre fichiers, aucun
    quart d'heure « différent » avant la bascule SDAC ; dérivés à jour du brut."""
    from .check import Resultat
    r = Resultat("ENTSO-E : lecture (pas de chevauchement, de conflit entre fichiers ni de quarts d'heure de prix "
                 "différents avant le 01/10/2025) ; dérivés à jour", "OK")
    rp = meta["rapport"]
    q = rp["quarts_repetes"]
    lignes = [
        f"{rp['fichiers']} fichiers, {_f(rp['points_lus'], 0)} points lus dont {_f(rp['points_repetes_a03'], 0)} "
        f"répétés par la règle A03 ; {len(rp['fichiers_vides'])} réponse(s) « No matching data found »",
        f"séquences A44 ≠ 1 écartées : {_f(sum(rp['sequences_ecartees'].values()), 0)} points "
        f"({', '.join(sorted({k.split('/')[1] for k in rp['sequences_ecartees']})) or 'aucune'})",
        f"heures de prix PT15M ramenées à l'heure (4 quarts égaux, avant la bascule) : {q['heures_ramenees']} ("
        + ", ".join(f"{s} {j['jours']} j du {j['premier']} au {j['dernier']}"
                    for s, j in q.get('jours_ramenes_par_serie', {}).items()) + ")",
        f"doublons entre fichiers : {_f(rp['doublons']['lignes_en_double'], 0)} lignes, "
        f"{rp['doublons']['conflits']} conflit(s) de valeur",
        f"chevauchements de périodes : {rp['chevauchements']}",
    ]
    if q["heures_quarts_differents"] or rp["doublons"]["conflits"] or rp["chevauchements"]:
        r.statut = "ÉCHEC"
        lignes.append(f"quarts différents : {q.get('heures_quarts_differents_par_serie')} ; conflits : "
                      f"{rp['doublons']['exemples_conflits']} ; chevauchements : {rp.get('exemples_chevauchements')}")
    m = lire_manifeste(raw)
    brut = max((v["extrait_le"] for k, v in m.items() if k.startswith("entsoe_")), default=None)
    if brut and meta["extraction"]["derniere"] and brut > meta["extraction"]["derniere"]:
        r.statut = "ÉCHEC"
        lignes.append(f"brut extrait le {brut}, dérivés construits sur une extraction du "
                      f"{meta['extraction']['derniere']} : relancer `pc build`")
    r.lignes = lignes
    return r


def controle_prix_fr(raw: Path, natif: pl.DataFrame) -> "Resultat":
    """Prix FR natifs ENTSO-E = energy-charts, point à point (même pas, même début de période)."""
    from .check import Resultat
    r = Resultat(f"ENTSO-E : prix FR = energy-charts, point à point (écart ≤ {_f(TOLERANCE_PRIX_EUR, 3)} EUR/MWh)",
                 "OK")
    e = (natif.filter((pl.col("cle") == "entsoe_prix") & (pl.col("serie") == "FR"))
              .select("debut_utc", "pas_min", pl.col("valeur").alias("entsoe")))
    ec = charger_prix(raw).select("debut_utc", pl.col("pas_min").cast(pl.Int16), pl.col("prix_eur_mwh").alias("ec"))
    j = e.join(ec, on="debut_utc", how="full", coalesce=True, suffix="_ec")
    j = j.with_columns(annee_paris("debut_utc").alias("an"), (pl.col("entsoe") - pl.col("ec")).abs().alias("d"))
    for (an,), d in j.sort("debut_utc").group_by("an", maintain_order=True):
        com = d.filter(pl.col("entsoe").is_not_null() & pl.col("ec").is_not_null())
        pas_diff = com.filter(pl.col("pas_min") != pl.col("pas_min_ec")).height
        seul_e = d.filter(pl.col("entsoe").is_not_null() & pl.col("ec").is_null()).height
        seul_ec = d.filter(pl.col("entsoe").is_null() & pl.col("ec").is_not_null()).height
        dmax = com["d"].max() if com.height else None
        ok = com.height > 0 and dmax <= TOLERANCE_PRIX_EUR and pas_diff == 0
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : {com.height} points communs, écart max {_f(dmax or 0, 3)} EUR/MWh ; pas différents : "
                        f"{pas_diff} ; seulement ENTSO-E : {seul_e} ; seulement energy-charts : {seul_ec}"
                        f"{'' if ok else '  ← ÉCHEC'}")
    return r


def _ligne_fenetre(comp: pl.DataFrame) -> list[str]:
    if comp.height == 0:
        return []
    row = comp.row(0, named=True)
    return [f"fenêtres de décalage de source exclues ci-dessus ({row['heures']} h) : corrélation à 0 h "
            f"{_f(row['corr'], 4)}, à +1 h {_f(row['corr_p1'], 4)} (INFO : > à 0 h tant que la source n'est pas "
            f"corrigée)"]


def _controle_recoupement(nom: str, comp: pl.DataFrame, tol, corr_min: float, relatif: bool, Resultat) -> "Resultat":
    r = Resultat(nom, "OK")
    if comp.height == 0:
        return Resultat(nom, "ÉCHEC", ["aucune heure commune"])
    for row in comp.iter_rows(named=True):
        ecart = row["biais"] / row["ref"] if relatif else row["biais"]
        aligne = row["corr"] >= max(row["corr_m1"] or -1, row["corr_p1"] or -1)
        ok = abs(ecart) <= tol and row["corr"] >= corr_min and aligne
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(
            f"{row['an']} : {row['heures']} h, référence {_f(row['ref'], 0)} MW, écart moyen {_f(row['biais'], 0)} MW"
            f"{' (' + _pct(ecart) + ')' if relatif else ''}, écart absolu moyen {_f(row['mae'], 0)} MW, max "
            f"{_f(row['max'], 0)} MW ; corrélation {_f(row['corr'], 4)} (−1 h {_f(row['corr_m1'], 4)}, +1 h "
            f"{_f(row['corr_p1'], 4)}){'' if ok else '  ← ÉCHEC'}")
    return r


def _avec(lignes: list[str], r):
    r.lignes.extend(lignes)
    return r


def controle_solde(horaire: pl.DataFrame, table: pl.DataFrame) -> "Resultat":
    from .check import Resultat
    comp = comparer_par_an(horaire, table, "solde_physique_fr", "ech_physiques")
    fen = _ligne_fenetre(comparer_par_an(horaire, table, "solde_physique_fr", "ech_physiques", exclues=True))
    return _avec(fen, _controle_recoupement(
        f"ENTSO-E : solde des flux physiques A11 (6 frontières × 2 sens, + = import) ≈ éCO2mix ech_physiques "
        f"(|écart moyen| ≤ {_f(TOLERANCE_SOLDE_BIAIS_MW, 0)} MW, corrélation ≥ {_f(CORRELATION_SOLDE_MIN, 2)}, "
        f"alignement horaire), par an", comp, TOLERANCE_SOLDE_BIAIS_MW, CORRELATION_SOLDE_MIN, False, Resultat))


def ecart_charge_par_nature(horaire: pl.DataFrame, table: pl.DataFrame) -> pl.DataFrame:
    """Écart relatif moyen de la charge ENTSO-E à éCO2mix selon la nature de l'heure éCO2mix (définitif,
    consolidé, temps réel), hors fenêtres de décalage de source."""
    j = (horaire.select("heure_utc", "charge_fr").join(table.select("heure_utc", "consommation", "nature"),
                                                        on="heure_utc").drop_nulls()
                .filter(~_dans_fenetres("charge_fr")))
    return (j.group_by("nature").agg(pl.len().alias("heures"), pl.col("heure_utc").min().alias("debut"),
                                     pl.col("heure_utc").max().alias("fin"),
                                     ((pl.col("charge_fr") - pl.col("consommation")).mean()
                                      / pl.col("consommation").mean()).alias("ecart"))
             .sort("debut"))


def controle_charge(horaire: pl.DataFrame, table: pl.DataFrame) -> "Resultat":
    from .check import Resultat
    comp = comparer_par_an(horaire, table, "charge_fr", "consommation")
    fen = _ligne_fenetre(comparer_par_an(horaire, table, "charge_fr", "consommation", exclues=True))
    if "nature" in table.columns:
        fen += [f"écart relatif moyen selon la nature éCO2mix (INFO) : " + " ; ".join(
            f"{r['nature']} {_pct(r['ecart'])} ({r['heures']} h, {r['debut']:%Y-%m} → {r['fin']:%Y-%m})"
            for r in ecart_charge_par_nature(horaire, table).iter_rows(named=True))]
    return _avec(fen, _controle_recoupement(
        f"ENTSO-E : charge FR A65 ≈ éCO2mix consommation (|écart relatif moyen| ≤ "
        f"{_f(TOLERANCE_CHARGE_RELATIVE * 100, 0)} %, corrélation ≥ {_f(CORRELATION_CHARGE_MIN, 2)}, alignement horaire), "
        f"par an ; écart de niveau non expliqué, voir le rapport", comp, TOLERANCE_CHARGE_RELATIVE,
        CORRELATION_CHARGE_MIN, True, Resultat))


def controle_nucleaire(horaire: pl.DataFrame, table: pl.DataFrame) -> "Resultat":
    from .check import Resultat
    comp = comparer_par_an(horaire, table, "production_fr_b14", "nucleaire")
    fen = _ligne_fenetre(comparer_par_an(horaire, table, "production_fr_b14", "nucleaire", exclues=True))
    return _avec(fen, _controle_recoupement(
        f"ENTSO-E : production nucléaire FR A75/B14 ≈ éCO2mix nucleaire (|écart relatif moyen| ≤ "
        f"{_f(TOLERANCE_NUCLEAIRE_RELATIVE * 100, 0)} %, corrélation ≥ {_f(CORRELATION_NUCLEAIRE_MIN, 2)}, alignement "
        f"horaire), par an", comp, TOLERANCE_NUCLEAIRE_RELATIVE, CORRELATION_NUCLEAIRE_MIN, True, Resultat))


def controle_bornes(natif: pl.DataFrame) -> "Resultat":
    """Prix EUR dans [−500 ; 5 000] EUR/MWh ; puissances ≥ 0 (flux, NTC, charge, production)."""
    from .check import Resultat
    r = Resultat(f"ENTSO-E : bornes (prix EUR dans [{_f(PRIX_MIN_EUR, 0)} ; {_f(PRIX_MAX_EUR, 0)}] EUR/MWh, "
                 "puissances ≥ 0, unités attendues)", "OK")
    prix = natif.filter(pl.col("unite") == "EUR/MWh")
    hors = prix.filter((pl.col("valeur") < PRIX_MIN_EUR) | (pl.col("valeur") > PRIX_MAX_EUR))
    neg = natif.filter((pl.col("unite") == "MW") & (pl.col("valeur") < 0))
    unites = dict(natif.group_by("cle").agg(pl.col("unite").unique().sort()).iter_rows())
    gbp = natif.filter(pl.col("unite") == "GBP/MWh")["serie"].unique().to_list()
    attendu = {"entsoe_prix": ["EUR/MWh", "GBP/MWh"], "entsoe_production": ["MW"], "entsoe_flux": ["MW"],
               "entsoe_capacites": ["MW"], "entsoe_charge": ["MW"]}
    ok_unites = all(set(v) <= set(attendu[k]) for k, v in unites.items()) and set(gbp) <= {"GB"}
    if hors.height or neg.height or not ok_unites:
        r.statut = "ÉCHEC"
    if prix.height:
        r.lignes.append(f"prix EUR : {prix.height} points, min {_f(prix['valeur'].min(), 2)}, max "
                        f"{_f(prix['valeur'].max(), 2)} ; hors bornes : {hors.height}")
    r.lignes.append(f"puissances négatives : {neg.height}"
                    + (f" ({', '.join(sorted({f'{a}/{b}/{c}' for a, b, c in neg.select('cle', 'serie', 'filiere').iter_rows()})[:8])})"
                       if neg.height else ""))
    r.lignes.append(f"unités : {unites} ; séries en GBP : {gbp}")
    return r


def _passage_heure_hiver(debut: datetime, n: int) -> bool:
    from .check import _dernier_dimanche_octobre
    dim = _dernier_dimanche_octobre((debut + timedelta(hours=1)).year)
    heure = datetime(dim.year, dim.month, dim.day, tzinfo=timezone.utc)  # 02:00 CEST, première occurrence
    return n <= 2 and debut <= heure < debut + timedelta(hours=n)


def controle_completude(horaire: pl.DataFrame, meta: dict) -> "Resultat":
    """Séries FR : chaque plage d'heures vides entre la première et la dernière heure renseignées est
    expliquée (passage à l'heure d'hiver, lacune listée, ou trou court dans le budget annuel). Autres
    séries : heures vides décomptées, non contrôlées."""
    from .check import Resultat
    r = Resultat(f"ENTSO-E : complétude horaire des séries FR (prix, charge, nucléaire, solde des flux) : trous "
                 f"expliqués (heure d'hiver, lacunes listées, trous de 1-2 h ≤ {BUDGET_TROUS_COURTS_H} h/an) ; "
                 f"voisins décomptés", "OK")
    autres = []
    for col in horaire.columns[1:]:
        s = horaire.select("heure_utc", col)
        presentes = s.drop_nulls(col)
        if presentes.height == 0:
            autres.append(f"{col} : vide")
            continue
        a, b = presentes["heure_utc"].min(), presentes["heure_utc"].max()
        trous = s.filter(pl.col(col).is_null() & (pl.col("heure_utc") >= a) & (pl.col("heure_utc") <= b))
        if col not in SERIES_COMPLETUDE:
            if trous.height:
                autres.append(f"{col} : {trous.height} h")
            continue
        details, ok, courts, hiver = [], True, {}, 0
        for debut, n in _plages(trous["heure_utc"].to_list()):
            listee = next((c for s_, d_, n_, c in LACUNES_ENTSOE if s_ == col and d_ == debut and n_ == n), None)
            if listee:
                details.append(f"    trou {col} : {debut:%Y-%m-%d %H:%M} UTC, {n} h — {listee}")
            elif _passage_heure_hiver(debut, n):
                hiver += n
            elif n <= 2:
                an = (debut + timedelta(hours=1)).year
                courts[an] = courts.get(an, 0) + n
            else:
                ok = False
                details.append(f"    trou {col} : {debut:%Y-%m-%d %H:%M} UTC, {n} h — INEXPLIQUÉ")
        hors_budget = {an: h for an, h in courts.items() if h > BUDGET_TROUS_COURTS_H}
        if hors_budget:
            ok = False
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{col} : {a:%Y-%m-%d %H:%M} → {b:%Y-%m-%d %H:%M} UTC, {trous.height} h vides dont "
                        f"{hiver} h au passage à l'heure d'hiver et {sum(courts.values())} h de trous courts "
                        f"(par an : {', '.join(f'{an} {h}' for an, h in sorted(courts.items())) or 'aucun'})"
                        f"{'' if ok else '  ← ÉCHEC'}"
                        + (f" ; hors budget : {hors_budget}" if hors_budget else ""))
        r.lignes.extend(details)
    r.lignes.append("autres séries, heures vides entre leur première et leur dernière heure (non contrôlé) : "
                    + " ; ".join(autres))
    return r


def controles(raw: Path, derive: Path | None, table: pl.DataFrame) -> list:
    """Liste de contrôles (callables) pour pc/check.py."""
    from .check import Resultat
    if not entsoe_derive.fichiers_bruts(raw):
        return [lambda: Resultat("ENTSO-E : pas de données (data/raw/entsoe/ absent ; jeton requis pour "
                                 "`pc download entsoe_…`) — contrôles non exécutés", "INFO")]
    if derive is None or not (derive / "entsoe" / "meta.json").exists():
        return [lambda: Resultat("ENTSO-E", "ÉCHEC", ["data/raw/entsoe/ présent mais data/derive/entsoe/ absent : "
                                                     "lancer `pc build`"])]
    meta = json.loads((derive / "entsoe" / "meta.json").read_text())
    natif = entsoe_derive.charger_natif_derive(derive)
    horaire = entsoe_derive.charger_horaire(derive)
    return [
        lambda: controle_lecture(meta, raw),
        lambda: controle_bornes(natif),
        lambda: controle_prix_fr(raw, natif),
        lambda: controle_solde(horaire, table),
        lambda: controle_charge(horaire, table),
        lambda: controle_nucleaire(horaire, table),
        lambda: controle_completude(horaire, meta),
    ]
