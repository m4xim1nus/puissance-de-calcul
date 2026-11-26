# Arrêts pour modulation : variante réintégrée de la disponibilité nucléaire (agent, 26/11/2026)

Suite de l'erreur « "Quand ?" : un plafond qui dépend de ce qu'EDF déclare indisponible »
(making-of/ERREURS.md). Rien n'est commité ; `making-of/`, `ROADMAP.md`, `BACKLOG.md`,
`docs/MESSAGE.md`, `EnBref.svelte`, `bilan.py`, ENTSO-E et carbone non touchés. Le travail sur
les limites (rapport `2026-11-26-limites-agent.md`) n'est pas défait.

## 1. Règle d'identification

Code : `pipeline/pc/remit.py`, `MOTIF_MODULATION`, `MOTIF_AUTRE_CAUSE`, `est_modulation`. Elle
s'applique aux événements **retenus** par la reconstruction existante (dernière version active,
filière nucléaire, Planifiée ou Fortuite, EDF SA), sans rien changer aux autres règles.

Un événement est un arrêt ou une baisse pour modulation si :

1. **le texte libre de sa dernière version contient le mot « modulation »** (mot entier,
   insensible à la casse ; même mot en français et en anglais). Formes rencontrées : « arrêt /
   baisse / palier / limitation / indisponibilité pour modulation », « baisse avant arrêt pour
   modulation », « le placement de cette modulation », « unavailability for modulation supply »,
   « limitation for power modulation ». Les 165 textes distincts du jeu (toutes versions) qui
   contiennent le mot ont été lus : un seul emploi différent, « imposition suite à une
   modulation » (Cruas 1, 16/06/2020), dont l'événement est annulé ;
2. **ou** une version antérieure du même événement contient le mot, et la dernière version
   n'invoque pas une autre cause (fortuit / forced, combustible / fuel, prolongation de campagne /
   stretch, essai / test, environnement). EDF efface souvent le texte à la mise à jour.

Décompte (historique + liste courante) : **407 événements** sur 13 695 retenus, **384 par la
règle 1**, **23 par la règle 2** ; 406 « Planifiée », 1 « Fortuite » (Bugey 5, 31/03/2025, texte
« arrêt pour modulation »). 2 événements ont un mot « modulation » dans une version antérieure
mais une autre cause dans la dernière, et ne sont pas comptés : Gravelines 4 (03/10/2025, « Indisponibilité fortuite ») et Cattenom 1 (24/08/2026, « Arrêt pour économie de combustible »).

### Cas ambigus examinés à la main (non comptés)

| Catégorie (texte) | Événements retenus | Énergie brute | Raison |
|---|---|---|---|
| « Tranche en prolongation de campagne / Ongoing stretch » | 220 | 26,1 TWh cumulés (brut) | baisse physique en fin de combustible, pas un choix économique |
| « Arrêt pour économie (de) combustible / Fuel saving outage » sans le mot | 14 | 4,5 TWh (brut, 2024-2027) | gestion du combustible = la contrainte d'énergie elle-même ; sensibilité ci-dessous |
| « Essai à puissance stable… le niveau de puissance pourra être réinterrogé si les conditions économiques le justifient » | 461 | 1,8 TWh | essais ; l'économique ne porte que sur le niveau |
| « Le placement… sera réinterrogé… si les conditions économiques le justifient », sans le mot | 12 | 0,6 TWh (net) | même gabarit que la modulation, mais EDF ne le dit pas ; sensibilité ci-dessous |
| « baisse pour contraintes environnementales… conditions économiques » | 2 | < 0,1 TWh | contrainte de température des fleuves |
| Texte réduit à un lien « …/optimisation-et-trading/… » | 54 | 30,2 TWh | faux positif d'une recherche sur « optimisation » : arrêts de toute nature |
| « Le fonctionnement de cette tranche est dès à présent contraint par son stock de combustible » | 1 | 1,0 TWh | contrainte d'énergie |

Sensibilités (énergie nette ajoutée à la variante si l'on comptait aussi la catégorie, TWh) :
arrêts pour économie de combustible sans le mot : 0,28 (2024), 0,66 (2025), 2,65 (2026, année
incomplète) ; arrêts « réinterrogés si les conditions économiques » sans le mot : 0,17 (2019),
0,03 (2020), 0,39 (2021). La règle 2 seule ajoute 3,3 TWh en 2020 et 2,7 TWh en 2025 (Chooz 2,
18/04-26/06/2025 : « arrêt pour modulation » en versions 1 à 8, texte vide en version 9).

Tests : `tests/test_remit.py` (9 textes réels reconnus, 8 cas ambigus non reconnus, règle 2 avec
six dernières versions différentes, reconstruction réintégrée avec chevauchement d'une
maintenance).

## 2. Décompte, et écart avec le spike (928) et avec le comptage de Claude (380)

- **380** (Claude) : historique seul, dernière version active, mot « modulation ». La liste
  courante en ajoute 4 → **384**. Les **501 identifiants** (historique) ou 508 (avec la liste
  courante) comptent toutes les versions, y compris 99 événements dont la dernière version est
  annulée (91) ou supprimée (8) : ils ne sont pas dans la reconstruction.
- **928** (spike carbone) : événements « Planifiée » retenus dont le texte contient
  « combustible », « modulation », « économi » ou « optimisation » (reproduit exactement :
  928, ≈ 72 TWh bruts). Décomposition : 383 « modulation » (34,4 TWh), **461 essais à puissance
  stable** (1,8 TWh, via « économi[ques] »), **54 textes réduits à un lien
  « optimisation-et-trading »** (30,2 TWh, arrêts de toute nature, dont des visites décennales),
  14 arrêts pour économie de combustible (4,5 TWh), 15 autres mentions économiques (0,7 TWh),
  1 « contraint par son stock de combustible » (1,0 TWh). Le spike surcomptait donc d'un facteur
  2,4 en nombre et 2 en énergie ; le rapport du spike (§ 2.6 et § 3.7) le signalait comme
  recherche de mots, sans en mesurer l'effet. **À annoter dans `docs/spike/carbone.md`** (non fait :
  fichier carbone hors de mon périmètre).
- Énergie (« ≈ 10 TWh en 2024, ≈ 5 TWh en 2025 », Claude) : avec la règle 1 seule, 10,31 et
  5,14 TWh nets (10,34 et 5,21 bruts) : l'estimation tenait ; la règle 2 porte 2025 à 7,81 TWh.
  Les chevauchements comptent peu (brut − net ≤ 0,07 TWh par an).

| Année | Événements touchant l'année | Énergie retirée (TWh, nette) |
|---|---|---|
| 2015-2018 | 0 | 0 |
| 2019 | 39 | 1,76 |
| 2020 | 48 | 6,39 |
| 2021 | 24 | 4,27 |
| 2022 | 44 | 6,81 |
| 2023 | 42 | 3,73 |
| 2024 | 99 | 10,44 |
| 2025 | 87 | 7,81 |
| 2026 (incomplète) | 39 | 1,70 |

(`data/export/meta.json`, `nucleaire_disponible.arrets_modulation`.)

## 3. Pipeline

- `remit.py` : colonnes `modulation` et `modulation_par` des événements ;
  `segments_tranches` / `disponible_horaire(…, reintegrer_modulation=True)` : les événements
  `modulation` ne comptent plus dans le minimum ; puissance maximale lue sur **tous** les
  événements, mêmes périodes d'exploitation, même minimum des autres événements superposés.
- `build.py` : colonne `nucleaire_disponible_reintegre` (parquet, et **en dernière colonne** des
  `horaire/AAAA.csv` : toutes les lignes des CSV changent dans le diff, les colonnes existantes
  sont identiques, vérifié contre HEAD) ; `meta.json` : description, règle, décompte par an ;
  `LISEZMOI.md` des CSV.
- `quand.py` : `COLONNE_REINTEGRE`, `j_reintegre`, `indicateurs_annee` →
  `jeu_nucleaire_reintegre` (Σ J_r, heures, moyenne, `arrets_modulation_twh`, charges plates :
  parts et énergies avec et sans plancher) ; `effet_charge` / `simuler` → `reintegre` (le froid
  passe d'abord, comme pour J) ; RN inchangée (disponible déclaré).
- `export_quand.py` : définitions, limites (dont deux lignes chiffrées), et **88 chiffres
  nouveaux** (8 par année pleine 2015-2025) : `quand_arrets_modulation_AAAA`,
  `quand_j_reintegre_AAAA`, `quand_part_j_reintegre_{5,10}gw_AAAA`,
  `quand_part_j_plancher_reintegre_{5,10}gw_AAAA`, `quand_energie_j_reintegre_{5,10}gw_AAAA`.
  **Aucune valeur existante ne change** (comparé à HEAD : 0 valeur différente ; 64 chiffres dont
  seuls libellé ou note changent).

### Chiffres nouveaux (valeur publiée)

| Année | Arrêts pour modulation | Σ J → Σ J_r (TWh) | 5 GW : J → J_r | 5 GW plancher : J → J_r | 10 GW : J → J_r | 10 GW plancher : J → J_r | Énergie 5 GW : J → J_r (TWh) |
|---|---|---|---|---|---|---|---|
| 2019 | 1,8 | 18,3 → 20,1 | 40 → 41 % | 22 → 24 % | 21 → 23 % | 12 → 14 % | 17,3 → 18,0 |
| 2020 | 6,4 | 20,0 → 26,4 | 42 → 50 % | 24 → 34 % | 23 → 29 % | 13 → 20 % | 18,2 → 21,9 |
| 2021 | 4,3 | 16,0 → 20,2 | 35 → 44 % | 18 → 27 % | 18 → 23 % | 9 → 14 % | 15,4 → 19,2 |
| 2022 | 6,8 | 13,4 → 20,2 | 30 → 43 % | 14 → 27 % | 15 → 23 % | 7 → 14 % | 13,3 → 18,9 |
| 2023 | 3,7 | 18,3 → 22,1 | 38 → 45 % | 22 → 29 % | 21 → 25 % | 12 → 16 % | 16,9 → 19,5 |
| 2024 | 10,4 | 25,1 → 35,6 | 47 → 60 % | 32 → 46 % | 28 → 38 % | 19 → 29 % | 20,8 → 26,2 |
| 2025 | 7,8 | 29,1 → 37,0 | 52 → 58 % | 39 → 47 % | 32 → 39 % | 24 → 31 % | 22,8 → 25,6 |

2015-2018 : variantes égales aux valeurs déclarées (aucun arrêt pour modulation déclaré).
Les colonnes « J » 2019-2021 et certaines parts « J » viennent de `quand.json` (non publiées
comme chiffres pour toutes ces années) ; arrondis de quand.json à l'entier.

### Contrôles `pc check` (2 nouveaux, 29 contrôles verts)

- « REMIT, disponibilité réintégrant les arrêts pour modulation » : export = recalcul (écart
  max 0,05 MW, arrondi au dixième) ; réintégré ≥ déclaré à toute heure ; égal hors des 21 562
  heures touchées par un arrêt pour modulation ; règle appliquée telle qu'écrite.
- « « Quand ? » : J_r ≥ J à toute heure » (colonnes arrondies comme les CSV) ; Σ J_r, énergie des
  arrêts, parts 5 et 10 GW avec et sans plancher = recalcul polars ; parts réintégrées ≥
  déclarées ; Σ J_r comparé à la modulation EDF, écart affiché : 2023 Σ J 18,3 / Σ J_r 22,1 pour
  16 TWh (+38 %) ; 2024 25,1 / 35,6 pour 31 (+15 %) ; 2025 29,1 / 37,0 pour 33 (+12 %). Σ J était
  sous la modulation d'EDF en 2024 et 2025 ; Σ J_r est au-dessus les trois années (réserves,
  périmètre et frontière d'EDF différents : pas d'égalité attendue, rapport borné à [0,5 ; 2]).

## 4. Textes modifiés (emplacements)

Formule retenue partout : « au plus X, avec la disponibilité déclarée par EDF ; Y en réintégrant
les arrêts qu'EDF déclare indisponibles pour modulation », avec le pourquoi et le rappel de la
contrainte d'énergie.

- `docs/enquetes/partage/arrets-modulation.md` (**nouveau fragment**, inclus par « Quand ? » et
  par `lecture.md`) : « Ce plafond dépend de ce qu'EDF déclare indisponible. » — citation du texte
  d'EDF, nature économique des arrêts, énergie retirée 2024 et 2025, aucun avant 2019, part 5 GW
  avec plancher 39 → 47 %, « Ce n'est pas davantage une capacité physique : la contrainte
  d'énergie reste la limite la plus nette ». La source est citée en clair (jeu REMIT d'EDF,
  opendata.edf.fr) : `{{source:edf-remit}}` échoue au rendu, la source n'étant portée par aucun
  chiffre de `chiffres.json`.
- `docs/enquetes/quand.md` : § « Les heures de surplus », la frontière fixée par EDF
  (« et elle compte : EDF déclare indisponibles des arrêts « pour modulation »… En les
  réintégrant, … {{quand_j_reintegre_2024}} … {{quand_j_reintegre_2025}} ») ; § « Ce qu'une
  consommation continue… » : « au plus 52 % … et 32 % …, avec la disponibilité déclarée par EDF ;
  58 % et 39 % en réintégrant les arrêts qu'EDF déclare indisponibles pour modulation » ;
  inclusion du fragment après le plancher ; énergie « 22,8 TWh … (25,6 TWh en réintégrant les
  arrêts pour modulation) ».
- `site/src/lib/simulateur/lecture.md` : « un plafond, avec la disponibilité déclarée par EDF, et
  un plafond lâche » ; seconde fourchette annoncée ; inclusion du fragment ; « Réintégrer les
  arrêts pour modulation n'y change rien : la production supplémentaire affichée n'en est que
  plus haute ».
- `site/src/lib/simulateur/phrases.ts`, tuile « Dans le nucléaire disponible non produit » :
  valeur inchangée (« au plus 39 à 52 % » à 5 GW, 2025) et **seconde valeur** sous elle
  (« disponibilité déclarée par EDF ; 47 à 58 % en réintégrant ses arrêts pour modulation » ;
  « même valeur » en 2015-2018 ; « avec la disponibilité déclarée par EDF » seule pour un CSV
  sans la colonne) ; détail : pourquoi, valeur réintégrée et énergie, « en énergie, la limite est
  plus nette ». **Ordre des tuiles** : les prix passent avant le nucléaire (voir § 5).
- `Simulateur.svelte` : rendu de la seconde valeur, annonce pour lecteur d'écran, définition
  repliée du nucléaire disponible non produit.
- `site/src/lib/graphiques/ChargePlate.svelte` (graphique de « Quand ? ») : titre du panneau (a),
  infobulle, remarques, aide, légende et note du tableau requalifiés ; **cercle creux** = part
  réintégrée sans plancher ; deux colonnes de tableau. Données : `quand.ts`, `server/quand.ts`
  (lecture stricte de `jeu_nucleaire_reintegre`).
- Notes générées (`export_quand.py`) : libellés et notes de `quand_j_*`, `quand_part_j_*`,
  `quand_part_j_plancher_*`, `quand_energie_j_*`, `quand_heures_j5_*` ; définitions et limites de
  `quand.json` ; docstrings et `LIMITES_J` de `quand.py`.
- `docs/SIMULATEUR.md` : section « Disponibilité déclarée et arrêts pour modulation », résultat 2.

`git grep` final des formules (« au plus », « borne haute », « plafond », `quand_part_j_`) : il ne
reste de « au plus » non requalifié que dans **`docs/MESSAGE.md`** (l. 55, « au plus
{{quand_part_j_5gw_2025}} », texte de l'accueil « En bref »), hors de mon périmètre : **à
requalifier**.

## 5. Simulateur : forme retenue et écran

Seconde valeur dans la tuile plutôt qu'un réglage : un réglage ajoutait une ligne aux hypothèses
et un paramètre d'adresse pour une grandeur qui ne change qu'une tuile ; les deux lectures
restent visibles ensemble. Adresses anciennes et résultats par défaut inchangés (seule la seconde
valeur s'ajoute). La seconde valeur, sur deux lignes, faisait déborder l'outil d'environ 35 px à
1366 × 768 ; la tuile des prix passe donc avant celle du nucléaire (même rangée que le titre des
prix sur deux lignes) : par défaut, l'outil finit vers 750 px (735 avant). Captures dans le
scratchpad de la session, dossier `modulation/` : `simulateur-1366x768.png`,
`simulateur-5gw-1366x768.png`, `simulateur-2017-5gw-1366x768.png`, `simulateur-390x844.png`,
`simulateur-390x2400.png`, `simulateur-froid-1366x768.png`, `quand-1366x768.png`,
`quand-390x844.png`, `quand-1366-pleine.png`, `quand-390-pleine.png`, et les témoins
`avant-simulateur-1366.png`, `temoin-ancien-froid-1366x768.png`.

**Limite constatée** : avec froid et effacement (`?x=5&effacement=100&froid=8`), la phrase de
scénario fait trois lignes et l'outil dépassait déjà 768 px avant ce travail (paragraphe des
sources coupé) ; il dépasse maintenant d'environ 15 px de plus (estimé sur capture témoin).

Parité : 3 cas partagés ajoutés à `cas_quand.json` (valeurs calculées à la main : simuler sans
effacement, simuler avec froid, `indicateurs_annee`), `reintegre: null` attendu sur le cas « 4 GW
sans effacement » sans la colonne ; parité sur 2022 et 2025 réels (`moteur.test.ts`) ; tests de
phrases (forme, 2017, CSV sans colonne).

## 6. Tests

- `uv run pc build` : OK (253 chiffres calculés) ; `uv run pc check` : 29 contrôles, 0 échec ;
  `uv run pytest` : 185 passés.
- `npm run check` : 0 erreur ; `npm test` : 173 passés ; `npm run format:check` : OK ;
  `npm run build` : OK.

## 7. Doutes et erreurs repérées dans l'existant

1. **Erreur dans l'existant** (corrigée, à consigner) : `meta.json`, limite de
   `nucleaire_disponible` : « réserves pour services système, modulation économique et baisses non
   déclarées n'y figurent pas ». Faux depuis 2019 : EDF y retranche des arrêts économiques
   déclarés « pour modulation ». Texte réécrit dans `build.py`.
2. **Spike carbone** : le décompte de 928 événements et ≈ 72 TWh est faux comme mesure de la
   modulation déclarée (§ 2) ; la conclusion qualitative (disponibilité déclarée en partie
   endogène au prix) tient. Rapport du spike non annoté (hors périmètre).
3. **Avant 2019, zéro par construction de la règle**, pas par constat physique : en 2016-2018,
   54 événements n'ont pour texte qu'un lien (30 TWh, de toute nature) ; on ne peut pas savoir
   s'il s'y cache des arrêts économiques. La variante est donc une borne basse de l'effet de la
   déclaration, pas son effet exact.
4. **Arrêts pour économie de combustible exclus** : choix défendable (c'est la contrainte
   d'énergie), mais EDF lui-même les associe parfois à la modulation (« Unavailability for
   modulation… / Arrêt pour économie combustible », 2021). Inclus, ils ajouteraient 0,7 TWh en
   2025 et 2,7 TWh en 2026. À trancher par Claude ou l'auteur ; la règle est un paramètre.
5. **J_r n'est pas plus « physique » que J** : un arrêt pour modulation peut servir à garder du
   combustible pour l'hiver ; le réintégrer suppose que cette énergie était disponible. Les
   textes le disent (« sensibilité au choix d'EDF, pas une capacité physique »).
6. **Charge résiduelle inchangée** (disponible déclaré) : vérifié, aucune des 100 heures les plus
   tendues de 2022, 2024 et 2025 n'est touchée par un arrêt pour modulation (RN max identique).
7. `docs/MESSAGE.md` (accueil) cite encore « au plus 52 % » sans requalification.
8. Règle 2 : 23 événements, dont Chooz 2 2025 (2,5 TWh) ; si EDF changeait la nature d'un arrêt
   sans le dire dans la dernière version, la règle le compterait à tort. Les 25 cas ont été lus
   version par version (2 écartés).
9. Ordre des tuiles du simulateur modifié (prix avant nucléaire) : changement visible pour qui
   connaît la page.

## Corrections après relecture (`2026-11-26-limites-modulation.md`, F1, F2, f1 à f12 hors `docs/MESSAGE.md`)

**Les § 1 à 5 ci-dessus décrivent la première version.** Les valeurs de J_r qu'ils donnent
(réintégrant tous les arrêts pour modulation) sont remplacées par celles ci-dessous ; les
identifiants `quand_j_reintegre_*`, `quand_part_j_reintegre_*`, `quand_part_j_plancher_reintegre_*`
et `quand_energie_j_reintegre_*` sont gardés, avec leur nouveau sens : **arrêts courts
réintégrés**. `quand_arrets_modulation_*` disparaît, remplacé par `quand_arrets_modulation_courts_*`
et `quand_arrets_modulation_longs_*`. Aucune autre valeur publiée ne change (contre HEAD : 0 valeur
modifiée, 0 retrait ; 350 chiffres).

### F2, arrêts longs

**Règle** (`pc/remit.py`, `DUREE_MAX_COURT_H`, `MOTIF_COMBUSTIBLE`, colonne `modulation_courte`) :
un arrêt pour modulation est **court** si sa dernière version dure **moins de 7 jours** et
qu'aucune version ne parle de combustible. Seuls les courts sont réintégrés
(`reintegrer_modulation="courts"`) ; les autres (« longs ») restent retranchés.

**Pourquoi la durée et pas la clause « sera redémarrée »** (mesuré sur les 407 événements) :
sous 7 jours, déclaration en médiane 0,46 jour avant le début (3e quartile 0,8 jour ; 357
événements, clause présente dans 80 %) ; à partir de 7 jours, 14,5 jours en médiane, 95 jours
au 3e quartile, jusqu'à 291 jours (Chooz 2, 2025 ; 50 événements). La clause figure aussi dans
26 des 50 arrêts longs, jusqu'à 61 jours (Chooz 2, avril-juin 2020) : elle ne sépare pas les
arrêts décidés au jour le jour des arrêts planifiés. La règle « clause ou durée courte » proposée
dans la consigne aurait réintégré ces 26 arrêts (près de 11 TWh bruts) : je ne l'ai pas retenue.
Blayais 3 (2025, 6 jours, « Arrêt pour économie combustible ») est rangé dans les longs par la
mention du combustible. Résultat : 356 courts, 51 longs. Tests : `test_arrets_courts_et_longs`
(2 jours avec clause, 6 j 23 h sans clause, exactement 7 jours, combustible, deux mois avec texte
effacé).

**Énergie retirée de la disponibilité déclarée, nette des chevauchements (TWh)** — `meta.json`,
`nucleaire_disponible.arrets_modulation.par_annee` ; chiffres `quand_arrets_modulation_courts_*`
et `_longs_*` :

| Année | Courts (réintégrés) | Longs (retranchés) |
|---|---|---|
| 2019 | 1,5 | 0,2 |
| 2020 | 2,0 | 4,4 |
| 2021 | 0,5 | 3,8 |
| 2022 | 1,5 | 5,3 |
| 2023 | 0,8 | 2,9 |
| 2024 | 3,1 | 7,3 |
| 2025 | 3,9 | 3,9 |

**Nouvelles valeurs 2024 et 2025** (avec la disponibilité déclarée → arrêts courts réintégrés) :

| | 2024 | 2025 |
|---|---|---|
| Σ J → `quand_j_reintegre` | 25,1 → 28,3 TWh | 29,1 → 33,0 TWh |
| 5 GW, sans plancher → `quand_part_j_reintegre_5gw` | 47 → 50 % | 52 → 55 % |
| 5 GW, plancher 1 GW → `quand_part_j_plancher_reintegre_5gw` | 32 → 35 % | 39 → 43 % |
| 10 GW, sans plancher → `quand_part_j_reintegre_10gw` | 28 → 30 % | 32 → 35 % |
| 10 GW, plancher → `quand_part_j_plancher_reintegre_10gw` | 19 → 22 % | 24 → 27 % |
| Énergie 5 GW → `quand_energie_j_reintegre_5gw` | 20,8 → 21,8 TWh | 22,8 → 24,1 TWh |
| Énergie 10 GW → `quand_energie_j_reintegre_10gw` | — → 26,6 TWh | — → 31,0 TWh |

Σ J_r contre la modulation publiée par EDF (`pc check`) : 2023 +20 %, 2024 −9 %, 2025 +0 %.

**Série « tous » non exportée.** Une colonne réintégrant tous les arrêts portait les exports
au-delà du plafond de 15 Mo (`test_taille_des_exports`) : elle reste en mémoire au build, qui
passe l'énergie des arrêts longs à `quand.json` ; `pc check` la recalcule depuis REMIT (contrôle
« REMIT, disponibilité réintégrant… », qui vérifie aussi déclaré ≤ courts ≤ tous, l'égalité hors
des heures concernées et l'application des deux règles).

**Textes.** Fragment `arrets-modulation.md` réécrit (clause citée « pour la plupart » des arrêts
de moins de sept jours ; « la tranche peut redémarrer » ne vaut que pour eux ; arrêts longs et
arrêts pour économie de combustible retranchés, avec la note du BE2025, p. 25, sur l'imputation
d'EDF ; « sensibilité au choix de déclaration d'EDF, pas une capacité physique ») ; `quand.md`
(« ceux de moins de sept jours », phrase rétablie : « Les arrêts pour modulation plus longs et les
arrêts déclarés « pour économie de combustible » restent retranchés dans les deux calculs ») ;
tuile et définition du simulateur ; graphique (remarques : les arrêts longs pèsent surtout en
2020, 2022 et 2024) ; notes générées, définitions et limites de `quand.json`, `meta.json`,
`LISEZMOI.md`, `SIMULATEUR.md`.

### F1, repère de froid

- **Référentiel** : citation de `froid_2012_ecart_normale` complétée jusqu'à sa conclusion
  (« …devrait demeurer sensiblement inférieure à 100 GW cet hiver et pourrait ainsi être satisfaite
  par le parc de production français et les capacités d'imports du pays », hiver 2024-2025,
  p. 18, relu dans le PDF) ; note f10. Nouveau `pointe_froids_2010_hiver_2026_2027` (100 GW,
  borne : « devraient rester sensiblement inférieures à 100 GW (sauf cas très exceptionnels) »,
  synthèse hiver 2026-2027, p. 14, phrase entière en citation, relue ; recoupement avec la phrase de
  2024-2025). Nouveau `pointe_conso_record_2012_horaire` (100,6 GW : (99 166 + 102 098) / 2, points
  ODRÉ du 08/02/2012 relus par une requête du jour, copie dans `data/raw/spike_quand/pdf/`) ;
  `precision: 0.1` sur les deux pointes de 2012, pour qu'elles s'affichent 102,1 et 100,6 GW (et
  non 102 et 101).
- **Chiffre calculé** `quand_froid_100gw_AAAA` (toutes les années) : plus petit froid réglable
  (pas de 0,5 °C) qui porte la consommation horaire maximale du scénario au-delà de 100 GW
  (`froid_pour_depasser`, sur `annees.AAAA.froid` de `quand.json` : épisode, maxima dans et hors
  épisode). **5,5 °C en 2025** (comme la relectrice) ; 2,0 °C (2018) à 9,0 °C (2019). Pour la pointe
  à la demi-heure (102,1 GW) : 2,7 à 9,8 °C, comme la relectrice.
- **Textes** : raison du réglage (repère en consommation, « choix du site » pour la borne, f4 :
  ajout uniforme qui sous-estime la pointe et surestime la nuit) ; tuile « Consommation horaire
  maximale » (comparaison au même pas de temps, 100,6 GW, f3 ; « Le scénario la dépasse. » seulement
  s'il la dépasse ; texte de la relectrice adapté à la synthèse 2026-2027) ; fragment
  `limite-froid.md` (f7 : plus de lien vers la page elle-même) ; `SIMULATEUR.md` (paragraphe
  « Double compte » réécrit, dépendance à l'année, f4 avec la citation exacte du chauffage
  résidentiel). Les références `froid2012` et `froidCentennal` sont retirées du simulateur ; les
  chiffres restent au référentiel.

### Forme

- f1 : note de `quand_ecretement_prix_negatif_2025` (détail 1,3 + 1,6 = 2,9 TWh, soit 5,7 GW ;
  éolien en mer hors estimation) ; libellé et fragment : « plus haute que sans la production
  renoncée » au lieu de « surestimée ». Valeur inchangée (5,8 GW).
- f2 : nouvelle sortie `rn_max_heure_utc` (Python et TypeScript, cas partagé) ; la phrase du froid
  seul dit « l'heure du maximum, dans l'épisode, se dépasse elle-même dès le moindre froid » quand
  c'est le cas.
- f3, f4, f7, f10 : voir F1. f5 : tuile du nucléaire, la part du froid dans J n'est pas comptée dans
  la production en plus affichée. f6 : « Le plafond avec la disponibilité déclarée est lâche » ; le
  doublon « 39 % » disparaît avec les nouvelles valeurs (10 GW réintégré : 35 %). f8 : infobulle
  « en réintégrant les arrêts courts déclarés pour modulation ». f9 : phrase de `lecture.md`
  réécrite comme proposé. f11 : les cinq PDF (empreintes conformes) et leurs `.txt`, plus les
  extraits ODRÉ, rangés dans `data/raw/spike_quand/pdf/` (non versionné). f12 : raison du plancher
  (« un indice, pas une mesure »).

### Tests et contrôles

`pc build` (275 chiffres calculés), `pc check` (29 contrôles, 0 échec), `pytest` (187),
`npm run check`, `npm test` (173), `format:check`, `npm run build` : tous verts. Captures dans le
scratchpad de la session, `modulation/corrections/` (simulateur 1366 × 768 par défaut, 5 GW, froid,
froid et effacement ; 390 × 844 ; « Quand ? » 1366 × 768, 390 × 844 et pleine page). Par défaut et à
5 GW, l'outil tient à 1366 × 768 (seconde valeur sur deux lignes). Avec du froid, il déborde comme
avant.

### Doutes et écarts avec la relecture

1. Seuil de 7 jours : choix justifié par les préavis, pas par une source d'EDF ; les messages d'EDF
   cités en F2 (edf-2020-00076, etc.) ne sont pas lus. « Peuvent servir à garder du combustible »
   reste une hypothèse, écrite comme telle.
2. La relectrice place la phrase sur l'économie de combustible du BE2025 p. 30 : elle est p. 31 ; la
   note sur l'imputation d'EDF est p. 25 (vérifié, pagination imprimée = PDF). La citation du chauffage
   résidentiel est p. 60, pas p. 59.
3. `docs/MESSAGE.md` cite des identifiants dont la valeur change de sens (`quand_part_j_reintegre_5gw_2025` :
   58 → 55 %, `…_plancher_…` : 47 → 43 %, `quand_energie_j_reintegre_5gw_2025` : 25,6 → 24,1 TWh)
   et le mot « modulation » sans « courts » : à reprendre par Claude (F3).
4. Afficher 102,1 GW (et non 102 GW) pour `pointe_conso_record_2012` est un changement d'affichage
   d'un chiffre existant (valeur inchangée), limité aux deux textes du froid.
5. Avant 2019, toujours zéro par construction de la règle (§ 7, point 3).
