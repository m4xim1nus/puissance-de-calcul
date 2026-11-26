"""Contrôles de cohérence (`pc check`) : bilans qui bouclent, recoupements entre sources.

Chaque contrôle porte sa référence et sa tolérance dans le code, et affiche
OK / ÉCHEC (ou INFO pour un contrôle seulement informatif). Le code de retour
est non nul si un contrôle échoue. Spécification : docs/spike/systeme.md,
§ « Recommandation pour le pipeline », et docs/spike/contre-verification.md.

Les contrôles lisent l'export (`data/export/systeme_horaire.parquet`, ce que
le site affiche) et, pour les références et la série native, `data/raw/`.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from . import remit
from .build import (DATETIME_UTC, PAS_MIN, annee_paris, charger_eco2mix, debut_grille, debut_periode,
                    heures_negatives, mw_vers_mwh)
from .sources import ANNEE_DEBUT, fichier, fichiers_annuels, lire_manifeste

# --------------------------------------------------------------------------
# Références et tolérances
# --------------------------------------------------------------------------

#: Σ consommation éCO2mix (MW × 0,5 h, consolidé/définitif) par année civile (heure de Paris)
#: comparée à ODRÉ `consommation-annuelle-brute-regionale`, somme des 12 régions continentales
#: (hors Corse : éCO2mix national est au périmètre continental). Le spike boucle à 7 GWh près
#: en 2024 et 2 GWh en 2025 (docs/spike/systeme.md § 7).
#: Recalibré le 2026-11-26 : la tolérance de 0,05 % avait été calibrée par le spike sur 2024
#: seulement. De 2015 à 2023, l'écart va de −0,33 % à +0,27 % (jusqu'à 1,5 TWh), alors qu'ODRÉ
#: est cohérent avec lui-même (national − Corse = Σ régions à 1 GWh près). Cause non vérifiée
#: (révisions des totaux annuels, dont l'autoconsommation photovoltaïque ?). Tolérance stricte
#: pour les années de référence du site, large ailleurs ; l'écart reste affiché chaque année
#: (making-of/ERREURS.md, 2026-11-26).
ANNEES_REFERENCE = {2024, 2025}
TOLERANCE_CONSO_RELATIVE = 0.0005  # ± 0,05 %, années de référence
TOLERANCE_CONSO_RELATIVE_LARGE = 0.005  # ± 0,5 %, autres années (écart connu, non expliqué)

#: Nucléaire éCO2mix horaire comparé à ODRÉ `production-nette-nucleaire` (« convention
#: débutante », GWh par heure). Spike : 0,2 MW en convention « fin » contre 258 MW en « début ».
#: Recalibré le 2026-11-26 : 5 MW n'est tenu qu'en 2024 (0,2 MW) ; 28 MW en 2025, 56 à 126 MW
#: avant 2024, avec des totaux annuels concordants à moins de 0,1 %. C'est un écart de niveau
#: entre deux sources, pas de calage : la convention d'horodatage est vérifiée à part
#: (`controle_convention_cons_def`). Tolérance relative à la production moyenne.
TOLERANCE_NUCLEAIRE_RELATIVE = 0.005  # écart absolu moyen < 0,5 % du nucléaire moyen, par année

#: Heures à prix day-ahead FR strictement négatif, année civile (heure de Paris) ; après le
#: 2025-10-01, heure = moyenne des quarts d'heure. Chiffres RTE :
#: - 2023 : 147 h — Bilan électrique 2024, rapport complet, chapitre Prix (« 361 heures en 2024
#:   contre 147 en 2023 ») ;
#: - 2024 : 352 h — Bilan électrique 2025, chapitre Prix (« 513 heures en 2025 […] (352 en
#:   2024) ») ; révisé depuis 361 h (BE2024) : RTE retient Nord Pool après le découplage
#:   d'EPEX du 26/06/2024 (BE2025 p. 64, docs/spike/contre-verification.md) ;
#: - 2025 : 513 h — Bilan électrique 2025, note 10 pour la convention quart-horaire.
HEURES_NEGATIVES_RTE = {2023: 147, 2024: 352, 2025: 513}

#: Intensité GES moyenne de la consommation (imports compris), 2025 : 20,0 gCO2eq/kWh
#: (RTE, Bilan électrique 2025, rapport complet). Calcul : ODRÉ `part-enr-intensite-ges-conso-tr`
#: pondérée par la consommation horaire éCO2mix. Hypothèse : `date_heure_utc` d'ODRÉ marque le
#: début de l'heure (non documenté ; effet négligeable sur une moyenne annuelle pondérée).
INTENSITE_CONSO_RTE = {2025: 20.0}
TOLERANCE_INTENSITE_RELATIVE = 0.02  # ± 2 %

#: Complétude. Un trou (heure sans valeur) est **expliqué** s'il relève d'un des cas
#: structurels ci-dessous, reconnus automatiquement, ou d'une lacune de source listée dans
#: `LACUNES_CONNUES` ; tout autre trou fait échouer le contrôle.
#:
#: Cas structurels (consommation) :
#: - passage à l'heure d'hiver : l'heure répétée manque dans les fichiers RTE (96 quarts d'heure
#:   par jour local), d'où deux heures UTC amputées d'une demi-heure chacune en convention
#:   « fin » : samedi 23:00 et dimanche 00:00 UTC, le dernier dimanche d'octobre ;
#: - raccord entre deux natures (définitif → consolidé → temps réel) : une heure isolée dont
#:   les heures voisines n'ont pas la même nature (docs/spike/systeme.md, piège 4).
#:
#: Lacunes de source : (série, début UTC, nombre d'heures, constat).
LACUNES_CONNUES = [
    ("prix", datetime(2014, 12, 31, 23, tzinfo=timezone.utc), 96,
     "energy-charts FR : aucune valeur du 1er au 4 janvier 2015 (heure de Paris), la série commence "
     "le 5 janvier 2015 (spike : HTTP 404 « No content available » le 1er janvier)"),
    ("prix", datetime(2026, 11, 20, 23, tzinfo=timezone.utc), 24,
     "energy-charts FR : 96 quarts d'heure null pour la livraison du 21 novembre 2026, constaté "
     "dans la réponse du 2026-11-26 ; année en cours, à revérifier au prochain téléchargement"),
]

#: Disponibilité nucléaire REMIT (pc/remit.py).
#:
#: (a) Taux annuel reconstruit hors Flamanville 3 comparé au Bilan électrique 2025 de RTE (fig. 2.5,
#: p. 25), valeurs lues dans le référentiel (`dispo_nucleaire_rte_AAAA`, referentiels/chiffres.yaml).
#: Tolérance ± 0,5 pt sur 2018-2025 ; 2015-2017 affichés sans tolérance (la méthode de RTE sur ces
#: années n'est pas connue ; écarts de +0,2 à +0,4 pt au 2026-11-26). Écart typique observé :
#: +0,1 à +0,3 pt, toujours positif (cause non établie ; l'accord par centrale est à ± 1 pt pour
#: 187 centrales-années sur 198, BE2025 fig. 2.9, vérification manuelle du 2026-11-26).
TOLERANCE_TAUX_RTE_PT = 0.5
ANNEES_TAUX_CONTROLEES = range(2018, 2026)

#: (b) Production nucléaire éCO2mix ≤ disponible déclaré + tolérance, heure par heure.
#: La production peut dépasser le disponible déclaré sans erreur de reconstruction :
#: - eau froide en hiver : la puissance nette d'une tranche dépasse sa puissance maximale
#:   déclarée (EDF déclare parfois lui-même plus que la puissance maximale, ex. Blayais 2 à
#:   960 MW pour 910) ; les dépassements se concentrent en décembre-février, parc très disponible ;
#: - déclarations en escalier pendant les grèves ou les essais, alors que la puissance varie en
#:   rampe (ex. 18/01/2023 20:00 UTC : quatre tranches déclarées en baisse « grève » à 20:00 UTC,
#:   production encore en descente) ;
#: Calibrage (2026-11-26) sur **toutes** les années 2015-2026 (≈ 104 000 h, pas une seule
#: année : erreur du 26/11/2026, making-of/ERREURS.md) : dépassement relatif maximal 2,2 %
#: (31/01/2017, grève), 1,9 % (2025), 1,85 % (2016) ; 99,9e centile ≤ 1,1 % chaque année. Une
#: seule heure au-delà de 2,5 %, listée ci-dessous. Tolérance : 2,5 % du disponible déclaré.
TOLERANCE_EXCES_RELATIVE = 0.025
EXCES_EXPLIQUES = {
    datetime(2023, 1, 18, 20, tzinfo=timezone.utc):
        "grève : Belleville 2, Paluel 2, 3 et 4 déclarées en baisse à 20:00 UTC d'un seul coup (−3 200 MW), "
        "production en rampe (+2 154 MW, 5,3 %) ; l'heure suivante est sous le disponible",
}

#: (c) Fuseau des dates REMIT (`remit.FUSEAU_REMIT`). La notice d'EDF (« Note explicative
#: publication EDF », v3 du 28/03/2025, doaat.edf.fr, HTTP 403 pour un client automatisé ; lue
#: dans sa copie archive.org) dit : « Les heures indiquées sont au format UTC pour la zone Central
#: European Time », phrase ambiguë. Trois tests sur les données, tous en faveur de l'heure de
#: Paris (CET l'hiver, CEST l'été) :
#: 1. étude d'événements : pour les arrêts fortuits nets (tranche ≥ 880 MW à pleine
#:    disponibilité depuis 6 h, puissance disponible ≤ 20 % de la maximale, début à la minute non
#:    ronde, au moins 3 h), la plus forte baisse moyenne de la production nucléaire éCO2mix (pas
#:    de 30 min) doit tomber dans la demi-heure qui contient le début déclaré lu en heure de
#:    Paris, **séparément** en heure d'hiver et en heure d'été. En UTC, elle tomberait 1 h (hiver)
#:    ou 2 h (été) plus tard ;
#: 2. passage à l'heure d'été : aucune date (début, fin, publication, toutes filières) ne doit
#:    tomber entre 02:00 et 02:59, heure qui n'existe pas à Paris ces jours-là ;
#: 3. la dernière date de publication de l'historique, lue en heure de Paris, doit précéder la
#:    date de dépôt du fichier sur data-fair (07/09/2026 07:36 UTC pour une publication à
#:    « 07/09/2026 09:19 » : impossible en UTC).
FUSEAU_FENETRE_MIN = 240
FUSEAU_EVENEMENTS_MIN = 50


@dataclass
class Resultat:
    nom: str
    statut: str  # "OK", "ÉCHEC" ou "INFO"
    lignes: list[str] = field(default_factory=list)


def _f(x: float, dec: int = 1) -> str:
    """Nombre au format français (espace fine insécable pour les milliers, virgule décimale)."""
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


def _pct(x: float, dec: int) -> str:
    return f"{x * 100:+.{dec}f} %".replace(".", ",")


# --------------------------------------------------------------------------
# Contrôles
# --------------------------------------------------------------------------


def controle_consommation(raw: Path, natif: pl.DataFrame, annee_courante: int) -> Resultat:
    r = Resultat("Σ consommation éCO2mix (MW × 0,5 h) ≈ ODRÉ régional hors Corse "
                 "(± 0,05 % en 2024-2025, ± 0,5 % avant)", "OK")
    reg = pl.read_parquet(fichier(raw, "odre_conso_annuelle_regionale"))
    reg = (reg.with_columns(pl.col("annee").cast(pl.Utf8).str.slice(0, 4).cast(pl.Int32).alias("an"))
              .filter(pl.col("region") != "Corse")
              .group_by("an").agg(pl.len().alias("regions"),
                                  pl.col("consommation_brute_electricite_rte").sum().alias("gwh"),
                                  pl.col("statut_rte").unique().alias("statuts")))
    v = (natif.filter(pl.col("nature").is_in(["definitif", "consolide"]))
              .with_columns(annee_paris(debut_periode(pl.col("ts_utc"), pl.col("pas_min"))).alias("an"))
              .group_by("an").agg((mw_vers_mwh(pl.col("consommation"), pl.col("pas_min") / 60).sum() / 1e3).alias("gwh_eco"),
                                  pl.len().alias("demi_heures")))
    j = (v.join(reg, on="an", how="inner")
          .filter((pl.col("an") >= ANNEE_DEBUT) & (pl.col("an") < annee_courante) & (pl.col("regions") == 12))
          .sort("an"))
    if j.height == 0:
        return Resultat(r.nom, "ÉCHEC", ["aucune année commune"])
    for row in j.iter_rows(named=True):
        ecart = row["gwh_eco"] / row["gwh"] - 1
        attendu = 17568 if row["an"] % 4 == 0 else 17520
        tol = TOLERANCE_CONSO_RELATIVE if row["an"] in ANNEES_REFERENCE else TOLERANCE_CONSO_RELATIVE_LARGE
        ok = abs(ecart) <= tol
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(
            f"{row['an']} : éCO2mix {_f(row['gwh_eco'] / 1e3, 3)} TWh, ODRÉ {_f(row['gwh'] / 1e3, 3)} TWh "
            f"({'/'.join(row['statuts'])}) ; écart {_f(row['gwh_eco'] - row['gwh'], 0)} GWh ({_pct(ecart, 3)})"
            f" ; {attendu - row['demi_heures']} demi-heure(s) manquante(s){'' if ok else '  ← hors tolérance'}")
    return r


def _nucleaire_horaire(natif: pl.DataFrame, decalage: str) -> pl.DataFrame:
    """Nucléaire horaire à partir des points natifs, en convention « fin » ou « debut »
    (indépendamment de `HORODATAGE_ECO2MIX`, pour comparer les deux)."""
    debut = pl.col("ts_utc") - pl.duration(minutes=pl.col("pas_min")) if decalage == "fin" else pl.col("ts_utc")
    return (natif.with_columns(debut.dt.truncate("1h").alias("heure_utc"))
                 .group_by("heure_utc")
                 .agg((pl.col("nucleaire") * pl.col("pas_min")).sum().alias("s"), pl.col("pas_min").sum().alias("couv"))
                 .filter(pl.col("couv") == 60)
                 .select("heure_utc", (pl.col("s") / 60).alias("nuc_eco")))


def _nucleaire_odre(raw: Path) -> pl.DataFrame:
    n = pl.concat([pl.read_parquet(p) for p in fichiers_annuels(raw, "odre_nucleaire")])
    return (n.select(pl.col("horodate").dt.convert_time_zone("UTC").cast(DATETIME_UTC).alias("heure_utc"),
                     (pl.col("production_nette") * 1e3).alias("nuc_odre"))  # GWh par heure → MW moyen
             .unique(subset="heure_utc"))


def _mae_par_an(horaire: pl.DataFrame, odre: pl.DataFrame, col: str) -> pl.DataFrame:
    return (horaire.join(odre, on="heure_utc", how="inner")
                   .group_by(annee_paris("heure_utc").alias("an"))
                   .agg(pl.len().alias("heures"), (pl.col(col) - pl.col("nuc_odre")).abs().mean().alias("mae"),
                        (pl.col(col) - pl.col("nuc_odre")).mean().alias("biais"),
                        (pl.col(col) - pl.col("nuc_odre")).abs().max().alias("max"),
                        pl.col("nuc_odre").mean().alias("moyenne"))
                   .sort("an"))


def controle_convention_cons_def(raw: Path, natif: pl.DataFrame) -> Resultat:
    """La convention « fin » est-elle, chaque année, la meilleure contre ODRÉ nucléaire ?

    Balayage indépendant de `HORODATAGE_ECO2MIX` : « debut » (décalage 0), « fin » (+30 min) et
    +60 min. Le contrôle échoue si l'optimum n'est pas la convention retenue dans build.py.
    """
    from . import build
    r = Resultat(f"Convention d'horodatage cons-def (« {build.HORODATAGE_ECO2MIX} ») = optimum du balayage "
                 "contre ODRÉ nucléaire, chaque année", "OK")
    odre = _nucleaire_odre(raw)
    cd = natif.filter(pl.col("nature").is_in(["definitif", "consolide"]))
    maes = {}
    for nom, d in (("debut", 0), ("fin", 30), ("+60 min", 60)):
        h = (cd.with_columns((pl.col("ts_utc") - pl.duration(minutes=d)).dt.truncate("1h").alias("heure_utc"))
               .group_by("heure_utc").agg(pl.col("nucleaire").mean().alias("x"), pl.len().alias("k"))
               .filter(pl.col("k") == 2))
        maes[nom] = dict(_mae_par_an(h, odre, "x").select("an", "mae").iter_rows())
    for an in sorted(maes["fin"]):
        vals = {nom: m.get(an, float("inf")) for nom, m in maes.items()}
        meilleure = min(vals, key=vals.get)
        ok = meilleure == build.HORODATAGE_ECO2MIX
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : écart absolu moyen « debut » {_f(vals['debut'], 0)} MW, « fin » {_f(vals['fin'], 1)} MW, "
                        f"+60 min {_f(vals['+60 min'], 0)} MW → optimum « {meilleure} »{'' if ok else '  ← à revoir'}")
    return r


def controle_nucleaire(raw: Path, table: pl.DataFrame) -> Resultat:
    r = Resultat("Nucléaire horaire exporté ≈ ODRÉ production-nette-nucleaire "
                 "(écart absolu moyen < 0,5 % du nucléaire moyen, par an)", "OK")
    exp = table.filter(pl.col("nature").is_in(["definitif", "consolide"]) & pl.col("nucleaire").is_not_null())
    par_an = _mae_par_an(exp.select("heure_utc", "nucleaire"), _nucleaire_odre(raw), "nucleaire")
    if par_an.height == 0:
        return Resultat(r.nom, "ÉCHEC", ["aucune heure commune"])
    for row in par_an.iter_rows(named=True):
        ok = row["mae"] < TOLERANCE_NUCLEAIRE_RELATIVE * row["moyenne"]
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{row['an']} : {row['heures']} h, écart absolu moyen {_f(row['mae'], 2)} MW, "
                        f"biais {_f(row['biais'], 1)} MW, max {_f(row['max'], 0)} MW{'' if ok else '  ← hors tolérance'}")
    return r


def controle_convention_temps_reel(raw: Path, natif: pl.DataFrame) -> Resultat:
    """Informatif : quelle convention pour le temps réel (puissance instantanée, 15 min) ?

    Balayage du décalage d (le point t est affecté à l'heure trunc(t − d), heure = moyenne des
    4 points) contre ODRÉ nucléaire sur la période commune. Avec des valeurs instantanées, d = 0
    et d = 15 min (« fin ») sont deux sommes de Riemann de la même moyenne : on s'attend à ce
    qu'elles se valent. Écart < 10 % entre les deux → non concluant.
    """
    r = Resultat("Convention d'horodatage du temps réel (15 min) contre ODRÉ nucléaire — informatif", "INFO")
    tr = natif.filter(pl.col("nature") == "temps_reel")
    odre = _nucleaire_odre(raw)
    res = {}
    for d in (-15, 0, 15, 30, 45):
        h = (tr.with_columns((pl.col("ts_utc") - pl.duration(minutes=d)).dt.truncate("1h").alias("heure_utc"))
               .group_by("heure_utc").agg(pl.col("nucleaire").mean().alias("x"), pl.len().alias("k"))
               .filter(pl.col("k") == 4).join(odre, on="heure_utc", how="inner"))
        if h.height:
            res[d] = (h.height, (h["x"] - h["nuc_odre"]).abs().mean(), (h["x"] - h["nuc_odre"]).mean())
    if 15 not in res:
        r.lignes.append("aucune heure commune entre le temps réel et ODRÉ nucléaire : test impossible")
        return r
    for d, (n, mae, biais) in res.items():
        r.lignes.append(f"décalage {d:+d} min{' (« fin », retenu)' if d == 15 else ' (« debut »)' if d == 0 else ''} : "
                        f"{n} h, écart absolu moyen {_f(mae, 1)} MW, biais {_f(biais, 1)} MW")
    fin, debut = res[15][1], res[0][1]
    if abs(fin - debut) / min(fin, debut) < 0.10:
        r.lignes.append("→ non concluant : « fin » et « debut » se valent (attendu pour des valeurs instantanées) ; "
                        "le niveau du temps réel s'écarte d'ODRÉ (voir biais)")
    else:
        meilleure = "fin" if fin < debut else "debut"
        r.lignes.append(f"→ « {meilleure} » colle mieux" + ("" if meilleure == "fin" else " : revoir build.py"))
    return r


def controle_heures_negatives(table: pl.DataFrame) -> Resultat:
    r = Resultat("Heures à prix négatif par an = Bilans électriques RTE (147 / 352 / 513, égalité exacte)", "OK")
    calc = heures_negatives(table.select("heure_utc", "prix_eur_mwh"))
    for an, ref in HEURES_NEGATIVES_RTE.items():
        n = calc.get(an)
        ok = n == ref
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : calcul {n}, RTE {ref}{'' if ok else '  ← différent'}")
    autres = ", ".join(f"{a} : {n}" for a, n in calc.items() if a not in HEURES_NEGATIVES_RTE)
    r.lignes.append(f"autres années (non recoupées) : {autres or 'aucune heure négative'}")
    return r


def controle_intensite(raw: Path, table: pl.DataFrame) -> Resultat:
    r = Resultat("Intensité GES de la consommation 2025, pondérée ≈ 20,0 gCO2eq/kWh (BE2025, ± 2 %)", "OK")
    g = pl.read_parquet(fichier(raw, "odre_ges_conso"))
    g = (g.select(pl.col("date_heure_utc").dt.convert_time_zone("UTC").cast(DATETIME_UTC).alias("heure_utc"),
                  pl.col("intensite_emissions_conso").cast(pl.Float64))
          .drop_nulls().unique(subset="heure_utc"))
    j = table.select("heure_utc", "consommation").drop_nulls().join(g, on="heure_utc", how="inner")
    for an, ref in INTENSITE_CONSO_RTE.items():
        d = j.filter(annee_paris("heure_utc") == an)
        if d.height == 0:
            r.statut = "ÉCHEC"
            r.lignes.append(f"{an} : aucune heure commune")
            continue
        pond = (d["intensite_emissions_conso"] * d["consommation"]).sum() / d["consommation"].sum()
        simple = d["intensite_emissions_conso"].mean()
        ecart = pond / ref - 1
        ok = abs(ecart) <= TOLERANCE_INTENSITE_RELATIVE
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : pondérée {_f(pond, 2)} g/kWh sur {d.height} h (moyenne simple {_f(simple, 2)}, "
                        f"méthode fausse) ; RTE {_f(ref, 1)} ; écart {_pct(ecart, 2)}{'' if ok else '  ← hors tolérance'}")
    return r


def _plages(heures: pl.Series) -> list[tuple]:
    """Regroupe des heures manquantes consécutives en plages (début, nombre d'heures)."""
    plages: list[list] = []
    for h in heures.sort().to_list():
        if plages and (h - plages[-1][1]).total_seconds() == 3600:
            plages[-1][1] = h
            plages[-1][2] += 1
        else:
            plages.append([h, h, 1])
    return [(a, n) for a, _, n in plages]


def _dernier_dimanche_octobre(an: int) -> date:
    d = date(an, 10, 31)
    return d - timedelta(days=(d.weekday() + 1) % 7)


def _explication(serie: str, debut: datetime, n: int, natures: dict) -> str | None:
    """Explication d'un trou (plage d'heures manquantes), ou None s'il est inexpliqué."""
    for s_, d_, n_, constat in LACUNES_CONNUES:
        if s_ == serie and d_ == debut and n_ == n:
            return f"lacune de source connue : {constat}"
    if serie == "conso":
        dim = _dernier_dimanche_octobre(debut.year)
        if n == 2 and debut == datetime(dim.year, dim.month, dim.day, tzinfo=timezone.utc) - timedelta(hours=1):
            return "passage à l'heure d'hiver (heure répétée absente des fichiers RTE)"
        avant, apres = natures.get(debut - timedelta(hours=1)), natures.get(debut + timedelta(hours=n))
        if n == 1 and avant and apres and avant != apres:
            return f"raccord {avant} → {apres}"
    return None


def controle_completude(table: pl.DataFrame, annee_courante: int) -> Resultat:
    r = Resultat("Complétude : heures par année (8 760 / 8 784), trous listés et expliqués", "OK")
    t = table.with_columns(annee_paris("heure_utc").alias("an"))
    fin_conso = t.filter(pl.col("consommation").is_not_null())["heure_utc"].max()
    fin_prix = t.filter(pl.col("prix_eur_mwh").is_not_null())["heure_utc"].max()
    natures = dict(t.select("heure_utc", "nature").drop_nulls().iter_rows())
    for (an,), d in t.group_by("an", maintain_order=True):
        attendu = 8784 if (an % 4 == 0) else 8760
        close = an < annee_courante
        ok = d.height == attendu or (not close and d.height <= attendu)
        trous = {
            "conso": d.filter(pl.col("consommation").is_null() & (pl.col("heure_utc") <= fin_conso))["heure_utc"],
            "prix": d.filter(pl.col("prix_eur_mwh").is_null() & (pl.col("heure_utc") <= fin_prix))["heure_utc"],
        }
        details = []
        for serie, heures in trous.items():
            for debut, n in _plages(heures):
                pourquoi = _explication(serie, debut, n, natures)
                if pourquoi is None:
                    ok = False
                details.append(f"    trou {serie} : {debut:%Y-%m-%d %H:%M} UTC, {n} h — "
                               f"{pourquoi or 'INEXPLIQUÉ'}")
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} ({'close' if close else 'en cours'}) : {d.height} h "
                        f"(attendu {attendu if close else '≤ ' + str(attendu)}) ; sans consommation : "
                        f"{trous['conso'].len()} h ; sans prix : {trous['prix'].len()} h{'' if ok else '  ← ÉCHEC'}")
        r.lignes.extend(details)
    r.lignes.append(f"dernière heure avec consommation : {fin_conso:%Y-%m-%d %H:%M} UTC ; "
                    f"avec prix : {fin_prix:%Y-%m-%d %H:%M} UTC (trous comptés jusqu'à ces dates)")
    return r


# --------------------------------------------------------------------------
# Disponibilité nucléaire (REMIT)
# --------------------------------------------------------------------------


def _remit_par_tranche(raw: Path, table: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, dict]:
    brut, ev, bornes = remit.depuis_raw(raw)
    fin = min(bornes["horizon"], table["heure_utc"].max() + timedelta(hours=1))
    return brut, ev, remit.disponible_horaire(ev, debut_grille(), fin), bornes


def controle_remit_jonction(bornes: dict) -> Resultat:
    """L'historique (exports ponctuels) et la liste courante (trois mois glissants) se recouvrent-ils ?"""
    r = Resultat("REMIT : la liste courante remonte jusqu'au dernier export de l'historique (pas de trou)", "OK")
    fh, dc = bornes["fin_historique"], bornes["debut_courante"]
    r.lignes.append(f"historique : dernière publication {fh:%Y-%m-%d %H:%M} UTC ; liste courante : plus ancienne "
                    f"fin d'événement {dc:%Y-%m-%d %H:%M} UTC" if dc else "liste courante absente")
    if bornes["trou"]:
        r.statut = "ÉCHEC"
        r.lignes.append("← trou : des événements terminés entre ces deux dates manquent ; attendre ou chercher un "
                        "nouvel export de l'historique sur opendata.edf.fr, puis `pc download edf_remit`")
    else:
        r.lignes.append(f"recouvrement de {(fh - dc).days} jour(s) ; série arrêtée à {bornes['horizon']:%Y-%m-%d %H:%M} UTC "
                        "(extraction de la liste courante)")
    return r


def controle_taux_rte(par_tranche: pl.DataFrame, table: pl.DataFrame) -> Resultat:
    from . import chiffres
    r = Resultat("Taux de disponibilité nucléaire REMIT hors Flamanville 3 ≈ RTE, BE2025 fig. 2.5 "
                 "(± 0,5 pt sur 2018-2025) ; export = recalcul", "OK")
    ref = chiffres.charger().chiffres
    calc = dict(remit.taux_annuels(par_tranche, remit.HORS_TAUX_RTE).select("an", "taux").iter_rows())
    for an in range(ANNEE_DEBUT, max(calc) + 1):
        c = ref.get(f"dispo_nucleaire_rte_{an}")
        if c is None or an not in calc:
            continue
        ecart = calc[an] * 100 - float(c["valeur"])
        controle = an in ANNEES_TAUX_CONTROLEES
        ok = not controle or abs(ecart) <= TOLERANCE_TAUX_RTE_PT
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : reconstruit {_f(calc[an] * 100, 2)} %, RTE {_f(float(c['valeur']), 1)} % ; écart "
                        f"{ecart:+.2f} pt".replace(".", ",")
                        + ("" if controle else " (informatif)") + ("" if ok else "  ← hors tolérance"))
    manquantes = [a for a in ANNEES_TAUX_CONTROLEES if f"dispo_nucleaire_rte_{a}" not in ref]
    if manquantes:
        r.statut = "ÉCHEC"
        r.lignes.append(f"référence absente du référentiel : {manquantes}")
    # cohérence de l'export avec le recalcul
    nat = remit.national(par_tranche).select("heure_utc", "nucleaire_disponible")
    j = table.select("heure_utc", pl.col("nucleaire_disponible").alias("export")).join(nat, on="heure_utc", how="full",
                                                                                          coalesce=True)
    diff = j.select((pl.col("export") - pl.col("nucleaire_disponible")).abs().max()).item()
    nuls = j.filter(pl.col("export").is_null() != pl.col("nucleaire_disponible").is_null()).height
    ok = diff is not None and diff <= 0.05 + 1e-9 and nuls == 0
    if not ok:
        r.statut = "ÉCHEC"
    r.lignes.append(f"export contre recalcul : écart max {_f(diff or 0, 2)} MW (export arrondi au dixième), {nuls} heure(s) "
                    f"renseignée(s) d'un seul côté{'' if ok else '  ← export à refaire (`pc build`)'}")
    return r


def controle_production_sous_disponible(table: pl.DataFrame) -> Resultat:
    r = Resultat("Production nucléaire éCO2mix ≤ disponible REMIT + 2,5 % (toutes heures, toutes années)", "OK")
    t = (table.drop_nulls(["nucleaire", "nucleaire_disponible"])
              .with_columns((pl.col("nucleaire") - pl.col("nucleaire_disponible")).alias("exces"))
              .with_columns((pl.col("exces") / pl.col("nucleaire_disponible")).alias("rel"),
                            annee_paris("heure_utc").alias("an")))
    if t.height == 0:
        return Resultat(r.nom, "ÉCHEC", ["aucune heure avec production et disponible"])
    hors = t.filter(pl.col("rel") > TOLERANCE_EXCES_RELATIVE)
    for row in (t.group_by("an").agg(pl.len().alias("h"), (pl.col("exces") > 0).sum().alias("h0"),
                                     (pl.col("rel") > 0.01).sum().alias("h1"), pl.col("exces").max().alias("max"),
                                     pl.col("rel").max().alias("rmax")).sort("an").iter_rows(named=True)):
        r.lignes.append(f"{row['an']} : {row['h']} h ; production > disponible {row['h0']} h, > 1 % {row['h1']} h ; "
                        f"max {_f(row['max'], 0)} MW ({_f(row['rmax'] * 100, 2)} %)")
    for h, exc, rel in hors.select("heure_utc", "exces", "rel").iter_rows():
        motif = EXCES_EXPLIQUES.get(h)
        if motif is None:
            r.statut = "ÉCHEC"
        r.lignes.append(f"    {h:%Y-%m-%d %H:%M} UTC : +{_f(exc, 0)} MW ({_f(rel * 100, 1)} %) — "
                        f"{motif or 'INEXPLIQUÉ  ← hors tolérance'}")
    return r


def _arrets_fortuits_nets(ev: pl.DataFrame) -> pl.DataFrame:
    """Arrêts fortuits francs : tranche ≥ 880 MW, disponible ≤ 20 %, ≥ 3 h, début à une minute non
    ronde, sans autre événement de la tranche dans les 6 h qui précèdent."""
    f = ev.filter((pl.col("type") == "Fortuite") & (pl.col("pdispo") <= 0.2 * pl.col("pmax"))
                  & (pl.col("pmax") >= 880) & ((pl.col("fin") - pl.col("debut")) >= pl.duration(hours=3))
                  & (pl.col("debut").dt.minute() % 30 != 0))
    autres = ev.select("tranche", pl.col("debut").alias("d2"), pl.col("fin").alias("f2"), pl.col("id").alias("id2"))
    avant = (f.join(autres, on="tranche")
              .filter((pl.col("id") != pl.col("id2")) & (pl.col("d2") < pl.col("debut"))
                      & (pl.col("f2") > pl.col("debut") - pl.duration(hours=6)))["id"].unique())
    return f.filter(~pl.col("id").is_in(avant.to_list()))


def _jours_passage_ete(annees: range) -> list[date]:
    """Derniers dimanches de mars."""
    jours = []
    for an in annees:
        d = date(an, 3, 31)
        jours.append(d - timedelta(days=(d.weekday() + 1) % 7))
    return jours


def controle_fuseau_remit(raw: Path, natif: pl.DataFrame, brut: pl.DataFrame, ev: pl.DataFrame,
                          bornes: dict) -> Resultat:
    r = Resultat(f"Fuseau des dates REMIT = {remit.FUSEAU_REMIT} (arrêts fortuits contre éCO2mix, hiver et été ; "
                 "passage à l'heure d'été ; date de dépôt)", "OK")
    # 1. étude d'événements
    p = (natif.filter(pl.col("pas_min") == 30)
              .select(debut_periode(pl.col("ts_utc"), pl.col("pas_min")).alias("t0"), "nucleaire"))
    f = (_arrets_fortuits_nets(ev)
         .with_columns(pl.col("debut").dt.convert_time_zone(remit.FUSEAU_REMIT).dt.dst_offset().dt.total_minutes()
                         .alias("ete"), pl.col("debut").dt.truncate("30m").alias("base")))
    taus = pl.DataFrame({"tau": list(range(-FUSEAU_FENETRE_MIN, FUSEAU_FENETRE_MIN + 1, 30))})
    x = (f.select("id", "ete", "base").join(taus, how="cross")
          .with_columns((pl.col("base") + pl.duration(minutes=pl.col("tau"))).alias("t0"))
          .join(p, on="t0", how="inner").sort("id", "tau")
          .with_columns(pl.col("nucleaire").diff().over("id").alias("dd")).drop_nulls("dd"))
    prof = x.group_by("ete", "tau").agg(pl.col("dd").mean().alias("moy"), pl.col("id").n_unique().alias("n"))
    for ete, saison in ((0, "heure d'hiver"), (60, "heure d'été")):
        d = prof.filter(pl.col("ete") == ete).sort("tau")
        if d.height == 0 or d["n"].max() < FUSEAU_EVENEMENTS_MIN:
            r.statut = "ÉCHEC"
            r.lignes.append(f"{saison} : trop peu d'arrêts fortuits nets ({0 if d.height == 0 else d['n'].max()})")
            continue
        moy = dict(d.select("tau", "moy").iter_rows())
        pire = min(moy, key=moy.get)
        decal_utc = 60 if ete == 0 else 120
        ok = pire == 0
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{saison} : {d['n'].max()} arrêts ; baisse moyenne la plus forte à {pire:+d} min du début "
                        f"déclaré ({_f(moy[pire], 0)} MW par demi-heure) ; à +{decal_utc} min (lecture UTC) : "
                        f"{_f(moy.get(decal_utc, float('nan')), 0)} MW{'' if ok else '  ← fuseau à revoir'}")
    # 2. passage à l'heure d'été
    annees = range(brut["publication_local"].min().year, brut["publication_local"].max().year + 1)
    jours = _jours_passage_ete(annees)
    voisins = [j + timedelta(days=k) for j in jours for k in range(-7, 8) if k]
    for col in ("debut_local", "fin_local", "publication_local"):
        heure2 = brut.filter(pl.col(col).dt.hour() == 2)
        n = heure2.filter(pl.col(col).dt.date().is_in(jours)).height
        attendu = heure2.filter(pl.col(col).dt.date().is_in(voisins)).height / 14
        ok = n == 0
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"passage à l'heure d'été ({len(jours)} jours) : {n} date(s) « {col.removesuffix('_local')} » "
                        f"entre 02:00 et 02:59 (inexistantes à Paris) ; ≈ {_f(attendu, 1)} attendues si les dates "
                        f"étaient en UTC (moyenne des 14 jours voisins){'' if ok else '  ← fuseau à revoir'}")
    # 3. date de dépôt de l'historique
    m = lire_manifeste(raw).get("edf_remit/historique") or {}
    depot = m.get("mis_a_jour_source")
    if depot:
        depot = datetime.fromisoformat(depot.replace("Z", "+00:00"))
        derniere, locale = bornes["fin_historique"], bornes["fin_historique_local"]
        ok = derniere <= depot
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"historique : dernière publication « {locale:%d/%m/%Y %H:%M} » = {derniere:%H:%M} UTC lue en "
                        f"heure de Paris, déposé sur data-fair à {depot:%Y-%m-%d %H:%M} UTC"
                        f"{'' if ok else '  ← publication postérieure au dépôt'} ; lue en UTC elle serait "
                        f"{'postérieure' if locale.replace(tzinfo=timezone.utc) > depot else 'antérieure'} au dépôt")
    return r


# --------------------------------------------------------------------------
# « Quand ? » (data/export/quand.json, pc/quand.py, pc/export_quand.py)
# --------------------------------------------------------------------------

#: Tolérances d'arrondi de quand.json : MW à l'unité, TWh et parts à 4 décimales.
TOL_MW = 1.0
TOL_TWH = 2e-4
TOL_PART = 2e-4

#: Σ J (nucléaire déclaré disponible non produit) comparé à la modulation publiée : grandeurs
#: différentes (frontière modulation / indisponibilité fixée par EDF, réserves, Flamanville 3),
#: on vérifie seulement l'ordre de grandeur. Le spike trouvait 18 / 25 / 27-29 TWh pour 16 / 31 /
#: 33 TWh. Échec si le rapport sort de [1/2, 2].
RAPPORT_MODULATION = (0.5, 2.0)

#: Colonnes d'éCO2mix : écarts admis (arrondis des sous-filières ; bilan de quelques dizaines de MW).
TOL_HYDRO_MW = 3.0
TOL_GAZ_MW = 30.0
TOL_BILAN_MOYEN_MW = 150.0
TOL_COUVERTURE_MW = 15.0  # somme de 11 termes arrondis au MW
TOL_ECART_BILAN_TENDUES_MW = 300.0


def _quand(export: Path) -> dict:
    import json
    return json.loads((export / "quand.json").read_text(encoding="utf-8"))


def _table_arrondie(table: pl.DataFrame) -> pl.DataFrame:
    """Colonnes de « Quand ? » arrondies comme les CSV publiés, RN et J (recalcul polars, indépendant
    de pc/quand.py)."""
    from .export_quand import COLONNES
    t = table.select("heure_utc", annee_paris("heure_utc").alias("an"),
                     *[pl.col(src).round(dec).alias(nom) for src, (nom, dec) in COLONNES.items()])
    return t.with_columns(
        (pl.col("consommation") - pl.col("eolien") - pl.col("solaire") - pl.col("nucleaire_disponible")).alias("rn"),
        (pl.col("nucleaire_disponible") - pl.col("nucleaire")).clip(lower_bound=0).alias("j"))


def controle_quand_recalcul(q: dict, table: pl.DataFrame) -> Resultat:
    """quand.json (Python pur) = recalcul polars : RN max et sa date, Σ J, charges plates, prix."""
    r = Resultat("« Quand ? » : quand.json = recalcul indépendant (polars) — RN max et date, Σ J, parts tenues, "
                 "heures au-delà du max (annuel et pluriannuel), part avec plancher, J aux prix chers, production, "
                 "solde aux heures J ≥ X, couverture des heures tendues (échanges, gaz, "
                 "hydraulique), heures de "
                 "prix ≤ 0 et < 0", "OK")
    t = _table_arrondie(table)
    for an, a in q["annees"].items():
        d = t.filter(pl.col("an") == int(an))
        rn = d.drop_nulls("rn").sort(["rn", "heure_utc"], descending=[True, False])
        jv = d.drop_nulls("j")["j"]
        fautes = []
        rn_max = rn["rn"][0]
        h_max = rn["heure_utc"][0].strftime("%Y-%m-%dT%H:%MZ")
        if abs(a["charge_residuelle"]["max"]["valeur_mw"] - rn_max) > TOL_MW or a["charge_residuelle"]["max"]["heure_utc"] != h_max:
            fautes.append(f"RN max {a['charge_residuelle']['max']} ≠ {rn_max} à {h_max}")
        if abs(a["jeu_nucleaire"]["somme_twh"] - jv.sum() / 1e6) > TOL_TWH:
            fautes.append(f"Σ J {a['jeu_nucleaire']['somme_twh']} ≠ {jv.sum() / 1e6:.4f}")
        if (d["j"].drop_nulls() < 0).any():
            fautes.append("J < 0")
        for c in a["charges_plates"]:
            x = c["x_mw"]
            part = jv.clip(upper_bound=x).sum() / (x * jv.len())
            au_dela = int((rn["rn"] + x > rn_max).sum())
            hj = d.filter(pl.col("j") >= x).drop_nulls("ech_physiques")["ech_physiques"]
            solde = hj.mean() if hj.len() else None
            if (solde is None) != (c["solde_echanges_moyen_heures_j_ge_x_mw"] is None) or (
                    solde is not None and abs(c["solde_echanges_moyen_heures_j_ge_x_mw"] - solde) > TOL_MW):
                fautes.append(f"X = {x} MW : solde moyen aux heures J ≥ X {c['solde_echanges_moyen_heures_j_ge_x_mw']} "
                              f"≠ {solde}")
            if abs(c["part_dans_j"] - part) > TOL_PART or c["heures_rn_plus_x_au_dessus_du_max"] != au_dela \
                    or c["heures_j_superieur_ou_egal_x"] != int((jv >= x).sum()):
                fautes.append(f"X = {x} MW : part {c['part_dans_j']} / {part:.4f}, au-delà du max "
                              f"{c['heures_rn_plus_x_au_dessus_du_max']} / {au_dela}")
        from .quand import PLANCHER_J_MW, SEUIL_PRIX_CHER_EUR_MWH
        ref_pluri = (q.get("rn_max_pluriannuel") or {}).get("valeur_mw")
        jp = (jv - PLANCHER_J_MW).clip(lower_bound=0)
        for c in a["charges_plates"]:
            x = c["x_mw"]
            part_p = jp.clip(upper_bound=x).sum() / (x * jv.len())
            au_dela_ref = None if ref_pluri is None else int((rn["rn"] + x > ref_pluri).sum())
            if abs(c["part_dans_j_plancher"] - part_p) > TOL_PART or c["heures_rn_plus_x_au_dessus_du_max_reference"] != au_dela_ref:
                fautes.append(f"X = {x} MW : part avec plancher {c['part_dans_j_plancher']} / {part_p:.4f}, au-delà du "
                              f"max pluriannuel {c['heures_rn_plus_x_au_dessus_du_max_reference']} / {au_dela_ref}")
        ch = d.filter(pl.col("prix") > SEUIL_PRIX_CHER_EUR_MWH).drop_nulls("j")["j"]
        pc_ = a["jeu_nucleaire"]["prix_chers"]
        if pc_["heures"] != ch.len() or (ch.len() and abs(pc_["j_moyenne_mw"] - ch.mean()) > TOL_MW):
            fautes.append(f"J aux prix > {SEUIL_PRIX_CHER_EUR_MWH} : {pc_} ≠ {ch.len()} h, {ch.mean()}")
        prod = d["nucleaire"].drop_nulls().sum() / 1e6
        if abs(a["production_nucleaire_twh"] - prod) > TOL_TWH:
            fautes.append(f"production nucléaire {a['production_nucleaire_twh']} ≠ {prod:.4f} TWh")
        top = rn.head(a["heures_tendues"]["n"])
        if abs(a["heures_tendues"]["rn_moyenne_mw"] - top["rn"].mean()) > TOL_MW:
            fautes.append(f"RN moyenne des heures tendues {a['heures_tendues']['rn_moyenne_mw']} ≠ {top['rn'].mean():.0f}")
        cm = a["heures_tendues"]["couverture_moyenne_mw"]
        for c in ("ech_physiques", "gaz", "hydraulique_lacs", "hydraulique_step_turbinage", "hydraulique_fil_eau_eclusee"):
            if abs(cm[c] - top[c].mean()) > TOL_MW:
                fautes.append(f"couverture {c} {cm[c]} ≠ {top[c].mean():.0f} MW")
        p = d.drop_nulls("prix")
        neg, nul = int((p["prix"] < 0).sum()), int((p["prix"] <= 0).sum())
        if a["prix"]["heures_negatif"] != neg or a["prix"]["heures_nul_ou_negatif"] != nul:
            fautes.append(f"prix < 0 : {a['prix']['heures_negatif']} / {neg} ; ≤ 0 : {a['prix']['heures_nul_ou_negatif']} / {nul}")
        if fautes:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : RN max {_f(rn_max, 0)} MW ({h_max}), Σ J {_f(jv.sum() / 1e6, 2)} TWh"
                        + ("" if not fautes else "  ← " + " ; ".join(fautes)))
    return r


def controle_quand_coherence(q: dict, annees_pleines: list[int]) -> Resultat:
    """Propriétés internes : J ≥ 0, profil mensuel = total, part tenue décroissante et ≤ 1,
    Σ min(X, J) ≤ Σ J, monotone cohérente avec le maximum et les heures tendues, couverture qui boucle."""
    r = Resultat("« Quand ? » : J ≥ 0 ; Σ mois = Σ année ; part tenue décroissante en X et ≤ 1 ; Σ min(X, J) ≤ Σ J ; "
                 "monotone ↔ max ↔ heures tendues ; couverture des heures tendues = RN moyenne", "OK")
    if sorted(int(a) for a in q["annees"]) != annees_pleines:
        r.statut = "ÉCHEC"
        r.lignes.append(f"années de quand.json {sorted(q['annees'])} ≠ années pleines {annees_pleines}")
    for an, a in q["annees"].items():
        cr, jeu, td, cp = a["charge_residuelle"], a["jeu_nucleaire"], a["heures_tendues"], a["charges_plates"]
        fautes = []
        if min(jeu["par_mois_twh"]) < 0 or jeu["somme_twh"] < 0:
            fautes.append("J négatif")
        if abs(sum(jeu["par_mois_twh"]) - jeu["somme_twh"]) > 12 * TOL_TWH:
            fautes.append(f"Σ mois {sum(jeu['par_mois_twh']):.4f} ≠ {jeu['somme_twh']}")
        parts = [c["part_dans_j"] for c in cp]
        if any(p < 0 or p > 1 for p in parts) or any(b > a_ + TOL_PART for a_, b in zip(parts, parts[1:])):
            fautes.append(f"parts tenues {parts}")
        for c in cp:
            if c["energie_dans_j_twh"] > jeu["somme_twh"] + TOL_TWH or c["energie_dans_j_twh"] > c["energie_ajoutee_twh"] + TOL_TWH:
                fautes.append(f"X = {c['x_mw']} : Σ min(X, J) = {c['energie_dans_j_twh']} TWh > Σ J ou > énergie ajoutée")
            if c["rn_max_plus_x_mw"] != cr["max"]["valeur_mw"] + c["x_mw"]:
                fautes.append(f"X = {c['x_mw']} : RN max + X")
        parts_p = [c["part_dans_j_plancher"] for c in cp]
        if any(pp > p_ + TOL_PART or pp < 0 for pp, p_ in zip(parts_p, parts)) \
                or any(b > a_ + TOL_PART for a_, b in zip(parts_p, parts_p[1:])) \
                or any(c["energie_dans_j_plancher_twh"] > c["energie_dans_j_twh"] + TOL_TWH for c in cp):
            fautes.append(f"parts avec plancher {parts_p} (≤ sans plancher, décroissantes en X)")
        ref = [c["heures_rn_plus_x_au_dessus_du_max_reference"] for c in cp]
        if ref != sorted(ref) or any(r_ > c["heures_rn_plus_x_au_dessus_du_max"] for r_, c in zip(ref, cp)):
            fautes.append(f"heures au-delà du max pluriannuel {ref} (croissantes en X, ≤ au-delà du max annuel)")
        pluri = q.get("rn_max_pluriannuel")
        if not pluri or cr["max"]["valeur_mw"] > pluri["valeur_mw"]:
            fautes.append("maximum annuel au-dessus du maximum pluriannuel")
        au_dela = [c["heures_rn_plus_x_au_dessus_du_max"] for c in cp]
        if au_dela != sorted(au_dela) or au_dela[0] < 1:
            fautes.append(f"heures au-delà du max non croissantes en X : {au_dela}")
        mono = cr["monotone"]
        valeurs = [v for _, v in mono]
        if mono[0] != [1, cr["max"]["valeur_mw"]] or valeurs != sorted(valeurs, reverse=True) \
                or mono[-1] != [cr["heures_valides"], cr["min"]["valeur_mw"]]:
            fautes.append("monotone incohérente avec le max ou le min")
        if [v for _, v in td["heures"]] != valeurs[:td["n"]] or td["rn_min_mw"] != valeurs[td["n"] - 1]:
            fautes.append("heures tendues ≠ premiers rangs de la monotone")
        qs = list(cr["quantiles_mw"].values())
        if qs != sorted(qs) or qs[0] < cr["min"]["valeur_mw"] or qs[-1] > cr["max"]["valeur_mw"]:
            fautes.append("quantiles non ordonnés")
        if sum(td["par_mois"]) != td["n"] or sum(td["par_heure_paris"]) != td["n"]:
            fautes.append("répartition des heures tendues")
        cm = td["couverture_moyenne_mw"]
        somme = sum(cm.values())
        if td["heures_couverture"] != td["n"] or abs(somme - td["rn_moyenne_mw"]) > TOL_COUVERTURE_MW:
            fautes.append(f"couverture {somme} MW ≠ RN moyenne {td['rn_moyenne_mw']} MW")
        if abs(cm["ecart_bilan_eco2mix"]) > TOL_ECART_BILAN_TENDUES_MW:
            fautes.append(f"écart de bilan aux heures tendues {cm['ecart_bilan_eco2mix']} MW")
        if fautes:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : parts tenues {', '.join(_f(p * 100, 1) for p in parts)} % ; couverture "
                        f"{_f(somme, 0)} MW pour RN moyenne {_f(td['rn_moyenne_mw'], 0)} MW (écart de bilan "
                        f"{_f(cm['ecart_bilan_eco2mix'], 0)} MW)" + ("" if not fautes else "  ← " + " ; ".join(fautes)))
    pluri = q.get("rn_max_pluriannuel") or {}
    origine = q["annees"].get(str(pluri.get("annee")), {}).get("charge_residuelle", {}).get("max")
    if not origine or {k: origine[k] for k in ("valeur_mw", "heure_utc")} != {k: pluri[k] for k in ("valeur_mw", "heure_utc")}:
        r.statut = "ÉCHEC"
        r.lignes.append(f"maximum pluriannuel {pluri} ≠ maximum de son année")
    else:
        r.lignes.append(f"maximum pluriannuel {pluri['annees']} : {_f(pluri['valeur_mw'], 0)} MW, {pluri['debut_paris']} "
                        f"(heure de Paris de début)")
    for an, motif in q["annees_exclues"].items():
        r.lignes.append(f"{an} exclue : {motif}")
    return r


def controle_quand_heures_negatives(q: dict, table: pl.DataFrame) -> Resultat:
    r = Resultat("« Quand ? » : heures à prix < 0 = Bilans RTE (référentiel heures_negatives_*) et = calcul de "
                 "build.heures_negatives, chaque année", "OK")
    from . import chiffres
    ref = chiffres.charger().chiffres
    calc = heures_negatives(table.select("heure_utc", "prix_eur_mwh"))
    for an, a in q["annees"].items():
        n = a["prix"]["heures_negatif"]
        c = ref.get(f"heures_negatives_{an}")
        ok = n == calc.get(int(an), 0) and (c is None or n == c["valeur"])
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : < 0 {n} h, ≤ 0 {a['prix']['heures_nul_ou_negatif']} h ; build {calc.get(int(an), 0)}"
                        + (f", RTE {c['valeur']}" if c else " (non recoupé)") + ("" if ok else "  ← différent"))
    return r


def controle_quand_modulation(q: dict) -> Resultat:
    """Ordre de grandeur de Σ J contre la modulation publiée (autre grandeur : pas d'égalité attendue)."""
    from . import chiffres
    from .export_quand import MODULATION_PUBLIEE
    lo, hi = RAPPORT_MODULATION
    r = Resultat(f"« Quand ? » : Σ J du même ordre que la modulation publiée par EDF (rapport dans [{_f(lo, 1)} ; "
                 f"{_f(hi, 0)}]), sans l'égaler — écart affiché", "OK")
    ref = chiffres.charger().chiffres
    for an, cle in MODULATION_PUBLIEE.items():
        a, m = q["annees"].get(str(an)), ref.get(cle)
        if a is None or m is None:
            r.statut = "ÉCHEC"
            r.lignes.append(f"{an} : {'quand.json' if a is None else cle} absent")
            continue
        j, mod = a["jeu_nucleaire"]["somme_twh"], float(m["valeur"])
        rapport = j / mod
        ok = lo <= rapport <= hi
        if not ok:
            r.statut = "ÉCHEC"
        f3 = a["jeu_nucleaire"].get("flamanville3")
        r.lignes.append(f"{an} : Σ J {_f(j, 1)} TWh"
                        + (f" (hors EPR : {_f(f3['somme_j_sans_disponible_epr_twh'], 1)} à {_f(j, 1)})" if f3 else "")
                        + f", modulation EDF {_f(mod, 0)} TWh ({cle}) ; écart {_f(j - mod, 1)} TWh "
                          f"({_pct(rapport - 1, 0)}){'' if ok else '  ← hors ordre de grandeur'}")
    be = ref.get("modulation_nucleaire_2025_be")
    if be and "2025" in q["annees"]:
        j = q["annees"]["2025"]["jeu_nucleaire"]["somme_twh"]
        r.lignes.append(f"2025 : RTE « de l'ordre d'une trentaine de TWh » ; écart {_f(j - float(be['valeur']), 1)} TWh")
    r.lignes.append("grandeurs différentes : J compte le disponible DÉCLARÉ non produit (réserves comprises, arrêts pour "
                    "économie de combustible déclarés indisponibles exclus) ; la modulation d'EDF suit sa propre frontière")
    return r


#: Production nucléaire publiée (BE2025) contre la somme éCO2mix : même éditeur, périmètres proches
#: (la phrase de RTE ne précise pas l'EPR) ; une erreur d'unité ou d'heures donnerait bien plus.
TOL_PRODUCTION_RELATIVE = 0.005


def controle_quand_production(q: dict) -> Resultat:
    from . import chiffres
    r = Resultat("« Quand ? » : production nucléaire éCO2mix (somme horaire) ≈ RTE, BE2025 (± 0,5 %)", "OK")
    ref = chiffres.charger().chiffres
    for an, a in q["annees"].items():
        c = ref.get(f"prod_nucleaire_{an}")
        prod = a["production_nucleaire_twh"]
        if c is None:
            r.lignes.append(f"{an} : {_f(prod, 1)} TWh (non recoupé)")
            continue
        ecart = prod / float(c["valeur"]) - 1
        ok = abs(ecart) <= TOL_PRODUCTION_RELATIVE
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : éCO2mix {_f(prod, 1)} TWh, RTE {_f(float(c['valeur']), 1)} TWh ; écart {_pct(ecart, 2)}"
                        + ("" if ok else "  ← hors tolérance"))
    if not any(k.startswith("prod_nucleaire_") and k[-4:].isdigit() for k in ref):
        r.statut = "ÉCHEC"
        r.lignes.append("aucune production nucléaire de référence dans le référentiel")
    return r


def controle_colonnes_eco2mix(table: pl.DataFrame, annees: list[int]) -> Resultat:
    from .export_quand import verifier_colonnes_eco2mix
    r = Resultat(f"Colonnes éCO2mix : hydraulique = Σ sous-filières (± {_f(TOL_HYDRO_MW, 0)} MW), gaz = Σ sous-filières "
                 f"(± {_f(TOL_GAZ_MW, 0)} MW), consommation = Σ filières + pompage + solde (écart moyen ± "
                 f"{_f(TOL_BILAN_MOYEN_MW, 0)} MW), pompage ≤ 0", "OK")
    for an, v in verifier_colonnes_eco2mix(table, annees)["par_annee"].items():
        ok = (v["hydraulique_moins_sous_filieres_max_mw"] <= TOL_HYDRO_MW and v["gaz_moins_sous_filieres_max_mw"] <= TOL_GAZ_MW
              and abs(v["ecart_bilan_moyen_mw"]) <= TOL_BILAN_MOYEN_MW and v["pompage_max_mw"] <= 0)
        if not ok:
            r.statut = "ÉCHEC"
        r.lignes.append(f"{an} : hydraulique {_f(v['hydraulique_moins_sous_filieres_max_mw'], 1)} MW, gaz "
                        f"{_f(v['gaz_moins_sous_filieres_max_mw'], 1)} MW ; bilan moyen {_f(v['ecart_bilan_moyen_mw'], 1)} "
                        f"MW (max {_f(v['ecart_bilan_max_mw'], 0)}) ; pompage max {_f(v['pompage_max_mw'], 0)} MW"
                        + ("" if ok else "  ← hors tolérance"))
    return r


def controle_quand_chiffres(q: dict, export: Path) -> Resultat:
    """chiffres.json porte exactement les chiffres calculés depuis quand.json, au schéma du référentiel."""
    import json
    from . import chiffres
    from .export_quand import MODULATION_PUBLIEE, SOURCE_QUAND, chiffres_calcules
    r = Resultat("« Quand ? » : chiffres calculés de chiffres.json = quand.json, valeur publiée = arrondi (GW et TWh "
                 "à 0,1, % à l'entier) de la valeur non arrondie ; référentiel fusionné valide", "OK")
    ref = chiffres.charger()
    modulation = {an: ref.chiffres[c] for an, c in MODULATION_PUBLIEE.items() if c in ref.chiffres}
    attendus = chiffres_calcules(q, modulation)
    publies = json.loads((export / "chiffres.json").read_text(encoding="utf-8"))["chiffres"]
    source = (publies.get(next(iter(attendus)), {}).get("source") or {})
    fusion = chiffres.fusionner(ref, {SOURCE_QUAND: {k: v for k, v in source.items() if k != "cle"}}, attendus)
    erreurs = chiffres.valider(fusion)
    for cle, c in attendus.items():
        p = publies.get(cle)
        if p is None:
            erreurs.append(f"{cle} absent de chiffres.json")
        elif ({k: v for k, v in p.items() if k != "source"} != {k: v for k, v in c.items() if k != "source"}
              or p["source"].get("cle") != SOURCE_QUAND):
            erreurs.append(f"{cle} : chiffres.json ≠ quand.json (relancer `pc build`)")
        else:
            # la valeur publiée est l'arrondi de la valeur non arrondie de quand.json, à un demi-pas près
            if abs(p["valeur"] - p["valeur_calculee"]) > p["precision"] / 2 + 1e-9:
                erreurs.append(f"{cle} : valeur publiée {p['valeur']} à plus d'un demi-pas de {p['valeur_calculee']}")
    orphelins = sorted(k for k, v in publies.items() if v.get("produit_par") and k not in attendus)
    erreurs += [f"{k} : chiffre calculé orphelin" for k in orphelins]
    if erreurs:
        r.statut = "ÉCHEC"
    r.lignes.append(f"{len(attendus)} chiffres calculés ; source « {SOURCE_QUAND} » datée du "
                    f"{source.get('date_publication', '?')}")
    r.lignes += erreurs
    return r


def controles_quand(export: Path, table: pl.DataFrame) -> list:
    from .export_quand import annees_pleines
    if not (export / "quand.json").exists():
        return [lambda: Resultat("« Quand ? »", "ÉCHEC", ["quand.json absent : lancer `pc build`"])]
    q = _quand(export)
    pleines, _ = annees_pleines(table)
    return [
        lambda: controle_colonnes_eco2mix(table, pleines),
        lambda: controle_quand_coherence(q, pleines),
        lambda: controle_quand_recalcul(q, table),
        lambda: controle_quand_heures_negatives(q, table),
        lambda: controle_quand_modulation(q),
        lambda: controle_quand_production(q),
        lambda: controle_quand_chiffres(q, export),
    ]


# --------------------------------------------------------------------------


def controle_referentiel() -> Resultat:
    """Référentiel des chiffres publiés (referentiels/chiffres.yaml) : unités, sources,
    confiance, contraintes d'ordre (pc/chiffres.py)."""
    from . import chiffres
    ref = chiffres.charger()
    erreurs = chiffres.valider(ref)
    return Resultat(f"Référentiel des chiffres : {len(ref.chiffres)} chiffres, {len(ref.sources)} sources, "
                    f"{len(ref.contraintes)} contraintes d'ordre", "ÉCHEC" if erreurs else "OK", erreurs)


def check(raw: Path, export: Path, aujourd_hui: date | None = None, derive: Path | None = None) -> int:
    annee_courante = (aujourd_hui or date.today()).year
    chemin = export / "systeme_horaire.parquet"
    if not chemin.exists():
        print(f"ÉCHEC : {chemin} absent ; lancer `pc build`.")
        return 1
    table = pl.read_parquet(chemin)
    natif, _ = charger_eco2mix(raw)
    assert set(PAS_MIN.values()) <= {15, 30}
    try:
        brut, ev, par_tranche, bornes = _remit_par_tranche(raw, table)
        controles_remit = [
            lambda: controle_remit_jonction(bornes),
            lambda: controle_taux_rte(par_tranche, table),
            lambda: controle_production_sous_disponible(table),
            lambda: controle_fuseau_remit(raw, natif, brut, ev, bornes),
        ]
    except Exception as err:  # source absente ou illisible : échec, pas arrêt
        controles_remit = [lambda err=err: Resultat("Disponibilité nucléaire REMIT", "ÉCHEC", [f"erreur : {err!r}"])]
    controles = [
        controle_referentiel,
        lambda: controle_consommation(raw, natif, annee_courante),
        lambda: controle_convention_cons_def(raw, natif),
        lambda: controle_nucleaire(raw, table),
        lambda: controle_convention_temps_reel(raw, natif),
        lambda: controle_heures_negatives(table),
        lambda: controle_intensite(raw, table),
        lambda: controle_completude(table, annee_courante),
        *controles_remit,
        *controles_quand(export, table),
    ]
    try:  # ENTSO-E (pc/check_entsoe.py) : INFO sans données, ÉCHEC si le brut existe sans dérivés
        from . import check_entsoe
        controles += check_entsoe.controles(raw, derive if derive is not None else export.parent / "derive", table)
    except Exception as err:
        controles.append(lambda err=err: Resultat("ENTSO-E", "ÉCHEC", [f"erreur : {err!r}"]))
    resultats = []
    for c in controles:
        try:
            resultats.append(c())
        except Exception as err:  # un contrôle qui plante est un échec, pas un arrêt
            resultats.append(Resultat(getattr(c, "__name__", "contrôle"), "ÉCHEC", [f"erreur : {err!r}"]))
    for res in resultats:
        print(f"[{res.statut}] {res.nom}")
        for ligne in res.lignes:
            print(f"    {ligne}")
    echecs = [res for res in resultats if res.statut == "ÉCHEC"]
    print(f"\n{len(resultats) - len(echecs)} contrôle(s) sans échec, {len(echecs)} échec(s).")
    sys.stdout.flush()
    return 1 if echecs else 0
