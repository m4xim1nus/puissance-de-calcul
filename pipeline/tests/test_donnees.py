"""Tests sur les exports réels (data/export/), sautés s'ils sont absents."""

import json

import polars as pl
import pytest

from pc.build import COLONNES_CSV, annee_paris, heures_negatives
from pc.check import HEURES_NEGATIVES_RTE

pytestmark = pytest.mark.donnees

MES_FICHIERS = ("systeme_horaire.parquet", "prix_quart_horaire.csv", "meta.json", "horaire", "quand.json")


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


# --------------------------------------------------------------------------
# « Quand ? » (quand.json, chiffres calculés)
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def q(export):
    return json.loads((export / "quand.json").read_text(encoding="utf-8"))


def test_quand_taille(export):
    assert (export / "quand.json").stat().st_size < 500_000  # quelques centaines de Ko au plus


def test_quand_structure(q):
    assert list(q["annees"]) == [str(a) for a in range(2015, 2026)]
    assert "2026" in q["annees_exclues"]
    for an in ("2022", "2025"):
        m = q["matrices_rn"][an]
        assert len(m["jours"]) == 365 and all(len(ligne) == 24 for ligne in m["valeurs"])
    a = q["annees"]["2025"]
    assert [c["x_mw"] for c in a["charges_plates"]] == [500, 1000, 2000, 5000, 10000, 15000, 20000]
    assert len(a["charge_residuelle"]["monotone"]) < 600 and a["heures_tendues"]["n"] == 100
    assert {"charge_residuelle", "jeu_nucleaire", "charges_plates"} <= set(q["limites"])


def test_quand_retrouve_depuis_les_csv_publies(export, q):
    """Le simulateur lira horaire/AAAA.csv : la fonction de référence appliquée au CSV publié doit
    redonner quand.json (hors couverture des heures tendues, qui lit des colonnes du parquet)."""
    from pc import quand
    for an in ("2022", "2025"):
        d = pl.read_csv(export / "horaire" / f"{an}.csv")
        t = {"heure_utc": d["heure_utc"].to_list(), **{c: d[c].to_list() for c in
             ("consommation", "eolien", "solaire", "nucleaire", "nucleaire_disponible", "prix")}}
        r = quand.indicateurs_annee(t)
        a = q["annees"][an]
        assert r["charge_residuelle"]["max"]["valeur_mw"] == a["charge_residuelle"]["max"]["valeur_mw"]
        assert r["charge_residuelle"]["max"]["heure_utc"] == a["charge_residuelle"]["max"]["heure_utc"]
        assert round(r["jeu_nucleaire"]["somme_twh"], 4) == a["jeu_nucleaire"]["somme_twh"]
        for c, e in zip(r["charges_plates"], a["charges_plates"]):
            assert round(c["part_dans_j"], 4) == e["part_dans_j"]
            assert c["heures_rn_plus_x_au_dessus_du_max"] == e["heures_rn_plus_x_au_dessus_du_max"]
        assert r["prix"]["heures_negatif"] == a["prix"]["heures_negatif"]
        assert [h for h, _ in r["heures_tendues"]["heures"]] == [h for h, _ in a["heures_tendues"]["heures"]]


def test_chiffres_calcules_publies(export):
    c = json.loads((export / "chiffres.json").read_text(encoding="utf-8"))["chiffres"]
    for an in (2023, 2024, 2025):
        for cle in (f"quand_rn_max_{an}", f"quand_j_{an}", f"quand_part_j_1gw_{an}", f"quand_part_j_5gw_{an}",
                    f"quand_part_j_10gw_{an}", f"quand_heures_rn_sup_max_5gw_{an}",
                    f"quand_heures_rn_sup_max_10gw_{an}", f"quand_top100_hiver_{an}", f"quand_top100_plages_{an}"):
            assert c[cle]["produit_par"] == "pc build" and c[cle]["source"]["cle"] == "pdc-quand"
            assert c[cle]["calcul"] and c[cle]["confiance"] in ("B", "C")
    for an in (2022, 2023, 2024, 2025):
        for cle in (f"quand_top100_solde_{an}", f"quand_top100_gaz_{an}", f"quand_top100_lacs_step_{an}",
                    f"quand_top100_fil_eau_{an}", f"quand_solde_j5_{an}"):
            assert c[cle]["unite"] == "GW" and abs(c[cle]["valeur"]) < 20
    assert c["quand_j_2025_hors_epr"]["valeur"] < c["quand_j_2025"]["valeur"]
    assert c["quand_top100_plages_pp_2025"]["valeur"] <= c["quand_top100_plages_2025"]["valeur"]
    assert c["quand_heures_j5_2025"]["unite"] == "heures"
    # relecture adverse de « Quand ? » : chiffres de toutes les années pleines, maximum pluriannuel
    assert c["quand_rn_max_pluri"]["valeur"] >= max(c[f"quand_rn_max_{an}"]["valeur"] for an in (2022, 2023, 2024, 2025))
    for an in range(2015, 2026):
        for cle in (f"quand_top100_rn_moyenne_{an}", f"quand_heures_rn_sup_max_pluri_5gw_{an}",
                    f"quand_heures_rn_sup_max_pluri_10gw_{an}", f"quand_part_j_plancher_5gw_{an}",
                    f"quand_part_j_plancher_10gw_{an}", f"quand_energie_j_5gw_{an}", f"quand_energie_j_10gw_{an}",
                    f"quand_heures_prix_chers_{an}"):
            assert cle in c, cle
        assert c[f"quand_part_j_plancher_5gw_{an}"]["valeur"] <= c[f"quand_part_j_5gw_2025"]["valeur"] or an != 2025
    for an in (2024, 2025):
        assert 0 < c[f"quand_j_heures_cheres_{an}"]["valeur"] < 3
    assert "25,1 et 25,1" not in c["quand_j_2024"]["note"]  # relecture Fo1
    assert not [k for k, v in c.items() if v.get("produit_par") and "quand_" in v.get("note", "")]  # Fo2
    # publié = arrondi : GW et TWh à 0,1, % à l'entier
    for cle, v in c.items():
        if v.get("produit_par"):
            assert {"GW": 0.1, "TWh": 0.1, "%": 1, "heures": 1, "°C": 0.1}[v["unite"]] == v["precision"]
        # ordre de grandeur : RN max entre 20 et 45 GW ; Σ J entre 5 et 50 TWh
    assert all(20 < c[f"quand_rn_max_{an}"]["valeur"] < 45 for an in (2022, 2023, 2024, 2025))
    assert all(5 < c[f"quand_j_{an}"]["valeur"] < 50 for an in (2022, 2023, 2024, 2025))
