"""Tests synthétiques, sans réseau : reconstruction de la disponibilité nucléaire depuis REMIT (pc/remit.py)."""

from datetime import datetime, timezone

import polars as pl
import pytest

from pc import remit

UTC = timezone.utc
T0 = datetime(2024, 1, 10, 0, tzinfo=UTC)
T1 = datetime(2024, 1, 11, 0, tzinfo=UTC)


def u(*a) -> datetime:
    return datetime(*a, tzinfo=UTC)


def brut(lignes: list[dict]) -> pl.DataFrame:
    """Lignes façon `remit.fusionner` : une par version d'événement, dates déjà en UTC."""
    base = {"statut": "Active", "version": 1, "tranche": "BUGEY 2", "filiere": "Nucléaire", "type": "Fortuite",
            "pmax": 910.0, "pdispo": 0.0, "publication": u(2024, 1, 1), "info": None, "fichier": "historique"}
    rows = []
    for i, l in enumerate(lignes):
        r = {**base, "id": f"05470_EDF_T_{i:08d}", **l}
        rows.append(r)
    return pl.DataFrame(rows, schema={
        "statut": pl.Utf8, "id": pl.Utf8, "version": pl.Int32, "tranche": pl.Utf8, "filiere": pl.Utf8,
        "debut": pl.Datetime("us", "UTC"), "fin": pl.Datetime("us", "UTC"), "type": pl.Utf8, "pmax": pl.Float64,
        "pdispo": pl.Float64, "publication": pl.Datetime("us", "UTC"), "info": pl.Utf8, "fichier": pl.Utf8})


def dispo(lignes: list[dict], debut=T0, fin=T1, periodes=None) -> pl.DataFrame:
    ev = remit.evenements_nucleaires(brut(lignes))
    return remit.disponible_horaire(ev, debut, fin, {} if periodes is None else periodes)


def valeur(h: pl.DataFrame, heure: datetime, tranche: str = "BUGEY 2", col: str = "dispo") -> float:
    return h.filter((pl.col("tranche") == tranche) & (pl.col("heure_utc") == heure))[col].item()


# --------------------------------------------------------------------------
# Superposition, versions, statuts
# --------------------------------------------------------------------------


def test_hors_evenement_puissance_maximale_et_moyenne_exacte():
    # arrêt de 10:30 à 11:00 : l'heure 10 vaut la moitié de la puissance maximale
    h = dispo([{"debut": u(2024, 1, 10, 10, 30), "fin": u(2024, 1, 10, 11, 0), "pdispo": 0.0}])
    assert valeur(h, u(2024, 1, 10, 9)) == 910
    assert valeur(h, u(2024, 1, 10, 10)) == pytest.approx(455)
    assert valeur(h, u(2024, 1, 10, 11)) == 910
    assert h.height == 24


def test_superposition_puissance_disponible_minimale():
    h = dispo([
        {"debut": u(2024, 1, 10, 8), "fin": u(2024, 1, 10, 12), "pdispo": 600.0, "type": "Planifiée"},
        {"debut": u(2024, 1, 10, 10), "fin": u(2024, 1, 10, 14), "pdispo": 300.0},
    ])
    assert valeur(h, u(2024, 1, 10, 9)) == 600
    assert valeur(h, u(2024, 1, 10, 11)) == 300  # règle d'EDF : le minimum, pas la somme des baisses
    assert valeur(h, u(2024, 1, 10, 13)) == 300
    assert valeur(h, u(2024, 1, 10, 14)) == 910


def test_derniere_version_seule():
    idt = "05470_EDF_T_X"
    h = dispo([
        {"id": idt, "version": 1, "statut": "Inactive", "debut": u(2024, 1, 10, 0), "fin": u(2024, 1, 10, 12),
         "pdispo": 0.0},
        {"id": idt, "version": 2, "statut": "Active", "debut": u(2024, 1, 10, 6), "fin": u(2024, 1, 10, 8),
         "pdispo": 500.0},
    ])
    assert valeur(h, u(2024, 1, 10, 3)) == 910
    assert valeur(h, u(2024, 1, 10, 7)) == 500


@pytest.mark.parametrize("statut", ["Annulée", "Supprimée"])
def test_derniere_version_annulee_ou_supprimee_ecarte_l_evenement(statut):
    idt = "05470_EDF_T_X"
    h = dispo([
        {"id": idt, "version": 1, "statut": "Inactive", "debut": u(2024, 1, 10, 0), "fin": u(2024, 1, 10, 12)},
        {"id": idt, "version": 2, "statut": statut, "debut": u(2024, 1, 10, 0), "fin": u(2024, 1, 10, 12)},
        {"debut": u(2024, 1, 10, 20), "fin": u(2024, 1, 10, 21), "pdispo": 100.0},  # garde la tranche connue
    ])
    assert valeur(h, u(2024, 1, 10, 5)) == 910
    assert valeur(h, u(2024, 1, 10, 20)) == 100


def test_suppression_ecartee(monkeypatch):
    idt = "05470_EDF_T_X"
    monkeypatch.setattr(remit, "SUPPRESSIONS_ECARTEES", {idt: "test"})
    h = dispo([
        {"id": idt, "version": 1, "statut": "Inactive", "debut": u(2024, 1, 10, 0), "fin": u(2024, 1, 10, 12)},
        {"id": idt, "version": 2, "statut": "Supprimée", "debut": u(2024, 1, 10, 0), "fin": u(2024, 1, 10, 12)},
    ])
    assert valeur(h, u(2024, 1, 10, 5)) == 0


def test_puissance_disponible_bornee_a_la_puissance_maximale():
    h = dispo([{"debut": u(2024, 1, 10, 5), "fin": u(2024, 1, 10, 6), "pdispo": 960.0}])  # « maintenue à PMD »
    assert valeur(h, u(2024, 1, 10, 5)) == 910


def test_chroniques_luminus_et_autres_filieres_ignorees():
    h = dispo([
        {"type": "Chronique PMIN", "debut": u(2024, 1, 10, 0), "fin": u(2024, 1, 11, 0), "pmax": 0.0, "pdispo": 0.0},
        {"type": "Chronique aFRR", "debut": u(2024, 1, 10, 0), "fin": u(2024, 1, 11, 0), "pmax": 0.0, "pdispo": 0.0},
        {"id": "10000_LUM_T_1", "tranche": "SERAING TV", "filiere": "Gaz fossile", "debut": u(2024, 1, 10, 0),
         "fin": u(2024, 1, 11, 0)},
        {"filiere": "Réservoir hydraulique", "tranche": "GRAND MAISON 1", "debut": u(2024, 1, 10, 0),
         "fin": u(2024, 1, 11, 0)},
        {"debut": u(2024, 1, 10, 23), "fin": u(2024, 1, 11, 0), "pdispo": 0.0},
    ])
    assert set(h["tranche"].unique()) == {"BUGEY 2"}
    assert valeur(h, u(2024, 1, 10, 5)) == 910
    assert valeur(h, u(2024, 1, 10, 23)) == 0


def test_tranche_nucleaire_inconnue_refusee():
    with pytest.raises(ValueError, match="inconnues"):
        remit.evenements_nucleaires(brut([{"tranche": "BUGEY 9", "debut": T0, "fin": T1}]))


# --------------------------------------------------------------------------
# Tranches sans événement, périodes d'exploitation
# --------------------------------------------------------------------------


def test_periodes_d_exploitation():
    # arrêt définitif à 23:30 heure de Paris (22:30 UTC en hiver) ; mise en service à 13:50 heure de Paris
    periodes = {"FESSENHEIM 2": (None, datetime(2024, 1, 10, 23, 30)),
                "FLAMANVILLE 3": (datetime(2024, 1, 10, 13, 50), None)}
    h = dispo([
        {"tranche": "FESSENHEIM 2", "pmax": 880.0, "debut": u(2024, 1, 10, 1), "fin": u(2024, 1, 10, 2),
         "pdispo": 0.0},
        {"tranche": "FLAMANVILLE 3", "pmax": 1620.0, "debut": u(2024, 1, 10, 12, 50), "fin": u(2024, 1, 10, 18),
         "pdispo": 0.0},
    ], periodes=periodes)
    f = h.filter(pl.col("tranche") == "FESSENHEIM 2")
    assert f["heure_utc"].max() == u(2024, 1, 10, 22)  # absente ensuite (pas de pleine puissance fantôme)
    assert valeur(h, u(2024, 1, 10, 22), "FESSENHEIM 2") == 440
    assert valeur(h, u(2024, 1, 10, 22), "FESSENHEIM 2", "pmax") == 440  # demi-heure en exploitation
    f3 = h.filter(pl.col("tranche") == "FLAMANVILLE 3")
    assert f3["heure_utc"].min() == u(2024, 1, 10, 12)  # rien avant son premier événement
    assert valeur(h, u(2024, 1, 10, 12), "FLAMANVILLE 3", "pmax") == pytest.approx(1620 / 6)
    assert valeur(h, u(2024, 1, 10, 20), "FLAMANVILLE 3") == 1620
    nat = remit.national(h)
    assert nat.filter(pl.col("heure_utc") == u(2024, 1, 10, 23))["nucleaire_disponible"].item() == 1620


def test_puissance_maximale_variable():
    h = dispo([
        {"tranche": "FLAMANVILLE 3", "pmax": 1620.0, "debut": u(2024, 1, 10, 2), "fin": u(2024, 1, 10, 3)},
        {"tranche": "FLAMANVILLE 3", "pmax": 1600.0, "debut": u(2024, 1, 10, 12), "fin": u(2024, 1, 10, 13)},
    ])
    assert valeur(h, u(2024, 1, 10, 6), "FLAMANVILLE 3") == 1620
    assert valeur(h, u(2024, 1, 10, 20), "FLAMANVILLE 3") == 1600


def test_taux_annuels_et_exclusion():
    h = dispo([
        {"debut": u(2024, 1, 10, 0), "fin": u(2024, 1, 10, 12), "pdispo": 0.0},
        {"tranche": "FLAMANVILLE 3", "pmax": 1620.0, "debut": u(2024, 1, 10, 0), "fin": u(2024, 1, 11, 0)},
    ])
    t = remit.taux_annuels(h, {"FLAMANVILLE 3"})
    assert t["taux"].item() == pytest.approx(0.5)


# --------------------------------------------------------------------------
# Fuseau, changements d'heure
# --------------------------------------------------------------------------


def conv(*a) -> datetime:
    return pl.select(remit.local_vers_utc(pl.lit(datetime(*a)))).item()


def test_heure_de_paris_hiver_ete():
    assert conv(2024, 1, 10, 12, 0) == u(2024, 1, 10, 11, 0)
    assert conv(2024, 7, 10, 12, 0) == u(2024, 7, 10, 10, 0)


def test_passage_heure_ete_heure_inexistante():
    # 30/03/2025 : 02:30 n'existe pas à Paris ; lue avec le décalage d'hiver = 01:30 UTC (= 03:30 CEST)
    assert conv(2025, 3, 30, 2, 30) == u(2025, 3, 30, 1, 30)
    assert conv(2025, 3, 30, 3, 0) == u(2025, 3, 30, 1, 0)


def test_passage_heure_hiver_heure_ambigue():
    # 26/10/2025 : 02:30 existe deux fois ; première occurrence (heure d'été) = 00:30 UTC
    assert conv(2025, 10, 26, 2, 30) == u(2025, 10, 26, 0, 30)
    assert conv(2025, 10, 26, 3, 0) == u(2025, 10, 26, 2, 0)


def test_evenement_a_cheval_sur_le_changement_d_heure():
    # arrêt de 01:00 à 04:00 heure de Paris le 30/03/2025 : 2 heures réelles (00:00 → 02:00 UTC)
    d, f = conv(2025, 3, 30, 1, 0), conv(2025, 3, 30, 4, 0)
    h = dispo([{"debut": d, "fin": f, "pdispo": 0.0}], u(2025, 3, 29, 22), u(2025, 3, 30, 4))
    assert h.filter(pl.col("dispo") == 0)["heure_utc"].to_list() == [u(2025, 3, 30, 0), u(2025, 3, 30, 1)]


# --------------------------------------------------------------------------
# Lecture des fichiers bruts, fusion, jonction
# --------------------------------------------------------------------------

ENTETE_HIST = ";".join(remit.ENTETES)
ENTETE_COUR = ";".join(f'"{e}"' if " " in e else e for e in remit.ENTETES)


def ecrire(chemin, lignes: list[str]) -> None:
    chemin.write_bytes(("\r\n".join(lignes) + "\r\n").encode("latin-1"))


def test_lecture_deux_formats_et_fusion(tmp_path):
    h = tmp_path / "h.csv"
    c = tmp_path / "c.csv"
    ecrire(h, [ENTETE_HIST,
               "Active;05470_EDF_T_1;1;BUGEY 2;Nucléaire;10/01/2024 08:00;10/01/2024 12:00;Fortuite;Défaillance;;910;0;10/01/2024 08:10",
               "Active;05470_EDF_T_2;3;BUGEY 3;Nucléaire;15/07/2024 08:00;15/07/2024 09:00;Planifiée;x;;910;455,5;14/07/2024 08:10"])
    ecrire(c, [ENTETE_COUR,
               'Inactive;05470_EDF_T_1;1;"BUGEY 2";Nucléaire;"2024-01-10 08:00:00";"2024-01-10 12:00:00";Fortuite;x;;910,00;0,00;"2024-01-10 08:10:00"',
               'Active;05470_EDF_T_1;2;"BUGEY 2";Nucléaire;"2024-01-10 08:00:00";"2024-01-10 10:00:00";Fortuite;x;;910,00;300,00;"2024-01-10 09:00:00"'])
    lh, lc = remit.lire_csv(h, "historique"), remit.lire_csv(c, "courante")
    assert lh["debut"].to_list() == [u(2024, 1, 10, 7), u(2024, 7, 15, 6)]
    assert lh["pdispo"].to_list() == [0.0, 455.5]
    assert lc["debut"][0] == u(2024, 1, 10, 7)
    f = remit.fusionner(lh, lc)
    assert f.height == 3
    assert f.filter((pl.col("id") == "05470_EDF_T_1") & (pl.col("version") == 1))["statut"].item() == "Inactive"
    ev = remit.evenements_nucleaires(f)
    assert ev.filter(pl.col("id") == "05470_EDF_T_1")["pdispo"].item() == 300
    b = remit.bornes_fiables(lh, lc, u(2024, 7, 20, 10, 30))
    assert b["fin_historique"] == u(2024, 7, 14, 6, 10)
    assert b["horizon"] == u(2024, 7, 20, 10)
    assert b["trou"] is False  # la liste courante remonte au 10/01, avant l'export de l'historique


def test_trou_entre_historique_et_liste_courante():
    h = brut([{"debut": u(2024, 1, 1), "fin": u(2024, 1, 2), "publication": u(2024, 1, 5)}])
    c = brut([{"debut": u(2024, 3, 1), "fin": u(2024, 3, 2), "publication": u(2024, 3, 5)}])
    h = h.with_columns(pl.col("publication").dt.replace_time_zone(None).alias("publication_local"))
    assert remit.bornes_fiables(h, c, None)["trou"] is True


def test_entete_inattendu_refuse(tmp_path):
    p = tmp_path / "x.csv"
    ecrire(p, ["Status;Identifiant;Autre", "Active;1;2"])
    with pytest.raises(ValueError, match="en-têtes"):
        remit.lire_csv(p, "historique")
