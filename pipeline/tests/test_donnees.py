"""Tests sur les exports réels (data/export/), sautés s'ils sont absents."""

import json

import polars as pl
import pytest

from pc.build import COLONNES_CSV, annee_paris, heures_negatives
from pc.check import HEURES_NEGATIVES_RTE

pytestmark = pytest.mark.donnees

MES_FICHIERS = ("systeme_horaire.parquet", "prix_quart_horaire.csv", "meta.json", "horaire")


@pytest.fixture(scope="module")
def table(export):
    return pl.read_parquet(export / "systeme_horaire.parquet")


def test_taille_des_exports(export):
    taille = sum(p.stat().st_size for nom in MES_FICHIERS for p in
                 ([export / nom] if (export / nom).is_file() else (export / nom).rglob("*")) if p.is_file())
    assert taille < 15e6


def test_grille_horaire_sans_trou_ni_doublon(table):
    h = table["heure_utc"]
    assert h.is_unique().all()
    assert (h.diff().drop_nulls().dt.total_minutes() == 60).all()


def test_natures_valides(table):
    assert set(table["nature"].drop_nulls().unique()) <= {"definitif", "consolide", "temps_reel"}


def test_ordres_de_grandeur(table):
    c = table["consommation"].drop_nulls()
    assert 25_000 < c.min() and c.max() < 105_000  # MW, France continentale
    assert table["pompage"].drop_nulls().max() <= 0


def test_csv_annuels(export, table):
    attendu = ["heure_utc"] + [nom for _, nom, _ in COLONNES_CSV]
    annees = sorted(table.select(annee_paris("heure_utc")).to_series().unique().to_list())
    for an in annees:
        d = pl.read_csv(export / "horaire" / f"{an}.csv")
        assert d.columns == attendu
        assert d.height == table.filter(annee_paris("heure_utc") == an).height
    assert (export / "horaire" / "LISEZMOI.md").exists()


def test_energie_2024_csv(export):
    # Σ MW moyens horaires × 1 h ≈ 440,0 TWh (éCO2mix 2024, hors Corse ; spike § 7), à 0,05 % près
    # malgré les deux heures vides d'octobre.
    d = pl.read_csv(export / "horaire" / "2024.csv")
    assert d["consommation"].sum() / 1e6 == pytest.approx(440.0, rel=5e-4)


def test_heures_negatives_depuis_l_export(table):
    calc = heures_negatives(table.select("heure_utc", "prix_eur_mwh"))
    for an, ref in HEURES_NEGATIVES_RTE.items():
        assert calc[an] == ref


def test_meta(export):
    m = json.loads((export / "meta.json").read_text())
    licences = {a["licence"] for a in m["attributions"]}
    assert {"Licence Ouverte v2.0 (Etalab)", "CC BY 4.0"} <= licences
    assert all("extrait_le" in s and "sha256" in s for s in m["sources"].values())
    assert m["conventions"]["horodatage_eco2mix"] in ("fin", "debut")


# --------------------------------------------------------------------------
# Nucléaire disponible (REMIT)
# --------------------------------------------------------------------------


def test_nucleaire_disponible_bornes(table):
    d = table.drop_nulls("nucleaire_disponible")
    assert d["heure_utc"].min() == table["heure_utc"].min()  # dès la première heure de 2015
    assert (d["heure_utc"].diff().drop_nulls().dt.total_minutes() == 60).all()  # sans trou jusqu'à l'extraction
    assert d["nucleaire_disponible"].min() > 20_000 and d["nucleaire_disponible"].max() < 66_000  # MW
    assert (d["nucleaire_disponible"] <= d["nucleaire_puissance_max"] + 0.1).all()
    # parc 2024 hors Flamanville 3 : 61 370 MW (registre ODRÉ, spike système § 3) ; avec l'EPR, + 1 620
    pmax = d.filter(pl.col("heure_utc").dt.year() == 2025)["nucleaire_puissance_max"]
    assert pmax.min() == pytest.approx(61_370 + 1_620)


def test_nucleaire_disponible_dans_les_csv(export):
    d = pl.read_csv(export / "horaire" / "2025.csv")
    assert d["nucleaire_disponible"].null_count() == 0
    assert (d["nucleaire_disponible"] >= d["nucleaire"] * 0.9).mean() > 0.99
    assert "nucleaire_disponible" in (export / "horaire" / "LISEZMOI.md").read_text()


def test_meta_nucleaire_disponible(export):
    from pc import chiffres
    m = json.loads((export / "meta.json").read_text())
    n = m["nucleaire_disponible"]
    assert n["trou_entre_fichiers"] is False
    assert {"edf_remit/historique", "edf_remit/courante"} <= set(n["extractions"])
    assert any("EDF" in a["attribution"] and a["licence"].startswith("Licence Ouverte") for a in m["attributions"])
    ref = chiffres.charger().chiffres
    for an in range(2018, 2026):
        assert abs(n["taux_disponibilite_hors_flamanville3"][str(an)] - ref[f"dispo_nucleaire_rte_{an}"]["valeur"]) <= 0.5
