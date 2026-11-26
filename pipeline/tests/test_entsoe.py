"""ENTSO-E : lecture XML, normalisation, vue horaire, jeton et contrôles, sur données synthétiques
(sans réseau ni jeton)."""

import gzip
from datetime import date, datetime, timedelta, timezone

import polars as pl
import pytest

from pc import check_entsoe, entsoe, entsoe_derive, sources

UTC = timezone.utc
NS = "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3"


def u(*a) -> datetime:
    return datetime(*a, tzinfo=UTC)


def periode(debut: str, fin: str, res: str, points: dict) -> str:
    pts = "".join(f"<Point><position>{p}</position><{'price.amount' if isinstance(v, tuple) else 'quantity'}>"
                  f"{v[0] if isinstance(v, tuple) else v}</{'price.amount' if isinstance(v, tuple) else 'quantity'}>"
                  f"</Point>" for p, v in points.items())
    return (f"<Period><timeInterval><start>{debut}</start><end>{fin}</end></timeInterval>"
            f"<resolution>{res}</resolution>{pts}</Period>")


def serie(periodes: list[str], champs: dict | None = None, psr: str | None = None, curve: str = "A03") -> str:
    ch = "".join(f"<{k}>{v}</{k}>" for k, v in (champs or {}).items())
    p = f"<MktPSRType><psrType>{psr}</psrType></MktPSRType>" if psr else ""
    return f"<TimeSeries><mRID>1</mRID>{ch}{p}<curveType>{curve}</curveType>{''.join(periodes)}</TimeSeries>"


def document(type_: str, series: list[str]) -> bytes:
    return (f'<?xml version="1.0" encoding="utf-8"?><Publication_MarketDocument xmlns="{NS}"><mRID>x</mRID>'
            f"<type>{type_}</type>{''.join(series)}</Publication_MarketDocument>").encode()


MW = {"quantity_Measure_Unit.name": "MAW"}
EUR = {"currency_Unit.name": "EUR", "price_Measure_Unit.name": "MWH"}


# --------------------------------------------------------------------------
# Lecture XML
# --------------------------------------------------------------------------


def test_a03_position_omise_repete_la_precedente_jusqu_a_la_fin():
    xml = document("A65", [serie([periode("2024-03-10T23:00Z", "2024-03-11T05:00Z", "PT60M", {1: 10, 2: 20, 5: 50})],
                                 {**MW, "outBiddingZone_Domain.mRID": "10YFR-RTE------C"})])
    pts = entsoe.points(entsoe.lire_document(xml)["series"][0])
    assert [(t.hour, v, p) for t, _, v, p in pts] == [
        (23, 10, True), (0, 20, True), (1, 20, False), (2, 20, False), (3, 50, True), (4, 50, False)]


def test_a03_sans_position_1_les_premieres_restent_vides():
    xml = document("A65", [serie([periode("2024-03-10T23:00Z", "2024-03-11T03:00Z", "PT60M", {3: 30})], MW)])
    pts = entsoe.points(entsoe.lire_document(xml)["series"][0])
    assert [(t.hour, v) for t, _, v, _ in pts] == [(1, 30), (2, 30)]


def test_courbe_a01_pas_de_propagation():
    xml = document("A65", [serie([periode("2024-03-10T23:00Z", "2024-03-11T03:00Z", "PT60M", {1: 1, 3: 3})], MW,
                                 curve="A01")])
    assert len(entsoe.points(entsoe.lire_document(xml)["series"][0])) == 2


def test_resolution_mixte_dans_une_reponse():
    xml = document("A65", [serie([periode("2024-12-29T23:00Z", "2024-12-30T01:00Z", "PT60M", {1: 1, 2: 2}),
                                  periode("2024-12-30T23:00Z", "2024-12-31T00:00Z", "PT15M", {1: 5, 3: 7})], MW)])
    pts = entsoe.points(entsoe.lire_document(xml)["series"][0])
    assert [(t, pas, v) for t, pas, v, _ in pts] == [
        (u(2024, 12, 29, 23), 60, 1), (u(2024, 12, 30, 0), 60, 2),
        (u(2024, 12, 30, 23), 15, 5), (u(2024, 12, 30, 23, 15), 15, 5), (u(2024, 12, 30, 23, 30), 15, 7),
        (u(2024, 12, 30, 23, 45), 15, 7)]


def test_changement_d_heure_nombre_de_positions():
    # 30/03/2025 : jour de 23 h (22 positions après la dernière publiée à 1 → 23 au total)
    ete = document("A44", [serie([periode("2025-03-29T23:00Z", "2025-03-30T22:00Z", "PT60M", {1: (50,)})], EUR)])
    assert len(entsoe.points(entsoe.lire_document(ete)["series"][0])) == 23
    # 26/10/2025 : jour de 25 h, au quart d'heure : 100 positions
    hiver = document("A44", [serie([periode("2025-10-25T22:00Z", "2025-10-26T23:00Z", "PT15M", {1: (50,)})], EUR)])
    pts = entsoe.points(entsoe.lire_document(hiver)["series"][0])
    assert len(pts) == 100 and pts[-1][0] == u(2025, 10, 26, 22, 45)
    # une position au-delà de la Period est une erreur, pas une donnée
    faux = document("A44", [serie([periode("2025-03-29T23:00Z", "2025-03-30T22:00Z", "PT60M", {24: (1,)})], EUR)])
    with pytest.raises(ValueError):
        entsoe.lire_document(faux)


def test_acquittement_vide():
    xml = (b'<?xml version="1.0"?><Acknowledgement_MarketDocument xmlns="urn:x"><mRID>a</mRID>'
           b"<Reason><code>999</code><text>No matching data found for Data item X</text></Reason>"
           b"</Acknowledgement_MarketDocument>")
    d = entsoe.lire_document(xml)
    assert d["series"] == [] and d["vide"].startswith("No matching data found")
    assert entsoe.motif_acquittement(xml).startswith("No matching")
    assert entsoe.motif_acquittement(document("A65", [])) is None


def test_lecture_d_un_fichier_gzip(tmp_path):
    p = tmp_path / "2024.xml.gz"
    p.write_bytes(gzip.compress(document("A65", [serie([periode("2024-01-01T00:00Z", "2024-01-01T01:00Z",
                                                                  "PT15M", {1: 4})], MW)])))
    assert len(entsoe.points(entsoe.lire_document(p)["series"][0])) == 4


# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------


def test_sequence_a44_2_ecartee():
    s1 = serie([periode("2024-03-10T23:00Z", "2024-03-11T01:00Z", "PT60M", {1: (48.93,), 2: (49.33,)})],
               {**EUR, "classificationSequence_AttributeInstanceComponent.position": 1})
    s2 = serie([periode("2024-03-10T23:00Z", "2024-03-11T01:00Z", "PT15M", {1: (75,)})],
               {**EUR, "classificationSequence_AttributeInstanceComponent.position": 2})
    df, r = entsoe_derive.normaliser_document(entsoe.lire_document(document("A44", [s1, s2])), "entsoe_prix",
                                              "DE-LU", 2024)
    assert df["valeur"].to_list() == [48.93, 49.33] and r["sequences_ecartees"] == 1
    assert df["unite"].unique().to_list() == ["EUR/MWh"]


def test_sequence_sans_classement_prioritaire_cas_espagnol():
    sdac = serie([periode("2026-01-02T23:00Z", "2026-01-03T00:00Z", "PT15M", {1: (84.34,), 2: (82.79,)})], EUR)
    ida = [serie([periode("2026-01-02T23:00Z", "2026-01-03T00:00Z", "PT15M", {1: (87.0 + k,)})],
                 {**EUR, "classificationSequence_AttributeInstanceComponent.position": k}) for k in (1, 2)]
    # séquence 3 seule sur un instant non couvert par le SDAC : pas de prix SDAC, écartée
    ida3 = serie([periode("2026-01-03T11:00Z", "2026-01-03T11:15Z", "PT15M", {1: (90.0,)})],
                 {**EUR, "classificationSequence_AttributeInstanceComponent.position": 3})
    df, r = entsoe_derive.normaliser_document(entsoe.lire_document(document("A44", [sdac, *ida, ida3])),
                                              "entsoe_prix", "ES", 2026)
    assert df["valeur"].to_list() == [84.34, 82.79, 82.79, 82.79]  # A03 : 4 quarts
    assert r["sequences_ecartees"] == 3


def test_production_et_consommation_distinguees():
    p = serie([periode("2024-01-01T00:00Z", "2024-01-01T01:00Z", "PT60M", {1: 900})],
              {**MW, "inBiddingZone_Domain.mRID": "FR"}, psr="B10")
    c = serie([periode("2024-01-01T00:00Z", "2024-01-01T01:00Z", "PT60M", {1: 300})],
              {**MW, "outBiddingZone_Domain.mRID": "FR"}, psr="B10")
    df, _ = entsoe_derive.normaliser_document(entsoe.lire_document(document("A75", [p, c])), "entsoe_production",
                                              "FR", 2024)
    assert dict(df.select("sens", "valeur").iter_rows()) == {"production": 900, "consommation": 300}
    h, info = entsoe_derive.vers_horaire(df)
    assert {"production_fr_b10", "consommation_fr_b10"} <= set(h.columns)


def test_unites_refusees():
    x = document("A44", [serie([periode("2024-01-01T00:00Z", "2024-01-01T01:00Z", "PT60M", {1: (1,)})],
                               {"currency_Unit.name": "USD", "price_Measure_Unit.name": "MWH"})])
    with pytest.raises(ValueError):
        entsoe_derive.normaliser_document(entsoe.lire_document(x), "entsoe_prix", "FR", 2024)
    gbp = document("A44", [serie([periode("2019-01-01T00:00Z", "2019-01-01T01:00Z", "PT60M", {1: (60,)})],
                                 {"currency_Unit.name": "GBP", "price_Measure_Unit.name": "MWH"})])
    df, _ = entsoe_derive.normaliser_document(entsoe.lire_document(gbp), "entsoe_prix", "GB", 2019)
    assert df["unite"].to_list() == ["GBP/MWh"]


def natif(lignes: list[tuple], cle="entsoe_prix", serie_="FR", annee=2025) -> pl.DataFrame:
    """(début, pas, valeur) → table native."""
    n = len(lignes)
    return pl.DataFrame({"cle": [cle] * n, "serie": [serie_] * n, "filiere": [None] * n, "sens": [None] * n,
                         "debut_utc": [t for t, _, _ in lignes], "pas_min": [p for _, p, _ in lignes],
                         "valeur": [v for _, _, v in lignes], "publie": [True] * n,
                         "unite": ["EUR/MWh" if cle == "entsoe_prix" else "MW"] * n, "annee_fichier": [annee] * n},
                        schema=entsoe_derive.SCHEMA_NATIF)


def test_quarts_repetes_du_30_septembre_2025():
    h = u(2025, 9, 30, 10)
    egaux = [(h + timedelta(minutes=15 * i), 15, 69.9) for i in range(4)]
    differents = [(h + timedelta(hours=1, minutes=15 * i), 15, 60.0 + i) for i in range(4)]
    apres = [(u(2025, 10, 1, 10) + timedelta(minutes=15 * i), 15, 50.0) for i in range(4)]  # après la bascule
    df, r = entsoe_derive.ramener_quarts_repetes(natif(egaux + differents + apres))
    assert r["heures_ramenees"] == 1 and r["heures_quarts_differents"] == 1
    d = df.sort("debut_utc")
    assert d.filter(pl.col("debut_utc") == h).select("pas_min", "valeur").row(0) == (60, 69.9)
    assert d.height == 1 + 4 + 4
    # la charge n'est jamais concernée
    df2, r2 = entsoe_derive.ramener_quarts_repetes(natif(egaux, cle="entsoe_charge"))
    assert df2.height == 4 and r2["heures_ramenees"] == 0


def test_doublons_entre_fichiers_et_conflits():
    a = natif([(u(2024, 12, 31, 23), 60, 10.0), (u(2025, 1, 1, 0), 60, 11.0)], annee=2025)
    b = natif([(u(2024, 12, 31, 23), 60, 10.0), (u(2025, 1, 1, 0), 60, 12.0)], annee=2024)
    out, r = entsoe_derive.dedoublonner(pl.concat([a, b]))
    assert out.height == 2 and r["lignes_en_double"] == 2 and r["conflits"] == 1
    assert out.filter(pl.col("debut_utc") == u(2025, 1, 1, 0))["valeur"].item() == 11.0  # fichier le plus récent


def test_chevauchement_detecte():
    df = natif([(u(2024, 1, 1, 0), 60, 1.0), (u(2024, 1, 1, 0, 15), 15, 2.0)])
    assert entsoe_derive.chevauchements(df).height == 1
    assert entsoe_derive.chevauchements(natif([(u(2024, 1, 1, 0), 60, 1.0), (u(2024, 1, 1, 1), 15, 2.0)])).height == 0


def test_vue_horaire_couverture_et_moyenne():
    pts = ([(u(2024, 1, 1, 0) + timedelta(minutes=15 * i), 15, float(i)) for i in range(4)]  # heure complète
           + [(u(2024, 1, 1, 1), 30, 100.0)]  # demi-heure seule : heure incomplète
           + [(u(2024, 1, 1, 2), 30, 100.0), (u(2024, 1, 1, 2, 30), 30, 200.0)])  # pas de 30 min
    h, _ = entsoe_derive.vers_horaire(natif(pts, cle="entsoe_charge"))
    assert h["charge_fr"].to_list() == [1.5, None, 150.0]
    assert h["heure_utc"].to_list() == [u(2024, 1, 1, 0), u(2024, 1, 1, 1), u(2024, 1, 1, 2)]


def test_solde_physique_signe_et_trou():
    lignes = []
    for v in entsoe.VOISINS_FLUX:
        lignes.append(natif([(u(2024, 1, 1, 0), 60, 100.0), (u(2024, 1, 1, 1), 60, 100.0)], "entsoe_flux", f"FR-{v}"))
        val = [(u(2024, 1, 1, 0), 60, 50.0)] + ([] if v == "GB" else [(u(2024, 1, 1, 1), 60, 50.0)])
        lignes.append(natif(val, "entsoe_flux", f"{v}-FR"))
    h, info = entsoe_derive.vers_horaire(pl.concat(lignes))
    assert h["solde_physique_fr"].to_list() == [6 * 50.0 - 6 * 100.0, None]  # export net : négatif
    assert "solde_physique_fr" in info["colonnes"]


# --------------------------------------------------------------------------
# Téléchargement : fenêtres, incrémental, jeton
# --------------------------------------------------------------------------


def test_fenetres_annee_civile_de_paris():
    assert entsoe.fenetre(2024, date(2026, 11, 26)) == ("202312312300", "202412312300")
    assert entsoe.fenetre(2026, date(2026, 11, 26)) == ("202512312300", "202611280000")


def test_annees_par_serie():
    gb = next(s for s in entsoe.CATALOGUE["entsoe_prix"] if s.nom == "GB")
    assert list(entsoe.annees_serie(gb, date(2026, 11, 26))) == list(range(2015, 2021))
    de = [s.nom for s in entsoe.CATALOGUE["entsoe_prix"]]
    assert "DE-AT-LU" in de and "DE-LU" in de
    assert len(entsoe.CATALOGUE["entsoe_flux"]) == 12


def test_annee_close():
    j = date(2026, 11, 26)
    assert not entsoe.annee_close(None, 2024, j)
    assert entsoe.annee_close({"extrait_le": "2026-11-26T10:00:00+00:00"}, 2024, j)
    assert not entsoe.annee_close({"extrait_le": "2025-01-03T10:00:00+00:00"}, 2024, j)  # trop tôt
    assert not entsoe.annee_close({"extrait_le": "2026-11-26T10:00:00+00:00"}, 2026, j)  # année en cours


def test_masquage_du_jeton():
    jeton = "abcd-1234-secret"
    assert jeton not in entsoe.masquer(f"https://x/api?a=1&securityToken={jeton}&b=2", jeton)
    assert "securityToken=***" in entsoe.masquer("…?securityToken=autre-chose", None)
    assert entsoe.url_publique({"documentType": "A65"}).endswith("securityToken=***")


class ClientQuiEchoue:
    def __init__(self, jeton, exc=True):
        self.jeton, self.exc, self.appels = jeton, exc, 0

    def get(self, url, params):
        self.appels += 1
        raise RuntimeError(f"boom sur {url}?securityToken={params['securityToken']}")


def test_erreur_reseau_sans_jeton_dans_le_message(monkeypatch, tmp_path):
    monkeypatch.setattr(entsoe, "ATTENTES_RELANCE_S", (0, 0))
    jeton = "jeton-tres-secret"
    c = ClientQuiEchoue(jeton)
    s = entsoe.CATALOGUE["entsoe_charge"][0]
    with pytest.raises(entsoe.ErreurEntsoe) as e:
        entsoe.telecharger_une(c, tmp_path, s, 2024, jeton, date(2026, 11, 26))
    assert jeton not in str(e.value) and c.appels == 3


class Reponse:
    def __init__(self, code, contenu=b"", entetes=None):
        self.status_code, self.content, self.headers = code, contenu, entetes or {}
        self.text = contenu.decode()


class ClientScenario:
    def __init__(self, reponses):
        self.reponses = list(reponses)

    def get(self, url, params):
        return self.reponses.pop(0)


def test_relance_sur_599_puis_ecriture_et_manifeste(monkeypatch, tmp_path):
    monkeypatch.setattr(entsoe, "ATTENTES_RELANCE_S", (0, 0, 0))
    xml = document("A65", [serie([periode("2024-01-01T00:00Z", "2024-01-01T01:00Z", "PT60M", {1: 5})], MW)])
    c = ClientScenario([Reponse(599, b"<text>Unable to access service</text>"), Reponse(429, b"", {"Retry-After": "0"}),
                        Reponse(200, xml)])
    s = entsoe.CATALOGUE["entsoe_charge"][0]
    e = entsoe.telecharger_une(c, tmp_path, s, 2024, "j", date(2026, 11, 26))
    assert e["lignes"] == 1 and "securityToken=***" in e["url"] and "periodStart=202312312300" in e["url"]
    assert gzip.decompress(entsoe.fichier_entsoe(tmp_path, s, 2024).read_bytes()) == xml


def test_http_400_sans_relance(monkeypatch, tmp_path):
    c = ClientScenario([Reponse(400, b"<text>Input parameter does not exist</text>")])
    with pytest.raises(entsoe.ErreurEntsoe, match="HTTP 400"):
        entsoe.telecharger_une(c, tmp_path, entsoe.CATALOGUE["entsoe_charge"][0], 2024, "j", date(2026, 11, 26))


def test_acquittement_inattendu_refuse(tmp_path):
    ack = (b'<?xml version="1.0"?><Acknowledgement_MarketDocument><Reason><code>999</code>'
           b"<text>The amount of requested data exceeds allowed limit</text></Reason></Acknowledgement_MarketDocument>")
    with pytest.raises(entsoe.ErreurEntsoe, match="acquittement"):
        entsoe.telecharger_une(ClientScenario([Reponse(200, ack)]), tmp_path, entsoe.CATALOGUE["entsoe_charge"][0],
                               2024, "j", date(2026, 11, 26))


def test_sans_jeton_echec_clair_et_rien_telecharge(monkeypatch, tmp_path):
    monkeypatch.delenv("ENTSOE_TOKEN", raising=False)
    monkeypatch.setattr(entsoe, "FICHIER_JETON", tmp_path / "absent")
    with pytest.raises(SystemExit, match="jeton ENTSO-E absent"):
        sources.download(tmp_path / "raw", ["entsoe_charge"])
    assert not (tmp_path / "raw" / "entsoe").exists()
    with pytest.raises(entsoe.JetonAbsent):
        entsoe.download(tmp_path, ["entsoe_charge"], {}, False, date(2026, 11, 26), None)


def test_jeton_lu_dans_l_environnement(monkeypatch, tmp_path):
    monkeypatch.setattr(entsoe, "FICHIER_JETON", tmp_path / "absent")
    monkeypatch.setenv("ENTSOE_TOKEN", " x ")
    assert entsoe.lire_jeton() == "x"


def test_licences_par_donnee():
    assert sources.SOURCES["entsoe_flux"]["licence"].startswith("CC BY 4.0")
    assert sources.SOURCES["entsoe_capacites"]["licence"].startswith("CC BY 4.0")
    for cle in ("entsoe_prix", "entsoe_production", "entsoe_charge"):
        assert "absente de la liste" in sources.SOURCES[cle]["licence"]


# --------------------------------------------------------------------------
# Contrôles
# --------------------------------------------------------------------------


def _horaire(col: str, valeurs: list[float], debut=u(2024, 6, 1)) -> pl.DataFrame:
    return pl.DataFrame({"heure_utc": [debut + timedelta(hours=i) for i in range(len(valeurs))], col: valeurs},
                        schema={"heure_utc": entsoe_derive.DATETIME_UTC, col: pl.Float64})


def _profil(n=24 * 30):
    import math
    return [50_000 + 8_000 * math.sin(i / 24 * 2 * math.pi) + 3_000 * math.sin(i / 168 * 2 * math.pi)
            for i in range(n)]


def test_controle_charge_detecte_un_decalage_d_une_heure():
    ref = _profil()
    table = _horaire("consommation", ref)
    ok = check_entsoe.controle_charge(_horaire("charge_fr", [x * 0.99 for x in ref]), table)
    assert ok.statut == "OK"
    decale = check_entsoe.controle_charge(_horaire("charge_fr", ref[1:] + ref[-1:]), table)
    assert decale.statut == "ÉCHEC"


def test_controle_solde_detecte_un_signe_inverse():
    ref = [x - 50_000 for x in _profil()]
    table = _horaire("ech_physiques", ref)
    assert check_entsoe.controle_solde(_horaire("solde_physique_fr", ref), table).statut == "OK"
    assert check_entsoe.controle_solde(_horaire("solde_physique_fr", [-x for x in ref]), table).statut == "ÉCHEC"


def test_controle_completude_trou_inexplique():
    trois = _horaire("prix_fr", [1.0, None, None, None, 2.0]).with_columns(pl.lit(1.0).alias("prix_be"))
    r = check_entsoe.controle_completude(trois, {})
    assert r.statut == "ÉCHEC" and any("INEXPLIQUÉ" in x for x in r.lignes)
    # trou d'une heure : toléré dans le budget annuel
    assert check_entsoe.controle_completude(_horaire("prix_fr", [1.0, None, 2.0]), {}).statut == "OK"
    # budget dépassé : 13 trous d'une heure sur une même année (26 h > 24 h)
    v = [1.0, None, None, 1.0] * 13 + [1.0]
    assert check_entsoe.controle_completude(_horaire("prix_fr", v), {}).statut == "ÉCHEC"
    # lacune listée
    lac = check_entsoe.LACUNES_ENTSOE[0]
    h = _horaire(lac[0], [1.0] + [None] * lac[2] + [1.0], debut=lac[1] - timedelta(hours=1))
    assert check_entsoe.controle_completude(h, {}).statut == "OK"


def test_passage_heure_hiver_reconnu():
    # 27/10/2024 : heure répétée = 00:00 UTC ; plage de 2 h commençant le samedi 23:00 UTC
    h = _horaire("charge_fr", [1.0, None, None, 1.0], debut=u(2024, 10, 26, 22))
    r = check_entsoe.controle_completude(h, {})
    assert r.statut == "OK" and "dont 2 h au passage à l'heure d'hiver" in r.lignes[0]


def test_controle_bornes():
    bon = natif([(u(2024, 1, 1, 0), 60, -499.0), (u(2024, 1, 1, 1), 60, 3000.0)])
    assert check_entsoe.controle_bornes(bon).statut == "OK"
    assert check_entsoe.controle_bornes(natif([(u(2024, 1, 1, 0), 60, -600.0)])).statut == "ÉCHEC"
    assert check_entsoe.controle_bornes(natif([(u(2024, 1, 1, 0), 60, -1.0)], cle="entsoe_flux")).statut == "ÉCHEC"


def test_controles_sans_donnees_info(tmp_path):
    r = check_entsoe.controles(tmp_path, tmp_path / "derive", pl.DataFrame())
    assert len(r) == 1 and r[0]().statut == "INFO"


def test_sequence_1_quart_horaire_sous_une_heure_non_classee():
    """ES, 05/09/2025 : SDAC horaire non classé et séquence 1 au quart d'heure le même jour."""
    sdac = serie([periode("2025-09-04T22:00Z", "2025-09-04T23:00Z", "PT60M", {1: (80.0,)})], EUR)
    ida1 = serie([periode("2025-09-04T22:00Z", "2025-09-04T23:00Z", "PT15M", {1: (70.0,), 2: (71.0,)})],
                 {**EUR, "classificationSequence_AttributeInstanceComponent.position": 1})
    df, _ = entsoe_derive.normaliser_document(entsoe.lire_document(document("A44", [sdac, ida1])),
                                              "entsoe_prix", "ES", 2025)
    assert df.select("pas_min", "valeur").rows() == [(60, 80.0)]
    assert entsoe_derive.chevauchements(df).height == 0


def test_http_400_panne_serveur_relancee(monkeypatch, tmp_path):
    monkeypatch.setattr(entsoe, "ATTENTES_RELANCE_S", (0, 0))
    xml = document("A65", [serie([periode("2024-01-01T00:00Z", "2024-01-01T01:00Z", "PT60M", {1: 5})], MW)])
    c = ClientScenario([Reponse(400, b"<text>An unexpected error occurred: I/O error on POST request</text>"),
                        Reponse(200, xml)])
    e = entsoe.telecharger_une(c, tmp_path, entsoe.CATALOGUE["entsoe_charge"][0], 2024, "j", date(2026, 11, 26))
    assert e["lignes"] == 1


# --------------------------------------------------------------------------
# Données réelles (data/raw/entsoe/, data/derive/entsoe/) : sautés si absentes
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def derive():
    from pc.cli import DERIVE
    if not (DERIVE / "entsoe" / "horaire.parquet").exists():
        pytest.skip("data/derive/entsoe/ absent (`pc download entsoe_…` avec jeton, puis `pc build`)")
    return DERIVE / "entsoe"


@pytest.mark.donnees
def test_derive_colonnes_et_prix_fr(derive, export):
    h = pl.read_parquet(derive / "horaire.parquet")
    attendues = {"prix_fr", "prix_de_lu", "prix_de_at_lu", "charge_fr", "solde_physique_fr", "production_fr_b14",
                 *[f"flux_fr_{v}" for v in ("be", "de", "ch", "it", "es", "gb")],
                 *[f"ntc_{a}_{b}" for v in ("ch", "it_nord", "es", "gb") for a, b in (("fr", v), (v, "fr"))]}
    assert attendues <= set(h.columns)
    assert (h["heure_utc"].diff().drop_nulls().dt.total_minutes() == 60).all()
    t = pl.read_parquet(export / "systeme_horaire.parquet").select("heure_utc", "prix_eur_mwh")
    j = h.select("heure_utc", "prix_fr").join(t, on="heure_utc").drop_nulls()
    assert j.height > 100_000 and (j["prix_fr"] - j["prix_eur_mwh"]).abs().max() < 1e-3


@pytest.mark.donnees
def test_manifeste_entsoe_sans_jeton(raw):
    import json
    m = {k: v for k, v in json.loads((raw / "manifeste.json").read_text()).items() if k.startswith("entsoe_")}
    if not m:
        pytest.skip("pas d'entrée ENTSO-E au manifeste")
    assert all(v["url"].endswith("securityToken=***") for v in m.values())
    jeton = entsoe.lire_jeton()
    if jeton:
        assert jeton not in (raw / "manifeste.json").read_text()
    attendu = {entsoe.cle_manifeste(s, a) for c in entsoe.CLES for s in entsoe.CATALOGUE[c]
               for a in entsoe.annees_serie(s, date.today())}
    assert attendu <= set(m)


@pytest.mark.donnees
def test_meta_export_sans_entsoe(export):
    import json
    m = json.loads((export / "meta.json").read_text())
    assert not [k for k in m["sources"] if k.startswith("entsoe_")]
