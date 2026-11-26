---
titre: Glossaire
mise_a_jour: 2026-11-26
---

<!--
Glossaire du site, rendu replié sur /methode (section « Glossaire »), une ancre par terme :
/methode#g-<identifiant>. Lu et contrôlé par site/src/lib/server/glossaire.ts ; tout écart au
format fait échouer le build et les tests.

Format, une entrée par titre de niveau 2, entrées dans l'ordre alphabétique des termes :

  ## Terme affiché {#identifiant}

  Définition : un seul paragraphe, de 2 à 5 phrases, au sens retenu par ce site.

  Source : [texte](https://…), p. N.          (facultatif, une seule ligne, source primaire)

- identifiant : minuscules, chiffres et tirets ; stable (des pages y renvoient).
- Dans la définition : **gras**, *italique*, liens [texte](https://…) et renvois à une autre
  entrée [texte](glossaire:identifiant). Pas de chiffre du référentiel ({{…}}) : une définition
  ne porte pas de chiffre sourcé, sauf nécessité (alors daté et sourcé dans la phrase).
- Depuis une page du site (enquêtes, message, textes du simulateur), un renvoi s'écrit
  [texte](glossaire:identifiant), à la première occurrence du terme dans la page seulement.
-->

## Adéquation, défaillance, délestage {#adequation}

L'adéquation est la capacité du parc (production, stockage, effacements, importations) à couvrir
la consommation ; RTE l'évalue par une simulation probabiliste du système français et européen,
sur de nombreux scénarios de météo et de disponibilité des moyens. Le critère public de sécurité
d'approvisionnement est une espérance annuelle de 3 heures de défaillance, c'est-à-dire de
déséquilibre entre l'offre et la demande, et de 2 heures de délestage, la coupure organisée de
consommateurs en dernier recours. La marge dont parle RTE est l'écart, en capacité, entre le parc
simulé et celui qui respecterait exactement ce critère : un résultat de simulation, pas une
grandeur observable heure par heure.

Source : [RTE, Bilan prévisionnel 2025-2035, Fonctionnement du système électrique](https://assets.rte-france.com/prod/public/2026-07/2026-07-15-bilan-previsionnel-fonctionnement-systeme-electrique.pdf), p. 2.

## CFE 24/7 (énergie décarbonée heure par heure) {#cfe-24-7}

Objectif de couvrir chaque heure de consommation par une production décarbonée de la même heure,
sur le même réseau ou dans la même zone de marché, au lieu d'un appariement en volume sur l'année
par [garanties d'origine](glossaire:garanties-origine) ou par contrat. Le score CFE est la part de
la consommation ainsi couverte, calculée heure par heure puis agrégée sur l'année. Porté
notamment par Google et par une initiative onusienne, le 24/7 Carbon-Free Energy Compact, ce
n'est pas une norme réglementaire : les sources admises (nucléaire compris ou non), le périmètre
géographique et la prise en compte du mix du réseau varient d'une méthode à l'autre. Le droit
européen applique une logique voisine, la corrélation temporelle à l'heure à partir de 2030, à
l'électricité renouvelable achetée par contrat pour produire des carburants renouvelables
d'origine non biologique, dont l'hydrogène.

Source : [Règlement délégué (UE) 2023/1184](https://eur-lex.europa.eu/eli/reg_del/2023/1184/oj), article 6, dans sa rédaction issue du règlement délégué (UE) 2024/1408.

## Charge résiduelle {#charge-residuelle}

Grandeur calculée par ce site, heure par heure : la consommation, moins la production éolienne
et solaire, moins la puissance nucléaire déclarée disponible par EDF au titre de
[REMIT](glossaire:remit). Ce qui reste doit venir de l'hydraulique (fil de l'eau compris), du
gaz, des autres centrales thermiques, des importations ou du stockage ; les effacements activés
sont déjà retranchés de la consommation observée. Ce n'est ni la « consommation résiduelle » des
publications de RTE, ni la charge nette courante qui ne retranche que l'éolien et le solaire, ni
une marge : la puissance disponible des autres moyens n'est pas observée heure par heure.

## Consommation plate {#consommation-plate}

Consommation dont la puissance est la même à chaque heure de l'année. C'est le profil que ce site
suppose pour une consommation ajoutée, faute de courbe de charge publiée des data centers : une
hypothèse de calcul, pas un profil observé.

## Écrêtement, production renoncée {#ecretement}

Baisse de la production d'une installation éolienne ou solaire en dessous de ce que permettraient
le vent ou l'ensoleillement. Elle peut être demandée par le gestionnaire de réseau, pour une
contrainte locale ou pour l'équilibre entre l'offre et la demande, ou décidée par le producteur
ou son agrégateur quand le prix est négatif. Ce site distingue l'énergie écrêtée à la demande de
RTE et la production renoncée aux heures à [prix négatif](glossaire:prix-negatif), estimée par
RTE : les deux se recouvrent probablement en partie et ne s'additionnent pas. Les séries de
production observées sont nettes de ces baisses.

## Effacement {#effacement}

Baisse temporaire de la consommation d'un site par rapport à ce qu'il aurait consommé, en réponse
à un signal de prix ou à une demande du gestionnaire de réseau ; l'énergie effacée est perdue ou
reportée à d'autres heures. Un effacement peut être valorisé sur les marchés de l'énergie, sur le
mécanisme d'ajustement ou au [mécanisme de capacité](glossaire:mecanisme-capacite). Dans les
séries éCO2mix, les effacements activés sont déjà retranchés de la consommation observée. Dans le
simulateur, l'effacement est une hypothèse : la consommation ajoutée se retire aux heures les
plus tendues de l'année, comme si on les connaissait à l'avance, et l'énergie n'est pas reportée.

## Facteur d'émission moyen et marginal {#facteur-moyen-marginal}

Moyen : émissions de l'ensemble de la production (ou de la consommation, échanges compris)
rapportées à l'énergie, sur une période donnée. Marginal : variation des émissions provoquée par
une variation de la consommation, c'est-à-dire les émissions des moyens qui s'ajustent à la
marge ; il dépend de l'heure et de l'horizon retenu (exploitation à court terme, ou évolution du
parc à long terme). L'un ne remplace pas l'autre : chaque chiffre carbone du site dit lequel il
est.

## Fast-track {#fast-track}

Procédure de raccordement accéléré encadrée par la CRE
([délibération n° 2025-120 du 7 mai 2025](https://www.cre.fr/fileadmin/Documents/Deliberations/2025/250507_2025-120_Procedure_raccordement_Fast_track.pdf)),
destinée à des consommateurs de très forte puissance raccordés en 400 kV sur des sites
préalablement identifiés par l'État. La capacité que RTE bloque sur ces sites, à la demande de
l'État, est la [puissance pré-réservée](glossaire:puissance-pre-reservee).

## Garanties d'origine {#garanties-origine}

Certificat électronique attestant qu'un MWh a été produit à partir d'une source renouvelable ;
les fournisseurs s'en servent pour justifier auprès de leurs clients l'origine de l'électricité
vendue. Une garantie d'origine s'échange indépendamment de l'électricité physique, sans
contrainte d'heure : en acheter ne change pas l'électricité soutirée au réseau, ni l'heure ni le
lieu de sa production. C'est la limite que vise le [CFE 24/7](glossaire:cfe-24-7).

Source : [Directive (UE) 2018/2001](https://eur-lex.europa.eu/eli/dir/2018/2001/oj), article 19.

## Intensité carbone : production, consommation, directe, cycle de vie {#intensite-carbone}

Émissions de l'électricité rapportées à l'énergie, en grammes de CO2 (ou d'équivalent CO2, selon
la source) par kWh, sur une période. Celle de la production rapporte les émissions des centrales
françaises à leur production ; celle de la consommation retranche les émissions attribuées aux
exportations et ajoute celles des importations. En émissions directes, seule la combustion dans
les centrales compte ; sur le cycle de vie s'y ajoutent l'extraction et le transport des
combustibles et la construction des installations, et une intensité ne se compare qu'à une
intensité de même périmètre. C'est une grandeur moyenne, pas un
[facteur marginal](glossaire:facteur-moyen-marginal).

## Jours et heures PP {#plages-pp}

Jours de tension de l'hiver, de novembre à mars, que RTE signale la veille pour le lendemain, et
heures de ces jours, sur lesquels se mesure la disponibilité des capacités du
[mécanisme de capacité](glossaire:mecanisme-capacite). Dans le mécanisme d'origine, les jours PP1
servaient à calculer l'obligation des fournisseurs et les jours PP2, plus nombreux, à certifier
les capacités ; le mécanisme centralisé, depuis la période de livraison 2026-2027, n'a plus
qu'une catégorie de jours PP, 22 jours signalés entre le 1er novembre et le 31 mars (CRE,
délibération n° 2026-43). Pour la période de livraison 2026-2027, les heures PP vont de 7 h à 10 h et de
17 h à 20 h ; ce sont les « plages de pointe du mécanisme de capacité » de « Quand ? ».

Source : [RTE, Bilan prévisionnel 2025-2035, Fonctionnement du système électrique](https://assets.rte-france.com/prod/public/2026-07/2026-07-15-bilan-previsionnel-fonctionnement-systeme-electrique.pdf), p. 30, note 38.

## Mécanisme de capacité, puissance certifiée {#mecanisme-capacite}

Dispositif qui rémunère des capacités de production, de stockage ou d'effacement pour leur
disponibilité aux heures de tension de l'hiver, afin de respecter le
[critère de sécurité d'approvisionnement](glossaire:adequation) au moindre coût. Depuis la période
de livraison 2026-2027, il est centralisé : RTE contractualise le besoin par enchères, sur une
courbe de demande fixée par le ministre chargé de l'énergie, et le coût est réparti entre les
consommateurs par une taxe ; auparavant, chaque fournisseur devait détenir des garanties de
capacité à hauteur de la consommation de ses clients aux jours de pointe. La puissance certifiée
d'une capacité est sa contribution reconnue à la sécurité d'approvisionnement : pour un moyen
pilotable, sa disponibilité moyenne aux [heures PP](glossaire:plages-pp) multipliée par un
coefficient de filière (égal à 1 pour le thermique à flamme, inférieur à 1 pour le nucléaire ou le
fil de l'eau) ; pour l'éolien et le solaire, sa puissance installée multipliée par un coefficient
bien plus faible ; pour un stockage ou un effacement, un coefficient de plus tient compte de la
durée pendant laquelle il peut tenir. Des GW certifiés ne sont donc ni des GW installés, ni des GW de marge au
sens du critère.

Source : [RTE, Mécanisme de capacité, rapport de paramétrage de la période de livraison 2026/2027](https://assets.rte-france.com/prod/public/2026-02/2026-02-12-rapport-parametrage-mecanisme-capacite.pdf), p. 5 et 10.

## Monotone {#monotone}

Courbe des valeurs d'une grandeur sur une période, souvent les heures d'une année, classées de la
plus élevée à la plus basse : en abscisse le rang ou le nombre d'heures, en ordonnée la valeur. On
y lit pendant combien d'heures la grandeur dépasse un niveau donné, au prix de la chronologie :
deux points voisins sur la monotone peuvent être séparés de plusieurs mois. Sur ce site, la
monotone de la [charge résiduelle](glossaire:charge-residuelle) a son rang 1 à l'heure la plus
tendue.

## MW et MWh {#mw-mwh}

Le MW mesure une puissance, un débit d'énergie à un instant ; le MWh mesure une énergie, une
puissance maintenue pendant une durée (1 MW pendant une heure donne 1 MWh ; 1 TWh vaut un million
de MWh). Une série au pas de 30 minutes exprimée en MW se somme en MWh avec un facteur 0,5.

## Nucléaire disponible non produit {#nucleaire-disponible-non-produit}

À une heure donnée, écart entre la puissance nucléaire qu'EDF déclare disponible (publications
[REMIT](glossaire:remit)) et la production nucléaire observée par RTE, ramené à zéro s'il est
négatif. C'est une borne haute de ce que le parc aurait pu produire en plus à cette heure, à
frontière donnée entre « indisponible » et « modulé », fixée par EDF : en réintégrant les arrêts
courts qu'EDF déclare indisponibles pour modulation, l'écart est plus grand ; à l'inverse, tout ce
qui est déclaré disponible n'est pas mobilisable à toute heure, et le combustible limite
l'énergie sur l'année.

## Poste électrique, poste source {#poste-electrique}

Installation du réseau où se rejoignent des lignes, avec des transformateurs et des appareils de
coupure ; un grand consommateur se raccorde soit à un poste du [réseau de transport](glossaire:rpt),
soit au [réseau de distribution](glossaire:rpd). Le poste source est le poste de transformation
qui alimente le réseau de distribution (HTA) à partir du réseau de transport (HTB). La puissance
qu'un poste peut accueillir en consommation dépend de ses transformateurs, des lignes qui
l'alimentent et de ce qui y est déjà raccordé ou réservé.

## PPA (contrat d'achat de long terme) {#ppa}

Contrat d'achat d'électricité de long terme (*power purchase agreement*) entre un producteur et un
consommateur ou un fournisseur, adossé à une ou plusieurs installations, à prix fixe ou indexé,
sur plusieurs années. Il est dit physique quand l'électricité est livrée au périmètre d'équilibre
de l'acheteur, financier (ou virtuel) quand elle est vendue sur le marché et que les parties
règlent l'écart entre le prix du contrat et le prix de marché. Le profil livré (production réelle
de l'installation, ruban constant, forme horaire) décide de qui porte les risques de volume et de
prix. Un PPA renouvelable s'accompagne en général du transfert des
[garanties d'origine](glossaire:garanties-origine) ; il ne change pas l'électricité physiquement
soutirée par l'acheteur.

## Préséance économique (merit order) {#merit-order}

Classement des offres de production par prix croissant, qui suit en première approximation le
coût variable de chaque moyen (combustible, CO2) : renouvelables et nucléaire en bas, centrales
fossiles en haut. Sur un marché à prix uniforme comme l'enchère [day-ahead](glossaire:day-ahead),
le prix d'une zone est fixé, en première approximation, par la dernière offre retenue pour
couvrir la demande. En pratique, les offres intègrent aussi des contraintes techniques
(démarrage, rampes), la valeur de l'eau stockée et des coûts d'opportunité, et le couplage des
zones fait dépendre le prix d'une zone des offres de ses voisines : le moyen « marginal » d'une
heure ne s'observe pas directement. RTE parle d'« ordre de préséance économique ».

## Prix capté (capture price) {#capture-price}

Prix moyen de marché pondéré par la production d'une filière ou d'une installation sur une
période : somme, pas de temps par pas de temps, du prix multiplié par l'énergie produite, divisée
par l'énergie produite. Rapporté au prix moyen simple de la période, il donne le taux de captage
(*capture rate*), inférieur à 1 pour une filière qui produit surtout quand les prix sont bas,
comme le solaire aux heures de surplus. Le résultat dépend du prix de référence, en général le
prix [day-ahead](glossaire:day-ahead) de la zone, et du traitement des heures à prix négatif où
l'installation s'arrête.

## Prix day-ahead {#day-ahead}

Prix de l'enchère journalière européenne couplée (SDAC, *Single Day-Ahead Coupling*), dont le
guichet ferme la veille à midi, heure de Paris, pour chaque période du lendemain ; ce site retient
le prix de la zone de prix France. L'algorithme commun apparie les offres de toutes les zones
couplées sous la contrainte des capacités d'échange : quand aucune contrainte n'est active entre
deux zones, elles ont le même prix. Le pas est horaire jusqu'au 30 septembre 2025 et de quinze
minutes depuis le 1er octobre 2025 ; ce site prend alors pour prix d'une heure la moyenne simple
de ses quatre quarts d'heure, comme RTE. Les séries viennent de Bundesnetzagentur / SMARD.de, via
energy-charts.info (Fraunhofer ISE).

## Prix de gros {#prix-de-gros}

Prix auquel l'électricité s'échange entre acteurs du marché (producteurs, fournisseurs,
négociants, grands consommateurs), en bourse ou de gré à gré, pour des livraisons qui vont de
plusieurs années à l'avance (marchés à terme) au temps réel (infrajournalier, ajustement). Il ne
comprend ni l'utilisation des réseaux ([TURPE](glossaire:turpe)), ni les taxes, ni la marge des
fournisseurs, qui s'y ajoutent dans le prix de détail. Sur ce site, « prix de gros » sans autre
précision désigne le prix [day-ahead](glossaire:day-ahead) de la zone France.

## Prix négatif {#prix-negatif}

Prix [day-ahead](glossaire:day-ahead) strictement inférieur à zéro : le vendeur paie pour
injecter, l'acheteur est payé pour soutirer. Il apparaît quand une production peu sensible au
prix (installations à tarif d'achat, contraintes techniques de démarrage et d'arrêt,
cogénérations, moyens dont l'arrêt coûterait plus que de produire à perte) dépasse ce que la
consommation, le stockage et les exportations absorbent. Ce site compte une heure comme négative
quand son prix est strictement inférieur à zéro ; un prix nul n'est pas négatif, et depuis le
passage au quart d'heure, une heure peut contenir des quarts d'heure négatifs sans l'être en
moyenne.

## PTF {#ptf}

Proposition technique et financière : offre du gestionnaire de réseau qui décrit la solution de
raccordement, son coût et son délai. Son acceptation, avec le versement du premier acompte, fait
entrer le projet dans la file d'attente et réserve la capacité.

## Puissance appelée {#puissance-appelee}

Puissance effectivement soutirée au réseau, à un instant donné ou en moyenne sur une période
(l'énergie consommée divisée par la durée ; sur un an, 8 760 heures, 8 784 en année bissextile).
Des puissances de ce glossaire, c'est la seule qui mesure une consommation.

## Puissance pré-réservée (fast-track) {#puissance-pre-reservee}

Capacité que RTE réserve, à la demande de l'État, sur un site identifié, avant qu'un porteur de
projet ne s'y engage. Elle est temporaire.

## Puissance raccordée {#puissance-raccordee}

Puissance de raccordement des installations effectivement raccordées : la puissance maximale
qu'elles peuvent soutirer au réseau selon leur contrat. Une capacité, pas une consommation.

## Puissance recherchée {#puissance-recherchee}

Puissance électrique que des porteurs de projets déclarent rechercher, telle que l'État l'annonce
pour les projets qu'il accompagne. Aucune définition publiée ; ce n'est ni un droit d'accès au
réseau ni un engagement.

## Puissance réservée {#puissance-reservee}

Capacité d'accès au réseau réservée par le gestionnaire pour un projet, une fois sa proposition
technique et financière ([PTF](glossaire:ptf)) acceptée et le premier acompte versé. C'est un droit
d'accès, avec une place dans la file d'attente ; il n'engage pas à consommer et peut être
abandonné. À ne pas confondre avec la [puissance signée](glossaire:puissance-signee), celle du
contrat de raccordement.

## Puissance signée {#puissance-signee}

Puissance de raccordement inscrite dans le contrat de raccordement, avec un calendrier de mise à
disposition, souvent par paliers. Ce n'est pas une date de mise en service de l'installation.

## REMIT {#remit}

Règlement (UE) n° 1227/2011 concernant l'intégrité et la transparence du marché de gros de
l'énergie, modifié en 2024 par le règlement (UE) 2024/1106. Il interdit les opérations d'initié et
les manipulations de marché, et oblige les acteurs à rendre publiques, de manière effective et en
temps utile, les informations privilégiées, dont les indisponibilités, planifiées ou fortuites, de leurs installations. Ce site
utilise les déclarations qu'EDF publie à ce titre pour reconstituer, heure par heure, la
puissance nucléaire déclarée disponible ; la frontière entre « indisponible » et « modulé » y est
fixée par EDF.

Source : [Règlement (UE) n° 1227/2011](https://eur-lex.europa.eu/eli/reg/2011/1227/oj), article 4.

## RPD {#rpd}

Réseau public de distribution : moyenne et basse tension (HTA et BT, jusqu'à 50 kV), exploité par
Enedis sur l'essentiel du territoire métropolitain et par des entreprises locales de distribution
ailleurs. Il est alimenté par le réseau de transport dans les
[postes sources](glossaire:poste-electrique).

## RPT {#rpt}

Réseau public de transport d'électricité : haute et très haute tension (HTB, au-delà de 50 kV),
exploité par RTE. Il relie les grands moyens de production, les interconnexions avec les pays
voisins, les postes sources et les plus grands consommateurs.

## S3REnR {#s3renr}

Schéma régional de raccordement au réseau des énergies renouvelables : élaboré par RTE avec les
gestionnaires de réseau de distribution, région par région, il identifie les ouvrages à renforcer
ou à créer pour accueillir la production renouvelable prévue et lui réserve des capacités
d'accueil. Les producteurs qui s'y raccordent paient, en plus de leur raccordement, une quote-part
par MW qui mutualise le coût de ces ouvrages. Il porte sur l'injection de production, pas sur le
soutirage : ses capacités réservées ne s'adressent pas aux consommateurs.

## Services système {#services-systeme}

Réserves de puissance que RTE se procure auprès des producteurs, des stockages et des effacements
pour maintenir en permanence la fréquence et la tension : réglage primaire de fréquence (FCR),
réglage secondaire (aFRR) et réglage de la tension. Une puissance réservée à ces services ne peut
pas être vendue en énergie : un groupe qui en porte une part ne produit pas à sa pleine puissance
disponible. C'est l'une des raisons pour lesquelles une partie du nucléaire disponible et non
produit n'est pas mobilisable, dans « Quand ? » et dans le simulateur.

## Solde des échanges {#solde-echanges}

Différence, sur un pas de temps, entre les flux physiques importés et exportés aux
interconnexions de la France avec ses voisins. Dans les séries éCO2mix de RTE qu'utilise ce site,
il est positif quand la France importe et négatif quand elle exporte. Ce sont des flux physiques
mesurés : frontière par frontière, ils diffèrent des échanges commerciaux issus des marchés, une
partie des flux transitant par un pays sans y être vendue.

## TURPE {#turpe}

Tarif d'utilisation des réseaux publics d'électricité, fixé par la CRE pour plusieurs années et
payé par les utilisateurs raccordés au réseau de transport comme au réseau de distribution. Pour
un consommateur, il comprend notamment une part liée à la puissance souscrite et une part liée à
l'énergie soutirée, différenciées selon le domaine de tension et selon la saison ou l'heure. Il
rémunère l'usage du réseau, pas le raccordement, facturé à part, et s'ajoute au
[prix de gros](glossaire:prix-de-gros) dans ce que paie le consommateur final.

## Zone de mutualisation (consommation) {#zone-mutualisation}

Zone où RTE dimensionne des ouvrages du réseau de transport pour raccorder plusieurs
consommateurs ou postes de distribution, et en répartit le coût entre eux par une quote-part par
MW de puissance de raccordement demandée (code de l'énergie, articles L. 342-2 et L. 342-18 ; décret
n° 2024-524 du 7 juin 2024). RTE en publie la carte et, pour chaque zone, la capacité d'accueil en
soutirage offerte, la part déjà attribuée aux projets entrés en file d'attente et le reste. Ces
capacités portent sur des ouvrages à construire ou à renforcer, pas sur le réseau existant. C'est
le pendant, côté consommation, des [S3REnR](glossaire:s3renr).

Source : [RTE Services, zones de mutualisation et capacités d'accueil pour la consommation](https://www.services-rte.com/fr/decouvrez-nos-offres-de-service/consulter-la-localisation-des-zones-de-mutualisation-et-les-capacites-daccueil-pour-la-consommation.html).
