# Séries horaires nationales — un fichier par année

Un fichier `AAAA.csv` par **année civile en heure de Paris** (comme les bilans RTE) :
le fichier 2024 commence à `2023-12-31T23:00Z`. Généré par `pc build` ; ne pas
modifier à la main. Métadonnées (dates d'extraction, natures, licences) :
`../meta.json`.

| Colonne | Unité | Définition |
|---|---|---|
| `heure_utc` | ISO 8601, UTC | **début** de l'heure décrite : `2024-06-01T10:00Z` = de 10:00 à 11:00 UTC |
| `consommation` | MW moyen sur l'heure | consommation France continentale **hors Corse**, pertes comprises, pompage exclu (éCO2mix) |
| `nucleaire` | MW moyen | production nucléaire |
| `nucleaire_disponible` | MW moyen | puissance nucléaire **disponible déclarée** par EDF au titre de REMIT (somme des tranches en exploitation, Flamanville 3 comprise depuis le 18/12/2024) ; ce n'est **pas** une production. Voir la note ci-dessous |
| `eolien` | MW moyen | production éolienne (terrestre + en mer) |
| `solaire` | MW moyen | production photovoltaïque |
| `hydraulique` | MW moyen | production hydraulique (dont turbinage des STEP) |
| `gaz` | MW moyen | production des centrales au gaz |
| `solde_echanges` | MW moyen | solde des échanges physiques ; **positif = import**, négatif = export (`ech_physiques`) |
| `pompage` | MW moyen | consommation des STEP en pompage, **négative** |
| `prix` | EUR/MWh | prix day-ahead zone France ; après le 2025-10-01, moyenne simple des 4 quarts d'heure (convention RTE) |
| `taux_co2` | gCO2eq/kWh | intensité **moyenne de la production** française (émissions directes, imports exclus), moyenne des demi-heures pondérée par la production. **Pas un facteur marginal**, pas l'intensité de la consommation |

- Une puissance moyenne horaire en MW vaut l'énergie de l'heure en MWh (× 1 h) :
  pour un total annuel en TWh, sommer la colonne et diviser par 10⁶.
- Cellule vide = donnée absente, **jamais imputée** : heure répétée du passage à
  l'heure d'hiver (absente des fichiers RTE), raccord entre deux natures de
  données, heures pas encore publiées.
- Arrondis : MW à l'unité, prix à 4 décimales (moyenne exacte de 4 quarts d'heure au centime ; une heure négative s'écrit donc avec son signe, jamais `-0.0`), `taux_co2` au dixième.
- Les autres filières (charbon, fioul, bioénergies), les échanges commerciaux par
  frontière et les sous-filières sont dans `../systeme_horaire.parquet`.
- Agrégation horaire de l'éCO2mix : un point horodaté t décrit la demi-heure
  **qui se termine** à t (convention établie empiriquement, non documentée par
  RTE) ; l'heure h est la moyenne des points h:30 et h+1:00. Au pas de 15 min
  (données temps réel), même convention : points h:15, h:30, h:45, h+1:00.
- `nucleaire_disponible` : reconstruit depuis les indisponibilités REMIT d'EDF
  (opendata.edf.fr, Licence Ouverte 2.0). Pour chaque tranche, dernière version
  active des arrêts et limitations planifiés ou fortuits ; si plusieurs se
  superposent, la puissance disponible la plus faible (règle d'EDF) ; sinon la
  puissance maximale. Moyenne exacte sur l'heure. Dates de la source lues en
  heure de Paris (vérifié). Vide après l'heure d'extraction (pas de prévision).
  La production peut le dépasser de quelques centaines de MW (eau froide en
  hiver, déclarations en escalier pendant les grèves ou les essais). Méthode,
  limites et taux annuels : `../meta.json`, clé `nucleaire_disponible`.
- Les données de l'année en cours mêlent **consolidé** et **temps réel**
  (puissance instantanée, moins précise) : voir `natures` dans `../meta.json`.
