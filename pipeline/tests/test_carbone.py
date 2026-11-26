"""« Quel carbone ? » (pc/carbone.py) sur données synthétiques : moyennes pondérées, statistiques,
matrices mois × heure, années couvertes, chiffres calculés au schéma du référentiel."""

import json
from datetime import datetime, timedelta, timezone

import polars as pl
import pytest

from pc import build, carbone, chiffres
from pc.build import DATETIME_UTC
from pc.export_quand import _dumps

from test_export_quand import table_synthetique

DEBUT_2025 = datetime(2024, 12, 31, 23, tzinfo=timezone.utc)  # 1er janvier 2025, minuit à Paris


def table_2025(**valeurs) -> pl.DataFrame:
    base = {"fioul": 0.0, "charbon": 0.0, "gaz": 2000.0, "taux_co2": 20.0}
    base.update(valeurs)
    return table_synthetique(DEBUT_2025, 8760, **base)


def ges_constante(t: pl.DataFrame, valeur: float) -> pl.DataFrame:
    return t.select("heure_utc", pl.lit(valeur).alias("intensite_conso"))


def test_filieres_identiques_au_build():
    assert carbone.FILIERES == build.FILIERES


def test_moyenne_ponderee_reference():
    # 10 g sur 1 000 MWh et 40 g sur 3 000 MWh : (10 000 + 120 000) / 4 000 = 32,5 (moyenne simple : 25)
    assert carbone.moyenne_ponderee([10.0, 40.0], [1000.0, 3000.0]) == 32.5


def test_moyenne_annuelle_ponderee_par_la_production():
    t = table_2025()
    # À 12 h UTC, intensité de 50 g et production doublée par le solaire ; 10 g le reste du temps.
    midi = pl.col("heure_utc").dt.hour() == 12
    t = t.with_columns(pl.when(midi).then(50.0).otherwise(10.0).alias("taux_co2"),
                       pl.when(midi).then(49000.0).otherwise(1000.0).alias("solaire"))
    c = json.loads(_dumps(carbone.construire_carbone(t, ges_constante(t, 30.0), {})))
    s = c["annees"]["2025"]["production"]
    prod_base = 5000 + 1000 + 40000 + 2000  # éolien + solaire + nucléaire + gaz (synthétique)
    prod_midi = prod_base + 48000
    attendu = (50 * prod_midi + 10 * prod_base * 23) / (prod_midi + prod_base * 23)
    assert s["moyenne_ponderee"] == pytest.approx(attendu, abs=1e-3)
    assert s["moyenne_simple"] == pytest.approx((50 + 23 * 10) / 24, abs=1e-3)
    assert s["max"]["valeur"] == 50 and s["min"]["valeur"] == 10
    # premier maximum : 1er janvier, 12 h UTC = 13 h à Paris
    assert s["max"]["debut_paris"] == "2025-01-01T13:00+01:00"
    # 23 heures sur 24 sous 15 g
    assert s["part_heures_sous_seuil_fond"] == pytest.approx(23 / 24, abs=1e-4)
    # profil horaire : la case de 13 h à Paris (hiver) et 14 h (été) mêlent les deux régimes
    assert len(s["profil_horaire"]) == 24 and len(s["profil_mensuel"]) == 12
    # émissions = Σ g/kWh × MWh / 1e9 (Mt)
    assert s["emissions_directes_mt"] == pytest.approx(
        (50 * prod_midi + 10 * prod_base * 23) * 365 / 1e9, abs=1e-3)
    assert c["annees"]["2025"]["consommation"]["moyenne_ponderee"] == 30.0


def test_hiver_ete_et_matrice_mois_heure():
    t = table_2025()
    hiver = pl.col("heure_utc").dt.convert_time_zone("Europe/Paris").dt.month().is_in([11, 12, 1, 2, 3])
    t = t.with_columns(pl.when(hiver).then(30.0).otherwise(10.0).alias("taux_co2"))
    c = carbone.construire_carbone(t, ges_constante(t, 20.0), {})
    s = c["annees"]["2025"]["production"]
    assert s["moyenne_hiver"] == 30 and s["moyenne_ete"] == 10
    m = c["matrices_mois_heure"]["production"]["2025"]
    assert len(m["valeurs"]) == 12 and all(len(ligne) == 24 for ligne in m["valeurs"])
    assert m["valeurs"][0][0] == 30 and m["valeurs"][6][12] == 10
    # cases extrêmes : la première dans l'ordre (mois, heure) à égalité
    assert m["case_max"] == {"mois": 0, "heure": 0, "valeur": 30, "heures": 31}
    assert m["case_min"]["mois"] == 3 and m["case_min"]["valeur"] == 10


def test_annee_incomplete_ou_serie_trouee_exclue():
    t = table_2025()
    # la série consommation ne couvre que la moitié de l'année : exclue
    ges = ges_constante(t, 20.0).head(4000)
    c = carbone.construire_carbone(t, ges, {})
    assert c["annees_couvertes"] == {"production": [2025], "consommation": []}
    assert "consommation" not in c["annees"]["2025"]
    # sans le jeu ODRÉ : production seule
    c = carbone.construire_carbone(t, None, {})
    assert c["annees_couvertes"]["consommation"] == []
    # une filière manquante rend l'heure invalide (poids inconnu), sans l'imputer ; au-delà de
    # TROUS_ADMIS heures invalides, l'année sort de la série
    def trouee(n):
        return t.with_columns(pl.when(pl.col("heure_utc") < DEBUT_2025 + timedelta(hours=n)).then(None)
                              .otherwise(pl.col("charbon")).alias("charbon"))
    c = carbone.construire_carbone(trouee(5), None, {})
    assert c["annees"]["2025"]["production"]["heures_valides"] == 8755
    assert carbone.construire_carbone(trouee(10), None, {})["annees_couvertes"]["production"] == []


def test_lire_ges_conso_refuse_les_doublons(tmp_path):
    h = [datetime(2025, 1, 1, 0, tzinfo=timezone.utc)] * 2
    pl.DataFrame({"date_heure_utc": h, "intensite_emissions_conso": [20, 21]}).with_columns(
        pl.col("date_heure_utc").cast(pl.Datetime("ms", "UTC"))).write_parquet(tmp_path / "g.parquet")
    with pytest.raises(ValueError, match="double"):
        carbone.lire_ges_conso(tmp_path / "g.parquet")
    pl.DataFrame({"date_heure_utc": h[:1], "intensite_emissions_conso": [20]}).with_columns(
        pl.col("date_heure_utc").cast(pl.Datetime("ms", "UTC"))).write_parquet(tmp_path / "g.parquet")
    g = carbone.lire_ges_conso(tmp_path / "g.parquet")
    assert g.schema["heure_utc"] == DATETIME_UTC and g["intensite_conso"].to_list() == [20.0]


def test_arrondis_de_l_export():
    assert carbone.arrondir({"moyenne_ponderee": 18.35946, "part_heures_sous_seuil_fond": 0.528123,
                             "emissions_directes_mt": 10.01823}) == {
        "moyenne_ponderee": 18.3595, "part_heures_sous_seuil_fond": 0.5281, "emissions_directes_mt": 10.018}
    # double arrondi évité : 20,14978 g → 20,1498 (export) → 20,1 (texte), pas 20,150 → 20,2
    assert carbone.arrondir({"moyenne_ponderee": 20.14978})["moyenne_ponderee"] == 20.1498
    assert carbone._valeur(20.1498, "gCO2eq/kWh")["valeur"] == 20.1


def test_chiffres_calcules_au_schema_du_referentiel():
    t = table_2025(taux_co2=18.36)
    c = json.loads(_dumps(carbone.construire_carbone(t, ges_constante(t, 20.15), {})))
    saisis = {"intensite_prod_rte_2025": {"valeur": 19.6, "unite": "gCO2eq/kWh", "page": "p. 104",
                                          "source": "rte-be2025"}}
    calc = carbone.chiffres_calcules(c, saisis)
    attendus = {f"carbone_{s}_{k}_2025" for s in ("prod", "conso") for k in ("moyenne", "max", "part_sous_15")}
    attendus |= {f"carbone_prod_{k}_2025" for k in ("hiver", "ete", "mh_max", "mh_min")}
    assert set(calc) == attendus  # 2022 et 2024 absentes des données : pas de chiffre
    assert calc["carbone_prod_moyenne_2025"]["valeur"] == 18.4
    assert calc["carbone_prod_moyenne_2025"]["unite"] == "gCO2eq/kWh"
    assert calc["carbone_prod_moyenne_2025"]["grandeur"] == "intensite_moyenne"
    assert calc["carbone_conso_moyenne_2025"]["valeur"] == 20.2  # 20,15 → 20,2 (au plus loin de zéro)
    assert calc["carbone_prod_part_sous_15_2025"]["valeur"] == 0 and calc["carbone_prod_part_sous_15_2025"]["unite"] == "%"
    rec = calc["carbone_prod_moyenne_2025"]["recoupements"][0]
    assert rec["independant"] is False and "19,6" in rec["valeur"]
    assert "MOYENNE" in calc["carbone_prod_moyenne_2025"]["note"]  # jamais sans son adjectif
    vide = chiffres.Referentiel(sources={"rte-be2025": {"editeur": "RTE", "titre": "BE", "date_publication": "2026-03-01",
                                                       "url": "https://exemple"}}, chiffres={})
    fusion = chiffres.fusionner(vide, {carbone.SOURCE_CARBONE: carbone.source_carbone("2026-11-26")}, calc)
    assert chiffres.valider(fusion) == []
    assert all(v["confiance"] != "A" for v in calc.values())


def test_seuil_de_fond_egal_au_referentiel():
    ref = chiffres.charger().chiffres
    assert carbone.SEUIL_FOND_G == ref["intensite_fond_rte"]["valeur"]
    for serie, refs in carbone.REFERENCES_RTE.items():
        for cle in refs.values():
            assert ref[cle]["grandeur"] == "intensite_moyenne" and ref[cle]["unite"] == carbone.UNITE


def test_controle_global_des_chiffres_calcules(tmp_path):
    """Un chiffre calculé d'une source qu'aucun contrôle ne couvre (ou sans source) fait échouer `pc check`."""
    from pc.check import controle_chiffres_calcules_couverts

    def ecrire(chiffres_):
        (tmp_path / "chiffres.json").write_text(json.dumps({"chiffres": chiffres_}), encoding="utf-8")
        return controle_chiffres_calcules_couverts(tmp_path)

    ok = {"a": {"produit_par": "pc build", "source": {"cle": "pdc-quand"}},
          "b": {"produit_par": "pc build", "source": {"cle": carbone.SOURCE_CARBONE}},
          "c": {"source": {"cle": "rte-be2025"}}}  # saisi : hors du contrôle
    assert ecrire(ok).statut == "OK"
    r = ecrire({**ok, "d": {"produit_par": "pc build", "source": {"cle": "pdc-entsoe"}},
                "e": {"produit_par": "pc build"}})
    assert r.statut == "ÉCHEC" and sum("sans contrôle" in ligne for ligne in r.lignes) == 2
