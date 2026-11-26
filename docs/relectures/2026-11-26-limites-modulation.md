# Relecture adverse « lectrice experte » : froid extrême, écrêtement, plancher, arrêts pour modulation

Relecture du 26/11/2026 (agent Opus), sur les changements non commités décrits par
`2026-11-26-limites-agent.md` et `2026-11-26-modulation-agent.md`. Aucun autre fichier modifié.

**Verdict : publiable après corrections listées.** Trois points de fond (F1 à F3), à corriger
avant publication ; les points de forme peuvent suivre, mais f1 à f4 sont recommandés dans la
même passe.

## Ce que j'ai vérifié moi-même, et qui tient

- **Citations du référentiel** relues dans les PDF (copies du scratchpad de session, empreintes
  conformes au rapport de l'agent) : RTE hiver 2024-2025 p. 18 (8 °C, 102 GW) ; RTE automne-hiver
  2022-2023 p. 59-60 (2 400 MW/°C, « profil journalier relativement peu affecté ») ; BE2017 p. 15
  du PDF (« en moyenne à environ 2 400 MW par degré », « variable au cours de la journée ») ; RTE
  hiver 2018-2019 p. 4 (85 000 / 100 000 / 109 000 MW ; 6,5 °C ; 12 °C ; « jusqu'à 2 400 MW ») ;
  CRE 10/05/2012 p. 1 (102,1 GW). Extrait ODRÉ : 102 098 MW au point 2012-02-08T18:00Z, hors
  Corse. Calcul du site 2,3 et 1,6 GW/°C : (100 − 85)/6,5 = 2,31 ; (109 − 100)/5,5 = 1,64. Exact.
- **Épisode de froid** recalculé indépendamment (polars, fenêtre glissante de 168 h sur la RN
  des CSV) : mêmes débuts que l'agent ; à 8 °C (19,2 GW), consommation horaire maximale de
  97,9 GW (2019) à 114,9 GW (2018), au-delà de 102,1 GW dans 7 années sur 11. Confirmé.
- **Écrêtement** : BE2025 p. 42 (« environ 3 TWh », note 19 : 1,3 + 1,6 TWh, éolien terrestre et
  solaire), p. 43 (0,1 TWh écrêtés à la demande de RTE), p. 70 (513 heures ; note 10 : depuis le
  pas de 15 min, une heure est négative si la moyenne de ses quarts d'heure l'est, convention
  identique à celle des CSV). 3 × 10⁶ MWh ÷ 513 h = 5 848 MW. Exact. 0,1 TWh ÷ 513 h = 195 MW :
  « au plus 0,2 GW » exact.
- **J_r** recalculé depuis `data/export/horaire/AAAA.csv` : Σ J_r 2025 = 36,96 TWh ; Σ J 29,15 ;
  écart 7,81 TWh = énergie des arrêts pour modulation (aucune heure où la production dépasse le
  disponible réintégré pendant ces arrêts) ; part 5 GW 52,2 → 58,5 % (publié 58, valeur calculée
  58,49) ; avec plancher 38,6 → 47,0 % ; 2024 : 25,12 → 35,55 TWh, 47 → 60 % ; 2022 : 13,44 →
  20,25 TWh. Tout concorde avec les chiffres publiés.
- **Règle d'identification** : 384 événements par la règle 1 (même décompte) ; aucun emploi négatif
  (« pas de / sans / hors modulation ») dans les textes ; faux négatifs examinés sur les mots
  « économi », « marché », « optimi », « prix » : essais à puissance stable (439), liens, arrêts
  pour économie de combustible, une dizaine d'arrêts « réinterrogés si les conditions économiques
  le justifient » sans le mot : conforme au rapport de l'agent, poids faible.
- **Aucune valeur publiée n'a changé** (question 6) : `chiffres.json` 231 → 326 entrées, 0 retrait,
  0 valeur modifiée (64 libellés ou notes changés) ; `quand.json` : 14 ajouts, 4 textes de
  définitions et limites modifiés, aucune valeur numérique ; `horaire/2018.csv` et `2025.csv`
  identiques à HEAD sur les 12 premières colonnes. `uv run pc check` : 29 contrôles, 0 échec.
- **« au plus »** (question 4) : `git grep` sur `docs/enquetes`, `docs/MESSAGE.md`, `site/src`,
  `pipeline/pc`, `quand.json`, `meta.json` : toutes les occurrences qui portent sur J sont
  qualifiées « avec la disponibilité déclarée par EDF » (texte, fragment, légendes, tableau, notes
  générées, tuile, annonce pour lecteur d'écran, accueil). Reste à reprendre : f8 (infobulle).

## Points de fond (bloquent la publication)

### F1. Le repère « février 2012, 8 °C » du réglage de froid induit en erreur, et la source citée dit le contraire

**Emplacements** : `site/src/lib/simulateur/Simulateur.svelte`, raison du réglage « Froid
supplémentaire » (« Repères : février 2012, … sous les normales ; la plage s'arrête au froid
« centennal » de RTE, … sous les normales ») ; `site/src/lib/simulateur/phrases.ts`, tuile
« Consommation horaire maximale » (« Le scénario la dépasse : le gradient moyen de RTE y est
prolongé… » et « (février 2012 : … sous les normales) ») ; `docs/enquetes/partage/limite-froid.md`
(« Le simulateur permet d'ajouter **ce** froid ») ; `docs/SIMULATEUR.md` (« Février 2012 … est donné
comme repère, pas comme équivalence ») ; citation de `froid_2012_ecart_normale`.

**Problème.** La phrase de RTE dont le site tire « 8 °C » se termine ainsi (hiver 2024-2025,
p. 18) : « dans des conditions météorologiques similaires à la vague de froid de février 2012
(…8 °C…, ayant conduit à une pointe historique de consommation de 102 GW), **la pointe de demande
électrique devrait demeurer sensiblement inférieure à 100 GW cet hiver** ». La citation du
référentiel s'arrête avant. Or le simulateur, réglé sur ce repère (8 °C, données 2025), donne
**106,6 GW** de consommation horaire (87,4 + 19,2), soit au moins 6,6 GW au-dessus de ce que la même
source annonce pour le même froid, et à l'heure (une pointe à la demi-heure serait plus haute
encore). La synthèse 2018-2019 (p. 4) dit de même qu'un froid comme 2012 conduirait, sur le parc
de 2018-2019, « à une valeur proche du pic historique […] à 102 000 MW » ; le simulateur donne
114,9 GW sur 2018.

L'écart vient surtout du double compte, pas du gradient : les degrés réglés s'ajoutent à une
semaine déjà froide. Le texte le dit, mais place juste à côté deux repères exprimés en écart aux
normales (8 °C, 12 °C) et écrit « ajouter ce froid » : une lectrice pressée règle 8 °C pour
« rejouer 2012 ». Le sens du réglage varie aussi beaucoup d'une année à l'autre : pour porter la
consommation horaire maximale de l'épisode à 102,1 GW, il faut 2,7 °C en 2018 (vague de froid de
fin février déjà dans l'épisode) et 9,8 °C en 2019 (épisode de mi-novembre, maximum de l'épisode
78,7 GW). La tuile attribue enfin le dépassement de la pointe au gradient « prolongé », alors que
la cause principale est le double compte.

**Correction proposée.**

1. Référentiel : compléter la citation de `froid_2012_ecart_normale` (phrase entière) et ajouter
   un chiffre `pointe_froid_2012_hiver_2024_2025` (« sensiblement inférieure à 100 GW », grandeur
   « pointe de consommation », borne supérieure, RTE hiver 2024-2025 p. 18, confiance B, note :
   « estimation de RTE pour un froid comparable à février 2012 sur le système de l'hiver
   2024-2025 ; pointe, pas moyenne horaire »). Facultatif : même chose pour 2018-2019 (≈ 102 GW, p. 4).
2. Ajouter un chiffre calculé `quand_froid_100gw_2025` : plus petit froid réglable (pas de 0,5 °C)
   qui porte la consommation horaire maximale de 2025 au-delà de 100 GW. Je le trouve à **5,5 °C**
   (87 438 + 5,5 × 2 400 = 100 638 MW ; à 5 °C : 99 438 MW).
3. Raison du réglage (remplace la phrase « Repères : … sous les normales. ») :
   « Ce n'est pas un écart aux normales : ces jours ont déjà leur propre froid, que le site ne
   mesure pas, et ces degrés s'y ajoutent ; le même réglage ne représente donc pas le même froid
   d'une année à l'autre. Repère, en consommation plutôt qu'en degrés : selon RTE, un froid
   comparable à celui de février 2012 aurait donné à l'hiver 2024-2025 une pointe « sensiblement
   inférieure à 100 GW » ; avec les données de 2025, le simulateur dépasse 100 GW de
   consommation horaire dès {{quand_froid_100gw_2025}} de plus. »
   Pour la borne de la plage, ne plus la justifier par le froid « centennal » (écart aux normales,
   même confusion : 12 °C sur 2018 donnent 124,5 GW, quand RTE annonçait 109 GW en froid
   centennal pour 2018-2019) ; écrire « choix du site » ou réduire la plage.
4. Tuile « Consommation horaire maximale » : remplacer la phrase sur le gradient et la
   parenthèse finale par : « Le scénario la dépasse. Ce n'est pas le froid de février 2012 : les
   degrés réglés s'ajoutent à ceux de jours déjà froids, et RTE estimait qu'un froid comparable
   donnerait, à l'hiver 2024-2025, une pointe sensiblement inférieure à 100 GW. Au-delà de
   quelques degrés, le gradient moyen est en outre prolongé hors de ce que RTE publie. » (« Le scénario la
   dépasse. » seulement s'il la dépasse ; le reste toujours.) Idéalement, afficher
   aussi pour l'année choisie le froid qui porte le maximum de l'épisode à la pointe de 2012.
5. Fragment `limite-froid.md` : « Le [simulateur](/simulateur) permet d'ajouter du froid :
   quelques degrés de plus pendant les sept jours les plus tendus de l'année observée, multipliés
   par ce gradient. Ces degrés s'ajoutent au froid que ces jours ont déjà connu : ce ne sont pas
   des degrés sous les normales, et 8 °C de plus ne rejouent pas février 2012. RTE estimait qu'un
   froid comparable donnerait, à l'hiver 2024-2025, une pointe « sensiblement inférieure à
   100 GW » {{source:rte-hiver-2024-2025|p. 18}}. » (le reste du point inchangé ; retirer la phrase
   finale redondante « Les jours choisis ont déjà leur propre froid… » ou la fusionner).
6. `docs/SIMULATEUR.md` : réécrire le paragraphe « Double compte » en conséquence, et consigner
   la dépendance à l'année (2,7 à 9,8 °C pour atteindre la pointe de 2012).

### F2. La variante J_r réintègre des arrêts longs qui relèvent de la gestion du combustible, ce que le site exclut ailleurs

**Emplacements** : `docs/enquetes/partage/arrets-modulation.md` (« La tranche peut donc
redémarrer : ce sont des arrêts économiques ») ; `docs/enquetes/quand.md` § « Les heures de
surplus » (phrase supprimée sur l'arrêt « pour économiser son combustible ») ; règle
`MOTIF_MODULATION` de `pipeline/pc/remit.py` et son commentaire ; graphique `ChargePlate.svelte`
(cercle creux 2022) ; notes `quand_*_reintegre_*`.

**Problème.** Le fragment cite la clause « la tranche sera redémarrée si les conditions économiques
le justifient » et en tire une propriété de tous les arrêts réintégrés. Mon décompte (énergie
brute, événements rangés par année de début, chevauchements non traités, donc à reprendre en net
par le pipeline) :

| Année | Arrêts réintégrés | dont texte avec la clause « redémarrée » | dont arrêts de 7 jours ou plus | dont 7 jours ou plus sans la clause |
|---|---|---|---|---|
| 2020 | 6,4 TWh | 2,9 | 4,4 | 3,1 |
| 2022 | 7,1 TWh | 0,6 | 5,6 | 5,2 |
| 2024 | 10,2 TWh | 5,0 | 7,0 | 4,7 |
| 2025 | 7,9 TWh | 5,1 | 3,8 | 2,5 |

Les arrêts longs sans clause durent d'une semaine à près de quatre mois : Chooz 2 du 18/04 au
26/06/2025 (2,5 TWh, un tiers de la variante 2025 ; cause « Maintenance prévisionnelle », première
version publiée le 01/07/2024, soit plus de neuf mois avant, texte vide dans la dernière version,
retenu par la seule règle 2), Cattenom 1 du 03/05 au 11/08/2024 (3,1 TWh), Saint-Laurent 2 du 11/08
au 29/11/2022 (2,4 TWh), en pleine crise des prix, quand une absence de débouchés n'est guère
plausible. Trois événements comptés par la règle 1 disent en toutes lettres « Arrêt pour économie
combustible » (Flamanville 1 2021, Bugey 5 et Blayais 3 2025 ; 0,8 TWh). Hypothèse à vérifier dans
les messages d'EDF auxquels ces déclarations renvoient (edf-2020-00076, edf-2020-00079,
edf-2022-00370, edf-2023-00199, edf-2023-00200, edf-2024-00033) : ces arrêts longs servent à
déplacer du combustible vers l'hiver. Si c'est le cas, ils relèvent de la contrainte d'énergie,
exactement le motif pour lequel la règle exclut les arrêts « pour économie de combustible »
sans le mot « modulation ». La frontière tracée par le mot n'est pas la frontière économique que
le texte affirme. Le BE2025 range d'ailleurs l'économie de combustible dans la modulation (p. 25,
note sur le taux REMIT ; p. 30, « un exemple de modulation liée à la gestion du parc est la
modulation pour économie de combustible »).

Les chiffres publiés ne sont pas faux en tant que calcul ; ce qu'on leur fait dire l'est en
partie, surtout pour 2020-2022 et 2024 (et le cercle creux 2022 du graphique).

**Correction proposée.**

1. Pipeline : séparer dans `meta.json` et dans les notes l'énergie des arrêts qui portent la clause
   de redémarrage (ou de moins de 7 jours) et celle des arrêts longs ; publier, au moins en note de
   `quand_part_j_reintegre_5gw_2025` et `quand_j_reintegre_2025`, la valeur obtenue avec les seuls
   arrêts courts (ou avec la règle 1 seule : 5,1 TWh en 2025 d'après l'agent), pour borner la
   dépendance à Chooz 2.
2. Fragment, en remplacement des phrases « EDF publie… sort du nucléaire disponible non produit. » :
   « EDF publie au titre de REMIT, comme des indisponibilités planifiées, des arrêts et des baisses
   de puissance « pour modulation ». Pour la plupart des arrêts de quelques jours, il précise :
   « Le placement et la durée de cet arrêt pour modulation seront réinterrogés et la tranche sera
   redémarrée si les conditions économiques le justifient » (champ « Information complémentaire »
   des déclarations, jeu REMIT d'EDF sur opendata.edf.fr). D'autres durent plusieurs semaines,
   sont parfois annoncés des mois à l'avance et ne portent pas cette clause : ils peuvent servir à
   garder du combustible pour l'hiver, ce que la contrainte d'énergie limite de toute façon. Les
   arrêts « pour économie de combustible » qui ne disent pas « modulation », qu'EDF et RTE comptent
   pourtant comme de la modulation, restent retranchés. »
   Puis garder la suite (énergie retirée, parts) et finir par : « C'est une sensibilité au choix de
   déclaration d'EDF, pas une capacité physique : la contrainte d'énergie reste la limite la plus
   nette. »
3. `quand.md` : rétablir dans « Les heures de surplus » la mention supprimée, par exemple
   « Les arrêts déclarés « pour économie de combustible » restent retranchés dans les deux
   calculs. »
4. Graphique : dans `remarques`, ajouter que la variante pèse surtout, certaines années (2020, 2022,
   2024), sur des arrêts longs de printemps et d'été.

### F3. Message d'accueil : une insinuation, une asymétrie et une comparaison qui ne dit pas ce qu'elle semble dire

**Emplacement** : `docs/MESSAGE.md`, paragraphe « Aux heures de surplus » (l. 54-65).

**Problème.**
- « les réacteurs qu'EDF déclare indisponibles **alors qu'il** les arrête pour des raisons
  économiques » suggère une déclaration abusive. Déclarer comme indisponibilité planifiée un arrêt
  économique décidé à l'avance est conforme à REMIT ; la variante mesure une sensibilité au choix
  de déclaration, pas une faute. La formule est aussi inexacte : la règle compte des baisses de
  puissance, pas seulement des réacteurs arrêtés, et une partie de l'énergie relève probablement
  du combustible (F2). Un site qui se veut « instrument de preuve, pas un tract » ne peut pas
  laisser cette tournure à l'accueil.
- « on atteint 58 % » : valeur sans plancher, alors que la valeur déclarée est donnée avec sa
  fourchette (52 % et 39 %) ; il manque 47 %.
- « Dans les deux cas, servir cette consommation demanderait plus de production nucléaire sur
  l'année que ce que l'exploitant prévoit » : exact (373,0 + 22,8 ≈ 396 TWh et 373,0 + 25,6 ≈
  399 TWh, contre 350 à 370 TWh), mais la production observée de 2025 dépasse déjà à elle seule
  le haut de la prévision 2026-2027 : la phrase laisse croire que c'est la consommation ajoutée qui
  fait le dépassement. Il faut les chiffres.
- « 1 GW jamais mobilisable » : c'est une hypothèse du site (et le repère du simulateur, 0,5 GW en
  2025 aux heures chères, est plus bas).

**Correction proposée** (identifiants vérifiés dans `chiffres.json` : 52 %, 39 %, 58 %, 47 %,
22,8 TWh, 25,6 TWh, 373,0 TWh, 350 à 370 TWh) :

« Aux heures de surplus, l'abondance ne suffit pas non plus : avec les données de 2025 et la
disponibilité déclarée par EDF, {{quand_part_j_5gw_2025}} au plus de l'énergie d'une consommation
plate de 5 GW aurait trouvé du nucléaire disponible et non produit
({{quand_part_j_plancher_5gw_2025}} en supposant 1 GW non mobilisable à toute heure). EDF déclare
aussi indisponibles des arrêts et baisses de puissance « pour modulation », décidés pour des raisons
économiques ; en les réintégrant, ces parts montent à {{quand_part_j_reintegre_5gw_2025}} et
{{quand_part_j_plancher_reintegre_5gw_2025}}. Dans les deux cas, il faudrait produire
{{quand_energie_j_5gw_2025}} à {{quand_energie_j_reintegre_5gw_2025}} de nucléaire en plus sur
l'année, pour un parc qui a produit {{prod_nucleaire_2025}} en 2025 et dont l'exploitant prévoit
{{prod_nucleaire_prevision_2026_2027}} par an pour 2026-2027 ; le reste viendrait d'autres moyens,
de renouvelables moins arrêtés ou d'exportations en moins. »

Le reste du message (pointe d'hiver, trajectoires, adéquation de RTE) n'est pas touché par ces
chantiers ; je ne l'ai pas relu à nouveau.

## Points de forme

**f1. Écrêtement : 2,9 ou 3 TWh.** `limite-ecretement.md`, note de
`quand_ecretement_prix_negatif_2025`. La note 19 du BE2025 donne 1,3 + 1,6 = 2,9 TWh ; « environ
3 TWh » en est l'arrondi. 2,9 × 10⁶ ÷ 513 = 5 653 MW, soit 5,7 GW. La borne haute reste vraie avec
3 TWh, mais une lectrice qui refait le calcul depuis la note tombera sur 5,7. Écrire « 5,7 à
5,8 GW » ou mentionner les deux. Préciser aussi que l'estimation de RTE ne couvre pas l'éolien en
mer, compté dans l'éolien observé (sens : borne haute un peu moins sûre, effet probablement
négligeable). « La charge résiduelle est surestimée » : la RN est observée, pas estimée ; écrire
« plus haute que sans la production renoncée ». Confiance C défendable (valeur d'entrée
« environ », borne conditionnelle).

**f2. Froid seul : un dépassement par construction.** `phrases.ts`, phrase « Le froid
supplémentaire, à lui seul, porte la charge résiduelle au-delà de ce maximum pendant N h ». Dans 9
années sur 11 (toutes sauf 2016 et 2021), l'heure du maximum de RN est dans l'épisode : le
moindre froid (0,5 °C) donne au moins une heure au-delà du maximum (2025 : 1 h à 0,5 °C). Ajouter
la même précision que pour X : « l'heure du maximum, dans l'épisode, se dépasse elle-même ».

**f3. Heure contre demi-heure.** Tuile « Consommation horaire maximale » : la comparaison du
maximum horaire du scénario à 102,1 GW (demi-heure) sous-estime les dépassements. D'après les
points ODRÉ connus, la moyenne horaire de 2012 la plus haute est au plus de 100,8 GW
((102 098 + 99 411) ÷ 2, le point de 17 h 30 UTC étant sous 99 411 MW). Télécharger 2012 et
publier le maximum horaire, ou dire l'écart dans la tuile.

**f4. Gradient uniforme.** `docs/SIMULATEUR.md`, raison du réglage : « le profil journalier est
relativement peu affecté » ne justifie pas un ajout **uniforme** en MW ; la même page de RTE donne
le chauffage résidentiel à « 30 GW le soir […] lors de froids sévères, contre respectivement 13 et
16 GW à température normale », et le BE2017 un gradient « variable au cours de la journée ». Un
ajout uniforme sous-estime probablement l'effet aux heures de pointe et le surestime la nuit : le
compte des heures au-delà du maximum en est plutôt minoré. À écrire dans les limites.

**f5. Énergie du froid dans J.** Tuile « Dans le nucléaire disponible non produit » : avec du
froid, la production nucléaire en plus affichée ne compte que la part de la consommation ajoutée ;
celle que le froid prend d'abord dans J s'y ajoute. Une demi-phrase dans le détail.

**f6. Deux « 39 % » voisins.** `quand.md`, « Ce qu'une consommation continue… » : la phrase donne
39 % pour 10 GW en réintégrant, puis le paragraphe donne 39 % pour 5 GW avec plancher, et le
fragment qui suit reprend « 47 % au lieu de 39 % ». Retirer les valeurs réintégrées de cette phrase
(le fragment les donne juste après), ou réordonner. « Ce plafond est lâche », placé après deux
valeurs, ne dit plus lequel : écrire « Le plafond avec la disponibilité déclarée est lâche. »

**f7. Lien vers soi-même.** Le fragment `limite-froid.md` est inclus dans `lecture.md` : sur la
page du simulateur, « Le [simulateur](/simulateur) permet… » pointe vers la page elle-même. Écrire
une formulation neutre (« Le réglage « froid supplémentaire » du simulateur… ») ou ne mettre le
lien que dans « Quand ? ».

**f8. Infobulle du graphique.** `ChargePlate.svelte`, `lignes()` : « en réintégrant la modulation
déclarée » ; ce n'est pas la modulation déclarée par EDF (grandeur différente, 33 TWh en 2025).
Écrire « en réintégrant les arrêts déclarés pour modulation ».

**f9. Phrase contradictoire.** `lecture.md` : « Réintégrer les arrêts pour modulation n'y change
rien : la production supplémentaire affichée n'en est que plus haute. » Écrire « Réintégrer les
arrêts pour modulation ne lève pas cette limite : la production nucléaire supplémentaire nécessaire
n'en est que plus haute. »

**f10. Nature de l'écart à la normale de 2012.** Note de `froid_2012_ecart_normale` : « écart moyen
sur l'épisode, pas un minimum » est une interprétation ; RTE écrit « températures moyennes France
inférieures de 8 °C », sans dire si c'est sur tout l'épisode ou au plus froid. Écrire « RTE ne
précise pas sur quelle période porte cet écart ».

**f11. Copies des sources du froid.** Les cinq PDF (hivers 2018-2019, 2022-2023, 2024-2025, BE2017,
CRE 2012) ne sont que dans le scratchpad de la session de l'agent, effacé au redémarrage. Les ranger
avec les autres dans `data/raw/spike_quand/pdf/` (avec leur `.txt`), non versionnés, pour que les
empreintes publiées restent vérifiables.

**f12. Raison du plancher.** Le repère (J moyen aux heures à plus de 150 €/MWh) est un indice de
non-mobilisable, pas une mesure : J à ces heures peut aussi être retenu pour garder du
combustible. Une demi-phrase suffit.

## Ce que je n'ai pas vérifié

- Les messages d'EDF cités en F2 (hypothèse de gestion du combustible pour les arrêts longs) : à
  lire avant d'écrire autre chose que « peuvent servir à ».
- Le rendu des pages (captures de l'agent non relues), les tests TypeScript, et la partie du
  message d'accueil étrangère à ces deux chantiers.
- Une valeur de gradient plus récente que 2022 (l'agent n'en a pas trouvé ; je n'ai pas cherché
  au-delà).

## Vérification des corrections

Vérification du 26/11/2026 (même agent), sur l'arbre de travail non commité, après les
corrections décrites dans `2026-11-26-modulation-agent.md` (« Corrections après relecture ») et la
réécriture de `docs/MESSAGE.md`.

**Verdict : publiable après une dernière correction de texte (V1)** ; V2 à V5 sont de forme.

### (a) Points de la relecture

| Point | Traité | Vérification |
|---|---|---|
| F1 | oui | Citation de `froid_2012_ecart_normale` complète (relue p. 18). Nouveau repère `pointe_froids_2010_hiver_2026_2027` : citation relue dans la synthèse hiver 2026-2027, p. 14 du PDF, et phrase de la p. 7 (« une pointe de plus de 100 GW […] ne se matérialiserait qu'en cas de vague de froid très extrême »). Il est présenté partout comme une borne (« sensiblement inférieures à »). `quand_froid_100gw_AAAA` recalculé : 2025 (100 000 − 87 438) / 2 400 = 5,23, d'où 5,5 °C ; 2018 1,79, d'où 2,0 ; 2019 8,89, d'où 9,0. Exact. Repères en degrés retirés de la raison et de la tuile ; borne de la plage dite « choix du site ». |
| F2 | oui, autrement que proposé | Réintégration limitée aux arrêts de moins de 7 jours sans mention du combustible. Règle défendable : préavis médian de 0,46 jour pour les courts (90 % sous 1,3 jour), de 17 jours pour les longs (3e quartile 96 jours ; mon recalcul depuis la première version publiée). La clause de redémarrage figure dans la dernière version de 18 longs sur 51 : elle ne sépare pas les deux familles, l'agent a raison. Aucune chaîne d'arrêts courts consécutifs (écart ≤ 24 h) ne totalise 7 jours ou plus : pas de long arrêt découpé en courts. Énergie des courts en 2025 : 3,87 TWh nets publiés, contre 3,88 TWh bruts selon mon décompte indépendant de la relecture (7,85 − 3,84 − Blayais 3). |
| F3 | oui | Paragraphe réécrit : plus d'insinuation, fourchette complète (52/39 % → 55/43 %), énergies 22,8 à 24,1 TWh contre 373,0 TWh produits et 350 à 370 TWh prévus (373,0 + 24,1 = 397,1). Équilibré et exact. |
| f1 | oui | Note : 2,9 TWh, soit 5,7 GW ; éolien en mer ; « plus haute que sans la production renoncée ». |
| f2 | oui | `phrases.ts` : « l'heure du maximum, dans l'épisode, se dépasse elle-même dès le moindre froid ». |
| f3 | oui | `pointe_conso_record_2012_horaire` = (99 166 + 102 098) / 2 = 100 632 MW, points relus dans `odre_2012-02-08_soir.json`. L'heure suivante donne 100 266 MW. Tuile au même pas de temps. |
| f4 | oui | Raison et `SIMULATEUR.md`. |
| f5 | oui | Tuile du nucléaire. |
| f6 | oui | « Le plafond avec la disponibilité déclarée est lâche » ; plus de doublon (35 % et 43 %). |
| f7 | oui | Plus de lien vers la page elle-même. |
| f8, f9, f12 | oui | Textes conformes aux propositions. |
| f10 | oui | Note de `froid_2012_ecart_normale`. |
| f11 | oui | PDF, `.txt` et extraits ODRÉ dans `data/raw/spike_quand/pdf/`. |

**Mes propres erreurs**, relevées par l'agent et vérifiées dans les PDF : la phrase du BE2025 sur
la modulation pour économie de combustible est p. 31, pas p. 30 ; la citation sur le chauffage
résidentiel (hiver 2022-2023) est p. 60, pas p. 59. Aucun texte publié ne reprend ces deux numéros
de page.

### (b) Valeurs recalculées indépendamment

Recalcul depuis `data/export/horaire/AAAA.csv` (colonne `nucleaire_disponible_reintegre`, arrêts
courts) :

- 2025 : Σ J_r 33,01 TWh (publié 33,0), part 5 GW 55,1 % (55), avec plancher 42,5 % (43),
  10 GW 35,4 % (35), énergie 5 GW 24,1 TWh (24,1) ;
- 2024 : Σ J_r 28,26 TWh (28,3), part 5 GW 49,7 % (50), avec plancher 34,6 % (35).

Tout concorde. `uv run pc check` : 29 contrôles, 0 échec.

### (c) Formules corrigées : `git grep`

Recherche dans `docs/enquetes`, `docs/MESSAGE.md`, `docs/SIMULATEUR.md`, `site/src`, `pipeline/pc`
et les exports, avec les motifs « 8 °C », « février 2012 », « redémarr », « modulation », « au
plus », plus les anciennes valeurs « 37,0 », « 35,6 », « 58 % », « 47 % », « 25,6 », les
identifiants supprimés (`quand_arrets_modulation_AAAA`, `froid2012`, `froidCentennal`),
« surestim » et « jamais mobilisable ». Il ne reste aucune ancienne valeur, aucun identifiant
supprimé, aucun « au plus » sans « avec la disponibilité déclarée par EDF », et aucun 8 °C
présenté comme repère. Seuls `SIMULATEUR.md` (historique de la correction) et les tests le citent
encore. Les points suivants restent ouverts :

**V1 (à corriger avant publication). Une hypothèse écrite comme un fait.** Le fragment
`arrets-modulation.md` écrit bien que les arrêts longs « peuvent servir à garder du combustible
pour l'hiver ». Les autres textes l'affirment en revanche : « les arrêts longs […] relèvent de la
gestion du combustible ». C'est le cas de la tuile du simulateur (`phrases.ts`, « Les plus longs
relèvent de la gestion du combustible et restent retranchés »), des notes générées
(`export_quand.py`, `NOTE_REINTEGRE` et note de `quand_arrets_modulation_longs_*`), de
`LIMITES_J` et des docstrings de `quand.py`, de `build.py` (donc `meta.json` et
`horaire/LISEZMOI.md`), de `quand.json` et de `SIMULATEUR.md`. Les messages d'EDF qui le diraient
ne sont pas lus. `doaat.edf.fr` répond 403 à une lecture automatique : je n'ai pas pu vérifier non
plus. Par ailleurs, 18 des 51 arrêts longs portent dans leur dernière version la clause « la
tranche sera redémarrée si les conditions économiques le justifient ». Correction : partout,
« les arrêts plus longs, souvent annoncés des semaines ou des mois à l'avance, peuvent relever de
la gestion du combustible : ils restent retranchés ». Puis `pc build`, et `git grep -n "relèvent
de la gestion du combustible"` vide.

**V2 (forme).** « Décidés au jour le jour » est vrai pour la plupart des arrêts courts, pas pour
tous : 18 sur 356 sont déclarés plus de 3 jours avant leur début. Écrire « pour la plupart
déclarés la veille ou le jour même » dans les notes et la tuile. Le fragment dit déjà « pour la
plupart ».

**V3 (forme).** Dans le fragment `arrets-modulation.md`, « Les arrêts longs et les arrêts « pour
économie de combustible », qu'EDF compte pourtant comme de la modulation » étend aux arrêts longs
la note du BE2025 (p. 25), qui ne cite que l'économie de combustible « par exemple ». Écrire :
« Les arrêts longs restent retranchés, comme les arrêts « pour économie de combustible », qu'EDF
compte pourtant comme de la modulation dans ses publications annuelles {{source:…}}. »

**V4 (forme).** Dans le fragment `limite-froid.md`, « dépasse le niveau donné par RTE » :
RTE donne une borne, pas un niveau. Écrire « dépasse 100 GW, seuil sous lequel RTE place ces
pointes ». « quand les températures sont restées 8 °C sous les normales » contredit la note f10 :
écrire « étaient ».

**V5 (forme).** Dans la tuile « Consommation horaire maximale », « les degrés réglés s'ajoutent à
ceux de jours déjà froids » ne vaut pas pour toutes les années : l'épisode de 2019 est en
mi-novembre, choisi parce qu'il est le plus tendu, pas le plus froid. Écrire « de jours déjà parmi
les plus tendus de l'année, souvent froids ».

### (d) Valeurs publiées en ligne (HEAD)

`data/export/chiffres.json` contre HEAD : 231 → 350 chiffres, 0 retrait, **0 valeur modifiée**
(seuls des libellés et des notes changent). `quand.json` : ajouts et textes de définitions et de
limites, aucune valeur numérique existante modifiée. CSV horaires : les 12 colonnes publiées sont
identiques à HEAD (vérifié sur 2018 et 2025), la colonne ajoutée est en dernière position.
`pointe_conso_record_2012` passe à `precision: 0.1`, mais ce chiffre n'existe pas à HEAD : ce
n'est pas un changement de valeur publiée. Les identifiants `quand_*_reintegre_*` ont changé de
sens entre les deux versions non commitées (tous les arrêts, puis les courts), mais aucune n'a été
publiée. Ce changement est décrit dans le rapport de l'agent et consigné dans une nouvelle entrée
de `ERREURS.md`. L'entrée précédente, « un plafond qui dépend de ce qu'EDF déclare
indisponible », donne encore sans renvoi les valeurs de la première version (407 arrêts,
37,0 TWh, 58 % et 47 %). Il faut y ajouter une ligne qui renvoie à l'entrée suivante, sans
réécrire l'entrée elle-même.
