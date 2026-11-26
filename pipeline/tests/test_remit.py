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


# --------------------------------------------------------------------------
# Arrêts et baisses pour modulation (MOTIF_MODULATION) et disponibilité réintégrée
# --------------------------------------------------------------------------

#: Textes réels du jeu d'EDF (abrégés), classés à la main (rapport du 26/11/2026).
MODULATION_OUI = [
    "Le placement et la durée de cet arrêt pour modulation seront réinterrogés et la tranche sera redémarrée si les "
    "conditions économiques le justifient -------- The planning and duration of this unavailability for modulation "
    "supply will be reassessed",
    "Le placement de cette baisse pour modulation est susceptible d?être modifié si les conditions économiques le "
    "justifient. La durée indiquée est la durée minimale de palier.",
    "Le placement et la durée de ce palier pour modulation seront réinterrogés",
    "The planning and duration of this unavailability for modulation supply will be reassessed if economically "
    "justified.",  # anglais seul
    "The duration of this limitation for power modulation  may be reassessed for economic reasons",
    "Baisse avant arrêt pour modulation Baisse à 600 MW : 30min",
    "Informations complémentaires :  Le placement de cette modulation sera réinterrogé",
    "Arrêt pour économie combustible. Le placement et la durée de cet arrêt pour modulation seront réinterrogés",
    "baisse pour modulation  ------  unavaiability for modulation",
]
MODULATION_NON = [
    "Tranche en prolongation de campagne ----- Ongoing stretch",
    "Arrêt pour économie combustible ------------ Fuel saving outage",
    "Essai à puissance stable. Le niveau de puissance pourra être réinterrogé si les conditions économiques le "
    "justifient. -------- Test at stable power.",
    "Le placement et la durée de cet arrêt seront réinterrogés et la tranche sera redémarrée si les conditions "
    "économiques le justifient",  # même gabarit, sans le mot : non compté (cas examinés, 2019-2021)
    "Pour plus d'informations / for more information : https://www.edf.fr/groupe-edf/qui-sommes-nous/activites/"
    "optimisation-et-trading/listes-des-indisponibilites-et-des-messages",
    "Le placement et la durée de cette baisse pour contraintes environnementales seront réinterrogés",
    "Modulations de puissance",  # pas le mot entier « modulation »
    "",
]


@pytest.mark.parametrize("texte", MODULATION_OUI)
def test_modulation_reconnue_francais_et_anglais(texte):
    assert pl.select(remit.est_modulation(pl.lit(texte))).item() is True


@pytest.mark.parametrize("texte", MODULATION_NON)
def test_cas_ambigus_non_comptes(texte):
    assert pl.select(remit.est_modulation(pl.lit(texte))).item() is False


def test_mention_dans_une_version_anterieure():
    """Règle 2 : texte effacé à la mise à jour → hérité ; autre cause donnée → pas hérité."""
    lignes = []
    for k, (dernier, attendu) in enumerate([
            ("", True), (None, True), ("Pour plus d'informations / for more information : https://x", True),
            ("La remontée se fera en 16 heures", True), ("Indisponibilité fortuite -------- Forced unavailability.", False),
            ("Arrêt pour économie de combustible -------- Fuel saving outage", False)]):
        idt = f"05470_EDF_T_M{k}"
        base = {"id": idt, "type": "Planifiée", "debut": u(2024, 1, 10, k), "fin": u(2024, 1, 10, k + 1)}
        lignes += [{**base, "version": 1, "statut": "Inactive", "info": "arrêt pour modulation"},
                   {**base, "version": 2, "statut": "Active", "info": dernier, "attendu": attendu}]
    attendus = {l["id"]: l.pop("attendu") for l in lignes if "attendu" in l}
    ev = remit.evenements_nucleaires(brut(lignes))
    obtenu = dict(ev.select("id", "modulation").iter_rows())
    assert obtenu == attendus
    assert ev.filter(pl.col("modulation"))["modulation_par"].unique().to_list() == ["version antérieure"]


def test_disponibilite_reintegree_memes_regles():
    """Un arrêt pour modulation qui chevauche une maintenance : le réintégré garde la maintenance
    (minimum des autres événements), la puissance maximale et les heures hors arrêt sont identiques."""
    lignes = [
        {"debut": u(2024, 1, 10, 2), "fin": u(2024, 1, 10, 10), "pdispo": 0.0, "type": "Planifiée",
         "info": "Le placement et la durée de cet arrêt pour modulation seront réinterrogés"},
        {"debut": u(2024, 1, 10, 6), "fin": u(2024, 1, 10, 12), "pdispo": 400.0, "type": "Planifiée",
         "info": "Maintenance"},
        {"tranche": "BUGEY 3", "debut": u(2024, 1, 10, 3, 30), "fin": u(2024, 1, 10, 4), "pdispo": 455.0,
         "type": "Planifiée", "info": "baisse pour modulation"},
    ]
    ev = remit.evenements_nucleaires(brut(lignes))
    assert ev["modulation"].sum() == 2
    d = remit.disponible_horaire(ev, T0, T1, {})
    r = remit.disponible_horaire(ev, T0, T1, {}, reintegrer_modulation="courts")
    assert valeur(d, u(2024, 1, 10, 3)) == 0 and valeur(r, u(2024, 1, 10, 3)) == 910
    assert valeur(d, u(2024, 1, 10, 7)) == 0 and valeur(r, u(2024, 1, 10, 7)) == 400  # la maintenance reste
    assert valeur(d, u(2024, 1, 10, 11)) == 400 and valeur(r, u(2024, 1, 10, 11)) == 400
    assert valeur(d, u(2024, 1, 10, 3), "BUGEY 3") == pytest.approx(682.5)  # demi-heure à 455 MW
    assert valeur(r, u(2024, 1, 10, 3), "BUGEY 3") == 910
    j = d.join(r, on=["tranche", "heure_utc"], suffix="_r")
    assert (j["dispo_r"] >= j["dispo"]).all() and (j["pmax_r"] == j["pmax"]).all()
    hors = j.filter(~pl.col("heure_utc").is_between(u(2024, 1, 10, 2), u(2024, 1, 10, 9)))
    assert (hors["dispo_r"] == hors["dispo"]).all()


def test_arrets_courts_et_longs():
    """Courts : moins de 7 jours et aucune version ne parle de combustible ; seuls eux sont réintégrés
    par « courts », tous par « tous ». La clause de redémarrage ne suffit pas à rendre un arrêt court."""
    clause = ("Le placement et la durée de cet arrêt pour modulation seront réinterrogés et la tranche sera "
              "redémarrée si les conditions économiques le justifient")
    lignes = [
        # 2 jours, avec la clause : court
        {"tranche": "BUGEY 2", "debut": u(2024, 1, 1), "fin": u(2024, 1, 3), "type": "Planifiée", "info": clause},
        # 6 jours 23 h, sans la clause : court
        {"tranche": "BUGEY 3", "debut": u(2024, 1, 1), "fin": u(2024, 1, 7, 23), "type": "Planifiée",
         "info": "baisse pour modulation", "pdispo": 400.0},
        # exactement 7 jours, avec la clause : long
        {"tranche": "BUGEY 4", "debut": u(2024, 1, 1), "fin": u(2024, 1, 8), "type": "Planifiée", "info": clause},
        # 2 jours mais « économie combustible » : long (gestion du combustible)
        {"tranche": "BUGEY 5", "debut": u(2024, 1, 1), "fin": u(2024, 1, 3), "type": "Planifiée",
         "info": "Arrêt pour économie combustible. " + clause},
        # deux mois, texte effacé ensuite (règle 2) : long
        {"id": "05470_EDF_T_L1", "version": 1, "statut": "Inactive", "tranche": "CHOOZ 1", "debut": u(2024, 1, 1),
         "fin": u(2024, 3, 1), "type": "Planifiée", "info": "arrêt pour modulation", "pmax": 1500.0},
        {"id": "05470_EDF_T_L1", "version": 2, "tranche": "CHOOZ 1", "debut": u(2024, 1, 1), "fin": u(2024, 3, 1),
         "type": "Planifiée", "info": None, "pmax": 1500.0},
    ]
    ev = remit.evenements_nucleaires(brut(lignes)).sort("tranche")
    assert dict(ev.select("tranche", "modulation_courte").iter_rows()) == {
        "BUGEY 2": True, "BUGEY 3": True, "BUGEY 4": False, "BUGEY 5": False, "CHOOZ 1": False}
    assert ev["modulation"].all()
    h = u(2024, 1, 2)
    d = remit.disponible_horaire(ev, u(2024, 1, 1), u(2024, 1, 4), {})
    c = remit.disponible_horaire(ev, u(2024, 1, 1), u(2024, 1, 4), {}, reintegrer_modulation="courts")
    t = remit.disponible_horaire(ev, u(2024, 1, 1), u(2024, 1, 4), {}, reintegrer_modulation="tous")
    for tranche, attendu_c in (("BUGEY 2", 910), ("BUGEY 3", 910), ("BUGEY 4", 0), ("BUGEY 5", 0), ("CHOOZ 1", 0)):
        assert valeur(d, h, tranche) < valeur(t, h, tranche)
        assert valeur(c, h, tranche) == attendu_c
    with pytest.raises(ValueError):
        remit.disponible_horaire(ev, u(2024, 1, 1), u(2024, 1, 2), {}, reintegrer_modulation=True)
