"""Référentiel des chiffres publiés : chargement, validation, export.

Chaque chiffre affiché sur le site vient d'une entrée de
`referentiels/chiffres.yaml`, qui renvoie à une source de
`referentiels/sources.yaml`. Rien n'est tapé à la main dans une page.

Règles vérifiées ici (voir CLAUDE.md, « Lectrice cible et exigence ») :
- l'unité est compatible avec la nature de la grandeur (une puissance en
  MW ou GW, une énergie en MWh, GWh ou TWh : jamais l'une pour l'autre) ;
- chaque chiffre cite sa source, la page et le passage exact ;
- la confiance A exige un recoupement par une source d'un autre éditeur ;
- les contraintes d'ordre déclarées (appelé ≤ raccordé ≤ réservé…)
  tiennent après conversion d'unités.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

REFERENTIELS = Path(__file__).resolve().parents[1] / "referentiels"

# Nature de la grandeur → unités admises et facteur vers l'unité de base.
_PUISSANCE = {"MW": 1.0, "GW": 1000.0}
_ENERGIE = {"MWh": 1.0, "GWh": 1e3, "TWh": 1e6}
UNITES: dict[str, dict[str, float]] = {
    # Les cinq étages de la pyramide, jamais additionnés entre eux.
    "puissance_recherchee": _PUISSANCE,
    "puissance_reservee": _PUISSANCE,
    "puissance_signee": _PUISSANCE,
    "puissance_raccordee": _PUISSANCE,
    "puissance_appelee_moyenne": _PUISSANCE,
    "puissance_appelee_max": _PUISSANCE,
    "puissance_it": _PUISSANCE,
    "energie": _ENERGIE,
    "part": {"%": 1.0},
    "nombre": {"sites": 1.0, "projets": 1.0, "heures": 1.0, "déclarants": 1.0},
    "intensite_moyenne": {"gCO2/kWh": 1.0, "gCO2eq/kWh": 1.0},
    "prix": {"€/MWh": 1.0},
    "pue": {"": 1.0},
}
CONFIANCES = {"A", "B", "C"}
CHAMPS_SOURCE = ("editeur", "titre", "date_publication", "url")
CHAMPS_CHIFFRE = ("libelle", "valeur", "unite", "grandeur", "periode", "perimetre",
                  "source", "page", "citation", "confiance")


@dataclass
class Referentiel:
    sources: dict[str, dict]
    chiffres: dict[str, dict]
    contraintes: list[dict] = field(default_factory=list)


def charger(dossier: Path = REFERENTIELS) -> Referentiel:
    sources = yaml.safe_load((dossier / "sources.yaml").read_text(encoding="utf-8")) or {}
    doc = yaml.safe_load((dossier / "chiffres.yaml").read_text(encoding="utf-8")) or {}
    return Referentiel(sources=sources, chiffres=doc.get("chiffres") or {},
                       contraintes=doc.get("contraintes") or [])


def bornes(valeur) -> tuple[float, float]:
    """Une valeur est un nombre ou un intervalle [min, max]."""
    if isinstance(valeur, list):
        if len(valeur) != 2 or valeur[0] > valeur[1]:
            raise ValueError(f"intervalle invalide : {valeur}")
        return float(valeur[0]), float(valeur[1])
    return float(valeur), float(valeur)


def en_base(chiffre: dict) -> tuple[float, float]:
    """Bornes converties dans l'unité de base de la grandeur (MW, MWh…)."""
    facteur = UNITES[chiffre["grandeur"]][chiffre["unite"]]
    lo, hi = bornes(chiffre["valeur"])
    return lo * facteur, hi * facteur


def _date(valeur) -> date | None:
    if isinstance(valeur, date):
        return valeur
    try:
        return date.fromisoformat(str(valeur))
    except ValueError:
        return None


def valider(ref: Referentiel) -> list[str]:
    """Liste des erreurs ; vide si le référentiel est cohérent."""
    erreurs: list[str] = []
    for cle, s in ref.sources.items():
        for champ in CHAMPS_SOURCE:
            if not s.get(champ):
                erreurs.append(f"source {cle} : champ « {champ} » manquant")
        if s.get("date_publication") and _date(s["date_publication"]) is None:
            erreurs.append(f"source {cle} : date_publication non ISO ({s['date_publication']})")

    for cle, c in ref.chiffres.items():
        manquants = [ch for ch in CHAMPS_CHIFFRE if c.get(ch) in (None, "")]
        if manquants:
            erreurs.append(f"chiffre {cle} : champs manquants {manquants}")
            continue
        g, u = c["grandeur"], c["unite"]
        if g not in UNITES:
            erreurs.append(f"chiffre {cle} : grandeur inconnue « {g} »")
            continue
        if u not in UNITES[g]:
            erreurs.append(f"chiffre {cle} : unité « {u} » incompatible avec « {g} » "
                           f"(admises : {sorted(UNITES[g])})")
        try:
            bornes(c["valeur"])
        except (TypeError, ValueError) as e:
            erreurs.append(f"chiffre {cle} : valeur invalide ({e})")
        if c["source"] not in ref.sources:
            erreurs.append(f"chiffre {cle} : source inconnue « {c['source']} »")
        if c["confiance"] not in CONFIANCES:
            erreurs.append(f"chiffre {cle} : confiance « {c['confiance']} » hors A/B/C")
        recoupements = c.get("recoupements") or []
        for r in recoupements:
            if r.get("source") not in ref.sources:
                erreurs.append(f"chiffre {cle} : recoupement, source inconnue « {r.get('source')} »")
        if c["confiance"] == "A":
            editeur = ref.sources.get(c["source"], {}).get("editeur")
            independants = [r for r in recoupements
                            if ref.sources.get(r.get("source"), {}).get("editeur") not in (None, editeur)
                            and r.get("independant", True)]
            if not independants:
                erreurs.append(f"chiffre {cle} : confiance A sans recoupement indépendant "
                               f"(autre éditeur que {editeur})")

    for k in ref.contraintes:
        a, b = k.get("inferieur", [None, None])
        if a not in ref.chiffres or b not in ref.chiffres:
            erreurs.append(f"contrainte {k} : chiffre inconnu")
            continue
        ca, cb = ref.chiffres[a], ref.chiffres[b]
        if UNITES.get(ca["grandeur"]) is not UNITES.get(cb["grandeur"]):
            erreurs.append(f"contrainte {a} ≤ {b} : grandeurs non comparables")
            continue
        if en_base(ca)[1] > en_base(cb)[0]:
            erreurs.append(f"contrainte non tenue : {a} ({ca['valeur']} {ca['unite']}) "
                           f"≤ {b} ({cb['valeur']} {cb['unite']}) — {k.get('motif', '')}")
    return erreurs


def exporter(ref: Referentiel, chemin: Path) -> None:
    """Export JSON pour le site : chaque chiffre avec sa source dépliée."""
    sortie = {
        "chiffres": {
            cle: {**c, "source": {"cle": c["source"], **ref.sources[c["source"]]}}
            for cle, c in ref.chiffres.items()
        },
    }
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=str) + "\n",
                      encoding="utf-8")
