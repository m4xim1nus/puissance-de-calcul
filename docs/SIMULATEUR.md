# Simulateur — spécification v1 (révisée le 26/11/2026 : froid supplémentaire, plancher réglable)

Document vivant. Décisions dans `making-of/DECISIONS.md`.

## Ce qu'il fait

On choisit une consommation supplémentaire (un parc de data centers) et
une année observée ; le simulateur l'ajoute **heure par heure** aux
séries de cette année et montre ce qu'elle rencontre : heures tendues,
heures de surplus, prix. Il prolonge « Quand ? » : mêmes indicateurs,
mêmes définitions, mêmes limites, mais avec les hypothèses entre les
mains de la lectrice.

Il **ne** modélise **pas** : le dispatch, la formation des prix (le prix
affiché est celui observé, sans la consommation ajoutée), les échanges
et les voisins, le réseau local, le risque de défaillance au sens de
RTE. Il le dit en tête de page, pas en note : premier lien à côté du
titre, « Ce que fait le simulateur, et ce qu'il ne modélise pas », qui
ouvre la notice de l'outil sur ce texte, à un clic (révisé le 26/11 :
l'outil tient dans la fenêtre sans défilement sur ordinateur, retours de
l'auteur ; la notice est un panneau latéral avec JavaScript, du texte
dans le flux sans ; rapport :
`docs/relectures/2026-11-26-simulateur-ux-agent.md`).

## Hypothèses réglables (v1)

| Hypothèse | Défaut | Plage | Remarque |
|---|---|---|---|
| Année de référence | 2025 | 2015-2025 | séries publiées `data/export/horaire/AAAA.csv` |
| Puissance appelée X | 1 GW | 0 à 20 GW | puissance **appelée**, pas réservée ni raccordée (lien vers « Combien ? ») |
| Profil | plat | plat ; plat avec effacement | aucune courbe de charge de data center n'est publiée |
| Effacement : heures | 0 | 0 à 500 h/an | la consommation ajoutée est nulle pendant les N heures où la charge résiduelle **observée** (froid supplémentaire compris, s'il est réglé) est la plus élevée (prévision parfaite) ; l'énergie effacée est **perdue**, ni reportée dans le temps ni vers un autre site. Le résultat est circulaire pour l'indicateur des heures au-delà du maximum (ce sont les heures effacées) : il donne une **borne basse** du nombre d'heures à effacer, dite comme telle |
| Froid supplémentaire | 0 °C | 0 à 12 °C, pas de 0,5 | ajouté le 26/11/2026, voir « Froid supplémentaire » ci-dessous ; borne de la plage : choix du site (voir « Double compte » ci-dessous) |
| Nucléaire non mobilisable (plancher de J) | 1 GW | 0 à 3 GW, pas de 0,1 | ajouté le 26/11/2026, voir « Plancher réglable » ci-dessous |

Chaque hypothèse affichée avec son défaut et sa plage dans le résumé
d'un repli « Raison », qui porte sa justification (et les notes des
chiffres du référentiel qu'elle cite) ; l'URL porte l'état (partage d'un
scénario par lien : `?annee=2022&x=5&effacement=100&froid=4.5&plancher=0.5`,
valeurs par défaut omises ; une adresse antérieure aux nouveaux réglages,
sans `froid` ni `plancher`, garde leurs défauts et redonne le même
scénario). Chaque résultat montre son qualificatif (« au plus », « à peu
près ») et sa valeur, et sa seconde valeur s'il en a une (« avec la
disponibilité déclarée par EDF ») ; ses réserves et ses sources sont dans
la notice, ouverte sur lui par son lien « Détail ». Aucun réglage ne
fait bouger la mise en page (hauteurs réservées, testé aux tailles
d'écran de référence).

Les valeurs par défaut des deux réglages ajoutés le 26/11/2026 (froid nul,
plancher de 1 GW) redonnent exactement les résultats d'avant : test
`test_froid_nul_ne_change_rien` (Python), « froid nul : mêmes résultats »
(TypeScript), et aucun chiffre publié ne change (`pc check`).

## Froid supplémentaire (limite « froid extrême », niveaux « sourcer » et « réglable »)

**Ce que fait le réglage.** Pendant un **épisode** de l'année observée, la
consommation gagne à chaque heure `F × G` MW, où F est le froid réglé (°C)
et G le gradient hivernal publié par RTE (`thermosensibilite_hiver_rte`,
2 400 MW/°C, *Perspectives pour l'automne et l'hiver 2022-2023*, p. 59-60 ;
même valeur dans le Bilan électrique 2017, p. 15). Le gradient vient du
référentiel, jamais tapé dans le code.

**L'épisode** (`episode_froid`, référence Python et moteur TypeScript) :
les **168 heures consécutives** (7 jours, `DUREE_FROID_H`) de l'année
observée dont la charge résiduelle **observée** moyenne est la plus élevée
(moyenne des heures renseignées ; fenêtre sans RN écartée ; à égalité, la
plus ancienne). Raisons :

- sans série de température branchée, on ne sait pas désigner les jours
  les plus froids ; les jours les plus tendus sont ceux où un froid de plus
  pèserait le plus. Ce sont des jours de novembre à février dans toutes
  les années 2015-2025 (vérifié le 26/11/2026 ; 2025 : du 13 au 20 janvier,
  test du moteur). Les plus tendus ne sont pas forcément les plus froids
  (2019 : mi-novembre ; 2016 et 2020 : fin novembre-début décembre) ;
- une semaine couvre des jours ouvrés et un week-end ; RTE dit « longue »
  la vague de février 2012 sans en donner la durée dans les documents lus.
  La durée est un **choix du site**, fixe, non réglable (un réglage de
  plus pour un paramètre dont on n'a pas de valeur sourcée) ;
- un ajout uniforme à toutes les heures de l'épisode : pendant une vague de
  froid, selon RTE, « le profil journalier est relativement peu affecté » et
  le niveau de la demande croît (même document, p. 59). Ce n'est pas un ajout
  uniforme **en MW** pour autant : la page suivante donne le chauffage
  résidentiel lors d'une journée froide « de l'ordre de 23 GW le matin et
  30 GW le soir – voire plus – lors de froids sévères, contre respectivement
  13 et 16 GW à température normale » (p. 60), et le BE2017 un gradient
  « variable au cours de la journée ». L'ajout uniforme
  sous-estime probablement l'effet aux heures de pointe et le surestime la
  nuit : le compte des heures au-delà du maximum en est plutôt **minoré**
  (limite écrite dans la raison du réglage, relecture du 26/11/2026, f4).

**Ce que le froid touche, et ce qu'il ne touche pas** (`effet_charge`,
paramètre `supplement`) :

- il s'ajoute à la charge résiduelle **après** (RN + froid + consommation
  ajoutée) ; les **seuils restent observés** (maximum de l'année, maximum
  2015-2025) et la monotone « avant » reste la RN observée ;
- il passe **avant** la consommation ajoutée dans le nucléaire disponible
  non produit : la charge ne trouve que `max(0, J − F × G)` pendant
  l'épisode (le même nucléaire inemployé ne sert pas deux fois) ;
- l'effacement est classé sur RN + froid (les heures les plus tendues du
  scénario) ;
- l'énergie ajoutée, la part dans J et les prix restent ceux de la
  **consommation ajoutée** : l'énergie du froid n'y est pas comptée ; les
  prix restent les prix observés.

**Double compte : traité par la définition, dit, et repère en consommation
(relecture adverse du 26/11/2026, F1).** L'année observée contient déjà ses
propres froids, et l'épisode tombe sur ses jours les plus tendus, en général
parmi ses plus froids. Le réglage n'est donc **pas** un écart aux normales :
ce sont des degrés **de plus** que ce qu'ont connu ces jours, et le simulateur
ne sait pas dire de combien ces jours étaient déjà sous les normales (aucune
série de température branchée). La première version donnait en repère
février 2012 (8 °C sous les normales) et le froid « centennal » de RTE
(12 °C) : régler 8 °C pour « rejouer 2012 » portait la consommation horaire
de 2025 à 106,6 GW, alors que la phrase même de RTE d'où vient ce 8 °C
conclut qu'un tel froid donnerait, à l'hiver 2024-2025, une pointe
« sensiblement inférieure à 100 GW » (citation complétée dans
`froid_2012_ecart_normale`). Ces repères en degrés sont retirés de la raison
et de la tuile. Le repère est désormais **en consommation** : RTE estime
qu'avec des froids comparables à ceux du début des années 2010, les pointes
de l'hiver 2026-2027 resteraient « sensiblement inférieures à 100 GW (sauf cas
très exceptionnels) » (`pointe_froids_2010_hiver_2026_2027`, synthèse hiver
2026-2027, p. 14), et le site publie le froid réglable à partir duquel la
consommation horaire maximale de l'année dépasse ce niveau
(`quand_froid_100gw_AAAA`, calculé par `pc build` sur l'épisode de chaque
année : 5,5 °C en 2025). Ce froid dépend beaucoup de l'année, parce que
l'épisode n'a pas le même froid propre : de 2,0 °C (2018, vague de froid de
fin février déjà dans l'épisode) à 9,0 °C (2019, épisode de mi-novembre).
Pour atteindre la pointe de 2012 à la demi-heure (102,1 GW), il faudrait de
2,7 °C (2018) à 9,8 °C (2019). La borne de la plage (12 °C) est un **choix du
site**, plus justifiée par le froid « centennal » (même confusion : 12 °C sur
2018 donnent 124,5 GW, quand RTE annonçait 109 GW en froid centennal pour
2018-2019).

**Linéarité.** Le gradient est une moyenne nationale, « variable au cours de
la journée » (BE2017), et RTE n'en publie pas la valeur aux froids extrêmes.
Ses repères de pointe pour l'hiver 2018-2019 (85 / 100 / 109 GW aux
températures de saison, à 6,5 °C et à 12 °C sous les normales) donnent
environ 2,3 GW par degré jusqu'au froid décennal et 1,6 GW au-delà (calcul
du site, note de `froid_centennal_ecart_normale`) : au-delà de quelques
degrés, le réglage **majore** probablement l'effet du froid sur la pointe.
Le résultat « Consommation horaire maximale » le rend visible : il compare
la consommation du scénario à la pointe de 2012 **au même pas de temps**
(`pointe_conso_record_2012_horaire`, 100,6 GW en moyenne horaire, hors Corse ;
102,1 GW à la demi-heure, `pointe_conso_record_2012`), dit quand le scénario
la dépasse, et rappelle l'estimation de RTE pour un froid comparable
(relecture du 26/11/2026, f3). Ordre de grandeur (26/11/2026) : 8 °C de plus
sur l'épisode portent la consommation horaire maximale de 98 GW (2019) à
115 GW (2018), au-delà de la pointe de 2012 à la demi-heure dans 7 années
sur 11 et de sa moyenne horaire dans 9 : c'est l'effet cumulé du double
compte et de la linéarité, pas une prévision.

**Résultats ajoutés.** Phrase de scénario (froid, durée, dates de
l'épisode, MW ajoutés) ; tuile « Consommation horaire maximale » (avec du
froid seulement) ; dans les tuiles des maxima, les heures au-delà dues au
**froid seul** (simulation à X nul) : aucun effacement de la consommation
ajoutée ne les supprime, et la phrase « il faudrait effacer au moins N*
heures » n'est écrite que si le froid seul ne dépasse pas le maximum.

**Limites qui restent écrites.** Une seule semaine de froid, une seule
année observée, pas de météo européenne commune (importations), pas de
stocks d'eau ; ce n'est pas une vague de froid simulée, c'est un ordre de
grandeur sur la consommation.

## Plancher réglable (limite « plancher nucléaire », niveau « réglable »)

Le plancher retranché à J pour la borne basse de la fourchette « dans le
nucléaire disponible non produit » était fixé à 1 GW. Il devient un
réglage : **défaut 1 GW** (inchangé : ordre de grandeur choisi par le site,
pas une donnée publiée), **plage 0 à 3 GW**. À 0, la fourchette se réduit à
la borne haute. Repères affichés dans la raison du réglage : J moyen aux
heures où le prix dépasse 150 €/MWh (`quand_j_heures_cheres_AAAA`), 0,5 GW
en 2025 ; la plus haute de ces moyennes annuelles sur 2015-2025 (2,0 GW en
2020, sur deux heures seulement) reste sous le haut de la plage. Les
chiffres publiés de « Quand ? » (`quand_part_j_plancher_*`) restent
calculés à 1 GW.

## Disponibilité déclarée et arrêts pour modulation (26/11/2026)

La part « au plus » dans le nucléaire disponible non produit vaut **avec
la disponibilité déclarée par EDF**. EDF déclare indisponibles, comme des
arrêts planifiés, des arrêts et baisses « pour modulation », qui sortent de
J (making-of/ERREURS.md, « un plafond qui dépend de ce qu'EDF déclare
indisponible »). Ceux de moins de 7 jours, décidés au jour le jour (le plus
souvent : « la tranche sera redémarrée si les conditions économiques le
justifient »), sont économiques ; les plus longs, d'une semaine à plusieurs
mois et souvent annoncés des semaines ou des mois à l'avance, peuvent relever
de la gestion du combustible (relecture adverse du 26/11/2026, F2). Le pipeline
reconstruit une seconde disponibilité qui **réintègre les arrêts courts**
seulement (`pc/remit.py`, `MOTIF_MODULATION`, `DUREE_MAX_COURT_H` ; colonne
`nucleaire_disponible_reintegre` des CSV horaires, ajoutée en dernière
position) ; le moteur en tire
J_r = max(0, disponible réintégré − produit) et la sortie `reintegre`
(part avec et sans plancher, énergie, heures couvertes ; la consommation
due au froid passe d'abord, comme pour J). La charge résiduelle reste
calculée avec le disponible déclaré.

**Forme retenue : une seconde valeur dans la tuile**, plutôt qu'un réglage.
Un réglage aurait ajouté une ligne aux hypothèses et un paramètre à
l'adresse, pour une grandeur qui ne change qu'une tuile ; la seconde valeur
montre les deux lectures ensemble, sans choix à faire. Sous « au plus 39 à
52 % » : « disponibilité déclarée par EDF ; 43 à 55 % en réintégrant ses
arrêts courts pour modulation » (5 GW, 2025). Pour que l'outil tienne toujours sur
un écran de 1366 × 768, la tuile des prix passe avant celle du nucléaire :
elles partagent une rangée, et la seconde valeur n'allonge pas la page. Les
résultats par défaut et les anciennes adresses ne changent pas ; une année
sans arrêt pour modulation déclaré (2015-2018) affiche « même valeur ». Un
CSV sans la colonne (antérieur) donne `reintegre = null` et la seule
mention « avec la disponibilité déclarée par EDF ».

## Résultats affichés

Pour l'année et les hypothèses choisies (énergies en TWh, puissances en
GW, heures de Paris) :

1. énergie ajoutée (Σ heures × X, effacement déduit) ;
2. part de cette énergie qui tiendrait **au plus** dans le nucléaire
   disponible non produit (J), avec la disponibilité déclarée par EDF, en
   fourchette sans plancher / avec un plancher non mobilisable réglable
   (1 GW par défaut, hypothèse du site), et l'énergie nucléaire
   supplémentaire correspondante, mise en regard de la production de
   l'année et des prévisions de l'exploitant ; en seconde valeur, la même
   fourchette en réintégrant les arrêts courts qu'EDF déclare indisponibles
   pour modulation (voir ci-dessus) ;
3. heures où charge résiduelle + charge ajoutée dépasse le maximum de
   l'année **et** le maximum 2015-2025 ; nouveau maximum ;
4. part de l'énergie ajoutée consommée à prix négatif ou nul (prix
   **observé**, sans effet en retour ; pour une consommation plate,
   c'est la part des heures de l'année). Pas de prix moyen pondéré :
   comparé entre scénarios, il se lisait comme une économie ;
5. monotone de la charge résiduelle avant / après ;
6. avec un froid supplémentaire seulement : consommation horaire
   maximale du scénario, comparée à l'observée et à la pointe historique ;
7. marge : une consommation plate de X GW retire à peu près X GW de
   marge (équivalence d'adéquation), mise en regard des marges publiées
   par RTE ; avec effacement, le simulateur ne sait pas dire combien de
   marge est rendue.

Qui servirait la consommation ajoutée (nucléaire, EnR moins arrêtées,
exportations) n'est pas déterminable sans les données des voisins : le
simulateur ne le dit pas.

## Architecture

- **Référence Python** : `pipeline/pc/quand.py` (déjà là) ; on y ajoute
  une fonction `simuler(table, x_mw, heures_effacement, …, plancher_mw,
  rn_max_reference_mw, froid_c, gradient_mw_par_c, duree_froid_h)` (et
  `episode_froid`, 26/11/2026) qui généralise
  `charges_plates` à un profil horaire quelconque (vecteur de charge
  ajoutée), et les cas de test correspondants dans
  `pipeline/tests/cas_quand.json` (valeurs calculées à la main).
- **Moteur TypeScript** : `site/src/lib/simulateur/`, fonctions pures,
  sans dépendance, mêmes règles (heure valide, arrondis, égalités,
  quantiles) ; un test vitest rejoue **tous** les cas de
  `cas_quand.json` (parité) et compare, sur une année réelle, le moteur
  aux valeurs de `quand.json`.
- **Données** : le navigateur charge le CSV de l'année choisie, servi
  par le site lui-même (copié au build depuis `data/export/horaire/`),
  aucun appel externe.
- **Page** : `/simulateur`, lisible sans JS pour la partie texte
  (hypothèses et limites) ; les résultats exigent JS, et le disent.
