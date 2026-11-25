---
titre: Combien ?
question: Combien pèsent les data centers dans le système électrique français, aujourd'hui et dans dix ans ?
mise_a_jour: 2026-11-26
---

<!--
Syntaxe propre au site :
- {{id}} : chiffre du référentiel (pipeline/referentiels/chiffres.yaml),
  rendu avec son unité et une note marginale (source, page, date, confiance).
- {{source:cle|page}} : renvoi à une source sans chiffre.
- ::: graphique nom ::: : emplacement d'un graphique.
Aucun nombre issu d'une source n'est tapé à la main dans ce fichier ;
les seuls nombres en clair sont des calculs expliqués dans la phrase.
-->

## Aujourd'hui : de l'ordre de 1 % de la consommation

En 2024, les data centers installés sur des sites dédiés ont consommé
{{dc_conso_sites_dedies_2024}}, pour une consommation brute française de
{{conso_brute_france_2024}} : de l'ordre de 1 %. RTE attribue
{{dc_conso_rpt_2024}} aux data centers raccordés au réseau de transport
et {{dc_conso_rpd_2024}} à ceux raccordés au réseau d'Enedis. Les deux
réunis font environ 3,8 TWh, sous la fourchette précédente. RTE
n'explique pas l'écart : data centers raccordés à d'autres
gestionnaires de réseau de distribution qu'Enedis, arrondis, ou
méthodes d'estimation distinctes, on ne sait pas.

Le chiffre change avec le périmètre, et c'est la première source de
confusion. Les salles informatiques installées dans les locaux des
entreprises et des administrations ne sont pas des « sites dédiés ».
En les comptant, RTE estime le total à {{dc_conso_avec_internes_2024}}.
Le SDES, qui part des points de livraison consommant plus de 1 GWh par
an, trouve {{dc_conso_sdes_2024}}. Ce n'est pas un recoupement
indépendant : il repose sur les mêmes comptages que RTE.

::: graphique estimations-2024 :::

## La pyramide des puissances

Pour un data center, le mot « puissance » désigne cinq grandeurs
différentes. Elles ne s'additionnent pas, et chacune est datée.

1. **Recherchée.** Ce que des porteurs de projets disent chercher.
   L'État annonçait {{dc_recherche_2026_01}}, sans publier de
   définition.
2. **Réservée.** Le droit d'accès au réseau, ouvert par la signature
   d'une proposition technique et financière avec RTE. Il n'engage pas
   à consommer. Les réservations des data centers sont passées de
   {{dc_reserve_rte_2024_12}} fin 2024 à {{dc_reserve_rte_2025_11}} en
   novembre 2025, puis à {{dc_reserve_rte_2026_05}} en mai 2026. En
   novembre 2025, RTE indiquait aussi que {{dc_reserve_avant_2030_2025_11}}
   de data centers visaient une mise en service avant 2030 : ce total
   compte les sites déjà raccordés, que les réservations excluent. Ce
   n'est donc pas une part des réservations.
3. **Signée.** Le contrat de raccordement, avec un calendrier. Le
   premier contrat « fast-track », celui du Campus IA à Fouju, prévoit
   {{dc_signe_fouju_2027}}, puis jusqu'à {{dc_signe_fouju_terme}} à
   terme. Ce sont des paliers de puissance mise à disposition, pas des
   dates de mise en service du data center.
4. **Raccordée.** Fin 2025, les data centers raccordés au réseau de
   transport totalisaient {{dc_raccorde_rpt_2025_12}} de puissance de
   raccordement. Côté Enedis, RTE indique {{dc_raccorde_rpd_2025}}
   « en fonctionnement », sans préciser s'il s'agit de puissance de
   raccordement ou d'une autre grandeur.
5. **Appelée.** Ce qui transite réellement. Sur le réseau de transport,
   la consommation de 2025 correspond à une puissance moyenne d'environ
   {{dc_appele_moyen_rpt_2025}}.

::: graphique pyramide :::

RTE le dit lui-même : toutes les demandes ne deviendront pas des
installations. Il observe que « certains développeurs ont parfois
sécurisé un accès au réseau sur plusieurs points du territoire pour des
projets en réalité similaires », et ses trajectoires appliquent des
« abattements significatifs par rapport à la somme des projets ayant
fait des demandes de raccordement »
{{source:rte-bp2025-consommation|p. 6}}.

## Ce que les data centers raccordés consomment vraiment

RTE publie un taux moyen d'utilisation de la puissance de raccordement
de {{dc_taux_utilisation_rpt}} pour les data centers raccordés au
réseau de transport. On ne le retrouve pas avec les autres chiffres du
même rapport : {{dc_conso_rpt_2025}} consommés en 2025, rapportés aux
{{dc_raccorde_rpt_2025_12}} raccordés fin 2025 sur les 8 760 heures de
l'année, donnent environ 15 %. L'écart tient
sans doute à la base de calcul (puissance moyenne de l'année plutôt que
de fin d'année, ou sous-ensemble de sites), que RTE ne précise pas.

Pour les data centers raccordés entre 2022 et 2024, RTE indique une
pointe de {{dc_pointe_cohorte_2022_2024}} en 2024. Ce chiffre ne se
rapporte pas aux {{dc_mis_a_disposition_2022_2025}} mis à disposition
entre 2022 et 2025 : ce ne sont ni la même cohorte, ni la même année,
ni la même grandeur. Il dit seulement que la montée en charge est
lente.

## 2030, 2035 : des trajectoires, pas des prévisions

Le Bilan prévisionnel 2025 de RTE décrit deux trajectoires pour les
sites dédiés. En décarbonation lente, la consommation atteint
{{traj_bp2025_lente_2030}} en 2030 et {{traj_bp2025_lente_2035}} en
2035. En décarbonation rapide, {{traj_bp2025_rapide_2030}} puis
{{traj_bp2025_rapide_2035}}. Pour 2030, RTE suppose qu'environ
{{traj_hyp_concretisation_lente}} (lente) ou {{traj_hyp_concretisation_rapide}}
(rapide) des projets ayant demandé un raccordement au réseau de
transport se concrétisent, avec un taux moyen d'utilisation de la
puissance de raccordement de {{traj_hyp_utilisation_2030}}.

::: graphique trajectoires :::

Les chiffres de « 15 à 20 TWh en 2030 » et « 23 à 28 TWh en 2035 »,
souvent cités, viennent d'un autre exercice : le Bilan prévisionnel
2023 ({{traj_bp2023_2030}} et {{traj_bp2023_2035}}), sur un périmètre
qui inclut les centres internes. La page grand public de RTE les
attribue aujourd'hui au Bilan 2025 {{source:rte-page-datacenters|page
web}}. Le scénario tendanciel de l'ADEME, lui aussi sur un périmètre
élargi, atteint {{traj_ademe_tendanciel_2035}} en 2035.

En énergie, la trajectoire haute de 2035 représente environ 7 % de la
consommation brute de 2024 (32 ÷ 442). La question de l'accueil ne se
réduit donc pas à des TWh par an : les enquêtes suivantes la posent à
l'heure et au poste.

## Ce qui manque

- **Aucun registre public** des data centers avec leur localisation et
  leur puissance. La base européenne prévue par la directive sur
  l'efficacité énergétique est confidentielle site par site.
- **La file d'attente de RTE** n'est publiée qu'en agrégats, à des dates
  et sous des définitions qui changent d'un document à l'autre (le
  même total de novembre 2025 est daté du 1er, du 15 ou de la fin du
  mois selon le document).
- **Les {{dc_sites_identifies_etat}} identifiés par l'État** ne sont
  pas listés publiquement.
- **Aucune courbe de charge** de data center n'est publiée : seulement
  des totaux annuels.
