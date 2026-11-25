# Conception du site

Document vivant : récit, pages, direction visuelle, arbitrages de
conception. Les décisions qui engagent le fond sont dans
`making-of/DECISIONS.md`.

## 1. Récit

Pas de thèse affichée avant les enquêtes (décision de l'auteur, 2026-11-26).
L'accueil **pose la question** et montre l'objet qui la rend
nécessaire : une année du système électrique **heure par heure**. Les
enquêtes répondent chacune à une sous-question, avec leurs chiffres
sourcés, leurs limites et ce qui manque. Le message principal s'écrira
quand deux enquêtes seront faites.

Ordre de livraison : « Combien ? » → « Quand ? » + simulateur → carbone,
prix → « Où ? » (enquête courte sur ce qui manque).

## 2. Pages

| Route | Contenu | Étape |
|---|---|---|
| `/` | Hero heatmap 8 760 h ; la question ; accès aux enquêtes et au simulateur | 2 |
| `/combien` | Enquête « Combien ? » : la pyramide des puissances, la consommation, les trajectoires | 2 |
| `/quand` | Enquête « Quand ? » | 3 |
| `/simulateur` | Module signature | 3 |
| `/methode` | Sources, hypothèses, contrôles de cohérence (`pc check`), glossaire replié | 2 |
| `/making-of` | Journal, décisions, erreurs, brief | fait |
| `/a-toi` | Missions à faire soi-même | 3 |

## 3. Direction visuelle

### Matériau

Le vocabulaire visuel vient du métier : courbes de charge, monotones,
calendriers horaires, plans de réseau. Pas de pictogrammes d'éclair, pas
de photos de serveurs, pas d'illustrations de « cloud ».

### Couleurs (jetons)

| Jeton | Clair | Rôle |
|---|---|---|
| `--papier` | `#EDF1F2` | fond : papier calque froid |
| `--encre` | `#16263A` | texte : bleu de Prusse |
| `--encre-2` | `#4E5D6C` | texte secondaire, axes |
| `--trait` | `#C5CED4` | filets, grilles |
| `--signal` | `#F2C200` | **unique** mise en évidence (surlignage, sélection) ; jamais du texte sur fond clair |
| `--sous-zero` | `#1C7C7D` | pôle négatif des échelles divergentes (prix < 0, surplus) |
| `--sur-zero` | `#B4642D` | pôle positif des échelles divergentes (prix élevés, tension) |

Mode sombre : fond `#101A26`, encre `#E3E9EC`, mêmes rôles. Les échelles
de données sont définies et validées avec le skill `dataviz` (contraste,
daltonisme) au moment de construire les graphiques ; les couleurs de
filières, si on en a besoin, sont **propres au site** (pas celles
d'éCO2mix).

### Typographie

- **Barlow Semi Condensed** (OFL) : titres, chiffres, axes, légendes,
  navigation. Inspirée de la signalétique routière : registre technique
  sans monospace. Chiffres tabulaires dans les tableaux.
- **Source Serif 4** (OFL) : texte courant, notes. Interligne 1,6,
  mesure ≤ 68 caractères.
- Polices **auto-hébergées** (paquets `@fontsource`, aucun CDN).
- Interdits : capitales espacées en sur-titre, mot isolé en couleur dans
  un titre, monospace pour les petites étiquettes.

### Mise en page

```
┌──────────────────────────────────────────────────────────────┐
│ Puissance de calcul        Combien  Quand  Simulateur  Méthode │
├──────────────────────────────────────────────────────────────┤
│  [ heatmap 365 jours × 24 heures, pleine largeur ]           │
│  question, en une phrase, sous la heatmap                    │
├────────────────────────────────────┬─────────────────────────┤
│ texte d'enquête (≤ 68 ch.)         │ note marginale :        │
│ … 0,77 GW raccordés¹ …             │ ¹ RTE, Bilan électrique │
│                                    │   2025, p. 19 · conf. B │
│ [ graphique : largeur texte+marge ]│                         │
└────────────────────────────────────┴─────────────────────────┘
```

- Alignement à gauche partout ; colonne de lecture + **marge de notes**
  à droite sur grand écran ; notes repliées sous le paragraphe sur
  téléphone.
- Les graphiques débordent sur la marge (largeur texte + marge).
- **Une seule audace : le hero heatmap.** Tout le reste est calme.

### Principes

1. **Chaque chiffre porte sa provenance** : source, date, page,
   confiance (A : source primaire et recoupement indépendant ; B :
   source primaire, recoupement partiel ; C : source unique ou
   définition floue). Le chiffre et sa note sont générés depuis la même
   entrée du référentiel `chiffres` : pas de chiffre tapé à la main dans
   une page.
2. **Les unités sont typographiées** : espace fine insécable avant
   l'unité, MW et MWh jamais abrégés en « M ».
3. **Les grandeurs de nature différente ne partagent pas un axe** : la
   pyramide des puissances (recherché → réservé → signé → raccordé →
   appelé) est montrée en échelle logarithmique, étage par étage, avec
   la date de chaque donnée ; jamais en somme ni en entonnoir continu.
4. Mouvement : aucun à l'arrivée sur la page ; transitions seulement en
   réponse à une action (filtre, curseur du simulateur).
5. Accessibilité : contraste AA, focus clavier visible,
   `prefers-reduced-motion`, chaque graphique a un tableau de données
   repliable.
