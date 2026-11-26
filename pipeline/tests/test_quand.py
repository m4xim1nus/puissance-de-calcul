"""Indicateurs « Quand ? » : cas de test partagés (tests/cas_quand.json) et propriétés, sans données."""

import json
import random
from pathlib import Path

import pytest

from pc import quand

CAS = json.loads((Path(__file__).parent / "cas_quand.json").read_text(encoding="utf-8"))


def lire(obj, chemin: str):
    """Valeur au chemin pointé (clés et indices de liste) ; chemin vide = l'objet lui-même."""
    for morceau in (chemin.split(".") if chemin else []):
        obj = obj[int(morceau)] if isinstance(obj, list) else obj[morceau]
    return obj


def egal(a, b, tol: float) -> bool:
    if isinstance(b, list):
        return isinstance(a, list) and len(a) == len(b) and all(egal(x, y, tol) for x, y in zip(a, b))
    if b is None or isinstance(b, str):
        return a == b
    if a is None or isinstance(a, str):
        return False
    return abs(a - b) <= tol * max(1.0, abs(b))


def executer(cas: dict):
    e, p = cas["entree"], cas.get("parametres", {})
    if cas["fonction"] == "indicateurs_annee":
        return quand.indicateurs_annee(e, **p)
    if cas["fonction"] == "matrice_jour_heure":
        return quand.matrice_jour_heure(e["heures_utc"], e["valeurs"])
    if cas["fonction"] == "quantile":
        return quand.quantile(e["tries"], e["q"])
    raise ValueError(cas["fonction"])


@pytest.mark.parametrize("cas", CAS["cas"], ids=[c["nom"] for c in CAS["cas"]])
def test_cas_partages(cas):
    sortie = executer(cas)
    fautes = [f"{chemin} : obtenu {lire(sortie, chemin)!r}, attendu {v!r}"
              for chemin, v in cas["attendu"].items() if not egal(lire(sortie, chemin), v, CAS["tolerance"])]
    assert not fautes, "\n".join(fautes)


def test_cas_partages_serialisables():
    # Le fichier est la source commune aux deux implémentations : il doit rester du JSON pur.
    assert json.loads(json.dumps(CAS)) == CAS


def test_monotone_courte_et_dernier_rang():
    assert quand.monotone([3, 1, 2], n_exact=100) == [[1, 3], [2, 2], [3, 1]]
    m = quand.monotone(list(range(1000)), n_exact=100, pas=20)
    assert m[:100] == [[r, 1000 - r] for r in range(1, 101)]
    assert m[100] == [120, 880] and m[-1] == [1000, 0]
    assert [r for r, _ in m] == sorted({r for r, _ in m})


def test_charge_plate_refuse_x_nul():
    with pytest.raises(ValueError):
        quand.charge_plate([1.0], [1.0], 0)


def test_heure_paris_refuse_heure_naive():
    with pytest.raises(ValueError):
        quand.heure_paris("2025-01-01T00:00")


def test_proprietes_sur_serie_aleatoire():
    """Part tenue décroissante en X et ≤ 1 ; Σ min(X, J) ≤ Σ J ; heures au-delà du max croissantes en X."""
    rng = random.Random(4)
    n = 500
    heures = [f"2025-01-{1 + i // 24:02d}T{i % 24:02d}:00Z" for i in range(n)]
    dispo = [rng.uniform(40000, 60000) for _ in range(n)]
    table = {
        "heure_utc": heures,
        "consommation": [rng.uniform(40000, 90000) for _ in range(n)],
        "eolien": [rng.uniform(0, 15000) for _ in range(n)],
        "solaire": [rng.uniform(0, 10000) for _ in range(n)],
        "nucleaire_disponible": dispo,
        "nucleaire": [d - rng.uniform(-500, 15000) for d in dispo],
        "prix": [rng.uniform(-20, 200) for _ in range(n)],
    }
    r = quand.indicateurs_annee(table)
    cp = r["charges_plates"]
    parts = [c["part_dans_j"] for c in cp]
    assert all(0 <= p <= 1 for p in parts)
    assert parts == sorted(parts, reverse=True)
    assert all(c["energie_dans_j_twh"] <= r["jeu_nucleaire"]["somme_twh"] + 1e-12 for c in cp)
    au_dela = [c["heures_rn_plus_x_au_dessus_du_max"] for c in cp]
    assert au_dela == sorted(au_dela) and au_dela[0] >= 1
    cr = r["charge_residuelle"]
    assert cr["monotone"][0][1] == cr["max"]["valeur_mw"]
    assert r["heures_tendues"]["heures"][0][1] == cr["max"]["valeur_mw"]
    assert sum(r["jeu_nucleaire"]["par_mois_twh"]) == pytest.approx(r["jeu_nucleaire"]["somme_twh"])
    q = list(cr["quantiles_mw"].values())
    assert q == sorted(q) and cr["min"]["valeur_mw"] <= q[0] and q[-1] <= cr["max"]["valeur_mw"]
