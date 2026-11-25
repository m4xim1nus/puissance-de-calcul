# Spike — sources « système électrique horaire »

> **Errata du 26/11/2026** (contre-vérification : `contre-verification.md`). (1) `taux_co2` est en CO2eq (émissions directes), pas en CO2 seul ; l'écart avec le Bilan vient pour ≈ 3/4 (2024) à 9/10 (2025) du fioul corse, le reste des facteurs d'émission. (2) La révision 361 → 352 h (2024) est expliquée : découplage d'EPEX le 26/06/2024, RTE retient les données Nord Pool (BE2025, p. 64). (3) La convention « fin de demi-heure » est confirmée par trois tests, dont un indépendant d'ODRÉ, mais pour le consolidé/définitif seulement ; le temps réel (« puissance instantanée ») reste à tester.

*Spike d'accès, pas de pipeline. Tests réels du 25 novembre 2026 (soir, heure de
Paris). Toutes les URL ont été appelées ce jour-là, sauf mention contraire.*

- **Script** (jetable, relançable) : `pipeline/explo/spike_systeme.py`
  (`download` puis `analyse`). Lancement :
  `uv run --no-project --with httpx,polars python pipeline/explo/spike_systeme.py analyse`.
- **Échantillons** : `data/raw/spike/systeme/` (≈ 70 Mo, non versionné : `data/raw/`
  est dans le `.gitignore`, créé pendant le spike).
- **Références publiées** utilisées pour les recoupements :
  - RTE, *Bilan électrique 2024 — rapport complet* (PDF, URL datée 2025-09) :
    <https://assets.rte-france.com/analyse-et-donnees/2025-09/BE2024%20-%20Rapport%20Complet.pdf>
    et la synthèse web <https://analysesetdonnees.rte-france.com/bilan-electrique-2024/synthese> ;
  - RTE, *Bilan électrique 2025 — rapport complet* (PDF, URL datée 2026-03) :
    <https://assets.rte-france.com/analyse-et-donnees/2026-03/BE2025%20-%20Rapport%20Complet.pdf> ;
  - RTE, *Spécification des fichiers de données en puissance pour éCO2mix*
    (PDF créé le 20 juin 2025) :
    <https://assets.rte-france.com/preprod/public/2025-06/Eco2mix%20-%20Sp%C3%A9cifications%20des%20fichiers%20en%20puissance.pdf>.

## Synthèse en une minute

| # | Source | Accès | Licence | Pas de temps | Profondeur | Verdict |
|---|---|---|---|---|---|---|
| 1 | éCO2mix national (ODRÉ) | libre, sans jeton | Licence Ouverte 2.0 | 30 min (déf./cons.), 15 min (temps réel) | 2012 → J | **GO** |
| 2 | éCO2mix régional (ODRÉ) | libre | Licence Ouverte 2.0 | 30 min (déf./cons.), 15 min (TR) | 2013 → J | **GO** |
| 3 | Registre national des installations (ODRÉ) | libre | Licence Ouverte 2.0 | photo trimestrielle + millésimes annuels | 2017 → 30/09/2026 | **GO** (poste source partiel) |
| 4 | Prix day-ahead FR (energy-charts) | libre, 2 req/min | CC BY 4.0 (SMARD) pour FR | 60 min puis 15 min depuis le 01/10/2025 | 5 janv. 2015 → J (sondages) | **GO** |
| 4b | ENTSO-E Transparency | **jeton requis** (HTTP 401 testé) | — | — | — | non testé |
| 5 | Mix et flux des voisins (energy-charts, Elexon) | libre | CC BY 4.0, prix restreints pour ES et l'Italie hors IT-North | 15, 30 ou 60 min selon le pays | non mesurée | **partiel** (GB absent d'energy-charts) |
| 6a | Prix négatifs | dérivé de 4 | — | horaire | 2023-2025 testés | **GO**, recoupe RTE à l'heure près |
| 6b | Modulation nucléaire | nucléaire national horaire (ODRÉ) | Licence Ouverte 2.0 | horaire | 2001 → 09/2026 | **partiel** (proxy seulement) |
| 6c | Écrêtement EnR | aucune série ouverte trouvée | — | — | — | **NO** (chiffres annuels RTE seulement) |
| 7 | Recoupement conso 2024 éCO2mix / RTE | — | — | — | — | **boucle à 7 GWh près** (0,002 %) une fois la Corse retirée |

---

## 1. éCO2mix national (ODRÉ)

**URL.** API Opendatasoft Explore v2.1 :

- consolidé + définitif : `https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-cons-def/`
- temps réel : `.../datasets/eco2mix-national-tr/`
- export complet sans pagination : `.../datasets/<id>/exports/parquet` (ou `csv`,
  `json`), filtrable par `where=` (ODSQL), par exemple
  `where=date_heure >= '2024-01-01T00:00:00+01:00' and date_heure < '2025-01-01T00:00:00+01:00'`.

**Accès.** Sans jeton. En-têtes renvoyés : quota de 10 000 000 appels par jour et
de 50 000 appels par mois et par jeu (`X-RateLimit-dataset-Limit`). L'endpoint
`/records` est plafonné à `limit ≤ 100` et `offset + limit ≤ 10 000` : il ne sert
pas pour l'historique. **Il faut passer par `/exports/`**, sans plafond mais lent :
le parquet complet du national (514 272 lignes, 22,9 Mo) a mis 5 min 15 s, et un
CSV d'un an 1 min 38 s.

**Licence.** Licence Ouverte v2.0 (Etalab), éditeur RTE (métadonnées ODRÉ).

**Natures et profondeur** (agrégats sur `date_heure`, UTC) :

| Jeu | Nature | Début (UTC) | Fin (UTC) | Lignes |
|---|---|---|---|---|
| cons-def | Définitives | 2011-12-31 23:00 | 2025-12-31 22:45 | 490 944 |
| cons-def | Consolidées | 2025-12-31 23:00 | 2026-08-31 21:45 | 23 328 |
| tr | Temps réel | 2026-08-31 22:00 | 2026-11-26 22:45 (prévisions) | 8 352 |

Les trois natures se suivent sans recouvrement. Le jeu temps réel est une fenêtre
glissante : il ne garde que les jours non encore consolidés. 2025 est déjà en
« définitif » en novembre 2026.

**Pas de temps.** Les lignes existent toutes les 15 min, mais **en consolidé et
en définitif, seules les lignes à :00 et :30 sont renseignées**. Les lignes à :15
et :45 ne portent que les prévisions J-1 et J (et, depuis mi-2024, l'échange
commercial avec l'Espagne). La spécification RTE l'écrit : « Les données
consolidées et définitives […] sont fournies au pas demi-heure. Seules les données
prévisionnelles […] sont fournies au pas quart d'heure ». Le temps réel est
renseigné aux quatre quarts d'heure.

**Nature physique de la valeur.** La spécification RTE (§ 1.1) distingue :

- le **temps réel**, une « puissance instantanée basée sur des télé-informations et
  des estimations » ;
- le **consolidé** et le **définitif**, une « puissance moyenne basée sur les
  comptages ».

On ne convertit donc proprement en énergie que le consolidé et le définitif :
MWh = MW × 0,5 par demi-heure. Sur le temps réel, MW × 0,25 n'est qu'une
approximation.

**Colonnes utiles** (cons-def, MW sauf mention) : `consommation`, `prevision_j1`,
`prevision_j`, `fioul`, `charbon`, `gaz`, `nucleaire`, `eolien`, `solaire`,
`hydraulique`, `pompage` (négatif), `bioenergies`, `ech_physiques` (solde, **positif
= import**), `taux_co2` (g/kWh), `ech_comm_angleterre`, `ech_comm_espagne`,
`ech_comm_italie`, `ech_comm_suisse`, `ech_comm_allemagne_belgique`, et des sous-filières
(`gaz_ccg`, `gaz_tac`, `gaz_cogen`, `hydraulique_step_turbinage`,
`hydraulique_lacs`, `hydraulique_fil_eau_eclusee`, `bioenergies_*`, `fioul_*`). Le
temps réel ajoute `eolien_terrestre`, `eolien_offshore`, `stockage_batterie` et
`destockage_batterie`, **absents du cons-def national**.

**Volumétrie 2015 → 2025.** Environ 17 520 demi-heures renseignées par an, soit
≈ 190 k lignes utiles (≈ 385 k lignes avec les quarts d'heure vides). Le parquet
complet 2012 → 2026 pèse 23 Mo.

**Contrôles effectués** (script, `analyse_eco2mix_national`) :

- Bilan instantané `consommation − Σ filières − pompage − ech_physiques` : résidu
  moyen inférieur à 1 MW jusqu'en 2020, puis de **70 à 95 MW de 2021 à 2026**
  (maximum 538 MW). Ma piste, non vérifiée : le stockage batterie, que le
  cons-def national ne ventile pas.
- Aucune valeur nulle sur les filières, `pompage`, `ech_physiques` et `taux_co2`
  dans les lignes renseignées. Il manque 8 valeurs sur `ech_comm_espagne` et 56
  sur `ech_comm_allemagne_belgique`.

**Pièges.**

1. **Horodatage = fin de la demi-heure (convention « finissante »).** Ce n'est
   documenté nulle part, mais deux tests indépendants le montrent :
   - Comparaison avec le jeu ODRÉ `production-nette-nucleaire`, déclaré en
     « convention débutante ». Si l'heure *h* vaut la moyenne des points *h*:30 et
     *h+1*:00 d'éCO2mix, l'écart absolu moyen est de **0,2 MW** sur 8 779 h. Si
     elle vaut la moyenne de *h*:00 et *h*:30, il monte à 258 MW.
   - Centroïde horaire de la production solaire de juin 2024 : 12:06 UTC sur les
     horodatages éCO2mix. energy-charts, dont l'horodatage marque le début de
     l'heure (documenté), place le centre réel à 11:52 UTC. Un décalage de
     +15 min correspond exactement à une demi-heure horodatée à sa fin.

   **Conséquence : l'heure UTC *h* (de *h* à *h+1*) = moyenne des points
   horodatés *h*:30 et *h+1*:00.** Un `truncate('1h')` naïf décale toute la série
   de 30 min, ce qui fausse les corrélations avec les prix horaires.
2. **Heure d'été et d'hiver mal converties en UTC par ODRÉ.** Les fichiers RTE ont
   toujours 96 quarts d'heure par jour local.
   - Le jour du passage à l'heure d'été (2024-03-31), les heures locales
     inexistantes 02:00 et 02:30 sont présentes : elles reçoivent le même
     `date_heure` UTC et les mêmes valeurs que 03:00 et 03:30, d'où des doublons.
   - Le jour du passage à l'heure d'hiver (2024-10-27), l'heure répétée manque :
     on saute de 23:30 à 01:00 UTC.

   On compte 3 anomalies par an, chaque année depuis 2012. En pipeline, il faut
   dédoublonner sur l'UTC et boucher (ou marquer) l'heure manquante d'octobre.
   Sur une année, l'effet net sur l'énergie est de quelques GWh (voir
   Recoupements).
3. **Types de colonnes incohérents** dans le schéma ODRÉ : `ech_comm_allemagne_belgique`
   et `gaz_cogen` sont typées `text` dans cons-def, et
   `hydraulique_fil_eau_eclusee` dans le temps réel. Il faut caster explicitement.
4. **Passage définitif → consolidé** : il manque la demi-heure du
   2026-01-01 00:00 locale (saut d'1 h à 2025-12-31 23:30 UTC).
5. **Le temps réel contient des lignes futures** (97 lignes au moment du test) où
   seule `prevision_j1` est remplie. Filtrer `consommation is not null`.
6. **Révisions** : le temps réel est remplacé par le consolidé « au cours des mois
   suivants », puis par le définitif « au cours de l'année suivante » (spécification
   RTE § 1.1). ODRÉ signale de plus que l'autoconsommation photovoltaïque a été
   recalculée sur 2022-2024, ce qui a relevé la consommation et la production
   solaire publiées (description des jeux `consommation-annuelle-brute` et
   `prod-national-annuel-filiere`). **Les données d'une année récente ne sont pas
   figées.** Il faut stocker la nature et la date d'extraction.
7. **Périmètre : France continentale, hors Corse** (démontré par le recoupement
   § 7). Le Bilan électrique, lui, inclut la Corse.
8. `taux_co2` est un **facteur moyen de la production française** (« estimation des
   émissions de carbone générées par la production d'électricité en France »),
   **pas un facteur marginal** et pas un facteur de la consommation (les imports
   n'y sont pas). Ses facteurs d'émission par filière ne sont pas documentés dans
   ODRÉ (voir § 7 pour l'écart avec le Bilan).

**Verdict : GO.** C'est la série pivot du site.

## 2. éCO2mix régional (ODRÉ)

**URL.** `.../datasets/eco2mix-regional-cons-def/` (définitif 2013-01-01 → 2025-12-31,
consolidé 2026-01-01 → 2026-08-31) et `.../datasets/eco2mix-regional-tr/`
(fenêtre glissante depuis 2026-08-31 22:00 UTC).

**Accès et licence.** Identiques au national.

**Granularité.** 12 régions métropolitaines continentales : Auvergne-Rhône-Alpes,
Bourgogne-Franche-Comté, Bretagne, Centre-Val de Loire, Grand Est,
Hauts-de-France, Normandie, Nouvelle-Aquitaine, Occitanie, Pays de la Loire,
Provence-Alpes-Côte d'Azur et Île-de-France. **Pas de Corse.** En cons-def, seules
les lignes à :00 et :30 existent (17 568 lignes par région en 2024) ; le temps
réel est au quart d'heure.

**Colonnes.** `consommation`, `thermique` (une seule rubrique fossile, sans détail
gaz / charbon / fioul), `nucleaire`, `eolien`, `eolien_terrestre`,
`eolien_offshore`, `solaire`, `hydraulique`, `pompage`, `bioenergies`,
`ech_physiques` (**solde avec les régions limitrophes et l'étranger confondus**),
`stockage_batterie`, `destockage_batterie`, et les taux de couverture et de charge
`tco_*` / `tch_*` (%). **Pas de `taux_co2` régional, et pas d'échanges par
frontière.**

**Volumétrie.** 2024 : 210 816 lignes, parquet de 10,3 Mo, export en 2 min 18 s.
2015 → 2025 : ≈ 2,3 M lignes, ≈ 115 Mo en parquet. Le jeu complet fait
2 874 816 lignes.

**Contrôles.**

- Σ des 12 régions en 2024 : 440,18 TWh, contre 440,09 TWh pour le national sur
  les mêmes pas. L'écart moyen national − Σ régions vaut −10,7 MW. Le maximum de
  47 GW vient des doublons d'heure d'été : 24 lignes par pas au lieu de 12.
- Aucune valeur nulle sur les filières en 2024.

**Pièges.**

- Mêmes pièges d'horodatage et d'heure d'été qu'au national.
- `eolien` est typé `text` (cons-def), et `pompage`, `stockage_batterie` et
  `destockage_batterie` le sont dans le temps réel.
- Une colonne parasite `column_30` (cons-def) / `column_68` (TR) est présente.
- La description ODRÉ indique que les données régionales consolidées sont
  « issues de comptages complétés par des forfaits » (data.gouv.fr, fiche du jeu).
  Elles sont moins fiables au pas fin que le national.

**Verdict : GO** pour les profils régionaux de consommation et de production. À
utiliser **avec prudence** pour un bilan carbone régional : `thermique` n'est pas
ventilé et `ech_physiques` mélange les régions voisines et l'étranger.

## 3. Registre national des installations de production et de stockage (ODRÉ)

**URL.**

- photo courante : `.../datasets/registre-national-installation-production-stockage-electricite-agrege/`
  (« au 30/09/2026 », modifiée le 2026-10-13) ;
- millésimes annuels : suffixes `-311217` à `-311225` (31/12/2017 → 31/12/2025) ;
- registres RTE seuls pour 2015 et 2016 : `registre-national-installation-production-electricite-rte-2015`
  et `-2016`.

**Accès et licence.** Libre, Licence Ouverte 2.0. Producteurs de données : RTE,
Enedis, EDF SEI et les ELD (description du jeu).

**Contenu** (une ligne par installation, sauf agrégats) : nom, code EIC, commune
(code INSEE du point de livraison et de la commune d'implantation), IRIS, EPCI,
département, région, **poste source** (`postesource`), code S3REnR, tension de
raccordement, filière, combustible, technologie, puissances en **kW**
(`puismaxinstallee`, `puismaxrac`, charge et décharge pour le stockage), énergie
stockable (kWh), dates (raccordement, mise en service, déraccordement), régime,
gestionnaire de réseau, énergie annuelle glissante injectée, produite et soutirée
(kWh).

**Mesures** (métropole continentale, hors DOM et hors Corse ; `puismaxinstallee`
sommée) :

| Filière | 31/12/2024 (GW) | 30/09/2026 (GW) |
|---|---|---|
| Nucléaire | 61,37 (56 lignes) | 62,99 (57 lignes) |
| Solaire | 24,30 | 34,93 |
| Éolien | 25,10 | 26,98 |
| Hydraulique (STEP comprises) | 25,46 | 25,40 |
| Thermique non renouvelable | 18,63 | 18,14 |
| Stockage non hydraulique | 1,09 | 2,41 |
| Bioénergies | 2,58 | 2,60 |

Pour comparaison, le jeu ODRÉ `parc-national-annuel-prod-eolien-solaire` donne
24 497 MW de solaire et 24 492 MW d'éolien pour 2024 (périmètre non précisé,
probablement Corse comprise). L'écart est de −0,8 % sur le solaire et de +2,5 %
sur l'éolien. Je n'ai pas encore cherché d'où vient l'écart sur l'éolien.

**Pièges.**

- Le registre **inclut les ZNI (DOM)** : 2 318 lignes et 3,4 GW en septembre 2026.
  Il faut filtrer `coderegion` (01 à 06 = DOM, 94 = Corse). 13 lignes ont
  `coderegion` nul.
- Les **installations de moins de 36 kW sont agrégées** par commune (lignes
  « Agrégation des installations de moins de 36KW », `regime` nul, champ
  `nbinstallations` > 1) : 1,17 M installations pour 6,1 GW en septembre 2026.
  Elles n'ont pas de poste source.
- **Poste source renseigné à 75 %** en métropole (68 % fin 2024) et code S3REnR à
  28 %. Une capacité par poste est donc possible pour l'essentiel de la puissance
  raccordée en HTA / HTB, mais pas exhaustive.
- Unités en **kW** et en **kWh** (et non MW).

**Verdict : GO** pour la capacité par filière, commune, EPCI et région, et pour la
dynamique (millésimes annuels). **Partiel** pour la capacité par poste source.

## 4. Prix day-ahead France

### 4a. energy-charts (Fraunhofer ISE), sans jeton

**URL.** `https://api.energy-charts.info/price?bzn=FR&start=2024-01-01&end=2024-12-31`
(la version `/v2/price` existe aussi). Spécification OpenAPI :
<https://api.energy-charts.info/openapi.json> (v2.0, publiée le 2026-07-20) et
<https://api.energy-charts.info/llms.txt>.

**Accès.** Sans jeton. **Limite : 2 requêtes par minute et par endpoint, avec un
burst de 2 pour `/price`, et une limite « ajustée dynamiquement à la charge »**.
Au-delà, HTTP 429 avec `Retry-After`. Une année entière passe en une requête
(≈ 150 ko de JSON, 5 s).

**Licence.** Le champ `license_info` de la réponse FR vaut, mot pour mot :
« CC BY 4.0 (creativecommons.org/licenses/by/4.0) from Bundesnetzagentur |
SMARD.de ». La documentation liste les zones sous CC BY 4.0 : AT, BE, CH, CZ,
DE-LU, DE-AT-LU, DK1, DK2, **FR**, HU, IT-North, NL, NO2, PL, SE4 et SI. Pour les
autres zones (**ES** testée, IT hors North…), la réponse dit : « for private and
internal use only. The utilization of any data, whether in its raw or derived
form, for external or commercial purposes is expressly prohibited ». **Le prix
espagnol n'est donc pas publiable via energy-charts.** Les autres données
d'energy-charts sont en CC BY 4.0 « with attribution to energy-charts.info »
(llms.txt). La page HTML « publishing notes » est rendue en JavaScript et je n'ai
pas pu en lire le texte.

**Contenu testé** (`unix_seconds` = début de période, EUR/MWh) :

| Année | Valeurs | Pas | Nulls | Min | Max | Moyenne horaire |
|---|---|---|---|---|---|---|
| 2023 | 8 760 | 60 min | 0 | −134,94 | 276,12 | 96,86 |
| 2024 | 8 784 | 60 min | 0 | −87,29 | 284,21 | 58,02 |
| 2025 | 15 387 | 60 min jusqu'au 2025-09-30 21:00 UTC, puis **15 min** dès 2025-09-30 22:00 UTC | 0 | −118,01 | 473,28 | 61,07 |

Les moyennes sont des moyennes arithmétiques horaires, non pondérées par le
volume.

**Passage au pas de 15 min.** Le couplage day-ahead européen (SDAC) est passé au
pas de 15 min le **30 septembre 2025 (jour d'enchère), pour la livraison du
1er octobre 2025**. Sources : communiqué du NEMO Committee
(<https://nemo-committee.eu/assets/files/15-minute-mtu-in-sdac-was-implemented.pdf>),
communiqué EPEX SPOT
(<https://www.epexspot.com/en/news/successful-implementation-15-minute-market-time-unit-mtu-sdac>)
et confirmation du MCSC du 12 septembre 2025, après un report du 11 juin 2025
(communiqué OTE :
<https://www.ote-cr.cz/en/about-ote/ote-news/market-coupling-steering-committee-confirms-go-live-of-15-minute-mtu-in-sdac-on-trading-day-30-september-2025-for-delivery-day-1-october-2025>).
La série energy-charts le confirme : le premier quart d'heure est le
2025-10-01 00:00 heure de Paris (2025-09-30 22:00 UTC). Le décompte
15 387 = 6 551 h + 8 836 quarts d'heure boucle avec le changement d'heure du
26 octobre.

**Effet sur les séries** :

- **mélange de résolutions dans une même année**, qu'il faut ramener à une heure
  pour comparer à l'historique (RTE fait ainsi : voir § 6) ;
- **l'agrégation horaire masque des quarts d'heure négatifs.** D'octobre à
  décembre 2025, on compte 65 quarts d'heure négatifs, répartis sur 28 heures
  contenant au moins un quart d'heure négatif, alors que seules 20 heures ont une
  moyenne négative. Pour valoriser une flexibilité de data center, c'est le quart
  d'heure qui compte.

**Pièges.** Les horodatages marquent le début de la période et sont en UTC (unix).
Une requête par jour (`start=2025-01-01`) est interprétée en heure locale de la
zone.

**Profondeur historique FR** : des données existent à chacun des sondages,
soit le 5 janvier 2015, le 4 janvier 2016, le 2 janvier 2017, le 2 janvier 2018,
le 1er octobre 2018 et le 2 janvier 2019 (une journée de valeurs horaires à
chaque fois, CC BY 4.0 SMARD). En revanche, **le 1er janvier 2015 renvoie HTTP 404 « No content
available »** : la série commence probablement le 5 janvier 2015 (non vérifié
jour par jour). **Seules les années 2023, 2024 et 2025 ont été vérifiées
complètes** (aucune valeur nulle). Pour 2015 → 2022, l'exhaustivité reste à
contrôler au moment du pipeline.

**Verdict : GO** pour FR depuis début 2015, ainsi que pour DE-LU, CH et IT-North,
dont la licence CC BY a été testée (BE et NL sont annoncés en CC BY par la
documentation, mais n'ont pas été testés).

### 4b. ENTSO-E Transparency Platform

`https://web-api.tp.entsoe.eu/api?documentType=A44&…` sans `securityToken` renvoie
**HTTP 401** (testé). Je n'ai pas créé de compte, comme demandé. ENTSO-E reste la
source de référence pour les prix de toutes les zones, la production par groupe
(A73), les indisponibilités et les flux. Le jeton est gratuit.

## 5. Échanges et mix des voisins

**Côté France (open data RTE) :**

- `ech_comm_*` par frontière dans éCO2mix national (pas 30 min). L'Allemagne et
  la Belgique y sont regroupées.
- `ech_physiques` : solde physique total uniquement, **pas par frontière** dans
  éCO2mix ODRÉ.
- Jeu ODRÉ `imports-exports-commerciaux` (horaire, 2005 → 2025, MWh). **En 2024,
  il a 2 lignes par (date, position) pour 8 702 heures sur 8 786, avec des valeurs
  différentes, et les totaux `export_france` / `import_france` sont nuls sur
  toute l'année.** Je n'ai pas compris cette structure : **à ne pas utiliser** sans
  clarification auprès de RTE.

**energy-charts** (`/public_power`, `/cbet`, `/cbpf` ; test du 1er juin 2024) :

| Pays | Pas | Séries | Remarque |
|---|---|---|---|
| FR | 60 min | 18 | Load 2024 = 429,7 TWh contre 440,1 TWh éCO2mix (**−2,4 %**) ; nucléaire 360,1 contre 361,7 ; solaire 23,3 contre 24,5 |
| DE | 15 min | 21 | lignite, houille et gaz séparés |
| BE | 60 min | 17 | |
| ES | 15 min | 19 | |
| IT | 60 min | 20 | national, pas par zone |
| CH | 60 min | 12 | pas de fossile (cohérent avec le parc suisse) |
| **UK** | 30 min | 9 | **Load moyen 663 MW : ce n'est que l'Irlande du Nord**. Pas de nucléaire, de solaire ni d'éolien offshore. **Inutilisable pour la Grande-Bretagne** |

- `/cbet` (échanges commerciaux) et `/cbpf` (flux physiques) pour FR : pas de
  15 min, **unité GW**, ventilés par pays (BE, DE, IT, ES, CH, UK) plus une somme.
  Les autres endpoints sont en MW.
- Les données d'energy-charts viennent pour l'essentiel d'ENTSO-E. L'écart de
  −2,4 % sur la charge française montre qu'**il ne faut pas mélanger** les
  séries France d'energy-charts et d'éCO2mix : éCO2mix fait foi pour la France.

**Grande-Bretagne : Elexon Insights (BMRS), sans clé.**
`https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?settlementDateFrom=2024-06-01&settlementDateTo=2024-06-01&format=json`
renvoie HTTP 200 : 912 lignes au pas de 30 min, filières BIOMASS, CCGT, COAL,
NUCLEAR, WIND, OCGT, OIL, PS, NPSHYD, OTHER et INT* (interconnexions, dont
`INTFR`, `INTIFA2` et `INTELEC` vers la France). **À vérifier** : FUELHH ne couvre
a priori que la production comptée au transport, sans le solaire ni l'éolien
raccordés en distribution. La licence (« BMRS Data Licence Terms ») n'a pas été
lue.

**Verdict : partiel.** On peut construire sans jeton un mix horaire des voisins
(DE, BE, ES, IT, CH) et des flux FR par frontière (energy-charts). Restent trois
manques : la Grande-Bretagne (via Elexon, à valider), les prix ES et IT hors North
(licence restrictive) et la cohérence entre sources. Pour un facteur marginal
sérieux, **le jeton ENTSO-E devient vite nécessaire** : source unique et
homogène, prix de toutes les zones, production par groupe.

## 6. Prix négatifs, modulation nucléaire, écrêtement

### 6a. Heures à prix négatif (France, day-ahead)

Calcul sur l'échantillon energy-charts. L'heure est en UTC, l'année civile en
heure de Paris. Après le 1er octobre 2025, une heure est comptée négative si la
**moyenne de ses 4 quarts d'heure** est négative, comme dans la note 10 du
BE2025.

| Année | Heures < 0 (calcul) | Heures ≤ 0 (calcul) | Chiffre RTE publié |
|---|---|---|---|
| 2023 | **147** | 184 | 147 (BE2024, rapport complet, chapitre Prix : « 361 heures en 2024 contre 147 en 2023 ») |
| 2024 | **352** | 549 | **361** (BE2024, même passage, et synthèse web) puis **352** (BE2025, chapitre Prix : « 513 heures en 2025 […] (352 en 2024) ») |
| 2025 | **513** (493 avant le 1er oct., 20 après) | 732 | 513 (BE2025) |

**Ça boucle exactement avec les derniers chiffres RTE.** RTE a révisé son propre
chiffre 2024 de 361 à 352 h entre deux éditions, sans explication que j'aie
trouvée. Le site doit citer 352 (BE2025) et signaler la révision. Le grand nombre
d'heures à prix nul (549 − 352 = 197 en 2024) mérite aussi d'être montré.

### 6b. Modulation nucléaire

Il n'existe **pas de série ouverte de « modulation »**. Ce qui est disponible
sans jeton :

- `production-nette-nucleaire` (ODRÉ) : production nucléaire nette nationale
  **horaire depuis 2001** (GWh par heure, « convention débutante »). 2024 :
  361,71 TWh, à comparer aux 361,7 TWh du BE2024.
- la colonne `nucleaire` d'éCO2mix (30 min).

On peut donc construire un **proxy** : la baisse de production aux heures de prix
négatifs ou nuls, par rapport à l'enveloppe journalière ou hebdomadaire. Une vraie
mesure demanderait la disponibilité déclarée par réacteur (REMIT / ENTSO-E, avec
jeton) ou la production par groupe (ENTSO-E A73 ou portail data.rte-france.com,
avec compte). Le BE2024 rappelle qu'EDF classe certains arrêts en « modulation »
et non en « indisponibilité » (rapport complet, chapitre Production, note 4). La
frontière entre les deux n'est donc pas observable de l'extérieur.

**Verdict : partiel.**

### 6c. Écrêtement éolien et solaire

**Aucune série horaire ouverte trouvée** dans le catalogue ODRÉ, qui compte
185 jeux, tous listés par le script. RTE ne publie que des estimations annuelles,
obtenues par écart à une prévision interne :

- **2024 : ≈ 1,7 TWh**, soit 2,4 % de la production éolienne et solaire. Le
  détail diffère selon le support : « environ 0,9 TWh » d'éolien et « 0,8 TWh » de
  solaire dans le rapport complet BE2024, contre 0,9 et 0,7 TWh dans la synthèse
  web. Puissance écrêtée moyenne de 4,5 GW aux heures de prix négatif, maximum de
  12 GW (synthèse BE2024).
- **2025 : 0,1 TWh** écrêtés à la demande de RTE (ajustements à la baisse, BE2025),
  en plus des arrêts sur incitation de marché.

Un proxy est envisageable : la production observée comparée à une production
« attendue », calculée avec le rayonnement et le vent ODRÉ
(`rayonnement-solaire-vitesse-vent-tri-horaires-regionaux`, pas de 3 h) et le
parc installé. Il serait approximatif et devrait être présenté comme tel.

**Verdict : NO** en donnée mesurée. Proxy à construire.

## 7. Recoupements

### Consommation annuelle

Somme des demi-heures éCO2mix définitives (MW × 0,5), année civile en heure de
Paris :

| | 2024 | 2025 |
|---|---|---|
| éCO2mix national, Σ MW × 0,5 h | **440,086 TWh** | **443,879 TWh** |
| RTE, consommation brute (Bilan) | 442,2 TWh (BE2024) | 446,1 TWh (BE2025) |
| Écart brut | **−0,48 %** | **−0,50 %** |
| ODRÉ `consommation-annuelle-brute` | 442,336 TWh (définitif) | 446,146 TWh (consolidé) |
| dont Corse (ODRÉ `consommation-annuelle-brute-regionale`) | 2,256 TWh | 2,266 TWh |
| **ODRÉ, Σ des 12 régions continentales** | **440,079 TWh** | **443,881 TWh** |
| **Écart éCO2mix − continent** | **+7 GWh (+0,002 %)** | **−2 GWh (−0,000 %)** |

**Ça boucle.** L'écart de −0,5 % avec le Bilan correspond exactement à la Corse,
que le Bilan inclut (« Consommation brute : consommation d'électricité au
périmètre France (Corse comprise) incluant les pertes sur le réseau mais excluant
la consommation pour le pompage », glossaire du BE2024). La consommation
éCO2mix est donc **pertes comprises, pompage exclu, Corse exclue**. Le résidu de
quelques GWh correspond à l'ordre de grandeur de l'artefact d'heure d'été (une
heure dupliquée en mars, une heure manquante en octobre, ≈ 40 à 47 GWh chacune).
Le Bilan 2024 a d'ailleurs été révisé de 442,2 à 442,3 TWh dans ODRÉ
(recalcul de l'autoconsommation photovoltaïque).

Autres recoupements 2024 :

- nucléaire : éCO2mix 361,70 TWh, ODRÉ horaire 361,71 TWh, BE2024 361,7 TWh ;
- solde physique : éCO2mix −89,6 TWh (exportateur), BE2024 « 89 TWh » ;
- production : éCO2mix 537,7 TWh, BE2024 539,0 TWh, ODRÉ
  `prod-national-annuel-filiere` 539,3 TWh (révisée). L'écart de 1,3 à 1,6 TWh
  devrait correspondre à la Corse et à l'autoconsommation photovoltaïque :
  hypothèse plausible, non chiffrée séparément.

### Intensité carbone moyenne

| | 2024 | 2025 |
|---|---|---|
| éCO2mix `taux_co2`, moyenne **pondérée par la production** | 20,10 g/kWh | 18,36 g/kWh |
| éCO2mix `taux_co2`, moyenne arithmétique (méthode fausse) | 18,99 | 17,32 |
| RTE, intensité de la **production** (émissions directes) | **21,7** gCO2eq/kWh (BE2024) | **19,6** (BE2025) |
| Écart, moyenne pondérée | **−7,4 %** | **−6,3 %** |
| ODRÉ `part-enr-intensite-ges-conso-tr` (intensité de la **consommation**, imports compris), moyenne pondérée par la consommation | 22,13 | **20,15** |
| RTE, intensité de la **consommation** | pas de valeur annuelle trouvée (recherche texte dans le rapport complet BE2024) | **20,0** (BE2025) |

**L'intensité de la consommation boucle** (+0,75 % en 2025). **L'intensité de la
production éCO2mix ne boucle pas** : elle est inférieure de 6 à 7 % au Bilan. En
émissions, l'écart vaut 21,7 × 539,3 − 20,10 × 537,7 ≈ 0,9 MtCO2eq en 2024, du
même ordre en 2025, pour 1,3 à 1,6 TWh de production supplémentaire au Bilan.
Mon hypothèse principale, **non vérifiée**, est la Corse : sa production
thermique au fioul est incluse dans le Bilan et absente d'éCO2mix, et 0,9 Mt pour
≈ 1,5 TWh ferait ≈ 600 g/kWh, un ordre de grandeur de production au fioul. Autre
cause possible : des facteurs d'émission différents, CO2 seul dans éCO2mix
(« Estimation des émissions de CO2 » selon la spécification) contre CO2eq dans le
Bilan, dont le tableau de facteurs donne par exemple 331 g pour les CCG et 769 g
pour le fioul en émissions directes. **Conséquence : pour l'intensité moyenne
annuelle, citer le Bilan. Pour le profil horaire, utiliser éCO2mix en signalant
le biais d'environ −7 %.** Et ne jamais présenter ni l'un ni l'autre comme un
facteur marginal.

**Distribution horaire : non reproduite.** Le BE2024 (chapitre Émissions) écrit
trois choses :

1. en 2024, « près de la moitié du temps, l'intensité de la production comme de la
   consommation a été en dessous de 10 gCO2eq/kWh » ;
2. le maximum de 2024 a été de 67 gCO2eq/kWh ;
3. en 2023, l'intensité de la consommation « avait dépassé 100 gCO2eq/kWh lors
   d'environ 3 % du temps ».

Mes calculs :

| | Part < 10 g en 2024 | Maximum 2024 | Part > 100 g en 2023 |
|---|---|---|---|
| ODRÉ `part-enr-intensite-ges-conso-tr` | 5,3 % | 68 | 0,35 % |
| éCO2mix `taux_co2` | 25,9 % | 69 | 0 % |

Le maximum boucle. **La part du temps sous 10 g et le dépassement de 100 g en
2023 ne bouclent pas du tout.** Je n'ai pas d'explication : méthode ou facteurs
différents dans le Bilan, ou révision des séries ouvertes. Il ne faut pas reprendre
ces deux phrases du Bilan sans avoir compris l'écart.

Note de méthode : la moyenne arithmétique des pas de temps sous-estime
l'intensité de 1 à 1,5 g/kWh, car les heures à forte intensité sont aussi les
heures à forte production ou consommation. Il faut toujours pondérer.

## Trous et risques

1. **Facteur marginal** : aucune source ne le fournit. Il faut le modéliser
   (technologie marginale par le prix, ou régression des variations d'émissions
   France + voisins sur les variations de demande) à partir des mix voisins et des
   flux. Sans jeton ENTSO-E, la Grande-Bretagne manque dans energy-charts et les
   prix ES et IT ne sont pas publiables. **Recommandation : demander le jeton
   ENTSO-E maintenant.**
2. **Écrêtement** : pas de série. Seulement des chiffres annuels RTE, révisés et
   arrondis différemment selon les supports.
3. **Modulation nucléaire** : proxy seulement, sans disponibilité par réacteur.
4. **Prix FR sur energy-charts avant 2023** : présents dès le 5 janvier 2015 aux
   sondages, mais l'exhaustivité 2015 → 2022 n'est pas vérifiée, et les
   premiers jours de janvier 2015 manquent.
5. **Horodatage éCO2mix** : la convention « fin de demi-heure » est déduite, pas
   documentée. Il faut la tester à nouveau à chaque rafraîchissement : le test du
   nucléaire ODRÉ est dans le script.
6. **Révisions** : le temps réel devient consolidé puis définitif, et
   l'autoconsommation photovoltaïque a été recalculée sur 2022-2024 ; RTE a aussi
   révisé le nombre d'heures négatives de 2024 (361 → 352). Il faut figer chaque
   extraction (date, nature) et l'afficher.
7. **Jeu `imports-exports-commerciaux`** : structure incompréhensible en 2024
   (doublons, totaux nuls). À éviter.
8. **Lenteur des exports ODRÉ** (≈ 2 à 5 min par an et par jeu) et
   **rate limit energy-charts** (2 req/min, ajusté à la charge). Un
   téléchargement complet 2015 → 2025 prendra de l'ordre d'une heure, qu'il faut
   mettre en cache, et le pipeline doit être incrémental.
9. **Licence energy-charts** : CC BY 4.0 déclarée par energy-charts sur des
   données en grande partie issues d'ENTSO-E et de SMARD. Pour un site public,
   citer energy-charts et la source amont (SMARD pour les prix).

## Recommandation pour le pipeline

**Granularité commune : l'heure UTC, ce n'est pas une erreur.** Elle est
défendable pour la simulation (couverture horaire, logique 24/7 CFE), à quatre
conditions :

1. **Stocker le brut à sa résolution native** (30 min éCO2mix, 15 ou 60 min pour
   les prix et les voisins), en parquet, avec la nature (TR, consolidé, définitif)
   et la date d'extraction. L'agrégat horaire est une **vue dérivée**.
2. **Agréger correctement** :
   - éCO2mix : heure *h* = moyenne des points *h*:30 et *h+1*:00 (horodatage à la
     fin), après dédoublonnage UTC des jours de changement d'heure ;
   - prix : moyenne simple des quarts d'heure (convention RTE). Il faut **garder
     les quarts d'heure** pour le module de flexibilité, car l'heure masque des
     quarts d'heure négatifs ;
   - énergies : MWh = moyenne horaire des MW × 1 h. Ne jamais sommer des MW.
3. **Afficher en heure de Paris** les profils journaliers et les heatmaps
   calendaires. En UTC, le pic solaire se décale d'une heure entre l'été et
   l'hiver, ce qui troublerait une lectrice experte. Les bilans annuels se font
   sur l'année civile locale, comme RTE.
4. **Tests de cohérence automatiques** dans le pipeline, issus de ce spike :
   - Σ conso éCO2mix ≈ Σ ODRÉ régional hors Corse (tolérance 0,05 %) ;
   - nucléaire éCO2mix ≈ ODRÉ horaire (écart moyen < 5 MW) ;
   - heures négatives par an = valeurs RTE (147, 352, 513) ;
   - intensité de la consommation pondérée ≈ BE (± 2 %).

**Séries à retenir** (2015 → 2025, puis mise à jour) :

| Série | Source | Résolution native |
|---|---|---|
| Consommation, production par filière, pompage, solde physique, échanges commerciaux par frontière, `taux_co2` (national) | éCO2mix cons-def + TR | 30 min / 15 min |
| Idem par région (12 régions) | éCO2mix régional | 30 min |
| Intensité GES de la consommation (imports compris) | ODRÉ `part-enr-intensite-ges-conso-tr` (depuis 2021) | 60 min |
| Nucléaire national | ODRÉ `production-nette-nucleaire` | 60 min |
| Prix day-ahead FR (+ DE-LU, BE, CH, IT-North) | energy-charts (ENTSO-E quand le jeton sera là) | 60 → 15 min |
| Mix des voisins, flux FR par frontière | energy-charts (`public_power`, `cbpf`, `cbet`) | 15 à 60 min |
| GB | Elexon FUELHH (à valider) | 30 min |
| Parc par filière, commune et poste | Registre ODRÉ (millésimes annuels + photo courante) | photo |
| Références annuelles | ODRÉ `consommation-annuelle-brute(-regionale)`, `prod-national-annuel-filiere` ; Bilans RTE | an |

**À ne pas faire** : utiliser `taux_co2` ou l'intensité de la consommation comme
facteur marginal ; mélanger les séries France d'energy-charts et d'éCO2mix ;
utiliser `imports-exports-commerciaux` en l'état.
