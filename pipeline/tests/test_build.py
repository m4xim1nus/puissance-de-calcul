"""Tests sur données synthétiques, sans réseau : normalisation éCO2mix, agrégation horaire, prix."""

from datetime import datetime, timedelta, timezone

import polars as pl
import pytest

from pc import build
from pc.build import (COLONNES_MW, caster_colonnes, heures_negatives, mw_vers_mwh, normaliser_eco2mix,
                      prix_depuis_json, prix_horaire, vers_horaire)

UTC = timezone.utc


def brut(lignes: list[tuple], nature: str = "Données définitives", texte: tuple = ()) -> pl.DataFrame:
    """Lignes brutes façon export ODRÉ : (heure locale déclarée, instant UTC, consommation[, nucléaire]).

    Les autres filières valent 0 ; les colonnes de `texte` sont typées `text` comme chez ODRÉ.
    """
    data = {
        "perimetre": ["France"] * len(lignes),
        "nature": [nature] * len(lignes),
        "date": [t.strftime("%Y-%m-%d") for _, t, *_ in lignes],
        "heure": [h for h, *_ in lignes],
        "date_heure": [t for _, t, *_ in lignes],
        "consommation": [c for _, _, c, *_ in lignes],
        "nucleaire": [r[3] if len(r) > 3 else 0 for r in lignes],
        "taux_co2": [20] * len(lignes),
    }
    for c in COLONNES_MW:
        data.setdefault(c, [0] * len(lignes))
    df = pl.DataFrame(data).with_columns(pl.col("date_heure").cast(pl.Datetime("ms", "UTC")))
    return df.with_columns([pl.col(c).cast(pl.Utf8) for c in texte])


def u(*a) -> datetime:
    return datetime(*a, tzinfo=UTC)


# --------------------------------------------------------------------------
# Cast des colonnes texte
# --------------------------------------------------------------------------


def test_cast_colonnes_texte():
    df = pl.DataFrame({"gaz_cogen": ["172", "ND", " 5 ", "", None], "nucleaire": [1, 2, 3, 4, 5]})
    out = caster_colonnes(df, ["gaz_cogen", "nucleaire", "absente"])
    assert out.schema["gaz_cogen"] == pl.Float64 and out.schema["nucleaire"] == pl.Float64
    assert out["gaz_cogen"].to_list() == [172.0, None, 5.0, None, None]
    assert out["absente"].null_count() == 5


def test_cast_refuse_valeur_inattendue():
    with pytest.raises(Exception):
        caster_colonnes(pl.DataFrame({"gaz_cogen": ["172", "douze"]}), ["gaz_cogen"])


def test_normalisation_caste_les_colonnes_texte():
    df = brut([("01:00", u(2024, 1, 1, 0, 0), 50000), ("01:30", u(2024, 1, 1, 0, 30), 51000)],
              texte=("gaz_cogen", "ech_comm_allemagne_belgique"))
    df = df.with_columns(pl.Series("gaz_cogen", ["ND", "120"]))
    n, _ = normaliser_eco2mix(df)
    assert n.schema["gaz_cogen"] == pl.Float64
    assert n["gaz_cogen"].to_list() == [None, 120.0]


# --------------------------------------------------------------------------
# Normalisation : lignes vides, pas, heure d'été
# --------------------------------------------------------------------------


def test_lignes_quart_heure_et_vides_ecartees():
    df = brut([("01:00", u(2024, 1, 1, 0, 0), 50000), ("01:15", u(2024, 1, 1, 0, 15), 49000),
               ("01:30", u(2024, 1, 1, 0, 30), 51000), ("01:45", u(2024, 1, 1, 0, 45), None)])
    n, rapport = normaliser_eco2mix(df)
    assert n["ts_utc"].dt.minute().to_list() == [0, 30]
    assert rapport["lignes_vides"] == 1 and rapport["lignes_hors_pas"] == 1
    assert n["nature"].unique().to_list() == ["definitif"] and n["pas_min"].unique().to_list() == [30]


def test_dedoublonnage_heure_ete():
    # 2024-03-31 : 02:00 et 02:30 locales n'existent pas ; ODRÉ les met au même instant UTC
    # que 03:00 et 03:30. On garde la ligne dont l'heure locale est cohérente avec l'UTC.
    df = brut([
        ("01:30", u(2024, 3, 31, 0, 30), 47367),
        ("02:00", u(2024, 3, 31, 1, 0), 99999),  # fantôme
        ("03:00", u(2024, 3, 31, 1, 0), 46662),
        ("03:30", u(2024, 3, 31, 1, 30), 47346),
        ("02:30", u(2024, 3, 31, 1, 30), 88888),  # fantôme, après la vraie ligne
    ])
    n, rapport = normaliser_eco2mix(df)
    assert rapport["doublons_utc"] == 2
    assert n["ts_utc"].is_unique().all()
    assert n["consommation"].to_list() == [47367, 46662, 47346]


def test_temps_reel_au_quart_heure():
    df = brut([("12:00", u(2026, 10, 1, 10, 0), 1), ("12:15", u(2026, 10, 1, 10, 15), 2)],
              nature="Données temps réel")
    n, _ = normaliser_eco2mix(df)
    assert n["nature"].to_list() == ["temps_reel"] * 2 and n["pas_min"].to_list() == [15, 15]


def test_nature_inconnue_refusee():
    with pytest.raises(ValueError):
        normaliser_eco2mix(brut([("01:00", u(2024, 1, 1, 0, 0), 1)], nature="Données bizarres"))


# --------------------------------------------------------------------------
# Agrégation horaire (convention « fin de demi-heure »)
# --------------------------------------------------------------------------


def natif(points: list[tuple], nature: str = "definitif") -> pl.DataFrame:
    """Série native normalisée synthétique : (instant UTC, consommation[, production nucléaire])."""
    pas = build.PAS_MIN[nature]
    d = {"ts_utc": [p[0] for p in points], "nature": [nature] * len(points), "pas_min": [pas] * len(points),
         "taux_co2": [20.0] * len(points)}
    for c in COLONNES_MW:
        d[c] = [0.0] * len(points)
    d["consommation"] = [float(p[1]) if p[1] is not None else None for p in points]
    d["nucleaire"] = [float(p[2]) if len(p) > 2 else 0.0 for p in points]
    return pl.DataFrame(d).with_columns(pl.col("ts_utc").cast(build.DATETIME_UTC), pl.col("pas_min").cast(pl.Int32))


def test_convention_fin_de_demi_heure(monkeypatch):
    monkeypatch.setattr(build, "HORODATAGE_ECO2MIX", "fin")
    n = natif([(u(2024, 6, 1, 10, 0), 1), (u(2024, 6, 1, 10, 30), 2), (u(2024, 6, 1, 11, 0), 3),
               (u(2024, 6, 1, 11, 30), 4)])
    h = vers_horaire(n)
    val = dict(zip(h["heure_utc"].dt.hour().to_list(), h["consommation"].to_list()))
    # heure 10 UTC = [10:00, 11:00) = points 10:30 et 11:00
    assert val[10] == pytest.approx(2.5)
    # heure 9 : seul 10:00 (qui décrit 9:30-10:00) → incomplète ; heure 11 : seul 11:30 → incomplète
    assert val[9] is None and val[11] is None


def test_convention_debut_si_on_la_change(monkeypatch):
    monkeypatch.setattr(build, "HORODATAGE_ECO2MIX", "debut")
    n = natif([(u(2024, 6, 1, 10, 0), 1), (u(2024, 6, 1, 10, 30), 2), (u(2024, 6, 1, 11, 0), 3)])
    val = dict(zip(*[vers_horaire(n)[c].to_list() for c in ("heure_utc", "consommation")]))
    assert val[u(2024, 6, 1, 10)] == pytest.approx(1.5)


def test_temps_reel_quatre_quarts_fin_de_periode(monkeypatch):
    monkeypatch.setattr(build, "HORODATAGE_ECO2MIX", "fin")
    pts = [(u(2026, 10, 1, 10, 0) + timedelta(minutes=15 * i), 10 * i) for i in range(6)]  # 10:00 … 11:15
    h = vers_horaire(natif(pts, nature="temps_reel"))
    val = dict(zip(h["heure_utc"].to_list(), h["consommation"].to_list()))
    # heure 10 = points 10:15, 10:30, 10:45, 11:00 = 10, 20, 30, 40
    assert val[u(2026, 10, 1, 10)] == pytest.approx(25.0)
    assert h.filter(pl.col("heure_utc") == u(2026, 10, 1, 10))["couverture_min"].item() == 60


def test_heure_mixte_demi_heure_et_quart_heure(monkeypatch):
    # Raccord consolidé (30 min) → temps réel (15 min) dans la même heure.
    monkeypatch.setattr(build, "HORODATAGE_ECO2MIX", "fin")
    a = natif([(u(2026, 8, 31, 21, 30), 100)], nature="consolide")
    b = natif([(u(2026, 8, 31, 21, 45), 200), (u(2026, 8, 31, 22, 0), 400)], nature="temps_reel")
    h = vers_horaire(pl.concat([a, b]))
    ligne = h.filter(pl.col("heure_utc") == u(2026, 8, 31, 21)).row(0, named=True)
    assert ligne["consommation"] == pytest.approx((100 * 30 + 200 * 15 + 400 * 15) / 60)
    assert ligne["nature"] == "temps_reel"  # la moins figée des deux


def test_heure_manquante_octobre_marquee_pas_inventee(monkeypatch):
    # 2024-10-27 : les fichiers RTE sautent de 23:30 à 01:00 UTC (heure répétée absente).
    monkeypatch.setattr(build, "HORODATAGE_ECO2MIX", "fin")
    pts = [(u(2024, 10, 26, 22, 30), 1), (u(2024, 10, 26, 23, 0), 1), (u(2024, 10, 26, 23, 30), 1),
           (u(2024, 10, 27, 1, 0), 1), (u(2024, 10, 27, 1, 30), 1), (u(2024, 10, 27, 2, 0), 1)]
    h = vers_horaire(natif(pts))
    val = dict(zip(h["heure_utc"].to_list(), h["consommation"].to_list()))
    couv = dict(zip(h["heure_utc"].to_list(), h["couverture_min"].to_list()))
    assert val[u(2024, 10, 26, 22)] == 1  # 22:30 + 23:00 : complète
    assert val[u(2024, 10, 26, 23)] is None and couv[u(2024, 10, 26, 23)] == 30  # manque 00:00
    assert val[u(2024, 10, 27, 0)] is None and couv[u(2024, 10, 27, 0)] == 30  # manque 00:30
    assert val[u(2024, 10, 27, 1)] == 1


def test_taux_co2_pondere_par_la_production(monkeypatch):
    monkeypatch.setattr(build, "HORODATAGE_ECO2MIX", "fin")
    n = natif([(u(2024, 1, 1, 0, 30), 0, 10000), (u(2024, 1, 1, 1, 0), 0, 30000)])
    n = n.with_columns(pl.Series("taux_co2", [40.0, 20.0]))
    h = vers_horaire(n)
    assert h["taux_co2"].item() == pytest.approx((40 * 10000 + 20 * 30000) / 40000)  # 25, pas 30


# --------------------------------------------------------------------------
# Unités
# --------------------------------------------------------------------------


def test_conversion_mw_mwh():
    assert mw_vers_mwh(1000.0, 0.5) == 500.0
    assert mw_vers_mwh(1000.0, 1.0) == 1000.0


def test_energie_identique_natif_et_horaire(monkeypatch):
    # Σ MW × 0,5 h sur les demi-heures = Σ MW moyens horaires × 1 h.
    monkeypatch.setattr(build, "HORODATAGE_ECO2MIX", "fin")
    t0 = u(2024, 1, 1, 0, 30)
    pts = [(t0 + timedelta(minutes=30 * i), 40000 + 1000 * (i % 7)) for i in range(48)]
    n = natif(pts)
    e_natif = n.select(mw_vers_mwh(pl.col("consommation"), 0.5).sum()).item()
    h = vers_horaire(n)
    assert h["consommation"].null_count() == 0 and h.height == 24
    assert h.select(mw_vers_mwh(pl.col("consommation"), 1.0).sum()).item() == pytest.approx(e_natif)


# --------------------------------------------------------------------------
# Prix
# --------------------------------------------------------------------------


def doc_prix(debut: datetime, pas_min: int, prix: list[float]) -> dict:
    t0 = int(debut.timestamp())
    return {"unix_seconds": [t0 + 60 * pas_min * i for i in range(len(prix))], "price": prix}


def test_prix_pas_natif_et_horaire():
    avant = doc_prix(u(2025, 9, 30, 20), 60, [10.0, -5.0])  # 20:00 et 21:00 UTC, horaires
    apres = doc_prix(u(2025, 9, 30, 22), 15, [-10.0, 5.0, 5.0, 5.0, -1.0, -1.0, -1.0, 2.0])
    p = prix_depuis_json([avant, apres])
    assert p["pas_min"].to_list() == [60, 60] + [15] * 8
    h = prix_horaire(p)
    val = dict(zip(h["heure_utc"].to_list(), h["prix_eur_mwh"].to_list()))
    assert val[u(2025, 9, 30, 21)] == -5.0
    assert val[u(2025, 9, 30, 22)] == pytest.approx(1.25)  # un quart d'heure négatif, heure positive
    assert val[u(2025, 9, 30, 23)] == pytest.approx(-0.25)
    qneg = dict(zip(h["heure_utc"].to_list(), h["quarts_negatifs"].to_list()))
    assert qneg[u(2025, 9, 30, 22)] == 1 and qneg[u(2025, 9, 30, 23)] == 3


def test_comptage_heures_negatives_avec_quarts_heure():
    avant = doc_prix(u(2025, 9, 30, 20), 60, [10.0, -5.0])
    apres = doc_prix(u(2025, 9, 30, 22), 15, [-10.0, 5.0, 5.0, 5.0, -1.0, -1.0, -1.0, 2.0])
    h = prix_horaire(prix_depuis_json([avant, apres]))
    # -5 (horaire) et -0,25 (moyenne de quarts) comptent ; 1,25 non malgré un quart négatif.
    assert heures_negatives(h) == {2025: 2}


def test_heure_prix_incomplete_videe():
    p = prix_depuis_json([doc_prix(u(2025, 10, 1, 10), 15, [1.0, 2.0, 3.0])])  # 3 quarts sur 4
    assert prix_horaire(p)["prix_eur_mwh"].to_list() == [None]


def test_annee_des_heures_negatives_en_heure_de_paris():
    # 2023-12-31 23:00 UTC = 2024-01-01 00:00 à Paris : compte pour 2024.
    h = prix_horaire(prix_depuis_json([doc_prix(u(2023, 12, 31, 22), 60, [-1.0, -2.0])]))
    assert heures_negatives(h) == {2023: 1, 2024: 1}
