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
RTE. Il le dit en tête de page, pas en note : premier élément sous le
titre, un repli « Ce que fait le simulateur, et ce qu'il ne modélise
pas », à un clic (révisé le 26/11 : l'outil tient sur un écran, retour
de l'auteur).

## Hypothèses réglables (v1)

| Hypothèse | Défaut | Plage | Remarque |
|---|---|---|---|
| Année de référence | 2025 | 2015-2025 | séries publiées `data/export/horaire/AAAA.csv` |
| Puissance appelée X | 1 GW | 0 à 20 GW | puissance **appelée**, pas réservée ni raccordée (lien vers « Combien ? ») |
| Profil | plat | plat ; plat avec effacement | aucune courbe de charge de data center n'est publiée |
| Effacement : heures | 0 | 0 à 500 h/an | la consommation ajoutée est nulle pendant les N heures où la charge résiduelle **observée** est la plus élevée (prévision parfaite) ; l'énergie effacée est **perdue**, ni reportée dans le temps ni vers un autre site. Le résultat est circulaire pour l'indicateur des heures au-delà du maximum (ce sont les heures effacées) : il donne une **borne basse** du nombre d'heures à effacer, dite comme telle |

Chaque hypothèse affichée avec son défaut, sa justification dans un
repli « Raison » ; l'URL porte l'état (partage d'un scénario par lien).
Chaque résultat montre son qualificatif (« au plus », « à peu près ») et
sa valeur ; ses réserves et ses sources sont dans son repli « Détail ».

## Résultats affichés

Pour l'année et les hypothèses choisies (énergies en TWh, puissances en
GW, heures de Paris) :

1. énergie ajoutée (Σ heures × X, effacement déduit) ;
2. part de cette énergie qui tiendrait **au plus** dans le nucléaire
   disponible non produit (J), en fourchette sans plancher / avec un
   plancher de 1 GW non mobilisable (hypothèse du site), et l'énergie
   nucléaire supplémentaire correspondante, mise en regard de la
   production de l'année et des prévisions de l'exploitant ;
3. heures où charge résiduelle + charge ajoutée dépasse le maximum de
   l'année **et** le maximum 2015-2025 ; nouveau maximum ;
4. part de l'énergie ajoutée consommée à prix négatif ou nul (prix
   **observé**, sans effet en retour ; pour une consommation plate,
   c'est la part des heures de l'année). Pas de prix moyen pondéré :
   comparé entre scénarios, il se lisait comme une économie ;
5. monotone de la charge résiduelle avant / après ;
6. marge : une consommation plate de X GW retire à peu près X GW de
   marge (équivalence d'adéquation), mise en regard des marges publiées
   par RTE ; avec effacement, le simulateur ne sait pas dire combien de
   marge est rendue.

Qui servirait la consommation ajoutée (nucléaire, EnR moins arrêtées,
exportations) n'est pas déterminable sans les données des voisins : le
simulateur ne le dit pas.

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
