---
titre: Ce qu'on peut en dire, à ce jour
mise_a_jour: 2026-11-26
version: 2
repose_sur: les quatre enquêtes et le Bilan prévisionnel 2025 de RTE
---

<!--
Message principal du site, sur l'accueil. Choix de l'auteur (option A de
docs/EDITO.md, 26/11/2026) : message tranché, explicitement prudent sur
les enquêtes qui manquent, révisé à la fin des enquêtes suivantes, daté,
et qui dit ce qui a changé (BACKLOG.md). Version 1 réécrite après la
relecture adverse docs/relectures/2026-11-26-message-en-bref.md
(ERREURS.md) ; version 2 après « Quel carbone ? » et « Où ? ».
Trois sections, dans cet ordre, contrôlées par le site :
- « À retenir » : un paragraphe court, en tête de l'accueil ;
- « Le message en détail » : replié sur l'accueil ;
- « Ce qui a changé » : une entrée par version, datée.
Même syntaxe que les enquêtes : {{id}} = chiffre du référentiel avec sa
note ; les nombres en clair sont des calculs expliqués dans la phrase
(dans « Le message en détail »).
-->

## À retenir

**Moins une question d'énergie annuelle que de pointe d'hiver, d'heure
et de lieu.** Les data centers pèsent peu dans la consommation
d'électricité de l'année. À la pointe, chaque GW consommé en permanence
retire à peu près autant à la [marge de sécurité](glossaire:adequation)
de l'hiver (inférence de ce site), que RTE évaluait à
{{marge_rte_hiver_2026_2027}} pour 2026-2027, avant la baisse de
disponibilité nucléaire prévue cet hiver. Avec ses propres
trajectoires, data centers compris, et ses hypothèses de référence, RTE
ne trouve pas de besoin de moyens nouveaux d'ici 2035 en décarbonation
lente, et un besoin de {{besoin_capacites_rapide_2035}} en 2035 en
décarbonation rapide, selon le rythme des renouvelables. Aux heures de surplus, le
nucléaire disponible et non produit ne servirait qu'environ la moitié,
au plus, d'une consommation plate de 5 GW ; le
carbone d'une consommation ajoutée n'est pas connu ; et, hors de
quelques zones où RTE renforce le réseau pour plusieurs clients, les
données publiques ne disent pas à quel poste il reste de la place.

## Le message en détail

**Moins une question d'énergie annuelle qu'une question de pointe
d'hiver.** En 2024, les data centers des sites dédiés ont consommé
{{dc_conso_sites_dedies_2024}}, de l'ordre de 1 % de la consommation
brute ({{conso_brute_france_2024}}). Pour ces mêmes sites, les deux
trajectoires de référence du Bilan prévisionnel 2025 de RTE vont de
{{traj_bp2025_lente_2035}} à {{traj_bp2025_rapide_2035}} en 2035, soit
environ 5 à 7 % de la consommation de 2024. Elles supposent qu'une
partie seulement des projets se concrétise, et que les sites
n'utilisent qu'une fraction de leur puissance de raccordement ; la
puissance réservée auprès de RTE en mai 2026, près de
{{dc_reserve_rte_2026_05}}, n'engage pas à consommer.

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

Aux heures de surplus, l'abondance ne suffit pas non plus. Avec les
données de 2025 et la disponibilité déclarée par EDF,
{{quand_part_j_5gw_2025}} au plus de l'énergie d'une consommation plate
de 5 GW aurait trouvé du nucléaire disponible et non produit
({{quand_part_j_plancher_5gw_2025}} en supposant 1 GW non mobilisable à
toute heure, hypothèse de ce site). EDF déclare aussi comme
indisponibilités des arrêts courts « pour modulation », décidés pour des
raisons économiques ; en les réintégrant, ces parts montent à
{{quand_part_j_reintegre_5gw_2025}} et
{{quand_part_j_plancher_reintegre_5gw_2025}} : le plafond dépend de la
frontière, fixée par EDF, entre indisponible et modulé. Il faudrait alors produire
{{quand_energie_j_5gw_2025}} à {{quand_energie_j_reintegre_5gw_2025}} de
nucléaire en plus sur l'année, pour un parc qui a produit
{{prod_nucleaire_2025}} en 2025 et dont l'exploitant prévoit
{{prod_nucleaire_prevision_2026_2027}} par an pour 2026-2027 ; le reste
viendrait d'autres moyens, de renouvelables moins arrêtés ou
d'exportations en moins.

À l'échelle nationale, la contrainte la plus nette est donc la pointe
d'hiver. Dans la trajectoire lente, RTE n'y voit pas de besoin de
moyens nouveaux d'ici 2035 ; dans la trajectoire rapide, il en voit un
de quelques GW, qui dépend surtout du nucléaire et des renouvelables.
Au-delà de ces trajectoires, chaque GW consommé en permanence entame la
marge : c'est là que se poserait la question de l'effacement des data
centers aux heures de pointe, ou de moyens nouveaux.

Le carbone ne tranche pas non plus, faute de chiffre. L'intensité
moyenne de l'électricité française est basse, mais elle répartit des
émissions qui ont eu lieu ; elle ne dit pas ce qu'une consommation
ajoutée ferait émettre, en France ou chez les voisins dont elle
réduirait les importations. Ce facteur marginal, RTE et l'ADEME en
ont publié une estimation en 2007, puis ont jugé l'approche inadaptée
aux gros volumes et lui préfèrent des comparaisons de scénarios
([« Quel carbone ? »](/carbone)).

Et la question se joue aussi au poste électrique, où les données
publiques s'arrêtent vite. Elles disent combien de puissance RTE a
allouée aux projets de consommation, région par région, et, pour
quelques zones où il renforce le réseau pour plusieurs clients, la
capacité d'accueil qu'il y crée et ce qu'il en reste ; ailleurs, elles
ne disent pas à quel poste il reste de la place pour une consommation
de plusieurs centaines de mégawatts. RTE a compté environ {{sddr_postes_250mw}} du réseau à
400 kV capables d'accueillir un projet d'environ 250 MW, sans en
publier la liste ([« Où ? »](/ou)).

**Ce que ce message ne dit pas encore.** Il repose sur quatre enquêtes
et sur les calculs de RTE. Plusieurs questions restent ouvertes et
peuvent le nuancer, voire le contredire : le réseau local, que les
données publiques ne permettent d'examiner que dans quelques zones ; le
profil réel des
data centers (aucune courbe de charge n'est publiée, et leur capacité à
baisser leur consommation aux heures de pointe n'est pas connue) ; les
hypothèses des trajectoires elles-mêmes (part des projets qui se
concrétisent, taux d'utilisation de la puissance raccordée) ; les
voisins (qui servirait la consommation ajoutée aux heures de surplus :
nucléaire, renouvelables moins arrêtés ou exportations en moins) ; le
carbone marginal, dont aucune institution ne publie d'estimation
récente à notre connaissance, et que ce site ne sait
pas encore estimer ; et le prix (ce que coûtent l'effacement et les
moyens nouveaux, et qui les paie). Ce message sera revu à mesure que ces
questions avancent.

## Ce qui a changé

- **Version 2, 26 novembre 2026, au soir**, après « Quel carbone ? » et
  « Où ? » : un paragraphe « À retenir » en tête, prolongé sur l'accueil
  par un chiffre fort par enquête ; deux paragraphes sur le
  carbone et sur le poste électrique ; la liste des questions ouvertes
  mise à jour (le réseau local et le carbone marginal sont maintenant
  documentés comme des manques). Une conclusion de la version 1 est
  corrigée : elle disait que personne ne publie ce que peut recevoir un
  poste électrique ; RTE le publie pour quelques zones où il renforce le
  réseau pour plusieurs clients (making-of, erreurs du 26/11). Aucun
  chiffre de la version 1 ne change.
- **Version 1, 26 novembre 2026**, après « Combien ? » et « Quand ? » :
  premier message, choisi par l'auteur parmi trois options
  (making-of, décisions du 26/11).
