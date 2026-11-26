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
  tiennent après conversion d'unités ;
- un chiffre calculé par le pipeline (`produit_par: pc build`, voir
  `pc/export_quand.py`) décrit son calcul et n'écrase aucun chiffre saisi
  (`fusionner`).
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
    "nombre": {"sites": 1.0, "projets": 1.0, "heures": 1.0, "déclarants": 1.0, "pays": 1.0,
               "postes": 1.0, "départements": 1.0, "zones": 1.0},
    # Carbone (« Quel carbone ? ») : une grandeur par famille de facteur, pour qu'aucune contrainte ne
    # compare un facteur moyen à un facteur marginal, à un paramètre de marché ou à un forfait
    # réglementaire. 1 MJ = 1/3,6 kWh : 1 gCO2eq/MJ = 3,6 gCO2eq/kWh.
    "intensite_moyenne": {"gCO2/kWh": 1.0, "gCO2eq/kWh": 1.0, "gCO2eq/MJ": 3.6},
    "contenu_marginal": {"gCO2/kWh": 1.0},  # contenu CO2 marginal publié (note ADEME-RTE de 2007)
    "facteur_emission_filiere": {"gCO2eq/kWh": 1.0},  # émissions d'une filière par kWh qu'elle produit
    "facteur_emission_marche": {"tCO2/MWh": 1.0},  # sensibilité du prix spot au SEQE (CRE, aides d'État)
    "valeur_forfaitaire": {"gCO2eq/MJ": 3.6, "gCO2eq/kWh": 1.0, "tCO2eq/MWh": 1000.0},  # fixée par un texte, pas une mesure
    "emissions": {"MtCO2eq": 1.0},  # émissions directes observées (inventaire)
    "emissions_evitees": {"MtCO2eq": 1.0},  # « émissions évitées » de RTE (différentiel d'intensités moyennes)
    "emissions_co2": {"MtCO2": 1.0},  # CO2 seul (AIE)
    "quotas": {"millions de quotas": 1.0},  # SEQE de l'UE, réserve de stabilité du marché
    "prix": {"€/MWh": 1.0},
    "pue": {"": 1.0},
    # Coefficient fixé par un texte, sans dimension déclarée (« 0,36 fois le prix d'un quota ») :
    # jamais un facteur d'émission.
    "coefficient_reglementaire": {"fois": 1.0},
    # Capacité pour laquelle des ouvrages sont conçus, sans engagement contractuel.
    "puissance_dimensionnement": _PUISSANCE,
    # Grandeurs du système électrique (« Quand ? »). Chacune a son propre dictionnaire d'unités :
    # une contrainte d'ordre entre deux grandeurs différentes est alors refusée (MW de marge ≠
    # MW certifiés ≠ MW installés ≠ MW appelés), même si les unités se convertissent.
    "pointe_consommation": dict(_PUISSANCE),  # puissance appelée maximale par la consommation nationale
    "charge_residuelle": dict(_PUISSANCE),  # consommation − éolien − solaire − nucléaire disponible, MW moyens horaires
    "disponibilite_moyenne": dict(_PUISSANCE),  # puissance disponible déclarée, moyenne sur une période
    "marge_adequation": dict(_PUISSANCE),  # marge par rapport au critère de sécurité d'approvisionnement (capacité équivalente, calcul probabiliste)
    "marge_certifiee": dict(_PUISSANCE),  # marge en MW certifiés du mécanisme de capacité
    "besoin_capacites": dict(_PUISSANCE),  # capacités nouvelles nécessaires au critère de sécurité d'approvisionnement (calcul d'adéquation, toute la consommation)
    "puissance_certifiee": dict(_PUISSANCE),  # capacité certifiée ou contractualisée au mécanisme de capacité
    "puissance_moyenne": dict(_PUISSANCE),  # puissance moyenne observée sur un ensemble d'heures (production, solde d'échanges)
    # Froid extrême (« Quand ? », simulateur) : hausse de la consommation par degré de baisse de
    # la température en hiver, et écart de température à la normale saisonnière.
    "gradient_thermosensibilite": {"MW/°C": 1.0, "GW/°C": 1000.0},
    "ecart_temperature": {"°C": 1.0},
}
CONFIANCES = {"A", "B", "C"}
CHAMPS_SOURCE = ("editeur", "titre", "date_publication", "url")
CHAMPS_CHIFFRE = ("libelle", "valeur", "unite", "grandeur", "periode", "perimetre",
                  "source", "page", "citation", "confiance")
#: Valeur du champ `produit_par` d'un chiffre calculé par le pipeline (et non saisi à la main) :
#: il doit alors décrire son `calcul`, porter sa valeur non arrondie (`valeur_calculee`) et le pas
#: d'arrondi de la valeur publiée (`precision`), et sa source est l'export qui le porte.
#: Un chiffre saisi peut aussi porter `precision` pour fixer son pas d'affichage (un dénombrement
#: ou un total de fichier affiché à l'unité, au lieu de l'arrondi générique à 3 chiffres significatifs).
PRODUIT_PAR_PIPELINE = "pc build"


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


def arrondi_publie(x: float, pas: float) -> float | int:
    """Arrondi au pas (0,1 ; 1…), à la moitié la plus éloignée de zéro : déterministe, sans
    l'arrondi bancaire de `round`, et reproductible en TypeScript."""
    from decimal import ROUND_HALF_UP, Decimal
    q = Decimal(str(pas))
    v = Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)
    return int(v) if q == q.to_integral() else float(v)


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
        if c.get("produit_par") is not None:
            if c["produit_par"] != PRODUIT_PAR_PIPELINE:
                erreurs.append(f"chiffre {cle} : produit_par « {c['produit_par']} » inconnu")
            if not c.get("calcul"):
                erreurs.append(f"chiffre {cle} : chiffre calculé sans « calcul »")
            # valeur publiée = arrondi de la valeur calculée (non arrondie, lue dans l'export)
            if c.get("valeur_calculee") is None or not c.get("precision"):
                erreurs.append(f"chiffre {cle} : chiffre calculé sans « valeur_calculee » ni « precision »")
            elif c["valeur"] != arrondi_publie(c["valeur_calculee"], c["precision"]):
                erreurs.append(f"chiffre {cle} : valeur {c['valeur']} ≠ arrondi au pas {c['precision']} de "
                               f"{c['valeur_calculee']}")
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


def fusionner(ref: Referentiel, sources: dict[str, dict], chiffres: dict[str, dict]) -> Referentiel:
    """Référentiel saisi + chiffres calculés par le pipeline (`produit_par: pc build`).

    Un identifiant ou une clé de source déjà présents dans le référentiel saisi lèvent une
    erreur : un chiffre calculé ne remplace jamais en silence un chiffre saisi.
    """
    doublons = sorted(set(chiffres) & set(ref.chiffres)) + sorted(set(sources) & set(ref.sources))
    if doublons:
        raise ValueError(f"identifiants calculés déjà présents dans le référentiel : {doublons}")
    sans_marque = sorted(k for k, c in chiffres.items() if c.get("produit_par") != PRODUIT_PAR_PIPELINE)
    if sans_marque:
        raise ValueError(f"chiffres calculés sans « produit_par: {PRODUIT_PAR_PIPELINE} » : {sans_marque}")
    return Referentiel(sources={**ref.sources, **sources}, chiffres={**ref.chiffres, **chiffres},
                       contraintes=list(ref.contraintes))


def exporter(ref: Referentiel, chemin: Path) -> None:
    """Export JSON pour le site : chaque chiffre avec sa source dépliée."""
    sortie = {
        "chiffres": {
            cle: {**c, "source": {"cle": c["source"], **ref.sources[c["source"]]}}
            for cle, c in ref.chiffres.items()
        },
        # Toutes les sources du référentiel, citées ou non par un chiffre : une enquête peut renvoyer
        # à une source sans chiffre (`{{source:cle|page}}`, citation de texte réglementaire…).
        "sources": {cle: {"cle": cle, **s} for cle, s in ref.sources.items()},
    }
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=str) + "\n",
                      encoding="utf-8")
