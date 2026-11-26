"""Spike carbone, annexe (jetable). Usage, depuis pipeline/ : uv run python explo/spike_carbone_saisons.py"""
import sys; sys.path.insert(0, "explo")
import polars as pl
import spike_carbone as sc
d = sc.joindre().with_columns((pl.col("jsem") >= 6).alias("we"), (pl.col("eolien") + pl.col("solaire")).alias("vre"),
    (-pl.col("ech_physiques")).alias("exports"),
    pl.when(pl.col("mois").is_in([12,1,2])).then(pl.lit("hiver")).when(pl.col("mois").is_in([3,4,5])).then(pl.lit("printemps"))
      .when(pl.col("mois").is_in([6,7,8])).then(pl.lit("été")).otherwise(pl.lit("automne")).alias("saison"))
ys = ["nucleaire", "hydraulique", "gaz", "charbon", "fioul", "exports", "pompage", "emis_fr_t"]
for per, a0, a1 in [("2019-2021", 2019, 2021), ("2023-2025", 2023, 2025), ("2024-2025", 2024, 2025)]:
    tot = {k: 0.0 for k in ys}
    for s in ["hiver", "printemps", "été", "automne"]:
        g = d.filter(pl.col("an").is_between(a0, a1) & (pl.col("saison") == s))
        r = sc.within(g, ys, ["consommation", "vre"], ["an", "mois", "h", "we"])
        print(per, f"{s:9s}", "  ".join(f"{k}={b[0]:+.3f}±{1.96*se[0]:.3f}" for k, (b, se, n) in r.items()))
        for k in ys: tot[k] += r[k][0][0] / 4
    print(per, "moyenne des 4 saisons (≈ charge plate) :", "  ".join(f"{k}={v:+.3f}" for k, v in tot.items()))
