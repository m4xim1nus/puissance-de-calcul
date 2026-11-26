"""Spike jetable : sources de « marge » pour l'enquête « Quand ? ».

Relançable :
    uv run --no-project --with httpx,polars python -I pipeline/explo/spike_quand.py download
    uv run --no-project --with httpx,polars python -I pipeline/explo/spike_quand.py analyse
    uv run --no-project --with httpx,polars python -I pipeline/explo/spike_quand.py indicateurs

Échantillons : data/raw/spike_quand/ (non versionné). Téléchargements sautés
si le fichier existe déjà. Aucun jeton requis. Rapport : docs/spike/quand.md.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import httpx
import polars as pl

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "spike_quand"
EXPORT = ROOT / "data" / "export"
ODRE = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets"
EDF = "https://opendata.edf.fr/data-fair/api/v1/datasets"

PDF = {
    # BP2025 (RTE) : chapitres utiles à la marge et au surplus
    "bp2025_principaux_resultats.pdf": "https://assets.rte-france.com/prod/public/2025-12/2025-12-16-bilan-previsionnel-principaux-resultats-2025.pdf",
    "bp2025_resume_executif.pdf": "https://assets.rte-france.com/prod/public/2025-12/2025-12-09-BP2025-resume-executif-synthese.pdf",
    "bp2025_production.pdf": "https://assets.rte-france.com/prod/public/2026-01/BP2025-chapitre-production.pdf",
    "bp2025_fonctionnement.pdf": "https://assets.rte-france.com/prod/public/2026-07/2026-07-15-bilan-previsionnel-fonctionnement-systeme-electrique.pdf",
    "bp2025_analyse_eco.pdf": "https://assets.rte-france.com/prod/public/2026-07/2026-07-15-bilan-previsionnel-analyse-economique.pdf",
    "bp2025_europe.pdf": "https://assets.rte-france.com/prod/public/2025-12/2025-12-23-bilan-previsionnel-2025-europe.pdf",
    "bp2025_consommation.pdf": "https://assets.rte-france.com/prod/public/2025-12/2025-12-23-bilan-previsionnel-2025-consommation.pdf",
    "perspectives_2025-12-09.pdf": "https://assets.rte-france.com/prod/public/2025-12/2025-12-09-perspectives-systeme-electrique.pdf",
    "be2025.pdf": "https://assets.rte-france.com/analyse-et-donnees/2026-03/BE2025%20-%20Rapport%20Complet.pdf",
    "be2024.pdf": "https://assets.rte-france.com/analyse-et-donnees/2025-09/BE2024%20-%20Rapport%20Complet.pdf",
    # Analyses saisonnières et mécanisme de capacité
    "hiver_2026-2027_synthese.pdf": "https://assets.rte-france.com/prod/public/2026-11/2026-11-18-synthese-perspectives-passage-hiver-2026-2027.pdf",
    "ete_2026_premieres_analyses.pdf": "https://assets.rte-france.com/prod/public/2026-09/20260921%20-%20Premi%C3%A8res%20analyses%20%C3%A9t%C3%A9%202026.pdf",
    "rte_parametrage_mecapa_2026-02-12.pdf": "https://assets.rte-france.com/prod/public/2026-02/2026-02-12-rapport-parametrage-mecanisme-capacite.pdf",
    "cre_2026-43_parametrage.pdf": "https://www.cre.fr/fileadmin/Documents/Deliberations/2026/260210_2026-43_Parametrage_PL_26-27.pdf",
}

ODRE_JEUX = [
    "nouveau_signal_ecowatt",
    "signal-ecowatt",
    "effacements-quotidiens-ma",
    "volumes-actives-ma",
    "registre-garanties-capacite",
    "extremas-quotidiens-flux-commerciaux",
]

EDF_JEUX = {
    "historique_indispo_2015.csv": "historique-des-indisponibilites-des-moyens-de-production-de-edf-sa-depuis-2015",
    "indispo_courantes.csv": "indisponibilites-des-moyens-de-production-edf-sa",
}


def _get(client: httpx.Client, url: str, dest: Path, params: dict | None = None) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  déjà là : {dest.name}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    r = client.get(url, params=params)
    print(f"  {dest.name} : HTTP {r.status_code}, {len(r.content) / 1e6:.2f} Mo en {time.time() - t0:.0f} s")
    r.raise_for_status()
    dest.write_bytes(r.content)


def download() -> None:
    with httpx.Client(timeout=600, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as c:
        for nom, url in PDF.items():
            _get(c, url, RAW / "pdf" / nom)
        for ds in ODRE_JEUX:
            _get(c, f"{ODRE}/{ds}/exports/csv", RAW / "odre" / f"{ds}.csv", {"delimiter": ";"})
        for nom, slug in EDF_JEUX.items():
            _get(c, f"{EDF}/{slug}/raw", RAW / "edf" / nom)
        # Accès sans jeton aux API data.rte-france.com : HTTP 400 attendu (OAuth requis)
        for api in ("ecowatt/v5/signals", "unavailability_additional_information/v6/generation_unavailabilities"):
            r = c.get(f"https://digital.iservices.rte-france.com/open_api/{api}")
            print(f"  API RTE {api} sans jeton : HTTP {r.status_code}")
        # Tempo (couleurs des jours, contrats « Tempo-like ») : endpoint d'éCO2mix
        for saison in ("2023-2024", "2024-2025", "2025-2026"):
            _get(
                c,
                "https://eco2mix.rte-france.com/curves/downloadCalendrierTempo",
                RAW / "tempo" / f"tempo_{saison}.zip",
                {"annee": saison},
            )
        # JAO, publication tool Core : positions nettes max (flow-based)
        _get(
            c,
            "https://publicationtool.jao.eu/core/api/data/maxNetPos",
            RAW / "jao" / "core_maxnetpos_20250601.json",
            {"FromUtc": "2025-06-01T00:00:00.000Z", "ToUtc": "2025-06-02T00:00:00.000Z"},
        )


# --------------------------------------------------------------------------
# Analyse des jeux téléchargés
# --------------------------------------------------------------------------


def analyse() -> None:
    o = RAW / "odre"
    # Ecowatt : distribution des valeurs horaires
    ew = pl.read_csv(o / "nouveau_signal_ecowatt.csv", separator=";", infer_schema_length=0)
    hcols = [f"h{i}" for i in range(24)]
    long =ew.unpivot(index="date", on=hcols, variable_name="h", value_name="v")
    print("Ecowatt : période", ew["date"].min(), "→", ew["date"].max(), "jours", ew.height)
    print(long.group_by("v").len().sort("v"))
    print(
        long.filter(pl.col("v").cast(pl.Int32) >= 2)
        .with_columns(pl.col("date").str.slice(0, 4).alias("an"))
        .group_by("an", "v")
        .len()
        .sort("an", "v")
    )
    # Effacements sur le mécanisme d'ajustement
    ef = pl.read_csv(o / "effacements-quotidiens-ma.csv", separator=";")
    ef = ef.with_columns(pl.col("date").str.slice(0, 4).alias("an"))
    print("Effacements MA : ", ef["date"].min(), "→", ef["date"].max())
    print(
        ef.group_by("an")
        .agg(
            pl.col("capacite_effacement_moy").mean().round(0).alias("offre_moy_MW"),
            pl.col("pmax_effacee").max().alias("pmax_activee_MW"),
            (pl.col("pmax_effacee") > 0).sum().alias("jours_activation"),
        )
        .sort("an")
    )
    va = pl.read_csv(o / "volumes-actives-ma.csv", separator=";")
    print(va.sort("annee").select("annee", "vah_effacement", "vab_consommation", "nb_situations_tendues_h_en_1_2j", "nb_situations_tendues_b_en_1_2j"))
    # Garanties de capacité : prix par année de livraison
    gc = pl.read_csv(o / "registre-garanties-capacite.csv", separator=";", infer_schema_length=0)
    print("Garanties de capacité :", gc.height, "lignes ; types", gc["type"].unique().to_list())
    print(gc.head(5))
    fx = pl.read_csv(o / "extremas-quotidiens-flux-commerciaux.csv", separator=";")
    print("Extremas flux commerciaux :", fx["date"].min(), "→", fx["date"].max())
    print(fx.with_columns(pl.col("date").str.slice(0, 4).alias("an")).group_by("an").agg(pl.col("solde_min").min(), pl.col("solde_max").max()).sort("an"))


# --------------------------------------------------------------------------
# Indisponibilités nucléaires EDF (REMIT) → disponibilité horaire
# --------------------------------------------------------------------------


COLS_EDF = ["status", "id", "version", "nom", "filiere", "debut", "fin", "type", "cause", "info", "pmax", "pdispo", "pub"]


def remit_nucleaire() -> pl.DataFrame:
    """Indisponibilités nucléaires EDF (REMIT), dernière version active de chaque événement.

    Fichier : historique depuis 2015 (export du 07/09/2026), latin-1, « ; », virgule
    décimale, dates « jj/mm/aaaa hh:mm » supposées en heure de Paris (non documenté
    dans la fiche ; la note explicative EDF renvoie HTTP 403).
    """
    h = pl.read_csv(RAW / "edf" / "historique_indispo_2015.csv", separator=";", encoding="latin1", infer_schema_length=0)
    h.columns = COLS_EDF
    n = h.filter((pl.col("filiere") == "Nucléaire") & pl.col("type").is_in(["Planifiée", "Fortuite"]))
    n = n.with_columns(
        pl.col("version").cast(pl.Int32),
        pl.col("pmax").str.replace(",", ".").cast(pl.Float64),
        pl.col("pdispo").str.replace(",", ".").cast(pl.Float64),
        pl.col("debut").str.strptime(pl.Datetime, "%d/%m/%Y %H:%M").dt.replace_time_zone("Europe/Paris", ambiguous="earliest", non_existent="null").dt.convert_time_zone("UTC").alias("d"),
        pl.col("fin").str.strptime(pl.Datetime, "%d/%m/%Y %H:%M").dt.replace_time_zone("Europe/Paris", ambiguous="earliest", non_existent="null").dt.convert_time_zone("UTC").alias("f"),
    )
    # dernière version de chaque événement ; on écarte annulées et supprimées
    n = n.sort("version").group_by("id").last().filter(pl.col("status") == "Active")
    return n


def dispo_nucleaire(annee: int, n: pl.DataFrame | None = None) -> pl.DataFrame:
    """Puissance nucléaire disponible déclarée (MW) au pas horaire UTC, année civile de Paris.

    Pour chaque tranche et chaque heure : minimum des puissances disponibles des
    événements actifs couvrant le milieu de l'heure (règle EDF de superposition),
    sinon la puissance maximale de la tranche (max observé dans le fichier).
    """
    n = remit_nucleaire() if n is None else n
    t0 = pl.datetime(annee, 1, 1, time_zone="Europe/Paris").dt.convert_time_zone("UTC")
    t1 = pl.datetime(annee + 1, 1, 1, time_zone="Europe/Paris").dt.convert_time_zone("UTC")
    heures = pl.select(pl.datetime_range(t0, t1, "1h", closed="left").alias("h"))
    # Fessenheim (fermée en 2020) n'a plus d'événement : sans ce filtre elle
    # compterait comme disponible à pleine puissance.
    pmax = n.filter(~pl.col("nom").str.starts_with("FESSENHEIM")).group_by("nom").agg(pl.col("pmax").max())
    ev = n.filter((pl.col("f") > heures["h"].min()) & (pl.col("d") < heures["h"].max() + pl.duration(hours=1)))
    ev = ev.with_columns(
        pl.datetime_ranges(
            (pl.col("d") - pl.duration(minutes=30)).dt.truncate("1h"),
            pl.col("f"),
            "1h",
        ).alias("h")
    ).explode("h")
    ev = ev.filter((pl.col("h") + pl.duration(minutes=30) >= pl.col("d")) & (pl.col("h") + pl.duration(minutes=30) < pl.col("f")))
    ev = ev.group_by("nom", "h").agg(pl.col("pdispo").min())
    grille = heures.join(pmax, how="cross").join(ev, on=["nom", "h"], how="left")
    grille = grille.with_columns(pl.coalesce("pdispo", "pmax").clip(upper_bound=pl.col("pmax")).alias("dispo"))
    return grille


def indicateurs() -> None:
    """Indicateurs candidats, calculés à titre exploratoire (spike, pas de publication).

    Sources : data/export/systeme_horaire.parquet (éCO2mix + prix) et disponibilité
    nucléaire REMIT reconstruite (dispo_nucleaire_AAAA.parquet, voir dispo_nucleaire).
    """
    sh = pl.read_parquet(EXPORT / "systeme_horaire.parquet").with_columns(
        pl.col("heure_utc").cast(pl.Datetime("us", "UTC")).alias("h")
    )
    for an in (2023, 2024, 2025):
        dn = pl.read_parquet(RAW / f"dispo_nucleaire_{an}.parquet").select("h", "dispo_hf3", "dispo")
        d = sh.join(dn, on="h").drop_nulls(["consommation", "nucleaire", "eolien", "solaire"])
        # Flamanville 3 : exclu de la disponibilité en 2023-2024 (essais), inclus en 2025
        dispo = "dispo_hf3" if an < 2025 else "dispo"
        d = d.with_columns(
            (pl.col("consommation") - pl.col("eolien") - pl.col("solaire")).alias("resid"),
            (pl.col("consommation") - pl.col("eolien") - pl.col("solaire") - pl.col(dispo)).alias("resid_nuc"),
            (pl.col(dispo) - pl.col("nucleaire")).clip(lower_bound=0).alias("jeu_nuc"),
            (pl.col("gaz_tac") + pl.col("fioul")).alias("pointe_thermique"),
        )
        print(f"===== {an} ({d.height} h)")
        print(
            d.select(
                (pl.col("consommation").max() / 1e3).round(1).alias("conso_max_GW"),
                (pl.col("resid").max() / 1e3).round(1).alias("resid_max_GW"),
                (pl.col("resid_nuc").max() / 1e3).round(1).alias("resid_nuc_max_GW"),
                (pl.col("resid_nuc").quantile(0.99) / 1e3).round(1).alias("resid_nuc_p99_GW"),
                (pl.col("resid_nuc") < 0).sum().alias("h_resid_nuc<0"),
                (pl.col("ech_physiques") > 0).sum().alias("h_import"),
                (pl.col("pointe_thermique") > 500).sum().alias("h_TAC+fioul>0,5GW"),
                (pl.col("prix_eur_mwh") <= 0).sum().alias("h_prix<=0"),
                (pl.col("jeu_nuc").sum() / 1e6).round(1).alias("jeu_nuc_TWh"),
            )
        )
        # Les 100 heures de plus forte charge résiduelle nette du nucléaire disponible : qui couvre ?
        top = d.sort("resid_nuc", descending=True).head(100)
        print(
            "  100 h les plus tendues (moyennes, GW) :",
            top.select(
                (pl.col(c).mean() / 1e3).round(1).alias(c)
                for c in ["resid_nuc", "hydraulique_lacs", "hydraulique_step_turbinage", "gaz", "gaz_tac", "fioul", "ech_physiques", "jeu_nuc"]
            ).to_dicts()[0],
            "prix moyen", round(top["prix_eur_mwh"].mean(), 1),
        )
        # Charge plate supplémentaire de X GW
        for x in (1, 5, 10, 15):
            xm = x * 1000
            r = d.select(
                # part de l'énergie ajoutée qui tiendrait dans le jeu nucléaire observé
                (pl.min_horizontal(pl.col("jeu_nuc"), pl.lit(xm)).sum() / (xm * pl.len()) * 100).round(1).alias("part_jeu_nuc_%"),
                # heures où la charge résiduelle nette dépasserait le maximum observé l'année même
                (pl.col("resid_nuc") + xm > pl.col("resid_nuc").max()).sum().alias("h_au_dela_max_annee"),
                # heures à prix <= 0 (énergie ajoutée qui y tombe)
                ((pl.col("prix_eur_mwh") <= 0).sum() / pl.len() * 100).round(1).alias("part_h_prix<=0_%"),
            )
            print(f"  +{x} GW plat :", r.to_dicts()[0])


if __name__ == "__main__":
    {"download": download, "analyse": analyse, "indicateurs": indicateurs}[sys.argv[1]]()
