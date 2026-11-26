# ENTSO-E dans le pipeline : téléchargement, lecture, contrôles

*Rédigé le 26/11/2026 par un agent (Opus), à partir du spike d'accès du même jour
(`docs/spike/entsoe-acces.md`). Rapport de travail, non relu : rien ici n'est publiable
sans relecture. « Constaté » = mesuré aujourd'hui sur les données téléchargées.*

Code : `pipeline/pc/entsoe.py` (catalogue, jeton, téléchargement, lecture XML),
`pipeline/pc/entsoe_derive.py` (normalisation, vue horaire), `pipeline/pc/check_entsoe.py`
(contrôles), `pipeline/tests/test_entsoe.py` (38 tests, dont 3 sur les données réelles).
Branchements : `pc/sources.py` (clés `entsoe_*`), `pc/cli.py` (`--derive` pour `build` et
`check`, la commande `bilan` est intacte), `pc/check.py` (appel des contrôles), `pc/build.py`
(entrées ENTSO-E exclues de `data/export/meta.json`), `.gitignore` (`data/derive/`),
`CLAUDE.md` (section Commandes seulement), `referentiels/sources.yaml` (entrée
`entsoe-transparence`).

## 1. Ce qui est téléchargé

Une requête par (clé, série, année civile de Paris), soit une fenêtre de 23:00Z à 23:00Z,
alignée sur les jours de livraison et égale au maximum de l'API (P1Y). Pour l'année en
cours, la fenêtre s'arrête à J+2.

| Clé | Document | Séries | Fichiers | XML | Stocké (gzip) | Points publiés |
|---|---|---|---|---|---|---|
| `entsoe_prix` | A44 day-ahead | FR, BE, DE-AT-LU (2015-2018), DE-LU (2018→), ES, IT-Nord, CH, GB (2015-2020, en GBP) | 79 | 189 Mo | 7,2 Mo | 1,18 M |
| `entsoe_production` | A75 / A16, toutes filières | FR, BE, DE, ES, IT, CH, GB (2015-2021) | 79 | 1 993 Mo | 101,2 Mo | 15,14 M |
| `entsoe_flux` | A11 flux physiques | FR↔BE, DE, CH, IT, ES, GB, dans les deux sens | 144 | 118 Mo | 7,0 Mo | 0,96 M |
| `entsoe_capacites` | A61 / A01 (NTC jour-1) | FR↔CH, IT-Nord, ES, GB, dans les deux sens | 96 | 12 Mo | 0,5 Mo | 0,08 M |
| `entsoe_charge` | A65 / A16 | FR | 12 | 19 Mo | 1,1 Mo | 0,15 M |
| **Total** | | | **410** | **2,33 Go** | **117 Mo** | **17,5 M** |

Choix des domaines (sondes du 26/11/2026, en plus du spike) :

- **Allemagne**. Prix : la zone DE-AT-LU jusqu'au 30/09/2018 (DE-LU est vide en 2016), puis
  DE-LU. Production et flux : la zone de contrôle `DE` (`10Y1001A1001A83F`), qui répond de
  2016 à 2024, avec les mêmes valeurs que DE-LU en 2024. On a donc une série continue
  (Luxembourg exclu).
- **Italie**. Prix et NTC : IT-Nord. Production et flux : l'Italie entière.
- **Belgique et Allemagne, NTC**. Rien n'est publié pour FR↔BE ni FR↔DE (A61 vide en 2016
  et 2021). Ces frontières sont en flow-based.
- **Grande-Bretagne**. A75 vide à partir de 2022 (constaté), prix seulement jusqu'en 2020,
  en GBP.

Où : `data/raw/entsoe/<clé>/<série>/<AAAA>.xml.gz`. Le XML est brut, compressé (×20). Chaque
fichier a une entrée au manifeste `<clé>/<série>/<AAAA>` : URL avec `securityToken=***`,
sha256 du gzip et du XML, tailles, nombre de points, licence, et `vide` pour une réponse
« No matching data found » (aucune constatée).

**Incrémental** : comme le reste (année en cours toujours refaite, `--force`), avec une règle
de plus. Une année close n'est figée que si elle a été extraite **après le 1er février de
l'année suivante**, parce que les données de fin décembre arrivent ou sont corrigées en
retard.

**Robustesse** :

- 5 requêtes en parallèle.
- Relances (15, 30, 60, 120, 240 s) sur délai dépassé, erreur réseau, 5xx dont 599, et 429
  (`Retry-After` respecté).
- Les **HTTP 400 de panne serveur** sont relancés aussi. Deux constatés, sur A75 IT 2025 et
  2026 (« An unexpected error occurred: I/O error on POST request… »). Un 400 de paramètre
  refusé ne l'est pas.
- Un acquittement autre que « No matching data found » est une erreur.

**Jeton** : lu dans `$ENTSOE_TOKEN` ou `source/entsoe_token`, et ajouté seulement aux
paramètres de la requête envoyée. Toute chaîne d'erreur passe par `masquer()`.

- Vérifié après coup : le jeton n'apparaît ni dans le manifeste, ni dans les 410 fichiers (XML
  décompressé), ni dans le journal du téléchargement.
- Sans jeton :
  - `pc download entsoe_…` échoue tout de suite avec un message clair, sans rien télécharger ;
  - `pc download` sans clé télécharge le reste, puis sort en erreur en nommant les clés
    ENTSO-E sautées ;
  - `pc build` ignore ENTSO-E si `data/raw/entsoe/` est absent ;
  - `pc check` affiche un seul INFO.

**Durées et volumes** (constatés) :

- Téléchargement complet : **26 min** (399 requêtes ; les 11 années closes de la charge
  étaient déjà là), mémoire maximale 1,2 Go. Bilan :
  - 4 relances sur 599 ;
  - 2 échecs (les 400 de panne ci-dessus), repris par une seconde passe.
- Passe incrémentale : **34 requêtes en 2 min 44 s**.
- La production des voisins pèse 85 % du volume. DE : 15 min, ≈ 80 Mo de XML par an.

## 2. Lecture et règles (`pc build`)

Lecture incrémentale du XML (`iterparse`, une TimeSeries à la fois). Le dépliage est fait
en polars (`entsoe.deplier`) :

- **résolution lue par Period**. Une même réponse mêle PT60M, PT15M et PT30M (FR passe au
  quart d'heure le 31/12/2024 pour A65 et le 19/12/2024 pour A75) ;
- **nombre de positions** = (end − start) / pas, ce qui couvre les jours de 23 h et de 25 h ;
- **A03** : une position omise répète la précédente jusqu'à la fin de la Period. Avant le
  premier point publié d'une Period, il n'y a rien. 6,89 M points sur 24,0 M sont des
  répétitions (colonne `publie` = faux) ;
- **horodatage** : début de période, UTC. Une position hors de [1, n] ou répétée est une
  erreur.

**Séries de prix dédoublées : cause établie, règle choisie.** Les TimeSeries A44 qui couvrent
le même instant se distinguent par `classificationSequence_AttributeInstanceComponent.position`.
Le sens de ce numéro **dépend de la zone** :

- **DE-LU** : séquences 1 et 2, aucune série non classée. La 1 est égale au prix DE-LU
  d'energy-charts (écart **nul** les 11/03/2024 et 16/11/2026, 24 et 95 points). La 2 s'en
  écarte de 38 à 125 €/MWh.
- **ES**, depuis le 05/09/2025 : une série **sans** séquence, égale à energy-charts ES (écart
  nul les 02/11/2025 et 03/01/2026, 96 points). Les séquences 1, 2 et 3 s'en écartent de 9 à
  55 €/MWh. La 3 ne couvre que 12:00-24:00, heure de Madrid, ce qui ressemble à l'enchère
  infrajournalière IDA3, sans que ce soit documenté.

Règle : à chaque quart d'heure, la série non classée si elle existe, sinon la séquence 1. Le
reste est écarté (388 908 points). La comparaison se fait **par quart d'heure couvert** : le
05/09/2025, ES publie le SDAC en PT60M et la séquence 1 en PT15M.

*Erreur de ma part, corrigée* : ma première règle (« séquence 1 ou aucune ») gardait les
enchères infrajournalières ES. Le contrôle de lecture l'a signalée par 32 483 conflits de
valeurs, puis 624 chevauchements.

**Quarts d'heure « faux » avant le 01/10/2025.** Quand les quatre quarts d'une heure
publiée en PT15M sont égaux, ils sont ramenés à un point horaire. C'est le cas pour FR et BE
(30/09/2025, 24 h chacune) et pour **IT-Nord** (tout 2025 jusqu'au 30/09, 273 jours : un cas
de plus que celui que le spike avait vu). Après la règle de séquence, aucune heure ne reste
avec des quarts différents.

**Production A75** : la série « production » est repérée par `inBiddingZone`, la série
« consommation » (pompage, stockage, etc.) par `outBiddingZone`. Elles ont des colonnes
distinctes et ne sont jamais additionnées.

**Doublons** entre deux années consécutives : 120 lignes, **0 conflit**. On garde le fichier
le plus récent. Aucun chevauchement de périodes.

**Vue horaire UTC.** Même convention que le pipeline. L'heure h = [h, h+1) reçoit les points
dont la période commence dans l'heure, en moyenne pondérée par la durée (MW moyens = MWh de
l'heure ; pour les prix, la moyenne des quarts, convention RTE). Une heure non couverte à
60 min reste vide. Colonnes :

- `prix_<zone>` ;
- `production_<zone>_<psr>` et `consommation_<zone>_<psr>` ;
- `flux_<de>_<vers>` ;
- `ntc_<de>_<vers>` ;
- `charge_fr` ;
- `solde_physique_fr` = Σ(voisin→FR) − Σ(FR→voisin), positif = import comme `ech_physiques`.
  Il reste vide si l'un des 12 sens manque.

**Où vont les dérivés : `data/derive/entsoe/`, non versionné** (`.gitignore`) :

| Fichier | Contenu | Taille |
|---|---|---|
| `natif.parquet` | 24,0 M points au pas natif, colonnes `Enum` | 122 Mo |
| `horaire.parquet` | 104 399 h × 179 colonnes | 25 Mo |
| `meta.json` | conventions, codes de filière, règles, rapport de lecture, licences, extraction | 72 ko |

Pourquoi ne rien verser dans `data/export/` :

- les exports versionnés pèsent 14,6 Mo, pour un plafond testé de 15 Mo ; la seule vue
  horaire en ferait 40 ;
- aucune page ne les lit ;
- prix, production et charge **ne sont pas sous CC BY 4.0** (§ 5).

Quand une page en aura besoin, on exportera un agrégat propre à cette page, comme `quand.json`.
`data/export/meta.json` exclut les entrées ENTSO-E du manifeste ; le reste des exports n'a
pas changé.

**Coût du build ENTSO-E** : ≈ 40 s, 4,3 Go de mémoire au maximum (6 processus de lecture).

- *Deux erreurs de ma part, corrigées.* La première version montait à **16,9 Go** : dépliage
  en tuples Python, puis colonnes texte sur 24 M de lignes. La seconde **bloquait** dans
  `pc build`, des processus fils créés par `fork` après usage de polars ; elle utilise
  maintenant `spawn`.

## 3. Contrôles (`pc check`) et résultats chiffrés

Ces contrôles visent une **rupture du pipeline** : lecture XML, A03, horodatage, signe,
série perdue. Ils ne « valident » pas ENTSO-E. Sans données ENTSO-E, ils se réduisent à un
INFO ; avec le brut mais sans dérivés, ils échouent. Résultat au 26/11/2026 : **26
contrôles, 0 échec** (dont 7 pour ENTSO-E).

1. **Lecture.** Rien d'anormal :
   - 0 chevauchement ;
   - 0 conflit entre fichiers ;
   - 0 heure de prix à quarts différents avant la bascule ;
   - dérivés plus récents que le brut.
2. **Bornes.** Prix en EUR dans [−500 ; 5 000] (constaté : −500,00 à 2 987,78), aucune
   puissance négative, unités attendues (GBP seulement pour GB).
3. **Prix FR ENTSO-E = energy-charts, point à point** (tolérance 0,005 €/MWh, même résultat
   SDAC au centime) :
   - **écart maximal 0,000 €/MWh chaque année de 2015 à 2026** ;
   - aucun point présent d'un côté seulement, sauf 96 quarts présents chez ENTSO-E seul en
     2026 : la livraison du 27/11, publiée après l'extraction energy-charts. Ce n'est pas un
     trou ;
   - le 21/11/2026 manque toujours des deux côtés (lacune listée).
4. **Solde des flux A11 vs `ech_physiques`**, par an. Tolérances : |écart moyen| ≤ 1 200 MW,
   corrélation ≥ 0,98, et la corrélation à 0 h doit dépasser celles à ±1 h.

   | Années | Écart moyen (ENTSO-E − éCO2mix) |
   |---|---|
   | 2015-2017 | +598 à +639 MW |
   | 2018 | +424 MW |
   | 2019-2023 | +117 à +239 MW |
   | 2024 | **+804 MW** (de +700 à +1 300 MW par mois de janvier à octobre, ≈ 0 ensuite) |
   | 2025 | +36 MW |
   | 2026 | +41 MW |

   - Corrélation horaire de 0,9846 (2024) à 0,9984. Le signe est bon, l'alignement aussi.
   - L'écart tombe à ≈ 0 en **octobre 2018**, le mois de la scission DE-AT-LU.
   - Les frontières **GB et ES** suivent les échanges commerciaux d'éCO2mix mois par mois. Ce
     sont des liaisons continues ou peu bouclées : l'écart ne vient donc pas d'elles.
   - Pour BE, DE, CH et IT, les flux de bouclage empêchent toute comparaison frontière par
     frontière. **Cause non établie.**
   - Le spike (−137 MW, corrélation 0,993, une semaine de 2026) est cohérent : +41 MW en 2026.
   - Tolérance de 1 200 MW : perdre un sens ou une frontière, ou inverser le signe, la dépasse
     largement.
5. **Charge A65 vs consommation éCO2mix**, par an. Tolérances : |écart relatif| ≤ 3 %,
   corrélation ≥ 0,99, alignement.
   - Écart : −0,41 à −0,88 % de 2015 à 2021, −1,20 % en 2022, −2,07 à −2,35 % de 2023 à 2025,
     −1,76 % en 2026.
   - Corrélation ≥ 0,9943 hors fenêtre de décalage.
   - **Mon pipeline reproduit le spike exactement** : +139 MW (semaine du 16/11/2026) et
     −959 MW (semaine du 11/03/2019).
   - Ventilation par nature éCO2mix : **définitif −0,97 %, consolidé −2,42 %, temps réel
     +0,25 %**. Mois par mois, en 2026 : −1,4 à −2,5 % contre le consolidé (janvier à août),
     +0,23 à +0,27 % contre le temps réel (septembre à novembre).
   - L'écart est aussi corrélé à l'éolien (−0,06 à −0,12 MW par MW, régression horaire) et au
     solaire (jusqu'à −0,10 MW par MW en 2025).
   - **Hypothèse, non confirmée par RTE** : la charge publiée sur ENTSO-E est l'estimation
     temps réel, jamais révisée par le consolidé, qui réintègre notamment la production
     décentralisée. Cela explique l'écart du spike (+0,26 % contre le temps réel, −1,6 %
     contre le définitif).
   - Conséquence : **A65 ne sert pas de niveau de référence** ; éCO2mix reste la source.
6. **Nucléaire A75/B14 vs `nucleaire` éCO2mix** : contrôle ajouté, qui valide la lecture A75
   et le sens production/consommation. Tolérances : ≤ 2 %, corrélation ≥ 0,99, alignement.
   Constaté : −0,22 à −0,50 % par an, corrélation ≥ 0,9996 hors fenêtre de décalage.
7. **Complétude des séries FR** (prix, charge, nucléaire, solde). Chaque plage vide doit être
   expliquée :
   - (a) l'heure répétée du passage à l'heure d'hiver, ≤ 2 h, absente comme dans éCO2mix
     (constaté sur la Period A65 de 2017, qui s'arrête et reprend) ;
   - (b) l'une des **25 lacunes listées** dans `LACUNES_ENTSOE` (plages ≥ 3 h, avec constat :
     aucun point publié, Period interrompue, ou sens de flux manquants) ;
   - (c) un trou de 1 ou 2 h, dans un **budget de 24 h par série et par an** (mesuré : 17 h au
     plus, nucléaire 2016).

   Toute autre plage fait échouer le contrôle. Lacunes notables :
   - prix FR du 21/11/2026 ;
   - charge FR : 13 h le 05/02/2017 ;
   - A75 FR : 26 h à partir du 01/01/2026 ;
   - solde : FR↔GB manquant 494 h en octobre 2016 et 72 h en juin 2021, ES→FR manquant 36 h
     à partir du 28/04/2025 10:00Z, ce qui **coïncide avec la panne générale ibérique**.

   Les séries des voisins sont seulement décomptées (beaucoup de filières n'apparaissent que
   par intermittence). NTC FR↔IT-Nord : 8 640 h vides, non analysées.

**Décalage d'une heure dans la source (constat important).** Sur une fenêtre de 2023-2024,
la **charge A65** et la **production A75** FR (nucléaire et solaire testés) d'ENTSO-E sont
**en retard d'une heure** sur éCO2mix : la valeur ENTSO-E de h+1 égale celle d'éCO2mix de h.

- Corrélation hebdomadaire : 0,99+ avec ce décalage, contre 0,87 à 0,98 sans.
- Délimitation au jour près, par minimisation de l'écart quotidien (approximative) :
  - A75 : par intermittence du 31/05/2023 au 14/09/2023, puis en continu du 15/09/2023 au
    01/04/2024 ;
  - A65 : du 31/05 au 02/06/2023, du 21/07 au 31/10/2023 et du 01/02 au 31/03/2024.
- C'est bien ENTSO-E qui est décalé, pas éCO2mix : la convention d'éCO2mix est vérifiée
  chaque année contre ODRÉ nucléaire, et les prix ENTSO-E sont exacts.
- Les flux A11 ne sont pas décalés (dans la fenêtre : 0,985 à 0 h, 0,954 à +1 h).
- La fenêtre englobante (31/05/2023 → 02/04/2024) est **exclue** des contrôles 5 et 6 et
  rapportée à part (corrélations à 0 h et à +1 h). **La donnée n'est pas corrigée** dans
  `data/derive/`. Tout usage de la production ou de la charge FR d'ENTSO-E sur 2023-2024
  doit en tenir compte.

## 4. Tests

`tests/test_entsoe.py`, sans réseau ni jeton (sauf les trois `donnees`, sautés sans
données) :

- **lecture XML** :
  - A03, y compris sans position 1 et jusqu'à la fin de la Period ;
  - courbe A01 ;
  - résolution mixte ;
  - jours de 23 h et 25 h, et position hors Period refusée ;
  - acquittement ;
  - gzip ;
- **normalisation** :
  - séquences DE-LU et ES ;
  - séquence 1 au quart d'heure sous une heure non classée ;
  - production et consommation A75 ;
  - unités ;
  - quarts répétés du 30/09/2025 ;
  - doublons et conflits ;
  - chevauchement ;
  - couverture horaire ;
  - signe et trou du solde ;
- **téléchargement** :
  - fenêtres ;
  - années par série ;
  - clôture ;
  - masquage du jeton (y compris dans une exception réseau) ;
  - relances 599, 429 et 400 de panne ;
  - 400 de paramètre sans relance ;
  - acquittement inattendu ;
  - absence de jeton ;
  - licences ;
- **contrôles** :
  - décalage d'une heure détecté ;
  - signe inversé détecté ;
  - complétude (inexpliqué, budget, lacune listée, heure d'hiver) ;
  - bornes ;
  - INFO sans données ;
- **données** :
  - colonnes ;
  - prix horaire = export ;
  - manifeste complet et sans jeton ;
  - `meta.json` sans ENTSO-E.

Suite complète : voir § 7.

## 5. Licence (vérifiée le 26/11/2026)

Sources : la page « Legal Terms and Conditions » du centre d'aide de la Transparency
Platform (transparencyplatform.zendesk.com, article 40921911218961, lue par son API
publique ; la page web renvoie 403 à un client automatisé, et l'ancienne URL
`transparency.entsoe.eu/content/static_content/…` renvoie 400). Deux documents en sont
téléchargés :

- **Conditions générales d'utilisation** : « approved by the ENTSO-E Market Committee on 29
  March 2023, applicable as from 01 November 2023 » (pièce jointe 40921869376401, sha256
  `665d08621f711e3c…`). § 3.1 : le Data User doit « mention the ENTSO-E Transparency
  Platform as the source of publication of the data », et « not cause prejudice to the
  copyright or related right on a Transparency Platform Data, which may be owned by the
  concerned Primary Owner of Data. In case of a risk to cause prejudice to said right, the
  Data User shall seek the prior agreement of the holder of the copyright or related right ».
  § 2.5 : « ENTSO-E currently publishes a subset of the Transparency Platform data available
  under an open source license (CC-BY 4.0) ».
- **« List of data available for free re-use »** : « Last modified: 18 October 2023 » (pièce
  jointe 40921869379729, sha256 `b21717e8a5a41b9b…`). Elle dit : « Data Users may freely
  copy, redistribute, and adapt the listed data for any purpose, by giving appropriate
  credit (attribution) to its source and indicating if they have made any changes ».

Ce que dit la liste, sans interprétation au-delà :

| Donnée téléchargée | Article (Règl. 543/2013) | Sur la liste CC BY 4.0 ? |
|---|---|---|
| Flux physiques (A11) | 12.1.g « Physical flows » | **oui** |
| NTC prévues (A61) | 11.1.a « Forecasted cross-zonal capacity » | **oui** |
| Prix day-ahead (A44) | 12.1.d | **non** |
| Production réalisée par filière (A75) | 16.1.b&c | **non** |
| Charge réalisée (A65) | 6.1.a | **non** (seules les *prévisions* de charge, 6.1.b-e, y sont) |

Exception écrite dans la liste : « data provided by interconnectors Interconnexion
France-Angleterre ». La liste ne dit pas si les flux et NTC FR↔GB téléchargés sont
« provided by » IFA. **Doute, à trancher avant toute publication FR↔GB.**

Codage :

- `entsoe.LICENCES` : CC BY 4.0 pour `entsoe_flux` et `entsoe_capacites`, conditions générales
  seules pour les trois autres clés ;
- le manifeste et `data/derive/entsoe/meta.json` reprennent ces licences ;
- `referentiels/sources.yaml` reçoit une entrée `entsoe-transparence`, qu'aucun chiffre ne
  cite encore.

Sur la convention de `sources.yaml` : le fichier ne liste que des sources citées par
`chiffres.yaml`, et l'entrée est ajoutée par anticipation, commentaire à l'appui. À retirer
si l'auteur préfère.

Conséquence pratique, à trancher par l'auteur : publier sur le site des prix, de la
production ou de la charge **tirés d'ENTSO-E** n'est pas couvert par CC BY 4.0. Pour les
prix FR, energy-charts (CC BY 4.0, via SMARD) reste la source affichée ; ENTSO-E sert de
contrôle.

## 6. Limites et doutes

- **Décalage d'une heure 2023-2024** (A65, A75 FR) : délimité approximativement, non corrigé,
  non signalé à ENTSO-E ni à RTE. Les autres zones n'ont pas été testées.
- **Écart de charge** : l'hypothèse « temps réel non révisé » repose sur 3 mois de temps réel
  (la fenêtre glissante d'éCO2mix). Rien de publié par RTE ne la confirme.
- **Biais du solde des flux** (+600 MW en 2015-2017, +800 MW en 2024) : non expliqué.
- **IFA** : l'exception de licence pour FR↔GB n'est pas résolue.
- **Séquences A44** : identification « IDA » des séquences ES et nature de la séquence 2
  DE-LU **non documentées** par ENTSO-E. La règle repose sur 4 recoupements energy-charts
  (2 jours par zone). Les autres zones n'ont qu'une série par instant (constaté sur
  2016-2026).
- **IT-Nord 2025** en PT15M à quarts égaux : ramené à l'heure (identique en moyenne
  horaire) ; la raison de cette publication n'est pas cherchée.
- **Limite de débit officielle** : toujours non lue. 5 requêtes parallèles, aucun 429
  constaté.
- **Mémoire** : le build ENTSO-E demande ≈ 4,3 Go et le téléchargement 1,2 Go (XML d'un an en
  mémoire). Le téléchargement est réductible en flux continu si besoin.
- **Non fait** : flow-based (JAO), A26, prix NL, charge des voisins, production par groupe.
- **Doublons de fin d'année** (120 lignes, valeurs identiques) : leur origine exacte
  (débordement de fenêtre de A75 ou A11) n'est pas cherchée.

## 7. Exécution finale (26/11/2026)

Lancé depuis `pipeline/`, avec les données téléchargées ce jour :

| Commande | Résultat | Durée | Mémoire max |
|---|---|---|---|
| `uv run pc download entsoe_…` (premier passage) | 397 fichiers, 2 échecs (400 de panne), 4 relances 599 | 26 min 04 s | 1,2 Go |
| `uv run pc download entsoe_…` (incrémental) | 34 requêtes (années en cours + 2 reprises), 0 échec | 2 min 44 s | 0,4 Go |
| `uv run pc build` (tout le pipeline) | exports inchangés (14,6 Mo ; seul `genere_le` de `meta.json` bouge) ; ENTSO-E : 24 003 546 points, 104 399 h × 179 colonnes, 152,7 Mo dans `data/derive/entsoe/` | 46 s (dont 40 s ENTSO-E) | 4,8 Go |
| `uv run pc check` | **26 contrôles, 0 échec** | 7 s | — |
| `uv run pytest` | **147 réussis** (dont 38 dans `test_entsoe.py`) | 3 s | — |

Volumes : `data/raw/entsoe/` 113 Mo (2,33 Go de XML décompressé) ; `data/derive/entsoe/`
147 Mo ; `data/export/` inchangé (14 600 826 octets, sous le plafond de 15 Mo).
