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

from .build import (DATETIME_UTC, PAS_MIN, annee_paris, charger_eco2mix, debut_periode, heures_negatives,
                    mw_vers_mwh)
from .sources import ANNEE_DEBUT, fichier, fichiers_annuels

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


def controle_referentiel() -> Resultat:
    """Référentiel des chiffres publiés (referentiels/chiffres.yaml) : unités, sources,
    confiance, contraintes d'ordre (pc/chiffres.py)."""
    from . import chiffres
    ref = chiffres.charger()
    erreurs = chiffres.valider(ref)
    return Resultat(f"Référentiel des chiffres : {len(ref.chiffres)} chiffres, {len(ref.sources)} sources, "
                    f"{len(ref.contraintes)} contraintes d'ordre", "ÉCHEC" if erreurs else "OK", erreurs)


def check(raw: Path, export: Path, aujourd_hui: date | None = None) -> int:
    annee_courante = (aujourd_hui or date.today()).year
    chemin = export / "systeme_horaire.parquet"
    if not chemin.exists():
        print(f"ÉCHEC : {chemin} absent ; lancer `pc build`.")
        return 1
    table = pl.read_parquet(chemin)
    natif, _ = charger_eco2mix(raw)
    assert set(PAS_MIN.values()) <= {15, 30}
    controles = [
        controle_referentiel,
        lambda: controle_consommation(raw, natif, annee_courante),
        lambda: controle_convention_cons_def(raw, natif),
        lambda: controle_nucleaire(raw, table),
        lambda: controle_convention_temps_reel(raw, natif),
        lambda: controle_heures_negatives(table),
        lambda: controle_intensite(raw, table),
        lambda: controle_completude(table, annee_courante),
    ]
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
