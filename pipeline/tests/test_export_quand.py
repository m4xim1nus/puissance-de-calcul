"""Export de « Quand ? » (pc/export_quand.py) sur données synthétiques : années pleines, arrondis,
JSON, encadrement hors EPR, chiffres calculés au schéma du référentiel."""

import json
from datetime import datetime, timedelta, timezone

import polars as pl

from pc import chiffres, export_quand, quand
from pc.build import DATETIME_UTC


def table_synthetique(debut: datetime, heures: int, **valeurs) -> pl.DataFrame:
    t = pl.DataFrame({"heure_utc": [debut + timedelta(hours=i) for i in range(heures)]})
    t = t.with_columns(pl.col("heure_utc").cast(DATETIME_UTC))
    base = {"consommation": 60000.0, "eolien": 5000.0, "solaire": 1000.0, "nucleaire": 40000.0,
            "nucleaire_disponible": 45000.0, "nucleaire_disponible_flamanville3": 0.0, "prix_eur_mwh": 50.0,
            "nature": "definitif", "gaz_ccg": 0.0, "gaz_tac": 0.0, "gaz_cogen": 0.0, "gaz_autres": 0.0,
            "hydraulique": 0.0, "bioenergies": 0.0}
    base.update(valeurs)
    for c in quand.COMPOSANTES:
        base.setdefault(c, 0.0)
    return t.with_columns([pl.lit(v).alias(k) for k, v in base.items()])


def test_annees_pleines_et_exclues():
    debut = datetime(2022, 12, 31, 23, tzinfo=timezone.utc)  # 1er janvier 2023, minuit à Paris
    t = table_synthetique(debut, 8760 + 100)
    pleines, exclues = export_quand.annees_pleines(t)
    assert pleines == [2023] and list(exclues) == [2024]
    t2 = t.with_columns(pl.when(pl.col("heure_utc") == debut).then(pl.lit("temps_reel")).otherwise(pl.col("nature"))
                        .alias("nature"))
    assert export_quand.annees_pleines(t2)[0] == []


def test_table_annee_arrondie_comme_les_csv():
    debut = datetime(2022, 12, 31, 23, tzinfo=timezone.utc)
    t = table_synthetique(debut, 3, consommation=60000.4, prix_eur_mwh=-0.00251)
    d = export_quand.table_annee(t, 2023)
    assert d["heure_utc"][0] == "2022-12-31T23:00Z"
    assert d["consommation"] == [60000, 60000, 60000] and isinstance(d["consommation"][0], int)
    assert d["prix"][0] == -0.0025


def test_arrondir_et_json_lisible():
    o = {"part_dans_j": 0.123456, "energie_twh": 1.234567, "valeur_mw": 1234.6,
         "quantiles_mw": {"p50": 10.4}, "monotone": [[1, 5.6], [2, 4.4]], "heures": 8760,
         "par_annee": {2015: {"x": 1.0}}}
    a = export_quand.arrondir(o)
    assert a["part_dans_j"] == 0.1235 and a["energie_twh"] == 1.2346 and a["valeur_mw"] == 1235
    assert a["quantiles_mw"]["p50"] == 10 and a["monotone"] == [[1, 6], [2, 4]] and a["heures"] == 8760
    texte = export_quand._dumps(a)
    assert json.loads(texte)["par_annee"]["2015"] == {"x": 1.0}
    assert '[1, 6]' in texte


def test_encadrement_flamanville3():
    t = {"nucleaire_disponible": [50000, 50000], "nucleaire_disponible_flamanville3": [1000, 1000],
         "nucleaire": [48000, 49500]}
    e = export_quand.encadrement_flamanville3(t)
    # J total = 2 000 + 500 ; sans le disponible de l'EPR : 1 000 + 0
    assert e["disponible_declare_epr_twh"] == 0.002 and e["somme_j_sans_disponible_epr_twh"] == 0.001
    assert export_quand.encadrement_flamanville3({**t, "nucleaire_disponible_flamanville3": [0, 0]}) is None


def test_chiffres_calcules_au_schema_du_referentiel():
    debut = datetime(2022, 12, 31, 23, tzinfo=timezone.utc)
    t = table_synthetique(debut, 8760)
    t = t.with_columns(pl.when(pl.col("heure_utc").dt.hour() == 17).then(70000.0).otherwise(60000.0)
                       .alias("consommation"))
    q = export_quand.construire_quand(t, {"eco2mix": "2026-11-25T23:12:49+00:00"})
    q = json.loads(export_quand._dumps(q))  # comme relu depuis le fichier
    calc = export_quand.chiffres_calcules(q)
    ids = {"quand_rn_max_2023", "quand_j_2023", "quand_part_j_1gw_2023", "quand_part_j_5gw_2023",
           "quand_part_j_10gw_2023", "quand_heures_rn_sup_max_5gw_2023", "quand_heures_rn_sup_max_10gw_2023",
           "quand_top100_hiver_2023", "quand_top100_plages_2023", "quand_top100_solde_2023",
           "quand_top100_gaz_2023", "quand_top100_lacs_step_2023", "quand_top100_fil_eau_2023",
           "quand_top100_plages_pp_2023", "quand_heures_j5_2023", "quand_solde_j5_2023"}
    assert set(calc) == ids  # pas d'EPR : pas de quand_j_2023_hors_epr
    # RN = 70 000 − 5 000 − 1 000 − 45 000 à 17 h UTC (18 h à Paris en hiver)
    assert calc["quand_rn_max_2023"]["valeur"] == 19.0 and calc["quand_rn_max_2023"]["unite"] == "GW"
    assert calc["quand_rn_max_2023"]["periode"] == "2023-01-01, 18 h-19 h (heure de Paris)"
    assert calc["quand_j_2023"]["valeur"] == 43.8 and calc["quand_j_2023"]["valeur_calculee"] == 43.8
    assert calc["quand_part_j_1gw_2023"]["valeur"] == 100 and calc["quand_part_j_10gw_2023"]["valeur"] == 50
    assert calc["quand_top100_gaz_2023"]["valeur"] == 0.0 and calc["quand_top100_gaz_2023"]["grandeur"] == "puissance_moyenne"
    vide = chiffres.Referentiel(sources={}, chiffres={})
    fusion = chiffres.fusionner(vide, {export_quand.SOURCE_QUAND: export_quand.source_quand("2026-11-26")}, calc)
    assert chiffres.valider(fusion) == []
    assert all(c["confiance"] != "A" for c in calc.values())  # pas de A sans recoupement indépendant


def test_couverture_et_borne_hors_epr_publiees():
    """Couverture des heures tendues (signe du solde conservé : positif = import) et Σ J hors EPR."""
    debut = datetime(2022, 12, 31, 23, tzinfo=timezone.utc)
    t = table_synthetique(debut, 8760, ech_physiques=-3184.0, gaz=7572.0, hydraulique_lacs=5577.0,
                          hydraulique_step_turbinage=2616.0, hydraulique_fil_eau_eclusee=6875.0,
                          nucleaire_disponible_flamanville3=500.0)
    q = json.loads(export_quand._dumps(export_quand.construire_quand(t, {})))
    calc = export_quand.chiffres_calcules(q)
    assert calc["quand_top100_solde_2023"]["valeur"] == -3.2
    assert "positif = import" in calc["quand_top100_solde_2023"]["libelle"]
    assert calc["quand_top100_gaz_2023"]["valeur"] == 7.6
    assert calc["quand_top100_lacs_step_2023"]["valeur"] == 8.2  # 5,577 + 2,616 = 8,193
    assert calc["quand_top100_fil_eau_2023"]["valeur"] == 6.9
    # J = 5 000 MW ; sans le disponible de l'EPR : 4 500 MW, sur 8 760 h
    h = calc["quand_j_2023_hors_epr"]
    assert h["valeur"] == 39.4 and h["valeur_calculee"] == 39.42 and h["unite"] == "TWh"
    # J = 5 000 MW à toutes les heures : J ≥ 5 GW sur 8 760 h, solde moyen −3,184 GW
    assert calc["quand_heures_j5_2023"]["valeur"] == 8760
    assert calc["quand_solde_j5_2023"]["valeur"] == -3.2
    for c in calc.values():
        assert c["valeur"] == chiffres.arrondi_publie(c["valeur_calculee"], c["precision"])
