# Spike — sources de « marge » pour l'enquête « Quand ? »

*Rédigé le 26/11/2026 par un agent (Opus), pour la session principale. Rapport
brut : rien ici n'est publiable sans relecture. Chaque chiffre renvoie à une
source, une date et une page (numérotation **du PDF** ; pour les documents RTE
cités, elle coïncide avec la pagination imprimée, vérifié page par page). La
colonne « vérifié » distingue ce que j'ai recalculé ou téléchargé moi-même de
ce que je reprends d'un document.*

- **Script** (jetable, relançable) : `pipeline/explo/spike_quand.py`
  (`download`, `analyse`, `indicateurs` ; fonctions `remit_nucleaire()` et
  `dispo_nucleaire(annee)`). Lancement :
  `uv run --no-project --with httpx,polars python -I pipeline/explo/spike_quand.py indicateurs`.
- **Échantillons** : `data/raw/spike_quand/` (≈ 180 Mo, non versionné) : PDF
  RTE/CRE et leur texte, jeux ODRÉ, historique REMIT d'EDF, disponibilité
  nucléaire horaire reconstruite 2023-2026 (`dispo_nucleaire_AAAA.parquet`).
- **Question posée** : à quelles heures le système a-t-il de la marge, à quelles
  heures n'en a-t-il pas, et que change une consommation plate de X GW ?

## Synthèse en une minute

| # | Source | Accès testé | Licence | Pas / période | Verdict |
|---|---|---|---|---|---|
| 1a | RTE, BP2025 et analyses saisonnières (marges vs critère des 3 h) | PDF, libre | — (document) | scalaires par hiver ou horizon | **GO** comme référence citée ; **aucune série horaire** |
| 1b | Série horaire publique de « marge » | cherchée : ODRÉ, data.rte-france.com, presse | — | — | **NO-GO** : non trouvée |
| 1c | Signal Ecowatt (ODRÉ) | libre, CSV | LO 2.0 | horaire, 01/09/2022 → J-1 | **GO**, mais **aucune heure orange ni rouge** sur la période (vérifié) : inutile comme indicateur de tension récente |
| 2a | **Indisponibilités nucléaires EDF (REMIT), historique depuis 2015** (opendata.edf.fr, data-fair) | libre, CSV 112 Mo | LO 2.0 | événements datés → horaire reconstruit, 2015 → 07/09/2026 (+ liste courante, horaire) | **GO** : taux de disponibilité reconstruit à 0,0-0,3 pt de RTE sur 2018-2025 (1,3 pt au pire, 2017) |
| 2b | API RTE « Unavailability Additional Information », « Actual Generation » par groupe | **compte requis** (HTTP 400 sans jeton) | conditions du portail, non lues | horaire, par groupe | non testé (pas de compte créé) |
| 2c | ENTSO-E (A80, A73, A61…) | jeton en attente | — | — | non testé |
| 3a | Prix négatifs | déjà dans `data/export/` | — | horaire | **GO** (spike système) |
| 3b | Modulation nucléaire | proxy « disponible déclaré − produit » (2a + éCO2mix) ; chiffres annuels RTE/EDF | — | horaire (proxy), annuel (officiel) | **partiel** : proxy calculable, ne recoupe pas exactement les chiffres EDF |
| 3c | Écrêtement / modulation EnR | chiffres annuels RTE seulement | — | annuel | **NO-GO** en série (confirmé) |
| 3d | Capacités d'échange aux frontières | JAO (Core, positions nettes maximales) sans jeton ; ODRÉ « monitoring 70 % » arrêté en 2022 ; ENTSO-E avec jeton | JAO : non lue ; ODRÉ : LO 2.0 | horaire | **partiel** (Core seulement, licence non lue) |
| 3e | Extremas quotidiens des flux commerciaux (ODRÉ) | libre | LO 2.0 | journalier, 2012 → 10/2026 | **GO** (signe inverse d'éCO2mix, voir pièges) |
| 4a | Effacements sur le mécanisme d'ajustement (ODRÉ) | libre | LO 2.0 | journalier 2013-2025 ; annuel 2004-2025 | **GO** (faible volume, voir § 4) |
| 4b | Mécanisme de capacité | registre des transactions (ODRÉ) ; rapports de paramétrage RTE/CRE (PDF) | LO 2.0 / documents | annuel | **partiel** : les paramètres (marge, Cref, heures PP) sont publics ; le rapport d'enchère 2026-2027 n'a pas été trouvé |
| 4c | Calendrier Tempo | endpoint éCO2mix : fichier vide ; référence = site client RTE / API (compte) | — | journalier | **NO-GO** sans compte |
| 5 | Ce que RTE dit d'une consommation supplémentaire à la pointe | BP2025 (4 chapitres), rapport de paramétrage du mécanisme de capacité | — | — | **GO**, mais **RTE n'isole nulle part l'effet des data centers sur la pointe** |

**Le résultat principal du spike** : la disponibilité nucléaire déclarée au
titre de REMIT est accessible sans jeton (EDF, data-fair), reconstructible au pas
horaire, et elle recoupe les taux publiés par RTE. Elle permet de construire une
charge résiduelle **nette du nucléaire disponible** (et non du nucléaire
produit), ce qui évite le piège principal (§ 6). En revanche, **aucune série
horaire publique ne donne une « marge »** : la marge de RTE est un résultat de
simulation probabiliste, publié en quelques scalaires par hiver.

---

## 1. Marge de sécurité d'approvisionnement

### 1.1 Ce que RTE publie (documents lus)

| Chiffre | Source (date) | Page | Vérifié |
|---|---|---|---|
| Critère : « espérance annuelle de 3 heures de défaillance et de 2 heures de délestage » (art. D. 141-12-6 code de l'énergie ; délibération CRE n° 2022-152 du 25/05/2022) | BP2025, chap. *Fonctionnement du système électrique* (URL datée 15/07/2026, PDF créé le 30/06/2026) | p. 2 | lu |
| Marges hiver 2026-2027 : « entre 8 et 10 GW par rapport au critère public de sécurité d'approvisionnement » | idem ; aussi BP2025 *Principaux résultats* (16/12/2025), p. 15 | p. 13 | lu |
| Marges retenues pour dimensionner le mécanisme de capacité 2026/2027 : **8,0 GW** (décarbonation rapide), **9,5 GW** (lente) ; Cref = 80,5 / 79,0 GW ; parc certifié projeté 88,5 GW (nucléaire 48,5 ; thermique 13,0 ; hydraulique hors fil de l'eau 12,3 ; EnR variables 9,5 ; flexibilités 5,2) | RTE, *Mécanisme de capacité — rapport de paramétrage PL 2026/2027* (daté 21/01/2026, URL 2026-02-12) | p. 10-12, tableaux 5 et 7 | lu |
| Hiver 2026-2027 : risque « significativement en dessous du critère […] dans toutes les configurations étudiées » ; disponibilité nucléaire moyenne prévue **48,5 GW** de novembre à mars (50,5 GW en 2025-2026) ; « autour de 54 GW » en janvier 2027 ; disponibilité affichée « lissée sur 7 jours » | RTE, *Perspectives pour le système électrique pour l'hiver 2026-2027* (18/11/2026) | p. 8, 15 | lu |
| Même document : parc thermique « 7,7 GW de cycles combinés et de turbines à combustion au gaz, 1,8 GW de centrales à charbon, 1,6 GW de turbines à combustion au fioul et près de 5 GW de centrales à cogénération » ; charbon disponible retenu ≈ 1,2 GW | idem | p. 12 | lu |
| Même document : stock hydraulique « inférieur à 50 % » début novembre (≈ 70 % en moyenne décennale) ; les barrages « devraient toutefois être en mesure de produire à forte puissance lors des pointes » | idem | p. 10 | lu |
| Même document : indisponibilités climatiques nucléaires « culminé à 13,4 GW (soit 21 % du parc installé) pendant quelques heures le 17 août » 2026 | idem | p. 7 | lu |
| Risque à l'échelle de la journée : « près de 50 % du volume de défaillance resterait concentré autour des pointes de consommation du matin et du soir, sur les plages 7 h-10 h et 17 h-20 h » ; « le risque sur les plages méridiennes apparaît dès aujourd'hui très faible » ; heures PP du mécanisme de capacité 2026/2027 : [7h-10h[ et [17h-20h[ (note 38) | BP2025, *Fonctionnement* | p. 30 | lu |

**Ce que ces chiffres sont, et ne sont pas.** Une marge de 8 à 10 GW « par
rapport au critère » est la capacité qu'on pourrait retirer (ou la consommation
qu'on pourrait ajouter, en première approximation) avant que l'espérance de
défaillance n'atteigne 3 h/an, dans le modèle probabiliste de RTE (centaines de
scénarios météo × aléas de disponibilité, Europe interconnectée). Ce n'est
**pas** un écart observable entre une capacité installée et une pointe : on ne
peut pas le recalculer avec nos données, et aucun indicateur déterministe tiré
d'éCO2mix ne doit être présenté comme « la marge ».

### 1.2 Série horaire publique de marge : non trouvée

- **ODRÉ** : recherche plein texte (« marge », « capacité », « ecowatt »,
  « indisponib », « pointe », « ajustement ») sur le catalogue (185 jeux) :
  aucune série de marge prévisionnelle ou réalisée. Les seuls jeux liés sont
  Ecowatt, les effacements, les volumes d'ajustement et les extremas
  d'échanges (§ 3 et 4).
- **data.rte-france.com** : le catalogue (rendu en JavaScript) liste
  notamment Ecowatt v5, Tempo, *Unavailability Additional Information* (v7.1,
  modifiée le 13/10/2026), *Generation Forecast* v3.1, *Generation Installed
  Capacities* v1.2, *Actual Generation* (par filière et par groupe). Je n'ai pas
  vu d'API « marge ». Toutes demandent un compte (OAuth) : HTTP 400 sans jeton
  (testé le 26/11/2026). Je n'ai pas créé de compte.
- **Portail services RTE** : la synthèse hiver cite un « Stock hydraulique —
  RTE Portail Services » (note 6, p. 10), hebdomadaire. Non testé.
- **Doute** : je n'exclus pas qu'une publication de marges prévisionnelles à
  court terme existe sur le portail services RTE (connecté) ; je ne l'ai pas
  trouvée en accès libre.

### 1.3 Ecowatt (ODRÉ) — GO mais muet

- `nouveau_signal_ecowatt` : 24 valeurs horaires par jour, du 01/09/2022 au
  25/11/2026 (1 544 jours), LO 2.0, rafraîchi chaque jour. Valeurs : 0 (vert +
  production décarbonée, depuis le 03/11/2023), 1 (vert), 2 (orange), 3 (rouge).
- **Vérifié** : sur 37 056 heures, seulement des 0 (19 115) et des 1 (17 941) ;
  `couleur_du_jour` vaut 1 les 1 544 jours. **Aucune heure orange ni rouge
  depuis septembre 2022.**
- L'ancien jeu régional (`signal-ecowatt`, 16/11/2020 → 30/08/2022, 4 plages
  par jour et par région) contient 65 plages-régions à 2 et 36 à 3, et 2 394
  à 0, valeur que sa fiche ne documente pas (elle annonce des valeurs de 1 à
  4). Signaux régionaux, non comparables au signal national actuel ; dates des
  plages 2 et 3 non extraites.
- Usage possible : dire « RTE n'a émis aucun signal de tension depuis
  septembre 2022 ». Inutile pour classer les heures.

---

## 2. Disponibilité du parc

### 2.1 Indisponibilités REMIT d'EDF (data-fair) — GO

**URL.**
- historique : `https://opendata.edf.fr/data-fair/api/v1/datasets/historique-des-indisponibilites-des-moyens-de-production-de-edf-sa-depuis-2015/raw`
  (fichier « … depuis 2015 - 07092026.csv », 111,6 Mo, 413 289 lignes, mis à jour le 07/09/2026) ;
- liste courante (indisponibilités non terminées depuis plus de 3 mois, mise à
  jour **toutes les heures**) : `…/indisponibilites-des-moyens-de-production-edf-sa/raw`
  (8,6 Mo, 29 717 lignes).
- Source amont déclarée : `https://doaat.edf.fr/doaat/export/full/csv` (plateforme
  de transparence EDF). La note explicative EDF (doaat.edf.fr) renvoie
  **HTTP 403** à un client automatisé : non lue.
- **Attention** : l'ancienne API Opendatasoft d'opendata.edf.fr renvoie
  **HTTP 410** ; la fiche data.gouv.fr pointe vers la nouvelle API data-fair.

**Licence.** Licence Ouverte 2.0 (métadonnées data-fair et data.gouv.fr).

**Contenu.** Une ligne par **version** d'événement : statut (Active, Inactive =
version remplacée, Annulée, Supprimée), identifiant, version, centrale
(tranche), filière, début, fin, type, cause, information complémentaire,
puissance maximale (MW), puissance disponible (MW), date de publication.
Filières : nucléaire (273 k lignes), STEP, réservoirs, fil de l'eau, charbon,
gaz, fioul/TAC, éolien en mer, énergie marine. **EDF SA seulement** : complet
pour le nucléaire, partiel pour l'hydraulique et le thermique (CNR, SHEM,
TotalEnergies, Engie, GazelEnergie… absents).

Types de publication nucléaire (vérifié) : `Planifiée` et `Fortuite` (vraies
indisponibilités, avec puissance disponible) ; `Chronique`, `Chronique.`,
`Chronique PMIN`, `Chronique aFRR` (depuis 2021-2025 : chroniques de **puissance
minimale** et de réserve aFRR par tranche, dans le texte libre, puissances à 0).
Les chroniques PMIN permettraient d'estimer le **plancher technique** du parc
en marche (utile pour les heures de surplus). Non exploitées.

**Reconstruction horaire** (`dispo_nucleaire`) : dernière version active de
chaque événement Planifié/Fortuit ; pour chaque tranche et chaque heure, minimum
des puissances disponibles des événements couvrant le milieu de l'heure (règle
EDF de superposition : « retenir la puissance disponible minimale », description
du jeu), sinon puissance maximale de la tranche. Dates supposées en heure de
Paris (non documenté). Fessenheim exclue (aucun événement après sa fermeture :
elle compterait à pleine puissance). Σ des puissances maximales hors Flamanville 3
et Fessenheim : **61 370 MW**, identique au registre ODRÉ au 31/12/2024
(61,37 GW, spike système § 3).

**Recoupement (vérifié)** : taux annuel de disponibilité = Σ disponible /
Σ puissance maximale, hors Flamanville 3, comparé au BE2025 (fig. 2.5, p. 25,
« sur la base des indisponibilités déclarées au titre de REMIT », hors EPR) :

| Année | Reconstruit | RTE (BE2025) | Écart (pt) |
|---|---|---|---|
| 2015 | 79,67 % | 79,5 % | +0,17 |
| 2016 | 72,85 % | 72,2 % | +0,65 |
| 2017 | 72,39 % | 71,1 % | +1,29 |
| 2018 | 74,05 % | 74,0 % | +0,05 |
| 2019 | 71,61 % | 71,6 % | +0,01 |
| 2020 | 65,70 % | 65,2 % | +0,50 |
| 2021 | 70,03 % | 69,8 % | +0,23 |
| 2022 | 54,35 % | 54,2 % | +0,15 |
| 2023 | 62,97 % | 62,9 % | +0,07 |
| 2024 | 71,76 % | 71,5 % | +0,26 |
| 2025 | 74,31 % | 74,0 % | +0,31 |

Biais systématiquement positif (≤ 0,3 pt depuis 2018). Pistes non vérifiées :
échantillonnage au milieu de l'heure, Fessenheim exclue de mon dénominateur
avant 2020 alors que RTE l'inclut (2015-2020), traitement des versions.

Autres contrôles (vérifiés) :
- disponibilité moyenne novembre 2025 → mars 2026, Flamanville 3 inclus :
  **50,68 GW**, contre « 50,5 GW en 2025-2026 sur la même période » (RTE, hiver
  2026-2027, p. 8). Maximum horaire 56,7 GW, contre « 55,5 GW atteints en
  janvier 2026 » (RTE, valeur lissée sur 7 jours : non comparable strictement) ;
- production éCO2mix ≤ disponible reconstruit : en 2024, une seule heure en
  dépassement (−11 MW). En 2025, 185 heures en dépassement (jusqu'à −1 052 MW)
  si Flamanville 3 est compté, ce qui signale un traitement incertain de l'EPR
  pendant sa montée en puissance (premiers événements REMIT de F3 :
  18/12/2024). **À résoudre avant usage sur 2025.**

**Pièges.**
1. Le fichier est en **latin-1**, séparateur « ; », virgule décimale, dates
   « jj/mm/aaaa hh:mm » (historique) mais « aaaa-mm-jj hh:mm:ss » entre
   guillemets (liste courante) : deux formats.
2. L'historique s'arrête au 07/09/2026 ; la suite est dans la liste courante
   (qui ne garde que les événements non terminés depuis plus de 3 mois).
3. Unités sans événement (Fessenheim après fermeture, Flamanville 3 avant
   décembre 2024) comptent à pleine puissance si on ne les filtre pas.
4. « Disponible » REMIT ≠ disponible pour l'énergie : RTE précise que l'écart
   entre disponibilité et production vient « notamment [de] la réservation
   d'une partie de la puissance disponible pour les services système, [de]
   modulations de puissance pour des raisons économiques ou encore [de] baisses
   de production faisant suite aux mouvements sociaux » (hiver 2026-2027, p. 8,
   note 5).
5. EDF classe certains arrêts (économie de combustible) et certaines limitations
   (température de l'eau) en **modulation** dans ses bilans, alors qu'ils
   peuvent être déclarés indisponibilités dans REMIT (BE2025, fig. 2.5, note *).
   La frontière modulation / indisponibilité n'est pas observable de l'extérieur.

### 2.2 Sans ENTSO-E, le reste du parc

- **Hydraulique et thermique EDF** : même fichier REMIT (partiel, EDF seul).
- **Autres producteurs** : leurs publications REMIT sont ailleurs (plateformes
  propres, EEX Transparency). Non testé. ENTSO-E (A80) les agrège : à faire
  quand le jeton arrive.
- **Capacités installées** : registre ODRÉ (spike système § 3) et chiffres RTE
  ci-dessus.

---

## 3. Surplus

### 3.1 Ce que RTE et EDF publient (lu)

| Chiffre | Source | Page |
|---|---|---|
| Modulation nucléaire : « de 16 TWh en 2023, à 31 TWh en 2024 puis 33 TWh en 2025 » (donnée provisoire, « source EDF 2026_02_16_ETUDE_MODULATION.pdf »), « pour un volume total de production non utilisée intégrant d'autres causes relativement stable, de 41 TWh en 2023 et 38 TWh en 2024 » | BP2025, *Fonctionnement* | p. 6, note 4 |
| « La modulation (toutes typologies confondues) a représenté de l'ordre d'une trentaine de TWh en 2025 » ; profil : « plutôt lors des après-midis, particulièrement le week-end, entre les mois d'avril et d'octobre » | RTE, BE2025 | p. 31-32 |
| Modulation pour manque de débouchés à court terme : « entre 20 et 30 TWh par an en moyenne […] voire jusqu'à 40 TWh » certaines années ; amplitude journalière de modulation « 5 à 6 GW à l'horizon 2026-2027, contre 5 GW en 2024 et 2 GW en 2021-2022 » | BP2025, *Fonctionnement* | p. 15 |
| EnR : « environ 3 TWh de production solaire et éolienne » non produits lors des prix négatifs en 2025 (1,3 TWh éolien terrestre, 1,6 TWh solaire, estimation RTE), « près du double » de 2024 ; capacités susceptibles de s'arrêter à prix négatif : +3,3 GW entre 2024 et 2025 | RTE, BE2025 | p. 42, note 19 |
| Écrêtement à la demande de RTE : « 0,1 TWh de production solaire et éolienne » en 2025 | RTE, BE2025 | p. 43 |
| Depuis fin décembre 2025, les installations sous obligation d'achat > 10 MW sont incitées à s'arrêter à la demande de l'acheteur obligé (loi de finances 2025, art. 175 II ; arrêté du 22/12/2025) | RTE, BE2025 | p. 43, notes 22-23 |
| Solde exportateur 2026-2027 attendu « 80 à 100 TWh » ; débouchés européens limités aux heures solaires | BP2025, *Fonctionnement* | p. 13 |
| « 15 % des épisodes de prix négatifs ont […] coïncidé avec des situations d'import » (2023 et 1er semestre 2024, d'après la CRE) | BP2025, *Fonctionnement* | p. 5 |
| Test « stagnation » de la consommation 2026-2030 : « hausse relative de près de 20 % de la modulation de la production bas-carbone » | BP2025, *Fonctionnement* | p. 47 |

**Incohérence à signaler** : les 16 / 31 / 33 TWh du BP2025 sont présentés comme
la modulation « assimilable à des absences de débouchés économiques » dans la
phrase, mais le BE2025 donne « une trentaine de TWh » pour la modulation
« toutes typologies confondues » en 2025. Je ne sais pas lequel des deux
périmètres correspond aux 33 TWh. Ne pas citer l'un pour l'autre.

### 3.2 Proxy horaire calculé (vérifié, exploratoire)

« Jeu nucléaire » J(h) = disponible REMIT reconstruit − production éCO2mix
(borné à 0) :

| Année | Σ J (TWh) | Ce qu'on compare |
|---|---|---|
| 2023 | 18,3 (hors F3) | EDF/RTE : 16 TWh de modulation |
| 2024 | 25,1 (hors F3) | EDF/RTE : 31 TWh ; production non utilisée 38 TWh |
| 2025 | 26,5 (hors F3) à 29,1 (F3 inclus) | EDF/RTE : 33 TWh (provisoire) ; BE2025 : « une trentaine » |

Le proxy est du même ordre de grandeur, **pas identique**, et l'écart change de
signe entre 2023 et 2024. Causes plausibles, non vérifiées : arrêts classés
modulation par EDF mais déclarés indisponibles dans REMIT (pièges 2.1-5) ;
réserves de services système ; traitement de F3. **On ne doit pas l'appeler
« modulation »** ; on peut l'appeler « nucléaire déclaré disponible et non
produit », en montrant les chiffres EDF à côté, séparément.

Profil mensuel (vérifié, 2025, hors F3 pour la disponibilité) : J ≈ 0,5 à
1,8 TWh/mois de janvier à mars et en novembre, 2,1 TWh en octobre, 2,6 à
4,1 TWh/mois d'avril à septembre ; décembre ressort **négatif** (−0,2 TWh),
artefact du traitement de Flamanville 3 (production comptée, disponibilité
exclue). Le profil saisonnier est celui que décrit RTE (BE2025, p. 32).

### 3.3 Écrêtement : NO-GO en série (confirmé)

Aucune série horaire ouverte (spike système § 6c, recherche refaite sur ODRÉ).
Pistes de proxy : jeu ODRÉ `courbes-de-production-mensuelles-eolien-solaire-complement-de-remuneration`
(production horaire des installations sous complément de rémunération, France,
depuis 2020, pas de 15 min depuis mai 2026, LO 2.0 ; métadonnées lues, données
non téléchargées) comparé à une production attendue. Approximatif.

### 3.4 Exportations et capacités d'échange

- **Flux** : éCO2mix donne les échanges commerciaux par frontière (DE et BE
  regroupés) et le solde physique (déjà dans `systeme_horaire.parquet`).
  Maximum horaire d'export en 2025 (vérifié) : 20,8 GW (Σ des échanges
  commerciaux) ; ODRÉ `extremas-quotidiens-flux-commerciaux` : 20 984 MW.
- **Capacités** :
  - JAO, *publication tool* Core : `https://publicationtool.jao.eu/core/api/data/maxNetPos`
    répond **sans jeton** (HTTP 200, testé sur le 01/06/2025) : positions
    nettes minimales et maximales par zone et par heure (`minFR`, `maxFR`). Ce sont les
    sommets du domaine flow-based **Core** (BE, DE pour la France), pas une
    capacité d'export totale (ES, IT, CH, GB hors Core). Licence et conditions
    non lues. Interprétation à faire par quelqu'un qui maîtrise le flow-based.
  - ODRÉ `monitoring-capacites-echanges-*` (CWE, CORE, SWE, Italie Nord) :
    arrêtés en 2022-2023. Inutilisables pour la période récente.
  - CRE, *Rapport de mise en œuvre de la cible des 70 %* (juillet 2026) :
    trouvé par recherche, non lu.
  - ENTSO-E (A61, A31…) : jeton.

---

## 4. Effacements et flexibilité

| Jeu / document | Contenu | Vérifié |
|---|---|---|
| ODRÉ `effacements-quotidiens-ma` (2013 → **31/12/2025**, malgré le titre « 2013 à 2024 ») | capacité d'effacement offerte sur le mécanisme d'ajustement (minimum, moyenne, maximum) et puissance maximale activée, par jour (MW) | 2025 : offre moyenne 590 MW, activation maximale 695 MW, 49 jours avec activation |
| ODRÉ `volumes-actives-ma` (2004 → 2025, annuel) | volumes d'ajustement à la hausse et à la baisse par filière (MWh), coûts moyens, **nombre de « situations tendues » en demi-journées** (hausse / baisse) | effacements activés à la hausse : 5 238 MWh en 2025 (5,2 GWh). Situations tendues à la hausse : 45 (2024), 68 (2025) ; à la baisse : 114 (2024), 137 (2025). **Définition de « situation tendue » absente des métadonnées** : à trouver avant tout usage |
| Mécanisme de capacité 2026-2027 : « 4,4 GW de capacités d'effacement de consommation ont été contractualisées » lors de l'enchère du 6 juillet 2026 | RTE, hiver 2026-2027, p. 13 | lu |
| Nouveau mécanisme centralisé, institué par la loi de finances pour 2025 ; première période de livraison 01/11/2026 → 31/03/2027 | RTE, hiver 2026-2027, p. 12 ; BP2025 *Principaux résultats*, p. 34 | lu |
| Prix de l'enchère du 6/07/2026 : 28 182,99 €/MW | **EDF** (site commercial), pas RTE | **non vérifié** à la source primaire ; rapport RTE (`rapport-enchere-public-pl-26-27.pdf`, cité en note 9 p. 12 de la synthèse hiver) non trouvé |
| ODRÉ `registre-garanties-capacite` | transactions de garanties de capacité (ancien mécanisme décentralisé), prix et volumes | téléchargé (2 900 lignes), non analysé |
| Tempo | endpoint `eco2mix.rte-france.com/curves/downloadCalendrierTempo` : renvoie un fichier vide (en-tête seul), quel que soit le paramètre ; l'en-tête dit que la seule référence est le site client RTE | NO-GO sans compte |

Ne pas additionner les 4,4 GW (capacité certifiée contractualisée pour l'hiver)
et les ≈ 0,6 GW (offre quotidienne sur le mécanisme d'ajustement) : ce sont deux
grandeurs et deux mécanismes différents.

---

## 5. Ce que RTE dit déjà d'une consommation supplémentaire

**RTE n'isole nulle part la contribution des data centers à la pointe
hivernale.** Les data centers sont dans les trajectoires de consommation
(énergie), avec un « facteur de charge normatif » de 20 % en 2030 (BP2025,
*Consommation*, p. 14 ; *Principaux résultats*, p. 25), qui intègre la montée en
charge et ne dit rien de la puissance appelée à la pointe. Ailleurs, pour un
calcul « théorique », RTE retient 90 % pour « l'hydrogène et les centres de
données » (*Principaux résultats*, p. 21 ; *Consommation*, p. 6). Ces deux
pourcentages ne sont pas comparables (l'un est une hypothèse de trajectoire à
2030, l'autre une borne théorique) ; ne pas les mettre dans la même phrase sans
le dire.

Citations utiles (lues) :

1. « la hausse brute de la pointe de consommation induite impliquerait un
   besoin de capacité supplémentaire d'environ 8 GW, toutes choses égales par
   ailleurs, pour accompagner l'électrification et la réindustrialisation dans
   les scénarios de décarbonation rapide » ; avec les flexibilités de la
   demande, « la hausse du besoin capacitaire du système liée à l'évolution de
   la consommation est limitée à environ 5 GW entre 2026 et 2030 » (BP2025,
   *Fonctionnement*, p. 25).
2. Bilan « décarbonation rapide – R3 » : « ~ −10 GW de marges entre 2026 et
   2030 » (fig. 5.15) ; besoin de capacités additionnelles « de l'ordre de 2 à
   4 GW en 2030 » (*idem*, p. 26). Décarbonation lente : besoin « nul à
   l'horizon 2030-2035 » sous réserve d'EnR au rythme R3 et d'un socle thermique
   « proche de 13 GW » (p. 28).
3. Disponibilité nucléaire hivernale médiane 2030 : « environ 51,5 GW »,
   variantes 46 et 55 GW ; à 46 GW, « le besoin de capacités additionnelles
   augmente de 5 à 6 GW » (p. 25 et 27).
4. Profil : les retards d'électrification portent « surtout sur les secteurs
   non thermosensibles (industrie, centres de données, électrolyse) » ; « plus
   le rythme d'électrification sera lent et plus la consommation résiduelle
   atteindra des niveaux bas en milieu de journée » (p. 42).
5. Les épisodes de défaillance futurs seraient « plus longs et plus profonds »,
   « le système est parfois contraint en énergie pour passer les pointes et non
   seulement en puissance » ; profondeur horaire moyenne « entre 3 GW » (lente)
   « et 4 GW » (rapide) (p. 30).
6. « les datacenters déjà raccordés n'utilisant par exemple à date que 20 % de
   leur puissance contractuelle de raccordement » (*Principaux résultats*,
   p. 23 ; *Résumé exécutif*, p. 23).
7. Hiver 2026-2027 : « RTE n'anticipe pas de forte hausse de consommation en
   lien avec les usages émergents (datacenters, électrolyseurs) durant l'hiver
   2026-2027 » (synthèse hiver, p. 7).

**Ce qu'on peut en tirer, en le disant comme une inférence du site et non de
RTE** : une consommation plate de X GW, présente aux heures de pointe, réduit
la marge d'environ X GW au premier ordre. Avec 8 à 10 GW de marge pour
2026-2027, quelques GW passent ; 10 GW réellement appelés à la pointe
consommeraient l'essentiel de la marge de cet hiver-là. C'est un ordre de
grandeur : le passage exact de X GW de consommation à X GW de besoin dépend de
la corrélation avec le froid et avec les voisins, et seul le modèle de RTE le
calcule. À vérifier par la relecture : RTE écrit-il quelque part l'équivalence
« 1 GW de consommation à la pointe ≈ 1 GW de besoin » ? Je ne l'ai pas trouvée.

---

## 6. Méthode : quels indicateurs devant une experte ?

### 6.1 Pièges d'une « monotone de charge nette »

1. **Nucléaire produit ≠ nucléaire disponible.** Retrancher la production
   nucléaire mélange cause et effet : le nucléaire module *parce que* la charge
   nette est basse. Les heures de surplus semblent alors « équilibrées ». Il
   faut retrancher le **disponible déclaré** (REMIT), et montrer à part le jeu
   « disponible − produit ».
2. **EnR observées = EnR après écrêtement.** En heure de prix négatif, la
   production observée est déjà réduite (≈ 3 TWh en 2025, 12 GW écrêtés au
   maximum en 2024 d'après la synthèse BE2024, spike système § 6c). La charge
   résiduelle y est surestimée.
3. **Hydraulique de lac et STEP : contraintes d'énergie.** Leur puissance
   installée n'est pas disponible à toute heure ; en 2026 le stock est bas
   (§ 1.1). Les compter comme marge à pleine puissance surestime la marge sur
   des épisodes longs, exactement le type d'épisode que RTE anticipe (§ 5,
   citation 5). Le pompage (négatif dans éCO2mix, exclu de `consommation`) est
   une demande flexible aux heures de surplus.
4. **Échanges.** La consommation éCO2mix exclut les exports. Aux heures de
   surplus, la vraie « demande » inclut les exports ; aux heures tendues, les
   imports ne sont pas une marge ferme (vagues de froid communes à l'Europe). Le
   BE2025 note que les exports baissent au moment de la pointe française de
   19 h en hiver (p. 91). Signe : éCO2mix `ech_physiques` positif = import,
   ODRÉ `extremas` positif = export (vérifié : corrélation −0,99 entre le
   minimum journalier d'éCO2mix et le maximum journalier d'ODRÉ).
5. **Services système.** Une partie du nucléaire disponible est réservée aux
   réserves (RTE, note 5 p. 8 de la synthèse hiver). Le jeu nucléaire n'est pas
   entièrement mobilisable.
6. **Économie de combustible.** Une modulation pour économiser le combustible
   déplace de l'énergie dans le temps ; ce n'est pas de l'énergie perdue. Le jeu
   nucléaire est une **borne haute** de l'énergie « gratuite ».
7. **Météo.** 2015-2025 ne contient aucune vague de froid de type 2012
   (102 GW) ; la pointe 2025 a été de 88 GW (BE2025, p. 10). Une monotone
   observée n'est pas une distribution de risque. RTE simule ; nous observons.
8. **Moyenne horaire vs demi-heure, périmètre.** Pointe 2025 éCO2mix au pas
   horaire (hors Corse) : 87,4 GW le 14/01/2025, 08 h-09 h heure de Paris
   (vérifié) ; RTE : 88 GW « le 14 janvier à 9 h », consommation brute (Corse
   comprise). Cohérent, mais pas le même chiffre.

### 6.2 Indicateurs proposés

**I1 — Charge résiduelle nette du nucléaire disponible** (descriptif, *défendable*)
`RN(h) = consommation − éolien − solaire − nucléaire disponible REMIT` : ce qui
doit venir de l'hydraulique, du thermique, des imports, des effacements, des
bioénergies et du stockage. Monotone annuelle, heatmap jour × heure.
- Ce qu'il montre (calcul exploratoire, vérifié) : les 100 heures de RN la plus
  élevée tombent en janvier-février (et décembre), aux plages 7 h-11 h et
  17 h-21 h (heure de Paris), comme les plages PP de RTE. RN maximal : 37,5 GW
  (2023), 29,6 GW (2024), 31,4 GW (2025, le 14/01 à 08 h-09 h). Sur ces 100
  heures en 2025 : hydraulique de lac 5,6 GW, STEP 2,6 GW, gaz 7,6 GW, TAC +
  fioul 0,7 GW en moyenne, et un **solde exportateur** moyen de 3,2 GW.
- Limites : ne donne pas une marge en GW (la capacité disponible de
  l'hydraulique, du thermique et des imports n'est pas observée heure par
  heure) ; dépend de la météo des années observées.
- Défendable devant l'experte **comme carte des heures tendues**, pas comme marge.

**I2 — Jeu bas-carbone non utilisé** (surplus, *défendable comme borne haute*)
`J(h) = nucléaire disponible − nucléaire produit`, montré avec les heures à prix
≤ 0 et les chiffres annuels RTE d'écrêtement EnR (sans les additionner heure par
heure, puisque l'écrêtement n'est pas horaire).
- Test d'une charge plate de X GW (exploratoire) : part de l'énergie ajoutée
  (X × 8 760 h) qui tiendrait dans J(h) :

  | X | 2023 | 2024 | 2025 |
  |---|---|---|---|
  | 1 GW | 87 % | 92 % | 87 % |
  | 5 GW | 39 % | 47 % | 52 % |
  | 10 GW | 21 % | 28 % | 32 % |
  | 15 GW | 14 % | 19 % | 22 % |

  Les heures à prix ≤ 0 représentent 2,1 % (2023), 6,3 % (2024) et 8,4 %
  (2025) des heures.
- Limites : borne haute (pièges 5 et 6) ; ignore que la charge ajoutée serait
  d'abord servie en partie par **moins d'exports** (la France exporte 80 à
  100 TWh/an) : ce qui manque alors aux voisins relève du facteur marginal, et
  il faut ENTSO-E et un modèle européen pour en parler ; 2025 dépend du
  traitement de Flamanville 3.
- Défendable si l'on écrit « au plus » et qu'on montre les trois limites.

**I3 — Charge plate contre marge publiée** (pointe, *défendable comme ordre de grandeur*)
Comparer X aux marges RTE (8 à 10 GW pour 2026-2027 ; 8,0 et 9,5 GW dans le
paramétrage du mécanisme de capacité) et aux sensibilités du BP2025 (+8 GW de
besoin pour la hausse brute de pointe en décarbonation rapide 2026-2030). En
complément, le nombre d'heures où `RN + X` dépasse le RN maximal observé dans
l'année (exploratoire, vérifié) : pour X = 5 GW, 29 h (2023), 42 h (2024), 4 h
(2025) ; pour X = 10 GW, 109, 130 et 36 h.
- Limites : la marge RTE est probabiliste et date d'un exercice ; l'équivalence
  X GW consommés ≈ X GW de marge est une approximation du site ; le décompte
  d'heures « au-delà du maximum observé » ne dit pas que ces heures seraient en
  défaillance.
- Défendable si la phrase reste au conditionnel et cite RTE pour la marge.

**À ne pas faire** : une « marge horaire » calculée comme capacité installée (ou
certifiée) − charge résiduelle observée. Elle mélange une simulation (la
certification RTE) et une observation, ignore la contrainte d'énergie de
l'hydraulique et la disponibilité réelle des imports. L'experte la refuserait.

---

## 7. Doutes et limites, dits franchement

1. **REMIT, fuseau horaire** : j'ai supposé les dates en heure de Paris. Le test
   « production ≤ disponible » le soutient en 2024 (une heure en défaut), sans
   le prouver. La note explicative d'EDF (HTTP 403) le dirait sans doute.
2. **Flamanville 3 en 2025** : 185 heures où la production éCO2mix dépasse le
   disponible reconstruit. Non résolu.
3. **Modulation** : mon proxy (25 à 29 TWh en 2024-2025) n'est pas le chiffre
   d'EDF (31 et 33 TWh) ; le périmètre des 33 TWh est ambigu dans le BP2025
   lui-même (§ 3.1).
4. **« Situations tendues »** (ODRÉ, volumes d'ajustement) : définition non
   trouvée.
5. **Rapport d'enchère du mécanisme de capacité 2026-2027** : non trouvé ; le
   prix n'est connu que par EDF.
6. **JAO** : accès testé sur un jour ; licence non lue ; interprétation
   flow-based non faite.
7. **Équivalence consommation ↔ marge** à la pointe : inférence du spike, pas
   phrase de RTE.
8. Les calculs exploratoires des § 3.2 et 6.2 n'ont pas été relus par un autre
   agent. Ils servent à montrer la faisabilité ; ils ne doivent pas entrer dans
   `docs/` ou sur le site sans un passage dans le pipeline et `pc check`.

## 8. Recommandations pour la suite

1. Ajouter au pipeline une clé `pc download edf_remit` (historique + liste
   courante) et une vue dérivée `nucleaire_disponible` horaire, avec un contrôle
   `pc check` : taux annuel reconstruit à ± 0,5 pt des valeurs du BE2025 (fig.
   2.5) pour 2018-2025, et production ≤ disponible + tolérance.
2. Résoudre Flamanville 3 et le fuseau horaire avant de publier 2025.
3. Construire I1 et I2 ; garder I3 comme phrase sourcée, pas comme calcul
   central.
4. Quand le jeton ENTSO-E arrive : A80 (indisponibilités tous producteurs), A61
   (capacités d'échange), prix et mix des voisins (pour dire ce que deviennent
   les exports déplacés).
5. Chercher la définition des « situations tendues » et le rapport d'enchère
   2026-2027 sur le site de RTE.
