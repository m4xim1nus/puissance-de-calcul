# Spike — accès à l'API ENTSO-E Transparency Platform

*Rédigé le 26/11/2026 par un agent (Sonnet). Rapport brut : rien ici n'est publiable
sans relecture. Tout ce qui est marqué « constaté » a été mesuré aujourd'hui avec le
jeton ; « non vérifié » = repris de ma mémoire ou non testé.*

- **Script** (jetable) : `pipeline/explo/spike_entsoe.py` (fonctions `get`, `resume`,
  `serie`). Le jeton est lu dans `source/entsoe_token` (ou `$ENTSOE_TOKEN`), ajouté à
  l'URL à l'envoi, jamais écrit ni journalisé. Les réponses XML sont mises en cache
  hors dépôt (`$ENTSOE_CACHE`). Les scripts d'essai (hors dépôt) ne contiennent pas
  le jeton non plus. Les URL ci-dessous seraient de la forme
  `https://web-api.tp.entsoe.eu/api?securityToken=***&documentType=…`.
- Fenêtres testées : semaine du 16 au 22/11/2026 (« 2026 ») et du 11 au 17/03/2019
  (« 2019 »), plus des sondages ponctuels (années entières 2024 et 2025, janvier
  2014/2015/2016, 29/09–03/10/2025).

## 1. Verdict d'accès

**Le jeton fonctionne** : HTTP 200 sur toutes les requêtes bien formées (réponses
XML, UTF-8). Un « vide » est un HTTP 200 avec un `Acknowledgement_MarketDocument`
(~1 ko, « No matching data found ») : ce n'est pas une erreur. Les erreurs de paramètre
sont des HTTP 400 avec un message lisible (champ `<text>`) ; deux HTTP 599 (gateway
timeout, « Unable to access service within time limit ») sont survenus par
intermittence, repris avec succès : **prévoir des relances**.

**Latence** : très lente, de 3 s à 40 s par requête (médiane ~15 s), quelle que soit
la taille (une semaine ou un an). **Parallélisme** : 12 et 15 requêtes simultanées
passées sans HTTP 429 ni blocage (constaté).

**Limites de débit** : je n'ai pas pu lire le guide officiel (les URL testées ont
renvoyé 400/404). *Non vérifié* : je crois me souvenir de 400 requêtes/min par jeton,
avec blocage temporaire au-delà. Aucun 429 observé dans mes ~110 requêtes, dont deux
rafales de 12 et 15. **Fenêtre max par requête : 1 an** (constaté : « larger than
maximum allowed period 'P1Y' » pour A65, A75 et A11 ; 1 an entier accepté pour A44,
A65, A75, A11, A61 ; 2 ans refusés).

## 2. Requête par requête

Domaines : FR `10YFR-RTE------C`, BE `10YBE----------2`, DE-LU `10Y1001A1001A82H`,
ES `10YES-REE------0`, IT-Nord `10Y1001A1001A73I` (IT national `10YIT-GRTN-----B`),
CH `10YCH-SWISSGRIDZ`, GB `10YGB----------A`, NL `10YNL----------L`.
Pour A11, `in_Domain` = zone qui **importe**, `out_Domain` = zone qui **exporte**.
Colonne « pas » : résolution (`PT15M`, `PT30M`, `PT60M`).

| # | Requête | HTTP | Contenu constaté | Pas | Profondeur |
|---|---|---|---|---|---|
| 1 | **A44** prix day-ahead, `in=out=zone` | 200 | FR, BE, DE-LU, ES, IT-Nord, CH, NL : EUR, `MWH` (= EUR/MWh). **GB : vide en 2026, présent en 2019 et jusqu'au 31/12/2020, en GBP** (pas d'EUR, cf. §5). DE (zone `10Y1001A1001A83F`) : vide en 2019 comme en 2026 (zone supprimée en 2018, remplacée par DE-LU). | 60 min jusqu'au 29/09/2025, 15 min ensuite (voir §5) | FR : depuis le 05/01/2015 (livraison) ; 2014 vide |
| 2 | **A75** production réalisée, `processType=A16`, `in_Domain=zone` | 200 | FR 2026 : B01 biomasse, B04 gaz, B06 fioul, B10 hydro STEP, B11 hydro fil/éclusée, B12 hydro lacs, B14 nucléaire, B16 solaire, B17 déchets, B18 éolien mer, B19 éolien terre, B25 stockage (+ B05 charbon, B10 et B25 en série « consommation »). Unité `MAW` (= MW). Mêmes codes pour les voisins avec des différences (DE-LU a B02/B03 lignite, B09 géothermie, B15, B20 ; ES a B07, B08, B13…). GB : vide en 2026. | FR : 60 min → 15 min à partir du 19/12/2024 ; BE et CH 60 min en 2026 ; DE-LU, ES, IT 15 min ; GB 30 min en 2019 | FR : depuis le 01/01/2015 (2014 vide) |
| 3 | **A11** flux physiques, par frontière et par sens | 200 | Les 6 voisins répondent dans les deux sens (FR↔BE, DE-LU, CH, IT, ES, GB). Série par sens, **flux brut** (pas un solde). Sens dominant plein ; sens opposé quasi vide (ex. CH→FR : 1 point sur la semaine). | FR↔BE/DE-LU/IT/ES 15 min (BE : 15 min sur toute l'année 2024) ; CH et GB 60 min en 2026 ; 60 min en 2019 | FR↔BE, IT : depuis le 01/01/2015 |
| 4a | **A61** NTC prévues, `contract_MarketAgreement.Type=A01` (jour-1) | 200 | **Publiées** : FR↔CH, FR↔IT-Nord (IT-Nord→FR et FR→IT-Nord), FR→ES, FR→GB (valeur unique sur la semaine : ES 2960, GB 3028 MW ; CH alternant 2385/2015 MW). **Non publiées : FR↔BE, FR↔DE-LU** (vide, 2019 comme 2026). | 60 min (ES en 2026 : 15 min, 1 point) | FR→ES : depuis 01/01/2015 |
| 4b | **A61** mensuel (`…Type=A03`) FR→ES | 200 | 1 point, période `P1D` | P1D | — |
| 4c | **A26** `businessType=B08`, FR→ES / FR→CH | 200 | 3 séries (`A01`/`A06`/`A07`, valeurs 0 sur FR→ES) ; contenu **non interprété** | 15 min | — |
| 4d | A25 (allocations explicites) FR→ES, B09 (positions nettes), B11 / A26 flow-based Core | 200 vide / 400 / 400 | **Rien d'exploitable** : A25 vide ; B09 refusé (« parameters do not match the dataItem ») ; flow-based Core refusé (« combination … not valid, or … not allowed to be fetched via this service ») | — | — |
| 5 | **A65** charge réalisée, `processType=A16`, `outBiddingZone_Domain=FR` | 200 | 1 série, `MAW` | 60 min → 15 min **à partir du 31/12/2024** | depuis le 01/01/2015 |

### Volumes constatés (XML, 1 requête)

| Requête | Taille | Points |
|---|---|---|
| A44 FR année 2024 | 1,5 Mo | 8 679 |
| A44 FR année 2025 | 2,4 Mo | 15 087 (mélange 60/15 min) |
| A44 DE-LU année 2024 | 6,7 Mo | 43 807 (séries dédoublées, voir §5) |
| A65 FR année 2024 | 1,1 Mo | 8 786 |
| A75 FR année 2024 (toutes filières) | 12,4 Mo | 94 513 |
| A11 FR→BE année 2024 | 3,6 Mo | 28 469 (15 min, points omis non comptés) |
| A11 BE→FR année 2024 | 0,9 Mo | 7 466 |
| A61 FR→ES année 2024 | 0,2 Mo | 1 585 |
| A75 DE-LU, une semaine | 1,3 Mo (≈ 70 Mo/an) | 10 071 |

## 3. Recoupements

### 3.1 Prix day-ahead France : ENTSO-E A44 contre energy-charts (`data/raw/prix_fr/`)

- Semaine 2026 : 672 quarts d'heure ENTSO-E, tous présents dans energy-charts ;
  **écart maximal 0,000 EUR/MWh**, aucun écart > 0,005. Semaine 2019 : 192 heures,
  **écart maximal 0,000 EUR/MWh**. Les deux séries ont donc la même source (SDAC) et
  les mêmes horodatages : **début de période, UTC** (energy-charts : `unix_seconds` ;
  ENTSO-E : `timeInterval/start` + position − 1).
- Le **21/11/2026** (jour de livraison) manque **dans les deux sources** (vide chez
  ENTSO-E aussi, pas de série pour la période 20/11 23:00Z → 21/11 23:00Z) : le trou
  noté dans `check.py` n'est donc pas propre à energy-charts. *À reconfirmer dans
  quelques jours* si ENTSO-E le publie plus tard.
- Passage au 15 min : voir §5 (le 30/09/2025 ENTSO-E donne déjà 4 quarts par heure ;
  energy-charts reste horaire ce jour-là, d'où 72 quarts « absents » côté energy-charts).

### 3.2 Charge France : ENTSO-E A65 contre éCO2mix (`data/export/systeme_horaire.parquet`)

Méthode : moyenne des quarts d'heure ENTSO-E (MW) par heure UTC de début, comparée à la
colonne `consommation` (MW moyens sur l'heure, début d'heure UTC).

| Semaine | n (heures) | éCO2mix | Moyenne ENTSO-E | Écart moyen ENTSO-E − éCO2mix | Écart-type | |max| |
|---|---|---|---|---|---|---|
| 16–22/11/2026 (éCO2mix **temps réel**) | 168 | 53 470 MW | 53 609 MW | **+139 MW** (+0,26 %) | 312 MW | 779 MW |
| 11–17/03/2019 (éCO2mix **définitif**) | 168 | 60 301 MW | 59 342 MW | **−959 MW** (−1,6 %) | 556 MW | 2 391 MW |

- **Alignement horaire** : écart-type minimal avec décalage 0 h (σ 312 MW ; avec ±1 h :
  1 800–2 300 MW). La convention du pipeline (`HORODATAGE_ECO2MIX`, heure de début
  d'heure UTC) est donc cohérente avec ENTSO-E (début de période).
- L'écart 2019 (−1,6 %) est **non expliqué**. Ajouter `|pompage|` à éCO2mix l'aggrave
  (écart −1 942 MW en 2019), donc ce n'est pas le pompage. Hypothèses non testées :
  périmètre de la « charge totale » ENTSO-E (estimation partielle par RTE),
  méthode d'agrégation. **Ne pas utiliser A65 comme « vérité » en niveau sans
  trancher.**

### 3.3 Bonus : flux physiques (A11) contre éCO2mix `ech_physiques`, semaine 2026

Solde = Σ(FR→X) − Σ(X→FR) sur BE, DE-LU, CH, IT (national, pas seulement IT-Nord), ES,
GB, moyennes horaires. ENTSO-E : **+12 964 MW** (export net moyen). `ech_physiques` du
parquet : **−13 101 MW** ; le signe est donc opposé dans l'export (exports négatifs), et
après inversion l'écart moyen est **−137 MW** (~1 %), corrélation |0,993|.
La concordance valide l'ordre de grandeur et le signe, pas le détail frontière par
frontière (non testé).

## 4. Ce qui est publié, ce qui ne l'est pas (capacités)

- **NTC jour-1 (A61)** : publiées pour FR↔CH, FR↔IT-Nord, FR→ES, FR→GB (le sens inverse
  vers l'ES/GB n'a pas été testé). **Pas de NTC pour FR↔BE ni FR↔DE-LU** : ces
  frontières sont en flow-based (CWE jusqu'en 2022, Core depuis le 08/06/2022 : date à
  vérifier, non testée ici).
- **Flow-based (domaines Core, PTDF, RAM)** : **non accessible** via cette API avec les
  combinaisons essayées (A26/B11, B11). Publié par JAO (Core), hors ENTSO-E REST. Je
  n'ai pas cherché de combinaison valide dans le guide (non lu) : à vérifier avant
  d'abandonner. Conséquence : pas de « capacité disponible » FR↔BE/DE-LU
  ; seulement les flux réalisés (A11).
- A25 (allocations explicites) vide ; A31 refusé ; A26/B08 non interprété.

## 5. Pièges

1. **Résolution mixte dans une même réponse** : un même document peut contenir des
   `Period` en PT60M puis PT15M (A44 FR autour de fin septembre 2025, A65 FR le
   31/12/2024, A75 FR le 19/12/2024, DE-LU 2024). Lire `resolution` **par `Period`**,
   jamais globalement ; les points d'une année entière ne sont pas équidistants.
2. **Prix : 15 min effectif au 01/10/2025 (SDAC), mais ENTSO-E sert déjà PT15M pour le
   30/09/2025** avec le prix horaire **répété** sur 4 quarts (ex. 69,9 sur
   22:00/22:15/22:30/22:45Z). Ne pas lire cela comme une vraie granularité quart-horaire.
   energy-charts reste horaire ce jour-là.
3. **`curveType=A03` (blocs de taille variable)** : toutes les séries vues sont en A03 :
   **une position omise = la valeur précédente répétée**, pas une donnée manquante.
   Il faut propager la dernière valeur (y compris jusqu'à la fin de la `Period`). Ex. prix FR
   2026 : 56 positions omises sur 672. Un `position` manquant au début d'une période
   (premier point absent) n'est pas imputable : traité comme vide dans `serie()`.
   Sans cette règle, A11 BE→FR (34 points pour une semaine) ressemble à un trou.
4. **Horodatage** : début de période, UTC, en `timeInterval/start` et position 1-based.
   Les requêtes sont en `yyyyMMddHHmm` **UTC**. A44 renvoie des `Period` alignées sur le
   jour de livraison **CET/CEST** (début 22:00Z ou 23:00Z) : une requête 16→23/11
   UTC a renvoyé 8 jours de livraison (15/11 23:00Z → 23/11 23:00Z) ; A65/A75/A11 sont
   renvoyés au plus près de la fenêtre demandée. Jours de 23 h / 25 h : le nombre de
   positions d'une `Period` varie (92/100 quarts), à calculer depuis
   `start`/`end`/`resolution`, pas à supposer.
5. **Séries dédoublées** : DE-LU a 2 `TimeSeries` par jour de livraison (2019 :
   PT60M **et** PT15M ; 2026 : 2 PT15M), toutes `auction.type=A01`,
   `businessType=A62`. Non élucidé ; ne pas sommer, dédoublonner ou comparer à une
   référence.
6. **Production A75 : séries « consommation »** (`outBiddingZone_Domain` présent) pour
   B10 (pompage), B25 et B05 (FR 2026) : à ne pas additionner à la production. Production
   = `inBiddingZone_Domain`. Production nette de ce qui est consommé par les STEP ?
   *non vérifié*. Le code **B25** (stockage) n'existe qu'après ~2024 ; B20 « autres » existe
   en BE/DE.
7. **GB** : plus de prix day-ahead EUR après 2020 (Brexit, pas de couplage) ; avant,
   prix en **GBP**/MWh (unité `MWH`, devise `GBP`), pas en EUR : ne pas mélanger.
   GB production/flux : vérifier la couverture après 2021 (A75 vide en 2026 ; A11 FR↔GB
   répond bien).
8. **IT** : FR↔IT dans les flux A11 est testé avec la zone nationale `IT`
   (`10YIT-GRTN-----B`) ; pour les prix, c'est la zone de marché **IT-Nord**
   (`10Y1001A1001A73I`). Ne pas confondre.
9. **Paramètres** : `contract_MarketAgreement.Type` (**avec un point**, pas un
   underscore, sinon HTTP 400 « Input parameter does not exist ») ; B09 exige
   `processType`.
10. **Poids** : XML très verbeux (A75 FR : 12 Mo/an pour ~95 000 points utiles) ;
    A75 des voisins à 15 min : ~70 Mo/an pour DE-LU.
11. **Pas de requête par `offset`/pagination observée** : ma limite de ~100 documents
    n'a pas été rencontrée avec des réponses d'un an. *Non vérifié* que ce soit vrai pour
    d'autres types.
12. **Trous de publication** : le jour de livraison 21/11/2026 vide pour FR (voir §3.1).
    Les prix jour-1 de J+1 sont publiés vers midi ; pas de test sur l'heure exacte.

## 6. Proposition pour `pc download`

Principe : une clé par (type de document, zone/frontière), requêtes **par année civile**
(max 1 an), cache `data/raw/entsoe_<clé>/AAAA.xml` (ou .json/.parquet normalisé),
même incrémentalité qu'aujourd'hui (année close non refaite, année en cours toujours
retéléchargée), jeton lu dans `source/entsoe_token` ou `$ENTSOE_TOKEN`, **jamais** dans
les logs ni dans le manifeste (masquer `securityToken` dans les URL journalisées).
Relancer sur HTTP 599/5xx (backoff) ; respecter 429 si `Retry-After`. Parallélisme borné
à 4–6 (je n'ai observé aucun problème à 12–15, mais le plafond officiel n'est pas
vérifié).

| Clé | Requête | Années | Requêtes | Volume estimé (XML) |
|---|---|---|---|---|
| `entsoe_charge_fr` | A65 FR | 2015→en cours | 12 | ~12 Mo |
| `entsoe_prod_fr` | A75 FR (toutes filières) | 2015→ | 12 | ~120–150 Mo |
| `entsoe_flux` | A11 FR↔{BE, DE-LU, CH, IT, ES, GB}, 2 sens | 2015→ | 6×2×12 = 144 | ~100 Mo |
| `entsoe_ntc` | A61 (A01) FR↔{CH, IT-Nord, ES, GB}, 2 sens | 2015→ | 4×2×12 = 96 | ~10 Mo |
| `entsoe_prix_voisins` | A44 BE, DE-LU, ES, IT-Nord, CH (+ NL optionnel) ; GB 2015–2020 (GBP) | 2015→ | 5×12 + 6 = 66 | ~30 Mo (DE-LU ~7 Mo/an) |
| `entsoe_prix_fr` (contrôle) | A44 FR | 2015→ | 12 | ~20 Mo |

Remarques :

- **Total ≈ 340 requêtes, ≈ 300 Mo de XML** (en normalisant en parquet, quelques Mo).
  À ~15 s par requête en série : **~1 h 25** ; à 4–6 en parallèle : **15–25 min**. Un
  usage incrémental (année en cours seulement) = ~35 requêtes (~3 min en parallèle).
- Priorité si on veut du léger : **A65 FR, A11 FR↔voisins, A44 voisins**. Ne pas
  télécharger A75 des voisins (≈ 70 Mo/an par zone à 15 min) sauf besoin précis :
  filtrer par `psrType` si oui.
- **Prix FR ENTSO-E redondant avec energy-charts** (écart nul) : ne le télécharger que comme
  contrôle (peut remplacer le goulot « 2 requêtes/min » d'energy-charts : 12 requêtes
  ENTSO-E en parallèle contre ~6 min).
- Normalisation : dépiler chaque `Period` avec sa propre résolution, propager A03,
  conserver `start` UTC début de période, écrire MW (`MAW`) et EUR/MWh ; MW → MWh avec
  le facteur durée/60 ; noter en colonne la résolution native.
- **Ne pas** viser le flow-based via cette API (pas accessible, voir §4) ; si besoin,
  prévoir JAO comme source séparée.

## 7. Doutes et non vérifié

- Limite de débit officielle (400 req/min ?) non lue : guide inaccessible.
- Cause de l'écart de charge 2019 (−1,6 %) non élucidée ; un seul échantillon par époque
  (une semaine), pas de contrôle sur l'année.
- Séries dédoublées DE-LU non expliquées ; pas de comparaison de ses prix avec une autre
  source.
- Date du passage de FR en Core (08/06/2022), absence de NTC FR↔BE/DE-LU avant 2022 :
  testé seulement sur mars 2019 (vide) et nov. 2026 (vide) ; une fenêtre 2021 n'a pas été
  testée.
- A26 (`B08`) non interprété ; profondeur de A61 vers ES/GB seulement testée en 2015–2016.
- Sens GB→ES/IT→… des NTC non testés ; A61 FR↔GB, FR↔ES inverse non testés.
- Heure de publication des prix de J+1 et reprise du jour manquant du 21/11/2026 : non
  suivies.
- Droits de réutilisation des données ENTSO-E (licence, attribution) non vérifiés :
  **à examiner avant publication** (règle « sourcé et daté »).
