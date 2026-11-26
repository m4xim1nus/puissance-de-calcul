# Contre-vérification adverse — enquête « Quand ? »

Rapport d'un agent distinct de celui du spike. Il a reçu la liste des
17 affirmations, mais pas les conclusions du spike (`docs/spike/quand.md` n'a
pas été lu). Rédigé le 26/11/2026. Toutes les pages citées sont des pages PDF ;
pour les documents RTE cités, elles coïncident avec la pagination imprimée.

## Sources consultées et vérification d'origine

Les copies locales de `data/raw/spike_quand/pdf/` ont été retéléchargées
depuis l'URL d'origine le 26/11/2026 pour six documents. Les six sont
**identiques octet pour octet** (SHA-256).

| Document | URL | Date | Copie locale |
|---|---|---|---|
| Synthèse « Perspectives… hiver 2026-2027 » | assets.rte-france.com/prod/public/2026-11/2026-11-18-synthese-perspectives-passage-hiver-2026-2027.pdf | couverture « novembre 2026 » ; PDF créé le 19/11/2026 ; Last-Modified 23/11/2026 | identique |
| Rapport de paramétrage du mécanisme de capacité, PL 2026/2027 | assets.rte-france.com/prod/public/2026-02/2026-02-12-rapport-parametrage-mecanisme-capacite.pdf | couverture « 21 janvier 2026 » ; publié le 12/02/2026 (URL, Last-Modified) | identique |
| BP2025, « Fonctionnement du système électrique » | assets.rte-france.com/prod/public/2026-07/2026-07-15-bilan-previsionnel-fonctionnement-systeme-electrique.pdf | URL du 15/07/2026 ; PDF créé le 30/06/2026 | identique |
| BP2025, « Principaux résultats » | …/2025-12/2025-12-16-bilan-previsionnel-principaux-resultats-2025.pdf | 16/12/2025 | identique |
| BP2025, « La consommation » | …/2025-12/2025-12-23-bilan-previsionnel-2025-consommation.pdf | 23/12/2025 | identique |
| Bilan électrique 2025, rapport complet | assets.rte-france.com/analyse-et-donnees/2026-03/BE2025%20-%20Rapport%20Complet.pdf | URL de mars 2026 | identique |
| **Rapport d'enchère PL 2026/2027** (nouveau, absent du dépôt) | www.services-rte.com/files/live/sites/services-rte/files/rapport-enchere-public-pl-26-27.pdf | couverture « 17 juillet 2026 » | téléchargé (non versionné) |
| Règles de marché, chap. 2 « Mécanisme d'ajustement », V02 en vigueur au 01/01/2026 | www.services-rte.com/…/RM-2-MECANISME_D_AJUSTEMENT-V02-20260101_6224_fr | Last-Modified 17/12/2025 | téléchargé (non versionné) |
| ODRÉ `nouveau_signal_ecowatt`, `volumes-actives-ma` | odre.opendatasoft.com, export CSV | retéléchargés le 26/11/2026 | mêmes valeurs que les copies |
| EDF data-fair (2 jeux d'indisponibilités) | opendata.edf.fr/data-fair/api/v1/datasets/… | métadonnées et API interrogées le 26/11/2026 | cohérent |

Inaccessibles (HTTP 403 pour un client automatique) : l'étude EDF
`2026_02_16_ETUDE_MODULATION.pdf` et les deux notices EDF sur le format des
publications REMIT (doaat.edf.fr). Ce qui en est dit plus bas vient du
communiqué EDF ou d'extraits de moteur de recherche, et c'est signalé.

## Tableau des verdicts

| # | Affirmation (résumé) | Verdict |
|---|---|---|
| 1 | EDF data-fair : historique depuis 2015, LO 2.0, Pmax/Pdispo, liste courante horaire | **Exact, avec trois précisions** : l'historique n'est mis à jour que chaque trimestre ; le périmètre est « EDF SA + Luminus » et comprend des unités belges ; les lignes sont des versions de déclaration, pas des événements |
| 2 | BE2025 fig. 2.5 : taux REMIT 2015-2025 | **Exact** (11 valeurs, p. 25) |
| 3 | Dates EDF en heure de Paris | **Exact en pratique** (établi par un test sur les données). La documentation EDF est ambiguë et n'a pas pu être lue directement |
| 4 | BP2025 Fonct. p. 13 : marges 2026-2027 de 8 à 10 GW | **Exact** ; marges en capacité équivalente par rapport au critère, évaluées avant les hypothèses de l'hiver 2026-2027 |
| 5 | Paramétrage : 8,0 GW (rapide), 9,5 GW (lente) | **Chiffres exacts** (p. 10). La date est **à préciser** : le rapport est daté du 21/01/2026, mais la version publiée le 12/02/2026 a été modifiée après la saisine de la CRE. Le scénario finalement retenu est le scénario lent |
| 6 | Hiver 2026-27 p. 8 : 48,5 GW contre 50,5 GW | **Exact** |
| 7 | BP2025 Fonct. p. 30 : ≈ 50 % de la défaillance entre 7 h-10 h et 17 h-20 h ; risque méridien très faible | **Exact**, mais c'est une projection « à moyen terme » dans une configuration donnée |
| 8 | Modulation 16/31/33 TWh contre « une trentaine de TWh » | **Chiffres exacts** ; **même périmètre large** (toutes causes de modulation). Ni l'un ni l'autre ne mesure la modulation économique seule |
| 9 | ≈ 3 TWh renoncés à prix négatifs ; 0,1 TWh écrêtés à la demande de RTE | **Exact** ; **ne pas additionner** (périmètres qui se recouvrent, texte RTE incohérent) |
| 10 | 8 GW / 5 GW / −10 GW / 2 à 4 GW | **Exact** |
| 11 | 20 % / 20 % / 90 % | **Citations exactes** : trois grandeurs différentes (détail plus bas) |
| 12 | RTE n'isole pas la contribution des data centers à la pointe | **Exact** (aucun chiffre trouvé ; une seule mention qualitative, dans la synthèse hiver p. 7) |
| 13 | « X GW de plus à la pointe ⇒ X GW de marge en moins » | **Non trouvé** : RTE ne l'écrit pas pour la consommation. Une équivalence proche existe côté offre (nucléaire) |
| 14 | Aucune heure orange ni rouge du 01/09/2022 au 25/11/2026 | **Exact sur le jeu ODRÉ**, avec trois réserves (jours manquants, signal « dernier publié », changement d'échelle en 2022) |
| 15 | Pointe 2025 : 88 GW le 14/01 à 9 h | **Exact** (BE2025 p. 10) ; recoupé par éCO2mix : 87 713 MW à 09:00 |
| 16 | 4,4 GW d'effacement contractualisés ; prix 28 182,99 €/MW | **Exact** ; rapport d'enchère RTE trouvé (p. 9) : seule une partie des capacités est payée à ce prix |
| 17 | Situations tendues à la hausse : 45 (2024), 68 (2025) | **Exact** ; unité : demi-journées ; définition trouvée chez RTE |

---

## Détail par affirmation

### 1. Jeux EDF d'indisponibilités (opendata.edf.fr, data-fair)

**Verdict : exact sur le fond, à préciser sur quatre points.**

Métadonnées lues par l'API data-fair le 26/11/2026 :

- « Historique des indisponibilités des moyens de production de EDF SA - depuis 2015 » : licence « Licence Ouverte / Open Licence version 2.0 » ; `temporal.start` 2015-01-01 ; `frequency: quarterly` ; résumé : « Dernière date de mise à jour : 07/09/2026 » ; 413 289 lignes.
- « Indisponibilités des moyens de production de EDF SA » (liste courante) : « Informations relatives aux indisponibilités non terminées il y a trois mois […] Les données présentées sur notre site sont récupérées toutes les heures » ; `dataUpdatedAt` 2026-11-26T08:00 ; 29 717 lignes.
- Colonnes `puissance_maximale_mw` (« Puissance maximale de la centrale de production ») et `puissance_disponible_mw` (« Puissance disponible lors de l'indisponibilité ») : présentes.

Ce qui manque ou piège :

1. **L'historique n'est pas à jour** : dernière mise à jour des données le 07/09/2026. Entre cette date et aujourd'hui, seule la liste courante couvre les événements, et seulement ceux qui ne sont pas « terminés il y a trois mois ». Toute série « depuis 2015 jusqu'à aujourd'hui » doit raccorder les deux jeux.
2. **Périmètre « EDF SA + Luminus », pas « EDF SA »** : le champ `perimetre_juridique` vaut « EDF SA + Luminus » et `perimetre_spatial` « France métropolitaine sans la Corse ni les îles du ponant + Belgique » sur 100 % des lignes. Le fichier contient 1 311 lignes `10000_LUM_*` : RINGVAART STEG, SERAING (gaz), NOBELWIND (éolien en mer belge), BESS Navagne. Le nucléaire n'est pas touché (59 noms, tous français, Fessenheim et Flamanville 3 compris), mais un agrégat « gaz » ou « éolien en mer » serait faux.
3. **Une ligne est une version de déclaration, pas un événement** : 413 289 lignes pour 231 796 identifiants. Répartition des statuts : Active 213 351, Inactive 181 493, Annulée 17 567, Supprimée 878. Il faut garder une seule version par identifiant.
4. **Les « chroniques » ne sont pas des indisponibilités** : les types `Chronique PMIN`, `Chronique aFRR`, `Chronique`, `Chronique.` (224 739 lignes) portent `Pmax = 0` et `Pdispo = 0` dans l'historique, avec la vraie information dans le texte libre (par ex. « PMIN 08/09/2026 00h00 : 905MW »). Un filtre naïf `Pdispo = 0` les compterait comme des arrêts complets. Dans la liste courante, ces deux champs sont vides.
5. Règle de superposition, citée dans la description des deux jeux : « En cas de superposition d'indisponibilités, fortuites ou programmées, la pratique est de retenir la puissance disponible minimale des indisponibilités sur chaque période de superposition. » Il ne faut donc pas additionner les MW indisponibles de deux déclarations qui se chevauchent.

### 2. BE2025, fig. 2.5 (p. 25)

**Verdict : exact.** La figure 2.5, « Évolution du taux annuel de disponibilité* du parc nucléaire français entre 2015 et 2025 », donne : 79,5 / 72,2 / 71,1 / 74,0 / 71,6 / 65,2 / 69,8 / 54,2 / 62,9 / 71,5 / 74,0 %. Le texte de la même page confirme : « sur l'ensemble de l'année 2025, celle-ci s'est élevée à 74,0 % […] (71,5 %) ». Note * : « Sur la base des indisponibilités déclarées au titre de REMIT. […] Le calcul exclut l'EPR de Flamanville qui est encore en phase d'essais. »

Pièges de sens :
- **Ce n'est pas le Kd d'EDF.** RTE écrit : « Le taux ainsi calculé est légèrement inférieur au coefficient de disponibilité (Kd) rapporté par EDF […] EDF impute certains arrêts (pour économie de combustible par exemple) ou certaines limitations de puissance […] en tant que modulations et non en tant qu'indisponibilités. Ici toutes les indisponibilités sont comptées. » Conséquence pour l'affirmation 8 : un arrêt pour économie de combustible est compté **à la fois** comme indisponibilité dans ce taux et comme modulation dans les « ~30 TWh ». On ne peut donc pas combiner les deux chiffres dans un même bilan d'énergie non produite.
- C'est un **taux annuel**, été compris. Il ne dit rien de la disponibilité hivernale, qui est la grandeur pertinente pour « Quand ? » (voir l'affirmation 6).

### 3. Fuseau horaire des dates EDF

**Verdict : exact en pratique (heure légale de Paris), établi par un test sur les données.**

- Documentation : les deux notices EDF (doaat.edf.fr) n'ont pas pu être lues (HTTP 403). D'après les extraits du moteur de recherche, elles écrivent « Les heures indiquées sont au format UTC pour la zone Central European » et « The times indicated are in UTC format for the Central European Time zone ». La formule est **ambiguë** : elle ne tranche pas entre UTC et CET/CEST. À lire dans le PDF par un humain avant de la citer.
- La plateforme data-fair sert les dates **avec un décalage horaire** : par exemple `"2033-07-17T07:00:00+02:00"` en été, `"2026-01-20T11:50:00+01:00"` en hiver. Elle interprète donc les dates comme l'heure légale de Paris. C'est cohérent, mais c'est l'interprétation de la plateforme, pas une déclaration d'EDF.
- **Test empirique (concluant)** : on prend les 121 déclenchements fortuits de réacteurs d'au moins 1 300 MW passés à `Pdispo = 0` en 2023-2025, avec une heure de début hors heure ronde. Pour chacun, on calcule la variation de la production nucléaire éCO2mix définitive (pas de 30 min) autour de l'heure déclarée.
  - Si les dates EDF sont en heure de Paris, la chute est alignée sur l'heure déclarée : −500 MW en moyenne sur la fenêtre centrée, −752 MW sur la suivante, ≈ 0 avant.
  - Si elles étaient en UTC, la production chuterait 1 à 2 h **avant** le déclenchement déclaré (−445 MW à −90 min), ce qui est impossible.
  - Le test séparé par saison donne la même chose : 44 événements en heure d'hiver (chute maximale −1 033 MW dans la demi-heure suivante) et 77 en heure d'été (−591 MW).
- Piège : les dates sont **naïves** (sans décalage) dans les CSV (« 01/10/2026 08:00 », « 2026-11-26 00:00:00 »). L'heure 02:00-03:00 du dernier dimanche d'octobre est donc ambiguë, et la conversion en UTC demande une règle explicite.

### 4. BP2025, « Fonctionnement », p. 13 : marges de 8 à 10 GW

**Verdict : exact.** Citation : « le niveau de marges pour l'hiver 2026-2027 est évalué entre 8 et 10 GW par rapport au critère public de sécurité d'approvisionnement, et varie en fonction de la dynamique d'évolution de la consommation, des rythmes de développement des énergies renouvelables et de la disponibilité du parc nucléaire. » Même ordre de grandeur dans les Principaux résultats (16/12/2025), p. 15 : « celles-ci se maintiendront autour de 8 à 10 GW par rapport au critère public de sécurité d'approvisionnement ».

Pièges :
- Une marge « par rapport au critère » est une capacité équivalente dans un calcul probabiliste (espérance de défaillance de 3 h/an). Ce n'est **pas** un excédent de puissance observable à la pointe.
- **Date des hypothèses** : le chiffre vient du BP2025, dont les hypothèses datent de 2025. La synthèse de l'hiver 2026-2027 (novembre 2026) ne redonne **aucune marge en GW** : elle écrit seulement que le risque se situe « significativement en dessous du critère réglementaire […] dans toutes les configurations étudiées » (p. 15). Depuis le BP2025, la disponibilité nucléaire prévue est passée à 48,5 GW et l'EPR est indisponible tout l'hiver (affirmation 6). Présenter « 8 à 10 GW » comme la marge actuelle de l'hiver 2026-2027 serait un raccourci.

### 5. Rapport de paramétrage du mécanisme de capacité PL 2026/2027

**Verdict : chiffres exacts ; date et grandeur à préciser.**
- p. 10, « Tableau 5 : Valeurs de marge dans les scénarios de dimensionnement », colonne « Marge utilisée pour Cref » : « Décarbonation rapide 8,0 GW », « Décarbonation lente 9,5 GW ». La figure 4 (p. 12) reprend ces chiffres et donne Cref = 80,5 GW (rapide) et 79,0 GW (lente).
- **Date** : la couverture porte « 21 janvier 2026 », mais le document a été mis en ligne le 12/02/2026 (URL, Last-Modified), et sa note 7 (p. 11) dit : « La version initiale de ce rapport soumis pour saisine à la CRE ne prenait pas compte la différence entre STEPs journalières, hebdomadaires et saisonnières. Les valeurs de certification du parc et de Cref ont été modifiées. » Il faut donc citer « rapport daté du 21/01/2026, version publiée le 12/02/2026 ». Je n'ai pas vérifié si les marges ont changé entre les deux versions.
- **Grandeur** : ce sont des GW **certifiés**, au sens du mécanisme de capacité (axe « GW certifiés » de la figure 4 ; nucléaire certifié avec un coefficient de 0,95 sur la disponibilité aux heures PP, tableau 6). Elles ne se comparent pas directement aux marges du BP.
- **Scénario retenu** : la CRE propose le scénario lent (délibération 2026-43 du 10/02/2026, p. 9 : « sa proposition de retenir le scénario de décarbonation lente pour le paramétrage de la courbe de demande »). Le rapport d'enchère (p. 9) donne un volume Cref arrêté de **79 000 MW**, soit la valeur du scénario lent. La marge qui sous-tend le mécanisme réel est donc 9,5 GW, pas 8,0.
- Coïncidence piège : le paramétrage projette un nucléaire **certifié** de 48,5 GW (tableau 7, p. 11), le même nombre que la **disponibilité moyenne** prévue pour novembre-mars dans l'affirmation 6. Ce sont deux grandeurs différentes. Le nucléaire effectivement certifié à l'enchère est de **44 755 MW** (rapport d'enchère, p. 10), et le volume certifié total de 86 197,8 MW, contre 88,5 GW projetés.

### 6. Synthèse hiver 2026-2027, p. 8

**Verdict : exact.** Citation : « les prévisions de RTE pour l'hiver 2026-2027 conduisent à une disponibilité moyenne du parc nucléaire estimée à 48,5 GW entre les mois de novembre et de mars (contre 50,5 GW en 2025-2026 sur la même période), avec un niveau pouvant atteindre autour de 54 GW courant janvier 2027 (contre 55,5 GW atteints en janvier 2026) ».

Pièges :
- Note 5, même page : la disponibilité « est différente de la production nucléaire » et « la disponibilité affichée est lissée sur 7 jours ». La figure 2 est arrêtée « au 13 novembre 2026 ».
- p. 7 : « l'EPR de Flamanville 3 (1 600 MW de puissance installée) est à l'arrêt depuis le 26 septembre dernier jusqu'au mois de septembre 2027 […] et sera donc indisponible pour l'hiver ». C'est un candidat évident pour une bonne part de l'écart de 2 GW, mais **RTE ne fait pas ce lien chiffré**. Ne pas l'écrire comme un constat de RTE.
- Ne pas comparer avec la synthèse de l'hiver précédent (09/12/2025, p. 6) : « 54 GW (hors EPR de Flamanville) entre les mois de décembre et de janvier ». La fenêtre (décembre-janvier) et le périmètre (hors EPR) diffèrent de « novembre-mars ».

### 7. BP2025, « Fonctionnement », p. 30

**Verdict : exact, avec son contexte.** Citation : « Si au sein d'une journée, près de 50 % du volume de défaillance resterait concentré autour des pointes de consommation du matin et du soir, sur les plages 7 h-10 h et 17 h-20 h, les épisodes de défaillance auraient tendance à devenir plus longs et à s'étendre davantage sur les heures en soirée, voire la nuit. En revanche, le risque sur les plages méridiennes apparaît dès aujourd'hui très faible ».

Pièges :
- Section 5.3.4 : « à moyen terme », « dans les trajectoires de décarbonation étudiées ». La figure 5.20 (p. 31) porte sur la configuration « Décarbonation rapide – R3 » (sans bouquet d'équilibrage), aux horizons 2026, 2030 et 2035. C'est une **projection conditionnelle** (conditionnel « resterait »), pas un constat.
- C'est une part du **volume d'énergie non distribuée** (MWh), pas du nombre d'heures. La phrase dit aussi l'inverse de « tout se joue à 7 h-10 h et 17 h-20 h » : l'autre moitié glisse vers la soirée et la nuit.
- Note 38 (p. 30) : les plages PP du mécanisme de capacité 2026/2027 sont « [7h-10[ et [17h-20h[ ». Les deux plages coïncident par construction ; ce n'est pas une confirmation indépendante.

### 8. Modulation nucléaire : 16/31/33 TWh contre « une trentaine de TWh »

**Verdict : chiffres exacts ; même périmètre large ; formulation du BP ambiguë.**
- BP2025 Fonct., p. 6 : « Depuis quelques années, la modulation assimilable à des absences de débouchés économiques du parc nucléaire évolue à la hausse, et a contribué à faire passer la modulation de 16 TWh en 2023, à 31 TWh en 2024 puis 33 TWh en 2025⁴, pour un volume total de production non utilisée intégrant d'autres causes relativement stable, de 41 TWh en 2023 et 38 TWh en 2024. » Note 4 : « Donnée provisoire, source EDF 2026_02_16_ETUDE_MODULATION.pdf ».
- BE2025, p. 31 : « La modulation (toutes typologies confondues) a représenté de l'ordre d'une trentaine de TWh en 2025, un volume relativement stable par rapport à l'année précédente. » Les typologies sont listées sur la même page : « participation des réacteurs à l'équilibrage du système, […] modulation assimilable à une absence de débouchés économiques ou d'autres modulations liées à la gestion du parc », par exemple « pour économie de combustible ». Les contraintes environnementales (« moins d'un térawattheure ») et les grèves sont traitées à part (p. 32).
- Communiqué EDF du 16/02/2026 (lu par un outil de récupération web ; le PDF de l'étude a renvoyé 403) : « En 2025, le parc nucléaire a modulé à hauteur de 33 TWh. » Définition en note : modulation « lorsqu'un réacteur fonctionne à une puissance inférieure à sa puissance maximale », arrêt compris, hors rechargement, maintenance, aléas, contraintes environnementales ou réglementaires. Le communiqué ne ventile pas par cause.

**Périmètre** : les deux chiffres couvrent la **modulation toutes causes** (équilibrage, économique, économie de combustible), hors contraintes environnementales. Le « 33 TWh » du BP est un chiffre EDF provisoire ; la « trentaine » de RTE est une estimation arrondie. Ils sont compatibles. Mais la phrase du BP laisse croire que 16 → 31 → 33 TWh mesure la modulation **économique** : c'est faux. Aucun de ces documents ne donne la modulation économique seule en 2025.

Autres pièges :
- Ne pas rapprocher de la projection du BP Fonct. p. 14 (« 20 à 30 TWh en moyenne » à l'horizon 2026-2027) : celle-ci porte sur la modulation « liée à l'absence de débouchés économiques », modélisée. Ce n'est pas le même périmètre.
- Double comptage avec l'affirmation 2 (arrêts pour économie de combustible).

### 9. BE2025 : environ 3 TWh à prix négatifs (p. 42) ; 0,1 TWh à la demande de RTE (p. 43)

**Verdict : exact ; les deux chiffres ne s'additionnent pas.**
- p. 42 : « En 2025, les épisodes de prix négatifs ont conduit à renoncer à environ 3 TWh¹⁹ de production solaire et éolienne. » Note 19 : « 1,3 TWh de production éolienne terrestre et 1,6 TWh de production solaire (estimation RTE) ». La somme fait 2,9 TWh ; l'éolien en mer est exclu ; c'est une **estimation**.
- p. 43 : « En 2025, les ajustements à la baisse sollicités par RTE ont conduit à écrêter 0,1 TWh de production solaire et éolienne. » La figure 2.30 (p. 44) inclut l'éolien en mer.
- **Incohérence interne de RTE à signaler** : p. 36, les 1,3 TWh éoliens couvrent les deux causes (« soit en regard d'une incitation économique lors d'épisode de prix spot négatifs (l'essentiel des volumes), soit lorsque RTE les a sollicités »). p. 41, les 1,6 TWh solaires aussi (« en regard d'incitations économiques […] ou à la demande de RTE »). Or la note 19 attribue ces mêmes 1,3 et 1,6 TWh aux prix négatifs. Les « ≈ 3 TWh » contiennent donc probablement une partie des 0,1 TWh. **Ne jamais écrire 3,1 TWh.**

### 10. BP2025, « Fonctionnement », p. 25-26

**Verdict : exact.**
- p. 25 : « la hausse brute de la pointe de consommation induite impliquerait un besoin de capacité supplémentaire d'environ 8 GW, toutes choses égales par ailleurs » ; « en intégrant l'effet des flexibilités de la demande (configuration médiane), la hausse du besoin capacitaire du système liée à l'évolution de la consommation est limitée à environ 5 GW entre 2026 et 2030 dans la configuration de décarbonation rapide ».
- p. 26, figure 5.15 (« Décarbonation rapide – R3 ») : étiquette « ~ -10 GW de marges entre 2026 et 2030 ». Texte : « un besoin de capacités additionnelles limité, de l'ordre de 2 à 4 GW en 2030, qui varie selon le rythme d'installation des capacités de production renouvelable ».
- Complément : les Principaux résultats, p. 32, précisent « autour de 2,5 GW en particulier dans un scénario "Décarbonation rapide - R3" ».
- Pièges : les −10 GW cumulent tous les effets (consommation, thermique −3 GW, Europe, EnR, nucléaire, flexibilités), pas la seule consommation. Les 8 GW sont **bruts**, avant flexibilités. Tout cela vaut dans la seule trajectoire rapide ; dans la trajectoire lente, le besoin est « nul » en R3 (p. 28).

### 11. Les trois « 20 % / 20 % / 90 % »

**Verdict : les trois citations sont exactes ; ce sont trois grandeurs différentes, et aucune n'est une contribution à la pointe.**

| Chiffre | Citation et page | Sens exact |
|---|---|---|
| 20 % « à date » | Principaux résultats, p. 23 (tableau) : « les datacenters déjà raccordés n'utilisant par exemple à date que 20% de leur puissance contractuelle de raccordement » | **Constat** sur les sites déjà raccordés, à une date non précisée. Ni le dénominateur exact ni le type de grandeur (moyenne ou maximum) ne sont donnés. ERREURS.md signale ailleurs un 22 % RTE (« rapport moyen ») |
| 20 % en 2030 | Consommation, p. 14 : « en supposant des facteurs de charge normatifs, en 2030, respectivement de 20 %, 40 % et 60 %, pour les centres de données, les sites industriels et les unités de production d'hydrogène » ; p. 28, note 15 : « Le taux moyen d'utilisation de la puissance de raccordement prend en compte pour les centres de données à la fois la différence entre puissance consommée et puissance de raccordement en régime nominal, et le stade d'avancement de chaque site dans sa montée en charge » | **Hypothèse normative** pour la trajectoire rapide en 2030. Elle **inclut la montée en charge** (la plupart des sites ont moins de dix ans) : ce n'est pas un facteur de charge à maturité. Appliquée aux 4,3 GW (60 %) ou 2,4 GW (30 %) des projets à raccorder avant 2030 (Consommation, p. 13 et 27-28) |
| 90 % | Principaux résultats, p. 21 : « 180 TWh en tenant compte de moindres facteurs de charge (40 % pour les projets industriels, 90 % pour les unités de production d'hydrogène bas-carbone et les centres de données) » ; même idée dans Consommation, p. 6 (« hypothèses plus réalistes de facteur de charge ») | **Calcul théorique** : facteur de charge à maturité, appliqué à 100 % des ≈ 14 GW de projets de data centers ayant une PTF signée. Il sert à montrer l'écart avec les trajectoires, pas à prévoir |

Piège pour « Quand ? » : un facteur de charge (énergie annuelle rapportée à la puissance de raccordement) n'est pas la puissance appelée à la pointe d'hiver. Le passage de l'un à l'autre n'est donné nulle part par RTE (voir 12 et 13).

### 12. Contribution des data centers à la pointe : affirmation négative

**Verdict : exact (pas de contre-exemple chiffré).** J'ai cherché « centres de données », « datacenter(s) », « numérique » et « pointe » dans les sept documents BP2025, dans les synthèses des hivers 2025-2026 et 2026-2027, dans le paramétrage et dans les premières analyses de l'été 2026. Aucun chiffre de contribution des data centers à la pointe. Mentions qualitatives seulement :
- synthèse hiver 2026-2027, p. 7 : « RTE n'anticipe pas de forte hausse de consommation en lien avec les usages émergents (datacenters, électrolyseurs) durant l'hiver 2026-2027 » ;
- BP Fonct., p. 12 : « la montée en charge progressive des centres de données » parmi les facteurs haussiers « portant sur un volume limité de consommation électrique ».

Les 8 GW de « hausse brute de la pointe » (affirmation 10) incluent les data centers sans les isoler.

### 13. « X GW de consommation à la pointe ⇒ X GW de marge en moins »

**Verdict : non trouvé ; RTE ne l'écrit pas pour la consommation.** Ce qui s'en approche, sans le dire :
- BP Fonct., p. 25 : la hausse de la pointe « impliquerait un besoin de capacité supplémentaire d'environ 8 GW, toutes choses égales par ailleurs ». Le texte ne donne pas la hausse de pointe correspondante, donc pas de ratio.
- Côté **offre**, BP Fonct., p. 27 : avec une disponibilité hivernale de 46 GW au lieu de 51,5 GW (−5,5 GW), « le besoin de capacités additionnelles augmente de 5 à 6 GW ». C'est une équivalence proche de un pour un, mais pour la disponibilité nucléaire.
- Contre-indice méthodologique : le paramétrage (p. 16, § 8) calcule le vecteur de température extrême par « une analyse de sensibilité de la contribution au risque de défaillance d'un profil de consommation non thermosensible comparativement à celui d'une consommation purement thermosensible ». Pour RTE, la contribution au risque d'un GW de consommation dépend donc de son profil. Une charge plate (data center) et une charge thermosensible ne pèsent pas pareil. L'équivalence un pour un est une approximation à construire et à afficher comme telle, pas une citation.

### 14. Ecowatt national (ODRÉ `nouveau_signal_ecowatt`)

**Verdict : exact sur ce jeu, avec trois réserves.** Jeu retéléchargé le 26/11/2026 : du 01/09/2022 au 25/11/2026, 1 544 jours. Sur les 37 056 pas horaires : valeur 1 (vert) 17 941, valeur 0 (« vert + production décarbonée », depuis le 03/11/2023) 19 115, **aucun 2 ni 3**. `couleur_du_jour` vaut 1 tous les jours.

Réserves :
1. **3 jours manquants** : 14/10/2023, 28/10/2023, 01/02/2025 (ce dernier en hiver). Il faut écrire « aucune heure orange ni rouge dans les jours publiés ».
2. Description ODRÉ : « Il s'agit des derniers signaux Ecowatt publiés pour les 24 pas horaires ». Le jeu ne conserve donc **pas les prévisions** J-3 à J-1. Un orange prévu puis levé n'y apparaît pas.
3. **Rupture d'échelle avant septembre 2022** : l'ancien jeu `signal-ecowatt` (16/11/2020-31/08/2022) est régional, par quarts de journée, et suit une autre échelle de 1 à 4 (« 3 : La consommation d'électricité dans notre région est trop élevée »). On y trouve des valeurs 2 et 3 (janvier 2021, janvier 2022, 04/04/2022). Ne pas écrire « jamais d'alerte Ecowatt » sans dater ; ne pas mettre bout à bout les deux séries.

### 15. BE2025, p. 10 : pointe de 88 GW

**Verdict : exact.** Citation : « La pointe annuelle de consommation a cependant été relevée le 14 janvier à 9 h (lors de la montée en charge du matin). […] la pointe de consommation de 2025 s'est établie à son niveau le plus élevé depuis 2021, en atteignant 88 GW. »

Recoupement éCO2mix définitif (`data/raw/eco2mix_cons_def/2025.parquet`) : maximum de **87 713 MW** le 14/01/2025 à 09:00 (heure légale), puis 87 683 MW à 09:30. Piège : la série horaire du site (`data/export/horaire/2025.csv`) affiche 87 438 MW sur l'heure 07:00Z, soit 08:00-09:00 heure de Paris, à cause de la moyenne et de la convention d'horodatage. On ne retrouve pas « 88 GW à 9 h » sur la courbe horaire du site. Il faut le dire si les deux apparaissent côte à côte.

### 16. Effacements (synthèse hiver p. 13) et rapport d'enchère

**Verdict : exact ; rapport d'enchère trouvé.**
- Synthèse hiver 2026-2027, p. 13 : « Au cours de l'enchère du mécanisme de capacité organisée le 6 juillet 2026 au titre de la période de livraison 2026-2027, 4,4 GW de capacités d'effacement de consommation ont été contractualisées. »
- Rapport d'enchère RTE (17/07/2026), p. 10 : filière Effacement, 5 031 MW certifiés, **4 361 MW contractualisés** (86,7 %). p. 9 : « Prix d'équilibre de l'enchère 28 182,99 €/MW » ; « Volume total de capacités retenues à l'enchère 82 446,8 MW » ; filière marginale « Thermique CCG ». Le chiffre d'EDF est donc confirmé par RTE.

Pièges :
- Ce sont des **MW certifiés**, pas une puissance d'effacement physique. Ne pas comparer aux « capacités d'effacement estimées à 3,7 GW » de la synthèse de l'hiver 2025-2026 (p. 9), qui est une autre grandeur.
- **Tout le monde n'est pas payé 28 182,99 €/MW** (p. 12) : « 11 487,1 MW seront rémunérés au prix d'équilibre de l'enchère […] 70 900,5 MW seront rémunérés au prix plafond intermédiaire établi à 15 000 €/MW ». Rémunération prévisionnelle totale : 1 394 416 924,8 € HT. L'effacement est payé au prix d'équilibre (4 360,5 MW), le nucléaire au plafond (44 754,8 MW).
- Volume réservé aux flexibilités (p. 11) : 4 700 MW, dont 2 925,6 MW d'effacement ; « prix d'équilibre des flexibilités » 14 967,2 €/MW, inopérant ici parce qu'il est inférieur au prix général.
- Unité : €/MW certifié **pour la période de livraison** (1er novembre 2026-31 mars 2027), pas €/MW-an ni €/MWh.
- Le volume contractualisé (82 446,8 MW) dépasse le besoin « Cref » de 79 000 MW de 3 446,8 MW (p. 9) en raison de l'élasticité de la courbe de demande. Ce n'est pas une « marge » au sens du BP.

### 17. ODRÉ `volumes-actives-ma` : situations tendues

**Verdict : exact.** Jeu retéléchargé le 26/11/2026 : `nb_situations_tendues_h_en_1_2j` vaut **45 (2024)** et **68 (2025)** ; à la baisse : 114 et 137. Unité : **demi-journées**. Le jeu va de 2004 à 2025 ; il a été modifié le 25/02/2026.

Définition :
- Bilan électrique 2022 en ligne (analysesetdonnees.rte-france.com/bilan-electrique-flexibilites, lu par un outil de récupération web) : les périodes de situation tendue sont celles où « les offres d'ajustement disponibles sont susceptibles de ne pas se révéler suffisantes », et elles sont « signalées aux acteurs par l'envoi de "messages de manque d'offres" » ; le graphique compte « le nombre de demi journées tendues à la hausse ou à la baisse ».
- Règles de marché, chap. 2 (V02, 01/01/2026), p. 63, art. 2.K.4.1 : « Les Offres d'Ajustement sont réputées insuffisantes pour traiter l'Equilibre P=C lorsque la Marge Opérationnelle est inférieure à la Marge Requise. » Art. 2.K.4.2 : RTE publie alors « un message d'information » invitant à soumettre de nouvelles offres. Cela reste distinct du « passage en mode dégradé » (art. 2.K.4.3).

Piège : c'est un indicateur **opérationnel de réserves d'équilibrage** (J-1 et infrajournalier). Ce n'est pas un indicateur d'adéquation. En 2025, il monte (45 → 68) alors que les marges d'adéquation sont au plus haut. Il ne se compare ni aux marges du BP ni à Ecowatt.

---

## Les cinq points les plus importants

1. **Le jeu EDF « EDF SA » contient des unités belges (Luminus), et une ligne n'est pas un événement.** Il faut garder une version par identifiant, exclure les types `Chronique*` (Pmax et Pdispo à 0) et appliquer la règle du minimum en cas de chevauchement. L'historique s'arrête au 07/09/2026.
2. **Les marges de 8 à 10 GW sont antérieures aux hypothèses de l'hiver 2026-2027.** La synthèse de novembre 2026 ne donne plus de marge en GW. Le mécanisme de capacité retient le scénario lent (Cref 79 GW, marge 9,5 GW certifiés). Le nucléaire certifié à l'enchère est de 44,8 GW, contre 48,5 GW projetés : ce 48,5 GW « certifié » n'est pas le 48,5 GW de disponibilité moyenne de la synthèse hiver.
3. **Ne pas additionner les 3 TWh (prix négatifs) et les 0,1 TWh (RTE).** Le texte même de RTE les fait se recouvrir. De même, la modulation nucléaire (« ~30 TWh », « 33 TWh ») couvre toutes les causes, pas la seule absence de débouchés, et chevauche le taux de disponibilité REMIT (arrêts pour économie de combustible comptés deux fois).
4. **RTE ne fournit ni la contribution des data centers à la pointe ni l'équivalence « 1 GW de consommation = 1 GW de marge ».** Ses propres méthodes disent que la contribution au risque dépend du profil de charge. Toute équivalence de ce type est un calcul du site, à afficher comme tel. Les trois « 20 / 20 / 90 % » sont trois grandeurs différentes, et aucune n'est une puissance à la pointe.
5. **Le prix de 28 182,99 €/MW n'est payé qu'à 11,5 GW sur 82,4 GW** (70,9 GW au plafond de 15 000 €/MW). Les 4,4 GW d'effacement sont des MW certifiés. Le fuseau des dates EDF est l'heure de Paris : c'est établi par les données, pas par une documentation lisible.

## Doutes et limites de cette contre-vérification

- Notices EDF REMIT et étude modulation EDF : non lues directement (HTTP 403). Les citations viennent d'extraits de recherche ou du communiqué de presse.
- La définition des « situations tendues » vient d'une page web du BE2022, lue par un outil qui résume. Les fragments entre guillemets sont ceux qu'il a rendus ; à relire sur la page avant publication.
- Le test du fuseau horaire repose sur la convention d'horodatage éCO2mix du projet (pas de 30 min). Il discrimine sans ambiguïté un décalage de 1 à 2 h, mais pas un décalage de ± 30 min.
- Je n'ai pas recalculé le taux de disponibilité REMIT (affirmation 2) à partir du fichier EDF. C'est le bon recoupement à faire avant de publier un indicateur dérivé de ce fichier.
