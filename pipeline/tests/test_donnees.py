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
