# Relecture adverse « lectrice experte » — accueil, Combien ?, Méthode

Date : 26/11/2026. Relecture faite par un agent Opus qui joue la lectrice cible : ingénieure marchés de l'électricité et modélisation, avant la première publication.

Périmètre : `site/build/index.html` (hero), `combien.html`, `methode.html`, rendus servis par `vite preview` et capturés dans Chromium headless (thème sombre). Pour chaque point douteux, je suis revenu aux sources : référentiel `data/export/chiffres.json`, PDF RTE (BE2025, BP2025 chapitre Consommation, BP2025 Principaux résultats, Tableau de bord de l'électrification), communiqué Campus IA, délibérations CRE 2025-120 et 2026-32, synthèse ADEME, classeur SDES, communiqué DGE du 30/01/2026 (relu en ligne). J'ai aussi recalculé les heures négatives sur `site/build/donnees/prix/*.json` et `data/export/horaire/*.csv`.

Les erreurs déjà consignées dans `making-of/ERREURS.md` ne sont pas reprises. Le point 3 contredit toutefois la correction n° 3 de l'entrée « Trois imprécisions ».

Gravités : **FOND** = une erreur qui ferait perdre confiance ; **PRÉCISION** = une imprécision qu'une experte relèverait ; **FORME** = une maladresse.

---

## Points

### 1. Fouju : 1 400 MW présentés comme un palier contractuel, et le palier de 700 MW a disparu — **FOND**

- **Pages** : /combien, texte (étage 3) et pyramide (étage « Signée ») ; référentiel `dc_signe_fouju_terme`.
- **Passage** : « Le premier contrat « fast-track », celui du Campus IA à Fouju, prévoit 240 MW, puis jusqu'à 1 400 MW à terme. Ce sont des paliers de puissance mise à disposition ». Sur la pyramide, étage « Signée » (« contrat de raccordement du Campus IA à Fouju : paliers de puissance mise à disposition ») : « 1 400 MW · à terme (non daté) ».
- **Preuve** : communiqué RTE / Campus IA du 26/01/2026 : « L'accord prévoit la mise à disposition par RTE d'un premier palier de puissance de 240 MW d'ici fin 2027, suivi d'un second palier de 700 MW avant fin 2029. Les infrastructures électriques seront **conçues de manière à permettre, à terme**, une montée en puissance jusqu'à 1 400 MW ». Le contrat porte donc sur 240 puis 700 MW. Les 1 400 MW sont une marge de dimensionnement des ouvrages, pas un palier contractualisé. Le site range sous « Signée » une capacité que le contrat ne garantit pas : c'est la confusion « annoncé ≠ signé » que le site s'interdit lui-même. Le palier réellement signé de 700 MW (avant fin 2029) n'apparaît nulle part, et le texte ne date pas non plus les 240 MW.
- **Correction** : « Le premier contrat « fast-track », celui du Campus IA à Fouju (signé le 26 janvier 2026), prévoit 240 MW mis à disposition d'ici fin 2027, puis 700 MW avant fin 2029. Les ouvrages sont dimensionnés pour permettre, à terme, jusqu'à 1 400 MW, mais ce niveau n'est pas un palier du contrat. » Dans le référentiel, créer `dc_signe_fouju_2029` (700 MW, fin 2029). Sur la pyramide, remplacer les 1 400 MW par les 700 MW. Si l'on garde les 1 400 MW, les sortir de l'étage « Signée » (marque distincte, libellé « dimensionnement des ouvrages, non contractuel »). Corriger aussi le libellé et le périmètre de `dc_signe_fouju_terme`.

### 2. Taux de concrétisation 30 % / 60 % : l'assiette est tronquée, d'un facteur 2 environ — **FOND**

- **Page** : /combien, § « 2030, 2035 ».
- **Passage** : « Pour 2030, RTE suppose qu'environ 30 % (lente) ou 60 % (rapide) des projets ayant demandé un raccordement au réseau de transport se concrétisent, avec un taux moyen d'utilisation de la puissance de raccordement de 20 %. »
- **Preuve** :
  - BP2025, Principaux résultats, p. 25, fig. 16, NB : « Les taux de concrétisation sont calculés par rapport aux projets disposant de droits d'accès au réseau de transport **pour un raccordement d'ici fin 2029** ».
  - BP2025, Consommation, p. 27-28 : « 60 % (4,3 GW) pour les projets ayant demandé un raccordement au réseau de transport d'électricité **et dont la mise en service est prévue avant 2030** ». La citation de la note 28 contient cette restriction, mais la phrase du texte la supprime.
  - Calcul : 4,3 / 0,60 ≈ 7,2 GW et 2,4 / 0,30 = 8 GW. L'assiette est donc d'environ 7 à 8 GW, pas les 14 GW (ni les 18 GW) du paragraphe sur les réservations. Une lectrice qui applique 60 % à 14 GW obtient 8,4 GW × 20 % × 8 760 h ≈ 14,7 TWh pour le seul transport. Le total dépasse alors largement les 15 TWh affichés (≈ 5 TWh de base + 7,5 TWh RPT + 2,4 TWh RPD selon RTE). Le texte, tel qu'il est écrit, est incohérent avec ses propres chiffres.
- **Correction** : « … 30 % (lente) ou 60 % (rapide) des projets disposant d'un accès réservé au réseau de transport pour une mise en service avant 2030 (soit environ 2,4 GW et 4,3 GW concrétisés) … ». Aligner le périmètre de `traj_hyp_concretisation_lente` sur celui de la trajectoire rapide.

### 3. Enedis : « sans préciser s'il s'agit de puissance de raccordement », alors que la source le précise — **FOND**

- **Pages** : /combien, texte (étage 4), pyramide (« côté Enedis, nature de la puissance non précisée »), note 15 (confiance C, « nature exacte de la puissance non précisée ») ; référentiel `dc_raccorde_rpd_2025`.
- **Passage** : « Côté Enedis, RTE indique 0,9 GW « en fonctionnement », sans préciser s'il s'agit de puissance de raccordement ou d'une autre grandeur. »
- **Preuve** : Tableau de bord de l'électrification, p. 26 (la page citée). Le graphique est titré « **Puissance raccordée** pour des datacenters [MW] ». L'encadré d'analyse dit : « La **puissance raccordée** des datacenters en service sur le réseau Enedis a augmenté régulièrement entre 2019 et 2023 ». Il ajoute une information que le site omet : « Depuis l'été 2025, un nouveau cadre réglementaire mis en place par les gestionnaires de réseaux permet de procéder à des **baisses de puissance de raccordement** lorsque celles-ci sont surdimensionnées […]. Ce nouveau cadre conduit à une baisse de la puissance raccordée pour les centres de données en 2025. » L'affirmation du site sur sa source est donc fausse et vérifiable en dix secondes sur la page qu'il cite. La correction n° 3 de l'entrée « Trois imprécisions » d'`ERREURS.md` (« la source dit seulement "en fonctionnement" ») a introduit l'erreur.
- **Correction** : « Côté Enedis, RTE indique 0,9 GW de puissance raccordée pour les data centers en service en 2025 (environ 400 sites). Ce chiffre est en baisse par construction : depuis l'été 2025, les gestionnaires de réseau peuvent réduire les puissances de raccordement surdimensionnées. » Retirer « nature de la puissance non précisée » de la pyramide, de la note et du référentiel. Réviser la confiance C, ou la justifier autrement (source unique). Consigner l'erreur dans `ERREURS.md`.

### 4. « 2035. » en début de ligne : le Markdown crée une liste et l'année disparaît — **FOND** (défaut de rendu, mais l'effet est un chiffre clé non daté)

- **Page** : /combien, § « 2030, 2035 » (capture : « … et 21 TWh en », puis une liste « 1. En décarbonation rapide, 15 TWh puis 32 TWh. »).
- **Passage source** : `docs/enquetes/combien.md`, ligne 103 : « 2035. En décarbonation rapide, {{traj_bp2025_rapide_2030}} puis ». CommonMark lit « 2035. » comme le début d'une liste ordonnée. Le HTML contient un second `<ol>`, rendu « 1. ».
- **Preuve** : `grep -o '<ol[^>]*>' site/build/combien.html` renvoie deux `<ol>`. Le texte rendu donne « la consommation atteint 10 TWh en 2030 et 21 TWh en », puis la liste. Les 21 TWh perdent leur année, et la page paraît cassée au premier coup d'œil.
- **Correction** : reformuler pour qu'aucune ligne ne commence par « nombre + point » (par exemple « en 2030 et {{traj_bp2025_lente_2035}} en 2035. » sur une même ligne), ou échapper (`2035\.`). Garde-fou : ajouter au test du Markdown un contrôle qui refuse toute ligne `^\d{3,}\. ` hors d'une liste voulue.

### 5. Note ADEME : « 9,91 TWh (8,16 inventoriés + 3,5 modélisés) », une addition fausse — **FOND** (dans une note dépliée, mais l'arithmétique se voit d'un coup d'œil)

- **Page** : /combien, note 5, « Recoupement indépendant (ADEME…) : 9,91 TWh (8,16 inventoriés + 3,5 modélisés) » ; référentiel `dc_conso_avec_internes_2024.recoupements`.
- **Preuve** : 8,16 + 3,5 = 11,66 ≠ 9,91. Synthèse ADEME, p. 5-6 : l'inventaire recense 8,16 TWh, dont « colocation […] 6,46 TWh, les centres de données privés pour 1,34 TWh, […] public pour 0,21 TWh et […] HPC pour 0,15 TWh ». Les 3,5 TWh modélisés « inclu[ent] des centres de données privés, des centres de données publics et des baies informatiques dans les bâtiments tertiaires ». Le total retenu (« colocation issus de la collecte et l'extrapolation surfacique », « 10 TWh en 2024 ») vaut donc environ 6,46 + 3,5 ≈ 10, et le tableau donne 9,91. Les 3,5 TWh remplacent les centres privés et publics inventoriés : ils ne s'y ajoutent pas.
- **Correction** : « 9,91 TWh : colocation inventoriée (6,46 TWh) et estimation surfacique des centres privés, publics et des salles internes (3,5 TWh) ».

### 6. « Il dit seulement que la montée en charge est lente » : une conclusion sans dénominateur — **PRÉCISION**

- **Page** : /combien, § « Ce que les data centers raccordés consomment vraiment ».
- **Passage** : « Pour les data centers raccordés entre 2022 et 2024, RTE indique une pointe de 35 MW en 2024. Ce chiffre ne se rapporte pas aux 0,63 GW […]. Il dit seulement que la montée en charge est lente. »
- **Preuve** : pour conclure à une montée en charge lente, il faut rapporter les 35 MW à une capacité. Or le texte vient d'écarter le seul dénominateur disponible, et la capacité raccordée de la cohorte 2022-2024 n'est pas publiée. En outre, la source écrit « utilisés au maximum », sans définition : rien ne dit s'il s'agit d'une pointe simultanée ou d'une somme de pointes (le référentiel le note, pas le texte). Le constat appartient à RTE : « La consommation des projets raccordés au RPT depuis 2022 reste aujourd'hui bien inférieure à la puissance totale mise à disposition » (TdB, p. 25).
- **Correction** : « RTE indique que ces data centers ont « utilisé au maximum » 35 MW en 2024 (grandeur non définie : pointe simultanée ou somme des pointes). RTE en conclut que leur consommation « reste aujourd'hui bien inférieure à la puissance totale mise à disposition ». La capacité de cette seule cohorte n'est pas publiée. »

### 7. Réservations « passées de 5 à 14 puis à 18 GW » : une série hétérogène présentée comme continue — **PRÉCISION**

- **Pages** : /combien, étage 2 et pyramide (étage « Réservée », trois points sur une même ligne).
- **Passage** : « Les réservations des data centers sont passées de 5 GW fin 2024 à 14 GW en novembre 2025, puis à 18 GW en mai 2026. »
- **Preuve** : les 14 GW viennent du BP2025-PR (p. 21, PTF signées au 1/11/2025, hors sites raccordés, projets suspendus inclus ; le BP2025-C, p. 6, dit « hors projets abandonnés ou ayant déjà été raccordés »). Les 5 et 18 GW viennent de la page web RTE (« RTE avait réservé près de 18 GW de capacité » ; intertitre « demandes de raccordement signées »), qui ne précise ni le traitement des sites raccordés ni celui des projets suspendus. La section « Ce qui manque » le reconnaît (« sous des définitions qui changent »), mais le verbe « sont passées de » et l'alignement sur une même ligne de la pyramide suggèrent une série homogène.
- **Correction** : « RTE donnait environ 5 GW fin 2024 et près de 18 GW en mai 2026 (page web, définition non précisée). Au 1er novembre 2025, le Bilan prévisionnel comptait 14 GW de PTF signées, hors sites raccordés. » Sur la pyramide, distinguer le point des 14 GW (autre source) par sa marque ou par une note.

### 8. Le taux de 22 % : RTE a aussi publié 20 %, ce que le texte ne dit pas — **PRÉCISION**

- **Page** : /combien, § « Ce que les data centers raccordés consomment vraiment ».
- **Passage** : « RTE publie un taux moyen d'utilisation de la puissance de raccordement de 22 % […] On ne le retrouve pas […] L'écart tient sans doute à la base de calcul ».
- **Preuve** : BP2025-PR, p. 23, fig. 14 (décembre 2025) : « les datacenters déjà raccordés n'utilisant par exemple à date que 20 % de leur puissance contractuelle de raccordement ». RTE a donc publié deux valeurs à trois mois d'intervalle (20 % puis 22 %), et le site n'en cite qu'une. Le « sans doute » est une conjecture du site, sans appui.
- **Correction** : citer les deux valeurs RTE (20 %, décembre 2025 ; 22 %, mars 2026), garder le calcul simple (≈ 15 %), et remplacer « sans doute » par « peut-être ». Ajouter le 20 % au référentiel comme recoupement non indépendant.

### 9. « Aucune courbe de charge […] seulement des totaux annuels » : contredit par la page elle-même — **PRÉCISION**

- **Page** : /combien, « Ce qui manque ».
- **Preuve** : la même page cite une grandeur infra-annuelle (« utilisés au maximum » en 2024, TdB p. 25). ODRÉ publie en outre au pas de 30 min les soutirages RPT par section NAF, dont la section J « Information et communication ». Le spike `docs/spike/datacenters.md` l'identifie comme « proxy horaire partiel » (≈ 0,26 TWh contre ≈ 1 TWh).
- **Correction** : « Aucune courbe de charge propre aux data centers n'est publiée. Il existe des totaux annuels, une valeur maximale annuelle pour une cohorte et un proxy partiel au pas de 30 min (soutirages RPT de la section NAF J, qui ne couvrent qu'environ un quart de la consommation des data centers raccordés au transport). »

### 10. « Environ 7 % de la consommation brute de 2024 » : numérateur de 2035, dénominateur de 2024 — **PRÉCISION** (et ton)

- **Page** : /combien, fin du § « 2030, 2035 ».
- **Passage** : « En énergie, la trajectoire haute de 2035 représente environ 7 % de la consommation brute de 2024 (32 ÷ 442). La question de l'accueil ne se réduit donc pas à des TWh par an ».
- **Preuve** : le calcul est juste (7,2 %), mais une modélisatrice rapporte une consommation de 2035 à la consommation de 2035 de la même trajectoire : environ 580 TWh en décarbonation rapide (BP2025-PR, fig. 16, consommation intérieure), soit ≈ 5,5 %. De plus, « donc » ne suit pas : qu'une part soit faible en énergie ne prouve pas que l'enjeu soit horaire. C'est l'hypothèse de travail du site, présentée comme une conclusion.
- **Correction** : donner les deux rapports (≈ 7 % de 2024, ≈ 5,5 % de 2035 dans la même trajectoire) et remplacer « donc » par une transition qui ne conclut pas : « Les enquêtes suivantes examinent la même question à l'heure et au poste. »

### 11. ADEME : un scénario construit sur les usages des Français, périmètre mal décrit — **PRÉCISION**

- **Pages** : /combien (« Le scénario tendanciel de l'ADEME, lui aussi sur un périmètre élargi, atteint 36,7 TWh en 2035 »), trajectoires, référentiel (`perimetre` : « territoire français, centres internes compris »).
- **Preuve** : synthèse ADEME, p. 7-8 : tableau « Évolution de la consommation électrique **pour l'usage français** », lignes « en France » et « import ». Le scénario tendanciel « rend compte de l'évolution potentielle des consommations électriques des centres de données pour les usages des Français ». Les trajectoires RTE partent au contraire des demandes de raccordement, campus tournés vers l'export compris. Il y a donc deux raisons de ne pas comparer, pas une seule (centres internes).
- **Correction** : périmètre « centres de données situés en France, centres internes compris, dans un scénario construit à partir des usages des Français (hors demande étrangère explicite) ». Ajouter cette réserve à la phrase.

### 12. « Non recoupé » à côté de « Confiance B : source primaire, recoupement partiel » — **PRÉCISION**

- **Pages** : /combien, une vingtaine de notes (3, 4, 6, 7, 8, 10, 12, 13, 14…), /methode (« B : Source primaire, recoupement partiel »).
- **Preuve** : la note 3, par exemple, affiche « Non recoupé. » puis « Confiance B : source primaire, recoupement partiel ». La règle codée (`pc/chiffres.py`) n'exige rien pour B. Le libellé affiché promet donc un recoupement que la note dément.
- **Correction** : redéfinir B comme « source primaire ; recoupement partiel ou absent ». Mieux : réserver B aux chiffres recoupés, même partiellement, et passer en C les chiffres non recoupés.

### 13. La pyramide a six étages, le texte annonce cinq grandeurs ; la pré-réservation n'est ni expliquée ni datée — **PRÉCISION**

- **Page** : /combien. Texte : « le mot « puissance » désigne cinq grandeurs différentes ». Titre de la figure : « recherchée, réservée, pré-réservée, signée, raccordée, appelée ».
- **Preuve** : l'étage « Pré-réservée (fast-track) », 3,8 GW au 19/12/2025, n'apparaît que dans le graphique. Sa nature temporaire (« pré-réservations temporaires » ; Bosquel prolongé jusqu'à mi-mai 2026, état actuel non vérifié selon le référentiel) figure au glossaire mais pas sur la figure. Fouju apparaît à deux étages (700 MW pré-réservés compris dans les 3,8 GW, puis contrat signé), sans que le lecteur en soit averti.
- **Correction** : ajouter au texte un paragraphe « Pré-réservée » (ou retirer l'étage). Sur la figure, mentionner « temporaire ; état en novembre 2026 non vérifié » et signaler que Fouju figure aux deux étages.

### 14. Hero : années incomplètes non signalées dans la phrase, « provisoires » mal employé, « 0 heures » — **PRÉCISION**

- **Page** : accueil, phrase « En AAAA, le prix day-ahead a été strictement négatif pendant N heures ».
- **Preuve** (recalcul sur `donnees/prix/*.json`) :
  - 2015 : 96 heures sans prix (du 1er au 4 janvier, avant le début de la série SMARD). La phrase affiche « 0 heures (calcul du site sur les données affichées, non recoupé) » sans signaler le trou.
  - 2026 : le 21 novembre manque en entier (24 h) ; la phrase dit « jusqu'au 26 novembre » sans le dire.
  - « données provisoires » : un prix day-ahead publié est définitif. L'année en cours est incomplète, pas provisoire (le mot vaut pour éCO2mix, pas pour les prix).
  - « 0 heures » : l'usage veut le singulier (« 0 heure », ou « aucune heure »).
- **Correction** : ajouter « (N heures sans prix publié) » dès qu'il manque des heures dans l'année ; remplacer « provisoires » par « incomplètes » pour les prix ; accorder au singulier pour 0 et 1.

### 15. Hero : plus de la moitié des « heures négatives » sont à quelques centimes sous zéro — **PRÉCISION**

- **Page** : accueil, chiffre principal (513 h en 2025).
- **Preuve** (CSV horaires) : heures négatives comprises entre −0,1 €/MWh et 0 : 73/147 (2023), 124/352 (2024), 279/513 (2025), 320/568 (2026). Le chiffre est juste et conforme à RTE, mais une experte attend que l'on distingue les prix planchers à −0,01 €/MWh (offres renouvelables sous obligation d'achat ou en complément de rémunération) des prix franchement négatifs. Sans cette distinction, 513 h suggère un excédent plus profond qu'il ne l'est.
- **Correction** : sous le chiffre, ou dans le tableau mensuel, ajouter la répartition (par exemple « dont 279 h entre −0,10 et 0 €/MWh »).

### 16. Infobulle « négatif, arrondi à zéro dans la source » : c'est le site qui arrondit — **PRÉCISION**

- **Page** : accueil, infobulle (`HeroPrix.svelte`, `prixTexte`) ; 7 heures en 2025, 93 en 2026.
- **Preuve** : depuis la correction consignée dans `ERREURS.md`, le CSV porte 4 décimales (par exemple −0,0025). C'est `arrondiStockage` (arrondi au centime entre −1 et 1) qui produit le marqueur −0,001. La source n'arrondit rien à zéro.
- **Correction** : « −0,00 €/MWh (négatif ; moins de 0,005 €/MWh en valeur absolue) », ou stocker ces prix avec 4 décimales.

### 17. « Sites dédiés raccordés au réseau d'Enedis » : la source ne le dit pas explicitement — **PRÉCISION**

- **Pages** : /combien, graphique des estimations 2024 ; référentiel `dc_conso_rpd_2024` (périmètre « sur sites dédiés »).
- **Preuve** : BE2025, p. 18 : « (3 TWh sur le réseau public de distribution d'Enedis en 2024) ». La parenthèse suit une phrase sur les centres « sur site dédié » raccordés au RPT, mais elle ne qualifie pas elle-même le périmètre Enedis. Le TdB, p. 26, parle de « Datacenters sur le RPD Enedis ». L'inférence est plausible, mais c'est une inférence.
- **Correction** : libellé « Data centers raccordés au réseau d'Enedis (sites dédiés, par inférence) », ou une note de périmètre.

### 18. Glossaire, PTF : l'entrée en file d'attente suppose aussi le premier acompte — **PRÉCISION**

- **Page** : /methode, glossaire : « Sa signature par le demandeur fait entrer le projet dans la file d'attente et réserve la capacité. »
- **Preuve** : délibération CRE n° 2026-32 du 4/02/2026 : « La demande de raccordement entre en file d'attente (réservation de la capacité associée à cette demande) lorsque le demandeur accepte la PTF […] et, en particulier, […] qu'il a versé le premier acompte prévu ». Le même texte rend aussi un peu rapide « il n'engage pas à consommer » sans mention d'engagement financier.
- **Correction** : « Son acceptation, avec le versement du premier acompte, fait entrer le projet dans la file d'attente et réserve la capacité. »

### 19. Méthode : la liste des sources omet les données du hero — **PRÉCISION**

- **Page** : /methode, « 13 publications, citées par les 35 chiffres du référentiel ».
- **Preuve** : la série de prix day-ahead (SMARD / energy-charts), base du hero et des recoupements cotés A, n'y figure pas, pas plus qu'éCO2mix ou ODRÉ (recoupement de la consommation brute).
- **Correction** : ajouter une section « Données » (prix day-ahead : SMARD via energy-charts, CC BY 4.0, date d'extraction, convention quart-horaire ; éCO2mix ; ODRÉ), avec renvoi à `horaire/LISEZMOI.md`.

### 20. Citation RTE générale présentée comme propre aux data centers — **FORME**

- **Page** : /combien, note 17.
- **Passage** : « RTE le dit lui-même : toutes les demandes ne deviendront pas des installations. Il observe que « certains développeurs ont parfois sécurisé un accès au réseau sur plusieurs points du territoire pour des projets en réalité similaires » ».
- **Preuve** : BP2025-C, p. 6, § 2.1.3 : le passage porte sur l'ensemble des demandes (industrie, hydrogène, centres de données), et la suite de la phrase cite l'hydrogène en exemple. La citation est exacte, mais pas propre au secteur.
- **Correction** : « À propos de l'ensemble des demandes de raccordement (industrie, hydrogène, centres de données), RTE observe que… ».

### 21. Écrêtement à 200 €/MWh : 2022 devient une nappe uniforme — **FORME**

- **Page** : accueil, années 2021, 2022 et 2026.
- **Preuve** : heures ≥ 200 €/MWh : 1 291 (2021), 5 887 en 2022 (67 % de l'année), 900 en 2026. Avec une échelle fixe, la structure horaire de 2022 disparaît. La légende le dit, ce n'est donc pas trompeur, mais c'est l'année que l'experte ira regarder.
- **Correction** : une phrase sous la carte quand plus de 10 % des heures sont écrêtées (« 67 % des heures au-delà de 200 €/MWh »), ou une option d'échelle propre à l'année.

### 22. « égal au chiffre publié par RTE » est affirmé sans être vérifié — **FORME** (fragilité)

- **Page** : accueil, note du tableau mensuel.
- **Preuve** : `HeroPrix.svelte` affiche « égal au chiffre publié par RTE » dès qu'une référence existe (`{#if reference}`), sans comparer `negatives.total` à `reference.valeur`. Les décomptes sont égaux aujourd'hui (147, 352, 513 : vérifié), mais une mise à jour des prix pourrait rendre la phrase fausse sans que rien ne le signale.
- **Correction** : `{#if reference && reference.valeur === negatives.total}`, avec sinon « RTE publie X h ; écart de Y h », et un test.

### 23. Recoupement de la consommation brute attribué au mauvais document — **FORME**

- **Page** : /combien, note 2 : « Recoupement non indépendant (RTE, Bilan électrique 2024 — rapport complet) : 440,1 TWh (somme éCO2mix, hors Corse) + 2,3 TWh (Corse, ODRÉ) ».
- **Preuve** : le recoupement vient d'éCO2mix et d'ODRÉ (calcul de `pc check`), pas du Bilan.
- **Correction** : créer une source « RTE, éCO2mix / ODRÉ » et l'attacher à ce recoupement.

### 24. Méthode : « aucun chiffre n'est tapé à la main dans une page » — **FORME**

- **Page** : /methode.
- **Preuve** : /combien contient 3,8 TWh, 15 %, 8 760 heures, 7 % et « 32 ÷ 442 », tapés dans le texte. Ce sont des calculs expliqués, comme le dit le commentaire de `combien.md`, mais la phrase de la méthode est absolue.
- **Correction** : « aucun chiffre issu d'une source n'est tapé à la main ; les calculs du site sont écrits avec leurs termes ».

### 25. Accents graves bruts dans les notes — **FORME**

- **Pages** : accueil et /combien, notes des heures négatives : « Recoupement indépendant : 513 h (recalcul de `pc check`) ».
- **Correction** : rendre le Markdown en ligne des champs `recoupements`, ou écrire « recalcul du site sur les prix SMARD / energy-charts ».

### 26. Titre du hero : « Prix de l'électricité en France » — **FORME**

- **Page** : accueil.
- **Preuve** : la série est le prix de gros day-ahead de la zone France. Une experte lit « prix de l'électricité » comme un prix de détail. Le sous-titre corrige, mais le titre est ce qui sera repris.
- **Correction** : « Prix de gros day-ahead en France, heure par heure, 2025 ».

### 27. « Aujourd'hui » pour des chiffres de 2024 — **FORME**

- **Page** : /combien, intertitre « Aujourd'hui : de l'ordre de 1 % de la consommation ».
- **Preuve** : la page est datée du 26/11/2026 et le chiffre porte sur 2024 (seul le RPT est connu pour 2025).
- **Correction** : « En 2024 : de l'ordre de 1 % de la consommation ».

---

## Vérifié et juste (pour ne pas y revenir)

- 4 à 5 TWh ÷ 442 TWh ≈ 1 % ; 0,8 + 3 = 3,8 TWh ; 1 TWh ÷ 8 760 h ≈ 114 MW (majorant, dit comme tel) ; 1 TWh ÷ (770 MW × 8 760 h) ≈ 14,8 %.
- Citations BE2025 p. 18-19, BP2025-C p. 6, 27 et 28, TdB p. 25, communiqué DGE (28,6 GW « recherchée », 52 entreprises, 63 sites) : conformes.
- BP2023 15-20 / 23-28 TWh et leur attribution erronée par la page RTE : conforme (BP2023-C p. 43 ; page web, lignes « entre 15 et 20 TWh en 2030 »).
- Heures négatives : le décompte du site sur les JSON publiés donne 147 (2023), 352 (2024) et 513 (2025), égal à RTE ; la somme mensuelle de 2025 fait 513.
- Changements d'heure : jour de 23 h (case 2 h inexistante) et jour de 25 h (case 2 h doublée, deux prix présents chaque année de 2015 à 2026) traités correctement ; années civiles en heure de Paris.
- Pas de 15 min : moyenne simple des quarts d'heure, conforme à la note 10 du BE2025 ; dite sur la page.
- Échelle de couleurs : seuils et graduations bien placés (−20, −5, 0, 25, 50, 100, 200 aux frontières des classes) ; écrêtement annoncé.
- Axes : estimations 2024 en linéaire depuis 0 ; trajectoires sur un axe des années linéaire (6 ans entre 2024 et 2030, 5 ans entre 2030 et 2035, espacements proportionnels) ; pyramide en log avec décades étiquetées et mise en garde « pas un entonnoir ».
- Glossaire : RPT (HTB > 50 kV) ; RPD (HTA/BT ≤ 50 kV, Enedis et ELD) ; fast-track (CRE, délibération 2025-120 du 7/05/2025, HTB3 400 kV, sites identifiés par l'État : conforme) ; MW/MWh et facteur 0,5 ; facteur moyen ≠ marginal : justes.
- `taux_co2` n'est pas affiché sur ces pages ; le LISEZMOI le qualifie correctement d'intensité moyenne de la production.

## Verdict

**Publiable après corrections FOND** (points 1 à 5). Les points 1, 2 et 3 sont exactement le type d'erreur que la lectrice cible traque : une capacité présentée comme contractualisée alors qu'elle ne l'est pas, l'assiette d'une hypothèse tronquée, et une affirmation fausse sur ce que dit la page source. Les points 4 et 5 se voient sans ouvrir aucune source. Les points PRÉCISION 6, 7, 8, 10 et 14 devraient être traités dans la même passe : chacun ferait lever un sourcil à une experte, sans être faux à proprement parler.

Décompte : 5 FOND, 14 PRÉCISION, 8 FORME (27 points).

---

## Suites (Claude, 2026-11-26)

Les 27 points sont traités : texte et référentiel corrigés par Claude
(1, 2, 3, 5 à 11, 13, 17, 20, 23, 25, 27), rendu corrigé par l'agent du
site (1, 3, 4, 7, 12 à 16, 18, 19, 21, 22, 24, 26). Les points 3 et 5
ont été revérifiés dans les PDF avant correction. Le point 15 compte
désormais les prix planchers de −0,10 €/MWh (inclus) à 0 € (exclu), d'où
285 h en 2025 au lieu des 279 h de ce rapport, qui excluait la borne.
Erreurs consignées dans `making-of/ERREURS.md`.
