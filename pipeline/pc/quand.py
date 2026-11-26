"""Indicateurs de l'enquête « Quand ? » — implémentation de référence, en Python pur.

Ce module ne dépend que de la bibliothèque standard : le simulateur du site (TypeScript) le
réimplémentera et devra donner les mêmes résultats sur les cas de test partagés
(`tests/cas_quand.json`). Toute règle de calcul (arrondi, égalité, ordre, quantile) est donc
écrite ici explicitement, sans s'en remettre au comportement d'une bibliothèque.

Entrée : une **table horaire** d'une année, sous forme de colonnes (dict de listes de même
longueur), une ligne par heure UTC :

- `heure_utc` : début de l'heure, chaîne ISO 8601 en UTC (`"2025-01-14T07:00Z"`) ;
- `consommation`, `eolien`, `solaire`, `nucleaire`, `nucleaire_disponible` : MW moyens sur
  l'heure (= MWh de l'heure) ; `None` = donnée absente, jamais imputée ;
- `prix` : EUR/MWh (day-ahead France), ou `None` ;
- facultatif, pour la couverture des heures tendues : les colonnes de `COMPOSANTES`.

Indicateurs (décision du 26/11/2026, making-of/DECISIONS.md) :

- **I1, charge résiduelle nette du nucléaire disponible** :
  `RN = consommation − éolien − solaire − nucléaire disponible déclaré (REMIT)`, en MW. Carte
  des heures tendues, **pas** une marge : ce qui doit venir de l'hydraulique, du thermique, des
  échanges, du stockage et des effacements ;
- **I2, nucléaire déclaré disponible et non produit** :
  `J = max(0, nucléaire disponible − nucléaire produit)`, en MW. **Borne haute**, avec la
  disponibilité déclarée par EDF, de ce qu'une charge ajoutée trouverait sans autre moyen (voir
  `LIMITES_J`), jamais appelée « modulation » ;
- **I2 réintégré** (si la table a la colonne `nucleaire_disponible_reintegre`, `COLONNE_REINTEGRE`) :
  `J_r = max(0, disponible réintégré − nucléaire produit)`, où le disponible réintégré est
  reconstruit avec les mêmes règles en ignorant les arrêts et baisses **courts** (moins de 7 jours)
  qu'EDF déclare indisponibles **pour modulation** (pc/remit.py, `MOTIF_MODULATION`,
  `DUREE_MAX_COURT_H`) ; les arrêts longs, qui peuvent relever de la gestion du combustible, restent retranchés. J_r ≥ J à
  toute heure. J dépend de ce
  qu'EDF déclare indisponible : J_r en donne la sensibilité. Ni l'un ni l'autre n'est une capacité
  physique : la contrainte d'énergie (combustible, calendrier des arrêts) reste la limite nette ;
- **charge plate de X MW** : part de son énergie qui tiendrait dans J, et nombre d'heures où
  `RN + X` dépasse le RN maximal observé de l'année (un écart à l'observé, pas une défaillance) ;
- **simulateur** (`simuler`, docs/SIMULATEUR.md) : la même charge, effacée pendant les N heures
  de RN la plus élevée, et ce qu'elle rencontre (J, maximum observé, prix observés) ; en option,
  un froid supplémentaire de F °C pendant les `DUREE_FROID_H` heures consécutives de RN observée
  la plus élevée (`episode_froid`), qui ajoute F × gradient à la consommation de ces heures.

Conventions communes (à reproduire à l'identique) :

- une heure est **valide** pour un indicateur si toutes ses entrées sont renseignées ; les
  sommes et moyennes portent sur les heures valides, et leur nombre est rendu ;
- énergie : Σ des MW moyens horaires × 1 h = MWh ; TWh = MWh / 10⁶ ;
- heure de Paris : conversion de l'instant UTC dans le fuseau `Europe/Paris` (heure légale) ;
  l'heure de Paris *h* désigne l'intervalle [h, h+1[ ;
- quantiles : interpolation linéaire entre rangs (type 7 de Hyndman et Fan, défaut de numpy
  et de R) sur les valeurs triées par ordre croissant ;
- classement des heures tendues : RN décroissant, puis `heure_utc` croissante en cas d'égalité ;
- comparaisons strictes là où c'est écrit (`RN + X > RN max`, prix `< 0`) ; `J ≥ X` au sens large.
"""

from __future__ import annotations

from datetime import datetime, timezone
from math import floor
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")

#: Charges plates testées, en MW (0,5 ; 1 ; 2 ; 5 ; 10 ; 15 ; 20 GW).
CHARGES_PLATES_MW = (500, 1000, 2000, 5000, 10000, 15000, 20000)

#: Nombre d'heures tendues retenues par année (RN la plus élevée).
N_HEURES_TENDUES = 100

#: Monotone sous-échantillonnée : les `N_MONOTONE_EXACT` premiers rangs exacts, puis un rang
#: sur `PAS_MONOTONE`, et toujours le dernier rang.
N_MONOTONE_EXACT = 100
PAS_MONOTONE = 20

#: Quantiles de RN publiés (clé → probabilité).
QUANTILES = {"p01": 0.01, "p05": 0.05, "p10": 0.10, "p25": 0.25, "p50": 0.50,
             "p75": 0.75, "p90": 0.90, "p95": 0.95, "p99": 0.99}

#: Mois d'hiver (heure de Paris). « Hiver » = novembre-mars, comme la période de livraison du
#: mécanisme de capacité et la synthèse hivernale de RTE ; le trimestre décembre-février est
#: rendu à part.
MOIS_HIVER = (11, 12, 1, 2, 3)
MOIS_DEC_FEV = (12, 1, 2)

#: Plages de pointe, heures de Paris de début : [7 h, 11 h[ et [17 h, 21 h[ (plages du spike),
#: et plages PP du mécanisme de capacité 2026/2027, [7 h, 10 h[ et [17 h, 20 h[ (RTE, BP2025,
#: « Fonctionnement », note 38 p. 30).
PLAGES_POINTE = (7, 8, 9, 10, 17, 18, 19, 20)
PLAGES_PP_RTE = (7, 8, 9, 17, 18, 19)

#: Ce qui couvre RN aux heures tendues : colonnes éCO2mix (MW moyens). Par construction,
#: consommation = Σ production + pompage + solde des échanges + écart de bilan, d'où
#: RN = Σ COMPOSANTES + (nucléaire produit − disponible) + écart de bilan.
#: - `hydraulique` d'éCO2mix = fil de l'eau et éclusées + lacs + turbinage des STEP
#:   (vérifié sur 2015-2026, à 2 MW près d'arrondi) : on rend les trois sous-filières ;
#: - `pompage` : consommation des STEP en pompage, **négative** (exclue de `consommation`) ;
#: - `ech_physiques` : solde des échanges physiques, **positif = import** ; négatif, la France
#:   exporte : ses moyens couvrent alors RN **et** les exports, et le terme est retranché.
COMPOSANTES = (
    "hydraulique_fil_eau_eclusee", "hydraulique_lacs", "hydraulique_step_turbinage",
    "gaz", "charbon", "fioul", "bioenergies", "pompage", "ech_physiques",
)

#: Plancher retranché à J pour la sensibilité `part_dans_j_plancher` (MW) : **hypothèse du site**,
#: pas une donnée. J reste le plus souvent au-dessus de zéro, même aux heures les plus chères (réserves FCR et aFRR
#: portées par le parc, rampes de redémarrage, fins de cycle, décalage entre déclaration et
#: puissance réelle) : J' = max(0, J − plancher) écarte cette part non mobilisable.
PLANCHER_J_MW = 1000

#: Durée de l'épisode de froid du simulateur, en heures consécutives de la table : **choix du site**
#: (une semaine, jours ouvrés et week-end compris ; RTE qualifie de « longue » la vague de février
#: 2012 sans en donner la durée). Voir `episode_froid` et docs/SIMULATEUR.md.
DUREE_FROID_H = 168

#: Seuil de prix day-ahead (EUR/MWh) au-dessus duquel une heure est dite « chère » : **choisi par
#: le site** pour montrer que J reste positif quand le système manque d'énergie (`prix_chers`).
SEUIL_PRIX_CHER_EUR_MWH = 150

#: Colonne facultative : nucléaire disponible déclaré en réintégrant les arrêts courts pour modulation (MW).
COLONNE_REINTEGRE = "nucleaire_disponible_reintegre"


#: Grandeurs des charges plates recalculées avec J_r (`jeu_nucleaire_reintegre.charges_plates`).
CLES_CHARGE_REINTEGRE = ("x_mw", "energie_dans_j_twh", "part_dans_j", "heures_j_superieur_ou_egal_x",
                         "energie_dans_j_plancher_twh", "part_dans_j_plancher")

#: Limites de I2, portées en clair dans l'export.
LIMITES_J = (
    "borne haute : une partie du nucléaire disponible est réservée aux services système "
    "(réserves primaire et secondaire), elle n'est pas mobilisable pour une charge ajoutée",
    "plancher : J ne tombe pas à zéro, même aux heures les plus chères (réserves, rampes de "
    "redémarrage, fins de cycle, décalage entre déclaration et puissance réelle) ; cette part "
    "n'est pas mobilisable. `part_dans_j_plancher` retranche à J un plancher uniforme "
    "(`PLANCHER_J_MW`, hypothèse du site) ; `jeu_nucleaire.prix_chers` donne J moyen aux heures "
    "où le prix dépasse `SEUIL_PRIX_CHER_EUR_MWH`",
    "contrainte d'énergie : J est une marge en puissance heure par heure, pas un gisement "
    "d'énergie annuel. Le combustible et le calendrier des arrêts plafonnent la production de "
    "l'année ; une baisse de production pour économiser le combustible déplace de l'énergie dans "
    "le temps. `energie_dans_j_twh` serait du nucléaire produit EN PLUS de la production observée, "
    "à comparer aux prévisions de production de l'exploitant et de RTE",
    "qui servirait la charge ajoutée (nucléaire inemployé, moins d'exports, autres moyens) dépend "
    "de la saturation des interconnexions : non déterminable sans les données des voisins",
    "disponibilité DÉCLARÉE par EDF (REMIT) : la frontière entre indisponibilité et modulation "
    "est fixée par EDF. Depuis 2019, EDF déclare indisponibles des arrêts et baisses « pour "
    "modulation », qui sortent de J. J est donc une borne haute AVEC LA DISPONIBILITÉ DÉCLARÉE. "
    "Les arrêts courts (moins de 7 jours), décidés au jour le jour (« la tranche sera redémarrée "
    "si les conditions économiques le justifient »), sont économiques : `jeu_nucleaire_reintegre` "
    "recalcule J en les réintégrant (J_r ≥ J), sensibilité au choix de déclaration d'EDF, pas une "
    "capacité physique. Les arrêts longs pour modulation (une semaine à plusieurs mois, souvent "
    "annoncés des semaines ou des mois à l'avance) et les arrêts pour économie de combustible "
    "peuvent relever de la gestion du combustible : ils restent retranchés",
    "J n'est pas la « modulation » publiée par EDF ou RTE (périmètre et méthode différents) : "
    "seul l'ordre de grandeur se compare",
)


# --------------------------------------------------------------------------
# Briques
# --------------------------------------------------------------------------


def instant_utc(iso: str) -> datetime:
    """Instant UTC d'une chaîne ISO 8601 (`2025-01-14T07:00Z` ou avec décalage explicite)."""
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError(f"heure sans fuseau : {iso}")
    return t.astimezone(timezone.utc)


def heure_paris(iso: str) -> datetime:
    """Même instant en heure légale de Paris."""
    return instant_utc(iso).astimezone(PARIS)


def charge_residuelle(consommation, eolien, solaire, nucleaire_disponible) -> float | None:
    """RN (MW) d'une heure, ou None si une entrée manque."""
    if None in (consommation, eolien, solaire, nucleaire_disponible):
        return None
    return consommation - eolien - solaire - nucleaire_disponible


def jeu_nucleaire(nucleaire_disponible, nucleaire) -> float | None:
    """J (MW) d'une heure : disponible déclaré non produit, borné à 0 ; None si une entrée manque."""
    if nucleaire_disponible is None or nucleaire is None:
        return None
    return max(0.0, nucleaire_disponible - nucleaire)


def quantile(tries: list[float], q: float) -> float:
    """Quantile d'ordre q de valeurs **triées par ordre croissant** (type 7, interpolation linéaire)."""
    if not tries:
        raise ValueError("quantile d'une liste vide")
    h = (len(tries) - 1) * q
    i = floor(h)
    if i + 1 >= len(tries):
        return float(tries[-1])
    return tries[i] + (h - i) * (tries[i + 1] - tries[i])


def monotone(valeurs: list[float], n_exact: int = N_MONOTONE_EXACT, pas: int = PAS_MONOTONE) -> list[list]:
    """Monotone décroissante sous-échantillonnée : liste de [rang (1 = la plus élevée), valeur].

    Rangs 1 à `n_exact` exacts, puis `n_exact + pas`, `n_exact + 2 pas`… et toujours le dernier.
    """
    d = sorted(valeurs, reverse=True)
    n = len(d)
    rangs = list(range(1, min(n_exact, n) + 1))
    r = n_exact + pas
    while r <= n:
        rangs.append(r)
        r += pas
    if n and rangs[-1] != n:
        rangs.append(n)
    return [[r, d[r - 1]] for r in rangs]


def _moyenne(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def _instant(heures_utc: list[str], i: int, rn: float) -> dict:
    p = heure_paris(heures_utc[i])
    return {"valeur_mw": rn, "heure_utc": heures_utc[i], "debut_paris": p.isoformat(timespec="minutes")}


def charge_plate(rn: list, j: list, x_mw: float, heures: int | None = None, solde: list | None = None,
                 plancher_mw: float = PLANCHER_J_MW, rn_max_reference_mw: float | None = None) -> dict:
    """Effet d'une consommation supplémentaire constante de `x_mw` MW sur une année.

    - `energie_ajoutee_twh` = X × heures de l'année (toutes les heures de la table) ;
    - `part_dans_j` = Σ min(X, J) / (X × heures où J est renseigné) : part de l'énergie ajoutée
      qui tiendrait dans le nucléaire disponible non produit (**au plus**, avec la disponibilité
      déclarée par EDF, voir `LIMITES_J`) ;
    - `heures_j_superieur_ou_egal_x` : heures où J ≥ X (la charge y tiendrait entièrement) ;
    - `heures_rn_plus_x_au_dessus_du_max` : heures où RN + X > max(RN), max pris sur l'année
      observée (un écart à l'observé, pas une défaillance) ; `rn_max_plus_x_mw` ;
    - `solde_echanges_moyen_heures_j_ge_x_mw` : solde moyen des échanges physiques (`solde`,
      positif = import, négatif = export) aux heures où J ≥ X et où le solde est renseigné ;
      None sans solde ou sans telle heure. Négatif : à ces heures, la France exporte déjà ;
    - `energie_dans_j_plancher_twh`, `part_dans_j_plancher` : mêmes calculs avec
      J' = max(0, J − `plancher_mw`) (sensibilité au plancher non mobilisable, hypothèse du site) ;
    - `heures_rn_plus_x_au_dessus_du_max_reference` : heures où RN + X > `rn_max_reference_mw`
      (strictement), un seuil fixé hors de l'année (maximum pluriannuel) ; None sans seuil.
    """
    if x_mw <= 0:
        raise ValueError("charge plate nulle ou négative")
    heures = len(rn) if heures is None else heures
    jv = [v for v in j if v is not None]
    rnv = [v for v in rn if v is not None]
    tenu = sum(min(x_mw, v) for v in jv)
    tenu_plancher = sum(min(x_mw, max(0.0, v - plancher_mw)) for v in jv)
    rn_max = max(rnv) if rnv else None
    soldes = [] if solde is None else [e for v, e in zip(j, solde) if v is not None and e is not None and v >= x_mw]
    return {
        "x_mw": x_mw,
        "energie_ajoutee_twh": x_mw * heures / 1e6,
        "energie_dans_j_twh": tenu / 1e6,
        "part_dans_j": tenu / (x_mw * len(jv)) if jv else None,
        "heures_j_superieur_ou_egal_x": sum(1 for v in jv if v >= x_mw),
        "rn_max_plus_x_mw": None if rn_max is None else rn_max + x_mw,
        "heures_rn_plus_x_au_dessus_du_max": None if rn_max is None else sum(1 for v in rnv if v + x_mw > rn_max),
        "solde_echanges_moyen_heures_j_ge_x_mw": _moyenne(soldes),
        "plancher_mw": plancher_mw,
        "energie_dans_j_plancher_twh": tenu_plancher / 1e6,
        "part_dans_j_plancher": tenu_plancher / (x_mw * len(jv)) if jv else None,
        "heures_rn_plus_x_au_dessus_du_max_reference": None if rn_max_reference_mw is None
        else sum(1 for v in rnv if v + x_mw > rn_max_reference_mw),
    }


# --------------------------------------------------------------------------
# Simulateur : une charge ajoutée heure par heure
# --------------------------------------------------------------------------


def classement_tendues(heures_utc: list[str], rn: list) -> list[int]:
    """Indices des heures où RN est renseignée, de la plus tendue à la moins tendue (RN
    décroissant, puis `heure_utc` croissante en cas d'égalité : même ordre que les heures tendues)."""
    return sorted((i for i in range(len(rn)) if rn[i] is not None), key=lambda i: (-rn[i], heures_utc[i]))


def profil_effacement(heures_utc: list[str], rn: list, x_mw: float, heures_effacement: int = 0) -> list[float]:
    """Charge ajoutée heure par heure : X partout, 0 pendant les `heures_effacement` heures **valides**
    (RN renseignée) où RN observée est la plus élevée (`classement_tendues`).

    Prévision parfaite : l'effacement tombe exactement sur les heures les plus tendues de l'année
    observée, ce qu'aucun opérateur ne sait faire (borne optimiste). Une heure où RN manque n'est pas
    classée : la charge y reste X. Au-delà du nombre d'heures valides, toutes les heures valides sont
    effacées.
    """
    if x_mw < 0:
        raise ValueError("puissance ajoutée négative")
    if heures_effacement < 0 or int(heures_effacement) != heures_effacement:
        raise ValueError("nombre d'heures d'effacement négatif ou non entier")
    charge = [float(x_mw)] * len(rn)
    for i in classement_tendues(heures_utc, rn)[:int(heures_effacement)]:
        charge[i] = 0.0
    return charge


def _dans_j(js: list, charge: list[float], plancher_mw: float) -> dict:
    """Part d'une charge (MW par heure) qui tient dans `js` (J laissé à la charge, None = absent) :
    mêmes règles que le point 2 d'`effet_charge`, pour la variante réintégrée."""
    ij = [i for i in range(len(js)) if js[i] is not None]
    base = sum(charge[i] for i in ij)
    tenu = sum(min(charge[i], js[i]) for i in ij)
    tenu_plancher = sum(min(charge[i], max(0.0, js[i] - plancher_mw)) for i in ij)
    return {
        "energie_dans_j_twh": tenu / 1e6,
        "part_dans_j": tenu / base if base > 0 else None,
        "energie_dans_j_plancher_twh": tenu_plancher / 1e6,
        "part_dans_j_plancher": tenu_plancher / base if base > 0 else None,
        "heures_j_couvre_charge": sum(1 for i in ij if charge[i] > 0 and js[i] >= charge[i]),
    }


def effet_charge(heures_utc: list[str], rn: list, j: list, prix: list, charge: list[float],
                 solde: list | None = None, n_exact: int = N_MONOTONE_EXACT, pas: int = PAS_MONOTONE,
                 plancher_mw: float = PLANCHER_J_MW, rn_max_reference_mw: float | None = None,
                 supplement: list[float] | None = None, j_reintegre: list | None = None) -> dict:
    """Ce qu'une charge ajoutée `charge` (MW par heure, une valeur par heure, jamais None) rencontre
    dans une année observée. Généralise `charge_plate` (charge constante) à un profil quelconque.

    `supplement` (MW par heure, ≥ 0, défaut 0 partout) : consommation qui s'ajoute à l'observé sans
    être la charge ajoutée (le froid supplémentaire du simulateur). Elle s'ajoute à RN **après**
    (RN + supplément + charge) mais pas aux seuils, qui restent observés (`rn_max_mw`, seuil de
    référence) ni à `monotone_avant` (RN observée) ; elle passe **avant** la charge dans J : la
    charge ne trouve que J_s = max(0, J − supplément) (même nucléaire inemployé, pas deux fois).
    Avec un supplément nul, toutes les sorties sont celles d'avant (aucun chiffre publié ne change).

    1. `energie_ajoutee_twh` = Σ charge, toutes les heures de la table ;
    2. `part_dans_j` = Σ min(charge, J) / Σ charge, sommes sur les heures où J est renseigné :
       part qui tiendrait **au plus**, avec la disponibilité déclarée, dans le nucléaire disponible
       non produit (`LIMITES_J` ; variante réintégrée au point 6) ; None
       si la charge y est nulle. `heures_j_couvre_charge` : heures où charge > 0 et J ≥ charge ;
       `solde_echanges_moyen_heures_j_couvre_mw` : solde moyen des échanges (positif = import) à
       ces heures, quand il est renseigné. Constat, pas causalité : qui servirait la charge
       ajoutée dépend de la saturation des interconnexions (`LIMITES_J`) ;
       `part_dans_j_plancher`, `energie_dans_j_plancher_twh` : mêmes calculs avec
       J' = max(0, J − `plancher_mw`) (plancher non mobilisable, hypothèse du site) ;
    3. sur les heures où RN est renseignée : `rn_max_mw` (maximum observé) et `rn_max_heure_utc` (son
       heure, même départage que les heures tendues), `max_apres` (maximum de
       RN + charge, même départage que les heures tendues), `heures_au_dessus_du_max` = heures où
       RN + charge > RN max observé (strictement : un écart à l'observé, pas une défaillance ; dès
       que la charge est positive à l'heure du maximum, cette heure-là compte) ;
       `heures_au_dessus_du_max_reference` : heures où RN + charge > `rn_max_reference_mw`, seuil
       fixé hors de l'année (maximum pluriannuel) ; None sans seuil ;
    4. sur les heures où le prix est renseigné : `part_prix_negatif` (prix < 0),
       `part_prix_nul_ou_negatif` (prix ≤ 0), parts de l'énergie ajoutée ; `prix_moyen_pondere_eur_mwh`
       = Σ charge × prix / Σ charge (prix **observé**, sans effet en retour de la charge ajoutée ; non
       affiché par le site, qui le lirait comme une économie : relecture du simulateur, SF5) ;
       `prix_moyen_eur_mwh` = moyenne simple des prix (ce que paierait une charge plate) ; None si
       la charge y est nulle ; `heures_prix_nul_ou_negatif_charge` : heures à prix ≤ 0 où la charge
       est positive, dont `heures_prix_nul_ou_negatif_j_couvre` où J ≥ charge ;
    5. `monotone_avant`, `monotone_apres` : monotones de RN et de RN + charge (chacune triée pour
       elle-même), sous-échantillonnées comme `monotone`.
    6. `reintegre` : si `j_reintegre` (J_r, une valeur par heure, None = absent) est donné, les
       grandeurs du point 2 recalculées avec J_r (même supplément retranché d'abord) :
       `energie_dans_j_twh`, `part_dans_j`, `energie_dans_j_plancher_twh`, `part_dans_j_plancher`,
       `heures_j_couvre_charge` ; None sinon. RN et les autres sorties ne changent pas.
    """
    n = len(heures_utc)
    for nom, v in (("rn", rn), ("j", j), ("prix", prix), ("charge", charge)):
        if len(v) != n:
            raise ValueError(f"{nom} : {len(v)} valeurs pour {n} heures")
    if any(c is None or c < 0 for c in charge):
        raise ValueError("charge ajoutée absente ou négative")
    supplement = [0.0] * n if supplement is None else supplement
    if len(supplement) != n or any(v is None or v < 0 for v in supplement):
        raise ValueError("supplément absent, négatif ou de mauvaise longueur")
    solde = [None] * n if solde is None else solde
    # J laissé à la charge après le supplément (identique à J sans supplément)
    js = [None if j[i] is None else (j[i] if supplement[i] == 0 else max(0.0, j[i] - supplement[i]))
          for i in range(n)]
    if j_reintegre is not None and len(j_reintegre) != n:
        raise ValueError(f"j_reintegre : {len(j_reintegre)} valeurs pour {n} heures")
    reintegre = None if j_reintegre is None else _dans_j(
        [None if v is None else (v if supplement[i] == 0 else max(0.0, v - supplement[i]))
         for i, v in enumerate(j_reintegre)], charge, plancher_mw)

    # 2. Nucléaire disponible non produit
    ij = [i for i in range(n) if js[i] is not None]
    base_j = sum(charge[i] for i in ij)
    tenu = sum(min(charge[i], js[i]) for i in ij)
    tenu_plancher = sum(min(charge[i], max(0.0, js[i] - plancher_mw)) for i in ij)
    couvre = [i for i in ij if charge[i] > 0 and js[i] >= charge[i]]
    soldes = [solde[i] for i in couvre if solde[i] is not None]

    # 3. Charge résiduelle
    irn = [i for i in range(n) if rn[i] is not None]
    rn_max = max((rn[i] for i in irn), default=None)
    i_rn_max = min(irn, key=lambda i: (-rn[i], heures_utc[i])) if irn else None
    apres = {i: rn[i] + supplement[i] + charge[i] for i in irn}
    i_max = min(irn, key=lambda i: (-apres[i], heures_utc[i])) if irn else None

    # 4. Prix
    ip = [i for i in range(n) if prix[i] is not None]
    base_p = sum(charge[i] for i in ip)
    bas = [i for i in ip if prix[i] <= 0 and charge[i] > 0]

    def part_prix(pred) -> float | None:
        return sum(charge[i] for i in ip if pred(prix[i])) / base_p if base_p > 0 else None

    return {
        "heures": n,
        "energie_ajoutee_twh": sum(charge) / 1e6,
        "heures_charge_nulle": sum(1 for c in charge if c == 0),
        "heures_j_valides": len(ij),
        "energie_dans_j_twh": tenu / 1e6,
        "part_dans_j": tenu / base_j if base_j > 0 else None,
        "plancher_mw": plancher_mw,
        "energie_dans_j_plancher_twh": tenu_plancher / 1e6,
        "part_dans_j_plancher": tenu_plancher / base_j if base_j > 0 else None,
        "heures_j_couvre_charge": len(couvre),
        "solde_echanges_moyen_heures_j_couvre_mw": _moyenne(soldes),
        "heures_rn_valides": len(irn),
        "rn_max_mw": rn_max,
        "rn_max_heure_utc": None if i_rn_max is None else heures_utc[i_rn_max],
        "max_apres": None if i_max is None else _instant(heures_utc, i_max, apres[i_max]),
        "heures_au_dessus_du_max": None if rn_max is None else sum(1 for i in irn if apres[i] > rn_max),
        "rn_max_reference_mw": rn_max_reference_mw,
        "heures_au_dessus_du_max_reference": None if rn_max_reference_mw is None
        else sum(1 for i in irn if apres[i] > rn_max_reference_mw),
        "heures_prix_valides": len(ip),
        "energie_prix_valide_twh": base_p / 1e6,
        "part_prix_negatif": part_prix(lambda p: p < 0),
        "part_prix_nul_ou_negatif": part_prix(lambda p: p <= 0),
        "prix_moyen_pondere_eur_mwh": sum(charge[i] * prix[i] for i in ip) / base_p if base_p > 0 else None,
        "prix_moyen_eur_mwh": _moyenne([prix[i] for i in ip]),
        "heures_prix_nul_ou_negatif_charge": len(bas),
        "heures_prix_nul_ou_negatif_j_couvre": sum(1 for i in bas if js[i] is not None and js[i] >= charge[i]),
        "monotone_avant": monotone([rn[i] for i in irn], n_exact, pas),
        "monotone_apres": monotone([apres[i] for i in irn], n_exact, pas),
        "reintegre": reintegre,
    }


def j_reintegre(table: dict[str, list]) -> list | None:
    """J_r de chaque heure (disponible réintégré non produit), ou None sans `COLONNE_REINTEGRE`."""
    if COLONNE_REINTEGRE not in table:
        return None
    return [jeu_nucleaire(d, p) for d, p in zip(table[COLONNE_REINTEGRE], table["nucleaire"])]


def episode_froid(rn: list, duree_h: int = DUREE_FROID_H) -> list[int]:
    """Indices de l'épisode de froid : les `duree_h` lignes **consécutives** de la table dont la RN
    observée moyenne (sur les heures où elle est renseignée) est la plus élevée.

    Règles (à reproduire à l'identique) : fenêtres de `duree_h` lignes, de la première à la dernière
    position possible ; moyenne = somme des RN renseignées, dans l'ordre de la table, divisée par leur
    nombre ; une fenêtre sans RN renseignée est écartée ; à égalité, la fenêtre la plus ancienne
    (comparaison stricte) ; table plus courte que `duree_h` : toute la table. Liste vide si aucune RN.
    Les lignes sont supposées horaires et contiguës (c'est le cas des tables annuelles exportées).
    """
    if duree_h <= 0 or int(duree_h) != duree_h:
        raise ValueError("durée de l'épisode de froid nulle, négative ou non entière")
    n = len(rn)
    longueur = min(int(duree_h), n)
    meilleur, m_meilleur = None, None
    for debut in range(0, n - longueur + 1):
        vals = [rn[i] for i in range(debut, debut + longueur) if rn[i] is not None]
        if not vals:
            continue
        m = sum(vals) / len(vals)
        if m_meilleur is None or m > m_meilleur:
            meilleur, m_meilleur = debut, m
    return [] if meilleur is None else list(range(meilleur, meilleur + longueur))


def simuler(table: dict[str, list], x_mw: float, heures_effacement: int = 0,
            n_exact: int = N_MONOTONE_EXACT, pas_monotone: int = PAS_MONOTONE,
            plancher_mw: float = PLANCHER_J_MW, rn_max_reference_mw: float | None = None,
            froid_c: float = 0.0, gradient_mw_par_c: float | None = None,
            duree_froid_h: int = DUREE_FROID_H) -> dict:
    """Simulateur (docs/SIMULATEUR.md) : X MW ajoutés à toutes les heures de la table, sauf
    pendant les `heures_effacement` heures valides de RN la plus élevée (`profil_effacement`).

    Mêmes entrées que `indicateurs_annee` (colonnes `heure_utc`, `consommation`, `eolien`,
    `solaire`, `nucleaire`, `nucleaire_disponible`, `prix` ; `ech_physiques` facultative). Sortie :
    celle d'`effet_charge`, plus les paramètres, `heures_effacees` (heures UTC effacées, de la plus
    tendue à la moins tendue) et `rn_seuil_effacement_mw` (RN de la moins tendue des heures effacées,
    froid compris, None sans effacement), `energie_effacee_twh` (X × heures effacées : énergie
    **perdue**, reportée ni dans le temps ni sur un autre site) et `production_nucleaire_twh` (Σ de
    la production nucléaire observée, heures renseignées). Avec `heures_effacement = 0`,
    `froid_c = 0` et X > 0, les grandeurs communes avec `charge_plate` sont identiques.

    **Froid supplémentaire** (`froid_c` °C, ≥ 0 ; `gradient_mw_par_c` obligatoire s'il est positif) :
    pendant l'épisode `episode_froid(rn, duree_froid_h)`, la consommation gagne
    `froid_ajout_mw` = froid_c × gradient à chaque heure. Ce supplément passe par `effet_charge`
    (`supplement`) : il s'ajoute à RN après, pas aux seuils observés, et passe avant la charge dans
    J. L'effacement est classé sur RN + supplément (les heures les plus tendues du scénario). Ce
    n'est **pas** un écart aux normales : l'année observée a déjà ses froids, et l'épisode tombe sur
    ses jours les plus tendus ; F °C s'ajoutent à ce qu'ils ont été. Sorties : `froid_c`,
    `gradient_mw_par_c`, `froid_ajout_mw`, `froid_heures` (nombre d'heures de l'épisode),
    `froid_debut_utc`, `froid_fin_utc` (début de la dernière heure ; None sans froid),
    `energie_froid_twh` ; et, sur les heures où la consommation est renseignée,
    `consommation_max_observee` et `consommation_max_apres` (consommation + supplément + charge),
    au format des instants (même départage que les heures tendues).

    Avec la colonne `COLONNE_REINTEGRE`, `reintegre` porte la part dans J_r (voir `effet_charge`) ;
    sans elle, `reintegre` vaut None et rien d'autre ne change.
    """
    hu = table["heure_utc"]
    n = len(hu)
    for c, v in table.items():
        if len(v) != n:
            raise ValueError(f"colonne {c} : {len(v)} valeurs pour {n} heures")
    if not froid_c >= 0:
        raise ValueError("froid supplémentaire négatif")
    if froid_c > 0 and (gradient_mw_par_c is None or not gradient_mw_par_c > 0):
        raise ValueError("froid supplémentaire sans gradient positif")
    rn = [charge_residuelle(*vals) for vals in zip(table["consommation"], table["eolien"], table["solaire"],
                                                   table["nucleaire_disponible"])]
    j = [jeu_nucleaire(d, p) for d, p in zip(table["nucleaire_disponible"], table["nucleaire"])]
    jr = j_reintegre(table)
    episode = episode_froid(rn, duree_froid_h) if froid_c > 0 else []
    ajout = froid_c * gradient_mw_par_c if froid_c > 0 else 0.0
    supplement = [0.0] * n
    for i in episode:
        supplement[i] = ajout
    # Classement des heures tendues du scénario : RN + froid (= RN observée sans froid).
    rn_s = [None if rn[i] is None else rn[i] + supplement[i] for i in range(n)]
    charge = profil_effacement(hu, rn_s, x_mw, heures_effacement)
    effacees = classement_tendues(hu, rn_s)[:int(heures_effacement)]
    r = effet_charge(hu, rn, j, table.get("prix", [None] * n), charge, table.get("ech_physiques"),
                     n_exact, pas_monotone, plancher_mw, rn_max_reference_mw, supplement, jr)
    conso = table["consommation"]
    ic = [i for i in range(n) if conso[i] is not None]
    c_apres = {i: conso[i] + supplement[i] + charge[i] for i in ic}
    i_obs = min(ic, key=lambda i: (-conso[i], hu[i])) if ic else None
    i_apres = min(ic, key=lambda i: (-c_apres[i], hu[i])) if ic else None
    return {
        "x_mw": x_mw,
        "heures_effacement": int(heures_effacement),
        "heures_effacees": [hu[i] for i in effacees],
        "rn_seuil_effacement_mw": rn_s[effacees[-1]] if effacees else None,
        "energie_effacee_twh": x_mw * len(effacees) / 1e6,
        "production_nucleaire_twh": sum(v for v in table["nucleaire"] if v is not None) / 1e6,
        "froid_c": froid_c,
        "gradient_mw_par_c": gradient_mw_par_c,
        "froid_ajout_mw": ajout,
        "froid_heures": len(episode),
        "froid_debut_utc": hu[episode[0]] if episode else None,
        "froid_fin_utc": hu[episode[-1]] if episode else None,
        "energie_froid_twh": ajout * len(episode) / 1e6,
        "consommation_max_observee": None if i_obs is None else _instant(hu, i_obs, conso[i_obs]),
        "consommation_max_apres": None if i_apres is None else _instant(hu, i_apres, c_apres[i_apres]),
        **r,
    }


# --------------------------------------------------------------------------
# Indicateurs d'une année
# --------------------------------------------------------------------------


def indicateurs_annee(table: dict[str, list], charges_mw=CHARGES_PLATES_MW, n_tendues: int = N_HEURES_TENDUES,
                      n_exact: int = N_MONOTONE_EXACT, pas_monotone: int = PAS_MONOTONE,
                      plancher_j_mw: float = PLANCHER_J_MW, seuil_prix_cher_eur_mwh: float = SEUIL_PRIX_CHER_EUR_MWH,
                      rn_max_reference_mw: float | None = None) -> dict:
    """Tous les indicateurs « Quand ? » d'une table horaire (en général une année civile, heure de Paris).

    Sorties en unités de base : MW (moyens horaires), TWh, nombres d'heures, parts entre 0 et 1.
    Aucun arrondi : l'export arrondit. `rn_max_reference_mw` : seuil extérieur à l'année (en
    pratique le maximum pluriannuel, `max_pluriannuel`) pour `heures_rn_plus_x_au_dessus_du_max_reference`.
    `jeu_nucleaire.prix_chers` : J moyen aux heures où le prix est strictement supérieur à
    `seuil_prix_cher_eur_mwh` et J renseigné, et le nombre de ces heures.

    Avec la colonne `COLONNE_REINTEGRE`, `jeu_nucleaire_reintegre` : J_r (heures valides, Σ en TWh,
    heures positives, moyenne), `arrets_modulation_courts_twh` = Σ (disponible réintégré −
    disponible déclaré) sur les heures où les deux sont renseignés (énergie que les arrêts courts
    pour modulation retirent de la disponibilité déclarée, chevauchements traités ; l'énergie des
    arrêts longs est ajoutée par pc/export_quand.py), et `charges_plates` : les
    grandeurs `CLES_CHARGE_REINTEGRE` de `charge_plate` calculées avec J_r. Sans la colonne, la
    clé est absente.
    """
    hu = table["heure_utc"]
    n = len(hu)
    for c, v in table.items():
        if len(v) != n:
            raise ValueError(f"colonne {c} : {len(v)} valeurs pour {n} heures")
    paris = [heure_paris(h) for h in hu]
    rn = [charge_residuelle(*vals) for vals in zip(table["consommation"], table["eolien"], table["solaire"],
                                                   table["nucleaire_disponible"])]
    j = [jeu_nucleaire(d, p) for d, p in zip(table["nucleaire_disponible"], table["nucleaire"])]

    # I1 — charge résiduelle
    idx_rn = [i for i in range(n) if rn[i] is not None]
    rnv = [rn[i] for i in idx_rn]
    cr: dict = {"heures_valides": len(rnv)}
    if rnv:
        tries = sorted(rnv)
        i_max = min(idx_rn, key=lambda i: (-rn[i], hu[i]))
        i_min = min(idx_rn, key=lambda i: (rn[i], hu[i]))
        cr.update({
            "max": _instant(hu, i_max, rn[i_max]),
            "min": _instant(hu, i_min, rn[i_min]),
            "moyenne_mw": _moyenne(rnv),
            "quantiles_mw": {k: quantile(tries, q) for k, q in QUANTILES.items()},
            "heures_negatives": sum(1 for v in rnv if v < 0),
            "monotone": monotone(rnv, n_exact, pas_monotone),
        })

    # Heures tendues : les n_tendues heures de RN la plus élevée
    top = sorted(idx_rn, key=lambda i: (-rn[i], hu[i]))[:n_tendues]
    par_mois = [0] * 12
    par_heure = [0] * 24
    for i in top:
        par_mois[paris[i].month - 1] += 1
        par_heure[paris[i].hour] += 1

    def part(pred) -> float | None:
        return sum(1 for i in top if pred(paris[i])) / len(top) if top else None

    couverture: dict = {}
    complets = [i for i in top if all(table.get(c, [None] * n)[i] is not None for c in COMPOSANTES)
                and table["nucleaire"][i] is not None]
    for c in COMPOSANTES:
        couverture[c] = _moyenne([table[c][i] for i in complets])
    couverture["nucleaire_produit_moins_disponible"] = _moyenne(
        [table["nucleaire"][i] - table["nucleaire_disponible"][i] for i in complets])
    couverture["ecart_bilan_eco2mix"] = _moyenne(
        [rn[i] - sum(table[c][i] for c in COMPOSANTES) - (table["nucleaire"][i] - table["nucleaire_disponible"][i])
         for i in complets])
    tendues = {
        "n": len(top),
        "rn_moyenne_mw": _moyenne([rn[i] for i in top]),
        "rn_min_mw": min((rn[i] for i in top), default=None),
        "par_mois": par_mois,
        "par_heure_paris": par_heure,
        "part_hiver_nov_mars": part(lambda p: p.month in MOIS_HIVER),
        "part_dec_fev": part(lambda p: p.month in MOIS_DEC_FEV),
        "part_plages_7_11_17_21": part(lambda p: p.hour in PLAGES_POINTE),
        "part_plages_pp_rte": part(lambda p: p.hour in PLAGES_PP_RTE),
        "heures_couverture": len(complets),
        "couverture_moyenne_mw": couverture,
        "heures": [[hu[i], rn[i]] for i in top],
    }

    # I2 — nucléaire disponible non produit
    jv = [v for v in j if v is not None]
    j_mois = [0.0] * 12
    for i in range(n):
        if j[i] is not None:
            j_mois[paris[i].month - 1] += j[i]
    jeu = {
        "heures_valides": len(jv),
        "somme_twh": sum(jv) / 1e6,
        "par_mois_twh": [x / 1e6 for x in j_mois],
        "heures_positif": sum(1 for v in jv if v > 0),
        "moyenne_mw": _moyenne(jv),
    }
    prix = table.get("prix", [None] * n)
    cheres = [j[i] for i in range(n) if prix[i] is not None and j[i] is not None and prix[i] > seuil_prix_cher_eur_mwh]
    jeu["prix_chers"] = {"seuil_eur_mwh": seuil_prix_cher_eur_mwh, "heures": len(cheres),
                         "j_moyenne_mw": _moyenne(cheres)}

    # Prix nuls ou négatifs
    ip = [i for i in range(n) if prix[i] is not None]
    neg = [i for i in ip if prix[i] < 0]
    nul_neg = [i for i in ip if prix[i] <= 0]
    prix_bas = {
        "heures_valides": len(ip),
        "heures_negatif": len(neg),
        "heures_nul_ou_negatif": len(nul_neg),
        "rn_moyenne_prix_negatif_mw": _moyenne([rn[i] for i in neg if rn[i] is not None]),
        "rn_moyenne_prix_nul_ou_negatif_mw": _moyenne([rn[i] for i in nul_neg if rn[i] is not None]),
        "j_moyenne_prix_negatif_mw": _moyenne([j[i] for i in neg if j[i] is not None]),
    }

    sortie = {
        "heures": n,
        "charge_residuelle": cr,
        "heures_tendues": tendues,
        "jeu_nucleaire": jeu,
        "charges_plates": [charge_plate(rn, j, x, n, table.get("ech_physiques"), plancher_j_mw, rn_max_reference_mw)
                           for x in charges_mw],
        "prix": prix_bas,
    }

    # I2 réintégré : mêmes calculs avec J_r
    jr = j_reintegre(table)
    if jr is not None:
        jrv = [v for v in jr if v is not None]
        dr, d = table[COLONNE_REINTEGRE], table["nucleaire_disponible"]
        sortie["jeu_nucleaire_reintegre"] = {
            "heures_valides": len(jrv),
            "somme_twh": sum(jrv) / 1e6,
            "heures_positif": sum(1 for v in jrv if v > 0),
            "moyenne_mw": _moyenne(jrv),
            "arrets_modulation_courts_twh": sum(a - b for a, b in zip(dr, d) if a is not None and b is not None) / 1e6,
            "charges_plates": [{k: c[k] for k in CLES_CHARGE_REINTEGRE}
                               for c in (charge_plate(rn, jr, x, n, None, plancher_j_mw) for x in charges_mw)],
        }
    return sortie


def max_charge_residuelle(table: dict[str, list]) -> dict | None:
    """Maximum de RN d'une table (même départage que les heures tendues), ou None."""
    hu = table["heure_utc"]
    rn = [charge_residuelle(*vals) for vals in zip(table["consommation"], table["eolien"], table["solaire"],
                                                   table["nucleaire_disponible"])]
    idx = classement_tendues(hu, rn)
    return _instant(hu, idx[0], rn[idx[0]]) if idx else None


def max_consommation(table: dict[str, list]) -> dict | None:
    """Consommation horaire maximale d'une table (MW moyens sur l'heure ; même départage que les heures
    tendues : valeur décroissante, puis heure UTC la plus ancienne), ou None. Repère de la limite
    « froid extrême » : à comparer à la pointe historique, publiée à la demi-heure."""
    hu, c = table["heure_utc"], table["consommation"]
    idx = [i for i in range(len(c)) if c[i] is not None]
    if not idx:
        return None
    i = min(idx, key=lambda i: (-c[i], hu[i]))
    return _instant(hu, i, c[i])


def max_pluriannuel(maxima: dict[str, dict | None]) -> dict | None:
    """Maximum de plusieurs maxima annuels ({année: {valeur_mw, heure_utc, debut_paris}}) : valeur la
    plus élevée, puis heure UTC la plus ancienne ; l'année d'origine est ajoutée (`annee`)."""
    candidats = [(a, m) for a, m in maxima.items() if m is not None]
    if not candidats:
        return None
    a, m = min(candidats, key=lambda am: (-am[1]["valeur_mw"], am[1]["heure_utc"]))
    return {**m, "annee": a}


def matrice_jour_heure(heures_utc: list[str], valeurs: list) -> dict:
    """Matrice jour × heure de Paris (pour une heatmap).

    Lignes : dates de Paris présentes dans `heures_utc`, triées ; 24 colonnes (heure de Paris de
    début). Cellule = moyenne des valeurs renseignées qui y tombent ; None si aucune (heure
    inexistante du passage à l'heure d'été, donnée absente). L'heure répétée du passage à
    l'heure d'hiver reçoit la moyenne de ses deux occurrences.
    """
    cellules: dict[str, list[list[float]]] = {}
    for h, v in zip(heures_utc, valeurs):
        p = heure_paris(h)
        ligne = cellules.setdefault(p.date().isoformat(), [[] for _ in range(24)])
        if v is not None:
            ligne[p.hour].append(v)
    jours = sorted(cellules)
    return {"jours": jours, "valeurs": [[_moyenne(c) for c in cellules[d]] for d in jours]}
