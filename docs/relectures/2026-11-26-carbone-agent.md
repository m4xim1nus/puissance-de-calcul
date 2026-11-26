# « Quel carbone ? » : rapport de l'agent rédacteur

Agent du 26/11/2026 (Opus), chargé de l'enquête courte « Quel carbone ? » (décision de l'auteur
« courte d'abord », `making-of/DECISIONS.md`). Rien n'est commité. `making-of/` n'a pas été
touché par cet agent (le fichier `making-of/JOURNAL.md` apparaît modifié dans `git status` : la
modification n'est pas de moi, elle était absente au début de ma session). **Relecture adverse
« lectrice experte » à faire avant publication** : le référentiel porte `verification: spike`
sur toutes les entrées saisies ici.

## Ce qui est livré

- **Texte** : `docs/enquetes/carbone.md` (titre « Quel carbone ? »). Encart « en préparation » :
  `docs/enquetes/chantier/facteur-marginal.md`, appelé par la nouvelle directive
  `::: chantier nom :::`.
- **Pipeline** : `pipeline/pc/carbone.py` (nouveau) → `data/export/carbone.json` (29 Ko) et 22
  chiffres calculés `carbone_*` (source `pdc-carbone`) ; branché dans `pc/build.py`
  (`build(..., saisis=)`) et `pc/cli.py`. Trois contrôles `pc check` (`pc/check.py`,
  `controles_carbone`). La règle des « orphelins » de `controle_quand_chiffres` est restreinte à
  la source `pdc-quand` (sinon les chiffres carbone y étaient comptés comme orphelins).
- **Référentiel** : 8 sources, 26 chiffres saisis, 8 contraintes d'ordre ; 8 grandeurs nouvelles
  dans `pc/chiffres.py` (`contenu_marginal`, `facteur_emission_marche`, `valeur_forfaitaire`,
  `facteur_emission_filiere`, `emissions`, `emissions_evitees`, `emissions_co2`, `quotas`) et
  l'unité `gCO2eq/MJ` (× 3,6) dans `intensite_moyenne`. Une grandeur par famille de facteur :
  aucune contrainte ne peut comparer un moyen à un marginal.
- **Site** : route `/carbone` (`+page.server.ts`, `+page.svelte`), carte sur l'accueil (titre et
  question tirés du front matter), lien « Carbone » dans la navigation ; graphique
  `carbone-mois-heure` (`CarboneMoisHeure.svelte`, SVG en viewBox, lisible sans JavaScript) ;
  `lib/carbone.ts`, `lib/server/carbone.ts` (lecture stricte) ; directive `chantier` dans
  `lib/server/enquetes.ts` (`lireChantier`), bloc `chantier` dans `lib/enquete.ts` et
  `Enquete.svelte` (premier usage de `EnChantier.svelte`, inchangé) ; jetons `--co2-0…4` dans
  `app.css` (alias de la rampe `--prix-p0…p4`, déjà validée en clair et en sombre).
- **Tests** : `pipeline/tests/test_carbone.py` (9 tests synthétiques), 6 tests `donnees` dans
  `test_donnees.py` ; site : `lib/carbone.test.ts`, `lib/server/carbone.test.ts`, 4 tests dans
  `lib/server/enquetes.test.ts`.

Tout au vert le 26/11/2026 : `pc build` ; `pc check` (32 contrôles, 0 échec) ; `pytest` (201) ;
`npm run check` (0 erreur) ; `npm test` (184) ; `npm run format:check` ; `npm run build`.
**Aucune valeur déjà publiée ne change** : vérifié en comparant `chiffres.json` avant et après
(0 retiré, 0 modifié, 48 ajoutés : 26 saisis, 22 calculés) ; `quand.json`, `systeme_horaire.parquet`,
`prix_quart_horaire.csv` et `horaire/` identiques ; `meta.json` : horodatage et une ligne
décrivant `carbone.json`.

## Sources relues par moi (copies dans `data/raw/carbone/` et `data/raw/spike*/`, non versionnées)

| Source | Passages relus | SHA-256 (début) |
|---|---|---|
| RTE, Bilan électrique 2025, rapport complet (`spike_quand/pdf/be2025.pdf`) | p. 99 (10,9 Mt) ; p. 102-103 (gaz 6,7 Mt, cogénérations 3,2 Mt « indépendant des conditions du marché », déchets 2,3 Mt, 40 % hors socle) ; p. 104 (19,6 et 20,0 g) ; p. 105 (« près de la moitié du temps » sous 15 g, maximum 58 g, « surtout en hiver… », 3 % du temps au-dessus de 100 g en 2023, facteurs « issus de travaux internes ») ; p. 106 (29,0 g ACV ; CCG « les centrales au gaz les plus performantes ») ; p. 107 (27 Mt évitées, méthode et limite jusqu'à sa conclusion) ; p. 145 (annexe des facteurs). Folio imprimé = page du PDF. | dcd91c93 |
| RTE, Bilan électrique 2024, rapport complet (`be2024.pdf`) | p. 90 (21,7 g) ; p. 98 (20 Mt évitées, 10,0 MtCO2 consommation). Le BE2024 ne donne pas d'intensité de la consommation en g/kWh. | f7e38668 |
| RTE, méthodologie de l'intensité de la consommation, avril 2026, v1 (pièce jointe ODRÉ) | p. 1-6 : traçage des flux, 15 pays, émissions directes, historique recalculé en mars 2026, facteurs de l'annexe | 3c3639f8 |
| Note ADEME-RTE du 8/10/2007 (copie DREAL Hauts-de-France, PDF de 7 pages sans folio) | p. 3 (25 % du temps, 600-700 g, 450-550 g en base, 400 g à l'horizon 2020) ; p. 4 (« revisitée régulièrement ») ; p. 7 (méthodes « complémentaires », « évaluer l'impact futur d'une décision prise aujourd'hui ») | 41eb003b |
| CRE, délibération n° 2021-126 (11 p.) | p. 1-3 et 11 : 0,59 tCO2/MWh, méthode avec et sans SEQE, « jusqu'à la prochaine révision des lignes directrices soit 2025 », méthodes du moyen marginal « moins robustes », note 4 (flow-based, plusieurs moyens marginaux). Le rapport de RTE annexé n'est pas dans ce PDF : non lu. | f12b9383 |
| Règlement délégué (UE) 2023/1185, texte français du JO (PDF de l'Office des publications, EUR-Lex refusant les robots) | annexe, partie A, point 6 a-c (L 157/24-25) ; partie C (L 157/28-29 : combustion + amont des combustibles, pas la construction) ; tableau A, France 19,6 gCO2eq/MJ, 2020, JRC 2022 (L 157/32) | 1d272783 |
| Règlement délégué (UE) 2023/1184, texte français du JO | art. 4 à 6 (L 157/15-17) : 90 %, 18 gCO2eq/MJ, corrélation mensuelle puis horaire, 20 €/MWh ou 0,36 × prix du quota | d5776ad4 |
| Décision (UE) 2015/1814, version consolidée au 01/01/2024 (outil documentaire) | art. 1er, § 4, 5, 5 bis, 6 (833 / 1 096 millions, 12 % × 2 jusqu'en 2030, invalidation au-delà de 400 millions) | 85637812 |
| Décision (UE) 2023/852 | article premier (doublement jusqu'au 31/12/2030) | 1e492287 |
| Communication C/2026/2957 (TNAC 2025), version française XHTML de l'Office des publications ; copie espagnole du JO (BOE) pour la mise en page | TNAC 2025 = 1 023 494 202 ; 190 494 202 placés de 09/2026 à 08/2027 ; TNAC 2024 = 1 148 049 585 ; 270 506 086 invalidés au 01/01/2025 ; 400 000 000 en réserve au 01/01/2026 ; proposition COM(2026) 153 du 01/04/2026 de mettre fin à l'invalidation | d42b586b (HTML) |
| AIE, *Energy and AI* (`spike/datacenters/iea_energy_ai.pdf`) | **p. 246** (et non 245 comme l'écrit la relecture du spike) : 180 Mt, hors secours, méthode non dite | 0bcbbb6b |
| Page RTE « éCO2 emissions » (en ligne, anglais) | méthode de `taux_co2` (facteur ADEME × rendement moyen, combustion seule). Non citée par une note (le site ne cite une source que via un chiffre). | — |

**Non relu, donc non publié** : RTE-ADEME 2020 (rapport chauffage, p. 219) ; rapport de RTE
annexé à la délibération de la CRE ; communication C/2025/3180 (le TNAC 2024 est pris dans
C/2026/2957, qui le rapporte) ; issue de la proposition COM(2026) 153 (dite « non vérifiée » dans
le texte) ; littérature (Perino, Rosendahl, Bruninx et Ovaere : page de Nature refusée,
Europe PMC non concluant ; Holland et al.) : aucune citation académique dans la page ; GHG
Protocol ; ADEME Base Empreinte ; règlement 2025/2359.

## Chiffres nouveaux

Calculés par `pc build` (`carbone.json`, intensités MOYENNES, émissions directes, hors Corse) :

| | Production (éCO2mix) | Consommation (ODRÉ, RTE) | Référence RTE |
|---|---|---|---|
| Moyenne 2025 | 18,4 g | 20,1 g | 19,6 / 20,0 (−6,3 % / +0,7 %) |
| Moyenne 2024 | 20,1 g | 22,1 g | 21,7 production (−7,4 %) |
| Moyenne 2022 | 53,8 g | 62,1 g | — |
| Maximum horaire 2025 | 57,5 g (14/01, 9 h-10 h) | 60,0 g | 58 g, série non précisée |
| Heures sous 15 g, 2025 | 53 % | 47 % | « près de la moitié » |
| Hiver / été 2025 | 26,0 / 11,5 g | — | — |
| Case mois × heure min / max 2025 | 7,2 g (sept., 13 h) / 36,2 g (févr., 18 h) | — | — |
| Idem 2022 ; hiver / été 2022 | 31,6 / 72,4 g ; 61,9 / 45,6 g | — | — |

Le maximum horaire de 2022 (110,5 g production, 154 g consommation) et ceux de 2024 sont aussi
au référentiel. Saisis : les chiffres RTE ci-dessus ; 29,0 g en ACV ; 10,9 / 3,2 / 2,3 Mt et
40 % ; 27 Mt « évitées » ; 15 g (« intensité de fond ») ; 331 g (CCG, direct) ; ADEME-RTE 2007
(450-550 g, 25 %, 400 g) ; CRE 0,59 tCO2/MWh ; UE 183 et 19,6 gCO2eq/MJ, 20 €/MWh ; AIE 180
MtCO2 ; SEQE 833, 1 096, 400 millions, TNAC 2024 et 2025 ; 15 pays du traçage des flux.

**Contrôles `pc check` ajoutés** : (1) `carbone.json` = recalcul depuis la table publiée et le
jeu ODRÉ, moyennes recalculées par une seconde implémentation, ordre min ≤ p10 ≤ p50 ≤ p90 ≤
max, matrices complètes et dans [min, max] ; (2) recoupements de même éditeur : production dans
une bande de −9 à −4 % du Bilan (Corse et facteurs ; calibrée sur 2024 et 2025), consommation à
± 2 %, part sous 15 g entre 40 et 55 %, maximum 2025 de la production à 58 ± 0,5 g ; lignes
d'information (émissions 10,02 Mt hors Corse contre 10,9 Mt, −8,1 %) ; (3) chiffres de
`chiffres.json` = `carbone.json`, **et égaux à l'arrondi de la valeur non arrondie** (voir
erreur ci-dessous).

## Choix

- Deux séries, toutes deux appelées « intensité moyenne » partout (texte, libellés, notes,
  JSON). La consommation n'est pas republiée heure par heure : seuls des agrégats.
- Graphique : mois × heure plutôt que jour × heure (le propos est la variation saisonnière et
  horaire, et 288 cases se lisent sans JavaScript). Classes 10 / 20 / 40 / 60 g, choisies pour
  que 2025 (7 à 36 g) et 2022 (32 à 72 g) restent lisibles sur la même échelle.
- **Pas de calcul « 1 GW × moyenne = 0,17 Mt/an »** : la relecture le proposait comme piège
  montré, mais la consigne exclut le tableau en Mt/an ; le piège est dit en mots (« donne la part
  des émissions existantes qu'on lui attribuerait dans un inventaire »).
- Argument « moyen ≠ marginal » appuyé sur les chiffres de RTE (cogénérations et déchets « 
  indépendant[s] des conditions du marché »), sans calcul du site ni phrase causale de notre cru.
- SEQE : trois phrases tirées des textes (décision 2015/1814 consolidée, communication TNAC),
  lecture des règles « sans les modéliser », part non chiffrée, proposition de fin de
  l'invalidation signalée. Aucune référence académique, faute de texte relu.
- Encart « en préparation » : directive `::: chantier nom :::` et fichier Markdown à trois
  sections fixes, texte simple (pas de chiffre, pas de lien), plutôt que du texte dans le code.
- Ni C2, ni C3, ni la part française de C4, ni régression, ni arrêts fortuits, ni Mt/an.

## Erreur de l'agent (à consigner dans `ERREURS.md` par Claude)

- **Double arrondi** : la première version de `carbone.json` arrondissait les intensités au
  millième ; `carbone_conso_moyenne_2025` (valeur exacte 20,14978 g) devenait 20,150 puis 20,2
  au lieu de 20,1. Repéré par moi en relisant les valeurs avant le texte, jamais publié.
  Correction : 4 décimales dans l'export, et contrôle `pc check` qui compare chaque chiffre
  publié à l'arrondi de la valeur non arrondie. Le même risque existe en principe pour
  `quand.json` (4 décimales pour les TWh et les parts) : non vérifié.
- Deux pièges attrapés par les garde-fous existants avant tout rendu : une ligne commençant par
  « 2024. » (liste involontaire) et un test trop fragile que j'avais écrit (retiré).

## Captures (1366 × 768 et 390 × 844, clair et sombre, `npm run dev`)

Dans `[caviardé : chemin local]/carbone-page/` :
`haut-*`, `graphique-*`, `encart-*`, `accueil-*` (haut de l'accueil) et
`accueil-grille-1366x768-clair.png` (grille des enquêtes). Les vues `graphique` et `encart`
sont découpées dans des captures pleine page (`long-*`) : l'ancre d'URL donnait une page vide
avec `headless_shell`.

## Doutes, à trancher par la relecture

1. **« 3 % du temps au-dessus de 100 g en 2023 »** (BE2025 p. 105) : le jeu ODRÉ actuel donne
   0,35 % des heures. Cause non établie (recalcul d'avril 2026 avec les facteurs actuels ?
   autre série ?). Non publié ; affiché par `pc check` comme « non recoupé ».
2. **Maximum de 58 g** : RTE ne dit pas s'il s'agit de la production ou de la consommation ;
   la production redonne 57,5 g, la consommation 60 g. Coté C.
3. « 6 % et 7 % » d'écart au Bilan : attribués en mots à la Corse et aux facteurs, d'après la
   contre-vérification du 26/11 (Corse ≈ 3/4 en 2024, 9/10 en 2025), chiffrage qui n'est pas
   dans le pipeline.
4. **SEQE** : la phrase « une partie d'une émission supplémentaire s'ajoute au total européen »
   est une lecture des règles, pas un calcul ; avec un TNAC dans la bande 833-1 096 millions,
   la réponse du placement en réserve est d'une unité par tonne, mais la dynamique pluriannuelle
   n'est pas modélisée. À relire par une experte du marché carbone.
5. « Personne ne publie de facteur marginal français récent » : « à notre connaissance », sur
   une recherche non exhaustive (spike + mes lectures). Le facteur de la CRE (2019) est
   présenté comme un paramètre de prix, ce qu'il est d'après la délibération.
6. Horodatage du jeu ODRÉ de la consommation (début d'heure supposé) : sans effet sur les
   moyennes annuelles, possible décalage d'une heure du profil (non tracé pour la consommation).
7. Marge du test de taille des exports (`test_taille_des_exports`, < 15 Mo) : 5,6 Ko avant mon
   passage, `meta.json` a pris environ 250 octets. `carbone.json` a son propre test (< 100 Ko).
8. Le règlement 2023/1185 est cité depuis le PDF de l'Office des publications, pas depuis
   EUR-Lex ; la date d'entrée en vigueur (10/07/2023) est déduite de la règle des vingt jours,
   article final non recopié.

## Corrections après relecture

Relecture adverse : `docs/relectures/2026-11-26-carbone.md` (F1 à F5, C1, f1 à f16), avec les
précisions de Claude (vérification à la source de F2 et F4). Rien n'est commité.

**Nouveaux documents relus par moi** (`data/raw/carbone/`, non versionné) :

| Source | Passages | SHA-256 (début) |
|---|---|---|
| RTE et ADEME, rapport « chauffage » (décembre 2020, PDF du 28/01/2021, copie de Claude) | p. 208 (« n'est pas généralisable à un volume important… », « La méthode marginale n'apparaît donc pas adaptée dans une approche prospective à long terme si le parc de production évolue. ») ; p. 209 (méthode incrémentale avec adaptation du mix, mobilité 2019, hydrogène 2020, « les variations d'émissions induites sur les systèmes électriques des pays voisins ») | fd76eee3 |
| Note ADEME-RTE de 2007 (relue de nouveau) | p. 2 (« compte tenu des équipements de production existants et décidés », ampleur de « quelques dizaines de TWh ») ; p. 4 (« Les résultats sont valables pour des décisions représentant plusieurs dizaines de TWh », « Nécessite d'être revisitée régulièrement… ») | 41eb003b |
| Conseil de l'UE, document 14944/26 du 28/10/2026 (anglais ; pas de version française servie) | lu en entier : compromis approuvé par le Coreper, considérants 3, 3a et 3b, nouveau § 5 bis (400 millions jusqu'à l'entrée en vigueur, 700 millions ensuite), entrée en vigueur au 3e jour après publication | e0f0f72d |
| Parlement européen, fiche de procédure 2026/0085(COD) (Observatoire législatif, HTML) | étapes : proposition 01/04/2026, décision du Parlement en 1re lecture le 24/11/2026 (T10-0381/2026), état « Awaiting Council's 1st reading position ». **Texte adopté T10-0381/2026 non relu** (le site du Parlement renvoie une page vide) : le texte écrit seulement qu'il a été adopté en première lecture | fbcdee52 |
| Règlement délégué (UE) 2024/1408, JO du 21/05/2024 (français, Office des publications) | article 1er, point 7 : nouvel article 6 du 2023/1184, identique en substance (dates, 20 €/MWh, 0,36 × prix du quota, option du 1er juillet 2027) | ed9945cd |
| BE2024 (relu de nouveau) | p. 99 : « environ 3 % du temps » au-dessus de 100 g en 2023, « intensité de fond » à 10 g, maximum de 67 g en 2024 | f7e38668 |

**Fond.**
- **F1** : paragraphe réécrit comme proposé (cogénérations au fioul non chiffrées par RTE ;
  citation « ne représente que 40 % » ; figure 5.6). Contrôle `pc check` ajouté :
  (cogénérations au gaz + déchets) / total ≤ 1 − part hors socle (50 % ≤ 60 %).
- **F2** : puce « RTE et l'ADEME, 2020 », source `rte-ademe-2020-chauffage`, chapeau, section
  « personne ne le publie » et encart (« Pourquoi ») retouchés ; puce 2007 complétée par son
  domaine de validité (p. 2 et p. 4) ; la page dit que les deux textes divergent, sans trancher.
  **La thèse de la section change : à soumettre à l'auteur (décision du 26/11).**
- **F3** : phrase datée d'après le document du Conseil (lu) et la fiche de procédure (lue) ;
  nouveau chiffre `ets_seuil_invalidation_compromis` (700 millions, non adopté) ; phrase
  conditionnelle « Si ce texte entre en vigueur… ». Périmètre corrigé : Union seulement,
  Grande-Bretagne (système britannique) et Suisse (système suisse, lié) nommées. Le seuil de
  20 MW thermiques proposé par la relecture n'est pas écrit (directive non relue). L'état des
  négociations de liaison entre les systèmes européen et britannique n'est pas vérifié, et
  la page n'en dit rien.
- **F4** : `intensite_max_rte_2025` rattaché à la consommation, cote **B**
  (`verification: contre-verification`), recoupement avec `carbone_conso_max_2025` (60 g) ;
  `pc check` compare désormais à la consommation (± 3 g), la production devient une ligne
  d'information. Texte : « Pour la consommation, RTE donne un maximum de 58 g ; sa monotone […]
  culmine à ce niveau ». Les « 3 % » ne sont pas publiés ; la raison est écrite au référentiel et
  dans `pc check`. Je n'écris pas les « 0,4 % » : c'est une lecture graphique, que je n'ai pas
  faite moi-même.
- **F5** : texte (« RTE y compte zéro pour l'incinération des déchets », annexe p. 145, sans
  l'explication que RTE n'écrit pas), périmètre de `intensite_prod_acv_rte_2025` et motif de la
  contrainte corrigés.

**Forme.** f1 « nécessite d'être revisitée régulièrement » ; f2 `ue_correlation_seuil_prix`
cité dans le règlement 2024/1408, avec un nouveau chiffre `ue_correlation_coef_quota` (0,36,
exprimé en tCO2eq/MWh pour que le produit par un prix en €/t donne des €/MWh) et « exige
notamment » ; la révision ciblée annoncée en mai 2026 n'est pas mentionnée (non lue) ; f3 « du
pays ou de la zone de prix » ; f4 « près de » et titre de la puce adouci ; f5 « publié et
sourcé » ; f6 « notamment » et liste complétée (sans chiffres) ; f7 eau de barrage ; f8 « facteur
moyen de filière », TAC 497 g saisi (`facteur_tac_direct_rte`) ; f9 source `rte-eco2mix-emissions`
citée ; f10 « d'après une estimation du site » ; f11 note de convention d'horodatage sur les
moyennes et maxima calculés, et puce « La décimale » dans les limites ; f12 date d'usage du
facteur de la CRE et « non vérifié s'il a été remplacé » ; f13 note de `intensite_fond_rte` (10 g
au BE2024) ; f15 limite d'échelle dans l'encart ; f16 remarque du graphique.

**Mécanisme nouveau** : `chiffres.json` porte désormais une clé `sources` (toutes les sources du
référentiel), et le site résout `{{source:cle|page}}` sur l'ensemble des sources, plus seulement
sur celles qu'un chiffre cite (`chargerSources`, `server/chiffres.ts`). Les documents
réglementaires et la fiche de procédure se citent donc sans chiffre artificiel. Test ajouté.

**Contrôles.** C1 : `controle_chiffres_calcules_couverts` vérifie, toutes sources confondues,
que chaque chiffre calculé relève d'une source qu'un contrôle couvre (`pdc-quand`,
`pdc-carbone`) ; les contrôles par enquête sont gardés. Test synthétique : une source inconnue
et une source absente donnent deux échecs.

**Taille des exports (f14).** Le test n'a pas été modifié. Mesure du 26/11/2026 après
`pc build` :
- fichiers comptés par le test : 14 994 667 octets, marge **5 333 octets**. `horaire/2026.csv`
  grossit d'environ 2 Ko par jour de données, le test cassera donc dans quelques jours, sans
  aucun changement de code ;
- tout `data/export/` : 15 756 650 octets, dont `chiffres.json` 731 Ko (697 Ko avant la clé
  `sources`) et `carbone.json` 31 Ko (testé à part, < 100 Ko). `quand.json` a aussi son propre
  test (< 500 Ko) ;
- répartition : `horaire/*.csv` 8,6 Mo (≈ 3,1 Mo compressés en gzip), `systeme_horaire.parquet`
  5,0 Mo (incompressible), `prix_quart_horaire.csv` 1,0 Mo (0,2 Mo compressé).

Proposition, à trancher par l'auteur (DECISIONS.md), sans rien d'irréversible d'ici là :
1. **Mesurer ce qui est réellement versionné** : compter tous les fichiers de `data/export/`
   (rien n'y échappe plus, ni `chiffres.json`, ni les futurs JSON d'enquête), avec un budget
   global explicite, par exemple 20 Mo, et une marge annuelle écrite (environ 0,7 Mo par an de
   CSV horaire). On ne relève pas le plafond en douce, on le décide et on le date.
2. **Garder des plafonds par fichier** pour les JSON des enquêtes, comme `quand.json` et
   `carbone.json` aujourd'hui, pour qu'un export qui dérape se voie seul.
3. Si l'auteur préfère ne pas relever le budget, l'allègement le moins risqué serait de ne plus
   versionner l'année en cours dans `horaire/` (reconstruite au build). Mais cela change ce que
   le site publie, à décider aussi. Je ne propose pas de toucher aux décimales ou aux colonnes
   publiées : ce serait changer des valeurs publiées.

**Valeurs publiées** : `chiffres.json` comparé à l'état d'avant mon travail, 0 retiré, 0 modifié,
51 ajoutés (29 saisis, 22 calculés). `quand.json`, `systeme_horaire.parquet` et
`prix_quart_horaire.csv` sont identiques, tout comme `horaire/` (non modifié selon git).

**Vérifications** : `pc build` ; `pc check` 33 contrôles, 0 échec ; `pytest` 202 ; `npm run
check` 0 erreur ; `npm test` 185 ; `format:check` ; `npm run build`. Captures refaites (mêmes
noms, même dossier `scratchpad/carbone-page/` : `haut-*`, `graphique-*`, `encart-*`,
`accueil-*`, en 1366 × 768 et 390 × 844, clair et sombre).

**Doutes restants** : texte adopté par le Parlement non relu (on écrit seulement l'adoption en
première lecture) ; état d'adoption au Conseil à revérifier avant publication ; statut de la
liaison entre les systèmes britannique et européen non vérifié ; la phrase sur la Grande-Bretagne et la
Suisse n'a pas de source primaire dans le référentiel ; le maximum de 58 g reste une attribution
par la figure (cote B, non A) ; le budget de taille est à décider avant le prochain `pc build`
qui fera dépasser le plafond.
