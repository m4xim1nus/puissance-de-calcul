# Limites de « Quand ? » et du simulateur : froid extrême, écrêtement, plancher nucléaire

Rapport de l'agent chargé du point 3 de l'étape 4 (`ROADMAP.md`), 26/11/2026.
Règle appliquée : les trois niveaux de `making-of/DECISIONS.md` (sourcer et
afficher ; estimer nous-mêmes ; hypothèse réglable). Rien n'est commité ;
`making-of/` n'est pas touché (les décisions à consigner sont listées en fin
de rapport). Relecture adverse « lectrice experte » à faire avant publication.

## 1. Sources trouvées (froid extrême)

Toutes lues dans le PDF ou dans l'API, page relue, citation recopiée mot pour
mot. Copies locales hors dépôt (non versionnées), empreintes SHA-256 :

| Clé (`sources.yaml`) | Document | SHA-256 |
|---|---|---|
| `rte-hiver-2022-2023` | RTE, *Perspectives pour le système électrique pour l'automne et l'hiver 2022-2023* (PDF du 14/09/2022) | `8322bc8d5639cd45a5af2050a3f941a3bdc3ca69f71e551959a2a72d858cda94` |
| `rte-be2017` | RTE, *Bilan électrique 2017* (version imprimable, PDF du 21/02/2018) | `67345df324e0a91fe52892fbe24f7d243d3e20d15c0b167332f2cdf2b7606971` |
| `rte-hiver-2018-2019` | RTE, *Synthèse — L'équilibre offre-demande pour l'hiver 2018-2019* (PDF du 19/11/2018) | `a52024d803c127b5a21df380ec48efebadc5402ae59797e5a00638350b8b3a68` |
| `rte-hiver-2024-2025` | RTE, *Perspectives pour l'hiver 2024-2025*, synthèse (PDF du 13/11/2024) | `7b7cc6c26cdf3784146627d979b6ad5423bb8ba1f9455ce407dcf81cd52b5706` |
| `cre-2012-pics-prix` | CRE, délibération du 10/05/2012 sur les pics de prix des 9 et 10/02/2012 | `b5ebca75bfa19889e58eb57046a177becba508ace728c14774ee70ddd764dfa8` |
| `rte-eco2mix-odre` (existante) | éCO2mix national, données définitives, API ODRÉ, requête du 26/11/2026 | réponse JSON : `faee6737e0e84ddc2c64cd095d5b953cadbd7233b5539ea3c05db361f96f44bb` |

**Pointe record** (`pointe_conso_record_2012`, 102,1 GW, confiance B) :
- source principale, éCO2mix définitif (ODRÉ, jeu `eco2mix-national-cons-def`,
  tri par consommation décroissante sur tout le jeu, 2012 à 2026) :
  `date_heure 2012-02-08T18:00:00+00:00, consommation 102098, nature Données définitives`,
  soit 19 h 00 à Paris, point demi-horaire (la demi-heure qui se termine à
  19 h selon la convention d'horodatage du site), France continentale **hors
  Corse**. Valeur suivante : 101 201 MW à 18 h 30 UTC le même jour ;
- RTE, hiver 2024-2025, p. 18 : « vague de froid de février 2012 (températures
  moyennes France inférieures de 8 °C à la normale saisonnière durant une vague
  de froid longue, ayant conduit à une pointe historique de consommation de
  102 GW) » ;
- RTE, hiver 2018-2019, p. 4 : « une valeur proche du pic historique de
  consommation à 102 000 MW » (figure : 2012) ;
- CRE, délibération du 10/05/2012, p. 1 : « Le 8 février, soit la veille du
  pic de prix, le pic de consommation est atteint avec 102,1 GW pour la pointe
  du soir. » Autre éditeur, même donnée (comptage RTE) : non indépendant.

Le Bilan électrique 2012 de RTE n'est plus sur `assets.rte-france.com` (404 au
chemin des autres bilans republiés) ; une copie existe sur un site tiers, non
utilisée.

**Gradient hivernal** (`thermosensibilite_hiver_rte`, 2 400 MW/°C, B) :
- RTE, automne-hiver 2022-2023, p. 59-60 : « le gradient hivernal (sensibilité
  de la consommation à la baisse de température en hiver) est aujourd'hui
  estimé à 2 400 MW/°C. » Même page 59 : « Si le profil journalier est
  relativement peu affecté lors de tels épisodes, le niveau global de la
  demande peut croître fortement » ;
- recoupements, même éditeur : BE2017, p. 15 (page du PDF) : « Elle est
  estimée en moyenne à environ 2 400 MW par degré Celsius en hiver », et
  « Cette sensibilité […] est variable au cours de la journée » ; hiver
  2018-2019, p. 4 : « pour chaque degré en moins, la consommation peut
  augmenter jusqu'à 2 400 MW » (« jusqu'à » : formulation de plafond, pas de
  moyenne, voir doutes) ; BE2025, p. 126 : « L'augmentation de la
  consommation par degré perdu pour les basses températures est restée
  quasiment constante au cours des dix dernières années pour les pays
  analysés » (qualitatif, cinq pays dont la France).
- **Pas trouvé** : une valeur chiffrée plus récente que 2022. Cherchée dans
  les synthèses des hivers 2022-2023 (actualisation de janvier), 2023-2024,
  2024-2025, 2026-2027, les perspectives du 09/12/2025, le BE2024, le BE2025
  et les volets du Bilan prévisionnel 2025 présents en local. Année de
  référence saisie : « estimation de 2022 ».

**Repères de température** : `froid_2012_ecart_normale` (8 °C, hiver
2024-2025 p. 18), `froid_decennal_ecart_normale` (6,5 °C) et
`froid_centennal_ecart_normale` (12 °C), hiver 2018-2019 p. 4 : « 85 000 MW
aux températures moyennes de saison », « 100 000 MW en cas de vague de froid
décennale à 6,5°C en moyenne sous les normales de saison en janvier et
février », « 109 000 MW en cas de vague de froid centennale à 12°C ».
Calcul du site (note du chiffre) : 2,3 GW par degré jusqu'au froid décennal,
1,6 GW au-delà.

Toutes ces entrées portent `verification: spike` : une contre-vérification
indépendante reste à faire.

## 2. Choix de spécification (froid supplémentaire)

Écrits dans `docs/SIMULATEUR.md` (section « Froid supplémentaire »). En bref :

- **Épisode** : les 168 heures consécutives (7 jours, `DUREE_FROID_H`, choix
  du site, non réglable) de charge résiduelle **observée** moyenne la plus
  élevée (`episode_froid` : moyenne des heures renseignées, fenêtre sans RN
  écartée, égalité → la plus ancienne). Sans série de température, on ne sait
  pas désigner les jours les plus froids ; les plus tendus sont ceux où un
  froid de plus pèse le plus. Vérifié sur 2015-2025 : toujours entre
  novembre et février (2025 : 13-20 janvier ; 2019 : mi-novembre, ce qui
  montre que « plus tendus » n'est pas « plus froids »).
- **Ajout** : froid × gradient, uniforme à toutes les heures de l'épisode
  (RTE : profil journalier peu affecté).
- **Double compte** : traité par la définition. Le réglage s'appelle « froid
  supplémentaire », pas « X °C sous les normales » (écart à la consigne,
  assumé) : les jours choisis ont déjà leur froid, les degrés réglés s'y
  ajoutent. C'est dit dans la raison du réglage, dans la tuile
  « Consommation horaire maximale » et dans le texte partagé.
- **Ce que le froid touche** (`effet_charge`, paramètre `supplement`) : RN
  « après » (RN + froid + charge) ; les seuils restent **observés** (maximum
  de l'année, maximum 2015-2025) ; la monotone « avant » reste observée ; le
  froid passe **avant** la charge dans J (`max(0, J − froid)`), pour ne pas
  compter deux fois le même nucléaire inemployé ; l'effacement est classé sur
  RN + froid ; énergie ajoutée, part dans J et prix restent ceux de la
  consommation ajoutée (prix observés).
- **Froid seul** : une simulation à X nul donne les heures au-delà des maxima
  dues au froid seul. La phrase « il faudrait effacer au moins N* heures »
  n'est écrite que si ce nombre est nul ; sinon le simulateur dit qu'aucun
  effacement ne supprime ces heures (propriété testée des deux côtés).
- **Tuile ajoutée** (avec du froid seulement) : consommation horaire maximale
  du scénario, comparée à l'observée et à la pointe record ; dit quand le
  scénario dépasse la pointe (le gradient est alors prolongé hors de ce que
  RTE publie).
- **Plage** : 0 à 12 °C (froid « centennal » de RTE), pas de 0,5, défaut 0.

**Plancher** : réglage 0 à 3 GW, pas de 0,1, défaut 1 GW (inchangé). Repères
dans la raison : J moyen aux heures à plus de 150 €/MWh en 2025 (0,5 GW) et
la plus haute de ces moyennes sur 2015-2025 (2,0 GW en 2020, sur 2 heures),
lus dans le référentiel au prérendu. Les chiffres publiés de « Quand ? »
restent à 1 GW.

**Interface** : cinq réglages à gauche, chacun sur trois lignes (nom et
saisie, curseur, résumé « Défaut … ; plage. Raison » qui ouvre le repli).
Consigne réduite à « Le lien de la page porte le scénario. » URL :
`froid` (°C) et `plancher` (GW), omis à leur défaut ; une ancienne adresse
redonne le même scénario (test).

## 3. Écrêtement (niveau « estimer »)

Définitions revérifiées dans le BE2025 : p. 42, « En 2025, les épisodes de
prix négatifs ont conduit à renoncer à environ 3 TWh de production solaire et
éolienne », note 19 « 1,3 TWh de production éolienne terrestre et 1,6 TWh de
production solaire (estimation RTE) », figure 2.28 « Estimation des volumes
de modulation solaire et éolienne lors d'épisodes de prix négatifs » (éolien
terrestre et solaire seulement) ; p. 43, 0,1 TWh écrêtés par les ajustements
à la baisse demandés par RTE (éolien en mer compris, figure 2.30). Les
entrées du référentiel sont conformes.

Calcul (`quand_ecretement_prix_negatif_2025`, `pc build`) : 3 TWh = 3 × 10⁶
MWh ÷ 513 heures à prix day-ahead strictement négatif en 2025 = **5,85 GW**
en moyenne, publié **5,8 GW**, « calcul du site ».

Sens : l'éolien et le solaire observés sont nets de la production renoncée,
donc la RN observée est **au-dessus** de la RN sans écrêtement ; le surplus
réel de ces heures est plus grand que celui que montre la RN (−9,8 GW en
moyenne observée ; de l'ordre de −15,7 GW sans la production renoncée).
Pourquoi une borne haute (de la moyenne) : une partie de la production
renoncée a pu l'être hors de ces 513 heures (quarts d'heure négatifs d'heures
positives depuis le 01/10/2025), ce qui ne peut que baisser la moyenne sur ces
heures. Limites, dites dans la note du chiffre : borne « à l'estimation de
RTE près » (« environ » 3 TWh : ±0,1 TWh déplace la moyenne de 0,2 GW) ; les
0,1 TWh écrêtés par RTE, qui recouvrent probablement en partie ce volume,
ajouteraient au plus 0,2 GW ; ce n'est pas une borne heure par heure.

Contrôle `pc check` ajouté : recompte polars des heures à prix négatif,
égalité du chiffre, et garde-fou d'unité (5,85 GW < 13,7 GW d'éolien + solaire
observés en moyenne à ces heures).

## 4. Chiffres nouveaux

| Identifiant | Valeur | Nature |
|---|---|---|
| `pointe_conso_record_2012` | 102,1 GW | saisi, éCO2mix (RTE) |
| `thermosensibilite_hiver_rte` | 2 400 MW/°C | saisi, RTE |
| `froid_2012_ecart_normale` | 8 °C | saisi, RTE |
| `froid_decennal_ecart_normale` | 6,5 °C | saisi, RTE |
| `froid_centennal_ecart_normale` | 12 °C | saisi, RTE |
| `quand_conso_max_pluri` | 95,7 GW (28/02/2018, 11 h-12 h) | `pc build` ; repère du texte « froid extrême » |
| `quand_ecretement_prix_negatif_2025` | 5,8 GW | `pc build` |

Deux grandeurs ajoutées à `pc/chiffres.py` : `gradient_thermosensibilite`
(MW/°C, GW/°C) et `ecart_temperature` (°C). `quand.json` gagne
`consommation_max_pluriannuelle` (et son paramètre) ; rien d'autre n'y
change. Comparaison avant/après de `chiffres.json` : 7 ajouts, 0 retrait,
0 modification.

## 5. Textes

- `docs/enquetes/partage/limite-froid.md` et `limite-ecretement.md` : les deux
  points de « Ce que ce calcul ne dit pas », écrits une fois, inclus dans
  `docs/enquetes/quand.md` et `site/src/lib/simulateur/lecture.md` par une
  ligne `- ::: inclure nom :::` (nouvelle fonction `inclureFragments` de
  `site/src/lib/server/enquetes.ts`, testée ; la forme en item de liste est
  celle que Prettier laisse en place : une première forme en ligne nue a été
  déplacée par Prettier et sortait de la liste, corrigé avant la fin) ;
- « Quand ? » : phrase du plancher complétée (« le simulateur permet de régler
  ce plancher ») ;
- simulateur : raison des deux réglages, tuile de consommation, phrases des
  maxima, puce « Une vague de froid » dans l'en-tête, paragraphes « au plus »
  et « effacement » de la lecture ajustés.

## 6. Tests et contrôles (26/11/2026, fin de session de l'agent)

- `uv run pc build` : OK ; `uv run pc check` : 27 contrôles, 0 échec (dont
  « écrêtement réparti » et la consommation horaire maximale sous la pointe
  record) ; `uv run pytest` : 162 réussis ;
- `npm run check` : 0 erreur ; `npm test` : 168 réussis (dont la parité
  moteur ↔ référence sur 7 nouveaux cas partagés calculés à la main dans
  `pipeline/tests/cas_quand.json` : 3 `simuler` avec froid et plancher,
  4 `episode_froid`) ; `npm run format:check` : OK ; `npm run build` : OK.

Captures (navigateur sans tête, 1366 × 768, scratchpad de la session, non
versionnées) : `avant.png` (état d'origine), `defaut.png` (défauts :
résultats identiques à l'origine, les cinq réglages tiennent sans défiler),
`froid.png` (`?x=5&effacement=100&froid=8&plancher=0.5`), `ancienne-url.png`
(`?annee=2022&x=5&effacement=100`), `telephone.png` (390 × 844).

## 7. Doutes, et ce que j'ai repéré dans l'existant

1. **Hors écran dans un cas** : avec du froid (huit tuiles et une phrase de
   scénario de trois lignes), la dernière ligne des sources de la colonne des
   résultats passe sous le bas de l'écran à 1366 × 768. Les réglages et les
   tuiles restent visibles ; aux défauts, tout tient.
2. **Linéarité et double compte, chiffrés** : avec 8 °C de plus, la
   consommation horaire maximale du scénario va de 98 GW (2019) à 115 GW
   (2018) et dépasse la pointe de 2012 dans 7 années sur 11. Le simulateur le
   dit (tuile), mais un lecteur pressé peut prendre 8 °C pour « février 2012 ».
   Brancher une série de température (Météo-France, ou la température
   moyenne France de RTE si elle est publiée en open data) permettrait de
   régler un écart aux normales : à mettre au backlog.
3. **« jusqu'à » contre « en moyenne »** : RTE écrit le même 2 400 MW tantôt
   comme une moyenne (BE2017, 2022), tantôt comme un plafond (hiver
   2018-2019). Le site retient la moyenne, la seule définition explicite.
4. **Périmètre des pointes** (constat, rien corrigé) : la pointe de 2012
   d'éCO2mix est hors Corse (102 098 MW) et correspond aux 102,1 GW de la CRE
   et de la presse de l'époque. `pointe_conso_2025` (88 GW) est saisi « Corse
   comprise », d'après la définition de la consommation brute du glossaire du
   BE2025, pas d'après la phrase citée ; le texte ne compare pas les deux,
   mais une phrase qui les rapprocherait mélangerait deux périmètres.
   De même, la synthèse 2018-2019 donne 96 600 MW pour 2018 quand éCO2mix
   hors Corse donne 96 272 MW (demi-heure du 28/02/2018 à 19 h 30) : écart
   non expliqué, non utilisé.
5. **Duplications restantes** : seuls les deux points traités sont partagés.
   Les paragraphes « au plus », « en énergie », « qui servirait », « deux
   maxima », « les marges de RTE » et le point « La pointe exacte » restent
   recopiés à la main entre `quand.md` et `lecture.md` (déjà au backlog
   d'après `ERREURS.md`) ; la directive d'inclusion permet maintenant de les
   rassembler.
6. **Confiance B** pour `quand_ecretement_prix_negatif_2025`, comme les autres
   `quand_*` ; on pourrait plaider C (entrée « environ », borne conditionnelle).
7. **Fichiers modifiés par un tiers pendant ma session** (pas par moi) :
   `ROADMAP.md`, `making-of/DECISIONS.md`, `making-of/ERREURS.md`,
   `making-of/JOURNAL.md`, et les fichiers non suivis `docs/spike/carbone.md`,
   `pipeline/explo/spike_carbone*.py`.
8. **Caviardage** : aucun chemin de machine dans les fichiers versionnés
   ajoutés ; `max(0, …)` apparaît dans le code et la spécification (le
   `git grep -w -i max` d'avant push le remontera, sans rien à caviarder).

## 8. Décisions à consigner (par la session principale)

- Épisode de froid : 7 jours de RN observée la plus élevée, ajout uniforme,
  réglage défini comme « froid supplémentaire » et non écart aux normales
  (double compte traité par la définition) ; plage 0-12 °C ; le froid passe
  avant la charge dans J ; seuils observés inchangés (Claude, sur délégation).
- Plancher réglable 0-3 GW, défaut 1 GW.
- Écrêtement : borne haute de la moyenne, 5,8 GW, « calcul du site ».
- Fragments partagés `docs/enquetes/partage/` et directive
  `- ::: inclure nom :::`.
- Nouveau chiffre calculé `quand_conso_max_pluri` (repère du texte « froid
  extrême »).
