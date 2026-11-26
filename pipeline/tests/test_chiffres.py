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


# --------------------------------------------------------------------------
# Grandeurs du système et chiffres calculés par le pipeline
# --------------------------------------------------------------------------


def test_marge_certifiee_et_installee_non_comparables():
    # MW de marge ≠ MW certifiés ≠ MW raccordés : unités convertibles, grandeurs différentes.
    marge = chiffre(grandeur="marge_adequation", valeur=9, unite="GW")
    certifiee = chiffre(grandeur="marge_certifiee", valeur=9.5, unite="GW")
    effacement = chiffre(grandeur="puissance_certifiee", valeur=4.4, unite="GW")
    raccorde = chiffre(valeur=0.63, unite="GW")
    for a, b in ((marge, certifiee), (effacement, raccorde), (marge, raccorde)):
        erreurs = chiffres.valider(ref({"a": a, "b": b}, [{"inferieur": ["a", "b"]}]))
        assert any("non comparables" in e for e in erreurs)
    assert chiffres.valider(ref({"a": marge, "b": certifiee, "c": effacement})) == []


def test_chiffre_calcule_exige_son_calcul():
    sans = chiffre(produit_par=chiffres.PRODUIT_PAR_PIPELINE)
    avec = chiffre(produit_par=chiffres.PRODUIT_PAR_PIPELINE, calcul="Σ J")
    inconnu = chiffre(produit_par="à la main", calcul="x")
    assert any("sans « calcul »" in e for e in chiffres.valider(ref({"a": sans})))
    assert chiffres.valider(ref({"a": avec})) == []
    assert any("inconnu" in e for e in chiffres.valider(ref({"a": inconnu})))


def test_fusion_refuse_les_collisions_et_les_chiffres_non_marques():
    import pytest
    r = ref({"a": chiffre()})
    calc = chiffre(produit_par=chiffres.PRODUIT_PAR_PIPELINE, calcul="x", source="calc")
    src = {"calc": {"editeur": "site", "titre": "t", "date_publication": "2026-11-26", "url": "https://q"}}
    f = chiffres.fusionner(r, src, {"b": calc})
    assert set(f.chiffres) == {"a", "b"} and chiffres.valider(f) == []
    with pytest.raises(ValueError):
        chiffres.fusionner(r, src, {"a": calc})
    with pytest.raises(ValueError):
        chiffres.fusionner(r, {"rte-a": src["calc"]}, {"b": calc})
    with pytest.raises(ValueError):
        chiffres.fusionner(r, src, {"b": chiffre(source="calc", calcul="x")})


def test_referentiel_saisi_ne_contient_aucun_chiffre_calcule():
    # Les chiffres `produit_par: pc build` naissent dans `pc build`, jamais dans le YAML.
    dossier = Path(chiffres.REFERENTIELS)
    if not (dossier / "chiffres.yaml").exists():
        return
    r = chiffres.charger(dossier)
    assert not [k for k, c in r.chiffres.items() if c.get("produit_par")]
    assert not [k for k in r.chiffres if k.startswith("quand_")]
