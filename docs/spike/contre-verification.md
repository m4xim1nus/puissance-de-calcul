# Contre-vérification des affirmations clés (relecture adverse)

Date : 26/11/2026. Méthode : retour au document primaire pour chaque affirmation, citation exacte avec page du PDF (la page du PDF coïncide avec la page imprimée dans tous les documents cités), recalcul indépendant sur les échantillons de `data/raw/spike/systeme/`. Scripts et PDF téléchargés dans le scratchpad de session (non versionnés).

Documents ouverts pour cette vérification :

- RTE, *Bilan électrique 2025*, rapport complet (BE2025) : https://assets.rte-france.com/analyse-et-donnees/2026-03/BE2025%20-%20Rapport%20Complet.pdf
- RTE, *Bilan électrique 2024*, rapport complet (BE2024) : https://assets.rte-france.com/analyse-et-donnees/2025-09/BE2024%20-%20Rapport%20Complet.pdf
- RTE, *Bilan prévisionnel 2025-2035*, chapitre Consommation (BP2025-C) : https://assets.rte-france.com/prod/public/2025-12/2025-12-23-bilan-previsionnel-2025-consommation.pdf
- RTE, *Bilan prévisionnel 2025*, Principaux résultats (BP2025-PR) : https://assets.rte-france.com/prod/public/2025-12/2025-12-16-bilan-previsionnel-principaux-resultats-2025.pdf
- RTE, *Bilan prévisionnel 2023*, chapitre 2 Consommation (BP2023-C) : https://assets.rte-france.com/prod/public/2023-11/Bilan-previsionnel-2023-chapitre2-consommation.pdf
- RTE, *Tableau de bord de suivi de l'électrification* (TdB), archivé dans `data/raw/spike/datacenters/tdb_electrif.pdf`
- RTE, page « Les data centers en chiffres clés », version actuelle et versions Wayback Machine du 30/10/2025, du 06/03/2026, du 03/06/2026 et du 17/09/2026
- RTE Services, actualités du 20/05/2025 et du 19/12/2025 ; fiche fast-track et communiqué Campus IA archivés dans `data/raw/spike/datacenters/docs/`
- RTE, *éCO2mix – Spécifications des fichiers en puissance* (2025-06) ; page RTE « éCO2 emissions » ; métadonnées ODRÉ des jeux `eco2mix-national-cons-def`, `eco2mix-national-tr` et `production-nette-nucleaire` ; ODRÉ `prod-region-annuelle-filiere` (Corse)

## Synthèse

| | Affirmation | Verdict |
|---|---|---|
| A | Sites dédiés : 4 à 5 TWh en 2024 | **CONFIRMÉ** |
| B | RPT : ≈ 1 TWh (2025), ≈ 0,8 TWh (2024), 770 MW, 22 % | **CONFIRMÉ** pour la citation, **À NUANCER** pour le 22 % (non reconstituable) |
| C | 0,63 GW mis à disposition ; 0,035 GW utilisés au maximum | **CONFIRMÉ** pour la citation, **À NUANCER** pour la comparaison (cohortes et grandeurs différentes) |
| D | ~14 GW (nov. 2025) ; ~18 GW / ~80 projets (mai 2026) | **CONFIRMÉ**, mais la combinaison « 18 GW dont 7 GW avant 2030 » est **FAUSSE** |
| E | BP2025 = 10-15 / 21-32 TWh ; page web = 15-20 / 23-28 | **CONFIRMÉ**, contradiction expliquée : la page RTE recycle les chiffres du **BP2023** |
| F | 5 sites fast-track, 3,8 GW pré-réservés ; Fouju 240 → 700 → 1 400 MW | **CONFIRMÉ** (photographie de décembre 2025 ; puissances de raccordement, pas de mise en service) |
| G | Heures à prix négatif : 147 / 352 (ex-361) / 513 | **CONFIRMÉ**, et la révision 361 → 352 est expliquée par RTE |
| H | éCO2mix 2024 = 440,086 TWh ; écart au Bilan = Corse | **CONFIRMÉ** |
| I | Horodatage éCO2mix = fin de la demi-heure | **CONFIRMÉ empiriquement** (deux tests, dont un indépendant d'ODRÉ) ; **non documenté** par RTE ni ODRÉ |
| J | `taux_co2` 20,1 contre 21,7 g/kWh ; écart dû à la Corse | **À NUANCER** : la Corse explique environ 3/4 de l'écart en 2024 et environ 9/10 en 2025, pas la totalité |

---

## A. Data centers sur sites dédiés : 4 à 5 TWh en 2024

**Verdict : CONFIRMÉ.**

Citation, BP2025-C, p. 27, § 2.5.2 :

> « Jusqu'à présent, la consommation du secteur semble encore globalement modeste : inférieur à 1 TWh en 2024 pour les seuls centres de données raccordés au réseau de transport ou de l'ordre de 4 à 5 TWh pour l'ensemble des centres de données sur sites dédiés (et entre 5 et 10 TWh en incluant les centres de données internes). »

Périmètre, même page : les centres « sur sites dédiés » s'opposent aux centres « internes, c'est-à-dire appartenant aux locaux mêmes de l'entreprise ou de l'administration qui en a l'usage ». La note 14 précise que le BP2023 englobait les deux catégories, ce qui est essentiel pour E. Le périmètre couvre le RPT et le RPD : « les projections englobent aussi les consommations des centres de données sur sites dédiés raccordés au réseau de distribution » (p. 27).

Corroboration par le même émetteur : BP2025-PR, p. 25, fig. 16, ligne « Datacenter », colonne 2024 : « ~5 TWh ».

Remarque de lecture : grammaticalement, « en 2024 » n'est rattaché qu'à la proposition sur le RPT, mais la construction parallèle et le « ~5 TWh » du BP2025-PR (colonne 2024) lèvent l'ambiguïté.

**Formulation recommandée :** « En 2024, les data centers sur sites dédiés (hors salles informatiques internes aux entreprises) ont consommé de l'ordre de 4 à 5 TWh, dont moins de 1 TWh pour ceux raccordés au réseau de transport (RTE, Bilan prévisionnel 2025, chap. Consommation, p. 27). En incluant les centres internes, RTE estime ce total entre 5 et 10 TWh. »

---

## B. RPT : ≈ 1 TWh en 2025, ≈ 0,8 TWh en 2024, 770 MW, 22 %

**Verdict : CONFIRMÉ pour la citation ; À NUANCER pour l'usage du 22 %.**

Citations, BE2025, p. 18 :

> « La consommation électrique des centres de données "sur site dédié" raccordés au réseau public de transport d'électricité est aujourd'hui relativement faible au regard de la consommation totale française : elle a atteint près de 1 TWh en 2025 et environ 0,8 TWh en 2024 (3 TWh sur le réseau public de distribution d'Enedis en 2024). »

BE2025, p. 18-19 :

> « Aujourd'hui, les puissances de raccordement de ces structures varient entre 40 à 240 MW pour un total de 770 MW à fin décembre 2025. »

> « Le taux moyen d'utilisation de la puissance de raccordement pour les installations raccordées au réseau public de transport s'élève ainsi aujourd'hui à 22 %. »

Remarques :

- Le chiffre Enedis porte sur 2024 seulement. La note 30 dit : « Au moment de la rédaction de ce chapitre, les chiffres 2025 n'étaient pas encore disponibles. »
- La note 29 cite le SDES : « environ 4 à 6 TWh en 2023 » pour la « consommation totale des centres de données en France ». C'est un autre périmètre et une autre année que A.

**Sens du 22 %.** Le BE2025 ne le définit pas. La définition se trouve dans le BP2025-C, p. 28, note 15 :

> « Le taux moyen d'utilisation de la puissance de raccordement prend en compte pour les centres de données à la fois la différence entre puissance consommée et puissance de raccordement en régime nominal, et le stade d'avancement de chaque site dans sa montée en charge […] »

Dans le BP, ce taux sert de **facteur de charge rapporté à la puissance de raccordement**, c'est-à-dire puissance moyenne appelée divisée par puissance de raccordement. Il ne s'agit pas d'un rapport de pointes. On le vérifie en refaisant le calcul du BP2025-PR, p. 25 :

- trajectoire rapide : 4,3 GW × 20 % × 8 760 h ≈ 7,5 TWh, plus 2,4 TWh sur le RPD (BP2025-C, p. 28), soit ≈ 10 TWh, le « +10 TWh » affiché ;
- trajectoire lente : 2,4 GW × 20 % × 8 760 h ≈ 4,2 TWh, plus 1,8 TWh, soit ≈ 6 TWh, le « +6 TWh » affiché.

**Problème non résolu :** avec cette définition, on ne retrouve pas 22 % à partir des chiffres du BE2025. 1 TWh / 8 760 h ≈ 114 MW, soit ≈ 15 % de 770 MW. Pour obtenir 22 % sur 770 MW, il faudrait ≈ 1,5 TWh. Le 22 % est donc probablement calculé sur une autre base, que RTE ne donne pas (puissance raccordée moyenne de l'année plutôt que celle de fin d'année, ou sous-ensemble de sites).

**Formulation recommandée :** « Les data centers raccordés au réseau de transport ont consommé près de 1 TWh en 2025 (≈ 0,8 TWh en 2024), pour 770 MW de puissance de raccordement fin 2025. Cela fait environ 114 MW appelés en moyenne. RTE indique un "taux moyen d'utilisation de la puissance de raccordement" de 22 % (BE2025, p. 19), sans en préciser le calcul. Le rapport simple de l'énergie annuelle à la puissance de fin d'année donne plutôt ≈ 15 %. » Ne pas présenter 22 % comme un taux de pointe.

---

## C. 0,63 GW mis à disposition ; 0,035 GW utilisés au maximum en 2024

**Verdict : CONFIRMÉ pour la citation ; À NUANCER, voire à proscrire, pour la comparaison 0,035 / 0,63.**

Citation, TdB, p. 25, encadré « Datacenters sur le RPT » :

> « 0,63 GW de puissance de raccordement mise à disposition entre 2022 et 2025 »
> « 14 GW de puissance contractualisée fin 2025 dont ~7 GW pour mise en service d'ici 2030 »
> « 0,035 GW utilisés au maximum en 2024 (datacenters raccordés entre 2022 et 2024) »

Note du graphique : « Les données de raccordement concernent uniquement le RPT et représentent la situation au 15 novembre 2025. » Encadré d'analyse : « La consommation des projets raccordés au RPT depuis 2022 reste aujourd'hui bien inférieure à la puissance totale mise à disposition. »

**Ce que mesure « utilisés au maximum ».** Aucune note ni le lexique (p. 41) ne le définit. La lecture la plus probable est la **puissance maximale appelée en 2024** (une pointe en MW) par la cohorte raccordée en 2022-2024. On ne sait pas s'il s'agit de la pointe simultanée de la cohorte ou de la somme des pointes individuelles. Ce n'est en tout cas **pas** une consommation moyenne, ni une énergie.

**La comparaison 0,035 / 0,63 (≈ 6 %) n'est pas loyale :**

1. **Cohortes différentes.** Le numérateur couvre les sites raccordés en 2022-2024, le dénominateur ceux de 2022-2025. Les mises à disposition de 2025 (inconnues, peut-être la majorité) gonflent le dénominateur alors qu'elles n'ont rien pu consommer en 2024.
2. **Années différentes.** Le numérateur est mesuré en 2024. Le dénominateur est un cumul au 15/11/2025.
3. **Montée en charge.** Un site raccordé fin 2024 compte entier dans la cohorte mais n'a pratiquement pas consommé en 2024.
4. **Grandeurs.** Le numérateur est une pointe appelée, le dénominateur une capacité de raccordement. Le ratio n'est comparable ni au 22 % du BE2025, ni au 20 % du BP2025-PR (p. 23), qui sont des rapports moyens.

RTE ne calcule ce ratio nulle part.

**Incohérence interne de la page.** Mesurée au pixel, la barre « Raccordés depuis 2022 » du graphique vaut ≈ 0,76 GW, alors que l'encadré dit 0,63 GW. Pour mémoire, le BE2025 donne 770 MW pour **l'ensemble** des data centers sur le RPT, toutes années de raccordement confondues. Le graphique est en cascade : raccordés ≈ 0,76 GW, en travaux ≈ 0,95 GW, signés 2025-2029 ≈ 5,0 GW, sommet ≈ 6,85 GW. Les « ~7 GW pour mise en service d'ici 2030 » **incluent donc les sites déjà raccordés**.

**Fiabilité éditoriale.** Le PDF a été créé le 22/05/2026, alors que l'URL porte 2026-07. Il contient un commentaire interne oublié, « Voir avec TV ? » (p. 38). C'est un diaporama peu relu : à citer en second rang, derrière le BE2025.

Coïncidence à signaler sans conclure : dans l'échantillon ODRÉ « soutirages RPT, section NAF J », la pointe 2024 (90 + 225 kV) vaut 35,3 MW. Mais l'énergie de ce périmètre (177 GWh en 2024) est bien inférieure aux 0,8 TWh des data centers RPT. Ce n'est donc pas le même périmètre.

**Formulation recommandée :** « Les data centers raccordés au réseau de transport entre 2022 et 2024 ont appelé au plus 35 MW en 2024 (RTE, tableau de bord de l'électrification, p. 25). Sur l'ensemble 2022-2025, RTE leur a mis à disposition 630 MW de raccordement. » Ne pas écrire « 5,6 % », ni « 35 MW utilisés sur 630 MW ». Si l'on veut un ratio, utiliser celui que publie RTE (22 %, BE2025) avec la réserve de B.

---

## D. File RTE : ~14 GW (novembre 2025) et ~18 GW, ~80 projets (mai 2026)

**Verdict : CONFIRMÉ pour chaque chiffre. FAUX si on les combine comme dans `datacenters.md` (« environ 18 GW réservés (mai 2026), dont environ 7 GW visent une mise en service avant 2030 »).**

Citations :

- BP2025-PR, p. 21 : « au 1er novembre 2025, les projets de nouveaux sites de consommation ou d'augmentation de puissance de sites existants ayant contractualisé un accès au réseau de transport d'électricité représentent une puissance cumulée de l'ordre de 30 GW (environ 14 GW pour des centres de données, y compris ceux s'inscrivant dans une procédure fast track […]) ».
- BE2025, p. 120 : « Ils atteignaient au premier novembre 2025 environ 30 GW, dont 14 GW de datacenters ». La figure 6.13 est pourtant légendée « situation à fin novembre 2025 ».
- TdB, p. 25 : « 14 GW de puissance contractualisée fin 2025 dont ~7 GW pour mise en service d'ici 2030 », avec un graphique « au 15 novembre 2025 ».
- Page RTE « Les data centers en chiffres clés » (publiée le 21/05/2025, date affichée 01/06/2026 ; texte identique dans les captures Wayback du 03/06 et du 17/09/2026) : « En mai 2026, RTE avait réservé près de 18 GW de capacité, pour environ 80 projets. Fin 2024, il y avait une quarantaine de projets totalisant environ 5 GW. » L'intertitre dit « Près de 18 GW de demandes de raccordement signées ».

Périmètre. Le BP2025-C (p. 27) définit l'engagement de raccordement comme le « périmètre des projets de centres de données dont la proposition technique et financière est signée » : parler de PTF est donc correct. Sur la fig. 6.13 du BE2025, le cadre « ~30 GW » couvre les colonnes « En phase travaux », « Signé pour mise en service 2025-2029 », « Signé pour mise en service à partir de 2030 » et « Suspendu ». Les sites déjà raccordés sont exclus, les projets suspendus inclus.

Le même chiffre de 14 GW est daté de trois façons selon le document : 01/11, 15/11 ou fin novembre 2025. Le « ~7 GW d'ici 2030 » se rapporte aux 14 GW de novembre 2025, pas aux 18 GW de mai 2026, et inclut le déjà-raccordé (voir C).

**Formulation recommandée :** « Fin 2025, environ 14 GW de raccordements data centers étaient contractualisés auprès de RTE (PTF signées, au 1er novembre 2025), dont environ 7 GW, y compris les sites déjà raccordés, visant une mise en service avant 2030. En mai 2026, la file atteignait près de 18 GW pour environ 80 projets (RTE). Ce sont des droits d'accès au réseau, pas des consommations. »

---

## E. Trajectoires : BP2025 (10-15 / 21-32 TWh) contre page web RTE (15-20 / 23-28 TWh)

**Verdict : CONFIRMÉ. La contradiction est réelle et s'explique : la page web RTE attribue au BP2025 des chiffres qui viennent du BP2023, établis sur un périmètre plus large.**

Document BP2025-C, p. 28 :

> « Le niveau de demande des centres de données sur sites dédiés atteint finalement près de 32 TWh en 2035 dans la trajectoire de décarbonation rapide contre 21 TWh dans la trajectoire de décarbonation lente. »

La figure 2.10, « Consommation d'électricité des centres de données sur sites dédiés », affiche 10 et 15 TWh en 2030, 21 et 32 TWh en 2035. Le BP2025-PR (p. 25) le confirme : base ~5 TWh, puis +6 TWh (lente) et +10 TWh (rapide) en 2030.

Page web actuelle : « Selon notre Bilan prévisionnel 2025-2035, dans une trajectoire de décarbonation rapide, […] entre 15 et 20 TWh en 2030 […], puis entre 23 et 28 TWh en 2035 ».

**Source réelle de ces chiffres.** BP2023-C, p. 43 :

> « La consommation des data centers estimée autour de 10 TWh au début de la décennie 2020 pourrait ainsi atteindre 15 à 20 TWh en 2030, et entre 23 et 28 TWh en 2035 ».

La version antérieure de la page RTE le disait explicitement. Wayback du 30/10/2025 et du 06/03/2026 : « Le Bilan prévisionnel de RTE publié en 2023 table sur un triplement de la consommation d'électricité des data centers d'ici à 2035. Elle pourrait atteindre 23 à 28 TWh ». La refonte de mai-juin 2026 a remplacé « publié en 2023 » par « 2025-2035 […] décarbonation rapide » sans changer les chiffres. Le périmètre du BP2023 inclut les centres internes (BP2025-C, p. 27, note 14 : « Dans le Bilan prévisionnel 2023, RTE englobait dans le secteur des centres de données à la fois les centres de données internes et les centres de données sur sites dédiés »). Le « 10 TWh » actuel de la page vient de la même base.

Il ne s'agit donc ni d'un incrément, ni d'une variante du BP2025. Ce sont des chiffres périmés, publiés sous une étiquette erronée. La presse les reprend avec cette mauvaise attribution, notamment IT for Business le 09/11/2026.

**Formulation recommandée :** « RTE (Bilan prévisionnel 2025) projette pour les data centers sur sites dédiés 10 à 15 TWh en 2030 et 21 à 32 TWh en 2035 selon la trajectoire. Les chiffres de 15-20 et 23-28 TWh, souvent cités, viennent du Bilan prévisionnel 2023, sur un périmètre incluant les salles informatiques internes. La page grand public de RTE les attribue à tort au BP2025. »

---

## F. Sites fast-track et Campus IA (Fouju)

**Verdict : CONFIRMÉ, à présenter comme une photographie de décembre 2025, en puissance de raccordement et non de consommation.**

- RTE Services, 20/05/2025 : « 700 MW of capacity at the Parc des Soufflantes site (Escaudain […]) », « 700 MW […] ZAC des Bordes site (Fouju […]) », « 700 MW […] former EDF power station Montereau site (Vernou-la-Celle-sur-Seine […]) », « 1 GW of capacity at the ZAC du Bosquel site ».
- RTE Services, 19/12/2025 : « the French State has asked RTE to pre-reserve 700 MW of capacity at the "Grande Industrie" area of the "Grand Port Maritime de Dunkerque" ». Pour Bosquel : « extension of the A GW capacity pre-booking » (sic, coquille pour 1 GW) ; « This pre-booking, which initially was supposed to end on 16 february 2026, is thus extended for three more months. »
- Fiche RTE de décembre 2025 (archivée), p. 1 : « Quatre sites "fast-track" ont été officialisés lors de "Choose France" en mai 2025 : Fouju (77), Montereau (77), Escaudain (59) et Le Bosquel (80). Un cinquième site a été validé par l'Etat en décembre 2025 dans la zone du Grand Port Maritime de Dunkerque (59). » La fiche ne donne pas de MW.

Total : 4 × 700 + 1 000 = **3,8 GW**, calcul exact au 19/12/2025. Deux réserves :

1. Ce sont des **pré-réservations temporaires**. Celle de Bosquel courait jusqu'au 16/02/2026 + 3 mois, soit mi-mai 2026. Leur état en novembre 2026 n'a pas été vérifié.
2. Le contrat Fouju va **au-delà** de la pré-réservation de 700 MW.

Communiqué RTE / Campus IA, La Défense, 26/01/2026 :

> « L'accord prévoit la mise à disposition par RTE d'un premier palier de puissance de 240 MW d'ici fin 2027, suivi d'un second palier de 700 MW avant fin 2029. Les infrastructures électriques seront conçues de manière à permettre, à terme, une montée en puissance jusqu'à 1 400 MW ».

C'est la « première mise en œuvre de la procédure de raccordement accélérée dite "Fast track" ». Il s'agit de paliers de **puissance de raccordement mise à disposition**. Ce ne sont pas des dates de mise en service du data center ni des consommations.

**Formulation recommandée :** « Cinq sites "fast-track" labellisés (Fouju, Montereau, Escaudain, Le Bosquel, Dunkerque), avec 3,8 GW de capacité pré-réservée à la demande de l'État en décembre 2025. Premier contrat signé : Campus IA à Fouju (26/01/2026), avec une puissance de raccordement de 240 MW mise à disposition fin 2027, puis 700 MW fin 2029, extensible à 1 400 MW. »

---

## G. Heures à prix day-ahead négatif : 147 (2023), 352 (2024, ex-361), 513 (2025)

**Verdict : CONFIRMÉ, révision expliquée.**

- BE2024, p. 55 : « Le nombre d'occurrences de prix spot négatifs a très fortement augmenté en 2024, avec 361 heures au cours de l'année (soit 4 % du temps). Il s'agit du double des occurrences de l'année précédente (147 heures) ». Même chose p. 44 et p. 142.
- BE2025, p. 68 : « Le prix spot horaire a été négatif pendant 513 heures en 2025, un nombre d'occurrences plus élevé que l'année précédente (352 en 2024) ». Note 10 : « Après le passage au pas 15 minutes, une heure est considérée à prix négatif si la moyenne des prix au cours de l'heure est négative ».
- **Explication de la révision**, BE2025, p. 64, sous la fig. 3.11, qui affiche 147, 352 et 513 : « Le nombre de prix négatifs de l'année 2024 est dépendant de la source de données, un incident technique ayant causé le découplage d'EPEX spot pendant quelques heures le 26 juin. La valeur affichée ici pour l'année 2024 considère les données Nord Pool pendant cet incident. »

Recalcul sur l'échantillon energy-charts (`ec_price_FR_{2023,2024,2025}.json`, source SMARD, CC BY 4.0). Méthode : année civile en heure de Paris ; en 2025, moyenne des quarts d'heure après le passage au pas 15 min.

| Année | Points | Heures | < 0 | ≤ 0 |
|---|---|---|---|---|
| 2023 | 8 760 (horaire) | 8 760 | **147** | 184 |
| 2024 | 8 784 (horaire) | 8 784 | **352** | 549 |
| 2025 | 15 387 (horaire puis 15 min) | 8 760 | **513** | 732 |

Le 26/06/2024, l'échantillon ne contient aucune heure négative : il suit bien le prix couplé, cohérent avec 352.

**Formulation recommandée :** « 147 h en 2023, 352 h en 2024 et 513 h en 2025 à prix day-ahead négatif en France (RTE, Bilan électrique 2025). Le chiffre de 361 h publié pour 2024 dans le Bilan 2024 a été révisé, à cause d'un découplage d'EPEX le 26 juin 2024. » Ajouter « prix strictement négatif » : les heures à prix nul (197 en 2024) ne sont pas comptées.

---

## H. Consommation éCO2mix 2024 = 440,086 TWh contre 442,2 TWh au Bilan ; écart = Corse

**Verdict : CONFIRMÉ.**

Recalcul sur `eco2mix_national_cons_def_all.parquet`, nature « Données définitives », lignes avec `consommation` renseignée, Σ MW × 0,5 h :

| | 2024 | 2025 |
|---|---|---|
| Année civile selon la colonne `date` (heure de Paris), 17 568 / 17 520 demi-heures | **440,086 TWh** | 443,879 TWh |
| Après dédoublonnage sur `date_heure` UTC (artefact du changement d'heure de mars) | 440,039 TWh | 443,831 TWh |
| ODRÉ `consommation-annuelle-brute`, France | 442,336 TWh | 446,146 TWh |
| ODRÉ régional, Corse | 2,256 TWh | 2,266 TWh |
| ODRÉ régional, Σ des 12 régions continentales | 440,079 TWh | 443,881 TWh |

L'écart résiduel est de +7 GWh en 2024. Il est du même ordre que l'artefact du changement d'heure : environ +47 GWh pour l'heure de mars dupliquée, et une heure manquante en octobre.

Le BE2024, p. 12, dit : « La consommation brute d'électricité de l'année 2024 s'est élevée à 442,2 TWh ». Le glossaire, p. 157 : « Consommation brute : Consommation d'électricité au périmètre France (Corse comprise) incluant les pertes sur le réseau […] mais excluant la consommation pour le pompage. » Le BE2025, p. 12, ajoute : « Le périmètre géographique considéré dans le Bilan électrique est la France métropolitaine (Corse incluse). »

**Formulation recommandée :** « éCO2mix couvre la France continentale, hors Corse : 440,1 TWh en 2024, contre 442,2 TWh au Bilan électrique, qui inclut la Corse (2,3 TWh). »

---

## I. Horodatage éCO2mix (cons-def) = fin de la demi-heure

**Verdict : CONFIRMÉ empiriquement ; INVÉRIFIABLE documentairement.**

**Documentation.** Aucune source ne tranche :

- spécification RTE (p. 3 et suivantes) : « Point horaire par pas de 15 minutes » et « Les données consolidées et définitives […] sont fournies au pas demi-heure », sans préciser si le point marque le début ou la fin ;
- métadonnées ODRÉ de `eco2mix-national-cons-def` et `-tr` : rien ;
- page RTE « éCO2 emissions » : rien ;
- seul `production-nette-nucleaire` le déclare : « la convention débutante est appliquée ».

À noter : la spécification qualifie le temps réel de « données de puissance instantanée ». La convention du flux `tr` n'est donc **pas** garantie identique à celle du cons-def. Elle n'a pas été testée ici.

**Test 1, refait** : moyenne horaire éCO2mix 2024 comparée à `production-nette-nucleaire` (convention débutante).

- hypothèse « fin », où l'heure [h, h+1) est la moyenne des points h:30 et h+1:00 : écart absolu moyen **0,2 MW** sur 8 781 h ;
- hypothèse « début », où l'heure [h, h+1) est la moyenne des points h:00 et h:30 : **258 MW**.

L'égalité quasi parfaite indique en outre que chaque point est une **moyenne sur la demi-heure qui se termine à l'horodatage**, et non une valeur instantanée.

**Test 2, indépendant d'ODRÉ** : energy-charts FR 2024 (données ENTSO-E, horodatage en début d'heure), balayage du décalage. Le point t est affecté à l'heure trunc(t − d).

| d | MAE solaire | MAE nucléaire | MAE conso/load | corr. Δ solaire | corr. Δ conso |
|---|---|---|---|---|---|
| −30 min | 675 MW | 494 | 1 895 | 0,865 | 0,714 |
| 0 (« début ») | 444 | 334 | 1 430 | 0,955 | 0,868 |
| **+30 min (« fin »)** | **357** | **242** | **1 271** | **0,964** | **0,911** |
| +60 min | 612 | 400 | 1 516 | 0,894 | 0,776 |

L'optimum est à +30 min pour les trois séries. Les MAE restent non nulles parce que les niveaux ENTSO-E diffèrent : sur le load, −2,4 % sur l'année.

**Test 3, centroïde solaire de juin 2024** : 12:05 UTC sur les horodatages éCO2mix, contre 11:51 UTC chez energy-charts. Le décalage d'environ 15 min correspond à une demi-heure horodatée à sa fin.

**Formulation recommandée (méthodologie du site) :** « Les valeurs éCO2mix consolidées et définitives sont des puissances moyennes par demi-heure, horodatées en fin de période. RTE ne le documente pas : nous l'avons établi par comparaison avec deux séries horodatées en début de période (ODRÉ nucléaire horaire, ENTSO-E). »

---

## J. Intensité carbone : `taux_co2` 20,1 g/kWh contre 21,7 gCO2eq/kWh ; l'écart vient-il de la Corse ?

**Verdict : À NUANCER. La Corse est la cause principale, mais pas unique : environ 3/4 de l'écart en 2024, environ 9/10 en 2025.**

**Valeurs RTE :**

- BE2024, p. 90 : « elle a atteint 21,7 gCO2eq par kilowatt-heure produit sur l'année 2024 » ;
- BE2024, p. 94 : « les émissions directes totales liées à la production d'électricité nationale se sont élevées à 11,7 MtCO2eq » ;
- BE2025, p. 104 : « l'intensité carbone de la production française a été de 19,6 gCO2éq/kWh » ;
- périmètre des deux Bilans : Corse incluse (voir H).

**Méthode éCO2mix** (page RTE « éCO2 emissions ») : émissions **directes**, en **CO2 équivalent**, égales à la production en MWh multipliée par un facteur combinant le facteur primaire du combustible (« gas, coal, fuel oil, household waste », Base Carbone ADEME) et un rendement moyen par filière (hypothèses RTE, lignes directrices ENTSO-E). Les échanges sont exclus. Les valeurs numériques ne sont pas publiées. L'hypothèse de `systeme.md` (« CO2 seul dans éCO2mix ») est donc infirmée : RTE parle de CO2eq dans les deux cas.

**Recalcul, 2024** (moyenne pondérée par la production = Σ émissions / Σ production) :

- éCO2mix : 20,10 g/kWh × 537,66 TWh = **10,81 Mt** ;
- Corse, ODRÉ `prod-region-annuelle-filiere` : production thermique 0,882 TWh, au fioul, l'île n'étant pas desservie en gaz. Au facteur fioul du Bilan (769 g/kWh, BE2024 p. 159), cela donne ≈ **0,68 Mt**. Production totale Corse : 1,636 TWh ;
- éCO2mix + Corse : 11,49 Mt / 539,30 TWh = **21,3 g/kWh** contre 21,7. La production reconstituée (539,30 TWh) égale celle d'ODRÉ `prod-national-annuel-filiere` (539,3), ce qui confirme qu'éCO2mix exclut la Corse côté production aussi ;
- part de l'écart expliquée par la Corse : (21,3 − 20,1) / (21,7 − 20,1) ≈ **75 %**.

**Même calcul, 2025** : 18,36 × 545,85 = 10,02 Mt. La Corse ajoute 0,825 TWh thermique, soit ≈ 0,63 Mt. On obtient 10,65 Mt / 547,44 TWh = **19,46** contre **19,6** (BE2025), soit ≈ 90 % de l'écart expliqué. La production BE2025 est de 547,5 TWh (p. 12).

**Le reste vient vraisemblablement des facteurs d'émission.** Une régression sans constante des émissions éCO2mix par demi-heure sur les sous-filières (R² = 0,9994) donne des facteurs implicites d'environ 350 g/kWh pour les CCG (331 au Bilan), 365 pour la cogénération gaz (**461** au Bilan), 990 pour le charbon (855), 760-780 pour le fioul (769) et 510 g/kWh appliqués à **toute** la filière déchets (le Bilan applique 988 g/kWh à la seule part non renouvelable, dont la proportion n'est pas publiée). Les écarts jouent dans les deux sens. Avec une part non renouvelable des déchets d'environ 2/3 (cohérente avec « environ un quart du volume d'émissions provient […] déchets non-renouvelables », BE2024 p. 94), on referme l'écart. Cette dernière étape repose sur une hypothèse : elle reste indicative.

**Formulation recommandée :** « Intensité carbone moyenne de la production : 21,7 gCO2eq/kWh en 2024 et 19,6 en 2025 (Bilans électriques RTE, émissions directes, Corse incluse). Le `taux_co2` d'éCO2mix, que nous utilisons pour le profil horaire, couvre la seule France continentale et donne en moyenne annuelle 6 à 7 % de moins. Les trois quarts environ de l'écart s'expliquent par la production au fioul de la Corse, le reste par des facteurs d'émission différents. C'est un facteur **moyen** de la production, ni marginal, ni de consommation. »

---

## Corrections à reporter dans les rapports de spike

1. `datacenters.md`, « Lecture » après le tableau des puissances : ne pas écrire « environ 18 GW réservés (mai 2026), dont environ 7 GW visent une mise en service avant 2030 ». Les 7 GW se rapportent aux 14 GW de novembre 2025 et incluent le déjà-raccordé.
2. `datacenters.md`, tableau de synthèse, ligne 3 : supprimer le rapprochement 0,035 / 0,63 et décrire 0,035 GW comme une **pointe** 2024 de la cohorte 2022-2024.
3. `datacenters.md`, § trajectoires : remplacer l'« hypothèse non vérifiée » par l'explication documentée (BP2023-C p. 43 et versions Wayback de la page RTE).
4. `datacenters.md` : la définition du « taux moyen d'utilisation » est dans BP2025-C p. 28, note 15. C'est un rapport moyen, pas une pointe. Garder l'écart 15 % / 22 % comme non résolu.
5. `systeme.md`, piège 8 et § « Intensité carbone » : `taux_co2` est en CO2eq (direct), pas en « CO2 seul ». L'hypothèse Corse est désormais chiffrée à environ 75 % (2024) et 90 % (2025) de l'écart.
6. `systeme.md`, § 6a : la révision 361 → 352 est expliquée (découplage EPEX du 26/06/2024, BE2025 p. 64).
7. `systeme.md`, piège 1 : préciser que la convention « fin de période » est établie pour le cons-def seulement. Le flux temps réel, décrit comme « puissance instantanée » par la spécification, reste à tester.
