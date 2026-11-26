---
titre: Combien ?
question: Combien pèsent les data centers dans le système électrique français, aujourd'hui et dans dix ans ?
mise_a_jour: 2026-11-26
accroche: Près de {{dc_reserve_rte_2026_05}} de [puissance réservée](glossaire:puissance-reservee) auprès de RTE pour des data centers en mai 2026 : un droit d'accès au réseau, qui n'engage pas à consommer. Les data centers en service sur des sites dédiés, eux, ont consommé {{dc_conso_sites_dedies_2024}} en 2024, de l'ordre de 1 % de la consommation du pays.
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

## En 2024 : de l'ordre de 1 % de la consommation

En 2024, les data centers installés sur des sites dédiés ont consommé
{{dc_conso_sites_dedies_2024}}, pour une consommation brute française de
{{conso_brute_france_2024}} : de l'ordre de 1 %. RTE attribue
{{dc_conso_rpt_2024}} aux data centers raccordés au [réseau de transport](glossaire:rpt)
et {{dc_conso_rpd_2024}} à ceux raccordés au [réseau d'Enedis](glossaire:rpd). Les deux
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

1. **[Recherchée](glossaire:puissance-recherchee).** Ce que des porteurs de projets disent chercher.
   L'État annonçait {{dc_recherche_2026_01}}, sans publier de
   définition.
2. **[Réservée](glossaire:puissance-reservee).** Le droit d'accès au réseau de transport, ouvert par
   l'acceptation d'une [proposition technique et financière](glossaire:ptf) de RTE et le
   versement d'un premier acompte. Il n'engage pas à consommer. Les
   chiffres publiés ne forment pas une série homogène. Le Bilan
   prévisionnel comptait {{dc_reserve_rte_2025_11}} de propositions
   signées au 1er novembre 2025, hors sites déjà raccordés. La page web
   de RTE donnait {{dc_reserve_rte_2024_12}} fin 2024 et près de
   {{dc_reserve_rte_2026_05}} en mai 2026, sans préciser le traitement
   des sites raccordés ni des projets suspendus. RTE indiquait aussi, en
   novembre 2025, que {{dc_reserve_avant_2030_2025_11}} de data centers
   visaient une mise en service avant 2030, sites déjà raccordés
   compris : ce n'est donc pas une part des réservations.

   Cas particulier, la **[pré-réservation](glossaire:puissance-pre-reservee)** : à la demande de l'État, RTE
   a bloqué {{dc_fasttrack_prereserve_2025_12}} sur cinq sites
   « [fast-track](glossaire:fast-track) », pour une durée limitée. En juin 2026, RTE écrivait que
   quatre d'entre eux avaient « déjà fait l'objet de la signature d'un engagement de
   raccordement », sans dire lesquels ni de quel engagement il s'agit
   {{source:rte-sddr-reponse-cpdp-2026|p. 20}} ; leur état en novembre 2026 n'est pas publié.
   Fouju figure à la fois parmi ces sites et à l'étage
   suivant, avec son contrat.
3. **[Signée](glossaire:puissance-signee).** Le contrat de raccordement, avec un calendrier. Le
   premier contrat « fast-track », celui du Campus IA à Fouju (signé le
   26 janvier 2026), prévoit {{dc_signe_fouju_2027}}, puis
   {{dc_signe_fouju_2029}}. Ce sont des paliers de puissance mise à
   disposition, pas des dates de mise en service du data center. Les
   ouvrages sont dimensionnés pour permettre, à terme,
   {{dc_signe_fouju_terme}}, mais ce niveau n'est pas un palier du
   contrat.
4. **[Raccordée](glossaire:puissance-raccordee).** Fin 2025, les data centers raccordés au réseau de
   transport totalisaient {{dc_raccorde_rpt_2025_12}} de puissance de
   raccordement. Côté Enedis, RTE indique {{dc_raccorde_rpd_2025}} de
   puissance raccordée pour les data centers en service en 2025. Ce
   total a baissé en 2025 par construction : depuis l'été 2025, les
   gestionnaires de réseau peuvent réduire les puissances de
   raccordement surdimensionnées.
5. **[Appelée](glossaire:puissance-appelee).** Ce qui transite réellement. Sur le réseau de transport,
   la consommation de 2025 correspond à une puissance moyenne d'environ
   {{dc_appele_moyen_rpt_2025}}.

::: graphique pyramide :::

À propos de l'ensemble des demandes de raccordement (industrie,
hydrogène, centres de données), RTE observe que « certains
développeurs ont parfois sécurisé un accès au réseau sur plusieurs
points du territoire pour des projets en réalité similaires ». Ses
trajectoires appliquent donc des « abattements significatifs par
rapport à la somme des projets ayant fait des demandes de
raccordement » {{source:rte-bp2025-consommation|p. 6}}.

## Ce que les data centers raccordés consomment vraiment

RTE a publié deux valeurs du taux d'utilisation de la puissance de
raccordement des data centers raccordés au réseau de transport :
{{dc_taux_utilisation_rpt_2025_12}} en décembre 2025, puis
{{dc_taux_utilisation_rpt}} en mars 2026. On ne retrouve ni l'une ni
l'autre avec les autres chiffres du même rapport : {{dc_conso_rpt_2025}}
consommés en 2025, rapportés aux {{dc_raccorde_rpt_2025_12}} raccordés
fin 2025 sur les 8 760 heures de l'année, donnent environ 15 %.
L'écart tient peut-être à la base de calcul (puissance moyenne de
l'année plutôt que de fin d'année, ou sous-ensemble de sites) ; RTE ne
la précise pas.

Pour les data centers raccordés entre 2022 et 2024, RTE indique qu'ils
ont « utilisé au maximum » {{dc_pointe_cohorte_2022_2024}} en 2024,
sans dire s'il s'agit d'une pointe simultanée ou d'une somme de
pointes. Ce chiffre ne se rapporte pas aux
{{dc_mis_a_disposition_2022_2025}} mis à disposition entre 2022 et
2025 : ce ne sont ni la même cohorte, ni la même année, ni la même
grandeur, et la capacité de cette seule cohorte n'est pas publiée. RTE
en conclut que leur consommation « reste aujourd'hui bien inférieure à
la puissance totale mise à disposition »
{{source:rte-tdb-electrification-2026|p. 25}}.

## 2030, 2035 : des trajectoires, pas des prévisions

Le Bilan prévisionnel 2025 de RTE décrit deux trajectoires pour les
sites dédiés. En décarbonation lente, la consommation atteint
{{traj_bp2025_lente_2030}} en 2030 et {{traj_bp2025_lente_2035}} en 2035.
En décarbonation rapide, elle atteint {{traj_bp2025_rapide_2030}} en
2030 et {{traj_bp2025_rapide_2035}} en 2035. Pour 2030, RTE suppose
qu'environ {{traj_hyp_concretisation_lente}} (lente) ou
{{traj_hyp_concretisation_rapide}} (rapide) des projets disposant d'un
accès réservé au réseau de transport pour une mise en service avant
2030 se concrétisent, avec un taux moyen d'utilisation de la puissance
de raccordement de {{traj_hyp_utilisation_2030}}. L'assiette de ces
taux est donc de l'ordre de 7 à 8 GW (4,3 GW ÷ 60 %), pas
l'ensemble des réservations.

::: graphique trajectoires :::

Les chiffres de « 15 à 20 TWh en 2030 » et « 23 à 28 TWh en 2035 »,
souvent cités, viennent d'un autre exercice : le Bilan prévisionnel
2023 ({{traj_bp2023_2030}} et {{traj_bp2023_2035}}), sur un périmètre
qui inclut les centres internes. La page grand public de RTE les
attribue aujourd'hui au Bilan 2025 {{source:rte-page-datacenters|page
web}}. Le scénario tendanciel de l'ADEME atteint
{{traj_ademe_tendanciel_2035}} en 2035 ; il ne se compare pas non plus
directement aux trajectoires de RTE, pour deux raisons : il inclut les
centres internes, et il part des usages numériques des Français, quand
RTE part des demandes de raccordement, campus tournés vers l'export
compris.

En énergie, la trajectoire haute de 2035 vaut environ 7 % de la
consommation brute de 2024 (32 ÷ 442). Les enquêtes suivantes examinent
la même question à l'heure et au [poste](glossaire:poste-electrique).

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
- **Aucune courbe de charge propre aux data centers** n'est publiée. Il
  existe des totaux annuels, une valeur maximale annuelle pour une
  cohorte, et un indicateur partiel au pas de 30 minutes : les
  soutirages sur le réseau de transport de la section NAF J
  (« information et communication »), dont le périmètre ne coïncide
  pas avec celui des data centers et dont le volume ne représente
  qu'environ un quart du leur sur le réseau de transport.
