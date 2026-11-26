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
    base.setdefault("nucleaire_disponible_reintegre", base["nucleaire_disponible"])
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
    toutes = {"quand_rn_max_pluri", "quand_conso_max_pluri", "quand_top100_rn_moyenne_2023", "quand_heures_rn_sup_max_pluri_5gw_2023",
              "quand_heures_rn_sup_max_pluri_10gw_2023", "quand_heures_prix_chers_2023",
              "quand_part_j_plancher_5gw_2023", "quand_part_j_plancher_10gw_2023", "quand_energie_j_5gw_2023",
              "quand_energie_j_10gw_2023"}
    # variantes réintégrant les arrêts courts pour modulation (la table a la colonne, ici égale au déclaré)
    toutes |= {"quand_arrets_modulation_courts_2023", "quand_j_reintegre_2023", "quand_part_j_reintegre_5gw_2023",
               "quand_part_j_reintegre_10gw_2023", "quand_part_j_plancher_reintegre_5gw_2023",
               "quand_part_j_plancher_reintegre_10gw_2023", "quand_energie_j_reintegre_5gw_2023",
               "quand_energie_j_reintegre_10gw_2023"}
    # pas d'EPR : pas de quand_j_2023_hors_epr ; aucun prix > 150 €/MWh : pas de quand_j_heures_cheres_2023
    assert set(calc) == ids | toutes
    # RN = 70 000 − 5 000 − 1 000 − 45 000 à 17 h UTC (18 h à Paris en hiver)
    assert calc["quand_rn_max_2023"]["valeur"] == 19.0 and calc["quand_rn_max_2023"]["unite"] == "GW"
    assert calc["quand_rn_max_2023"]["periode"] == "2023-01-01, 18 h-19 h (heure de Paris)"
    assert calc["quand_j_2023"]["valeur"] == 43.8 and calc["quand_j_2023"]["valeur_calculee"] == 43.8
    assert calc["quand_part_j_1gw_2023"]["valeur"] == 100 and calc["quand_part_j_10gw_2023"]["valeur"] == 50
    assert calc["quand_top100_gaz_2023"]["valeur"] == 0.0 and calc["quand_top100_gaz_2023"]["grandeur"] == "puissance_moyenne"
    # Consommation horaire maximale : 70 000 MW à 17 h UTC, la première heure à ce niveau (1er janvier)
    assert calc["quand_conso_max_pluri"]["valeur"] == 70.0
    assert calc["quand_conso_max_pluri"]["periode"] == "2023-01-01, 18 h-19 h (heure de Paris)"
    vide = chiffres.Referentiel(sources={}, chiffres={})
    fusion = chiffres.fusionner(vide, {export_quand.SOURCE_QUAND: export_quand.source_quand("2026-11-26")}, calc)
    assert chiffres.valider(fusion) == []
    assert all(c["confiance"] != "A" for c in calc.values())  # pas de A sans recoupement indépendant


def test_chiffres_reintegrant_les_arrets_pour_modulation():
    """Disponible déclaré 45 000 MW, réintégrant les arrêts courts 47 000 MW, produit 40 000 MW : J = 5 000,
    J_r = 7 000 MW toute l'année ; arrêts longs (non réintégrés) 8,76 TWh, fournis par le build ;
    les chiffres déclarés ne bougent pas, les variantes s'ajoutent."""
    debut = datetime(2022, 12, 31, 23, tzinfo=timezone.utc)
    t = table_synthetique(debut, 8760, nucleaire_disponible_reintegre=47000.0)
    q = json.loads(export_quand._dumps(export_quand.construire_quand(t, {}, {2023: 8.76})))
    r = q["annees"]["2023"]["jeu_nucleaire_reintegre"]
    assert r["somme_twh"] == 61.32 and r["arrets_modulation_courts_twh"] == 17.52 and r["heures_valides"] == 8760
    assert r["arrets_modulation_longs_twh"] == 8.76  # fourni par le build (1 000 MW toute l'année)
    calc = export_quand.chiffres_calcules(q)
    assert calc["quand_j_2023"]["valeur"] == 43.8 and calc["quand_part_j_10gw_2023"]["valeur"] == 50
    assert calc["quand_j_reintegre_2023"]["valeur"] == 61.3
    assert calc["quand_arrets_modulation_courts_2023"]["valeur"] == 17.5
    assert calc["quand_arrets_modulation_longs_2023"]["valeur"] == 8.8
    assert "8,8 TWh" in calc["quand_arrets_modulation_courts_2023"]["note"]
    assert calc["quand_part_j_reintegre_5gw_2023"]["valeur"] == 100
    assert calc["quand_part_j_reintegre_10gw_2023"]["valeur"] == 70
    # plancher 1 000 MW : J' = 4 000 → 40 % ; J_r' = 6 000 → 60 %
    assert calc["quand_part_j_plancher_10gw_2023"]["valeur"] == 40
    assert calc["quand_part_j_plancher_reintegre_10gw_2023"]["valeur"] == 60
    assert calc["quand_energie_j_reintegre_10gw_2023"]["valeur_calculee"] == 61.32
    # la note du chiffre déclaré cite la variante ; le libellé dit de quelle disponibilité il s'agit
    assert "70 %" in calc["quand_part_j_10gw_2023"]["note"]
    assert "disponibilité déclarée par EDF" in calc["quand_part_j_10gw_2023"]["libelle"]
    assert any(l.startswith("disponibilité déclarée, chiffrée (2023)") and "50 % à 70 %" not in l
               for l in q["limites"]["jeu_nucleaire"])  # la ligne chiffrée cite 5 GW : 100 % à 100 %
    vide = chiffres.Referentiel(sources={}, chiffres={})
    fusion = chiffres.fusionner(vide, {export_quand.SOURCE_QUAND: export_quand.source_quand("2026-11-26")}, calc)
    assert chiffres.valider(fusion) == []


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


def test_chiffres_du_plancher_du_seuil_pluriannuel_et_des_prix_chers():
    """Deux années : le maximum pluriannuel vient de la plus tendue ; J = 5 000 MW partout,
    plancher 1 000 MW → J' = 4 000 MW ; heures chères (prix 200 €/MWh) la moitié du temps."""
    debut = datetime(2022, 12, 31, 23, tzinfo=timezone.utc)
    t = table_synthetique(debut, 8760 + 8784)
    t = t.with_columns(
        pl.when(pl.col("heure_utc") == datetime(2023, 1, 10, 17, tzinfo=timezone.utc)).then(70000.0)
          .when(pl.col("heure_utc").dt.convert_time_zone("Europe/Paris").dt.year() == 2024).then(64000.0)
          .otherwise(60000.0).alias("consommation"),
        pl.when(pl.col("heure_utc").dt.hour() < 12).then(200.0).otherwise(50.0).alias("prix_eur_mwh"))
    q = json.loads(export_quand._dumps(export_quand.construire_quand(t, {})))
    assert q["rn_max_pluriannuel"]["valeur_mw"] == 19000 and q["rn_max_pluriannuel"]["annee"] == "2023"
    calc = export_quand.chiffres_calcules(q)
    assert calc["quand_rn_max_pluri"]["valeur"] == 19.0
    assert calc["quand_rn_max_pluri"]["periode"] == "2023-01-10, 18 h-19 h (heure de Paris)"
    # 2024 : RN = 64 000 − 6 000 − 45 000 = 13 000 ; + 5 GW = 18 000 < 19 000 ; + 10 GW > 19 000 partout
    assert calc["quand_heures_rn_sup_max_pluri_5gw_2024"]["valeur"] == 0
    assert calc["quand_heures_rn_sup_max_pluri_10gw_2024"]["valeur"] == 8784
    assert calc["quand_heures_rn_sup_max_5gw_2024"]["valeur"] == 8784  # maximum annuel : toutes égales
    assert calc["quand_part_j_plancher_5gw_2023"]["valeur"] == 80  # 4 000 / 5 000
    assert calc["quand_part_j_5gw_2023"]["valeur"] == 100
    assert calc["quand_energie_j_10gw_2023"]["valeur"] == 43.8  # 5 000 MW × 8 760 h
    assert calc["quand_heures_prix_chers_2023"]["valeur"] == 4380
    assert calc["quand_j_heures_cheres_2023"]["valeur"] == 5.0
    assert calc["quand_top100_rn_moyenne_2023"]["valeur_calculee"] == 9.1  # (19 000 + 99 × 9 000) / 100
    for c in calc.values():
        assert "quand_" not in c.get("note", ""), "identifiant interne dans une note (relecture Fo2)"
        assert "servie en partie par moins d'exports" not in c.get("note", "")


def test_ecretement_reparti_sur_les_heures_a_prix_negatif():
    """Limite « écrêtement » : production renoncée (TWh) ÷ heures à prix < 0 = MW moyens, borne haute.
    Synthèse : 2023 à prix −10 €/MWh une heure sur quatre (2 190 h) ; 2,19 TWh renoncés → 1 000 MW."""
    debut = datetime(2022, 12, 31, 23, tzinfo=timezone.utc)
    t = table_synthetique(debut, 8760)
    t = t.with_columns(pl.when(pl.col("heure_utc").dt.hour() % 4 == 0).then(-10.0).otherwise(50.0)
                       .alias("prix_eur_mwh"))
    q = json.loads(export_quand._dumps(export_quand.construire_quand(t, {})))
    assert q["annees"]["2023"]["prix"]["heures_negatif"] == 2190
    renoncee = {"id": "renoncee_2023", "libelle": "Production renoncée", "valeur": 2.19, "unite": "TWh"}
    ecretee = {"id": "ecretee_2023", "libelle": "Production écrêtée par RTE", "valeur": 0.1, "unite": "TWh"}
    calc = export_quand.chiffres_calcules(q, {}, {2023: (renoncee, ecretee)})
    c = calc["quand_ecretement_prix_negatif_2023"]
    assert c["valeur"] == 1.0 and c["valeur_calculee"] == 1.0 and c["unite"] == "GW"
    assert c["grandeur"] == "puissance_moyenne" and "borne haute" in c["libelle"]
    # RN = 60 000 − 5 000 − 1 000 − 45 000 = 9 000 MW à ces heures ; sans la production renoncée : 8 000
    assert "9,0 GW" in c["note"] and "8,0 GW" in c["note"] and "renoncee_2023" in c["citation"]
    vide = chiffres.Referentiel(sources={}, chiffres={})
    fusion = chiffres.fusionner(vide, {export_quand.SOURCE_QUAND: export_quand.source_quand("2026-11-26")}, calc)
    assert chiffres.valider(fusion) == []
    # Sans chiffre saisi, rien n'est calculé ; une unité inattendue est refusée.
    assert "quand_ecretement_prix_negatif_2023" not in export_quand.chiffres_calcules(q)
    import pytest
    with pytest.raises(ValueError):
        export_quand.chiffres_calcules(q, {}, {2023: ({**renoncee, "unite": "GWh"}, ecretee)})


def test_ecretement_du_referentiel():
    ref = chiffres.charger()
    e = export_quand.ecretement_du_referentiel(ref.chiffres)
    assert set(e) == {2025}
    assert e[2025][0]["valeur"] == 3 and e[2025][1]["valeur"] == 0.1
    assert e[2025][0]["id"] == "enr_renoncees_prix_negatifs_2025"


def test_froid_pour_depasser_et_chiffre_du_froid():
    """Plus petit froid au pas de 0,5 °C qui porte le maximum du scénario strictement au-delà du seuil
    (2025 : 87 438 MW dans l'épisode, 2 400 MW/°C, 100 GW → 5,5 °C ; 5 °C donnent 99 438 MW)."""
    f = {"consommation_max_episode_mw": 87438, "consommation_max_hors_episode_mw": 82749}
    assert export_quand.froid_pour_depasser(f, 100000, 2400) == 5.5
    assert export_quand.froid_pour_depasser({**f, "consommation_max_episode_mw": 88000}, 100000, 2400) == 5.5
    assert export_quand.froid_pour_depasser({**f, "consommation_max_episode_mw": 88001}, 100000, 2400) == 5.0
    assert export_quand.froid_pour_depasser({**f, "consommation_max_hors_episode_mw": 100001}, 100000, 2400) == 0.0
    debut = datetime(2022, 12, 31, 23, tzinfo=timezone.utc)
    t = table_synthetique(debut, 8760)
    q = json.loads(export_quand._dumps(export_quand.construire_quand(t, {})))
    assert q["annees"]["2023"]["froid"]["heures"] == 168
    gradient = {"valeur": 2400, "unite": "MW/°C", "id": "g"}
    pointe = {"valeur": 100, "unite": "GW", "id": "p"}
    calc = export_quand.chiffres_calcules(q, froid=(gradient, pointe))
    # consommation 60 000 MW partout : (100 000 − 60 000) / 1 200 = 33,3 pas → 34 pas de 0,5 °C
    assert calc["quand_froid_100gw_2023"]["valeur"] == 17.0 and calc["quand_froid_100gw_2023"]["unite"] == "°C"
    vide = chiffres.Referentiel(sources={}, chiffres={})
    fusion = chiffres.fusionner(vide, {export_quand.SOURCE_QUAND: export_quand.source_quand("2026-11-26")}, calc)
    assert chiffres.valider(fusion) == []
