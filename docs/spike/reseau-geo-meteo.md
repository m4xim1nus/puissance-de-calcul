# Spike d'accès — réseau, géographie, météo

*Date des tests : 25 novembre 2026. Scripts : `pipeline/explo/spike_reseau.py`.
Échantillons : `data/raw/spike/reseau/` (non versionné). Résumé chiffré reproductible : `data/raw/spike/reseau/summary.json`.*

Convention de lecture : **testé** = j'ai fait la requête et lu la réponse ; **non vérifié** = lu dans une page ou un résultat de recherche, pas
reproduit ; **non testé** = je n'ai pas pu ou pas voulu essayer.

## Tableau récapitulatif

| # | Source | Accès testé | Licence | Granularité | Verdict |
|---|---|---|---|---|---|
| 1a | Caparéseau (capareseau.fr), injection | Carte web seule, **aucun téléchargement** repéré | « publiques, réutilisation permise sous réserve de mentionner la source », mais modification interdite ; pas de licence formelle | Poste source | **NO** en open data ; **partiel** via extraits tiers (Loiret 2023) |
| 1b | Capacité d'accueil en **soutirage** (consommation) | Rien d'open data trouvé | — | — | **NO** (carte annoncée par RTE, publication non confirmée) |
| 1c | RTE — `contraintes-region` (flexibilité requise, 3-5 ans) | CSV ODRÉ testé | Licence Ouverte v2.0 | Ouvrage (ligne) lié à 3 postes, région | **Partiel** (côté injection EnR, pas de géométrie) |
| 2 | ODRÉ postes RTE | CSV testé, 5 042 lignes | Licence Ouverte v2.0 | Poste (code, nom, tension, département) | **Partiel : pas de coordonnées** |
| 2 | ODRÉ lignes aériennes / souterraines | CSV testé, 9 221 + 3 825 tronçons | Licence Ouverte v2.0 | Tronçon, tension | **Partiel : pas de géométrie** |
| 3 | S3REnR | Documents PDF (RTE, préfectures) ; pas de tableur trouvé | Non précisée | Région, poste | **Partiel / manuel** |
| 4a | Open-Meteo Archive (ERA5) | API testée, 2 points × 1 an | Données CC BY 4.0 ; API gratuite non commerciale | Horaire, 0,25° | **GO** (sous réserve de l'usage non commercial) |
| 4b | PVGIS 5.3 `seriescalc` | API testée, 2 points × 1 an | Réutilisation autorisée avec mention de la source (non vérifié pour l'API) | Horaire, point | **GO**, 2005-2023 seulement |
| 4c | renewables.ninja | API répond **sans jeton** (1 requête) ; quota annoncé 5/jour | CC BY-NC 4.0 | Horaire, point | **Partiel** (non commercial, compte nécessaire en pratique) |
| 5a | france-geojson (gregoiredavid) | Testé | Licence Ouverte (Admin Express), pas de fichier LICENSE | Régions, départements, communes | **GO** pour régions/départements ; millésime **2018** |
| 5b | IGN Admin Express | Catalogue testé ; archives non téléchargées | Licence Ouverte Etalab 2.0 (non vérifié sur la page de la source) | Commune → région | **GO** (à télécharger au moment du pipeline) |
| 5c | geo.api.gouv.fr | Testé (communes du 77) | — (non vérifié) | Commune, par département | **GO** pour un département |
| 6 | PUE / températures de conception | Rien d'ouvert par site | — | — | **NO** (agrégats européens seulement) |

---

## 1. Capacités d'accueil du réseau

### 1a. Caparéseau : injection uniquement, pas de téléchargement

- URL : <https://www.capareseau.fr/>. Testé : la page répond (HTTP 200), son titre est « Capacités d'accueil **en production** du réseau », et
  la mention légale dit qu'elle « affiche les possibilités de raccordement aux réseaux de transport et de distribution des installations de
  **production** d'électricité ».
- La page d'accueil ne contient aucun lien de téléchargement ni d'API (les scripts sont Leaflet, jQuery, cookies, autocomplétion). Je n'ai
  **pas** rétro-ingénierié les appels internes de la carte : ce serait du scraping hors des conditions affichées et je ne l'ai pas tenté.
  Existence d'une API cachée : **non vérifié**.
- Avertissement du site : les capacités sont « indicatives », « non engageantes pour les gestionnaires ».
- Conditions (`/mentions-legales`, testé) : « Les données publiées […] sont publiques et leur réutilisation est permise sous réserve de
  mentionner la source », mais « la modification, la dénaturation totale ou partielle du site ou de son contenu […] est interdite » et toute
  reproduction de contenu demande une autorisation écrite de RTE. Les fonds IGN sont sous licence n° 2220 (copie interdite). Ce n'est
  **pas** une licence ouverte : risque juridique pour une republication.
- **Extrait officiel tiers, testé** : data.gouv.fr, jeu « Capacité d'acceuil du réseau électrique » (DDT du Loiret), 
  <https://www.data.gouv.fr/datasets/capacite-dacceuil-du-reseau-electrique>, licence `lov2`, shapefile
  (<https://atom.geo-ide.developpement-durable.gouv.fr/atomArchive/GetResource?id=55304b34-d48c-45a8-84c5-b5e3d7e805c3&dataType=dataset>,
  9,7 ko). Contenu : **58 postes du Loiret**, extraction du **12 avril 2023** (champ `DTE_EXTR`), champs `CODE, NOM, S3RENR, TX_CAPA,
  PU_RACCS3, PU_DEVS3, CAPAS3, PU_RACC, PU_DEV, CAPA, SATURATION`, géométrie point en Lambert-93. Les unités et la définition des champs ne
  sont pas dans le shapefile (une fiche XML l'accompagne, non lue). La description du jeu renvoie vers capareseau.fr pour des données « plus
  complètes et actualisées ». Sert à prouver la structure, pas à alimenter le site (un département, 2023).
- **Clé de jointure, testée** : le champ `CODE` de ce shapefile correspond au `code_poste` des postes ODRÉ pour 56 des 58 postes (échecs :
  `ELOI3`, `LOIR1`). Cela donne un identifiant de poste commun, mais pas de coordonnées côté ODRÉ (voir §2).
- Un autre jeu data.gouv « Capacités d'accueil du réseau »
  (<https://www.data.gouv.fr/datasets/capacites-daccueil-du-reseau>, EDF SEI, licence `lov2`, CSV/GeoJSON/shapefile) concerne **Corse et
  outre-mer** uniquement : hors périmètre métropole. Testé via l'API data.gouv.
- Enedis (capacités HTA par poste source) : le portail `data.enedis.fr` redirige vers `opendata.enedis.fr` dont l'API Explore v2.1 que j'ai
  essayée répond 404/410. Je n'ai donc **pas pu confirmer** l'existence d'un export des capacités d'accueil HTA par poste source. À
  revérifier à la main.
- Verdict : **NO** pour un jeu national téléchargeable ; **partiel** si on accepte un extrait départemental daté.

### 1b. Soutirage / consommation : rien d'ouvert trouvé

Constats (références lues, pas reproduites sauf mention) :

- RTE, « Les data centers en chiffres clés » (<https://www.rte-france.com/bases-electricite/consommation-electricite/essor-data-centers-france>,
  page datée 01/06/2026, lue) : environ **18 GW réservés pour environ 80 projets en mai 2026**, contre environ 5 GW (une quarantaine de projets) fin 2024 ;
  environ 7 GW réservés en Île-de-France, 6 GW dans les Hauts-de-France. Page lue pour la présence de cartes ou de jeux de données de
  capacité par poste ou zone : **aucune carte ni jeu de données de capacité n'y est publié ou lié**.
- Schéma décennal de développement du réseau (SDDR) 2025, fiche 5 (PDF, **testé**, texte extrait avec `pdftotext`) :
  <https://assets.rte-france.com/prod/public/2025-02/SDDR2025-principales-orientations-fiche5-raccordement-industrie_0.pdf>. RTE y écrit qu'il
  « mettra à disposition dans les prochaines semaines une cartographie des zones favorables pour des projets industriels d'une puissance de
  l'ordre de 250 MW et de l'ordre de 750 MW » (zones du réseau 400 kV), et le PDF indique que « la carte […] sera publiée dans les prochaines
  semaines » : à la date du PDF (février 2025) la carte n'était pas dans le document. **Je n'ai pas trouvé confirmation de sa publication ni de
  son format** (image, carte web, ou données). Le même document donne une carte des demandes de raccordement (figure 5.6), image dans un PDF.
- Ce qui existe en open data côté consommation (testé, ODRÉ, Licence Ouverte v2.0) : `conso-rpt-par-secteur`
  (mensuelle 2014-01 → 2026-10, 9 secteurs, **pas de secteur « data centers »** : ils sont dans « Tertiaire »), `soutirages-regionaux-quotidiens-*`,
  `consommation-annuelle-par-iris` (industriels raccordés au transport, par IRIS), et `suivi-projet-raccordement-enr` (projets EnR en
  développement au 31/12/2024, par région, 193 lignes, testé). Aucun n'indique de **marge disponible en soutirage** par poste.
- Conclusion : la **capacité d'accueil en soutirage par poste** est, à ma connaissance et d'après ce que j'ai pu tester, **inexistante en open
  data** ; au mieux des cartes de zones (400 kV) annoncées ou publiées sous forme d'image/carte web, et des totaux agrégés par région
  (GW réservés). Verdict : **NO**.

### 1c. À retenir côté réseau : `contraintes-region`

ODRÉ `contraintes-region` (<https://odre.opendatasoft.com/explore/dataset/contraintes-region/>, testé, 407 lignes, Licence Ouverte v2.0, daté
décembre 2024, modifié le 2025-01-09) : contraintes résiduelles prospectives à 3-5 ans sur le réseau de transport (hors Corse), par ouvrage,
avec les 3 postes influents (`poste_1..3` et pourcentage de report), occurrence (« Moyenne : entre 25 et 75 fois par an »), durée, pérennité.
Elles traduisent un besoin de **flexibilité** lié à l'accueil des **EnR** : c'est le côté injection. Utile comme contexte (où le réseau est
contraint), pas comme marge de soutirage. Les colonnes `geom` et `centroid` existent mais sont **vides** dans l'export testé. Le jeu voisin
`energies-et-puissances-regionales-liees-au-contraintes` (12 lignes) donne la puissance EnR installée, la puissance à compenser et l'énergie non
évacuée par saison, par région.

---

## 2. Postes et lignes RTE (ODRÉ)

**Point bloquant : les coordonnées ont été retirées.** Testé : les exports GeoJSON renvoient `"geometry": null` pour tous les objets, et la
description des jeux dit que RTE « a fait évoluer l'accès aux données GPS des infrastructures […] pour des raisons de sécurité publique ».
Les tracés ne sont donc **pas** disponibles : on ne peut pas faire une carte du réseau avec ces jeux.

| Jeu (identifiant ODRÉ) | Contenu | Volume | Mise à jour | Licence |
|---|---|---|---|---|
| `postes-electriques-rte` | Sites RTE et points de piquage (« au 16 juin 2026 ») : `code_poste, nom_poste, fonction, etat, tension, departement` | 5 042 (4 232 « poste de transformation », 810 « point de piquage ») | 2026-06-16 | Licence Ouverte v2.0 |
| `lignes-aeriennes-rte-nv` | Tronçons aériens : `code_ligne, nom_ligne, etat, tension, nombre_circuit`, ouvrages partageant les pylônes | 9 221 | 2025-07-03 (annoncé « au 16 juin 2026 » dans le titre : incohérence à noter) | Licence Ouverte v2.0 |
| `lignes-souterraines-rte-nv` | Tronçons souterrains, mêmes champs | 3 825 | 2026-06-16 | Licence Ouverte v2.0 |

- URL type : `https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/<id>/exports/csv?delimiter=%3B&limit=-1`. L'ancien domaine
  `opendata.reseaux-energies.fr` redirige (HTTP 301) vers `odre.opendatasoft.com`. CSV de 378 ko (postes), 1,08 Mo (lignes aériennes), 384 ko
  (lignes souterraines).
- Tension (testé, postes) : 63 kV (2 658), 225 kV (1 038), 90 kV (1 016), 400 kV (200), 45 kV (51), 150 kV (42), <45 kV (31), courant continu (3),
  hors tension (3). Une seule valeur de tension par poste (pas de liste des niveaux présents), à interpréter avec prudence.
- Localisation : seulement le **département**. Pas de commune, pas de capacité de transformation (MVA), pas de puissance de soutirage.
- Pièges : la tension est du texte (« 63kV », « COURANT CONTINU », « HORS TENSION ») ; BOM UTF-8 en tête des CSV ; `etat` distingue « EN
  EXPLOITATION » (4 967) et « ACCORD ADMINISTRATIF » (75) ; les codes de poste ont 5 caractères avec des préfixes particuliers (`.PIOS`, `1AMBI`).
- Pistes pour retrouver une géométrie (**non testées**, à décider) : OpenStreetMap `power=substation` (j'ai tenté Overpass : 502 puis
  délai dépassé sur deux miroirs, donc **non vérifié**) ; extraits départementaux de la DDT (point du §1a, avec le `CODE` joint à 56/58). Les
  noms des postes ODRÉ permettent un rapprochement approximatif avec OSM, à valider.
- Verdict : **partiel** (liste fiable et ouverte, utile pour compter par tension et département, mais pas cartographiable).

---

## 3. S3REnR

- Les schémas régionaux de raccordement au réseau des énergies renouvelables sont publiés **en PDF** : « états techniques et financiers » annuels
  sur le site de RTE, par région, par exemple
  <https://assets.rte-france.com/prod/public/2025-06/2025-06-26-etats-techniques-financiers-2024-s3renr-occitanie.pdf>
  (application/pdf, environ 5,2 Mo ; le téléchargement a expiré à 4,1 Mo sur 5,2 : taille de 143 pages lue sur l'entête du fichier tronqué,
  à reconfirmer), et les schémas eux-mêmes sur les sites des préfectures et DREAL. Je n'ai **pas trouvé** de tableur ou de jeu de données
  ouvert national pour les S3REnR (recherches data.gouv.fr sur plusieurs libellés : aucun résultat). Le côté « machine-readable » se limite à
  Caparéseau (carte) et à des extraits départementaux (§1a).
- Ce qu'on y trouve (texte du PDF, non extrait en tableau) : capacités réservées, quote-part, postes à créer ou renforcer. Pas de soutirage.
- Utilisabilité : extraction de tableaux de PDF par région possible mais manuelle et fragile (12 régions, formats hétérogènes, mises à jour
  décalées). **Verdict : partiel / pas pour un pipeline automatique.** Et c'est de l'injection : hors question centrale (data centers = soutirage).

---

## 4. Météo, refroidissement et productible

Points testés : **Fouju** (48,58 ; 2,77) et **Marseille** (43,30 ; 5,37), année **2023**, une année complète de 8 760 heures. Éolien : Fouju, 2019 (pour
comparer à renewables.ninja).

### 4a. Open-Meteo Historical Weather API

- URL : `https://archive-api.open-meteo.com/v1/archive` — requête testée avec `models=era5`, `timezone=UTC`, `wind_speed_unit=ms`,
  `hourly=temperature_2m,relative_humidity_2m,shortwave_radiation,wind_speed_100m,wind_speed_10m,global_tilted_irradiance` (`tilt=35`, `azimuth=0`).
  Sans jeton. Réponse JSON de 408 ko par point et par an.
- Variables : toutes présentes, y compris `wind_speed_100m` (renvoyé avec des valeurs pour `era5`).
- Profondeur (documentation lue, <https://open-meteo.com/en/docs/historical-weather-api>) : ERA5 0,25° de 1940 à aujourd'hui (délai annoncé
  de 5 jours), ERA5-Land 0,1° de 1950. J'ai testé le 1er janvier 1940 : la réponse existe. Sans paramètre `models`, la maille et les valeurs
  diffèrent : le point Fouju est ramené à (48,6116 ; 2,7319) au lieu de (48,5 ; 2,75) avec `era5`. **Fixer `models` explicitement.** Une
  requête sur les derniers jours de novembre 2026 a renvoyé des valeurs jusqu'à l'heure en cours : l'origine (réanalyse ou prévision) de ces
  dernières valeurs n'est pas indiquée, ne pas s'en servir pour les années de référence.
- Limites (page de conditions, lue) : gratuit pour usage **non commercial**, moins de 10 000 appels par jour, 5 000 par heure, 600 par minute.
  Le coût est pondéré : l'en-tête `X-RateLimit-Cost` a affiché **18,25** pour une année horaire de 7 variables (limite : 600 par minute).
  Pour un pipeline de quelques dizaines de sites × 10 ans : largement dans les limites si on espace les appels.
- Licence : données **CC BY 4.0** (page <https://open-meteo.com/en/licence>, lue) avec mention de la source et lien ; mention Copernicus Climate Change
  Service demandée pour ERA5. **Piège** : si le site finit par avoir une activité commerciale, l'usage de l'API gratuite n'est plus permis ; il
  faudra l'API payante ou un auto-hébergement. À trancher avec l'auteur.
- Pièges d'unités et de temps (testés ou documentés) : avec `timezone=UTC` les horodatages sont en UTC ; `shortwave_radiation` est la
  **moyenne de l'heure précédente** en **W/m²** (documentation), donc 1 h × W/m² = Wh/m² ; la valeur « instantanée » est une variable séparée ;
  `wind_speed_100m` par défaut en km/h (j'ai forcé `ms`) ; humidité en %.

### 4b. PVGIS 5.3 `seriescalc`

- URL testée : `https://re.jrc.ec.europa.eu/api/v5_3/seriescalc?lat=48.58&lon=2.77&startyear=2023&endyear=2023&pvcalculation=1&peakpower=1&loss=14&angle=35&aspect=0&raddatabase=PVGIS-SARAH3&outputformat=json`.
  Sans jeton. Réponse de 0,82 Mo par point-année (8 760 lignes).
- Bases : `PVGIS-SARAH3` et `PVGIS-ERA5`, **années 2005 à 2023** pour les deux (l'API répond 400 pour 2004 et pour 2024-2025 : testé). La version
  v5_2 ne propose plus que `PVGIS-SARAH2`/`NSRDB`/`ERA5` jusqu'à 2020 : utiliser `v5_3`.
- Limite (page JRC, lue via recherche) : 30 appels par seconde par IP, sinon HTTP 429 ; non vérifié par moi. J'ai en revanche observé des
  coupures de connexion (`RemoteProtocolError`) sur des appels successifs rapprochés : le script réessaie avec pause.
- Licence : jeu « PVGIS 5.3 geospatial » catalogué CC BY 4.0 au JRC ; la réutilisation est autorisée avec mention de la source. **Je n'ai pas
  trouvé de mention de licence propre aux réponses de l'API** : non vérifié (mention de la source dans tous les cas).
- Pièges (testés) : horodatage `AAAAMMJJ:HHmm` en **UTC**, avec la minute à `:10` pour SARAH3 et `:30` pour ERA5 (valeurs de moyennes horaires,
  champ `timestamp: hourly averages`) ; `P` en **W** pour 1 kWc (donc la moyenne de P/1000 est le facteur de charge) ; `optimalangles=1` change l'angle
  (36° SARAH3 vs 39° ERA5 à Fouju) : j'ai figé 35°/plein sud pour comparer ; années bissextiles : le fichier renvoie 8 760 lignes en 2023 (non bissextile) ;
  le drapeau `Int` marque les valeurs de rayonnement reconstruites.

### 4c. renewables.ninja

- API : `https://www.renewables.ninja/api/data/wind?...`. **Testé : une requête sans jeton a renvoyé des données** (HTTP 200, 8 760 valeurs horaires
  en kW pour 1 kW, UTC), alors que la documentation lue indique que les utilisateurs anonymes sont limités à **5 requêtes par jour**, 50 par
  heure avec un compte gratuit (non vérifié, lu dans un résultat de recherche ; un fil de forum parle de 200 par heure, non daté). Je n'ai
  créé **aucun compte** ; je n'ai pas insisté pour ne pas épuiser un quota anonyme.
- Licence : **CC BY-NC 4.0** (<https://www.renewables.ninja/downloads>, lue) : **usage commercial interdit sans accord**. Une année maximum par
  requête. La page de téléchargements ne propose en bloc que d'anciennes versions des séries pays (PV, éolien, UE-28 ; versions v1.0/v1.1 de 2016-2017) ; les données courantes passent par l'interface « Point » ou « Country » (compte non testé).
- Verdict : **partiel** : bon pour comparer, mais la licence non commerciale et le quota empêchent d'en faire la source du pipeline. Open-Meteo (vent
  100 m) + courbe de puissance choisie par nous est l'alternative.

### Facteurs de charge obtenus (annuels, 2023 sauf indication)

| Point | PVGIS-SARAH3 (35°, 14 % de pertes) | PVGIS-ERA5 | Open-Meteo GTI 35° × 0,86 (sans effet température) | Observé régional ODRÉ (parc, 2023) |
|---|---|---|---|---|
| Fouju (Île-de-France) | **13,0 %** (1 142 kWh/kWc) | 13,0 % (1 138) | 13,6 % | Île-de-France **12,1 %** |
| Marseille | **19,0 %** (1 661 kWh/kWc) | 18,9 % (1 652) | 19,6 % | PACA **16,9 %** |

- L'ordre de grandeur attendu (« ~13-15 % en Île-de-France ») est **confirmé** par PVGIS à 13,0 % (annuel, AC, hors température dans la ligne
  Open-Meteo). Le facteur de charge observé du parc (source : ODRÉ `fc-tc-regionaux-annuels-enr`, testé) est plus bas (12,1 % et 16,9 %) : le
  parc réel mêle toitures, orientations et pertes différentes, et la définition du dénominateur (puissance installée moyenne ou fin d'année,
  AC ou DC) n'a pas été vérifiée. **Ne pas présenter le résultat PVGIS comme un facteur de charge du parc.**
- Éolien, **Fouju, 2019**, 1 MW équivalent : renewables.ninja (Vestas V80 2 MW, moyeu 100 m) **26,4 %** ; mon estimation à partir du vent 100 m
  Open-Meteo (courbe générique, entrée 3 m/s, nominal 12 m/s, coupure 25 m/s) donne 20,2 % : **un simple ordre de grandeur, la courbe est inventée par moi et
  n'est pas une turbine réelle**. L'observé régional ODRÉ pour 2019 : Île-de-France 26,5 %, Hauts-de-France 24,5 %, PACA 24,6 % ; en 2023 :
  Hauts-de-France 27,9 %. Le parc éolien d'Île-de-France est très petit : ne pas en tirer de conclusion. Pour 2023, mon proxy donne 23,3 % à
  Fouju et 20,6 % à Marseille, **non validé** contre un produit de référence.
- **Refroidissement (calcul d'accès, pas une analyse)** : à Fouju en 2023, 6 816 °C·h au-dessus de 20 °C, 1 561 au-dessus de 25 °C, 168 au-dessus
  de 30 °C, 0 h au-dessus de 35 °C, 337 h avec une température de bulbe humide (formule de Stull, valable pour 5 à 99 % d'humidité, bornée) supérieure à 20 °C ;
  à Marseille : 18 747, 6 806, 1 547 °C·h, 78 h au-dessus de 35 °C, 1 194 h de bulbe humide supérieur à 20 °C. Moyennes annuelles : 13,1 °C et 17,0 °C.
  Piège : une maille ERA5 de 25 km lisse les extrêmes urbains (îlot de chaleur) : les degrés-heures sont probablement **sous-estimés** à Paris.
  Le seuil de 20 à 35 °C est un paramètre ; ce n'est pas une température de conception sourcée.
- Vérification croisée utile : les températures et vents de PVGIS-ERA5 (`T2m`, `WS10m`) et d'Open-Meteo-ERA5 viennent de la même réanalyse
  (la première heure de `T2m` vaut 14,65 °C dans PVGIS à Fouju) ; ce n'est donc pas une validation indépendante.

---

## 5. Contours administratifs

| Source | Fichier testé | Poids | Remarques |
|---|---|---|---|
| france-geojson, régions « simplifiée » (5 %) | `regions-version-simplifiee.geojson` | **225 ko** (13 régions, dont Corse) | testé |
| france-geojson, départements « simplifiée » | `departements-version-simplifiee.geojson` | **569 ko** (96 départements) | testé |
| france-geojson, régions (25 %) | `regions.geojson` | 1,45 Mo | testé |
| france-geojson, départements (25 %) | `departements.geojson` | 3,43 Mo | testé |
| france-geojson, communes « simplifiée » | `communes-version-simplifiee.geojson` | environ **19,3 Mo** (taille annoncée par le serveur ; téléchargement interrompu, non testé en entier) | trop lourd pour un front |
| geo.api.gouv.fr, communes du 77 | `communes?codeDepartement=77&fields=nom,code,contour&format=geojson&geometry=contour` | **2,9 Mo** pour 507 communes | testé ; millésime courant du COG |
| IGN Admin Express (flux Atom) | <https://data.geopf.fr/telechargement/resource/ADMIN-EXPRESS> | non téléchargé | 110 archives (GPKG, Lambert-93 et WGS84), dernière mise à jour du flux le 2026-11-19 ; taille non vérifiée |

- france-geojson : <https://github.com/gregoiredavid/france-geojson>. Propriétés `code` et `nom`. **Licence** : le README dit « Voir conditions d'utilisation
  d'Admin Express (Licence ouverte) » ; le dépôt n'a **pas de fichier LICENSE** (l'API GitHub ne renvoie aucune licence). **Millésime : noms et codes INSEE 2018,
  tracés Admin Express COG 2018**, dernier push le 2022-12-02 : les communes fusionnées depuis 2018 sont fausses. Acceptable pour régions et départements
  (inchangés), pas pour des communes.
- Admin Express : licence ouverte Etalab 2.0 (mention lue sur la page IGN de licences, texte « licence etalab-2.0 »/« Licence Ouverte / Open
  Licence – Etalab ») : à confirmer au moment de l'usage. Simplification à faire nous-mêmes (mapshaper ou équivalent) ; non testé ici.
- Recommandation provisoire : régions + départements en `…-version-simplifiee` pour le front (moins de 1 Mo au total), communes via Admin Express
  courant si une carte communale devient nécessaire.
- Piège : coordonnées en WGS84 (EPSG:4326, longitude, latitude) pour france-geojson et geo.api ; Admin Express existe en Lambert-93 (EPSG:2154) :
  mélanger les deux sans reprojeter décale tout.

---

## 6. PUE et températures de conception pour les data centers

- Je n'ai trouvé **aucun jeu ouvert de PUE ou de températures de conception par site** en France. Recherche limitée à quelques requêtes, non exhaustive.
- Ce qui existe : la base européenne des data centers (règlement délégué (UE) 2024/1364, reporting annuel des data centers d'au moins 500 kW,
  PUE parmi les indicateurs). La page de la Commission (<https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficiency-targets-directive-and-rules/energy-efficiency-directive/energy-performance-data-centres_en>,
  lue) décrit un **tableau de bord de données agrégées**, mis à jour chaque mois, et une analyse de la période 2024 publiée en juillet 2025 ; elle ne
  mentionne **aucun jeu téléchargeable ni donnée par site**. Si les données par site sont publiques ou confidentielles : **non vérifié**.
- Ordres de grandeur du secteur, non français et non ouverts : l'Uptime Institute annonce une moyenne mondiale de PUE de 1,56 pour 2024 (via Statista, 
  non vérifié à la source) et 1,52 pour 2026 (page Uptime, résumé de recherche, non vérifié) ; cette moyenne est par répondant et non pondérée par
  capacité (1,36 pondérée selon la même source). Ce sont des enquêtes d'un acteur privé, pas des données ouvertes.
- Pour la modélisation, le PUE sera **une hypothèse affichée et modifiable**, avec une température d'air extérieur issue d'ERA5 (§4) ; les plages
  de températures admissibles des salles informatiques (ASHRAE) n'ont pas été vérifiées ici.
- Verdict : **NO** pour des données ; **hypothèse sourcée** pour le PUE.

---

## Trous et risques

1. **Pas de capacité d'accueil en soutirage par poste en open data** (testé et recherché) : c'est le trou central pour la question « où ? ». Ce qu'on peut dire
   de façon sourcée : demandes de raccordement agrégées (RTE : environ 18 GW réservés en mai 2026), répartition grossière par région, zones d'une carte 400 kV annoncée (publication non
   confirmée). Il faut le dire dans le site plutôt que le combler.
2. **Postes et lignes RTE sans coordonnées** : l'ODRÉ ne permet pas de les cartographier. Alternatives non validées : OSM (Overpass était en panne lors du test), extraits départementaux DDT.
   Décision à prendre : accepter une carte au niveau département/région, ou construire un rapprochement poste → coordonnées documenté.
3. **Caparéseau = injection, sans licence ouverte, sans export** : ne pas en tirer de chiffres sans autorisation écrite de RTE (conditions de réutilisation).
   Ne pas présenter une capacité d'injection comme une capacité de consommation : un point central pour la lectrice (une marge pour produire n'est pas une marge pour consommer).
4. **Licences non commerciales** : Open-Meteo (API gratuite non commerciale ; données CC BY 4.0) et renewables.ninja (CC BY-NC 4.0). Si le site devient commercial, il
   faut revoir. PVGIS : mention de la source ; licence de l'API non confirmée.
5. **Profondeur et fraîcheur de PVGIS** : s'arrête à 2023. Open-Meteo/ERA5 va plus loin (avec le délai de 5 jours). Un simulateur multi-années réalistes devra choisir les années (2005-2023 pour le PV
   si on veut PVGIS), et vérifier que le vent et le solaire d'une même année viennent de la même réanalyse pour garder la corrélation.
6. **Réanalyse ≠ mesure** : ERA5 a une maille de 25 km (îlot de chaleur et vent local lissés) ; les facteurs de charge calculés sont des modèles (PV : 13,0 % contre 12,1 % observé pour le
   parc régional ; éolien : proxy à 20 % contre 26 % chez ninja en 2019). Rien ne remplace un calage sur la production réelle (éCO2mix/ODRÉ) avant d'afficher un chiffre.
7. **Heures** : tout est en UTC ici. Les prix day-ahead et les données éCO2mix sont en heure locale (ou UTC selon le jeu) : fixer une convention unique dès le début et
   tester le passage à l'heure d'été (23 et 25 heures par jour) ; `shortwave_radiation` est une moyenne de l'heure précédente (Open-Meteo), PVGIS donne `:10` ou `:30` selon la base : l'alignement à
   l'heure H décale la courbe d'une demi-heure à une heure si on n'y prend pas garde.
8. **Contours** : france-geojson est au millésime 2018 et sans fichier LICENSE ; préférer Admin Express pour les communes.
9. **Non testés ou non vérifiés** : API interne de Caparéseau, export Enedis des capacités HTA (portail en migration), OSM/Overpass, publication effective de la carte RTE des zones favorables,
   quota réel de renewables.ninja, licence de l'API PVGIS, taille des archives Admin Express, conditions de réutilisation exactes du jeu data.gouv du Loiret (licence `lov2` affichée, millésime 2023).
10. **Registres et données connexes repérés mais hors périmètre de ce spike** : registre national des installations de production et de stockage (ODRÉ, au 31/12/2025,
    125 930 lignes, testé dans la liste du catalogue seulement, pas téléchargé), pour un autre spike.

## Pour reproduire

```
cd /home/max/dev/puissance-de-calcul
uv run --with httpx,pyshp python pipeline/explo/spike_reseau.py            # tout sauf renewables.ninja
uv run --with httpx,pyshp python pipeline/explo/spike_reseau.py ninja      # 1 requête anonyme (quota 5/jour annoncé)
```
