"""Spike carbone, annexe (jetable). Usage, depuis pipeline/ : uv run python explo/spike_carbone_regimes_croises.py"""
import sys; sys.path.insert(0, "explo")
import polars as pl
import spike_carbone as sc
pl.Config.set_tbl_cols(30); pl.Config.set_tbl_width_chars(250)
d = sc.joindre()
eps = 0.01
v = list(sc.VOISINS_PRIX.values())
x = d.filter(pl.col("prix_fr").is_not_null() & pl.all_horizontal([pl.col(c).is_not_null() for c in v])).with_columns(
    (pl.col("prix_fr") < pl.min_horizontal(v) - eps).alias("basse"),
    (pl.col("prix_fr") > pl.max_horizontal(v) + eps).alias("haute"),
    pl.any_horizontal([(pl.col("prix_fr") - pl.col(c)).abs() < eps for c in v]).alias("couplee"),
    (pl.col("nucleaire_disponible") - pl.col("nucleaire")).alias("J"),
    (pl.sum_horizontal(["fioul","charbon","gaz","nucleaire","eolien","solaire","hydraulique","bioenergies"])).alias("P"),
)
a = x.filter(pl.col("an").is_between(2019, 2025)).group_by("an").agg(
    (pl.col("basse").mean()*100).round(1).alias("%basse"),
    (pl.col("couplee").mean()*100).round(1).alias("%couplée"),
    (pl.col("haute").mean()*100).round(1).alias("%haute"),
    ((~pl.col("basse") & ~pl.col("couplee") & ~pl.col("haute")).mean()*100).round(1).alias("%entre"),
    ((pl.col("basse") & (pl.col("J") > 1000)).mean()*100).round(1).alias("%basse&J>1GW"),
    ((pl.col("J") > 1000).mean()*100).round(1).alias("%J>1GW"),
    ((pl.col("prix_fr") <= 0).mean()*100).round(1).alias("%p<=0"),
    (pl.col("taux_co2")*pl.col("P")).filter(pl.col("basse")).sum().truediv(pl.col("P").filter(pl.col("basse")).sum()).round(1).alias("gCO2_moy|basse"),
    (pl.col("taux_co2")*pl.col("P")).filter(pl.col("couplee")).sum().truediv(pl.col("P").filter(pl.col("couplee")).sum()).round(1).alias("gCO2_moy|couplée"),
    (pl.col("taux_co2")*pl.col("P")).sum().truediv(pl.col("P").sum()).round(1).alias("gCO2_moy"),
    pl.col("taux_co2").max().alias("gCO2_max"),
    (pl.col("gaz")+pl.col("charbon")+pl.col("fioul")).filter(pl.col("basse")).mean().round(0).alias("fossileFR_MW|basse"),
    (pl.col("gaz_ccg")).filter(pl.col("basse")).mean().round(0).alias("CCG_MW|basse"),
    (pl.col("gaz_ccg")).mean().round(0).alias("CCG_MW"),
).sort("an")
print(a)
