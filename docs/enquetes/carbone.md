---
titre: Quel carbone ?
question: Que vaut le contenu carbone de l'électricité française, et que dit-il des émissions d'une consommation ajoutée ?
mise_a_jour: 2026-11-26
accroche: {{intensite_prod_rte_2025}} en moyenne pour la production française de 2025. C'est une moyenne : elle ne dit pas ce qu'émettrait une consommation ajoutée, et aucune institution ne publie de [facteur marginal](glossaire:facteur-moyen-marginal) récent pour la France, à notre connaissance.
---

<!--
Syntaxe propre au site : voir docs/enquetes/combien.md.
Aucun nombre issu d'une source ou d'un calcul n'est tapé à la main dans
ce fichier ; les nombres en clair sont des conversions expliquées dans la
phrase (× 3,6 pour passer des MJ aux kWh) ou des écarts relatifs entre
deux chiffres cités. Les chiffres `carbone_*` sont calculés par `pc build`
(pipeline/pc/carbone.py) et contrôlés par `pc check`.
Tout chiffre carbone dit sa famille : intensité moyenne, contenu
marginal, facteur de marché, valeur forfaitaire, facteur d'une filière.
Une ligne `::: chantier nom :::` est remplacée par l'encart « en
préparation » décrit dans docs/enquetes/chantier/nom.md.
-->

Une consommation ajoutée au réseau français, celle d'un data center par
exemple, consomme une électricité dont RTE publie chaque année le contenu
carbone moyen. Ce chiffre est publié et sourcé. Il ne répond pourtant pas
à la question qu'on lui pose le plus souvent : combien d'émissions cette
consommation de plus entraînerait-elle ? Cette enquête dit ce que vaut
l'[intensité moyenne](glossaire:intensite-carbone), comment elle varie d'une heure et d'une saison à
l'autre, ce que publient les institutions, et pourquoi le chiffre utile,
le [facteur marginal](glossaire:facteur-moyen-marginal), manque.

**Ce qu'on en retient.** En 2025, l'intensité carbone moyenne de
l'électricité produite en France valait {{intensite_prod_rte_2025}} en
émissions directes selon RTE ; celle de l'électricité consommée,
importations comprises, {{intensite_conso_rte_2025}}. Cette moyenne varie
fortement selon la saison et l'heure. Mais une moyenne
répartit des émissions qui ont eu lieu ; elle ne dit pas ce qu'une
consommation ajoutée ferait émettre, en France ou chez les voisins. Ce
facteur marginal, aucune institution ne le publie aujourd'hui pour la
France, à notre connaissance : la dernière estimation d'un contenu
marginal en grammes par kWh, de RTE et de l'ADEME, date de 2007 ; depuis,
les deux organismes jugent cette approche inadaptée aux gros volumes et
comparent des scénarios. Les règles européennes contournent la question
par des forfaits et des règles de prix. Ce site ne sait pas encore le
calculer, et dit pourquoi.

## Une vingtaine de grammes par kWh, en moyenne

RTE publie deux intensités moyennes, en émissions directes, c'est-à-dire
celles de la combustion dans les centrales. Celle de la production valait
{{intensite_prod_rte_2025}} en 2025 et
{{intensite_prod_rte_2024}} en 2024. Celle de la consommation retranche les émissions de l'électricité
exportée et ajoute celles de l'électricité importée : {{intensite_conso_rte_2025}}
en 2025. Les deux sont presque égales, écrit RTE, parce que la France a
été exportatrice nette presque toute l'année. Pour attribuer une
intensité aux importations, RTE suit les flux à travers
{{intensite_conso_pays_tracage}} et donne à chaque importation
l'intensité moyenne de la production du pays d'où elle vient : la
consommation a donc, elle aussi, une intensité moyenne.

Ce site recalcule ces moyennes heure par heure, à partir des séries que
RTE publie en open data. Pour la production, le taux d'émission
d'éCO2mix, pondéré par la production de chaque heure, donne
{{carbone_prod_moyenne_2025}} en 2025 et {{carbone_prod_moyenne_2024}} en
2024, soit environ 6 % et 7 % de moins que le Bilan électrique. L'écart
est attendu et contrôlé : éCO2mix ne couvre pas la Corse, dont la
production thermique est au fioul, et n'applique pas les facteurs
d'émission de l'annexe du Bilan, mais le facteur de chaque combustible
tiré de la Base Carbone de l'ADEME (aujourd'hui intégrée à sa Base Empreinte), combiné au rendement moyen de la
filière {{source:rte-eco2mix-emissions|page éCO2mix « eCO2 emissions »}}.
D'après une estimation du site, la Corse explique l'essentiel de l'écart.
Pour la consommation,
la série horaire que RTE publie depuis 2021 donne
{{carbone_conso_moyenne_2025}} en 2025, à 1 % près du Bilan. Ces
recoupements viennent tous de RTE : ils vérifient le calcul du site, pas
les facteurs d'émission eux-mêmes, que RTE dit « issus de travaux
internes » {{source:rte-be2025|p. 105, sous la figure 5.8}}.

Ces facteurs ne comptent que la combustion. Sur le cycle de vie
(extraction et transport des combustibles, construction des centrales,
des éoliennes et des panneaux), RTE trouve {{intensite_prod_acv_rte_2025}}
pour la production de 2025 ; RTE y compte zéro pour l'incinération des
déchets {{source:rte-be2025|annexe, p. 145}}. Une intensité directe ne se compare qu'à une
intensité directe, et une intensité sur le cycle de vie qu'à une autre
intensité sur le cycle de vie.

## Heure par heure, saison par saison

La moyenne annuelle cache des écarts nets. En 2025, l'intensité moyenne
de la production valait {{carbone_prod_hiver_2025}} de novembre à mars et
{{carbone_prod_ete_2025}} d'avril à octobre. En moyenne par mois et par
heure, elle allait de {{carbone_prod_mh_min_2025}}, en début
d'après-midi en septembre, à {{carbone_prod_mh_max_2025}}, en début de
soirée en février. RTE situe les hausses « surtout en hiver, lors des
périodes de consommation élevée, lors desquelles il est nécessaire de
faire appel à des moyens de production thermique fossile, et
éventuellement aux importations depuis des pays dont la production est
plus carbonée » {{source:rte-be2025|p. 105}}.

L'heure la plus carbonée de 2025, pour la production, valait
{{carbone_prod_max_2025}} : le matin du 14 janvier, celui où la [charge
résiduelle](glossaire:charge-residuelle) de [« Quand ? »](/quand) a culminé. RTE donne un maximum de
{{intensite_max_rte_2025}}, sans nommer la série ; sa [monotone](glossaire:monotone) de
l'intensité de la consommation culmine à ce niveau en 2025
{{source:rte-be2025|p. 104, figure 5.7}}. La série horaire de la
consommation que RTE publie en open data, recalculée en 2026, culmine,
elle, à {{carbone_conso_max_2025}}. À l'autre bout,
{{carbone_prod_part_sous_15_2025}} des heures de 2025 sont restées sous
{{intensite_fond_rte}} pour la production, {{carbone_conso_part_sous_15_2025}}
pour la consommation. RTE appelle ce niveau « l'intensité de fond » du
système et l'attribue à l'incinération des déchets et aux cogénérations.

2022 donne un autre ordre de grandeur. La disponibilité du parc nucléaire
était tombée à {{dispo_nucleaire_rte_2022}} ; l'intensité moyenne de la
production a atteint {{carbone_prod_moyenne_2022}} sur l'année, celle de
la consommation {{carbone_conso_moyenne_2022}}, avec une heure à
{{carbone_conso_max_2022}}. Une intensité moyenne dépend de l'année
observée : une consommation qui démarrera en 2027 ou en 2030 tombera dans
un système qu'aucune de ces années ne décrit.

::: graphique carbone-mois-heure :::

## Pourquoi la moyenne ne dit pas l'effet d'une consommation ajoutée

Une intensité moyenne divise les émissions d'une période par l'énergie de
la période. Elle répartit entre tous les kWh des émissions qui ont eu
lieu : c'est la bonne mesure pour un inventaire, quand il s'agit
d'attribuer à chacun sa part. La question d'une consommation qui s'ajoute
est différente : de combien les émissions changent-elles quand la
consommation augmente ? C'est un facteur marginal, et rien n'oblige les
deux à se ressembler.

Les chiffres de RTE le montrent sans calcul. Sur les
{{emissions_prod_rte_2025}} émises par la production d'électricité en
2025, {{emissions_cogeneration_rte_2025}} viennent de cogénérations au
gaz, dont le « fonctionnement est indépendant des conditions du marché de
l'électricité », et {{emissions_dechets_rte_2025}} de l'incinération de
déchets, filière dont le fonctionnement est « principalement déterminé
par le besoin de traitement des déchets » {{source:rte-be2025|p. 102-103}}.
En comptant aussi les cogénérations au fioul, que RTE ne chiffre pas
séparément, la part des émissions « qui n'est pas assimilable aux
cogénérations ou aux filières fatales ne représente que »
{{part_emissions_hors_socle_rte_2025}} : elle vient de moyens qui
assurent l'équilibre du système aux périodes de forte consommation
{{source:rte-be2025|p. 103-104, figure 5.6}}. Ces émissions de fond
entrent dans la moyenne de chaque heure ; d'après la description qu'en
fait RTE, une consommation ajoutée ne les fait pas varier. Ce qui répond
à une consommation de plus, ce sont notamment les moyens qui peuvent
moduler leur production : le nucléaire quand il lui reste de la marge,
l'hydraulique, le gaz, le charbon et le fioul, le pompage des stations
de transfert d'énergie, les [effacements](glossaire:effacement), l'éolien et le solaire arrêtés
aux heures de [prix négatifs](glossaire:prix-negatif), et les échanges avec les voisins.

Le facteur marginal d'une heure peut donc être nul en émissions
directes, quand une consommation ajoutée est servie par du nucléaire
resté inemployé, même si le combustible utilisé alors peut manquer plus
tard (voir [« Quand ? »](/quand)), ou par de l'eau de barrage, qui
manquera à une autre heure ; ou bien plus élevé que la moyenne, quand
elle l'est par une centrale à gaz, en France, ou par moins d'exportations
vers un voisin qui fait alors tourner la sienne. Pour fixer un ordre de
grandeur, RTE retient pour les cycles combinés au gaz, les centrales au
gaz les plus performantes, un facteur moyen de filière de
{{facteur_ccg_direct_rte}} en émissions directes, et de
{{facteur_tac_direct_rte}} pour les turbines à combustion.
Multiplier une consommation ajoutée par l'intensité moyenne ne donne donc
pas les émissions qu'elle entraîne : cela donne la part des émissions
existantes qu'on lui attribuerait dans un inventaire.

## Ce que disent les institutions

- **RTE : des moyennes, et des émissions « évitées » calculées avec des
  moyennes.** Selon RTE, les exportations françaises ont évité près de
  {{emissions_evitees_rte_2025}} en Europe en 2025. La méthode compare,
  heure par heure, l'intensité moyenne de la production française à
  celle des pays importateurs, et multiplie l'écart par les volumes
  exportés. RTE en écrit la limite : elle « néglige certains phénomènes
  propres au fonctionnement du système électrique : en particulier, il
  n'est pas tenu compte de l'effet qu'aurait une modification des
  échanges sur l'ordre de préséance économique dans chaque pays. Cela
  étant, l'analyse des émissions évitées ainsi calculées permet tout de
  même de dégager des tendances, notamment dans le temps et dans la
  répartition géographique. » Ce chiffre n'est donc pas un facteur
  marginal, et il ne s'additionne à aucune autre estimation d'émissions.
- **RTE et l'ADEME, 2007 : le dernier contenu marginal publié en
  grammes par kWh.** Dans
  une note commune, les deux organismes estimaient qu'une consommation
  ajoutée en France était servie par le nucléaire environ
  {{ademe_rte_2007_marginalite_nucleaire}} du temps, et le reste du temps
  par du charbon, du gaz ou du fioul, en France ou ailleurs en Europe. Ils
  en tiraient un contenu marginal de {{ademe_rte_2007_marginal_base}}
  pour un usage « en base », celui d'une consommation continue, et
  l'envisageaient « de l'ordre de » {{ademe_rte_2007_marginal_base_2020}}
  à l'horizon 2020. Le calcul était fait « compte tenu des équipements de
  production existants et décidés » {{source:ademe-rte-2007|p. 2}}, et
  la note disait ses résultats « valables pour des décisions représentant
  plusieurs dizaines de TWh » {{source:ademe-rte-2007|p. 4}}. Elle jugeait
  les approches moyenne et marginale « complémentaires » : la première
  pour le bilan d'une situation figée, la seconde pour « évaluer l'impact
  futur d'une décision prise aujourd'hui » {{source:ademe-rte-2007|p. 7}} ;
  et la méthode marginale « nécessite d'être revisitée régulièrement »
  {{source:ademe-rte-2007|p. 4}}. Ses chiffres décrivent le parc européen
  de 2007 : ils sont historiques, pas transposables.
- **RTE et l'ADEME, 2020 : la méthode marginale écartée pour les gros
  volumes.** Dans leur rapport sur le chauffage, les deux organismes
  jugent que la méthode marginale « n'est pas généralisable à un volume
  important » et qu'elle « n'apparaît donc pas adaptée dans une approche
  prospective à long terme si le parc de production évolue »
  {{source:rte-ademe-2020-chauffage|p. 208}}. Ils comparent plutôt des
  scénarios avec et sans les nouveaux usages, en intégrant « les
  variations d'émissions induites sur les systèmes électriques des pays
  voisins », méthode déjà appliquée par RTE à la mobilité électrique en
  2019 et à l'hydrogène en 2020 {{source:rte-ademe-2020-chauffage|p. 209}}.
  Ce rapport ne publie pas de facteur marginal du système français. La
  note de 2007 et le rapport de 2020, des mêmes organismes, ne disent donc
  pas la même chose de l'usage du marginal pour de gros volumes ; ce site
  ne tranche pas.
- **La CRE, 2021 : un facteur « fondé sur le marché », qui ne mesure pas
  des émissions.** Pour plafonner les aides d'État aux industriels
  électro-intensifs, la CRE a approuvé un facteur de
  {{cre_facteur_marche_2019}}. RTE a simulé le marché de 2019 avec et
  sans marché du carbone ; le facteur est l'écart de prix moyen rapporté
  au prix du CO2. Il dit combien le prix du quota se retrouve dans le
  prix de l'électricité, pas ce qu'émet un kWh de plus. La CRE y juge
  « moins robustes » les méthodes qui cherchent le moyen marginal à
  partir des prix : les offres de marché étant anonymes, « il n'y a pas
  de "données observées relatives à la technologie marginale" », et
  plusieurs moyens doivent souvent ajuster leur production pour une même
  variation de la demande, notamment du fait du couplage des marchés
  fondé sur les flux {{source:cre-2021-126|p. 3 et note 4}}. Calculé sur
  2019, ce facteur devait servir « jusqu'à la prochaine révision des
  lignes directrices soit 2025 » {{source:cre-2021-126|p. 2}} ; ce site
  n'a pas vérifié s'il a été remplacé depuis.
- **L'Union européenne : des règles, pas des mesures.** Pour l'hydrogène
  et les autres carburants renouvelables d'origine non biologique, le
  règlement délégué (UE) 2023/1185 laisse trois façons de compter les
  émissions de l'électricité du réseau. La première prend l'intensité
  moyenne du pays ou de la zone de prix : pour la France,
  {{ue_intensite_france_2020}}, données de 2020, combustion et amont des
  combustibles compris, soit environ
  70,6 g par kWh (× 3,6) ; le même nombre que l'intensité de RTE pour
  2025, mais ni la même unité, ni la même année, ni le même périmètre. La
  deuxième est une règle de prix : zéro tant que l'installation ne tourne
  pas à pleine charge plus d'heures que n'en a compté, l'année
  précédente, le prix fixé par du renouvelable ou du nucléaire ; au-delà,
  un forfait de {{ue_forfait_reseau_183}}, soit environ 659 g par kWh
  (× 3,6). La troisième prend les émissions de l'unité marginale, mais
  seulement « si cette information est accessible au public auprès du
  gestionnaire de réseau de transport national »
  {{source:ue-2023-1185|annexe, partie A, point 6, JO L 157/25}} : à notre
  connaissance, RTE ne la publie pas. Pour compter comme renouvelable
  l'électricité du réseau achetée par contrat, le règlement 2023/1184,
  dans sa rédaction de 2024, exige notamment qu'elle soit consommée dans
  le même mois que sa production jusqu'à fin 2029, dans la même heure
  ensuite ; la condition est toujours tenue pour remplie quand le prix
  [day-ahead](glossaire:day-ahead) ne dépasse pas {{ue_correlation_seuil_prix}}, ou reste sous
  {{ue_correlation_coef_quota}} le prix d'un quota de CO2.
  Aucun de ces textes ne vise
  les data centers : ils montrent comment le législateur a tranché une
  question voisine, par des règles de prix et des forfaits, faute de
  mesure.
- **L'AIE : un ordre de grandeur mondial, sans méthode dite.** L'Agence
  internationale de l'énergie estime à {{aie_dc_emissions_monde_2024}}
  les émissions indirectes des data centers du monde, dues à leur
  consommation d'électricité. Le passage ne dit pas s'il s'agit d'une
  intensité moyenne ou marginale et ne donne aucun chiffre pour la
  France.
- **Le marché européen du carbone.** Les centrales fossiles de l'Union,
  en France comme chez les voisins qui en sont membres, sont soumises au
  système d'échange de quotas de l'Union : chaque tonne émise doit être
  couverte par un quota. Celles de Grande-Bretagne relèvent d'un système
  britannique, celles de Suisse d'un système suisse, lié au système
  européen ; ce qui suit ne vaut que pour l'Union. Si le
  plafond était fixe, une tonne émise en plus serait compensée ailleurs,
  avec un prix du quota plus élevé. Il ne l'est plus tout à fait : des
  quotas sont retirés des enchères et placés dans une réserve tant que le
  nombre de quotas en circulation dépasse {{ets_seuil_prelevement_bas}},
  et ceux que la réserve détient au-delà de {{ets_seuil_invalidation}}
  ne sont plus valides. Le nombre en circulation valait
  {{ets_tnac_2024}} pour 2024 et {{ets_tnac_2025}} pour 2025 : la réserve
  prélève. D'après ces règles, que ce site lit sans les modéliser, une
  tonne émise en plus diminue le nombre de quotas en circulation, donc
  ce qui part dans la réserve, donc ce qui y est annulé. Tant que des
  quotas sont annulés, une partie d'une émission supplémentaire s'ajoute
  au total européen au lieu d'être compensée ailleurs ; laquelle dépend
  de l'évolution du marché et ne se calcule pas sans modèle. Ces règles
  changent. La Commission a proposé le 1er avril 2026 de mettre fin à
  l'annulation {{source:ce-tnac-2025|section 2}}. Le texte de compromis
  approuvé par les représentants des États membres le 28 octobre 2026 la
  garde : à partir de son entrée en vigueur, seuls les quotas que la
  réserve détient au-delà de {{ets_seuil_invalidation_compromis}} ne sont
  plus valides. Il rappelle que la révision plus large proposée par la
  Commission en juillet 2026 rend dynamiques les seuils haut et bas de la
  réserve, leurs marges et la quantité qu'elle remet sur le marché, et
  demande que cette révision prévoie aussi une baisse annuelle du seuil
  d'invalidation {{source:conseil-14944-26|annexe, considérants 3 et 3a, article 1er}}.
  Le Parlement européen l'a adopté en première lecture le 24 novembre
  2026 ; au 26 novembre, la procédure attendait la position du Conseil
  {{source:pe-oeil-2026-0085|fiche de procédure}}. Si ce texte entre en
  vigueur, il peut n'y avoir aucune annulation tant que la réserve reste
  sous le nouveau seuil : l'effet décrit plus haut disparaîtrait alors à
  court terme.

## Le facteur marginal : personne ne le publie

Rassemblées, ces sources disent la même chose en creux. RTE publie des
moyennes, et des émissions « évitées » dont il écrit lui-même la limite.
La CRE publie un paramètre de prix. L'Union européenne fixe des forfaits
et des règles de prix. La dernière estimation d'un contenu marginal
français en grammes par kWh par une institution date de 2007 ; depuis,
RTE et l'ADEME jugent cette approche inadaptée aux gros volumes et
comparent des scénarios, sans publier de facteur du système. À notre
connaissance, après une recherche non exhaustive chez RTE, l'ADEME, la
CRE et le ministère chargé de l'énergie, aucune institution n'en publie
de plus récent, ni annuel, ni horaire.

Ce site ne le calcule pas non plus, pas encore. Les données publiques
montrent comment les émissions françaises, la production et les échanges
varient avec la consommation. Elles ne permettent pas, telles quelles,
de lire dans ces variations l'effet d'une consommation ajoutée, pour
trois raisons.

- **La météo est commune.** Un jour froid en France l'est aussi chez les
  voisins : leur demande et la demande française montent ensemble, et une
  centrale française qui démarre ce jour-là peut produire aussi pour
  l'exportation. Une corrélation entre consommation française et
  émissions mêle les deux effets.
- **Les voisins.** Une part d'une consommation ajoutée serait servie par
  moins d'exportations. Ce que le voisin produit alors à la place dépend
  de son parc, de ses prix et de ses propres échanges, qui ne sont pas
  encore dans les données publiées par ce site.
- **Le couplage par les flux.** Aux frontières avec la Belgique et
  l'Allemagne, les capacités d'échange sont calculées sur un réseau
  maillé : un MW de plus en France modifie les flux sur plusieurs lignes,
  et le prix d'une zone peut dépendre de plusieurs moyens à la fois,
  comme l'écrit la CRE.

::: chantier facteur-marginal :::

## Ce que ce calcul ne dit pas

- **Le marginal, à aucune heure.** Une heure de faible intensité moyenne
  n'est pas forcément une heure de faible facteur marginal, et
  inversement. Déplacer une consommation vers les heures les moins
  carbonées en moyenne ne garantit pas, à lui seul, une baisse des
  émissions.
- **Le long terme.** Une consommation durable de plusieurs TWh change ce
  qui se construit, ce qui ferme et la façon dont le parc est exploité.
  Ce site observe des années passées ; il ne modélise pas ces effets.
- **La Corse.** Les séries d'éCO2mix couvrent la France continentale ;
  le Bilan électrique inclut la Corse. D'après une estimation du site, non
  publiée en chiffres, c'est la principale raison de l'écart entre les
  deux moyennes de la production ; le reste tient à des différences de
  facteurs et de périmètre des filières.
- **Le cycle de vie.** Les intensités calculées ici sont en émissions
  directes. Les chiffres sur le cycle de vie sont ceux de RTE.
- **La décimale.** Les valeurs horaires dépendent de la convention
  d'horodatage d'éCO2mix retenue par le site ; avec la convention
  inverse, certaines moyennes et certains maxima changent d'un dixième ou
  d'un demi-gramme. Les notes le signalent.
- **L'horodatage de la consommation.** RTE ne précise pas si l'heure de
  la série de la consommation en marque le début ou la fin. Ce site la
  lit comme le début ; une erreur d'une heure ne change pas les
  moyennes annuelles, seulement le profil horaire.
