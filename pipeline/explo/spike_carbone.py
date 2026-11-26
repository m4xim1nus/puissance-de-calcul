"""Spike carbone (jetable) : régimes d'échange et de prix, réponse du système à une
consommation française, émissions de la zone couplée partielle.

Lit data/export/systeme_horaire.parquet (éCO2mix + REMIT EDF, heure UTC) et
data/derive/entsoe/horaire.parquet (ENTSO-E, heure UTC, non versionné).
Écrit seulement sur la sortie standard. Usage, depuis pipeline/ :
    uv run python explo/spike_carbone.py [regimes|reponse_fr|zone|instrument|decalage|tout]

Facteurs d'émission par filière : voir FACTEURS ci-dessous (émissions directes,
gCO2eq/kWh électrique). Ils viennent du rapport docs/spike/carbone.md, § 2.2 ;
les variantes « bas » et « haut » donnent la fourchette.
"""
import sys
from pathlib import Path

import numpy as np
import polars as pl

RACINE = Path(__file__).resolve().parents[2]
SYS = RACINE / "data/export/systeme_horaire.parquet"
ENT = RACINE / "data/derive/entsoe/horaire.parquet"

VOISINS_PRIX = {"be": "prix_be", "de": "prix_de", "es": "prix_es", "it_nord": "prix_it_nord", "ch": "prix_ch"}
PAYS_ZONE = ["be", "de", "es", "it", "ch"]  # voisins dont la production A75 est exploitable

# Facteurs d'émission directs (combustion), gCO2eq/kWh électrique, par code ENTSO-E :
# (central, bas, haut). Central = RTE, Bilan électrique 2025, annexe p. 145 (identique au
# BE2024, chapitre Émissions, p. 12), facteurs du parc FRANÇAIS. Bas / haut = autres sources
# primaires (GIEC AR5 annexe III tab. A.III.2 ; ADEME Base Carbone ; UBA Climate Change
# 16/2026 tab. 4 ; GIEC 2006 vol. 2 tab. 2.2). Détail : docs/spike/carbone.md, § 2.2.
# Biomasse : 0 partout (convention des émissions directes : CO2 biogénique non compté).
FACTEURS = {
    #        central, bas, haut
    "b01": (0, 0, 0),         # biomasse : convention biogénique (RTE 0)
    "b02": (961, 961, 1119),  # lignite : RTE 961 ; UBA 2025 1 119
    "b03": (855, 160, 936),   # gaz de houille : RTE « autres fossiles » ; GIEC 2006 cokerie / haut-fourneau (à 100 %, CALCUL)
    "b04": (435, 331, 497),   # gaz : RTE « indéterminé » 435 ; CCG 331 ; TAC 497
    "b05": (855, 760, 969),   # houille : RTE 855 ; AR5 médiane PC 760 ; ADEME combustion 969
    "b06": (769, 628, 769),   # fioul : RTE 769 ; ADEME combustion 628
    "b09": (0, 0, 0),         # géothermie
    "b17": (494, 0, 988),     # déchets : RTE 988 sur la part non renouvelable ; part fossile inconnue (50 % en central, HYPOTHÈSE)
    "b20": (435, 0, 855),     # autres : contenu inconnu (HYPOTHÈSE : gaz en central ; RTE « autres fossiles » en haut)
}


def charger_systeme() -> pl.DataFrame:
    s = pl.read_parquet(SYS)
    prod = ["fioul", "charbon", "gaz", "nucleaire", "eolien", "solaire", "hydraulique", "bioenergies"]
    return s.with_columns(
        pl.sum_horizontal(prod).alias("production_fr"),
        (pl.col("taux_co2") * pl.sum_horizontal(prod) / 1000).alias("emis_fr_t"),  # t/h
        (pl.col("consommation") - pl.col("eolien") - pl.col("solaire")).alias("charge_nette_fr"),
    )


def charger_entsoe() -> pl.DataFrame:
    e = pl.read_parquet(ENT)
    return e.with_columns(pl.coalesce("prix_de_lu", "prix_de_at_lu").alias("prix_de"))


def emissions_pays(e: pl.DataFrame, p: str, variante: int = 0) -> pl.Expr:
    termes = []
    for code, vals in FACTEURS.items():
        col = f"production_{p}_{code}"
        if col in e.columns and vals[variante] > 0:
            termes.append(pl.col(col).fill_null(0) * vals[variante] / 1000)  # t/h
    return pl.sum_horizontal(termes) if termes else pl.lit(0.0)


def joindre() -> pl.DataFrame:
    s = charger_systeme()
    e = charger_entsoe()
    d = s.join(e, on="heure_utc", how="inner")
    paris = pl.col("heure_utc").dt.convert_time_zone("Europe/Paris")
    return d.with_columns(
        paris.dt.year().alias("an"), paris.dt.month().alias("mois"), paris.dt.hour().alias("h"),
        paris.dt.date().alias("jour"), paris.dt.weekday().alias("jsem"),
    )


# ---------------------------------------------------------------- (a) régimes
def regimes(d: pl.DataFrame) -> None:
    """Part des heures où la France exporte, convergence des prix avec chaque voisin,
    France découplée vers le bas ou vers le haut, prix moyen par régime."""
    eps = 0.01
    voisins = list(VOISINS_PRIX.values())
    x = d.filter(pl.col("prix_fr").is_not_null() & pl.all_horizontal([pl.col(c).is_not_null() for c in voisins]))
    conv = {k: ((pl.col("prix_fr") - pl.col(c)).abs() < eps) for k, c in VOISINS_PRIX.items()}
    x = x.with_columns(
        [v.alias(f"conv_{k}") for k, v in conv.items()]
        + [pl.min_horizontal(voisins).alias("pmin_v"), pl.max_horizontal(voisins).alias("pmax_v")]
    ).with_columns(
        pl.any_horizontal([pl.col(f"conv_{k}") for k in VOISINS_PRIX]).alias("conv_un"),
        (pl.col("prix_fr") < pl.col("pmin_v") - eps).alias("fr_basse_isolee"),
        (pl.col("prix_fr") > pl.col("pmax_v") + eps).alias("fr_haute_isolee"),
        (pl.col("ech_physiques") < 0).alias("export"),
    )
    a = x.group_by("an").agg(
        pl.len().alias("heures"),
        (pl.col("export").mean() * 100).round(1).alias("%export"),
        *[(pl.col(f"conv_{k}").mean() * 100).round(1).alias(f"%=={k}") for k in VOISINS_PRIX],
        (pl.col("conv_un").mean() * 100).round(1).alias("%==1voisin"),
        (pl.col("fr_basse_isolee").mean() * 100).round(1).alias("%FR<tous"),
        (pl.col("fr_haute_isolee").mean() * 100).round(1).alias("%FR>tous"),
        pl.col("prix_fr").filter(pl.col("fr_basse_isolee")).mean().round(1).alias("p_FR<tous"),
        pl.col("prix_fr").filter(pl.col("conv_de")).mean().round(1).alias("p_==de"),
        (-pl.col("ech_physiques").filter(pl.col("fr_basse_isolee")).mean() / 1000).round(1).alias("exp_GW_FR<tous"),
    ).sort("an")
    print("\n## (a) Régimes de prix et d'échanges (heures où les 6 prix existent)\n")
    print(a)
    # exportatrice ET découplée vers le bas : l'unité marginale est en France
    b = x.filter(pl.col("export")).group_by("an").agg(
        pl.len().alias("h_export"),
        (pl.col("fr_basse_isolee").mean() * 100).round(1).alias("%FR<tous|export"),
        (pl.col("conv_un").mean() * 100).round(1).alias("%couplée|export"),
        (pl.col("conv_de").mean() * 100).round(1).alias("%==de|export"),
        ((pl.col("prix_fr") <= 0).mean() * 100).round(1).alias("%p<=0|export"),
    ).sort("an")
    print("\nSachant que la France exporte (solde physique éCO2mix < 0) :\n")
    print(b)
    return x


# ------------------------------------------------- (b) qui sert la charge FR
def within(df: pl.DataFrame, y: list[str], x: list[str], fe: list[str]) -> dict:
    """MCO avec effets fixes (démoyennage par groupe), erreurs-types groupées par jour."""
    cols = y + x
    g = df.select(cols + fe + ["jour"]).drop_nulls()
    dm = g.with_columns([(pl.col(c) - pl.col(c).mean().over(fe)) for c in cols])
    X = dm.select(x).to_numpy()
    out = {}
    XtX_inv = np.linalg.inv(X.T @ X)
    jours = dm["jour"].to_numpy()
    _, idx = np.unique(jours, return_inverse=True)
    for c in y:
        Y = dm[c].to_numpy()
        b = XtX_inv @ X.T @ Y
        r = Y - X @ b
        # erreurs-types groupées (jour)
        S = np.zeros((X.shape[1], X.shape[1]))
        sc = np.zeros((idx.max() + 1, X.shape[1]))
        np.add.at(sc, idx, X * r[:, None])
        S = sc.T @ sc
        V = XtX_inv @ S @ XtX_inv
        out[c] = (b, np.sqrt(np.diag(V)), len(Y))
    return out


def reponse_fr(d: pl.DataFrame) -> None:
    """Pour 1 MW de consommation française en plus (variation résiduelle après effets
    fixes année×mois×heure et jour de semaine), quelle part vient de chaque filière
    française et du solde des échanges ? Données éCO2mix seules."""
    print("\n## (b) Qui sert une variation de la consommation française (éCO2mix)\n")
    print("Régression intra-groupe : Y = β·consommation + γ·(éolien+solaire) + effets fixes ;")
    print("groupes = année × mois × heure × (ouvré/week-end). Erreurs-types groupées par jour.\n")
    d = d.with_columns((pl.col("jsem") >= 6).alias("we"), (pl.col("eolien") + pl.col("solaire")).alias("vre"),
                       (-pl.col("ech_physiques")).alias("exports"), pl.col("gaz").alias("gaz_tot"))
    ys = ["nucleaire", "hydraulique", "gaz_tot", "charbon", "fioul", "bioenergies", "pompage", "exports", "emis_fr_t"]
    for periode, f in [("2015-2019", pl.col("an").is_between(2015, 2019)), ("2020-2022", pl.col("an").is_between(2020, 2022)),
                       ("2023-2025", pl.col("an").is_between(2023, 2025))]:
        r = within(d.filter(f), ys, ["consommation", "vre"], ["an", "mois", "h", "we"])
        ligne = []
        for c in ys:
            b, se, n = r[c]
            u = "t/MWh" if c == "emis_fr_t" else ""
            ligne.append(f"{c}={b[0]:+.3f}±{1.96*se[0]:.3f}{u}")
        print(periode, f"(n={n})"); print("   " + "  ".join(ligne))
    print("\nLecture : β(exports) négatif = la consommation ajoutée réduit les exportations ;")
    print("pompage est compté positivement (consommation des STEP) dans éCO2mix.")


# ----------------------------------------- (c) émissions de la zone couplée
def zone(d: pl.DataFrame) -> None:
    """Hawkes (2010) appliqué à la zone FR+BE+DE+ES+IT+CH : ΔE sur Δ(production − éolien
    − solaire), heure par heure, par année, et selon le régime de prix FR."""
    print("\n## (c) Régression des émissions de la zone couplée partielle (FR, BE, DE, ES, IT, CH)\n")
    for var, nom in [(0, "central"), (1, "bas"), (2, "haut")]:
        exprs = [emissions_pays(d, p, var).alias(f"E_{p}") for p in PAYS_ZONE]
        x = d.with_columns(exprs)
        prodcols = [c for c in d.columns if c.startswith("production_") and any(c.startswith(f"production_{p}_") for p in PAYS_ZONE)]
        vre = [c for c in prodcols if c.split("_")[-1] in ("b16", "b18", "b19")]
        x = x.with_columns(
            (pl.sum_horizontal([pl.col(f"E_{p}") for p in PAYS_ZONE]) + pl.col("emis_fr_t")).alias("E"),
            (pl.sum_horizontal([pl.col(c).fill_null(0) for c in prodcols]) - pl.sum_horizontal([pl.col(c).fill_null(0) for c in vre])
             + pl.col("production_fr") - pl.col("eolien") - pl.col("solaire")).alias("G_nette"),
            (pl.sum_horizontal([pl.col(c).fill_null(0) for c in prodcols]) + pl.col("production_fr")).alias("G"),
        ).sort("heure_utc").with_columns(
            pl.col("E").diff().alias("dE"), pl.col("G_nette").diff().alias("dG"),
            (pl.col("heure_utc").diff().dt.total_hours() == 1).alias("consec"),
        ).filter(pl.col("consec") & pl.col("an").is_between(2019, 2024))
        res = []
        for an in range(2019, 2025):
            g = x.filter(pl.col("an") == an).drop_nulls(["dE", "dG"])
            b, _ = np.polyfit(g["dG"].to_numpy(), g["dE"].to_numpy(), 1)
            moy = g["E"].sum() / g["G"].sum()
            res.append((an, round(b, 3), round(moy, 3)))
        print(f"variante {nom} : (année, marginal ΔE/ΔG_nette t/MWh, moyen E/G t/MWh)", res)
    print("\nPente globale, à facteurs centraux, par régime de prix FR (2019-2024) : voir regimes_zone()")


def regimes_zone(d: pl.DataFrame) -> None:
    eps = 0.01
    exprs = [emissions_pays(d, p, 0).alias(f"E_{p}") for p in PAYS_ZONE]
    prodcols = [c for c in d.columns if c.startswith("production_") and any(c.startswith(f"production_{p}_") for p in PAYS_ZONE)]
    vre = [c for c in prodcols if c.split("_")[-1] in ("b16", "b18", "b19")]
    voisins = list(VOISINS_PRIX.values())
    x = d.with_columns(exprs).with_columns(
        (pl.sum_horizontal([pl.col(f"E_{p}") for p in PAYS_ZONE]) + pl.col("emis_fr_t")).alias("E"),
        (pl.sum_horizontal([pl.col(c).fill_null(0) for c in prodcols]) - pl.sum_horizontal([pl.col(c).fill_null(0) for c in vre])
         + pl.col("production_fr") - pl.col("eolien") - pl.col("solaire")).alias("G_nette"),
        (pl.col("prix_fr") < pl.min_horizontal(voisins) - eps).alias("fr_basse"),
        ((pl.col("prix_fr") - pl.col("prix_de")).abs() < eps).alias("conv_de"),
    ).sort("heure_utc").with_columns(
        pl.col("E").diff().alias("dE"), pl.col("G_nette").diff().alias("dG"),
        (pl.col("heure_utc").diff().dt.total_hours() == 1).alias("consec"),
        pl.col("fr_basse").shift(1).alias("fr_basse_prec"), pl.col("conv_de").shift(1).alias("conv_de_prec"),
    ).filter(pl.col("consec") & pl.col("an").is_between(2019, 2024)).drop_nulls(["dE", "dG"])
    print("\n## (c bis) Pente ΔE/ΔG_nette de la zone selon le régime FR (deux heures consécutives dans le régime)\n")
    for nom, f in [("FR découplée vers le bas", pl.col("fr_basse") & pl.col("fr_basse_prec")),
                   ("FR = DE", pl.col("conv_de") & pl.col("conv_de_prec")),
                   ("toutes heures", pl.lit(True))]:
        for an in range(2019, 2025):
            g = x.filter(f & (pl.col("an") == an))
            if g.height < 200:
                continue
            b, _ = np.polyfit(g["dG"].to_numpy(), g["dE"].to_numpy(), 1)
            print(f"  {nom:28s} {an} n={g.height:5d} pente={b:.3f} t/MWh")


# ------------------------------------ (d) expérience naturelle : nucléaire dispo
def preparer_jour(d: pl.DataFrame, var: int = 0, pas: str = "jour") -> pl.DataFrame:
    """Agrège au jour (ou à la semaine) : émissions par pays, solde par frontière, etc."""
    exprs = [emissions_pays(d, p, var).alias(f"E_{p}") for p in PAYS_ZONE]
    prodcols = [c for c in d.columns if c.startswith("production_") and any(c.startswith(f"production_{p}_") for p in PAYS_ZONE)]
    vre = [c for c in prodcols if c.split("_")[-1] in ("b16", "b18", "b19")]
    front = {"be": ("flux_fr_be", "flux_be_fr"), "de": ("flux_fr_de", "flux_de_fr"), "ch": ("flux_fr_ch", "flux_ch_fr"),
             "it": ("flux_fr_it", "flux_it_fr"), "es": ("flux_fr_es", "flux_es_fr"), "gb": ("flux_fr_gb", "flux_gb_fr")}
    x = d.with_columns(exprs).with_columns(
        pl.sum_horizontal([pl.col(f"E_{p}") for p in PAYS_ZONE]).alias("E_vois"),
        pl.sum_horizontal([pl.col(c).fill_null(0) for c in vre]).alias("vre_vois"),
        (pl.col("eolien") + pl.col("solaire")).alias("vre_fr"),
        (-pl.col("ech_physiques")).alias("exports"),
        *[(pl.col(a) - pl.col(b)).alias(f"exp_{k}") for k, (a, b) in front.items()],
    )
    if pas == "semaine":
        x = x.with_columns(pl.col("heure_utc").dt.convert_time_zone("Europe/Paris").dt.truncate("1w").dt.date().alias("cle"))
    else:
        x = x.with_columns(pl.col("jour").alias("cle"))
    attendu = 23 if pas == "jour" else 160
    vals = ["E_vois", "emis_fr_t", "nucleaire_disponible", "nucleaire", "hydraulique", "gaz", "consommation", "vre_vois",
            "vre_fr", "exports"] + [f"E_{p}" for p in PAYS_ZONE] + [f"exp_{k}" for k in front]
    j = x.group_by("cle").agg(pl.col("an").first(), pl.col("mois").first(), pl.col("jsem").first(),
                              *[pl.col(c).mean() for c in vals], pl.len().alias("n"))
    j = j.filter(pl.col("n") >= attendu).with_columns((pl.col("E_vois") + pl.col("emis_fr_t")).alias("E_tot"),
                                                     pl.col("cle").alias("jour"))
    return j


PERIODES = [("2016-2019", 2016, 2019), ("2019-2021", 2019, 2021), ("2022-2024", 2022, 2024),
            ("2023-2025", 2023, 2025), ("2024-2025", 2024, 2025)]


def instrument(d: pl.DataFrame) -> None:
    """Forme réduite : émissions des voisins (BE, DE, ES, IT, CH) et de la France sur le
    nucléaire français disponible (REMIT EDF), effets fixes année×mois (et jour de
    semaine au pas journalier), contrôles : consommation FR, éolien et solaire FR et
    voisins. On rapporte l'effet de −1 MW disponible, lu comme ≈ +1 MW de consommation
    plate (symétrie au premier ordre, discutée dans le rapport)."""
    print("\n## (d) Nucléaire français disponible → émissions (forme réduite)\n")
    X = ["nucleaire_disponible", "consommation", "vre_vois", "vre_fr"]
    for pas, fe in [("jour", ["an", "mois", "jsem"]), ("semaine", ["an", "mois"])]:
        for var, nom in [(0, "central"), (1, "bas"), (2, "haut")]:
            j = preparer_jour(d, var, pas)
            for periode, a0, a1 in PERIODES:
                g = j.filter(pl.col("an").is_between(a0, a1))
                r = within(g, ["E_vois", "emis_fr_t", "E_tot"], X, fe)
                txt = "  ".join(f"{k}={-b[0]:+.3f}±{1.96*se[0]:.3f}" for k, (b, se, n) in r.items())
                print(f"  [{pas}, {nom}] {periode} (n={r['E_tot'][2]}) −1 MW dispo → t/h par MW : {txt}")
        print()
    # décomposition physique (facteurs centraux, journalier)
    print("  Décomposition (journalier, facteurs centraux), effet de −1 MW disponible :")
    j = preparer_jour(d, 0, "jour")
    ys = ["nucleaire", "hydraulique", "gaz", "exports", "exp_be", "exp_de", "exp_ch", "exp_it", "exp_es", "exp_gb",
          "E_be", "E_de", "E_es", "E_it", "E_ch"]
    for periode, a0, a1 in PERIODES:
        g = j.filter(pl.col("an").is_between(a0, a1))
        r = within(g, ys, X, ["an", "mois", "jsem"])
        print(f"  {periode} : " + "  ".join(f"{k}={-b[0]:+.2f}" for k, (b, se, n) in r.items()))
    print("\n  Contrôle (biais météo attendu) : effet de +1 MW de consommation FR, même régression, journalier, central :")
    for periode, a0, a1 in PERIODES:
        g = j.filter(pl.col("an").is_between(a0, a1))
        r = within(g, ["E_vois", "emis_fr_t", "E_tot", "exports"], X, ["an", "mois", "jsem"])
        print(f"  {periode} : " + "  ".join(f"{k}={b[1]:+.3f}±{1.96*se[1]:.3f}" for k, (b, se, n) in r.items()))

# ------------------------------------------- (e) décalage horaire des voisins
def decalage(d: pl.DataFrame) -> None:
    """Heure (UTC) du maximum du profil solaire moyen par mois, par pays et par année :
    un décalage d'une heure d'un pays sur les autres trahirait un défaut d'horodatage
    (comme FR A75 en 2023-2024). Repère : solaire éCO2mix."""
    print("\n## (e) Heure UTC du pic solaire moyen (juin), par pays : test grossier d'horodatage\n")
    cols = {"fr_eco2mix": "solaire", "fr_entsoe": "production_fr_b16", "be": "production_be_b16", "de": "production_de_b16",
            "es": "production_es_b16", "it": "production_it_b16", "ch": "production_ch_b16"}
    x = d.with_columns(pl.col("heure_utc").dt.hour().alias("hu"))
    for an in range(2016, 2026):
        g = x.filter((pl.col("an") == an) & pl.col("mois").is_between(5, 7))
        ligne = []
        for k, c in cols.items():
            prof = g.group_by("hu").agg(pl.col(c).mean()).sort("hu")
            v = prof[c].to_numpy()
            if np.all(np.isnan(v.astype(float))) or np.nansum(v) == 0:
                ligne.append(f"{k}=—"); continue
            hu = prof["hu"].to_numpy()
            # barycentre du profil (plus fin que l'argmax)
            w = np.nan_to_num(v.astype(float))
            ligne.append(f"{k}={np.sum(hu * w) / np.sum(w):.2f}")
        print(an, "  ".join(ligne))


def moyen(d: pl.DataFrame) -> None:
    """Intensité moyenne de la production par pays et par an, à facteurs centraux, pour
    recoupement avec les intensités officielles (AEE, UBA, etc.)."""
    print("\n## Intensité moyenne de la production par pays (facteurs centraux, directes), gCO2eq/kWh\n")
    out = []
    for p in PAYS_ZONE:
        prodcols = [c for c in d.columns if c.startswith(f"production_{p}_")]
        x = d.with_columns(emissions_pays(d, p, 0).alias("E"), pl.sum_horizontal([pl.col(c).fill_null(0) for c in prodcols]).alias("G"))
        a = x.group_by("an").agg((pl.col("E").sum() / pl.col("G").sum() * 1000).round(0).alias(p), (pl.col("G").sum() / 1e6).round(0).alias(f"TWh_{p}"))
        out.append(a)
    fr = d.group_by("an").agg((pl.col("emis_fr_t").sum() / pl.col("production_fr").sum() * 1000).round(1).alias("fr_eco2mix"))
    r = out[0]
    for a in out[1:] + [fr]:
        r = r.join(a, on="an")
    print(r.sort("an"))


# ------------------------------- (d bis) instrument : arrêts fortuits seulement
def perte_fortuite() -> pl.DataFrame:
    """Puissance nucléaire perdue du fait des seuls événements « Fortuite » (REMIT EDF), MW
    moyens par heure UTC. Les arrêts « Planifiée » comprennent des arrêts pour modulation
    (décision économique, donc endogène au prix) : on les écarte de l'instrument."""
    from datetime import datetime, timezone
    from pc import remit
    _, ev, bornes = remit.depuis_raw(RACINE / "data/raw")
    debut = datetime(2015, 1, 1, tzinfo=timezone.utc)
    fin = bornes["horizon"]
    tout = remit.national(remit.disponible_horaire(ev, debut, fin))
    fort = remit.national(remit.disponible_horaire(ev.filter(pl.col("type") == "Fortuite"), debut, fin))
    return (fort.select("heure_utc", pl.col("nucleaire_pmax").alias("pmax_f"), pl.col("nucleaire_disponible").alias("dispo_f"))
                .with_columns((pl.col("pmax_f") - pl.col("dispo_f")).alias("perte_fortuite"))
                .select("heure_utc", "perte_fortuite"))


def instrument_fortuit(d: pl.DataFrame) -> None:
    print("\n## (d bis) Arrêts fortuits du nucléaire → émissions (forme réduite, journalier)\n")
    pf = perte_fortuite()
    d = d.join(pf, on="heure_utc", how="left")
    stats = d.group_by("an").agg((pl.col("perte_fortuite").mean() / 1000).round(2).alias("GW_moy"),
                                 (pl.col("perte_fortuite").std() / 1000).round(2).alias("GW_sd")).sort("an")
    print("Perte fortuite (GW) :", stats.rows())
    X = ["perte_fortuite", "consommation", "vre_vois", "vre_fr"]
    for var, nom in [(0, "central"), (1, "bas"), (2, "haut")]:
        j = preparer_jour(d, var, "jour")
        pfj = d.group_by("jour").agg(pl.col("perte_fortuite").mean())
        j = j.join(pfj, on="jour")
        for periode, a0, a1 in PERIODES + [("2016-2025", 2016, 2025)]:
            g = j.filter(pl.col("an").is_between(a0, a1))
            ys = ["E_vois", "emis_fr_t", "E_tot"] + (["nucleaire", "exports", "gaz", "hydraulique", "exp_gb", "E_de", "E_it", "E_es", "E_be"] if var == 0 else [])
            r = within(g, ys, X, ["an", "mois", "jsem"])
            txt = "  ".join(f"{k}={b[0]:+.3f}±{1.96*se[0]:.3f}" for k, (b, se, n) in r.items())
            print(f"  [{nom}] {periode} (n={r['E_tot'][2]} j) +1 MW perdu par arrêt fortuit → {txt}")
        print()


if __name__ == "__main__":
    quoi = sys.argv[1] if len(sys.argv) > 1 else "tout"
    pl.Config.set_tbl_cols(40); pl.Config.set_tbl_width_chars(260); pl.Config.set_tbl_rows(30)
    d = joindre()
    if quoi in ("regimes", "tout"):
        regimes(d)
    if quoi in ("reponse_fr", "tout"):
        reponse_fr(d)
    if quoi in ("zone", "tout"):
        zone(d); regimes_zone(d)
    if quoi in ("instrument", "tout"):
        instrument(d)
    if quoi in ("fortuit", "tout"):
        instrument_fortuit(d)
    if quoi in ("decalage", "tout"):
        decalage(d)
    if quoi in ("moyen", "tout"):
        moyen(d)
