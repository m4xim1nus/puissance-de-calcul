"""Spike jetable : accès aux sources « système électrique horaire ».

Relançable :
    uv run --no-project --with httpx,polars python -I pipeline/explo/spike_systeme.py download
    uv run --no-project --with httpx,polars python -I pipeline/explo/spike_systeme.py analyse

Les échantillons vont dans data/raw/spike/systeme/ (non versionné). Les
téléchargements sont sautés si le fichier existe déjà. Aucun jeton requis.
Rapport associé : docs/spike/systeme.md.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import polars as pl

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "spike" / "systeme"
ODRE = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets"
EC = "https://api.energy-charts.info"
ELEXON = "https://data.elexon.co.uk/bmrs/api/v1"

# --------------------------------------------------------------------------
# Téléchargement
# --------------------------------------------------------------------------


def _get(client: httpx.Client, url: str, dest: Path, params: dict | None = None) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  déjà là : {dest.name}")
        return
    t0 = time.time()
    for attempt in range(5):
        r = client.get(url, params=params)
        if r.status_code == 429:  # energy-charts : respecter Retry-After
            wait = int(r.headers.get("Retry-After", "60"))
            print(f"  429, attente {wait} s")
            time.sleep(wait)
            continue
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f"  {dest.name} : {len(r.content) / 1e6:.2f} Mo en {time.time() - t0:.0f} s")
        return
    raise RuntimeError(f"échec {url}")


def odre_export(client, dataset: str, dest: str, where: str | None = None, fmt: str = "parquet"):
    params = {"where": where} if where else None
    _get(client, f"{ODRE}/{dataset}/exports/{fmt}", RAW / dest, params)


def download() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    y2024 = "date_heure >= '2024-01-01T00:00:00+01:00' and date_heure < '2025-01-01T00:00:00+01:00'"
    # Les exports ODRÉ sont lents (~5 min pour 23 Mo) : timeout large.
    with httpx.Client(timeout=900, follow_redirects=True) as c:
        print("ODRÉ")
        odre_export(c, "eco2mix-national-cons-def", "eco2mix_national_cons_def_all.parquet")
        odre_export(c, "eco2mix-national-tr", "eco2mix_national_tr.parquet")
        odre_export(c, "eco2mix-regional-cons-def", "eco2mix_regional_2024.parquet", y2024)
        odre_export(c, "eco2mix-regional-tr", "eco2mix_regional_tr.parquet")
        odre_export(c, "registre-national-installation-production-stockage-electricite-agrege",
                    "registre_agrege_20260930.parquet")
        odre_export(c, "registre-national-installation-production-stockage-electricite-agrege-311224",
                    "registre_agrege_311224.parquet")
        odre_export(c, "production-nette-nucleaire", "nucleaire_horaire.parquet")
        odre_export(c, "part-enr-intensite-ges-conso-tr", "ges_conso_horaire.parquet")
        odre_export(c, "imports-exports-commerciaux", "echanges_commerciaux_2024.parquet",
                    "date >= date'2024-01-01' and date <= date'2024-12-31'")
        odre_export(c, "consommation-annuelle-brute", "consommation_annuelle_brute.parquet")
        odre_export(c, "consommation-annuelle-brute-regionale", "consommation_annuelle_brute_regionale.parquet")
        odre_export(c, "prod-national-annuel-filiere", "prod_national_annuel_filiere.parquet")

        print("energy-charts (2 req/min par endpoint, /price burst 2)")
        for y in (2023, 2024, 2025):
            _get(c, f"{EC}/price", RAW / f"ec_price_FR_{y}.json",
                 {"bzn": "FR", "start": f"{y}-01-01", "end": f"{y}-12-31"})
            time.sleep(31)
        # Licence par zone (champ license_info) et profondeur historique FR
        for bzn in ("ES", "DE-LU", "CH", "IT-North"):
            _get(c, f"{EC}/price", RAW / f"ec_price_{bzn}_2024-06-01.json", {"bzn": bzn, "start": "2024-06-01", "end": "2024-06-01"})
            time.sleep(40)
        for d in ("2015-01-05", "2016-01-04", "2017-01-02", "2018-01-02", "2018-10-01", "2019-01-02"):
            try:
                _get(c, f"{EC}/price", RAW / f"ec_price_FR_depth_{d}.json", {"bzn": "FR", "start": d, "end": d})
            except httpx.HTTPStatusError as err:  # 404 « No content available » = pas de donnée
                print(f"  FR {d} : HTTP {err.response.status_code}")
            time.sleep(40)
        _get(c, f"{EC}/public_power", RAW / "ec_public_power_fr_2024.json",
             {"country": "fr", "start": "2024-01-01", "end": "2024-12-31"})
        for ctry in ("de", "be", "es", "it", "ch", "uk"):
            _get(c, f"{EC}/public_power", RAW / f"ec_public_power_{ctry}_20240601.json",
                 {"country": ctry, "start": "2024-06-01", "end": "2024-06-01"})
            time.sleep(31)
        for ep in ("cbet", "cbpf"):
            _get(c, f"{EC}/{ep}", RAW / f"ec_{ep}_FR_2024w.json",
                 {"country": "fr", "start": "2024-06-01", "end": "2024-06-07"})

        print("Elexon (GB, sans clé)")
        _get(c, f"{ELEXON}/datasets/FUELHH", RAW / "elexon_fuelhh_20240601.json",
             {"settlementDateFrom": "2024-06-01", "settlementDateTo": "2024-06-01", "format": "json"})


# --------------------------------------------------------------------------
# Analyse
# --------------------------------------------------------------------------

FILIERES_NAT = ["fioul", "charbon", "gaz", "nucleaire", "eolien", "solaire", "hydraulique", "bioenergies"]

# Références publiées (URL + date de consultation 2026-11-25) — voir le rapport.
REF = {
    "conso_brute_2024_TWh_BE2024": 442.2,  # BE2024 rapport complet, p. « Consommation »
    "conso_brute_2024_GWh_ODRE": 442_336,  # ODRÉ consommation-annuelle-brute (Définitif)
    "conso_brute_2025_TWh_BE2025": 446.1,
    "co2_prod_2024_BE2024": 21.7,  # gCO2eq/kWh, émissions directes, production
    "co2_prod_2025_BE2025": 19.6,
    "co2_conso_2025_BE2025": 20.0,
    "neg_h_2023_BE2024": 147,
    "neg_h_2024_BE2024": 361,
    "neg_h_2024_BE2025": 352,
    "neg_h_2025_BE2025": 513,
}


def _load_nat() -> pl.DataFrame:
    df = pl.read_parquet(RAW / "eco2mix_national_cons_def_all.parquet")
    # piège : certaines colonnes sont typées texte dans le schéma ODRÉ
    for col in ("ech_comm_allemagne_belgique", "gaz_cogen"):
        if df.schema[col] == pl.Utf8:
            df = df.with_columns(pl.col(col).cast(pl.Float64, strict=False))
    return df.with_columns(
        pl.col("date_heure").dt.convert_time_zone("UTC").alias("ts_utc"),
        pl.col("date").cast(pl.Utf8).str.slice(0, 4).cast(pl.Int32).alias("annee_locale"),
    )


def analyse_eco2mix_national() -> None:
    print("\n=== éCO2mix national (cons-def) ===")
    df = _load_nat()
    print("schéma date_heure :", df.schema["date_heure"], "| lignes :", df.height)
    print(df.group_by("nature").agg(pl.len(), pl.col("ts_utc").min().alias("debut"), pl.col("ts_utc").max().alias("fin")))

    # Pas de temps effectif : lignes renseignées par minute
    pas = (df.with_columns(pl.col("ts_utc").dt.minute().alias("mn"))
             .group_by("mn").agg(pl.len().alias("lignes"), pl.col("consommation").count().alias("conso_non_nulle"))
             .sort("mn"))
    print("Lignes par minute de l'heure (toutes années) :\n", pas)

    # Heure d'été / d'hiver : nombre de lignes renseignées par date locale
    for d in ("2024-03-31", "2024-10-27", "2025-03-30", "2025-10-26"):
        sub = df.filter(pl.col("date").cast(pl.Utf8) == d)
        print(f"  {d} : {sub.height} lignes, {sub['consommation'].count()} conso non nulles, "
              f"heures locales distinctes = {sub['heure'].n_unique()}")

    # Bilan annuel (année civile locale, lignes à :00/:30 → 1 ligne = 0,5 h)
    v = df.filter(pl.col("consommation").is_not_null())
    v = v.with_columns(
        pl.sum_horizontal(FILIERES_NAT).alias("production"),
        (pl.col("consommation") - pl.sum_horizontal(FILIERES_NAT) - pl.col("pompage") - pl.col("ech_physiques"))
        .alias("residu"),
    )
    an = (v.group_by("annee_locale").agg(
        pl.len().alias("demi_heures"),
        (pl.col("consommation").sum() * 0.5 / 1e6).alias("conso_TWh"),
        (pl.col("production").sum() * 0.5 / 1e6).alias("prod_TWh"),
        (pl.col("nucleaire").sum() * 0.5 / 1e6).alias("nuc_TWh"),
        (pl.col("pompage").sum() * 0.5 / 1e6).alias("pompage_TWh"),
        (pl.col("ech_physiques").sum() * 0.5 / 1e6).alias("solde_phys_TWh"),
        ((pl.col("taux_co2") * pl.col("production")).sum() / pl.col("production").sum()).alias("co2_pondere"),
        pl.col("taux_co2").mean().alias("co2_moyenne_simple"),
        pl.col("residu").abs().mean().alias("residu_abs_moy_MW"),
        pl.col("residu").abs().max().alias("residu_abs_max_MW"),
    ).sort("annee_locale"))
    with pl.Config(tbl_cols=-1, tbl_width_chars=250, float_precision=2):
        print(an)

    a24 = an.filter(pl.col("annee_locale") == 2024).row(0, named=True)
    a25 = an.filter(pl.col("annee_locale") == 2025).row(0, named=True)
    print(f"Recoupement conso 2024 : éCO2mix {a24['conso_TWh']:.2f} TWh vs BE2024 {REF['conso_brute_2024_TWh_BE2024']} "
          f"(écart {100 * (a24['conso_TWh'] / REF['conso_brute_2024_TWh_BE2024'] - 1):+.2f} %) ; "
          f"vs ODRÉ annuel {REF['conso_brute_2024_GWh_ODRE'] / 1e3:.3f}")
    print(f"Recoupement conso 2025 : éCO2mix {a25['conso_TWh']:.2f} TWh vs BE2025 {REF['conso_brute_2025_TWh_BE2025']} "
          f"(écart {100 * (a25['conso_TWh'] / REF['conso_brute_2025_TWh_BE2025'] - 1):+.2f} %)")
    reg = pl.read_parquet(RAW / "consommation_annuelle_brute_regionale.parquet").with_columns(
        pl.col("annee").cast(pl.Utf8).str.slice(0, 4).cast(pl.Int32).alias("an"))
    for an_, row in ((2024, a24), (2025, a25)):
        r = reg.filter(pl.col("an") == an_)
        corse = r.filter(pl.col("region") == "Corse")["consommation_brute_electricite_rte"].sum() / 1e3
        cont = r.filter(pl.col("region") != "Corse")["consommation_brute_electricite_rte"].sum() / 1e3
        print(f"  {an_} : ODRÉ régional hors Corse {cont:.3f} TWh (Corse {corse:.3f}) ; éCO2mix {row['conso_TWh']:.3f} ; "
              f"écart {1e3 * (row['conso_TWh'] - cont):+.0f} GWh ({100 * (row['conso_TWh'] / cont - 1):+.3f} %)")
    print(f"CO2 2024 : pondéré {a24['co2_pondere']:.2f}, simple {a24['co2_moyenne_simple']:.2f} vs BE2024 {REF['co2_prod_2024_BE2024']}")
    print(f"CO2 2025 : pondéré {a25['co2_pondere']:.2f}, simple {a25['co2_moyenne_simple']:.2f} vs BE2025 {REF['co2_prod_2025_BE2025']}")

    # Agrégation horaire UTC (moyenne des deux demi-heures = MWh sur l'heure)
    h = (v.with_columns(pl.col("ts_utc").dt.truncate("1h").alias("h"))
          .group_by("h").agg(pl.len().alias("n"), pl.col("consommation").mean()))
    print("Heures UTC avec ≠ 2 demi-heures :", h.filter(pl.col("n") != 2).height, "sur", h.height)
    trous = (v.sort("ts_utc").with_columns(pl.col("ts_utc").diff().alias("dt"))
               .filter(pl.col("dt") != pl.duration(minutes=30)))
    print("Sauts ≠ 30 min dans la série renseignée :", trous.height)
    if trous.height:
        print(trous.select("ts_utc", "dt", "nature").head(10))

    # Convention d'horodatage (non documentée) : centroïde horaire de la production solaire de juin 2024.
    # energy-charts horodate le DÉBUT de l'heure (documenté) → centre réel = centroïde + 30 min.
    jun = v.filter(pl.col("date").cast(pl.Utf8).str.starts_with("2024-06")).with_columns(
        (pl.col("ts_utc").dt.hour().cast(pl.Int32) * 60 + pl.col("ts_utc").dt.minute().cast(pl.Int32)).alias("mn"))
    c_eco = (jun["mn"] * jun["solaire"]).sum() / jun["solaire"].sum()
    d = json.loads((RAW / "ec_public_power_fr_2024.json").read_text())
    sol = next(p["data"] for p in d["production_types"] if p["name"] == "Solar")
    ec = [(datetime.fromtimestamp(t, timezone.utc), x) for t, x in zip(d["unix_seconds"], sol) if x is not None]
    ec = [(t.hour * 60, x) for t, x in ec if t.month == 6]
    c_ec = sum(m * x for m, x in ec) / sum(x for _, x in ec) + 30
    print(f"Centroïde solaire juin 2024 (UTC) : éCO2mix horodatages {c_eco // 60:.0f}:{c_eco % 60:02.0f} ; "
          f"energy-charts centre réel {c_ec // 60:.0f}:{c_ec % 60:02.0f} → si horodatage = fin de demi-heure, attendu centre + 15 min")
    for d_ in ("2024-03-31", "2024-10-27"):
        print(v.filter(pl.col("date").cast(pl.Utf8) == d_).sort("ts_utc")
               .filter(pl.col("heure").is_in(["01:30", "02:00", "02:30", "03:00"])).select("date", "heure", "ts_utc", "consommation", "prevision_j1"))

    # Valeurs manquantes par colonne sur les lignes renseignées
    nulls = v.select([pl.col(c).null_count().alias(c) for c in FILIERES_NAT + ["pompage", "ech_physiques", "taux_co2",
                                                                              "ech_comm_espagne", "ech_comm_allemagne_belgique"]])
    print("Nulls sur lignes renseignées :", nulls.to_dicts()[0])


def analyse_eco2mix_tr() -> None:
    print("\n=== éCO2mix national temps réel ===")
    df = pl.read_parquet(RAW / "eco2mix_national_tr.parquet")
    df = df.with_columns(pl.col("date_heure").dt.convert_time_zone("UTC").alias("ts"))
    now = datetime.now(timezone.utc)
    print("lignes", df.height, "| min", df["ts"].min(), "| max", df["ts"].max())
    print("pas : lignes conso non nulles par minute :",
          df.group_by(pl.col("ts").dt.minute().alias("mn")).agg(pl.col("consommation").count(), pl.col("nucleaire").count()).sort("mn").to_dicts())
    fut = df.filter(pl.col("ts") > pl.lit(now))
    print("lignes dans le futur (prévisions seules) :", fut.height,
          "dont conso non nulle :", fut["consommation"].count(), "prevision_j1 non nulle :", fut["prevision_j1"].count())
    print("stockage batterie (MW) moy/max :", df["stockage_batterie"].mean(), df["stockage_batterie"].max(),
          "| destockage max :", df["destockage_batterie"].max())


def analyse_eco2mix_regional() -> None:
    print("\n=== éCO2mix régional 2024 ===")
    df = pl.read_parquet(RAW / "eco2mix_regional_2024.parquet")
    df = df.with_columns(pl.col("date_heure").dt.convert_time_zone("UTC").alias("ts"))
    print("lignes", df.height)
    print(df.group_by("libelle_region").agg(pl.len(), pl.col("consommation").count()).sort("libelle_region"))
    print("minutes :", df.group_by(pl.col("ts").dt.minute().alias("mn")).agg(pl.len(), pl.col("consommation").count()).sort("mn").to_dicts())
    for col in ("eolien", "pompage", "stockage_batterie"):
        if df.schema[col] == pl.Utf8:
            df = df.with_columns(pl.col(col).cast(pl.Float64, strict=False))
    reg = df.filter(pl.col("consommation").is_not_null()).group_by("ts").agg(pl.col("consommation").sum().alias("somme_reg"), pl.len().alias("n"))
    nat = _load_nat().filter(pl.col("consommation").is_not_null()).select("ts_utc", "consommation")
    j = reg.join(nat, left_on="ts", right_on="ts_utc", how="inner")
    j = j.with_columns((pl.col("consommation") - pl.col("somme_reg")).alias("ecart"))
    print("Pas de temps communs :", j.height, "| régions par pas (min/max) :", j["n"].min(), j["n"].max())
    print(f"national − Σ régions : moyenne {j['ecart'].mean():.1f} MW, |max| {j['ecart'].abs().max():.0f} MW")
    print(f"Σ régions 2024 : {j['somme_reg'].sum() * 0.5 / 1e6:.2f} TWh ; national même pas : {j['consommation'].sum() * 0.5 / 1e6:.2f} TWh")
    print("Nulls (lignes conso non nulles) :",
          df.filter(pl.col("consommation").is_not_null()).select([pl.col(c).null_count().alias(c) for c in
                                                                  ("nucleaire", "eolien", "solaire", "hydraulique", "pompage", "ech_physiques", "stockage_batterie")]).to_dicts()[0])


def _ec_price(year: int) -> pl.DataFrame:
    d = json.loads((RAW / f"ec_price_FR_{year}.json").read_text())
    return pl.DataFrame({"ts": d["unix_seconds"], "prix": d["price"]}).with_columns(
        pl.from_epoch("ts", time_unit="s").dt.replace_time_zone("UTC").alias("ts"))


def analyse_prix() -> None:
    print("\n=== Prix day-ahead FR (energy-charts / SMARD) ===")
    for y in (2023, 2024, 2025):
        p = _ec_price(y).sort("ts")
        p = p.with_columns(pl.col("ts").diff().dt.total_minutes().alias("pas_min"))
        pas = p.group_by("pas_min").agg(pl.len(), pl.col("ts").min().alias("debut"), pl.col("ts").max().alias("fin")).sort("pas_min")
        # Heure (UTC) : moyenne simple des valeurs de l'heure (1 valeur horaire ou 4 quarts d'heure)
        h = p.group_by(pl.col("ts").dt.truncate("1h").alias("h")).agg(pl.col("prix").mean(), pl.len().alias("n"),
                                                                       (pl.col("prix") < 0).sum().alias("qh_neg"))
        loc = h.with_columns(pl.col("h").dt.convert_time_zone("Europe/Paris").dt.year().alias("an"))
        loc = loc.filter(pl.col("an") == y)
        n_h_neg = loc.filter(pl.col("prix") < 0).height
        n_h_le0 = loc.filter(pl.col("prix") <= 0).height
        qh = p.filter(pl.col("pas_min") == 15) if y == 2025 else None
        print(f"{y} : {p.height} valeurs, nulls={p['prix'].null_count()}, heures={loc.height}, "
              f"heures prix<0 = {n_h_neg}, heures prix≤0 = {n_h_le0}, min={p['prix'].min()}, max={p['prix'].max()}, "
              f"moyenne horaire = {loc['prix'].mean():.2f} €/MWh")
        print("  pas observés :", pas.to_dicts())
        if y == 2025:
            q = p.filter(pl.col("ts") >= datetime(2025, 9, 30, 22, tzinfo=timezone.utc))
            heures_avant = loc.filter(pl.col("h") < datetime(2025, 9, 30, 22, tzinfo=timezone.utc))
            heures_apres = loc.filter(pl.col("h") >= datetime(2025, 9, 30, 22, tzinfo=timezone.utc))
            print(f"  premier quart d'heure : {q['ts'].min()} | heures<0 avant oct. {heures_avant.filter(pl.col('prix') < 0).height}, "
                  f"après {heures_apres.filter(pl.col('prix') < 0).height} | quarts d'heure<0 après : {(q['prix'] < 0).sum()} "
                  f"(soit {(q['prix'] < 0).sum() / 4:.1f} h-équivalent) | heures avec ≥1 QH<0 après : {heures_apres.filter(pl.col('qh_neg') > 0).height}")
    for k in ("neg_h_2023_BE2024", "neg_h_2024_BE2024", "neg_h_2024_BE2025", "neg_h_2025_BE2025"):
        print(f"  référence {k} = {REF[k]}")


def analyse_energy_charts_fr() -> None:
    print("\n=== energy-charts public_power FR 2024 vs éCO2mix ===")
    d = json.loads((RAW / "ec_public_power_fr_2024.json").read_text())
    ts = d["unix_seconds"]
    pas = sorted({b - a for a, b in zip(ts, ts[1:])})
    print("pas (s) :", pas, "| n =", len(ts))
    tot = {pt["name"]: sum(x for x in pt["data"] if x is not None) / 1e6 for pt in d["production_types"]}
    nulls = {pt["name"]: sum(x is None for x in pt["data"]) for pt in d["production_types"]}
    for k in ("Load", "Nuclear", "Solar", "Wind onshore", "Wind offshore", "Fossil gas", "Cross border electricity trading",
              "Hydro pumped storage consumption"):
        print(f"  {k}: {tot.get(k, float('nan')):.2f} TWh (pas horaire supposé, nulls={nulls.get(k)})")
    nat = _load_nat().filter((pl.col("annee_locale") == 2024) & pl.col("consommation").is_not_null())
    print(f"  éCO2mix 2024 : conso {nat['consommation'].sum() * 0.5 / 1e6:.2f} TWh, nucléaire {nat['nucleaire'].sum() * 0.5 / 1e6:.2f}, "
          f"solaire {nat['solaire'].sum() * 0.5 / 1e6:.2f}, éolien {nat['eolien'].sum() * 0.5 / 1e6:.2f}")


def analyse_voisins() -> None:
    print("\n=== energy-charts voisins (1 jour) + flux FR ===")
    for c in ("de", "be", "es", "it", "ch", "uk"):
        d = json.loads((RAW / f"ec_public_power_{c}_20240601.json").read_text())
        ts = d["unix_seconds"]
        load = next((p["data"] for p in d["production_types"] if p["name"] == "Load"), [])
        load = [x for x in load if x is not None]
        print(f"  {c}: pas {ts[1] - ts[0]} s, {len(d['production_types'])} séries, "
              f"Load moyen {sum(load) / max(len(load), 1):.0f} MW, séries = {[p['name'] for p in d['production_types']][:6]}…")
    for ep in ("cbet", "cbpf"):
        d = json.loads((RAW / f"ec_{ep}_FR_2024w.json").read_text())
        print(f"  {ep}: pas {d['unix_seconds'][1] - d['unix_seconds'][0]} s, pays = {[c['name'] for c in d['countries']]} (unité GW)")
    g = json.loads((RAW / "elexon_fuelhh_20240601.json").read_text())["data"]
    print("  Elexon FUELHH : ", len(g), "lignes, filières =", sorted({r["fuelType"] for r in g}))


def analyse_registre() -> None:
    print("\n=== Registre national (agrégé) ===")
    for f in ("registre_agrege_20260930.parquet", "registre_agrege_311224.parquet"):
        r = pl.read_parquet(RAW / f)
        print(f"-- {f} : {r.height} lignes, Σ nbinstallations = {r['nbinstallations'].sum()}")
        dom = {"01", "02", "03", "04", "06"}
        r = r.with_columns(pl.col("coderegion").is_in(list(dom)).alias("zni_dom"),
                           (pl.col("coderegion") == "94").alias("corse"))
        print(r.group_by("zni_dom").agg(pl.len(), (pl.col("puismaxinstallee").sum() / 1e6).alias("GW")))
        met = r.filter(~pl.col("zni_dom") & ~pl.col("corse"))
        print("Métropole continentale, GW par filière :")
        print(met.group_by("filiere").agg(pl.len().alias("lignes"), pl.col("nbinstallations").sum().alias("install"),
                                          (pl.col("puismaxinstallee").sum() / 1e6).round(2).alias("GW")).sort("GW", descending=True))
        print("Taux de remplissage (métropole) :", met.select(
            [(pl.col(c).is_not_null().mean() * 100).round(1).alias(c) for c in
             ("codeinseecommune", "postesource", "codes3renr", "datemiseenservice", "tensionraccordement",
              "energieannuelleglissanteinjectee", "regime")]).to_dicts()[0])
        agg = met.filter(pl.col("regime").is_null())
        print(f"Lignes agrégées (regime nul) : {agg.height} lignes, {agg['nbinstallations'].sum()} installations, "
              f"{agg['puismaxinstallee'].sum() / 1e6:.2f} GW ; exemple de nom : {agg['nominstallation'].head(3).to_list()}")


def analyse_autres_odre() -> None:
    print("\n=== Autres jeux ODRÉ ===")
    n = pl.read_parquet(RAW / "nucleaire_horaire.parquet")
    n = n.with_columns(pl.col("horodate").dt.convert_time_zone("Europe/Paris").dt.year().alias("an"))
    print("nucléaire horaire (GWh) :", n.group_by("an").agg(pl.len(), (pl.col("production_nette").sum() / 1e3).round(2).alias("TWh"))
          .filter(pl.col("an") >= 2022).sort("an").to_dicts())
    # Convention d'horodatage éCO2mix (non documentée) : on compare le nucléaire éCO2mix
    # agrégé à l'heure selon deux hypothèses avec la série horaire ODRÉ (« convention débutante »).
    nat = _load_nat().filter(pl.col("consommation").is_not_null() & (pl.col("annee_locale") == 2024))
    nn = n.with_columns(pl.col("horodate").dt.convert_time_zone("UTC").alias("h"), (pl.col("production_nette") * 1e3).alias("nuc_odre_MW"))
    for nom, decal in (("débutante (h:00 + h:30)", 0), ("finissante (h-1:30 + h:00)", 30)):
        e = (nat.with_columns((pl.col("ts_utc") - pl.duration(minutes=decal)).dt.truncate("1h").alias("h"))
                .group_by("h").agg(pl.col("nucleaire").mean().alias("nuc_eco_MW"), pl.len().alias("k")).filter(pl.col("k") == 2))
        j = e.join(nn, on="h", how="inner")
        d = (j["nuc_eco_MW"] - j["nuc_odre_MW"]).abs()
        print(f"  hypothèse {nom} : |écart| moyen {d.mean():.1f} MW, max {d.max():.0f} MW sur {j.height} h")
    g = pl.read_parquet(RAW / "ges_conso_horaire.parquet")
    g = g.with_columns(pl.col("date_heure_utc").dt.convert_time_zone("UTC").alias("ts"))
    ete = g.filter(pl.col("date_cet").cast(pl.Utf8) == "2024-07-01").sort("ts").head(2)
    print("GES conso : exemple 1er juillet 2024 (heure_cet vs UTC) :", ete.select("date_cet", "heure_cet", "ts").to_dicts())
    nat = _load_nat().filter(pl.col("consommation").is_not_null())
    natc = nat.with_columns(pl.col("ts_utc").dt.truncate("1h").alias("h")).group_by("h").agg(pl.col("consommation").mean())
    j = g.join(natc, left_on="ts", right_on="h", how="inner").with_columns(
        pl.col("ts").dt.convert_time_zone("Europe/Paris").dt.year().alias("an"))
    print("GES conso par an (moyenne simple / pondérée conso) :", j.group_by("an").agg(
        pl.len(), pl.col("intensite_emissions_conso").mean().round(2).alias("simple"),
        ((pl.col("intensite_emissions_conso") * pl.col("consommation")).sum() / pl.col("consommation").sum()).round(2).alias("pondere"))
        .sort("an").to_dicts())
    e = pl.read_parquet(RAW / "echanges_commerciaux_2024.parquet")
    print("échanges commerciaux 2024 : lignes", e.height, "| positions max par jour :",
          e.group_by("date").agg(pl.col("position").max()).group_by("position").agg(pl.len()).to_dicts())
    print("  lignes par (date, position) :", e.group_by("date", "position").agg(pl.len().alias("k")).group_by("k").agg(pl.len().alias("n")).to_dicts(),
          "| nulls export_france/import_france :", e["export_france"].null_count(), e["import_france"].null_count())
    c = pl.read_parquet(RAW / "consommation_annuelle_brute.parquet").sort("annee", descending=True).head(4)
    print("conso annuelle brute ODRÉ :", c.select("annee", "consommation_brute_electricite_rte", "statut_rte").to_dicts())


def analyse() -> None:
    with pl.Config(tbl_rows=40, tbl_cols=20, tbl_width_chars=200):
        analyse_eco2mix_national()
        analyse_eco2mix_tr()
        analyse_eco2mix_regional()
        analyse_prix()
        analyse_energy_charts_fr()
        analyse_voisins()
        analyse_registre()
        analyse_autres_odre()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "analyse"
    {"download": download, "analyse": analyse}[cmd]()
