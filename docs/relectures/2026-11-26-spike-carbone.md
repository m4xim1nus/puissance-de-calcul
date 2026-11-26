# Relecture adverse « lectrice experte » : spike carbone

Relecture du 26/11/2026 (agent Opus) de `docs/spike/carbone.md` et des prototypes
`pipeline/explo/spike_carbone*.py`. Aucun autre fichier du dépôt modifié, rien commité. Les
recalculs sont faits avec du code écrit pour cette relecture (sans reprendre les fonctions du
spike), hors dépôt, dans le scratchpad de session : `c4_plancher.py`, `c4_gaz.py`,
`c2_heures.py`, `c2_quarts.py` et leurs sorties `*_sortie.txt`. Le scratchpad peut être vidé :
la spécification est donc redonnée à chaque point, pour qu'on puisse refaire le calcul.

**Verdict : le spike est un bon état de l'art et un bon inventaire des pièges, mais sa
proposition d'enquête n'est pas publiable en l'état.** Les citations que j'ai pu ouvrir sont
exactes. Les calculs sont reproduits au centième près. Ce qui ne tient pas, c'est
l'**interprétation causale** : le « plancher mesuré » (C4) n'est ni un plancher ni une mesure
causale ; il est dit « recoupé » alors que les deux méthodes divergent en 2024-2025 ; C2 est
présenté comme « les heures où un MW ajouté est servi en France », et les données ne le
confirment pas ; les « 3 à 5 fois le facteur moyen » font en réalité 2,8 à 3,7 fois. La partie
ETS décrit le mécanisme de travers. Huit points de fond (F1 à F8), douze de forme (f1 à f12),
puis un plan d'enquête réduit.

## Ce que j'ai vérifié moi-même, et qui tient

**Sources primaires relues :**

- **RTE, Bilan électrique 2025**, rapport complet (copie locale `data/raw/spike_quand/pdf/be2025.pdf`) :
  19,6 gCO2éq/kWh pour la production, 20,0 pour la consommation, maximum horaire 58 g, 29,0 g en
  ACV, « près de 27 MtCO2éq » d'émissions évitées. La phrase sur l'ordre de préséance (« il n'est
  pas tenu compte de l'effet qu'aurait une modification des échanges sur l'ordre de préséance
  économique dans chaque pays ») est exacte, et elle n'est pas coupée avant sa conclusion. Annexe
  p. 145 : facteurs directs et ACV identiques au tableau du spike (CCG 331/389, TAC 497/583,
  cogénération 461/540, gaz indéterminé 435/471, charbon 855/941, lignite 961/1 040, fioul
  769/928, autres fossiles 855/941, déchets non renouvelables 988/0).
- **RTE, Bilan électrique 2024**, rapport complet (`be2024.pdf`) : 11,7 MtCO2eq, 21,7 g, 30,2 g en
  ACV, « près de 20 MtCO2eq » évitées, 10,0 MtCO2 pour la consommation. Exact (pages : f1).
- **Note ADEME-RTE du 8/10/2007** (copie DREAL Hauts-de-France, téléchargée) : marginalité
  nucléaire « environ 25 % du temps », 600 à 700 g hors de ces périodes, « pour les usages en
  base : 450 à 550 g », « de l'ordre de 400 g par kWh à l'horizon 2020 pour un usage en base »,
  méthodes « complémentaires », méthode marginale « la plus adaptée » pour une décision. Exact.
- **CRE, délibération n° 2021-126** (PDF du site de la CRE) : 0,59 tCO2/MWh ; méthode : prix avec
  SEQE moins prix sans SEQE, divisé par le prix du CO2 ; année 2019 ; paramètre du plafond d'aide
  des lignes directrices SEQE ; phrase « en 2019, pendant au moins la moitié des pas de temps, il y
  avait un moyen européen charbon et un gaz à moins de 1€/MWh du prix Spot ». Exact.
- **Règlement délégué (UE) 2023/1185**, annexe, partie A, point 6, sur le miroir lawplayer.com
  (EUR-Lex renvoie une page vide aux robots, comme l'avait constaté le spike) : options (a), (b)
  avec 183 gCO2eq/MJ, et (c). Tableau A : France 19,6 gCO2eq/MJ, année 2020, source JRC 2022.
  Conforme ; **texte officiel toujours pas relu** (f2).
- **AIE, *Energy and AI*** (copie locale `data/raw/spike/datacenters/iea_energy_ai.pdf`, p. 245) :
  « around 180 Mt of indirect CO2 emissions today from the consumption of electricity, not
  including any emissions from backup power generation ». Vérifiable, et le spike le donne pour
  non vérifié (f3).
- **Littérature** (résumés seulement, comme le spike) : Beltrami, Grossi et Liebensteiner (2025),
  fiche IDEAS : instrument = éolien des marchés voisins, et biais si l'on ignore le commerce ou la
  causalité inverse. Conforme. Holland et al. (2022), résumé PubMed : moyen −28 %, marginal +7 %.
  Conforme. Hawkes (2010) : le chiffre de 0,69 kgCO2/kWh est dans les diapositives de l'auteur ; je
  ne l'ai pas trouvé dans le résumé (f12).

**Non revérifié par cette relecture** (à marquer tel quel tant que personne ne l'a ouvert) :
citation RTE-ADEME 2020 p. 219, GHG Protocol § 6.10, ADEME Base Empreinte, figure 7.14 du BE2025
(valeurs lues sur un graphique), articles de Perino et de Rosendahl, Bruninx et Ovaere (titre et
DOI confirmés, phrase citée non relue).

**Chiffres reproduits** avec mon propre code :

- **C2**, part des heures « découplée vers le bas et J > 1 GW » : 9,1 / 4,5 / 3,3 / 0,0 / 4,3 /
  13,5 / 18,6 % (2019 à 2025). Identique au spike.
- **C3 et le plancher de C4** : spécification du spike (intra-groupe sur
  année × mois × heure × ouvré/week-end, contrôle éolien + solaire, une régression par saison,
  saisons moyennées à poids égaux). Émissions FR = `taux_co2` × production. Résultats : 0,097
  (2019-2021), 0,079 (2023-2025), 0,068 (2024-2025) t/MWh ; exportations −0,43 / −0,35 / −0,29 ;
  nucléaire +0,38, hydraulique +0,11, gaz +0,16, pompage +0,05 (2024-2025). Identique.
- **Années séparées** (demandé) : **2024 : 0,062 t/MWh** (IC 95 % ±0,010 avec grappes par jour,
  ±0,015 par semaine) ; **2025 : 0,069 t/MWh** (±0,009 / ±0,011) ; exportations −0,23 (2024),
  −0,31 (2025).
- **Arithmétique de C4** : 0,068 + 0,29 × 0,331 = 0,166 ; × 0,497 → 0,214 ; × 0,855 → 0,318 ;
  × 1,119 → 0,393 ; × 8,76 TWh. Exacte.
- **Robustesse au jeu de facteurs** : en recalculant les émissions FR avec l'annexe RTE p. 145 sur
  les sous-filières d'éCO2mix (CCG, TAC, cogénération, autres gaz, charbon, fioul ; bioénergies à
  0) au lieu de `taux_co2`, la pente est de 0,066 au lieu de 0,068 (2024-2025) et de 0,094 au lieu
  de 0,097 (2019-2021). Elle est donc insensible au jeu de facteurs. **L'intensité moyenne, elle,
  ne l'est pas** (F3).
- **Poids horaires d'une charge plate** : une pente par cellule saison × heure (96 cellules), puis
  la moyenne simple : 0,071 (2024-2025), 0,082 (2023-2025), 0,100 (2019-2021). La moyenne des
  saisons du spike est une bonne approximation de la charge plate. **Ce point tient.**
- Le contrôle par l'éolien et le solaire des voisins ne change rien (0,067 ; exportations −0,295).

## Points de fond

### F1. Le « plancher mesuré » n'est ni un plancher ni une mesure causale

- **Emplacement** : § 0, point 2 ; § 2.4, puce « Robuste » ; § 2.7, ligne 4 ; § 3.2 C3 et C4 ;
  § 3.3.
- **Problème.** Le spike réserve le biais de météo commune à la part « exportations » et dit
  « robuste » la part française. Or le même biais touche la part française. β est identifié par
  des écarts de consommation d'un jour à l'autre, à mois et heure donnés, donc surtout par la
  température. Un jour froid en France l'est aussi chez les voisins : leur demande monte, le prix
  couplé monte, et les CCG français (+0,14 MW par MW en 2024-2025, presque toute la réponse du gaz,
  `c4_gaz.py`) démarrent ou montent **pour exporter**, pas pour servir la consommation française.
  Sens probable des biais, à écrire :
  - **part française surestimée** : le CCG répond aussi à la demande voisine corrélée ;
  - **baisse des exportations sous-estimée** : la demande voisine tire les exportations françaises
    vers le haut le même jour ;
  - **part française sous-estimée** par l'hydraulique de stock (+0,11 MW) et la modulation
    nucléaire (+0,38 MW) : l'énergie prise aujourd'hui manque plus tard, et les émissions de ce
    report ne sont pas comptées (§ 2.4, « Biais connus »).

  Le signe net est inconnu. « Plancher » est donc faux dans les deux sens du mot : la valeur n'est
  pas une borne inférieure des émissions françaises induites, et le cas (i) n'est un plancher du
  total qu'à condition que la part française soit non biaisée.

  Indice que le biais n'est pas marginal : l'expérience des arrêts fortuits, malgré ses défauts
  (§ 2.6), donne une part française plus basse (0,03 ± 0,02 en 2023-2025 et 2024-2025) et une
  baisse des exportations plus forte (0,33 à 0,49). C'est la direction attendue d'un biais de
  météo commune sur la régression par la consommation.
- **Correction.** Ne plus écrire « plancher mesuré » ni « robuste ». Nommer la grandeur pour ce
  qu'elle est : « variation des émissions françaises associée à une variation de la consommation
  française, à heure et mois donnés (corrélation conditionnelle, court terme) ». Sur le site, rien
  de C3 ni de C4 avant une identification qui traite la météo commune : charge réalisée des
  voisins (A65, même jeton ENTSO-E) ou températures (réanalyse) en contrôle, et la variable
  instrumentale de Beltrami et al. (éolien des voisins) pour les échanges. Garder la valeur
  actuelle comme repère de travail.

### F2. « Recoupé par deux méthodes » : faux pour 2024-2025

- **Emplacement** : § 2.7, ligne « Émissions françaises induites… robuste à ± 30 % ; recoupé par
  deux méthodes » ; § 3.4, point 6.
- **Problème.** En 2024-2025, la consommation donne 0,068 ± 0,007 t/MWh et les arrêts fortuits
  0,03 ± 0,02. Les intervalles sont disjoints, avec un rapport de 2,3. Le recoupement promis au
  § 3.4.6 (« signaler un écart au-delà d'un facteur 2 ») **échouerait** sur cette période. En
  outre, le spike déclare lui-même la méthode des arrêts fortuits contaminée par un choc commun
  (les voisins produisent 1,3 à 1,5 MW de plus par MW perdu, § 2.6) : elle ne peut servir de
  recoupement à rien. Le « ± 30 % » n'a pas de source.
- **Correction.** Marquer le chiffre « non recoupé », comme le veut la règle du dépôt. Supprimer
  « ± 30 % ». Écrire le désaccord des deux méthodes, et ce qu'il dit du biais (F1).

### F3. « 3 à 5 fois l'intensité moyenne » : 2,8 à 3,7 fois, et le dénominateur n'est pas dit

- **Emplacement** : § 0, point 2 ; § 2.4.
- **Problème.** Intensité moyenne de la production éCO2mix (`taux_co2` pondéré, hors Corse) :
  35,4 / 33,3 / 35,8 g (2019-2021), 30,8 (2023), 20,1 (2024), 18,4 (2025). Rapports
  pente / moyenne :

  | Période | Pente | Moyenne éCO2mix | Rapport |
  |---|---|---|---|
  | 2019-2021 | 0,097 | 34,8 | 2,8 |
  | 2023-2025 | 0,079 | 23,1 | 3,4 |
  | 2024 | 0,062 | 20,1 (BE2024 : 21,7) | 3,1 (2,9) |
  | 2025 | 0,069 | 18,4 (BE2025 : 19,6) | 3,7 (3,5) |

  Le « 5 » n'apparaît qu'en divisant par une moyenne recalculée avec l'annexe RTE **sans les
  bioénergies** (13,9 à 15,4 g en 2024-2025). Les « 18 à 20 g » du § 2.4 sont des valeurs
  éCO2mix, pas celles du Bilan (19,6 à 21,7). Le rapport est sensible au jeu de facteurs : les
  bioénergies sont à environ 220 g dans `taux_co2` et à 0 dans l'annexe. Elles pèsent environ
  5 g/kWh dans la moyenne et rien dans la pente.
- **Correction.** Écrire « environ 3 à 3,5 fois l'intensité moyenne de la production publiée par
  RTE (2024-2025) », avec le dénominateur nommé et daté. Et seulement après F1 : c'est le
  numérateur qui est fragile.

### F4. Les intervalles ne disent que l'incertitude d'échantillonnage, et la sous-estiment

- **Emplacement** : § 2.4 (« intervalles à 95 % de ±0,01 à ±0,03 ») ; § 2.6 (tableau) ; § 3.7.
- **Problème.**
  1. Les grappes par jour ignorent l'autocorrélation des épisodes météo (vagues de froid de
     plusieurs jours). Avec des grappes par semaine, les intervalles s'élargissent d'environ 50 %
     (2024-2025 : ±0,007 → ±0,010 sur les émissions ; ±0,05 → ±0,075 sur les exportations ;
     ±0,054 → ±0,090 sur le nucléaire).
  2. L'intervalle de la moyenne des quatre saisons n'est pas donné (le spike le reconnaît).
  3. Surtout, un intervalle de ±0,007 sur une grandeur dont le biais d'identification est d'ordre
     0,03 (F1, F2) donne l'« apparence de précision » que le spike dénonce lui-même au § 2.6.
- **Correction.** Grappes par semaine (ou Driscoll-Kraay). Intervalle de la moyenne des saisons.
  Et une phrase : « intervalle d'échantillonnage, n'inclut pas l'incertitude d'identification,
  qui domine ».

### F5. C2 : le texte affirme un mécanisme que les données ne montrent pas, et le chiffre dépend de quatre choix non dits

- **Emplacement** : § 2.3, point 1 ; § 3.2 C2 ; § 3.7.
- **Problème.**
  1. **Mécanisme non vérifié.** Le texte dit qu'à ces heures « le prix français est fixé par une
     offre française » et qu'une petite consommation ajoutée « ne change pas, au premier ordre, ce
     que reçoivent les voisins ». C'est une intuition de couplage par NTC. Avec le flow-based
     (frontières BE et DE), un MW de plus en France change la position nette, donc les flux sur
     les éléments critiques. Le prix de zone est alors une combinaison de plusieurs moyens
     marginaux, ce que la CRE écrit dans la note 4 de la délibération 2021-126 (« plusieurs moyens
     […] doivent adapter leur production pour faire face à une variation, même infinitésimale »).
     Test (`c4_plancher.py`, section 4, 2024-2025, heures « basses » seules) : les émissions
     françaises répondent encore de **+0,055 ± 0,018 t/MWh**, les exportations de
     **−0,21 ± 0,06 MW/MW**, le CCG de +0,10 MW/MW, à un prix moyen de 44 à 52 €/MWh,
     inférieur à son coût variable. Réserve : conditionner sur le régime, qui dépend lui-même de la
     consommation, biaise ce test. Il ne prouve pas l'inverse, mais il interdit la phrase du
     spike. Autre indice : à ces heures, les flux physiques n'atteignent 90 % de la NTC prévue que
     39 % (CH), 44 % (IT), 47 % (ES) et 58 % (GB) du temps. C'est un indice faible (flux physiques
     et non programmes commerciaux, NTC prévue et non allouée), mais rien ne montre la saturation.
  2. **La Suisse n'est pas dans le couplage unique jour-1.** L'inclure dans « couplée à au moins un
     voisin » n'a pas de sens, et la retirer change C2 : 2024 passe de **13,5 % à 18,1 %**, 2019 de
     9,1 à 11,3 %.
  3. **Pas quart-horaire depuis le 1/10/2025.** L'effet « non mesuré » du § 3.7 se mesure avec
     `data/derive/entsoe/natif.parquet`. D'octobre à décembre 2025, la France est « basse » sur
     26,1 % des quarts d'heure, mais sur 32,8 % des heures moyennées : la moyenne gonfle
     « basse », et 14,6 % des heures sont classées basses alors que seuls 1 à 3 de leurs quarts
     d'heure le sont. Effet sur l'année 2025 : environ −1,7 point (21,8 → ≈ 20 %).
  4. **Taille de la charge.** Le seuil de 1 GW correspond à une charge de 1 GW. Pour 5 GW (ordre de
     grandeur de « Quand ? »), la part tombe à **1,7 % (2024) et 3,2 % (2025)** avec J, à
     **2,8 % et 4,4 %** avec J_r (arrêts courts pour modulation réintégrés, convention de
     « Quand ? »). Avec un seuil de 1 GW, J ou J_r ne change presque rien (18,6 → 18,8 % en 2025).

  Enfin, la Grande-Bretagne manque : ni prix ni production depuis 2021, alors que c'est une
  frontière d'export de 3 à 4 GW.
- **Correction.** Publier C2 comme une **statistique descriptive de prix** : « heures où le prix
  day-ahead français est strictement inférieur à celui de chaque zone voisine couplée », au quart
  d'heure depuis le 1/10/2025, CH à part, avec le seuil de marge paramétré par la taille de la
  charge (1, 5, 10 GW) et J et J_r côte à côte. **Aucune phrase causale** du type « servie en
  France », « presque rien », « ne change pas ce que reçoivent les voisins » tant que le test du
  point 1 n'a pas été refait proprement (programmes commerciaux A09 ou capacités allouées JAO,
  prix fictifs des éléments critiques du flow-based : un début de collecte JAO est dans
  `data/raw/spike_quand/jao/`).

### F6. Les trois cas de C4 ne sont pas des bornes

- **Emplacement** : § 0, point 4 ; § 3.2 C4 (tableau) ; § 3.4, point 7.
- **Problème.**
  1. **La part « exportations en moins » (0,29) est une estimation biaisée** (F1), probablement
     vers le bas, et non une donnée. Or le cas (iii) la multiplie par un facteur 3 à 4 fois plus
     grand que celui de la part française : une erreur de 0,1 MW/MW sur cette part déplace le cas
     (iii) de 0,1 t/MWh. Avec une part de 0,45 (2019-2021, ou arrêts fortuits 2023-2025) et une
     part française de 0,03 à 0,07, le cas (iii) va de 0,4 à 0,57 t/MWh. Le « plafond de court
     terme » 0,32-0,40 n'en est donc pas un.
  2. **Bornes de facteurs trop serrées vers le bas, et du parc français.** Les facteurs de RTE
     supposent des rendements (PCI) de **61 % pour le CCG** (331 g), 40,6 % pour la TAC (497 g),
     40 % pour le charbon et environ 38 % pour le lignite. Ce sont les valeurs du meilleur parc
     français, pleine charge. Le moyen marginal perdu est le plus souvent un CCG italien ou
     allemand (RTE BE2025 : près de la moitié des émissions « évitées » sont en Italie), à charge
     partielle, avec des démarrages. Ordre de grandeur, avec le facteur par défaut du gaz naturel
     du GIEC 2006 (56,1 tCO2/TJ, vol. 2, chap. 2, tab. 2.2, à recopier depuis le tableau) :
     348 g à 58 %, 388 g à 52 %, 561 g à 36 % (TAC). Pour une experte, le cas « gaz » se borne
     plutôt à **≈ 350-400 g (CCG) et ≈ 550-600 g (TAC)**. Charbon (94,6 t/TJ) : 851 g à 40 %,
     946 g à 36 %. Lignite (101 t/TJ) : 1 010 g à 36 %, 1 102 g à 33 % (cohérent avec l'UBA à
     1 119).
  3. **Direct seulement.** Pour le gaz importé (fuites de méthane amont, GNL), l'écart entre
     l'ACV et le direct est de +18 % chez RTE (CCG 389 contre 331). Dire que C4 l'exclut.
  4. **Deux jeux de facteurs dans une même somme** : `taux_co2` (implicites éCO2mix) pour la part
     française, l'annexe RTE pour les voisins. C'est sans effet numérique sur la pente (0,066
     contre 0,068, voir plus haut), mais le spike interdit ce mélange au § 2.2 et le pratique au
     § 3.2. Il faut au moins l'écrire.
- **Correction.** Ne pas publier le tableau « (i) / (ii) / (iii) » en Mt/an. Le remplacer par un
  calcul **conditionnel et explicitement hypothétique** à deux paramètres affichés et modifiables :
  part de la consommation ajoutée servie par des exportations en moins (0,3 à 0,5, avec la raison
  de la fourchette) et facteur du moyen remplacé (0 ; CCG 350-400 ; TAC 550-600 ; charbon
  850-950 ; lignite 950-1 100, avec les sources et rendements ci-dessus). Titre : « si… alors »,
  pas « estimation ». La ligne « facteur moyen FR 0,17 Mt » reste, comme piège montré.

### F7. Marché carbone européen : citer sans calculer suffit, mais pas avec ce texte

- **Emplacement** : § 3.5, point 4 ; § 3.2 C5 ; § 3.6.
- **Problème.**
  1. **Le mécanisme est mal dit.** « Depuis la réserve de stabilité et la règle d'invalidation […]
     l'effet est partiellement rétabli » : l'effet lit d'eau n'est pas « rétabli », il est
     **percé**. Tant que la réserve prélève et invalide, une tonne émise en plus aujourd'hui
     diminue le surplus (TNAC), donc les prélèvements dans la réserve, donc les invalidations. Le
     plafond cumulé effectif monte : **une partie** de l'émission supplémentaire s'ajoute
     réellement au cumul européen. Quand le lit d'eau est « scellé » à nouveau (plus
     d'invalidation), l'émission supplémentaire est compensée ailleurs dans le système et se
     traduit par un prix du quota plus élevé. Bruninx et Ovaere : la réponse dépend de l'année où
     le lit d'eau se referme, résultat endogène du marché.
  2. **Pas de source primaire réglementaire.** Il faut citer la directive 2003/87/CE consolidée
     (après la directive (UE) 2023/959) et la décision (UE) 2015/1814 modifiée par la décision
     (UE) 2023/852. Paramètres, d'après la page « Market Stability Reserve » de la Commission (lue
     par recherche, **à relire dans les textes**) : prélèvement de 24 % du TNAC au-delà de 1 096
     Mt, TNAC − 833 Mt entre 833 et 1 096 Mt, invalidation au-delà de 400 Mt détenus dans la
     réserve. Et la publication annuelle du TNAC par la Commission : 1 148 Mt pour 2024, publiée le
     28/05/2025, d'après la page d'actualité de la Commission, **à vérifier**. Le TNAC de 2025 a
     été publié en juin 2026 (C/2026/2957) ; valeur non lue. La révision de l'ETS et de la réserve
     est en cours en 2026 : à dater.
  3. **La réserve ne vise pas que l'étranger.** La part française (CCG français) est aussi sous
     plafond. L'avertissement ETS porte sur **tout** C4, plancher compris.
- **Correction.** Calculer serait hors de portée et dépendrait d'un modèle : ne pas le faire.
  Mais écrire trois phrases sourcées et datées :
  - C4 compte des émissions **physiques brutes de court terme** dans le périmètre de la
    production d'électricité ;
  - sous le plafond de l'ETS, leur effet sur le cumul européen est **compris entre zéro** (lit
    d'eau scellé : compensées ailleurs, avec un prix du quota plus élevé) **et la valeur brute**
    (lit d'eau percé), selon l'état de la réserve ;
  - en 2024-2026, le TNAC est au-dessus du seuil haut : la réserve prélève et invalide, donc une
    partie de l'émission s'ajoute au cumul. La part exacte n'est pas calculable sans modèle.

  Ne pas reprendre la thèse de Rosendahl (2019) sans l'avoir lue en texte intégral.

### F8. Les pièges : deux manquent, et deux sont rangés comme résolus alors qu'ils ne le sont pas

- **Emplacement** : § 3.5.
- **Problème.** Pièges traités correctement : moyen et marginal (1), double compte (2), court et
  long terme (3), direct et ACV (5), CO2 et CO2eq (6), dénominateur (7), décalage d'horodatage
  d'ENTSO-E pour la France (8 : contourné par éCO2mix, test des voisins honnêtement qualifié de
  grossier), endogénéité de la disponibilité (9), hydraulique de stock (12), unités (13).
  Rangés comme résolus à tort :
  - (10) « Météo commune » : présenté comme limité aux émissions voisines, alors qu'il touche la
    part française et la part « exportations » de C3 (F1) ;
  - (11) « Flow-based » : traité pour l'attribution de l'unité marginale, pas pour C2 (F5.1).

  Manquent :
  - **Échelle** : toutes les pentes sont locales (de petites variations autour de l'état
    observé). Pour 5 à 10 GW, la marge nucléaire non produite s'épuise (F5.4) et la réponse n'est
    plus linéaire. Le dire à chaque chiffre « pour 1 GW » ;
  - **Engagement des groupes** : les CCG répondent aussi à des heures où leur coût variable est
    au-dessus du prix (F5.1). La réponse horaire mêle l'effet de la journée (démarrages,
    réserves). Une charge plate change les deux ;
  - **Zones hors couplage** : CH (hors couplage unique jour-1) et GB (enchères explicites depuis
    2021, données absentes après 2020-2021). Dire comment chacune est traitée dans chaque
    indicateur ;
  - **Pas quart-horaire** depuis le 1/10/2025 (F5.3) ;
  - **Chaîne de substitution au-delà des voisins observés** : un export perdu vers l'Italie peut
    être remplacé par des importations italiennes depuis CH, AT ou SI. Le cas (iii) en tient
    compte comme borne, mais pas l'intensité « par pays ».

  Le piège « Italie » demandé est traité pour la production (catégorie B20 avant 2019, trou de
  l'hydraulique en 2025). Mais le prix utilisé est celui d'IT-Nord, alors que la production A75
  est celle de l'Italie entière (`meta.json` d'ENTSO-E) : à écrire au § 2.1.
- **Correction.** Ajouter ces cinq pièges au § 3.5, et requalifier (10) et (11).

## Points de forme

- **f1. Pages du BE2024.** § 1.2 et § 1.3 citent « BE2024 Émissions p. 8 » et « annexe p. 12 » :
  ce sont les pages du chapitre isolé. Dans le rapport complet (copie locale), c'est p. 97-98, et
  l'annexe est en fin de volume. Dire quelle édition. RTE écrit « 10,0 MtCO2 » (sans « eq ») pour
  la consommation : reproduire tel quel.
- **f2. Coïncidence de valeurs, piège d'unités.** § 1.4 : « France 19,6 gCO2eq/MJ, année 2020 »
  (règlement 2023/1185, ACV, JRC 2022) vaut **70,6 g/kWh**. Même nombre que les 19,6 g/kWh
  directs du BE2025 pour 2025. Écrire la conversion à côté, sinon l'erreur est certaine à la
  première reprise. Préciser aussi que le texte a été lu sur un miroir, non sur EUR-Lex.
- **f3. AIE marquée non vérifiée alors que le PDF est dans `data/raw/`** : 180 Mt vérifié (p. 245,
  « indirect CO2 emissions », hors secours). La méthode (moyenne ou marginale) n'est pas dite dans
  ce passage : laisser « méthode non précisée ».
- **f4. Annexe RTE « sans source ni année »** : RTE écrit (BE2025, sous la figure 5.8) que ses
  facteurs « sont issus de travaux internes ; ils reposent sur un ensemble de sources et modèles,
  et sont harmonisés entre les différentes publications », et (note 4 du chapitre) que les
  facteurs actuels sont appliqués à tout l'historique. Citer ces deux phrases au lieu de « ne cite
  ni source ni année ».
- **f5. § 0, point 2** : « 0,06 à 0,10 t (2023-2025 ; 0,10 en 2019-2021) » mêle une fourchette de
  saisons et une valeur de période. Donner les valeurs par période et par année : 0,097
  (2019-2021), 0,079 (2023-2025), 0,068 (2024-2025), 0,062 (2024), 0,069 (2025).
- **f6. § 3.7** : « effet non mesuré » du pas quart-horaire : il est mesurable, voir F5.3.
- **f7. 928 événements** : l'annotation en tête ne suffit pas. Le § 2.6 (928 événements,
  72 TWh) et le § 3.7 répètent le chiffre faux. Annoter **à l'endroit** (barré ou
  `[corrigé : 407 …]`), sinon un lecteur du seul § 2.6 le reprend.
- **f8. Libellé « Facteur moyen FR » du tableau C4** : 0,0196 est l'intensité de la production
  2025 (BE2025), appliquée à la période 2024-2025. Écrire « intensité moyenne de la production
  2025, RTE ».
- **f9. Figure 7.14 du BE2025** : les valeurs « RTE » du recoupement (DE 286, ES 95…) sont **lues
  sur un graphique**. Le marquer dans le tableau (± lecture), et ne pas en faire un contrôle
  `pc check` à ±5 % (§ 3.4.5) sans valeur publiée en clair.
- **f10. Délibération CRE** : ajouter que le facteur de 0,59 était prévu pour s'appliquer
  « jusqu'à la prochaine révision des lignes directrices soit 2025 » (même délibération). Il est
  donc possiblement remplacé : à dater.
- **f11. Source manquante** : le règlement délégué (UE) 2025/2359 (méthode des carburants bas
  carbone) reprendrait la même règle de l'heure fixée par le bas carbone avec 0 / 183 gCO2eq/MJ
  (vu dans les résultats de recherche, **non lu**). À vérifier : c'est la règle européenne la plus
  récente sur la question voisine.
- **f12. Hawkes (2010)** : 0,69 kgCO2/kWh vient des diapositives de l'auteur ; le résumé ne le
  donne pas. Garder « [résumé] » seulement si le chiffre y est, sinon « [diapositives de
  l'auteur] ».

## Réponses directes aux cinq questions

1. **Sources** : tout ce que j'ai pu ouvrir est exact et non tronqué (liste plus haut). Restent
   non vérifiés : RTE-ADEME 2020 p. 219, GHG Protocol, ADEME Base Empreinte, le texte officiel
   d'EUR-Lex, les textes intégraux de la littérature, et la figure 7.14 (lecture de graphique).
2. **Chiffres** : C2 et C4 reproduits à l'identique (2024 : 0,062 ; 2025 : 0,069 t/MWh). Mais
   aucune des méthodes n'est identifiée causalement : la consommation est corrélée à la météo
   voisine (F1), le régime de prix dépend de la consommation (F5), la disponibilité est en partie
   endogène (§ 2.6, déjà vu). Les intervalles sont trop étroits et ne couvrent pas
   l'identification (F4). « 3 à 5 fois » : non, 2,8 à 3,7 fois (F3).
3. **Cas des exportations perdues** : les facteurs viennent du parc français à pleine charge, en
   direct ; la part « exportations » est biaisée ; ce ne sont pas des bornes (F6). ETS : citer
   sans calculer suffit, mais le texte actuel inverse le sens du mécanisme et oublie les textes
   réglementaires (F7).
4. **Pièges** : onze bien traités, deux requalifiés, cinq ajoutés (F8).
5. **Publiable** : voir le plan ci-dessous.

## Plan d'enquête recommandé

Principe : publier ce qui est **mesuré ou cité**, montrer pourquoi le reste ne se mesure pas avec
des données ouvertes, et ne jamais donner un total en Mt/an qui ressemble à une estimation.

**Publiable après corrections de forme (une passe) :**

1. **C1, intensité moyenne**, production et consommation, horaire et annuelle, avec l'adjectif
   « moyenne » partout, la valeur RTE du Bilan (19,6 et 20,0 g en 2025) et une note sur les deux
   jeux de facteurs RTE (implicites d'éCO2mix et annexe). Le piège montré : « 1 GW × intensité
   moyenne = 0,17 Mt/an, et voici pourquoi ce calcul ne dit pas l'effet d'une consommation
   ajoutée ».
2. **« Ce que disent les institutions »**, texte seulement, citations relues : RTE sur les
   émissions évitées et l'ordre de préséance ; ADEME-RTE 2007 (marginal, historique, non
   transposable) ; CRE 2021-126 (facteur de marché 0,59, et pourquoi la CRE écarte le moyen
   marginal observé) ; règlement 2023/1185 (règle des heures fixées par le bas carbone, forfait
   183 g/MJ, avec la conversion) ; la littérature (désaccord court terme / long terme). C'est le
   cœur robuste de l'enquête : **personne ne publie de facteur marginal français récent, et
   chaque institution contourne la question par une règle**.

**Publiable après un travail court (jours, données déjà là) :**

3. **C2 refait en statistique descriptive** (F5) : au quart d'heure depuis le 1/10/2025, CH et GB
   traitées à part, seuil de marge selon la taille de la charge (1, 5, 10 GW), J et J_r. Sans
   phrase causale. Contrôles `pc check` : parts qui somment à 100 %, cohérence horaire et
   quart-horaire.
4. **ETS en trois phrases** sourcées sur les textes réglementaires et la publication du TNAC
   (F7).
5. **Calcul conditionnel « si… alors »** (F6) : deux réglages affichés (part servie par des
   exportations en moins ; facteur du moyen remplacé), sources des facteurs et rendements, en
   direct, avec l'ACV en note. Présenté comme une hypothèse de la lectrice, jamais comme un
   résultat du site. La part 0,3-0,5 est justifiée par les deux méthodes du spike et leur
   désaccord, sans en retenir une.

**À ne publier qu'après un vrai travail d'identification (semaines) :**

6. **C3 et la part française de C4**, avec la charge réalisée des voisins (A65) et des
   températures en contrôle, puis l'instrument éolien des voisins à la Beltrami et al. Critère
   d'entrée : deux méthodes à identification différente qui se recoupent à un facteur 1,5 près,
   intervalles à grappes par semaine. Jusque-là : « non recoupé », hors site.

**À abandonner :**

7. La régression de zone à la Hawkes (§ 2.5) : elle répond à une autre question, et le spike le
   démontre.
8. L'expérience des arrêts fortuits **comme estimation** (§ 2.6), sauf si les contrôles du point 6
   la rendent propre. On peut la garder comme diagnostic du biais de météo commune.
9. Toute attribution d'une « unité marginale » horaire par le prix (sans prix des combustibles ni
   du CO2, et la CRE explique pourquoi même avec eux c'est fragile).
10. Le tableau C4 en Mt/an avec trois cas « mesurés » (remplacé par le point 5).

**Pour le long terme (C5)** : texte seulement, RTE et littérature (Gagnon et al., Ricks et al.,
Hawkes 2014). Rien sur Hemmati et al. (préprint) tant qu'il n'est pas évalué par les pairs.
