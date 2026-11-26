---
titre: Quand ?
question: À quelles heures le système électrique français a-t-il de la marge, à quelles heures n'en a-t-il pas, et que change une consommation continue de plus ?
mise_a_jour: 2026-11-26
---

<!--
Syntaxe propre au site : voir docs/enquetes/combien.md.
Aucun nombre issu d'une source ou d'un calcul n'est tapé à la main dans
ce fichier ; les nombres en clair sont des paramètres (X = 1, 5, 10 GW)
ou des calculs expliqués dans la phrase. Les chiffres `quand_*` sont
calculés par `pc build` (pipeline/pc/quand.py) sur les séries publiées
dans data/export/horaire/, et contrôlés par `pc check`.
Une ligne `- ::: inclure nom :::` est remplacée par docs/enquetes/partage/nom.md :
le même texte sert au simulateur (site/src/lib/simulateur/lecture.md).
-->

Un data center consomme jour et nuit. Sa consommation tombe donc aussi
bien sur les heures où le système électrique a de la marge que sur
celles où il n'en a pas. Cette enquête cherche ces heures dans les
données de 2015 à 2025, puis regarde ce qu'une consommation continue de
quelques GW y ajouterait. Elle ne modélise pas le système : elle décrit
ce qui a été observé, y ajoute une consommation fixe par un calcul
simple, et dit où l'observation s'arrête.

**Ce qu'on en retient.** Les heures tendues sont des matins et des
débuts de soirée d'hiver ; les heures de surplus, des milieux de journée
de printemps et d'été. Une consommation plate tombe sur les unes comme
sur les autres. À la pointe, elle pèse de tout son poids : X GW
consommés en permanence retirent à peu près X GW de marge, et 10 GW
correspondent à l'ordre de grandeur des marges que RTE évaluait pour
l'hiver 2026-2027. Aux heures de surplus, une partie seulement de son
énergie trouverait du nucléaire resté inemployé, et l'énergie nucléaire
annuelle qu'il faudrait alors produire dépasserait nettement ce que
l'exploitant prévoit.

## Personne ne publie une marge heure par heure

RTE répond à la question de la marge par la simulation ; ce site regarde
ce que les données observées, elles, permettent de voir. La marge dont
parle RTE n'est pas un écart qu'on lit sur une courbe.
C'est le résultat d'une simulation : des scénarios de météo et de
disponibilité des moyens de production, à l'échelle de l'Europe
interconnectée, comparés au critère public de sécurité
d'approvisionnement, une espérance de trois heures de défaillance par
an {{source:rte-bp2025-fonctionnement|p. 2}}. Dans son Bilan prévisionnel 2025, RTE
évaluait les marges de l'hiver 2026-2027 à {{marge_rte_hiver_2026_2027}}
par rapport à ce critère. Pour paramétrer le mécanisme de capacité,
RTE a retenu une marge de {{marge_mc_certifiee_2026_2027}} certifiés,
dans le scénario de décarbonation lente : une autre unité de compte, et
pas un recoupement du chiffre précédent. Ces deux chiffres datent d'avant
les hypothèses de l'hiver : la synthèse que RTE publie en novembre 2026
ne donne plus de marge en GW, seulement un risque « significativement
en dessous du critère réglementaire » {{source:rte-hiver-2026-2027|p. 15}},
avec un nucléaire disponible prévu à {{dispo_nucleaire_prevue_hiver_2026_2027}}
en moyenne de novembre à mars, contre {{dispo_nucleaire_hiver_2025_2026}}
l'hiver précédent.

Aucune série horaire publique ne donne la marge par rapport au critère. On ne peut pas la
recalculer avec des observations, et ce site ne le tente pas : une
« marge » obtenue en retranchant la consommation des capacités
installées ignorerait les stocks d'eau, les pannes et la disponibilité
réelle des importations. Ce qu'on peut faire, c'est repérer les heures
où le système a dû aller chercher le plus loin.

## Les heures tendues : l'hiver, le matin et le soir

L'indicateur retenu est une **charge résiduelle** : la consommation,
moins l'éolien et le solaire produits, moins le nucléaire **disponible**
déclaré par EDF au titre de REMIT. Le choix du nucléaire disponible, et
non du nucléaire produit, est essentiel. Le nucléaire module sa
production quand la demande est faible ; retrancher ce qu'il a produit
masquerait la puissance restée inutilisée aux heures où il a baissé sa
production. Ce qui reste après ce retranchement doit venir de
l'hydraulique, du gaz, des autres centrales thermiques, des
importations ou du stockage (les effacements activés, eux, sont déjà
retranchés de la consommation observée). L'hydraulique au fil de l'eau
n'est pas retranchée : ce choix, que d'autres définitions ne font pas,
la compte parmi ce qui couvre la charge résiduelle. Cette grandeur n'est
pas la « consommation résiduelle » des publications de RTE.

En 2025, cette charge résiduelle a culminé à {{quand_rn_max_2025}}. En
2022, année où la disponibilité du parc nucléaire est tombée à
{{dispo_nucleaire_rte_2022}}, elle avait atteint {{quand_rn_max_2022}},
puis {{quand_rn_max_2023}} en 2023 et {{quand_rn_max_2024}} en 2024.

::: graphique monotone-rn :::

Les cent heures où elle est la plus élevée sont des heures d'hiver :
{{quand_top100_hiver_2025}} entre novembre et mars en 2025,
{{quand_top100_hiver_2024}} en 2024, {{quand_top100_hiver_2023}} en 2023
et {{quand_top100_hiver_2022}} en 2022. Elles se concentrent
le matin et en début de soirée : {{quand_top100_plages_pp_2025}}
tombent entre 7 h et 10 h ou entre 17 h et 20 h (heure de Paris) en
2025, {{quand_top100_plages_pp_2024}} en 2024. Ce sont les plages de
pointe du mécanisme de capacité. Dans les simulations de RTE à moyen
terme, près de {{rte_part_defaillance_plages_pointe}} de l'énergie non
distribuée y tomberait ; l'autre moitié glisserait vers la soirée et la
nuit, à mesure que les épisodes s'allongent. Une consommation plate
pèse sur toutes ces heures.

::: graphique heatmap-rn :::

Ces heures n'ont pas la même intensité d'une année à l'autre, et ce
qui les a couvertes a changé. Pendant les cent heures les plus tendues
de 2022, la charge résiduelle valait en moyenne
{{quand_top100_rn_moyenne_2022}} et le solde des échanges de la France
{{quand_top100_solde_2022}} (positif : importateur). Pendant celles de
2025, la charge résiduelle valait en moyenne
{{quand_top100_rn_moyenne_2025}}, et le solde {{quand_top100_solde_2025}} :
la France **exportait**. Le fil de l'eau apportait
{{quand_top100_fil_eau_2025}}, l'hydraulique de lac et le turbinage des
stations de pompage {{quand_top100_lacs_step_2025}}, le gaz
{{quand_top100_gaz_2025}} ; les bioénergies, le charbon et le fioul, le
reste.

## Les heures de surplus : le printemps, l'été, le milieu de journée

À l'autre bout, il y a les heures où la production peu flexible dépasse
ce que la consommation, le pompage et les exportations absorbent à prix
positif. Le signal le plus visible est le prix
négatif : {{heures_negatives_2023}} en 2023, {{heures_negatives_2024}}
en 2024, {{heures_negatives_2025}} en 2025. Ces heures-là, des
producteurs éoliens et solaires s'arrêtent : RTE estime à
{{enr_renoncees_prix_negatifs_2025}} la production renoncée en 2025.
Les {{enr_ecretees_rte_2025}} écrêtés à la demande de RTE pour
l'équilibre entre l'offre et la demande recouvrent probablement en
partie ce chiffre : les deux ne s'additionnent pas.

Le second signal est le nucléaire disponible et non produit : la
puissance déclarée disponible par EDF, heure par heure, moins la
production nucléaire. Sur l'année, il représente {{quand_j_2023}} en
2023, {{quand_j_2024}} en 2024 et {{quand_j_2025}} en 2025 ; sans la
disponibilité déclarée de Flamanville 3, en montée en puissance cette
année-là, au moins {{quand_j_2025_hors_epr}} (sa production n'est pas séparée
dans les séries par filière utilisées ici ; elle l'est dans les données
par groupe de RTE et d'ENTSO-E, accessibles avec un compte, pas encore
branchées).
C'est le même ordre de grandeur que la modulation publiée par EDF
({{modulation_nucleaire_2023_bp}}, {{modulation_nucleaire_2024_bp}} et
{{modulation_nucleaire_2025_bp}}) ou par RTE pour 2025
({{modulation_nucleaire_2025_be}}), mais ce n'est pas la même grandeur.
La frontière entre « indisponible » et « modulé » est fixée par EDF, et
elle compte : EDF déclare indisponibles des arrêts « pour modulation »,
qui sortent de ce calcul (voir plus bas). En réintégrant ceux de moins
de sept jours, économiques, le nucléaire disponible et non produit
représente {{quand_j_reintegre_2024}} en 2024 et
{{quand_j_reintegre_2025}} en 2025. Les arrêts pour modulation plus
longs et les arrêts déclarés « pour économie de combustible » restent
retranchés dans les deux calculs. Ce site n'appelle donc ni l'un ni
l'autre « modulation ».

## Ce qu'une consommation continue de plus y changerait

Supposons une consommation supplémentaire **plate** de X GW, présente
les 8 760 heures de l'année. C'est une hypothèse, pas un profil
observé : aucune courbe de charge de data centers n'est publiée, et les
data centers déjà raccordés au réseau de transport n'utilisaient, à
la date du Bilan prévisionnel (décembre 2025), que
{{dc_taux_utilisation_rpt_2025_12}} de leur puissance de raccordement,
un chiffre que RTE donne en exemple sans en préciser le calcul. X GW consommés ne sont pas X GW réservés (voir
[« Combien ? »](/combien)).

**Aux heures de surplus**, une partie de cette énergie trouverait du
nucléaire disponible et non produit. Avec les données de 2025, ce
serait au plus {{quand_part_j_5gw_2025}} de l'énergie pour 5 GW et
{{quand_part_j_10gw_2025}} pour 10 GW, avec la disponibilité déclarée
par EDF ; {{quand_part_j_reintegre_5gw_2025}} et
{{quand_part_j_reintegre_10gw_2025}} en réintégrant les arrêts courts
qu'EDF déclare indisponibles pour modulation (voir plus bas). Le plafond
avec la disponibilité déclarée est lâche. Même aux
heures les plus chères, le nucléaire disponible non produit reste le
plus souvent au-dessus de zéro : en 2025, il valait encore en moyenne
{{quand_j_heures_cheres_2025}} aux heures où le prix dépassait
150 €/MWh. Une part de ce « reste » n'est pas mobilisable (réserves de
services système, rampes, fins de cycle). En retranchant 1 GW à toute
heure, un ordre de grandeur choisi par ce site, les parts tombent à
{{quand_part_j_plancher_5gw_2025}} et {{quand_part_j_plancher_10gw_2025}} ; le
[simulateur](/simulateur) permet de régler ce plancher.

::: inclure arrets-modulation :::

En énergie, la limite est plus nette encore. Servir de cette façon une
consommation plate de 5 GW demanderait {{quand_energie_j_5gw_2025}} de
production nucléaire en plus sur l'année ({{quand_energie_j_reintegre_5gw_2025}}
en réintégrant les arrêts courts pour modulation), pour un parc qui a produit
{{prod_nucleaire_2025}} en 2025 et dont l'exploitant prévoit
{{prod_nucleaire_prevision_2026_2027}} par an pour 2026-2027. La
puissance restée inemployée heure par heure ne dit pas que le
combustible et le calendrier des arrêts suivraient : une baisse de
production pour économiser le combustible déplace de l'énergie dans le
temps, elle ne la perd pas.

Qui servirait réellement cette consommation (plus de nucléaire, moins
d'éolien et de solaire arrêtés, ou moins d'exportations) dépend, heure
par heure, de la saturation des interconnexions et des prix voisins. Ce
site ne sait pas encore le dire : les données des pays voisins ne sont
pas branchées. On sait seulement que la France exporte massivement à
ces heures : en 2025, quand le nucléaire disponible non produit dépasse
5 GW, son solde des échanges vaut en moyenne {{quand_solde_j5_2025}}
(négatif : exportateur). Si la consommation ajoutée réduisait ces
exportations, ce qui manquerait aux voisins se mesurerait avec le
facteur d'émission marginal européen, que ce calcul ne donne pas.

::: graphique charge-plate :::

**Aux heures tendues**, la même consommation s'ajoute à la charge
résiduelle. Avec 5 GW de plus, la charge résiduelle de 2025 aurait
dépassé son maximum de l'année pendant
{{quand_heures_rn_sup_max_5gw_2025}} ; avec 10 GW, pendant
{{quand_heures_rn_sup_max_10gw_2025}}. Ce décompte tient beaucoup à une
seule matinée, celle du maximum, nettement au-dessus des heures
suivantes. Le système a d'ailleurs couvert davantage : le maximum de
2015 à 2025, {{quand_rn_max_pluri}}, que la charge résiduelle de 2025
augmentée de 10 GW n'aurait dépassé que pendant
{{quand_heures_rn_sup_max_pluri_10gw_2025}}. Mais il l'a fait avec
d'autres moyens : à cette heure de février 2018, du charbon et du fioul,
et des importations importantes ; en décembre 2022, des importations
massives à des prix extrêmes. Dépasser un maximum observé n'est pas une
défaillance ; c'est demander au système de couvrir ce qu'il n'a couvert
que dans ses pires années, voire davantage.

Rapprocher X des marges de RTE est donc légitime, pour une
consommation plate. Dans un calcul d'adéquation, ajouter X GW consommés
en permanence revient à retirer X GW de capacité toujours disponible :
une consommation plate retire à peu près sa puissance à la marge. RTE
n'écrit pas cette équivalence pour la consommation, mais il fait le
même passage dans l'autre sens, en traduisant une hausse de la pointe
en besoin de capacité {{source:rte-bp2025-fonctionnement|p. 25}}.
10 GW consommés en permanence, c'est l'ordre de grandeur des marges
évaluées pour 2026-2027, des marges calculées avant la baisse de
disponibilité nucléaire prévue pour cet hiver. L'équivalence cesse
d'être exacte dès que la consommation n'est pas plate : montée en
charge progressive, report ou effacement aux heures de pointe. C'est
ce que le simulateur permet d'explorer.

## Ce que ce calcul ne dit pas

- ::: inclure limite-froid :::
- **Les voisins.** Aux heures tendues comme aux heures de surplus, les
  échanges comptent. Dire ce que deviennent les exportations déplacées,
  et à quelles émissions, demande les données des pays voisins
  (ENTSO-E), pas encore branchées.
- **Le système change.** Les années observées ne sont pas le système
  dans lequel arriveraient ces consommations : d'autres usages
  s'électrifient, le charbon ferme, le solaire grandit et déplace les
  heures de surplus.
- **Le réseau local.** Tout ici est national. Une consommation de
  quelques centaines de MW pèse d'abord sur un poste électrique et sur
  les lignes qui l'alimentent ; à notre connaissance, aucune capacité
  d'accueil en consommation par poste n'est publiée en open data.
- **Les stocks.** L'hydraulique de lac et les stations de pompage
  apportent de la puissance aux heures tendues, mais sur une quantité
  d'eau limitée : sur un épisode long, leur puissance n'est pas
  disponible à toute heure.
- ::: inclure limite-ecretement :::
- **La pointe exacte.** Les calculs sont à l'heure, hors Corse. RTE
  donne une pointe de {{pointe_conso_2025}} pour 2025, Corse comprise,
  au pas de la demi-heure ; la moyenne horaire de la même matinée est
  plus basse.
