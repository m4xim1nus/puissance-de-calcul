---
titre: Ce qu'on peut en dire, à ce jour
mise_a_jour: 2026-11-26
repose_sur: « Combien ? » et « Quand ? », et le calcul d'adéquation du Bilan prévisionnel 2025 de RTE
---

<!--
Message principal du site, affiché sur l'accueil sous la question.
Choix de l'auteur (option A de docs/EDITO.md, 26/11/2026) : message
tranché, explicitement prudent sur les enquêtes qui manquent, révisé à
la fin des enquêtes suivantes (BACKLOG.md). Réécrit après la relecture
adverse docs/relectures/2026-11-26-message-en-bref.md (ERREURS.md).
Même syntaxe que les enquêtes : {{id}} = chiffre du référentiel avec sa
note ; les nombres en clair sont des calculs expliqués dans la phrase.
-->

**Moins une question d'énergie annuelle qu'une question de pointe
d'hiver.** En 2024, les data centers des sites dédiés ont consommé
{{dc_conso_sites_dedies_2024}}, de l'ordre de 1 % de la consommation
brute ({{conso_brute_france_2024}}). Pour ces mêmes sites, les deux
trajectoires de référence du Bilan prévisionnel 2025 de RTE vont de
{{traj_bp2025_lente_2035}} à {{traj_bp2025_rapide_2035}} en 2035, soit
environ 5 à 7 % de la consommation de 2024. Elles supposent qu'une
partie seulement des projets se concrétise, et que les sites
n'utilisent qu'une fraction de leur puissance de raccordement ; les
{{dc_reserve_rte_2026_05}} de puissance réservée auprès de RTE en mai
2026 n'engagent pas à consommer.

En puissance, l'ordre de grandeur change. Dans un calcul d'adéquation,
une consommation plate de 1 GW, présente toute l'année, retire à peu
près 1 GW à la marge de sécurité d'approvisionnement : c'est une
inférence de ce site ; RTE fait le même passage pour une hausse de la
pointe, pas pour une consommation ajoutée. Cette marge n'est pas un écart qu'on
observe à une heure donnée ; RTE la calcule par simulation, et
l'évaluait à {{marge_rte_hiver_2026_2027}} pour l'hiver 2026-2027, dans
son Bilan prévisionnel 2025, avant la baisse de disponibilité nucléaire
prévue cet hiver. La hausse de consommation des data centers entre
2024 et ces trajectoires de 2035, si elle était plate, vaudrait au plus
1,9 à 3,2 GW en moyenne ((21 − 4) et (32 − 4) TWh répartis sur
8 760 heures), d'un cinquième à deux cinquièmes de cette marge : un
ordre de grandeur à système inchangé, pas un calcul d'adéquation.

Le calcul d'adéquation, RTE l'a fait, pour toute la consommation de ses
trajectoires (électrification, industrie, hydrogène, data centers). Dans
la trajectoire lente, il ne trouve aucun besoin de moyens nouveaux à la
pointe d'ici 2035 ({{besoin_capacites_lente_r3_2030_2035}}), si les
renouvelables se développent à son rythme de référence, si les
centrales thermiques existantes restent et si la disponibilité
nucléaire est médiane. Dans la trajectoire rapide, il trouve un besoin
de {{besoin_capacites_rapide_2030}} en 2030 et de
{{besoin_capacites_rapide_2035}} en 2035, qui disparaît si le nucléaire
est plus disponible ou si les renouvelables vont plus vite.

Aux heures de surplus, l'abondance ne suffit pas non plus : avec les
données de 2025, au plus {{quand_part_j_5gw_2025}} de l'énergie d'une
consommation plate de 5 GW aurait trouvé du nucléaire disponible et non
produit ({{quand_part_j_plancher_5gw_2025}} en retranchant 1 GW jamais
mobilisable) ; le reste viendrait d'autres moyens, de renouvelables
moins arrêtés ou d'exportations en moins.

À l'échelle nationale, la contrainte la plus nette est donc la pointe
d'hiver. Dans la trajectoire lente, RTE n'y voit pas de besoin de
moyens nouveaux d'ici 2035 ; dans la trajectoire rapide, il en voit un
de quelques GW, qui dépend surtout du nucléaire et des renouvelables.
Au-delà de ces trajectoires, chaque GW consommé en permanence entame la
marge : c'est là que se poserait la question de l'effacement des data
centers aux heures de pointe, ou de moyens nouveaux.

**Ce que ce message ne dit pas encore.** Il repose sur deux enquêtes
et sur les calculs de RTE. Plusieurs questions restent ouvertes et
peuvent le nuancer, voire le contredire : le réseau local (ce que peut
recevoir chaque poste électrique, que personne, à notre connaissance,
ne publie en données ouvertes) ; le profil réel des data centers (aucune
courbe de charge n'est publiée, et leur capacité à baisser leur
consommation aux heures de pointe n'est pas connue) ; les hypothèses
des trajectoires elles-mêmes (part des projets qui se concrétisent,
taux d'utilisation de la puissance raccordée) ; les voisins (qui
servirait la consommation ajoutée aux heures de surplus : nucléaire,
renouvelables moins arrêtés ou exportations en moins) ; le carbone (ce
qu'émettrait cette production, au facteur d'émission marginal,
européen dès que les exportations baissent) ; et le prix (ce que
coûtent l'effacement et les moyens nouveaux, et qui les paie). Ce
message sera revu à la fin de ces enquêtes, et la page dira ce qui a
changé.
