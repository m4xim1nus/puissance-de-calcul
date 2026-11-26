---
titre: Où ?
question: Où le réseau électrique français peut-il accueillir des data centers, et que permettent d'en savoir les données publiques ?
mise_a_jour: 2026-11-26
accroche: Environ {{sddr_postes_250mw}} du [réseau de transport](glossaire:rpt) à 400 kV pouvaient accueillir un projet d'environ 250 MW, selon RTE en 2025, qui n'en publie pas la liste. La carte des zones favorables qu'il annonçait en février 2025 n'est pas parue au 26 novembre 2026, à notre connaissance.
---

<!--
Syntaxe propre au site : voir docs/enquetes/combien.md.
Aucun nombre issu d'une source n'est tapé à la main dans ce fichier. Restent
en clair : des dates, des noms de catégories définis par les sources (projets
« de l'ordre de 250 MW » ou « de 750 MW », « environ 1 GW » de RTE, réseau à
400 kV), et les
noms des cinq sites « fast-track », comptés dans le chiffre
dc_fasttrack_prereserve_2025_12.
Enquête courte : elle dit ce qui manque pour répondre à la question, et ce qui
est publié malgré tout. Les constats d'absence sont datés du 26/11/2026 et
reposent sur une recherche non exhaustive (rapport de l'agent :
docs/relectures/2026-11-26-ou-agent.md).
-->

[« Combien ? »](/combien) et [« Quand ? »](/quand) regardent le système
électrique national. Un data center, lui, se raccorde à un poste précis : à
quel poste reste-t-il de la place pour soutirer plusieurs centaines de
mégawatts, et à quelle date ? Cette enquête courte montre qu'on ne peut
pas le dire avec les données publiques, ce qui manque, et ce qui est
publié malgré tout.

**Ce qu'on en retient.** Dans son schéma décennal de 2025, RTE a compté
environ {{sddr_postes_250mw}} du réseau à 400 kV capables d'accueillir un
projet de consommation de l'ordre de 250 MW, et environ
{{sddr_postes_750mw}} pour un projet de l'ordre de 750 MW. Il n'en a
publié ni la liste ni la carte, annoncée en février 2025 « dans les
prochaines semaines ». Au 26 novembre 2026, à notre connaissance, RTE ne
publie de capacité d'accueil pour une nouvelle consommation que dans
{{orrem_zones_2026_11}} de [mutualisation](glossaire:zone-mutualisation),
où il construit des ouvrages partagés entre plusieurs clients, et zone par
zone, non poste par poste ; ailleurs, rien n'est publié. La liste ouverte des
postes de RTE ne donne plus leurs coordonnées, et aucun registre public ne
situe les data centers. Le reste tient en des totaux régionaux et cinq
sites choisis par l'État. Ce site ne dessine donc pas de carte des
capacités d'accueil : les données publiques n'en couvrent que ces zones.

## Poste par poste, la capacité publiée est celle de la production

Les outils publics qui donnent une capacité d'accueil poste par poste
portent sur la production et sur le stockage. Caparéseau s'intitule
« Capacités d'accueil en production du réseau »
{{source:capareseau|page d'accueil}}. Cartostock, selon la CRE, « permet de
consulter et de télécharger la capacité d'accueil maximale disponible pour
une installation de stockage sur chaque poste concerné, sans limitation »
{{source:cre-2026-173|p. 3, note 7}} ; RTE la publie sur son site Analyses
et données {{source:rte-cartostock|page « Capacités de raccordement des batteries »}}.
Les schémas régionaux de raccordement au réseau des énergies
renouvelables (S3REnR) réservent eux aussi de la capacité à la
production. Une marge pour injecter, ou pour une batterie, ne dit pas la
marge pour une consommation de plusieurs centaines de mégawatts.

Côté consommation, RTE a annoncé une carte. Dans la fiche de son schéma
décennal consacrée au raccordement de l'industrie, en février 2025, il
écrivait : « RTE mettra à disposition dans les prochaines semaines une
cartographie des zones favorables pour des projets industriels d'une
puissance de l'ordre de 250 MW et de l'ordre de 750 MW ». Ces zones sont
celles où existe un poste à très haute tension et où l'on peut « consommer
à pleine puissance sans besoin de renforcement du réseau 400 kV ou via des
aménagements légers ». À l'emplacement de la carte, la figure du document
montre un fond de carte grisé du réseau et la mention « La carte avec les
zones du réseau 400 kV favorables à l'accueil de puissance de forte
consommation sera publiée dans les prochaines semaines »
{{source:rte-sddr2025-fiche5|p. 4 du PDF, folio 47, figure 5.2}}. Le
rapport complet de juin 2025 reproduit la même figure
{{source:rte-sddr2025-rapport|p. 49 et 54}}. Seule la synthèse chiffre ces
zones, par les deux comptes cités plus haut
{{source:rte-sddr2025-synthese|p. 19, figure 5}}. Nous n'avons trouvé
cette carte ni sur les sites de RTE, ni dans les documents publiés depuis
sur le schéma décennal.

En juillet 2026, la Commission de régulation de l'énergie (CRE) écrivait
que RTE « étudie la publication d'une cartographie plus détaillée des
capacités en soutirage sur son réseau », qu'elle y était favorable, et
qu'une telle carte donnerait des informations « plus précises que l'outil
“Toprac” », lequel « informe sur les puissances allouées par RTE en vue du
raccordement d'installations en projet » {{source:cre-2026-173|p. 3}}.
Toprac est public : il donne ces puissances par région et par type de
projet (production, consommation, stockage), pas par poste
{{source:rte-toprac|page « Projets en cours de raccordement »}}. La même
délibération demande à RTE de refondre Caparéseau d'ici le 1er janvier 2027
{{source:cre-2026-173|p. 8}}.

Le droit européen va dans ce sens. Depuis juillet 2024, les gestionnaires
de réseau de transport doivent publier « des informations sur la capacité
disponible pour de nouveaux raccordements dans leurs zones d'exploitation,
avec une granularité spatiale élevée, dans le respect de la sécurité
publique et de la confidentialité des données, y compris la capacité
faisant l'objet d'une demande de raccordement », et les mettre à jour « au
moins une fois par mois »
{{source:ue-2024-1747|article 1er, point 13, qui insère le § 4 bis de l'article 50 du règlement (UE) 2019/943}}.
Le texte parle de nouveaux raccordements sans les limiter à la
production, et son considérant 50 vise « les nouvelles installations de
production et de demande » {{source:ue-2024-1747|considérant 50}}. La
Commission juge « essentiel » d'en publier la capacité « tant pour la
charge que pour la production » {{source:ue-c-2025-6703|§ 2.2.1, p. 7}}.
Ni RTE ni la CRE n'ont écrit, à notre connaissance, comment cette
obligation est remplie pour la consommation hors des zones de
mutualisation.

Côté distribution, Enedis met à la disposition des entreprises
et des collectivités, dans leur espace client, une carte des capacités
disponibles pour les petits raccordements en basse tension
{{source:enedis-nmo-rac-005e|p. 12, § 6.2}}. Elle ne concerne pas des data
centers de plusieurs dizaines de mégawatts.

## Les postes sont listés, pas situés

RTE publie en données ouvertes la liste de ses sites électriques et
points de piquage : {{odre_postes_rte_2026_06}}, avec leur code, leur nom,
leur tension et leur département. Les coordonnées n'y figurent plus : RTE
« a fait évoluer l'accès aux données GPS des infrastructures du réseau
public de transport pour des raisons de sécurité publique » et « travaille
à des solutions alternatives ». Les jeux des lignes aériennes et
souterraines n'ont pas non plus de tracé
{{source:odre-lignes-rte|champs des jeux ODRÉ}}. Avec ce jeu, on peut
compter les postes par département et par tension, pas les placer sur une
carte ; il faut pour cela d'autres sources, non officielles
(OpenStreetMap par exemple), que RTE ne valide pas.

## Aucun registre public des data centers

La directive européenne sur l'efficacité énergétique oblige l'exploitant
de tout data center d'au moins {{ue_eed_seuil_dc}} de puissance
informatique installée à rendre publiques, chaque année, des informations
dont « le nom du centre de données, le nom du propriétaire et des
exploitants du centre de données, la date à laquelle le centre de données
a entamé ses activités et la commune où le centre de données est établi »,
ainsi que sa puissance installée, sauf secret des affaires
{{source:ue-2023-1791|annexe VII, points a et b}}. La base européenne qui
rassemble ces déclarations n'est publique qu'agrégée, par État membre et
pour l'Union ; la Commission et les États « préservent la confidentialité »
des informations de chaque centre
{{source:ue-2024-1364|article 5, paragraphes 2 et 5}}.

En France, le décret du 29 décembre 2025 demande à l'exploitant de publier
ces informations sur sa propre page internet, « dans un format ouvert et
structuré », et d'en transmettre l'adresse à l'ADEME. Ces adresses doivent
« ensuite » être publiées « sur un registre numérique national mis en place
par l'Etat ou un opérateur de l'Etat »
{{source:decret-2025-1382|article 8, article D. 236-3 du code de l'énergie, p. 6}}.
Nous n'avons pas trouvé ce registre en ligne au 26 novembre 2026.
L'information existe donc en principe, site par site, dispersée chez
chaque exploitant, sans liste publique pour la retrouver.

La statistique publique ne situe les data centers qu'au département, par
classes de consommation. En 2024, {{sdes_departements_classe_haute_2024}}
étaient dans la classe la plus haute du SDES : le Nord, l'Essonne, les
Hauts-de-Seine et la Seine-Saint-Denis.

## Ce qui est publié : des régions, des sites, des zones

**Des totaux régionaux.** Toprac donne, région par région, la puissance
allouée aux projets de consommation qui ont accepté une proposition
technique et financière de RTE, tous usages confondus : au 30 juin 2026,
{{toprac_conso_idf_2026_06}} en Île-de-France et
{{toprac_conso_hdf_2026_06}} dans les Hauts-de-France, sur
{{toprac_conso_2026_06}} pour la France. Pour les seuls data centers, RTE
attribue, sur sa page qui leur est consacrée, environ
{{dc_reserve_idf_2026}} de capacité réservée à l'Île-de-France et environ
{{dc_reserve_hdf_2026}} aux Hauts-de-France, les deux « territoires qui
concentrent la majorité des projets », sans dater ces deux chiffres. Le
total national de la même page est de près de
{{dc_reserve_rte_2026_05}} en mai 2026. Pour l'Île-de-France, le bilan
régional de RTE donne {{dc_raccorde_idf_2025_12}} de data centers déjà
raccordés fin 2025, sur les {{dc_raccorde_rpt_2025_12}} raccordés au
réseau de transport dans toute la France, et {{dc_en_cours_idf_2026}} de
raccordements « en cours ». La page web de RTE parle aussi, pour
l'Île-de-France, de « puissance demandée ». Réservée, en cours, demandée :
RTE emploie pour la même région des mots différents ; seul « en cours » a
une définition publiée, celle de Toprac (proposition acceptée), et rien ne
dit que le bilan régional l'emploie dans ce sens. Ces chiffres ne
s'additionnent pas. Les étages de puissance sont définis dans
[« Combien ? »](/combien).

**Des sites choisis par l'État.** L'État dit avoir identifié
{{dc_sites_identifies_etat}} propices aux data centers ; la page de RTE en
compte {{dc_sites_propices_rte}}. La liste n'est pas publiée : le guide de
l'État n'en montre qu'une carte par région, sans nom. Le schéma décennal
comptait {{sddr_sites_1gw}} capables d'accueillir rapidement un projet
d'environ 1 GW, sans les nommer. Seuls sont nommés les sites de la
procédure de raccordement accéléré dite « fast-track », approuvée par la
CRE le 7 mai 2025 : Fouju et Montereau en Seine-et-Marne, Escaudain et
Bourbourg dans le Nord, Le Bosquel dans la Somme. Ils disposent, écrit
RTE, « d'une grande surface foncière à proximité du réseau 400 000 volts »
et permettent « d'offrir rapidement une forte puissance sans restriction
de soutirage » {{source:rte-sddr-reponse-cpdp-2026|p. 20}}. RTE y avait
pré-réservé {{dc_fasttrack_prereserve_2025_12}} à la demande de l'État en
décembre 2025 ; en juillet 2026, il annonçait le lancement, d'ici la fin
de l'année, du raccordement « fast track » de cinq grands projets de data
centers {{source:rte-bilan-s1-2026|p. 16 du PDF}}.

**Des zones où RTE construit ou prévoit de la capacité.** Dans une zone de
mutualisation, RTE construit, ou prévoit de construire, le réseau pour plusieurs futurs clients et
répartit le coût entre eux par une quote-part par mégawatt. Il en publie
la carte et les données : {{orrem_zones_2026_11}}, à divers stades
(validées par la CRE, partagées avec elle, à l'étude ou en surveillance),
avec pour chacune la capacité d'accueil en soutirage offerte, la part déjà
attribuée aux projets entrés en file d'attente, le reste disponible et la
liste des postes concernés
{{source:rte-zones-mutualisation-2026-11|fichier du 10 novembre 2026}}.
Dans le sud de l'Île-de-France, la zone offre
{{orrem_idf_sud_offerte_2026_11}}, pour une fin de travaux prévue en
septembre 2031, et il en reste {{orrem_idf_sud_residuelle_2026_11}} :
tout est déjà attribué. À Plan-de-Campagne, entre Aix-en-Provence et
Marseille, il reste {{orrem_plan_campagne_residuelle_2026_11}} sur
{{orrem_plan_campagne_offerte_2026_11}}. Ce sont des capacités sur des
ouvrages à construire, pas sur le réseau d'aujourd'hui.

## Qui passe en premier : une règle en cours de refonte

Aujourd'hui, une demande entre dans la file d'attente de RTE quand le
demandeur accepte la proposition technique et financière, avec un
justificatif de maîtrise foncière, une preuve d'avancement du projet ou à
défaut une somme forfaitaire par mégawatt, et un premier acompte ; l'ordre
d'entrée « dépend de l'ordre d'acceptation »
{{source:cre-2026-32|p. 3 et 6}}. Cette procédure est commune à la
production, au stockage et à la consommation depuis juillet 2025
{{source:cre-2025-193|p. 1}}. RTE appelle ce principe « premier demandeur,
premier servi » {{source:rte-consultation-refonte-2026|p. 6}}. La CRE lui
a demandé de la saisir au plus tard le 1er octobre 2026 d'une première
évolution « intégrant une meilleure prise en compte de la maturité des
projets » {{source:cre-2026-32|p. 6}}. En juillet 2026, RTE annonçait une
refonte « achevée d'ici la fin d'année », fondée sur le « premier prêt
premier servi », et expérimentée « dès le second semestre en
Ile-de-France » {{source:rte-bilan-s1-2026|p. 16 du PDF}}. Au
26 novembre 2026, nous n'avons pas trouvé de délibération de la CRE approuvant ces
nouvelles règles. Nous n'avons pas trouvé de publication ouverte de la
file d'attente des consommateurs poste par poste ; Toprac en donne l'état
par région, et le fichier des zones de mutualisation la capacité déjà
attribuée, zone par zone.

## Limites

- **Des absences datées.** Chaque « nous n'avons pas trouvé » vaut au
  26 novembre 2026, après une recherche non exhaustive sur les sites de
  RTE (dont Analyses et données et RTE Services), de la CRE, d'ODRÉ, de
  data.gouv.fr et d'EUR-Lex, sans les espaces clients (RTE Services,
  Enedis) et sans ouvrir le contenu des cartes interactives. Une
  publication a pu nous échapper ; nous corrigerons.
- **Des totaux régionaux inégalement définis.** Ceux de Toprac sont datés
  et définis (proposition acceptée) mais mêlent tous les consommateurs.
  Ceux de la page de RTE consacrée aux data centers ne sont pas datés ou ne
  disent pas ce qu'ils comptent. Un total régional ne dit pas qu'un poste
  de la région a de la place.
