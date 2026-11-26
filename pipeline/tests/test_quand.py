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
    if cas["fonction"] == "max_pluriannuel":
        return quand.max_pluriannuel(e["maxima"])
    if cas["fonction"] == "quantile":
        return quand.quantile(e["tries"], e["q"])
    if cas["fonction"] == "simuler":
        return quand.simuler(e, **p)
    if cas["fonction"] == "episode_froid":
        return quand.episode_froid(e["rn"], **p)
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


def table_aleatoire(graine: int, n: int = 500) -> dict:
    rng = random.Random(graine)
    heures = [f"2025-01-{1 + i // 24:02d}T{i % 24:02d}:00Z" for i in range(n)]
    dispo = [float(rng.randint(40000, 60000)) for _ in range(n)]
    return {
        "heure_utc": heures,
        "consommation": [float(rng.randint(40000, 90000)) if rng.random() > 0.02 else None for _ in range(n)],
        "eolien": [float(rng.randint(0, 15000)) for _ in range(n)],
        "solaire": [float(rng.randint(0, 10000)) for _ in range(n)],
        "nucleaire_disponible": dispo,
        "nucleaire": [d - rng.randint(-500, 15000) if rng.random() > 0.02 else None for d in dispo],
        "prix": [round(rng.uniform(-20, 200), 2) if rng.random() > 0.02 else None for _ in range(n)],
        "ech_physiques": [float(rng.randint(-15000, 8000)) for _ in range(n)],
    }


@pytest.mark.parametrize("x_mw", [500, 3000, 12000])
def test_simuler_sans_effacement_egale_charge_plate(x_mw):
    """Sans effacement, `simuler` redonne exactement `charge_plate` et la monotone d'`indicateurs_annee`."""
    t = table_aleatoire(7)
    s = quand.simuler(t, x_mw)
    a = quand.indicateurs_annee(t, charges_mw=(x_mw,))
    cp = a["charges_plates"][0]
    assert s["energie_ajoutee_twh"] == pytest.approx(cp["energie_ajoutee_twh"], rel=1e-12)
    assert s["energie_dans_j_twh"] == pytest.approx(cp["energie_dans_j_twh"], rel=1e-12)
    assert s["part_dans_j"] == pytest.approx(cp["part_dans_j"], rel=1e-12)
    assert s["heures_j_couvre_charge"] == cp["heures_j_superieur_ou_egal_x"]
    assert s["solde_echanges_moyen_heures_j_couvre_mw"] == pytest.approx(cp["solde_echanges_moyen_heures_j_ge_x_mw"])
    assert s["max_apres"]["valeur_mw"] == cp["rn_max_plus_x_mw"]
    assert s["heures_au_dessus_du_max"] == cp["heures_rn_plus_x_au_dessus_du_max"]
    assert s["rn_max_mw"] == a["charge_residuelle"]["max"]["valeur_mw"]
    assert s["monotone_avant"] == a["charge_residuelle"]["monotone"]
    assert s["prix_moyen_pondere_eur_mwh"] == pytest.approx(s["prix_moyen_eur_mwh"], rel=1e-12)
    # Plancher et seuil de référence : mêmes valeurs que charge_plate.
    sr = quand.simuler(t, x_mw, rn_max_reference_mw=40000)
    ar = quand.indicateurs_annee(t, charges_mw=(x_mw,), rn_max_reference_mw=40000)["charges_plates"][0]
    assert sr["part_dans_j_plancher"] == pytest.approx(ar["part_dans_j_plancher"], rel=1e-12)
    assert sr["energie_dans_j_plancher_twh"] == pytest.approx(ar["energie_dans_j_plancher_twh"], rel=1e-12)
    assert sr["heures_au_dessus_du_max_reference"] == ar["heures_rn_plus_x_au_dessus_du_max_reference"]
    # Heures effacées = heures tendues d'indicateurs_annee, dans le même ordre.
    s2 = quand.simuler(t, x_mw, 40)
    a2 = quand.indicateurs_annee(t, charges_mw=(x_mw,), n_tendues=40)
    assert s2["heures_effacees"] == [h for h, _ in a2["heures_tendues"]["heures"]]


def test_simuler_effacement_minimal_pour_rester_sous_le_max():
    """Effacer les N* heures où RN + X dépasse le maximum (N* = résultat sans effacement) suffit, et
    il ne faut pas moins : prévision parfaite, la charge n'est retirée qu'aux heures les plus tendues."""
    t = table_aleatoire(11)
    x = 8000
    n_etoile = quand.simuler(t, x)["heures_au_dessus_du_max"]
    assert n_etoile > 1
    assert quand.simuler(t, x, n_etoile)["heures_au_dessus_du_max"] == 0
    assert quand.simuler(t, x, n_etoile - 1)["heures_au_dessus_du_max"] == 1
    au_dela = [quand.simuler(t, x, n)["heures_au_dessus_du_max"] for n in range(0, n_etoile + 3)]
    assert au_dela == sorted(au_dela, reverse=True)


def test_simuler_proprietes():
    t = table_aleatoire(3)
    for x, n in [(1000, 0), (1000, 50), (6000, 200), (20000, 10_000)]:
        s = quand.simuler(t, x, n)
        effacees = min(n, s["heures_rn_valides"])
        assert len(s["heures_effacees"]) == effacees == s["heures_charge_nulle"]
        assert s["energie_ajoutee_twh"] == pytest.approx(x * (s["heures"] - effacees) / 1e6)
        assert 0 <= s["part_dans_j"] <= 1
        assert 0 <= s["part_prix_negatif"] <= s["part_prix_nul_ou_negatif"] <= 1
        assert s["max_apres"]["valeur_mw"] >= s["rn_max_mw"]
        assert s["monotone_apres"][0][1] == s["max_apres"]["valeur_mw"]
        assert len(s["monotone_avant"]) == len(s["monotone_apres"])
        # Fourchette : le plancher ne peut que réduire la part.
        assert 0 <= s["part_dans_j_plancher"] <= s["part_dans_j"]
        assert s["energie_effacee_twh"] == pytest.approx(x * effacees / 1e6)
        assert s["heures_prix_nul_ou_negatif_j_couvre"] <= s["heures_prix_nul_ou_negatif_charge"]
        # L'heure du maximum observé compte dès que X > 0 et qu'elle n'est pas effacée.
        if n == 0:
            assert s["heures_au_dessus_du_max"] >= 1


def test_simuler_refuse_les_parametres_invalides():
    t = table_aleatoire(1, 10)
    with pytest.raises(ValueError):
        quand.simuler(t, -1)
    with pytest.raises(ValueError):
        quand.simuler(t, 1000, -1)
    with pytest.raises(ValueError):
        quand.simuler(t, 1000, 1.5)


# --------------------------------------------------------------------------
# Froid supplémentaire et plancher réglable (limites de « Quand ? », 26/11/2026)
# --------------------------------------------------------------------------

#: Clés de la sortie de `simuler` antérieures au froid : elles ne changent pas quand le froid est nul.
CLES_AVANT_FROID = ("energie_ajoutee_twh", "energie_dans_j_twh", "part_dans_j", "part_dans_j_plancher",
                    "heures_j_couvre_charge", "solde_echanges_moyen_heures_j_couvre_mw", "rn_max_mw", "max_apres",
                    "heures_au_dessus_du_max", "heures_au_dessus_du_max_reference", "part_prix_negatif",
                    "part_prix_nul_ou_negatif", "prix_moyen_pondere_eur_mwh", "heures_prix_nul_ou_negatif_charge",
                    "heures_prix_nul_ou_negatif_j_couvre", "monotone_avant", "monotone_apres", "heures_effacees",
                    "rn_seuil_effacement_mw", "energie_effacee_twh")


@pytest.mark.parametrize("x_mw, n", [(1000, 0), (5000, 30)])
def test_froid_nul_ne_change_rien(x_mw, n):
    """Froid nul (avec ou sans gradient) : résultats identiques à l'appel sans froid, et à
    `effet_charge` sans supplément ; aucun chiffre publié ne bouge."""
    t = table_aleatoire(5)
    s0 = quand.simuler(t, x_mw, n, rn_max_reference_mw=45000)
    s1 = quand.simuler(t, x_mw, n, rn_max_reference_mw=45000, froid_c=0, gradient_mw_par_c=2400)
    for k in CLES_AVANT_FROID:
        assert s0[k] == s1[k], k
    assert s1["froid_heures"] == 0 and s1["energie_froid_twh"] == 0 and s1["froid_debut_utc"] is None


def test_froid_proprietes():
    """Le froid s'ajoute à RN « après » sur l'épisode seulement, laisse les seuils observés, et réduit
    J pour la charge ; plus il fait froid, plus d'heures au-delà du maximum."""
    t = table_aleatoire(9, 600)
    s0 = quand.simuler(t, 2000, rn_max_reference_mw=45000)
    sf = quand.simuler(t, 2000, rn_max_reference_mw=45000, froid_c=4, gradient_mw_par_c=2400, duree_froid_h=48)
    assert sf["froid_heures"] == 48 and sf["froid_ajout_mw"] == 9600
    assert sf["energie_froid_twh"] == pytest.approx(9600 * 48 / 1e6)
    assert sf["rn_max_mw"] == s0["rn_max_mw"] and sf["monotone_avant"] == s0["monotone_avant"]
    assert sf["heures_au_dessus_du_max"] >= s0["heures_au_dessus_du_max"]
    assert sf["max_apres"]["valeur_mw"] >= s0["max_apres"]["valeur_mw"]
    assert sf["part_dans_j"] <= s0["part_dans_j"] and sf["energie_ajoutee_twh"] == s0["energie_ajoutee_twh"]
    assert sf["consommation_max_apres"]["valeur_mw"] >= s0["consommation_max_apres"]["valeur_mw"]
    # L'épisode est la fenêtre de RN observée moyenne la plus élevée.
    rn = [quand.charge_residuelle(*v) for v in zip(t["consommation"], t["eolien"], t["solaire"],
                                                     t["nucleaire_disponible"])]
    ep = quand.episode_froid(rn, 48)
    assert t["heure_utc"][ep[0]] == sf["froid_debut_utc"] and t["heure_utc"][ep[-1]] == sf["froid_fin_utc"]
    moyennes = []
    for d in range(len(rn) - 47):
        v = [x for x in rn[d:d + 48] if x is not None]
        moyennes.append(sum(v) / len(v))
    assert moyennes[ep[0]] == max(moyennes)
    plus = [quand.simuler(t, 2000, froid_c=f, gradient_mw_par_c=2400, duree_froid_h=48)["heures_au_dessus_du_max"]
            for f in (0, 2, 4, 8)]
    assert plus == sorted(plus)


def test_froid_effacement_suffisant_si_le_froid_seul_ne_depasse_pas():
    """Avec froid, effacer les N* heures (N* = sans effacement) ramène à zéro quand le froid seul ne
    dépasse pas le maximum ; sinon, les heures dues au froid seul restent (le simulateur le dit)."""
    t = table_aleatoire(11)
    for f in (0.5, 6):
        seul = quand.simuler(t, 0, froid_c=f, gradient_mw_par_c=2400, duree_froid_h=24)["heures_au_dessus_du_max"]
        n_etoile = quand.simuler(t, 6000, froid_c=f, gradient_mw_par_c=2400, duree_froid_h=24)["heures_au_dessus_du_max"]
        reste = quand.simuler(t, 6000, n_etoile, froid_c=f, gradient_mw_par_c=2400,
                              duree_froid_h=24)["heures_au_dessus_du_max"]
        assert reste == seul
    assert seul > 0  # le cas « froid seul au-delà du maximum » est bien exercé


def test_plancher_reglable():
    """La part avec plancher décroît quand le plancher croît ; plancher nul = part sans plancher."""
    t = table_aleatoire(13)
    parts = [quand.simuler(t, 3000, plancher_mw=p)["part_dans_j_plancher"] for p in (0, 500, 1000, 2000, 3000)]
    assert parts[0] == quand.simuler(t, 3000)["part_dans_j"]
    assert parts == sorted(parts, reverse=True)


def test_froid_refuse_les_parametres_invalides():
    t = table_aleatoire(1, 10)
    with pytest.raises(ValueError):
        quand.simuler(t, 1000, froid_c=-1, gradient_mw_par_c=2400)
    with pytest.raises(ValueError):
        quand.simuler(t, 1000, froid_c=2)
    with pytest.raises(ValueError):
        quand.episode_froid([1.0, 2.0], 0)
