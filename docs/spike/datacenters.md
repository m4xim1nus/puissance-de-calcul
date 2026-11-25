# Spike « data centers » : combien, où, et la pyramide des annonces

*Rédigé le 25/11/2026. Périmètre : France métropolitaine. Aucun chiffre n'est cité de mémoire : chacun renvoie à une URL, à une date de publication et à une page (numérotation **du PDF**, pas la pagination imprimée) ou à un tableau. Quand un point n'a pas pu être vérifié dans une source primaire, c'est écrit.*

Artefacts du spike :

- base amorce des sites : `data/spike/sites_datacenters.csv` (32 lignes) ;
- échantillons bruts : `data/raw/spike/datacenters/` (Overpass brut, extraction OSM métropole, taux de remplissage, soutirages RPT section J (ODRÉ), classeur SDES 2024, communes géocodées, 4 PDF sources clés dans `docs/`) ;
- script : `pipeline/explo/spike_datacenters.py` (sous-commandes `overpass`, `communes`, `odre`, `sdes` ; bibliothèque standard uniquement).

## Conventions (à garder partout sur le site)

Quatre grandeurs différentes circulent sous le mot « puissance ». Les sources les mélangent, souvent dans la même phrase :

| Grandeur | Unité | Ce que c'est | Exemple |
|---|---|---|---|
| Puissance **recherchée / annoncée** | MW, GW | intention d'un porteur ou d'un État | 28,6 GW « recherchés » (gouvernement, 30/01/2026) |
| Puissance de **raccordement réservée** (PTF signée) | MW, GW | droit d'accès au réseau, sans engagement de consommer | 14 GW de PTF data centers au 15/11/2025 (RTE) |
| Puissance **IT** (« MW IT ») | MW | puissance utile des serveurs, hors froid et pertes | 75 MW IT pour DC01 de Data4 PAR3 (MRAe) |
| Puissance **appelée** (moyenne ou maximale) | MW | ce qui transite réellement | 0,035 GW au maximum en 2024 pour les data centers raccordés au RPT entre 2022 et 2024 (RTE) |

L'énergie (TWh/an) se déduit d'une puissance **appelée moyenne** × 8 760 h, **jamais** d'une puissance de raccordement. Repère : 1 GW appelé en continu ≈ 8,76 TWh/an.

---

## 1. Combien aujourd'hui ?

### 1.1 Les sources, de la plus étroite à la plus large

| Source (date de publication) | Périmètre | Année | Énergie | Puissance | Où dans le document |
|---|---|---|---|---|---|
| RTE, *Bilan électrique 2025*, rapport complet (mars 2026) [1] | data centers « sur site dédié » raccordés au **réseau de transport** (RPT) | 2025 (2024) | « près de 1 TWh en 2025 et environ 0,8 TWh en 2024 » | raccordement de 40 à 240 MW par site, **770 MW** au total fin décembre 2025 ; « taux moyen d'utilisation de la puissance de raccordement […] 22 % » | p. 18-19 du PDF, fig. 1.15 |
| RTE, *Tableau de bord de suivi de l'électrification* (juillet 2026) [2] | RPT | 2022-2025 | — | **0,63 GW** de puissance de raccordement mise à disposition entre 2022 et 2025 ; **0,035 GW utilisés au maximum en 2024** par les data centers raccordés entre 2022 et 2024 | p. 25 du PDF |
| idem [2] | **réseau de distribution Enedis** (RPD) | 2024-2025 | « ~ 3 TWh en 2024 » | « 0,9 GW en fonctionnement en 2025 », « ~ 400 datacenters en opération » | p. 26 du PDF |
| RTE, *Bilan prévisionnel 2025-2035*, chapitre Consommation (23/12/2025) [3] | (a) RPT seul ; (b) tous les data centers sur sites dédiés ; (c) + centres internes | 2024 | (a) « inférieur à 1 TWh » ; (b) « de l'ordre de 4 à 5 TWh » ; (c) « entre 5 et 10 TWh » | — | p. 27 du PDF, § 2.5.2 |
| SDES, *La consommation d'électricité des data centers en 2024* (02/07/2026) [4] | points de livraison > 1 GWh/an (données locales de l'électricité + base OPERAT ADEME) | 2024 | **4,34 TWh** pour 471 data centers ; total estimé « 4,3 à 6 TWh » ; Île-de-France 63 % | — | classeur xlsx, Figure 1 (téléchargé : `sdes_datacenters_2024_donnees.xlsx`) |
| SDES, *… entre 2018 et 2023* (16/10/2025) [5] | idem | 2023 | 3,9 TWh pour 460 sites ; total « 4 à 6 TWh » | — | page web (cité aussi par RTE [1], note 29) |
| Arcep, *Enquête annuelle pour un numérique soutenable*, 5e édition (mai 2026) [6] | 23 opérateurs de **colocation** interrogés, ~160 centres, « environ 50 % » des centres de colocation (base 2020) | 2024 | **2,7 TWh** dont 1,9 TWh pour l'IT | « près de **600 MW** » de puissance IT maximale admissible ; PUE moyen 1,42 | p. 6-8, 19, 26-27 du PDF |
| ADEME, *Prospective d'évolution des consommations des centres de données en France de 2024 à 2060*, synthèse (janvier 2026) [7] | inventaire de 352 centres actifs + extrapolation des salles internes | 2024 | **8,16 TWh** inventoriés (colocation 6,46 ; privés 1,34 ; public 0,21 ; HPC 0,15) + 3,5 TWh modélisés = **≈ 10 TWh** (9,91 dans le tableau) | — | p. 5-6 et 8 du PDF |
| RTE, page « Les data centers en chiffres clés » (publiée le 21/05/2025, date affichée 01/06/2026) [8] | non précisé | **non précisée** | « environ 10 TWh », « environ 2 % » | « environ 300 data centers », dont **8** raccordés au RPT pour **800 MW** cumulés | page web |
| Institut Paris Région, note de novembre 2026, via Banque des Territoires (10/11/2026) [9] | Île-de-France, « puissance installée » (IT ou raccordement : non précisé) | 2025 | — | 1,01 GW en Île-de-France = « environ 64 % » du national ; 151 data centers au 01/01/2026 | article ; note IPR non lue |
| AIE, *Energy and AI* (avril 2025) [10] | **pas de chiffre France** | 2024 | Europe : « an estimated 70 TWh in 2024 » | — | p. 58 du PDF |
| Commission européenne, COM(2026) 500 (21/09/2026) [11] | UE | 2024 | 68 TWh (cité de l'AIE, *Key Questions on Energy and AI*) | — | p. 3 du PDF |

Consommation intérieure 2025 de référence : **451 TWh** (RTE, *Bilan électrique 2025*, p. 6 du PDF [1]).

### 1.2 Tests de cohérence

1. **Le bilan RPT + RPD boucle.** RPT ≈ 0,8 TWh (2024) + Enedis ≈ 3 TWh (2024) ≈ **3,8 TWh**. C'est cohérent avec « 4 à 5 TWh » de RTE pour les sites dédiés [3] et avec les 4,34 TWh du SDES pour les sites > 1 GWh [4], à ±15 % près. Les trois sources reposent largement sur les mêmes compteurs, donc **ce n'est pas un recoupement indépendant**.
2. **Facteurs d'utilisation** (calculs du spike) :
   - RPT : 1 TWh / 8 760 h ≈ 114 MW moyens pour 770 MW raccordés, soit **≈ 15 %**. RTE affiche 22 % ; la définition RTE du « taux moyen d'utilisation » n'est pas donnée p. 19 (pointe ou moyenne ?), écart non résolu.
   - Enedis : 3 TWh / 8 760 h ≈ 340 MW pour 0,9 GW, soit **≈ 38 %**.
   - Arcep : 1,9 TWh IT ≈ 217 MW IT moyens pour ~600 MW IT admissibles, soit **≈ 36 %**. Le PUE implicite vaut 2,7 / 1,9 = 1,42, ce qui boucle avec le PUE publié.
3. **Arcep × 2 ≈ 5,4 TWh pour la colocation.** C'est plus proche des 6,46 TWh « colocation » de l'ADEME que des 4,34 TWh tous types du SDES. **Contradiction non résolue** : l'inventaire ADEME semble au-dessus des compteurs SDES/RTE. Cause probable, non vérifiée : l'ADEME estime une partie des consommations à partir de puissances déclarées et d'hypothèses, plutôt que de les mesurer. Méthodologie détaillée de l'ADEME non lue.
4. **Le « 10 TWh » n'est pas le même chiffre partout.** Pour l'ADEME, c'est inventaire + salles internes modélisées. Pour RTE [3], c'est la borne haute avec les centres internes. Sur la page RTE [8], le périmètre et l'année ne sont pas donnés. **À ne pas comparer aux 4-5 TWh sans le dire.**
5. **Écart entre décomptes de puissance installée.** RTE compte 770 MW (RPT) + 0,9 GW (Enedis), soit **≈ 1,7 GW raccordés**. L'IPR calcule ~1,6 GW « installés » (1,01 / 0,64, calcul du spike). L'Arcep donne 600 MW IT pour la seule colocation interrogée. Les ordres de grandeur se tiennent si l'on garde à l'esprit l'écart raccordement > installé > IT > appelé.

### 1.3 Sources non lues ou non retrouvées

- AIE : aucun chiffre France dans *Energy and AI* ni dans *Key Questions on Energy and AI* (avril 2026). J'ai cherché « France » dans les deux PDF : seuls apparaissent des exemples de cas d'usage. **Ne pas citer l'AIE pour la France.**
- JRC (Kamiya & Bertoldi, 2024, doi:10.2760/706491) : référencé par COM(2026) 500, non lu.
- France Datacenter (association) : pas d'étude primaire trouvée. Les chiffres de cabinets (Cushman & Wakefield : 703 MW opérationnels à Paris ; « 714 MW fin 2024 » relayé par des sites secondaires) ne sont **pas retenus**, faute de document primaire lu.

---

## 2. Trajectoires 2030 et 2035

### 2.1 RTE, Bilan prévisionnel 2025-2035 : la référence, avec ses hypothèses

Source : chapitre Consommation, 23/12/2025 [3], § 2.5.3 et figure 2.10, p. 27-28 du PDF. Recoupement : *Principaux résultats*, 16/12/2025 [12], tableau p. 25 du PDF.

| Trajectoire | 2030 (TWh) | 2035 (TWh) | Hypothèse « GW » | Taux d'utilisation |
|---|---|---|---|---|
| Décarbonation rapide | **15** (≈ 5 actuels + 10) | **≈ 32** | **4,3 GW** de projets RPT concrétisés d'ici 2030 (≈ 60 % des projets dotés de droits d'accès pour un raccordement d'ici fin 2029) + 2,4 TWh de croissance sur le RPD | 20 % en 2030 |
| Décarbonation lente | **10** (≈ 5 + 6) | **21** | **2,4 GW** (≈ 30 %) + 1,8 TWh sur le RPD | 20 % en 2030 |
| Stagnation | « progression très lente » | non chiffrée | — | — |
| *Pour mémoire : BP2023, scénario A-référence* | *+10 TWh* | *+20 TWh* | — | — |

Contrôle arithmétique (calcul du spike) : 4,3 GW × 20 % × 8 760 h = 7,5 TWh, + 2,4 TWh = **9,9 TWh**, ce qui correspond au « +10 TWh » de RTE. Pour la trajectoire lente : 2,4 × 0,2 × 8 760 = 4,2 TWh, + 1,8 = **6,0 TWh**, ce qui correspond au « +6 TWh ». L'assiette implicite (4,3 / 0,6 ≈ 2,4 / 0,3 ≈ **7-8 GW**) recoupe les « ~7 GW pour mise en service d'ici 2030 » du tableau de bord RTE [2] (p. 25).

**En GW pour 2035 : RTE ne publie pas de puissance raccordée ou appelée** dans les passages lus. 32 TWh correspondent à ≈ 3,65 GW appelés en moyenne (calcul du spike, pas un chiffre RTE).

### 2.2 Une contradiction à lever : la page web de RTE

La page « Les data centers en chiffres clés » [8], datée du 01/06/2026, annonce **15 à 20 TWh en 2030** et **23 à 28 TWh en 2035**, en les attribuant au BP 2025-2035 (« décarbonation rapide »). Ces valeurs **ne correspondent pas** au document du BP (10-15 et 21-32). Elles sont reprises telles quelles par la presse : IT for Business, 09/11/2026 [13] ; Institut Quorum. Hypothèse, non vérifiée : la page web inclurait les centres internes, comme son « 10 TWh » actuel. **Pour le site, citer le document du BP et signaler l'écart.**

### 2.3 Autres trajectoires

- **ADEME** [7], tableau p. 8 du PDF, TWh/an **sur le territoire français** :

  | Scénario | 2024 | 2030 | 2035 |
  |---|---|---|---|
  | Tendanciel | 9,91 | 20,75 | 36,73 |
  | Génération frugale | 9,91 | 14,87 | 11,58 |
  | Coopérations territoriales | 9,91 | 17,10 | 17,54 |
  | Technologies vertes | 9,91 | 19,34 | 32,14 |
  | Pari réparateur | 9,91 | 19,28 | 33,04 |

  Le périmètre est plus large que celui de RTE : salles internes incluses, base ≈ 10 TWh. Les chiffres « import » (data centers à l'étranger servant des usages français) ne pèsent pas sur le système électrique français.
- **AIE** [10] : pas de France. Europe : « grows by more than 45 TWh (up 70%) » entre 2024 et 2030 (p. 64 du PDF). **Commission** [11] : UE 68 TWh (2024), 114 TWh (2030), soit 3,2 % de la demande (p. 3 du PDF, d'après l'AIE).
- **Institut Paris Région** [9] : Île-de-France, 6,5 à 8 GW « installés » en 2040. Nature de la puissance non précisée ; note non lue.
- **Rexecode** (juillet 2026) : ≈ 7,9 GW en 2035 (fourchette 5,7-10,9 GW), relayé par des sites secondaires. **Non lu, non retenu.**

---

## 3. La pyramide : annonces → demandes de raccordement → raccordements signés → mises en service → consommation

### 3.1 Les étages chiffrés

| Étage | Valeur | Date de la donnée | Source |
|---|---|---|---|
| **Annonces** (intentions) | « la puissance électrique recherchée atteint **28,6 GW** », 52 entreprises accompagnées | 30/01/2026 | Ministère (DGE), communiqué des Rencontres des centres de données [14] |
| Annonces (Sommet IA) | « 5 GW de capacité de centres de données déjà en cours de connexion » ; 109 Md€ | 09/02/2025 | Élysée, dossier de presse, p. 21 du PDF [15] |
| Annonces (Choose France 2026) | SoftBank : 3,1 GW d'ici 2031 (phase 1, 45 Md€), jusqu'à 5 GW (75 Md€) | 30/05/2026 | TechCrunch [16] ; RTE [8] |
| **Capacité réservée chez RTE** (demandes acceptées, PTF signées, phases travaux et suspendues comprises) | **~5 GW**, ~40 projets | fin 2024 | RTE [8] |
| idem | **~14 GW** data centers, « y compris ceux s'inscrivant dans une procédure fast track », sur ~30 GW tous usages | 01/11/2025 | BP2025, *Principaux résultats*, p. 21 du PDF [12] |
| idem | **14 GW** contractualisés, dont **~7 GW pour mise en service d'ici 2030** | 15/11/2025 | Tableau de bord RTE, p. 25 du PDF [2] |
| idem | **~18 GW**, ~80 projets ; la majorité entre 100 et 200 MW, une dizaine au-dessus de 400 MW ; Île-de-France ~7 GW, Hauts-de-France ~6 GW | mai 2026 | RTE [8] |
| « Sécurisés » au sens de l'État | **5,8 GW** « sécurisés par un site et faisant l'objet d'engagements de raccordement » | 30/01/2026 | Ministère [14] (définition non précisée) |
| **Raccordement signé, fast-track** | Campus IA (Fouju) : 240 MW fin 2027, 700 MW avant fin 2029, jusqu'à 1 400 MW | 26/01/2026 | RTE, communiqué [17] |
| **Raccordés** (RPT) | **770 MW** de raccordement fin 2025 | 31/12/2025 | RTE, BE2025, p. 19 [1] |
| idem | 8 data centers, 800 MW cumulés | 2026 (date exacte non indiquée) | RTE [8] |
| idem, flux | 0,63 GW mis à disposition entre 2022 et 2025 | 15/11/2025 | RTE [2] |
| Raccordés (Enedis) | 0,9 GW, ~400 sites | 2025 | RTE [2], p. 26 |
| **Consommation effective** (RPT) | ≈ 1 TWh, soit ≈ 114 MW moyens (calcul) | 2025 | RTE [1] |
| idem, **cohorte récente** | **0,035 GW au maximum en 2024** pour les data centers raccordés entre 2022 et 2024 | 2024 | RTE [2], p. 25 |

**Lecture.** Au niveau national, sur le seul réseau de transport : environ 28,6 GW sont recherchés, environ 18 GW réservés (mai 2026), dont environ 7 GW visent une mise en service avant 2030. Seulement 0,77 GW sont raccordés, et environ 0,11 GW sont appelés en moyenne. Les opérateurs eux-mêmes estiment qu'il faut « 10 à 15 ans » pour atteindre ~80 % de la puissance demandée [8]. Le BP note aussi que des développeurs « ont parfois sécurisé un accès au réseau sur plusieurs points du territoire pour des projets en réalité similaires » [3, p. 6 du PDF].

**Zoom Île-de-France** (RTE, Bilan électrique IdF, 09/07/2026 [18], p. 2) : **640 MW** raccordés sur 6 sites ; **8 GW** « en cours de raccordement » sur une cinquantaine de sites ; **7 GW** « à l'étude » sur une trentaine de sites. La page nationale [8] parle de « ~7 GW réservés » en Île-de-France, puis plus bas de 6,5 GW « demandés » : les définitions ne sont pas alignées entre documents RTE.

**Exemple à l'échelle d'un projet** (avis MRAe Equinix PA16, Argenteuil, 23/04/2025 [19], p. 14-15) : raccordement estimé à ~55 MW, mais « la demande formulée auprès de RTE porte sur une puissance de 240 MW » pour d'autres projets envisagés. C'est le surdimensionnement de la file en un seul dossier.

### 3.2 Procédures

- **Fast-track.** Délibération CRE n° 2025-120 du 07/05/2025 [20] et communiqué du même jour : « consommateurs de très forte puissance (entre 400 MW et 1 GW) », 400 kV, « à horizon 2028-2029 », sur des sites « préalablement identifiés par l'État ». Le modèle de convention a été approuvé le 24/06/2025 (délibération 2025-166). Conditions détaillées dans la fiche RTE de décembre 2025 [21] (archivée dans `docs/`) :
  - « réfaction » de 30 % sur la liaison principale ;
  - contribution aux coûts de congestion pendant 6 ans ;
  - acomptes de 30 % puis 60 % ;
  - permis de construire sous 15 mois ;
  - délais de raccordement « tous à moins de 4 ans ».
- **Cinq sites fast-track** (RTE [21], [22], [23] ; ministère [14]) :

  | Site | Commune | Pré-réservation RTE | Porteur connu |
  |---|---|---|---|
  | ZAC des Bordes | Fouju (77) | 700 MW | Campus IA, contrat signé à 1 400 MW à terme |
  | Ancienne centrale EDF de Montereau | Vernou-la-Celle-sur-Seine (77) | 700 MW | OpCore, en négociation exclusive avec EDF (CP EDF du 17/11/2025) |
  | Parc des Soufflantes | Escaudain (59) | 700 MW | Data4 (CP du 12/06/2026 : « 700MW sur 33ha ») |
  | ZAC du Bosquel | Bosquel (80) | 1 GW | Fluidstack retiré (Bloomberg, 18/03/2026) ; cité dans la phase 1 SoftBank |
  | Zone « Grande Industrie » du Grand Port Maritime de Dunkerque | Bourbourg (59) | 700 MW (à compter du 15/12/2025) | non identifié avec certitude |

  Total pré-réservé : **3,8 GW** (calcul du spike). Selon RTE, au moment de Choose France 2026, « quatre sites sur cinq étaient alloués » [8] ; lesquels exactement n'est pas dit.
- **Zones d'accueil mutualisées** (RTE [8]) : 300 M€ ; sud de l'Île-de-France ~1 200 MW ; Plan-de-Campagne ~500 MW ; zones industrialo-portuaires de Dunkerque, Le Havre et Fos. La base juridique (art. L. 342-2 et L. 342-18 du code de l'énergie, délibération CRE du 07/11/2024) est citée dans la délibération CRE 2026-173.
- **Réforme de la file d'attente.** La délibération CRE n° 2026-32 du 04/02/2026 [24] ne change pas les règles d'entrée. Elle demande à RTE de « la saisir au plus tard le 1er octobre 2026 d'une première évolution de la procédure intégrant une meilleure prise en compte de la maturité des projets » (p. 10 du PDF). RTE a consulté sur une « refonte » de type « premier prêt, premier servi » [13]. **Au 25/11/2026, aucune délibération CRE approuvant la nouvelle règle n'a été trouvée.**
- **Loi.** La loi n° 2026-403 du 26/05/2026 de simplification de la vie économique ouvrirait la qualification de « projet d'intérêt national majeur » (PINM) aux data centers, par décret (article 15 selon le cabinet Gossement et DCmag). **Texte non lu sur Légifrance : à vérifier.** Aucun décret PINM data center n'a été trouvé ; une seule source secondaire (DCmag, 07/10/2026, via GridReadiness) affirme qu'aucun n'existait mi-octobre 2026.
- **Fiscalité.** Un décret durcissant l'accès au taux réduit d'accise a été annoncé le 09/11/2026 [13]. **Non publié à ma connaissance.**

### 3.3 Les sites « clés en main » et sites propices de l'État

| Moment | Nombre | Ce qui est publié | Source |
|---|---|---|---|
| Sommet IA, 09/02/2025 | « au moins **35** sites », 1 200 ha, « 15 d'entre eux en mesure d'atteindre au moins 750 MW à terme », 16 disponibles immédiatement et 9 d'ici 2028, 12 « Sites clé en main France 2030 », 4 sites EDF, au moins 15 friches | **aucune liste nominative** | Élysée, p. 21 du PDF [15] |
| Choose France 2025, puis guide DGE du 25/11/2025 | **63** sites, « quatre d'entre eux bénéficient » du fast-track | **carte par région** sans nom de site, avec des pastilles (50 MW / 250 MW / > 250 MW, « jusqu'à 1 GW ») | DGE, guide, p. 13 du PDF [25] |
| Rencontres, 30/01/2026 | 63 identifiés, **26 « déjà sécurisés par un porteur de projet »**, 5 fast-track | pas de liste | Ministère [14] |
| Page RTE (2026) | « 65 sites » | pas de liste | RTE [8] |

Selon les auteurs de la carte « Le nuage était sous nos pieds », une liste de **26** sites « clés en main » aurait été révélée en juin 2025 par Contexte et Politico (article sous abonnement). **Non vérifiée.** Ne pas la confondre avec les 26 sites « sécurisés » de janvier 2026. Nos lignes `site_identifie_etat` du CSV ne contiennent que les sites **nommés officiellement** : les 5 fast-track et Plan-de-Campagne.

### 3.4 Grandes annonces et statut connu

| Annonce (date, source) | Puissance annoncée | Localisation | Échéance annoncée | Statut connu au 25/11/2026 |
|---|---|---|---|---|
| MGX / consortium franco-émirien, 09/02/2025 [15] p. 24 | campus de 1 GW, « jusqu'à 50 milliards d'euros » | non précisée en février 2025 | — | devenu **Campus IA** à Fouju : contrat de raccordement fast-track signé le 26/01/2026 (240 / 700 / 1 400 MW) [17]. Travaux et mise en service non vérifiés. |
| Fluidstack, 09/02/2025 [15] p. 26 | 1 GW, 10 Md€ | Bosquel (presse) | « lancement prévu pour 2026 » | **Retrait** selon Bloomberg (18/03/2026). Pas de communiqué Fluidstack trouvé. |
| Brookfield / Data4, 09/02/2025 [15] p. 25 | Data4 : tripler ses « plus de 500 MW » d'ici 2030 | plusieurs régions | 2030 | Escaudain : 700 MW confirmés (CP Data4, 12/06/2026). E-Valley (ex-BA 103) : « 1 GW à terme, première tranche de 300 MW », travaux annoncés au S2 2026 (info.fr, 11/06/2026). Choose France 2026 : +10 Md€ [8]. |
| Digital Realty, 09/02/2025 [15] p. 25 | 13 nouveaux sites pour « 666 MW de connexion électrique » | Marseille, région parisienne | — | MRS6 (Bouc-Bel-Air) : avis Ae du 12/06/2025. Le reste n'est pas suivi site par site. |
| evroc, 09/02/2025 [15] p. 26 | 96 MW | Mougins | « prévue pour 2025 » | **non vérifié** |
| Prologis, 09/02/2025 [15] p. 27 | 400 MW | Île-de-France | mise en service 2030 | non localisé, non suivi |
| Sesterce, 09/02/2025 [15] p. 27 | 600 MW d'ici 2028 (Grand Est) ; Drôme non chiffrée | Drôme, Grand Est | 2028 | non vérifié |
| Eclairion, 09/02/2025 [15] p. 25 | Bruyères-le-Châtel : « puissance finale de 100 MW » | 91 ; Bessé-sur-Braye (72) | — | Bruyères en service partiel (40 → 100 MW selon Le Monde Informatique, 17/11/2025) ; retenu par EDF à La Maxe et Richemont (57) |
| SoftBank, 30/05/2026 [16] | 3,1 GW (phase 1), jusqu'à 5 GW | Loon-Plage, Bosquel, Bouchain | 2031 | Bouchain : SoftBank « attributaire pressenti » d'EDF pour « un centre de données de 400 MW » (CP EDF, 30/05/2026) ; due diligence en cours |
| OpCore (EDF), 17/11/2025 | « plusieurs centaines de mégawatts », ~4 Md€ | ex-centrale de Montereau | première mise en service 2027 | négociations exclusives |

**Additionner ces puissances n'a pas de sens.** Elles mélangent IT, raccordement et objectifs commerciaux, et plusieurs se recouvrent : Bosquel (Fluidstack puis SoftBank), Dunkerque (site fast-track et SoftBank).

---

## 4. Où ?

### 4.1 OpenStreetMap (Overpass, horodatage OSM 25/11/2026 22:12 UTC)

Requête : `telecom=data_center` OU `building=data_center|datacenter`, zone `ISO3166-1=FR`, `out center tags`. Fichiers : `overpass_fr_datacenters_raw.json`, `osm_datacenters_fr_metro.csv`, `osm_quality.json`.

- **379 objets** pour la France entière, dont **375 en métropole** (emprise lat 41,2-51,2 / lon −5,6-9,8) : 363 `telecom=data_center` et 12 `building=data_center` seuls.
- Taux de remplissage en métropole :

  | Attribut | Taux |
  |---|---|
  | `name` | 77 % |
  | `operator` | 75 % |
  | `operator:wikidata` | 20 % |
  | `addr:city` | 21 % |
  | `website` | 12,5 % |
  | `ref:FR:SIRET` | 2,7 % |
  | `start_date` | 1,1 % |
  | `data_center:power` | **1,3 % (5 objets)** |

  Les 5 objets renseignés sont Digital Realty MRS1 à MRS4 (16, 16, 24, 20 MW) et Phocea DC (1,2 MW). La nature IT ou totale de ces puissances n'est pas précisée, ni leur source.
- **Bruit.** Les premiers opérateurs sont des opérateurs télécoms : Bouygues Télécom (26 + 4 sous une autre graphie), SFR (17), Orange (9). Beaucoup de ces objets sont des sites techniques réseau plutôt que des data centers au sens de RTE ou du SDES. Des campus sont découpés en bâtiments sans nom (Data4 Marcoussis/Nozay : une dizaine d'objets « data4 ») et il y a des doublons de nom (« OPCORE DC6-6 » ×2). Un objet « 1&1 Internet SE » à 48,97 N / 8,13 E, à la frontière allemande, est à contrôler.
- **Verdict.** OSM est utilisable comme **couche de localisation des sites connus** (coordonnées fiables à l'échelle du bâtiment), **pas pour la puissance** ni comme dénombrement. Les décomptes ne coïncident pas d'une source à l'autre : 375 objets OSM contre 352 (ADEME), 471 points de livraison > 1 GWh (SDES), ~300 (RTE), ~400 sur Enedis (RTE) et ~160 en colocation (Arcep).

### 4.2 Autres sources de localisation

| Source | Ouverte ? | Contenu utile | Limite |
|---|---|---|---|
| **SDES 2024** [4] (`sdes_datacenters_2024_donnees.xlsx`, Figure 3) | oui (publication statistique) | **classe de consommation par département** (< 2 / 2-10 / 10-100 / 100-300 / ≥ 300 GWh). ≥ 300 GWh : Nord, Essonne, Hauts-de-Seine, Seine-Saint-Denis | des classes, pas des valeurs ; pas de site. Petit écart interne : 4 339 GWh (Fig. 1) contre 4 348 GWh (Fig. 2) |
| **ODRÉ, soutirages RPT par section NAF**, pas de 30 min (Licence Ouverte) | oui | section **J** « Information et communication » : 2025 = 255,7 GWh, P moyenne 29 MW, P max 49 MW, ~6 points ; 2026 (janv.-août) : P moyenne ~50 MW | **ce n'est pas le périmètre data centers** (≈ 0,26 TWh contre ≈ 1 TWh selon RTE [1]) : beaucoup de data centers sont classés dans d'autres sections NAF, ou masqués par le secret statistique. Proxy horaire partiel, à manier avec prudence |
| **Avis MRAe / Ae (IGEDD)** | oui (documents administratifs publics) | pour chaque projet soumis à évaluation environnementale : commune, porteur, puissance (raccordement, IT ou « installée »), consommation annuelle estimée | ne couvre pas les sites existants ; le vocabulaire de puissance varie (voir Goodman Villeneuve-Saint-Georges : « 105 MW » mais 180 GWh/an) |
| Carte uMap « Le nuage était sous nos pieds » (mise à jour 25/11/2026) | **non** : la carte porte la mention « Aucune licence » | 358 existants (repris d'OSM), 128 projets (91 annoncés, 26 en instruction, 11 en construction), 20 sites « clés en main » non attribués, 39 oppositions | données non réutilisables sans accord ; consultée pour repérage, **non archivée** |
| datacentermap.com | **pas de licence ouverte identifiée** ; la page des conditions d'utilisation n'a pas pu être lue (HTTP 429) | — | ne pas utiliser sans accord |

### 4.3 Directive efficacité énergétique (UE) 2023/1791 et règlement délégué 2024/1364 : ce qui est effectivement publié

- **Obligation.** L'article 12 de la directive impose aux exploitants dont la puissance IT installée est d'au moins 500 kW de rendre publiques les informations de l'annexe VII. Le règlement délégué 2024/1364 (14/03/2024, JO du 17/05/2024) organise la base européenne. Échéances : « By 15 September 2024, then by 15 May 2025, and every year thereafter » (art. 3) [26].
- **Confidentialité** (art. 5 du règlement [26]) : la Commission et les États « shall keep confidential all information and key performance indicators for individual data centres ». Publication « in an aggregated manner, at Member State and Union level ». **Aucune donnée par site n'est publiée au niveau européen.**
- **Ce qui est publié** (COM(2026) 500, 21/09/2026 [11], p. 5-7 du PDF) :
  - première période (mai-septembre 2024) : **770** data centers déclarants, soit « around 36% » des centres estimés concernés ;
  - **France : environ 265 estimés et environ 137 déclarants** (lecture graphique de la figure 1, p. 6 du PDF ; valeurs approximatives) ;
  - PUE moyen UE 1,36 ;
  - « 70.1% of the reported data are deemed to be reliable » ;
  - seconde période : « at least 30% more data centres » (données préliminaires).
- **Tableau de bord** : la Commission renvoie à un tableau de bord « Policy Reporting Platform » de données agrégées, mis à jour mensuellement (https://link.europa.eu/q7x39t). **Non exploré dans ce spike**, ni export ni ventilation France vérifiés.
- **France.** L'Arcep a aligné sa collecte sur la directive fin 2024 et transmettra les données à la Commission « à partir de 2026 » (Arcep [6], p. 17 du PDF). Aucune publication française par site n'a été trouvée. L'obligation de « make publicly available » pèse sur chaque exploitant : on trouve des divulgations éparses sur les sites des opérateurs (par exemple un PDF Verizon France de juin 2026, repéré en recherche et non lu), **sans registre central**.

---

## 5. Chiffres clés candidats

Niveau de confiance : **A** = source primaire et recoupement indépendant ; **B** = source primaire, recoupement partiel ou de même origine ; **C** = source unique, secondaire ou définition floue.

| # | Chiffre | Source primaire | Recoupement | Confiance |
|---|---|---|---|---|
| 1 | Data centers sur sites dédiés : **4 à 5 TWh** en 2024, environ 1 % de la consommation (451 TWh) | RTE, BP2025, p. 27 [3] | SDES 4,34 TWh (> 1 GWh) [4] ; RPT 0,8 + Enedis ~3 TWh [1][2] (mêmes compteurs, pas indépendant) | **A−** |
| 2 | Data centers sur le RPT : **≈ 1 TWh en 2025**, **770 MW** raccordés fin 2025 | RTE, BE2025, p. 18-19 [1] | page RTE : 8 sites, 800 MW [8] (même émetteur) | **B** |
| 3 | Cohorte 2022-2024 sur le RPT : **0,035 GW appelés au maximum en 2024** pour 0,63 GW mis à disposition (2022-2025) | RTE, tableau de bord, p. 25 [2] | « 20 % » d'utilisation (BP2025 [12] p. 23 ; RTE [8]) ; ODRÉ section J P max 2024 = 35,3 MW (coïncidence possible, périmètre différent) | **B** |
| 4 | File RTE data centers : **~14 GW** (PTF, 01-15/11/2025), **~18 GW / ~80 projets** (mai 2026) | RTE [12] p. 21, [2] p. 25, [8] | gouvernement : 28,6 GW « recherchés », 5,8 GW « sécurisés » [14] (autres définitions) | **B** |
| 5 | ~7 GW de la file visent une mise en service avant 2030 | RTE [2] p. 25 | cohérent avec l'assiette implicite du BP (2,4 / 0,3 ≈ 4,3 / 0,6) [12] | **B+** |
| 6 | Trajectoire RTE sites dédiés : **10-15 TWh en 2030, 21-32 TWh en 2035** | BP2025, fig. 2.10, p. 28 [3] | *Principaux résultats* p. 25 [12] (+6 / +10 TWh) ; **contredit** par la page web RTE (15-20 / 23-28) [8] | **B** (document) ; page web **C** |
| 7 | 5 sites fast-track, **3,8 GW** pré-réservés (700 ×4 + 1 000) | RTE [22][23] | ministère [14] ; fiche RTE [21] | **A** |
| 8 | Campus IA Fouju : 240 MW (fin 2027) → 700 MW (fin 2029) → 1 400 MW | RTE, communiqué du 26/01/2026 [17] | non recoupé (concertation CNDP non lue) | **B** |
| 9 | Colocation (23 opérateurs) : 2,7 TWh, 600 MW IT, PUE 1,42 | Arcep [6] | PUE implicite 2,7 / 1,9 = 1,42 (cohérence interne) | **B** |
| 10 | Inventaire ADEME : 352 centres, 8,16 TWh ; ≈ 10 TWh avec les salles internes | ADEME [7] | RTE « 5 à 10 TWh » avec centres internes [3] ; mais écart de ~+50 % avec SDES sur la colocation | **C+** |
| 11 | 35 sites (fév. 2025) → 63 sites (2025) → 26 sécurisés (janv. 2026) | Élysée [15], DGE [25], ministère [14] | aucune liste publique : nombres **invérifiables** site par site | **B** (nombres) ; **C** (contenu) |
| 12 | Base UE (EED) : 770 déclarants dans l'UE, France ≈ 137 sur ≈ 265 estimés | COM(2026) 500 [11] | lecture graphique, non recoupée | **C** (France) |
| 13 | Île-de-France : 640 MW raccordés (6 sites RPT), 8 GW en cours, 7 GW à l'étude | RTE, Bilan IdF [18] | IPR : 1,01 GW « installés » en IdF [9] (autre définition) ; Arcep : > 70 % de la puissance IT en IdF | **B** |

---

## 6. Ce qui n'existe pas en open data

- **Aucun registre public des data centers avec localisation et puissance.** Ni l'État, ni RTE, ni Enedis, ni l'UE n'en publient : la base EED est confidentielle par site. OSM localise mais ne mesure pas.
- **La file d'attente RTE des consommateurs n'est publiée qu'en agrégats** (national, régional, par communiqué ou page web), à des dates et sous des définitions changeantes. Il n'existe pas de jeu ODRÉ « file d'attente consommateurs » par poste ou par projet, contrairement à Caparéseau pour la production. *Recherche sur le catalogue ODRÉ (mots-clés « attente », « datacenter », « grands consommateurs ») : rien de tel.*
- **Les listes des 35, 63 et 26 sites de l'État ne sont pas publiées.** Seules des cartes à pastilles régionales et le nom des 5 sites fast-track le sont.
- **Pas de courbe de charge des data centers.** Seuls existent les agrégats annuels (SDES, RTE) et un proxy partiel au pas de 30 min (ODRÉ, section NAF J sur le RPT).
- **Rien sur le statut réel des annonces** (permis, chantier, mise en service), hors communiqués d'entreprises et avis d'autorité environnementale. Il faudrait suivre les avis MRAe/IGEDD et les registres d'enquête publique, projet par projet.
- **Pas de publication française des déclarations EED** et pas de ventilation France exploitable au-delà d'un graphique.
- **Pas de décret PINM data center trouvé** à ce jour. Le texte de la loi 2026-403 n'a pas été lu dans sa version Légifrance.

---

## 7. Questions à trancher par l'auteur

1. **Chiffre de tête « aujourd'hui ».** Je propose **4 à 5 TWh** (sites dédiés, RTE/SDES), avec « jusqu'à ≈ 10 TWh en incluant les salles informatiques internes » en second rang. Le « 10 TWh ≈ 2 % » de la page RTE est sans année ni périmètre. D'accord pour ne pas le mettre en avant ?
2. **Trajectoire de référence.** Faut-il citer le document du BP 2025 (10-15 / 21-32 TWh) et signaler explicitement l'écart avec la page web RTE (15-20 / 23-28) ? Faut-il écrire à RTE pour lever l'ambiguïté ?
3. **Vocabulaire de la pyramide.** Je propose d'adopter cinq étages : recherché (État) → réservé (PTF RTE) → signé / fast-track → raccordé → appelé. Les « 5,8 GW sécurisés » du ministère n'ont pas de définition : faut-il les afficher ?
4. **Nomenclature du CSV.** Il manque des statuts qui se présentent déjà : `raccordement_signe` (Fouju), `en_autorisation` (tous les avis MRAe), `abandonne` (Fluidstack). Faut-il les ajouter ?
5. **Couche « Où ».** Deux options : OSM nettoyé (filtrer les sites télécoms) + avis MRAe pour les projets + classes départementales SDES ; ou couche minimale « projets ≥ 40 MW » uniquement. Le suivi systématique des avis MRAe (Île-de-France surtout) est la meilleure source ouverte de puissance par projet, mais il demande du temps de collecte.
6. **Carte « Le nuage était sous nos pieds ».** Elle est sans licence. Faut-il contacter les auteurs pour une réutilisation (128 projets, 39 oppositions) ?
7. **Demande de données.** Faut-il solliciter RTE (file par région ou par poste, cohortes de montée en charge) et la DGE (liste des 63 sites) ? Si oui, ce serait au nom du projet.
8. **Proxy horaire.** La série ODRÉ « section J » au pas de 30 min est-elle acceptable dans le module « Quand ? », avec un avertissement de périmètre ? Ou faut-il plutôt un profil plat paramétré ?

---

## Références

1. RTE, *Bilan électrique 2025 — Rapport complet*, mars 2026. https://assets.rte-france.com/analyse-et-donnees/2026-03/BE2025%20-%20Rapport%20Complet.pdf (p. 6, 18-19)
2. RTE, *Tableau de bord de suivi de l'électrification*, juillet 2026. https://assets.rte-france.com/analyse-et-donnees/2026-07/Tableau-de-bord-de-lelectrification.pdf (p. 25-26) — archivé dans `data/raw/spike/datacenters/docs/`
3. RTE, *Bilan prévisionnel 2025-2035 — La consommation d'électricité*, 23/12/2025. https://assets.rte-france.com/prod/public/2025-12/2025-12-23-bilan-previsionnel-2025-consommation.pdf (p. 6-7, 26-28)
4. SDES, *La consommation d'électricité des data centers en 2024*, 02/07/2026. https://www.statistiques.developpement-durable.gouv.fr/la-consommation-delectricite-des-data-centers-en-2024 ; données : https://www.statistiques.developpement-durable.gouv.fr/media/9471/download?inline
5. SDES, *La consommation d'électricité des centres de données entre 2018 et 2023*, 16/10/2025. https://www.statistiques.developpement-durable.gouv.fr/la-consommation-delectricite-des-centres-de-donnees-entre-2018-et-2023 (non lu directement : chiffres pris dans le résumé de recherche et dans la note 29 de [1])
6. Arcep, *Enquête annuelle « pour un numérique soutenable »*, 5e édition, mai 2026. https://www.arcep.fr/fileadmin/user_upload/observatoire/enquete-pns/edition-2026/enquete-annuelle-pour-un-numerique-soutenable_edition2026_mai2026.pdf (p. 4-8, 17-20, 26-27)
7. ADEME, *Prospective d'évolution des consommations des centres de données en France de 2024 à 2060 — Synthèse*, janvier 2026 (PDF créé le 19/12/2025). Copie lue : https://www.actu-environnement.com/media/pdf/news-47330-synthese-etude-Ademe-datacenter-scenario-janvier-2026.pdf (p. 5-8). Les pages ademe.fr ont renvoyé HTTP 403.
8. RTE, *Les data centers en chiffres clés*, publiée le 21/05/2025, date affichée 01/06/2026. https://www.rte-france.com/bases-electricite/consommation-electricite/essor-data-centers-france
9. Banque des Territoires (Localtis), 10/11/2026, sur une note de l'Institut Paris Région. https://www.banquedesterritoires.fr/linstitut-paris-region-alerte-sur-lexplosion-des-besoins-electriques-des-datacenters-franciliens
10. AIE, *Energy and AI*, avril 2025. https://iea.blob.core.windows.net/assets/86ed1178-4d77-45ac-ab38-28e849f3b93f/EnergyandAI.pdf (p. 58, 64). *Key Questions on Energy and AI*, avril 2026 : https://iea.blob.core.windows.net/assets/3179f7f8-01f6-4dd6-bffa-c9f7b73f1dc9/KeyQuestionsonEnergyandAI.pdf
11. Commission européenne, COM(2026) 500, *Report on the energy efficiency of data centres in the EU*, 21/09/2026. https://build-up.ec.europa.eu/system/files/2026-10/39-2026-48_Report%20on%20the%20energy%20efficiency%20of%20data%20centres%20in%20the%20EU.pdf (p. 3-7)
12. RTE, *Bilan prévisionnel 2025 — Principaux résultats*, 16/12/2025. https://assets.rte-france.com/prod/public/2025-12/2025-12-16-bilan-previsionnel-principaux-resultats-2025.pdf (p. 21, 23, 25)
13. IT for Business, *Raccordement des datacenters : RTE privilégie les projets prêts*, 09/11/2026. https://www.itforbusiness.fr/raccordement-datacenters-rte-premier-pret-premier-servi-109627
14. Ministère chargé du Numérique / DGE, communiqué *Rencontres des centres de données*, 30/01/2026. https://www.entreprises.gouv.fr/espace-presse/rencontres-des-centres-de-donnees-pres-dun-apres-le-sommet-pour-laction-sur-lia-de
15. Élysée, dossier de presse *Faire de la France une puissance de l'IA*, Sommet des 10-11/02/2025 (PDF du 09/02/2025). https://www.elysee.fr/admin/upload/default/0001/17/23058aa82354edfd8a30ff11b57b36f2801504f3.pdf (p. 21, 24-27)
16. TechCrunch, 30/05/2026. https://techcrunch.com/2026/05/30/softbank-says-it-will-invest-up-to-e75-billion-to-build-french-data-centers/
17. RTE, communiqué *Campus IA et RTE signent un contrat de raccordement accéléré*, 26/01/2026. https://assets.rte-france.com/prod/public/2026-01/20260122_CP_RACCORDEMENT_FASTTRACK_CAMPUSIA_VDEF_0.pdf — archivé
18. RTE, *Bilan électrique Île-de-France*, 09/07/2026. https://assets.rte-france.com/prod/public/2026-07/2026-07-09-bilan-electrique-idf-2026.pdf (p. 2)
19. MRAe Île-de-France, avis sur le projet Equinix PA16 à Argenteuil, 23/04/2025. https://www.mrae.developpement-durable.gouv.fr/IMG/pdf/2025-04-23-avis_projet_dc_pa_16_argenteuil_equinix_avis_delibere_.pdf (p. 14-15). Autres avis utilisés : voir `source_url` dans le CSV.
20. CRE, délibération n° 2025-120 et communiqué, 07/05/2025. https://www.cre.fr/fileadmin/Documents/Deliberations/2025/250507_2025-120_Procedure_raccordement_Fast_track.pdf ; https://www.cre.fr/fileadmin/Documents/Communiques_de_presse/2025/250507_CP_CRE_Procedure_fast_track.pdf
21. RTE, *Labellisation d'un site « fast-track » par RTE*, décembre 2025. https://www.services-rte.com/files/live/sites/services-rte/files/Fiche%20descriptive%20fast-track%20-%205%20sites.pdf — archivé
22. RTE Services, *Pre-reservation of capacity on four suitable sites*, 20/05/2025. https://www.services-rte.com/en/news/pre-reservation-of-capacity-on-four-suitable-sites.html
23. RTE Services, *Pre-reservation of capacity on a new "fast-track" site*, 19/12/2025. https://www.services-rte.com/en/news/pre-reservation-of-capacity-on-a-new-fast-track-site.html
24. CRE, délibération n° 2026-32, 04/02/2026. https://www.cre.fr/fileadmin/Documents/Deliberations/2026/260204_2026-32_Procedure_raccordement_RTE.pdf (p. 10)
25. DGE, *Guide — Implantation de centres de données*, 25/11/2025. https://www.entreprises.gouv.fr/files/files/Publications/2025/Guide/25112025__Guide%20Datacenters.pdf (p. 13)
26. Règlement délégué (UE) 2024/1364, 14/03/2024. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1364 (art. 1, 3, 5)

Sources complémentaires citées ponctuellement :

- EDF, communiqués du 17/11/2025 (OpCore, Montereau) et du 30/05/2026 (SoftBank, Bouchain), sur edf.fr ;
- Data4, communiqué du 12/06/2026 (archivé) ;
- Bloomberg, 18/03/2026 (Fluidstack), https://www.bloomberg.com/news/articles/2026-03-18/fluidstack-drops-out-of-marquee-10-billion-ai-project-in-france, titre seul lu, accès payant ;
- Le Monde Informatique, 17/11/2025 ;
- info.fr, 11/06/2026 (E-Valley) ;
- Next, 30/01/2026 ;
- carte uMap https://umap.openstreetmap.fr/fr/map/carte-des-projets-de-data-center-en-france_1289485.
