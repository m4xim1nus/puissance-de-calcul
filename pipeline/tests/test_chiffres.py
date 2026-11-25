from pathlib import Path

import yaml

from pc import chiffres

SOURCES = {
    "rte-a": {"editeur": "RTE", "titre": "A", "date_publication": "2025-12-23", "url": "https://x"},
    "rte-b": {"editeur": "RTE", "titre": "B", "date_publication": "2026-03-01", "url": "https://y"},
    "sdes": {"editeur": "SDES", "titre": "C", "date_publication": "2026-07-02", "url": "https://z"},
}


def chiffre(**kw):
    base = {"libelle": "x", "valeur": 1, "unite": "MW", "grandeur": "puissance_raccordee",
            "periode": "2025", "perimetre": "RPT", "source": "rte-a", "page": "p. 1",
            "citation": "« … »", "confiance": "B"}
    return {**base, **kw}


def ref(chiffres_, contraintes=None):
    return chiffres.Referentiel(sources=SOURCES, chiffres=chiffres_, contraintes=contraintes or [])


def test_referentiel_valide():
    assert chiffres.valider(ref({"a": chiffre()})) == []


def test_unite_incompatible_avec_la_grandeur():
    erreurs = chiffres.valider(ref({"a": chiffre(unite="MWh")}))
    assert any("incompatible" in e for e in erreurs)


def test_confiance_a_exige_un_autre_editeur():
    meme = chiffre(confiance="A", recoupements=[{"source": "rte-b"}])
    autre = chiffre(confiance="A", recoupements=[{"source": "sdes"}])
    non_indep = chiffre(confiance="A", recoupements=[{"source": "sdes", "independant": False}])
    assert chiffres.valider(ref({"a": meme}))
    assert chiffres.valider(ref({"a": autre})) == []
    assert chiffres.valider(ref({"a": non_indep}))


def test_contrainte_avec_conversion_d_unites():
    appele = chiffre(grandeur="puissance_appelee_max", valeur=35, unite="MW")
    raccorde = chiffre(valeur=0.63, unite="GW")
    ok = ref({"x": appele, "y": raccorde}, [{"inferieur": ["x", "y"]}])
    ko = ref({"x": appele, "y": raccorde}, [{"inferieur": ["y", "x"]}])
    assert chiffres.valider(ok) == []
    assert any("non tenue" in e for e in chiffres.valider(ko))


def test_energie_et_puissance_non_comparables():
    e = chiffre(grandeur="energie", unite="TWh")
    p = chiffre()
    assert any("non comparables" in m for m in chiffres.valider(ref({"e": e, "p": p}, [{"inferieur": ["p", "e"]}])))


def test_intervalle():
    assert chiffres.bornes([4, 5]) == (4.0, 5.0)
    assert chiffres.valider(ref({"a": chiffre(valeur=[5, 4])}))


def test_referentiel_du_depot_est_valide():
    dossier = Path(chiffres.REFERENTIELS)
    if not (dossier / "chiffres.yaml").exists():
        return
    assert chiffres.valider(chiffres.charger(dossier)) == []


def test_export(tmp_path):
    r = ref({"a": chiffre()})
    chiffres.exporter(r, tmp_path / "c.json")
    import json
    d = json.loads((tmp_path / "c.json").read_text())
    assert d["chiffres"]["a"]["source"]["editeur"] == "RTE"
    assert yaml  # import utilisé par le module
