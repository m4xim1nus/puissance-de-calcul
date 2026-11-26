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
-->

Un data center consomme jour et nuit. Sa consommation tombe donc aussi
bien sur les heures où le système électrique a de la marge que sur
celles où il n'en a pas. Cette enquête cherche ces heures dans les
données de 2015 à 2025, puis regarde ce qu'une consommation continue de
quelques GW y ajouterait. Elle ne modélise pas le système : elle décrit
ce qui a été observé, y ajoute une consommation fixe par un calcul
simple, et dit où l'observation s'arrête.

## Personne ne publie une marge heure par heure

La marge dont parle RTE n'est pas un écart qu'on lit sur une courbe.
C'est le résultat d'une simulation : des scénarios de météo et de
disponibilité des moyens de production, à l'échelle de l'Europe
interconnectée, comparés au critère public de sécurité
d'approvisionnement, une espérance de trois heures de défaillance par
an {{source:rte-bp2025-fonctionnement|p. 2}}. Dans son Bilan prévisionnel 2025, RTE
évaluait les marges de l'hiver 2026-2027 à {{marge_rte_hiver_2026_2027}}
par rapport à ce critère. Le mécanisme de capacité a été dimensionné
sur une marge de {{marge_mc_certifiee_2026_2027}}, en puissance
certifiée, une autre unité de compte. Ces deux chiffres datent d'avant
les hypothèses de l'hiver : la synthèse que RTE publie en novembre 2026
ne donne plus de marge en GW, seulement un risque « significativement
en dessous du critère réglementaire » {{source:rte-hiver-2026-2027|p. 15}},
avec un nucléaire disponible prévu à {{dispo_nucleaire_prevue_hiver_2026_2027}}
en moyenne de novembre à mars, contre {{dispo_nucleaire_hiver_2025_2026}}
l'hiver précédent.

Aucune série horaire publique ne donne cette marge. On ne peut pas la
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
ferait paraître « équilibrées » des heures où il restait de la
puissance inutilisée. Ce qui reste après ce retranchement doit venir de
l'hydraulique, du gaz, des autres centrales thermiques, des
importations, des effacements ou du stockage.

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
pointe du mécanisme de capacité, sur lesquelles RTE concentre, à moyen
terme, {{rte_part_defaillance_plages_pointe}} du volume de défaillance
qu'il simule.

::: graphique heatmap-rn :::

Ce qui a couvert ces heures a changé. Pendant les cent heures les plus
tendues de 2022, le solde des échanges de la France valait en moyenne
{{quand_top100_solde_2022}} (positif : importateur). Pendant celles de
2025, il valait {{quand_top100_solde_2025}} : la France **exportait**,
et l'hydraulique de lac et le turbinage des stations de pompage
apportaient {{quand_top100_lacs_step_2025}}, le gaz
{{quand_top100_gaz_2025}}.

## Les heures de surplus : le printemps, l'été, le milieu de journée

À l'autre bout, il y a les heures où le système produit plus que ce
qu'il peut consommer ou exporter. Le signal le plus visible est le prix
négatif : {{heures_negatives_2023}} en 2023, {{heures_negatives_2024}}
en 2024, {{heures_negatives_2025}} en 2025. Ces heures-là, des
producteurs éoliens et solaires s'arrêtent : RTE estime à
{{enr_renoncees_prix_negatifs_2025}} la production renoncée en 2025.
Les {{enr_ecretees_rte_2025}} que RTE a fait écrêter pour la sûreté du
réseau sont en partie comptés dans ce chiffre : les deux ne
s'additionnent pas.

Le second signal est le nucléaire disponible et non produit : la
puissance déclarée disponible par EDF, heure par heure, moins la
production nucléaire. Sur l'année, il représente {{quand_j_2023}} en
2023, {{quand_j_2024}} en 2024 et {{quand_j_2025}} en 2025 ; sans la
disponibilité déclarée de Flamanville 3, en montée en puissance cette
année-là, au moins {{quand_j_2025_hors_epr}} (sa production n'est pas
publiée à part : on ne peut pas faire mieux qu'un encadrement).
C'est le même ordre de grandeur que la modulation publiée par EDF
({{modulation_nucleaire_2023_bp}}, {{modulation_nucleaire_2024_bp}} et
{{modulation_nucleaire_2025_bp}}) ou par RTE pour 2025
({{modulation_nucleaire_2025_be}}), mais ce n'est pas la même grandeur.
La frontière entre « indisponible » et « modulé » est fixée par EDF : un
réacteur arrêté pour économiser son combustible peut être déclaré
indisponible, et sortir de ce calcul. Ce site ne l'appelle donc pas
« modulation ».

## Ce qu'une consommation continue de plus y changerait

Supposons une consommation supplémentaire **plate** de X GW, présente
les 8 760 heures de l'année. C'est une hypothèse, pas un profil
observé : aucune courbe de charge de data centers n'est publiée, et les
data centers déjà raccordés au réseau de transport n'utilisaient fin
2025 que {{dc_taux_utilisation_rpt_2025_12}} de leur puissance de
raccordement. X GW consommés ne sont pas X GW réservés (voir
[« Combien ? »](/combien)).

**Aux heures de surplus**, une partie de cette énergie trouverait du
nucléaire disponible et non produit. Avec les données de 2025, ce
serait au plus {{quand_part_j_1gw_2025}} de l'énergie pour 1 GW,
{{quand_part_j_5gw_2025}} pour 5 GW et {{quand_part_j_10gw_2025}} pour
10 GW. « Au plus », pour trois raisons : une partie de ce nucléaire est
réservée aux services système ; une baisse de production pour
économiser le combustible déplace de l'énergie dans le temps, elle ne la
perd pas ; et la France exporte à ces heures (en 2025, quand le
nucléaire disponible non produit dépasse 5 GW, son solde des échanges
vaut en moyenne {{quand_solde_j5_2025}}, négatif à l'exportation), si
bien qu'une consommation ajoutée serait
d'abord servie, en partie, par moins d'exportations. Ce qui manquerait alors aux voisins se mesure avec le
facteur d'émission marginal européen, que ce calcul ne donne pas.

::: graphique charge-plate :::

**Aux heures tendues**, la même consommation s'ajoute à la charge
résiduelle. Avec 5 GW de plus, la charge résiduelle de 2025 aurait
dépassé son maximum observé pendant {{quand_heures_rn_sup_max_5gw_2025}} ;
avec 10 GW, pendant {{quand_heures_rn_sup_max_10gw_2025}}. Sur les
données de 2024, ce serait {{quand_heures_rn_sup_max_5gw_2024}} et
{{quand_heures_rn_sup_max_10gw_2024}}. Dépasser le maximum observé n'est
pas une défaillance : c'est aller là où le système n'a pas été vu
fonctionner pendant l'année de référence.

Rapprocher X des marges de RTE est tentant : 10 GW consommés à la
pointe, c'est l'ordre de grandeur des marges de 2026-2027. Mais
l'équivalence « un GW de consommation de plus à la pointe, un GW de
marge de moins » est une approximation de ce site, que RTE n'écrit
nulle part. Sa propre méthode la contredit en partie : pour RTE, la
contribution d'une consommation au risque de défaillance dépend de son
profil, et une consommation plate ne pèse pas comme une consommation
qui monte avec le froid {{source:rte-parametrage-mc-2026|p. 16}}. Seul
son modèle sait faire ce passage.

## Ce que ce calcul ne dit pas

- **Le froid extrême.** Onze années observées ne contiennent pas
  forcément les froids les plus sévères que RTE place dans ses
  scénarios. Une année observée n'est pas une distribution de risque ;
  RTE simule, ce site observe.
- **Les voisins.** Aux heures tendues comme aux heures de surplus, les
  échanges comptent. Dire ce que deviennent les exportations déplacées,
  et à quelles émissions, demande les données des pays voisins
  (ENTSO-E), pas encore branchées.
- **Le réseau local.** Tout ici est national. Une consommation de
  quelques centaines de MW pèse d'abord sur un poste électrique et sur
  les lignes qui l'alimentent ; aucune capacité d'accueil locale n'est
  publiée en open data.
- **Les stocks.** L'hydraulique de lac et les stations de pompage
  apportent de la puissance aux heures tendues, mais sur une quantité
  d'eau limitée : sur un épisode long, leur puissance n'est pas
  disponible à toute heure.
- **L'écrêtement.** L'éolien et le solaire observés sont ce qui a été
  produit, après les arrêts à prix négatif : aux heures de surplus, la
  charge résiduelle est surestimée.
- **La pointe exacte.** Les calculs sont à l'heure, hors Corse. RTE
  donne une pointe de {{pointe_conso_2025}} pour 2025, Corse comprise,
  au pas de la demi-heure ; la moyenne horaire de la même matinée est
  plus basse.
