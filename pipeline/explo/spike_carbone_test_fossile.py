"""Spike carbone, annexe (jetable). Usage, depuis pipeline/ : uv run python explo/spike_carbone_test_fossile.py"""
import sys; sys.path.insert(0, "explo")
import polars as pl
import spike_carbone as sc
d = sc.joindre().join(sc.perte_fortuite(), on="heure_utc", how="left")
fos = ["b02","b03","b04","b05","b06"]
cols = [f"production_{p}_{c}" for p in sc.PAYS_ZONE for c in fos if f"production_{p}_{c}" in d.columns]
allc = [c for c in d.columns if c.startswith("production_") and c.split("_")[1] in sc.PAYS_ZONE]
d = d.with_columns(pl.sum_horizontal([pl.col(c).fill_null(0) for c in cols]).alias("G_fos_vois"),
                   pl.sum_horizontal([pl.col(c).fill_null(0) for c in allc]).alias("G_vois"))
j = sc.preparer_jour(d, 0, "jour").join(d.group_by("jour").agg(pl.col("perte_fortuite").mean(), pl.col("G_fos_vois").mean(), pl.col("G_vois").mean(), pl.col("prix_fr").mean(), pl.col("prix_de").mean()), on="jour")
X = ["perte_fortuite", "consommation", "vre_vois", "vre_fr"]
for periode, a0, a1 in sc.PERIODES + [("2016-2025", 2016, 2025)]:
    g = j.filter(pl.col("an").is_between(a0, a1))
    r = sc.within(g, ["G_fos_vois", "G_vois", "exports", "E_vois", "prix_fr", "prix_de"], X, ["an", "mois", "jsem"])
    print(periode, "  ".join(f"{k}={b[0]:+.3f}±{1.96*se[0]:.3f}" for k, (b, se, n) in r.items()))
# placebo : effet des arrêts fortuits de demain / d'il y a 30 jours
j = j.sort("jour").with_columns(pl.col("perte_fortuite").shift(-30).alias("pf_futur30"))
for periode, a0, a1 in [("2016-2025", 2016, 2025), ("2016-2021", 2016, 2021)]:
    g = j.filter(pl.col("an").is_between(a0, a1))
    r = sc.within(g, ["E_vois", "exports"], ["pf_futur30", "consommation", "vre_vois", "vre_fr"], ["an", "mois", "jsem"])
    print("placebo J+30", periode, "  ".join(f"{k}={b[0]:+.3f}±{1.96*se[0]:.3f}" for k, (b, se, n) in r.items()))
