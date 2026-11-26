# Simulateur — spécification v1

Document vivant. Décisions dans `making-of/DECISIONS.md`.

## Ce qu'il fait

On choisit une consommation supplémentaire (un parc de data centers) et
une année observée ; le simulateur l'ajoute **heure par heure** aux
séries de cette année et montre ce qu'elle rencontre : heures tendues,
heures de surplus, prix. Il prolonge « Quand ? » : mêmes indicateurs,
mêmes définitions, mêmes limites, mais avec les hypothèses entre les
mains de la lectrice.

Il **ne** modélise **pas** : le dispatch, la formation des prix (le prix
affiché est celui observé, sans la consommation ajoutée), les échanges
et les voisins, le réseau local, le risque de défaillance au sens de
RTE. Il le dit en tête de page, pas en note.

## Hypothèses réglables (v1)

| Hypothèse | Défaut | Plage | Remarque |
|---|---|---|---|
| Année de référence | 2025 | 2015-2025 | séries publiées `data/export/horaire/AAAA.csv` |
| Puissance appelée X | 1 GW | 0 à 20 GW | puissance **appelée**, pas réservée ni raccordée (lien vers « Combien ? ») |
| Profil | plat | plat ; plat avec effacement | aucune courbe de charge de data center n'est publiée |
| Effacement : heures | 0 | 0 à 500 h/an | la consommation ajoutée est nulle pendant les N heures où la charge résiduelle **observée** est la plus élevée (prévision parfaite : borne optimiste, dite) |

Chaque hypothèse affichée avec sa justification et son défaut ; l'URL
porte l'état (partage d'un scénario par lien).

## Résultats affichés

Pour l'année et les hypothèses choisies (énergies en TWh, puissances en
GW, heures de Paris) :

1. énergie ajoutée (Σ heures × X, effacement déduit) ;
2. part de cette énergie qui tiendrait **au plus** dans le nucléaire
   disponible non produit (J) ;
3. heures où charge résiduelle + charge ajoutée dépasse le maximum
   observé de l'année ; nouveau maximum ;
4. part de l'énergie ajoutée consommée à prix négatif ou nul, et prix
   moyen pondéré par la charge ajoutée (prix **observé**, sans effet en
   retour : le dire) ;
5. monotone de la charge résiduelle avant / après ;
6. rapprochement avec les marges publiées par RTE, présenté comme
   approximation du site (texte de « Quand ? »).

## Architecture

- **Référence Python** : `pipeline/pc/quand.py` (déjà là) ; on y ajoute
  une fonction `simuler(table, x_mw, heures_effacement)` qui généralise
  `charges_plates` à un profil horaire quelconque (vecteur de charge
  ajoutée), et les cas de test correspondants dans
  `pipeline/tests/cas_quand.json` (valeurs calculées à la main).
- **Moteur TypeScript** : `site/src/lib/simulateur/`, fonctions pures,
  sans dépendance, mêmes règles (heure valide, arrondis, égalités,
  quantiles) ; un test vitest rejoue **tous** les cas de
  `cas_quand.json` (parité) et compare, sur une année réelle, le moteur
  aux valeurs de `quand.json`.
- **Données** : le navigateur charge le CSV de l'année choisie, servi
  par le site lui-même (copié au build depuis `data/export/horaire/`),
  aucun appel externe.
- **Page** : `/simulateur`, lisible sans JS pour la partie texte
  (hypothèses et limites) ; les résultats exigent JS, et le disent.
