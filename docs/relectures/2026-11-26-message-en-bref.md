# Relecture adverse : message principal et « En bref » du making-of

Date : 2026-11-26. Relectrice : agent Opus, posture « lectrice experte »
(marchés de l'électricité, modélisation énergétique). Aucun autre fichier
modifié, rien commité.

**Lu** : `CLAUDE.md`, `docs/MESSAGE.md`, `docs/EDITO.md`,
`docs/enquetes/combien.md` et `quand.md` (en entier), entrées concernées de
`pipeline/referentiels/chiffres.yaml` et `data/export/chiffres.json`,
`docs/spike/quand.md`, `docs/spike/quand-contre-verification.md`,
`docs/spike/reseau-geo-meteo.md` (§ 1b), `pipeline/pc/bilan.py`,
`pipeline/tests/test_bilan.py`, `making-of/en-bref.json`,
`site/src/lib/EnBref.svelte`, `site/src/lib/server/makingof.ts` (décisions),
`site/src/lib/server/enbref.test.ts`, `making-of/JOURNAL.md` (sessions 1 à 3),
`making-of/DECISIONS.md` (colonne « Qui »).

**Sources primaires relues pour cette relecture** (texte extrait des PDF du
cache local `data/raw/spike_quand/pdf/`) : BP2025 *Fonctionnement du système
électrique*, § 5.2.1 et § 5.3 (p. 12 à 29) ; BP2025 *Principaux résultats*,
p. 15 et trajectoires de consommation (p. 22-23 en pagination du PDF) ;
BP2025 *La consommation d'électricité*, § 2.5 (p. 26-28). Les numéros de page
cités ci-dessous pour des chiffres **absents du référentiel** sont ceux du
fichier texte extrait : à vérifier contre la pagination imprimée avant
d'entrer dans `chiffres.yaml`.

Classement : **fond** = faux ou trompeur, bloque la publication ; **forme** =
à corriger, ne bloque pas. « Latent » = juste sur les données actuelles,
faux dans un cas prévisible.

---

## Objet 1 — `docs/MESSAGE.md`

### 1. Fond — le message ignore le calcul que RTE a déjà fait, et sa conclusion le contredit en partie

**Où** : 2e paragraphe, « d'un quart à près de la moitié de ces marges, si le
reste du système ne changeait pas. L'accueil de la vague se joue donc d'abord
sur ces heures-là : soit les data centers réduisent leur consommation aux
heures de pointe, soit des moyens nouveaux s'ajoutent. »

**Problème** : la trajectoire de consommation des data centers fait partie des
trajectoires « décarbonation lente » et « rapide » du Bilan prévisionnel 2025,
et RTE a calculé, dans le même exercice, l'adéquation 2030-2035 avec ces
trajectoires (BP2025 *Fonctionnement*, § 5.3.2 et 5.3.3) :

- décarbonation **lente** (celle des 21 TWh) : « Le besoin de capacités
  additionnelles à la pointe de consommation dans le mix R3 est nul à
  l'horizon 2030-2035 » (p. 28), sous réserve d'EnR au rythme R3 et d'un socle
  thermique d'environ 13 GW ; besoin d'environ 1 GW en R1, jusqu'à près de
  4 GW en 2035 en R1-R2 (p. 28-29) ;
- décarbonation **rapide** (celle des 32 TWh) : environ −10 GW de marges entre
  2026 et 2030, « besoin de capacités additionnelles limité, de l'ordre de 2 à
  4 GW en 2030 » (p. 26) ; en 2035, « entre 1 GW et 6 GW » selon le rythme EnR
  (R3 à R1), marge positive d'environ 1 GW en R4 (p. 28). Ce besoin vient de
  **toute** la hausse de consommation (électrification, industrie, hydrogène,
  data centers), pas des data centers seuls.

Une lectrice qui connaît le BP2025 objectera immédiatement : « RTE a fait le
calcul intégré, pourquoi le refaire à la main à système figé ? » Et le
« soit… soit… » est contredit, pour la trajectoire lente, par la source même
dont viennent les 21 TWh : à mix R3, ni effacement des data centers ni moyens
nouveaux ne sont nécessaires selon RTE. Le message tire une condition
nécessaire de données qui ne l'établissent pas. Aucune des deux enquêtes ne
cite ces résultats : le message ne peut donc pas non plus les « résumer ».

**Correction** : (a) ajouter au référentiel les résultats d'adéquation 2030 et
2035 du BP2025 (besoin de capacités par trajectoire et rythme EnR, avec
pages) ; (b) les citer dans le message à la place, ou à côté, du calcul à
système inchangé ; (c) reformuler la conclusion en condition **au-delà** des
trajectoires de RTE (voir la proposition de texte, point 11). Signalé hors
périmètre : « Quand ? » gagnerait aussi à citer ces résultats, dans le
paragraphe « Rapprocher X des marges de RTE ».

### 2. Fond — « d'un quart à près de la moitié » : le calcul compte deux fois la consommation déjà présente, et traite une trajectoire comme une charge plate

**Où** : « Les trajectoires de 2035 correspondent à une consommation moyenne de
2,4 à 3,7 GW (21 et 32 TWh répartis sur 8 760 heures) : d'un quart à près de
la moitié de ces marges, si le reste du système ne changeait pas. »

**Vérification arithmétique** : 21 ÷ 8,76 = 2,40 GW ; 32 ÷ 8,76 = 3,65 GW ;
2,40 ÷ 10 = 24 % ; 3,65 ÷ 8 = 46 %. L'arithmétique est juste. Le
raisonnement ne l'est pas, pour trois raisons :

1. **Double compte.** Les marges de 8 à 10 GW de l'hiver 2026-2027 sont
   calculées avec la consommation de 2026-2027, data centers compris (RTE :
   les marges varient « en fonction de la dynamique d'évolution de la
   consommation »). Ce qui s'ajoute d'ici 2035 n'est pas la consommation
   totale de 2035 mais sa **hausse**. Même en ne retranchant que le niveau de
   2024 (4 à 5 TWh, ≈ 0,5 GW, sans doute moins que le niveau 2026-2027
   supposé par RTE), la hausse vaut (21 − 5) ÷ 8,76 ≈ 1,8 GW à
   (32 − 4) ÷ 8,76 ≈ 3,2 GW, soit **18 à 40 %** des marges, et au plus cela.
   « D'un quart à près de la moitié » surestime.
2. **Puissance moyenne ≠ contribution à la pointe.** 2,4 à 3,7 GW est une
   moyenne annuelle. La contribution à la pointe d'hiver dépend du profil :
   plus basse si le refroidissement baisse en hiver ou si les sites
   s'effacent, plus haute si la montée en charge se poursuit pendant l'année
   2035 (le niveau de l'hiver 2035-2036 dépasse alors la moyenne de 2035).
   Aucune courbe de charge n'est publiée (« Combien ? », « Ce qui manque »).
   Le message passe de « un GW consommé jour et nuit » à « consommation
   moyenne » sans écrire l'hypothèse de profil plat.
3. **Deux années, deux systèmes.** Rapporter une consommation de 2035 à une
   marge de 2026-2027 est un raisonnement à système figé ; « si le reste du
   système ne changeait pas » le dit, mais le point 1 montre que la source
   publie l'alternative. Les extrêmes sont aussi croisés (trajectoire basse
   sur marge haute, trajectoire haute sur marge basse) sans que ce soit dit.

**Correction** : soit supprimer le ratio et citer les résultats intégrés de
RTE (point 1), soit l'écrire ainsi : « Si elle était plate, la hausse de
consommation de ces trajectoires entre 2024 et 2035 vaudrait au plus 1,8 à
3,2 GW, soit au plus un cinquième à deux cinquièmes de ces marges, à système
inchangé : un ordre de grandeur, pas un calcul d'adéquation. » Consigner dans
`ERREURS.md` (le calcul vient de `EDITO.md` et a déjà été corrigé une fois
sur l'arrondi, pas sur le fond).

### 3. Fond — l'équivalence « un GW retire un GW de marge » est énoncée sans les précautions de « Quand ? », et l'amalgame entre marge probabiliste et écart horaire est réintroduit

**Où** : « Un GW consommé jour et nuit retire à peu près un GW de marge aux
heures les plus tendues de l'hiver, et RTE évaluait ces marges à… »

**Problème** : « Quand ? » prend trois précautions que le message perd :
(a) l'équivalence vaut « dans un calcul d'adéquation » et pour une
consommation **plate** (« L'équivalence cesse d'être exacte dès que la
consommation n'est pas plate ») ; (b) c'est une inférence du site : « RTE
n'écrit pas cette équivalence pour la consommation » ; (c) « La marge dont
parle RTE n'est pas un écart qu'on lit sur une courbe. » Or le message écrit
« marge aux heures les plus tendues » puis « ces marges » : la lectrice
comprend que les 8 à 10 GW sont une réserve de puissance disponible aux
heures de pointe, exactement le contresens que « Quand ? » écarte. Enfin
« jour et nuit » ne dit pas « toute l'année » : c'est la présence en hiver
qui compte.

**Correction** : « Dans un calcul d'adéquation, une consommation plate de
1 GW, présente toute l'année, retire à peu près 1 GW à la marge de sécurité
d'approvisionnement (une inférence de ce site : RTE fait ce passage pour une
hausse de la pointe, pas pour une consommation ajoutée). Cette marge n'est
pas un écart observable à une heure donnée : RTE la calcule par simulation,
par rapport au critère des trois heures de défaillance par an. »

### 4. Fond — la date des marges manque dans le texte

**Où** : « RTE évaluait ces marges à {{marge_rte_hiver_2026_2027}} pour
l'hiver 2026-2027 ».

**Problème** : tout le second paragraphe repose sur ce chiffre. Il vient du
BP2025 (hypothèses de 2025, publication décembre 2025), il est antérieur à la
synthèse de l'hiver de novembre 2026, qui ne redonne aucune marge en GW et
prévoit une disponibilité nucléaire plus basse (48,5 GW contre 50,5 GW
l'hiver précédent). « Quand ? » et `EDITO.md` (point 3) le disent ; le
message ne le dit que dans la note marginale, repliée sur téléphone.

**Correction** : « dans son Bilan prévisionnel 2025, avant la baisse de
disponibilité nucléaire prévue pour cet hiver ».

### 5. Fond — le titre contredit l'une des deux conclusions de « Quand ? »

**Où** : « **Ce n'est pas une question d'énergie, c'est une question de
pointe d'hiver.** » et « En énergie, les data centers pèsent peu ».

**Problème** : « Quand ? » conclut aussi sur l'énergie : aux heures de
surplus, une charge plate de 5 GW ne trouverait au plus que
{{quand_part_j_5gw_2025}} (52 %) de son énergie dans du nucléaire disponible
non produit (39 % en retranchant 1 GW), et la servir ainsi demanderait
{{quand_energie_j_5gw_2025}} (22,8 TWh) de production nucléaire en plus, pour
un parc qui a produit 373 TWh en 2025 et dont l'exploitant prévoit 350 à
370 TWh par an : « En énergie, la limite est plus nette encore. » Le reste
viendrait de moins d'exportations ou d'autres moyens, au facteur d'émission
marginal européen, non calculé. Le message supprime ce constat (point 4 de
`EDITO.md`) et affirme l'inverse en titre. Par ailleurs « pèsent peu » ne
vaut que pour 2024 : dans les trajectoires du BP2025, la consommation totale
passe de 442 TWh (2024) à 505 TWh (lente) ou 580 TWh (rapide) en 2035
(*Principaux résultats*, p. 22-23 du PDF, à vérifier) ; la hausse des data
centers (≈ 16 à 28 TWh) en représente environ un quart (lente) à un cinquième
(rapide). Pour une experte, ce n'est pas « peu ».

**Correction** : titre « **Moins une question d'énergie annuelle qu'une
question de pointe d'hiver.** » ; « en énergie, les data centers pèsent peu
aujourd'hui » ; ajouter une phrase reprise de « Quand ? » sur les heures de
surplus (voir point 11). Si l'on cite la part dans la hausse, ajouter 505 et
580 TWh au référentiel.

### 6. Fond — « au plus 7 % » est numériquement faux et présente la trajectoire haute comme un plafond

**Où** : « au plus 7 % de la consommation de 2024 ».

**Problème** : 32 ÷ 442,2 = 7,24 %, donc plus de 7 % : « au plus » est faux
(« Combien ? » écrit correctement « environ 7 % »). Surtout, « au plus »
suggère un majorant, alors que la trajectoire rapide n'est pas un plafond :
elle suppose 60 % de concrétisation des projets à mise en service avant 2030
et 20 % d'utilisation de la puissance de raccordement en 2030 ; les
réservations ({{dc_reserve_rte_2026_05}}) et le scénario tendanciel de l'ADEME
(36,7 TWh, autre périmètre) vont au-delà.

**Correction** : « soit environ 5 à 7 % de la consommation de 2024 »
(21 ÷ 442 = 4,7 % ; 32 ÷ 442 = 7,2 %).

### 7. Fond — « la vague » n'est pas définie : glissement entre trajectoire abattue et réservations

**Où** : « L'accueil de la vague se joue donc… » ; le message ne mentionne ni
la pyramide des puissances ni les réservations.

**Problème** : le constat central de « Combien ? » (les étages recherché,
réservé, signé, raccordé, appelé ne s'additionnent pas ; RTE abat fortement
la somme des demandes) disparaît. La lectrice lit « la vague » = 21 à
32 TWh, alors que ces trajectoires sont précisément la version abattue par
RTE, bien en dessous des {{dc_reserve_rte_2026_05}} réservés. Le message
minimise ainsi l'incertitude sur l'ampleur (ses hypothèses de concrétisation
et d'utilisation) et confond implicitement « la vague » annoncée avec une
trajectoire.

**Correction** : une phrase : « Ces trajectoires supposent qu'une partie
seulement des projets se concrétise : elles sont très en dessous des
{{dc_reserve_rte_2026_05}} réservés auprès de RTE en mai 2026, qui n'engagent
pas à consommer. » Et remplacer « la vague » par « ces consommations » ou
« les trajectoires de RTE ».

### 8. Fond — « d'abord » n'est pas établi

**Où** : « L'accueil de la vague se joue donc d'abord sur ces heures-là ».

**Problème** : le réseau local n'a pas été étudié ; le paragraphe des limites
dit lui-même qu'il « peut nuancer, voire contredire » le message, et
`EDITO.md` écrit : « c'est peut-être là que se joue l'essentiel ». « D'abord »
hiérarchise une question mesurée et une question non mesurée.

**Correction** : « À l'échelle nationale, l'accueil se joue sur ces
heures-là ».

### 9. Fond — « que personne ne publie » est plus fort que ce que le site a établi

**Où** : « le réseau local (ce que peut recevoir chaque poste électrique, que
personne ne publie) ».

**Problème** : « Quand ? » écrit « à notre connaissance, aucune capacité
d'accueil en consommation par poste n'est publiée en open data » ; le spike
(`docs/spike/reseau-geo-meteo.md`, § 1b) note que RTE a annoncé une carte des
zones favorables (250 et 750 MW, réseau 400 kV) dont la publication n'a pas
été confirmée. « Personne ne publie » est réfutable par une seule carte.

**Correction** : « que personne, à notre connaissance, ne publie en données
ouvertes ».

### 10. Fond — le paragraphe des limites omet l'hypothèse dont dépend le calcul

**Où** : « **Ce que ce message ne dit pas encore.** »

**Problème** : il liste réseau local, carbone, prix, système 2035. Il manque :
(a) **le profil réel des data centers** (aucune courbe de charge publiée,
flexibilité inconnue), alors que le ratio du 2e paragraphe suppose un profil
plat et que la conclusion repose sur leur capacité à « réduire leur
consommation aux heures de pointe » ; (b) **l'hypothèse des trajectoires**
elles-mêmes (taux de concrétisation et d'utilisation supposés par RTE) ;
(c) la **date des marges** (point 4) si elle n'est pas mise dans le corps ;
(d) les **voisins** : qui sert la consommation ajoutée aux heures de surplus
(nucléaire, EnR moins arrêtées, exportations en moins) n'est pas calculé.
« Le carbone (ce qu'émettrait la production qui servirait ces
consommations) » gagnerait à dire « au facteur d'émission marginal, européen
dès que les exportations baissent », conformément à la règle moyen ≠
marginal.

**Correction** : ajouter (a) et (b) en une phrase chacune ; préciser
« marginal » dans le point carbone.

### 11. Proposition de texte (à recouper avant usage)

Les chiffres en clair sont des calculs ; les deux phrases marquées † exigent
d'ajouter au référentiel les résultats d'adéquation 2030-2035 du BP2025.

> **Moins une question d'énergie annuelle qu'une question de pointe
> d'hiver.** En 2024, les data centers des sites dédiés ont consommé
> {{dc_conso_sites_dedies_2024}}, de l'ordre de 1 % de la consommation brute
> ({{conso_brute_france_2024}}). Pour ces mêmes sites, les deux trajectoires
> de référence du Bilan prévisionnel 2025 de RTE vont de
> {{traj_bp2025_lente_2035}} à {{traj_bp2025_rapide_2035}} en 2035, soit
> environ 5 à 7 % de la consommation de 2024. Elles supposent qu'une partie
> seulement des projets se concrétise, et restent très en dessous des
> {{dc_reserve_rte_2026_05}} réservés auprès de RTE, qui n'engagent pas à
> consommer.
>
> En puissance, l'ordre de grandeur change. Dans un calcul d'adéquation, une
> consommation plate de 1 GW, présente toute l'année, retire à peu près 1 GW
> à la marge de sécurité d'approvisionnement (inférence de ce site). RTE
> évaluait cette marge, calculée par simulation, à
> {{marge_rte_hiver_2026_2027}} pour l'hiver 2026-2027, dans son Bilan
> prévisionnel 2025, avant la baisse de disponibilité nucléaire prévue cet
> hiver. Si elle était plate, la hausse de consommation des trajectoires
> entre 2024 et 2035 vaudrait au plus 1,8 à 3,2 GW, d'un cinquième à deux
> cinquièmes de cette marge à système inchangé. † Le système changera : en
> intégrant toute l'électrification, RTE ne trouve aucun besoin de capacités
> nouvelles d'ici 2035 dans la trajectoire lente (à rythme de renouvelables
> suffisant), et un besoin de 1 à 6 GW en 2035 dans la trajectoire rapide.
>
> Aux heures de surplus, l'abondance ne suffit pas non plus : en 2025, au
> plus {{quand_part_j_5gw_2025}} de l'énergie d'une consommation plate de
> 5 GW aurait trouvé du nucléaire disponible et non produit, et le reste
> viendrait d'autres moyens ou d'exportations en moins.
>
> À l'échelle nationale, l'accueil se joue donc à la pointe d'hiver : au-delà
> des trajectoires de RTE, ou † si l'électrification est rapide, il faudra
> que ces consommations baissent aux heures de pointe, ou que des moyens
> nouveaux s'ajoutent.

Paragraphe des limites : garder le texte actuel, avec les ajouts du point 10
et la correction du point 9.

### 12. Forme — périmètre et nombre de trajectoires

« Les trajectoires de RTE » : écrire « les deux trajectoires de référence du
Bilan prévisionnel 2025, pour ces mêmes sites dédiés » (le périmètre est
porté par la phrase précédente mais doit l'être par celle-ci ; RTE publie
aussi un test de sensibilité « stagnation », d'où « de référence »).

### 13. Forme — titre de la section

« Ce qu'établissent les enquêtes » : le message contient une inférence du site
(l'équivalence) et, après correction, des résultats de RTE absents des
enquêtes. « Ce qu'on peut en dire, à ce jour » est plus exact, ou garder le
titre et faire dire au texte ce qui est inférence.

---

## Objet 2 — « En bref » (`bilan.py`, `en-bref.json`, `EnBref.svelte`)

### 14. Fond — décisions : la somme des parts dépasse le total

**Où** : `EnBref.svelte` l. 67-68, alimenté par `making-of/+page.svelte`
l. 73-76.

**Problème** : le texte affiche « 34 décisions consignées, dont 14 tranchées
par l'auteur et 24 par Claude » : 14 + 24 = 38 > 34. Les 4 décisions à
attribution partagée (« l'auteur (demande), Claude (forme) », etc.) sont
comptées des deux côtés (`some(...)`). De plus, « tranchées par l'auteur »
est inexact pour une décision où l'auteur a formulé la demande et Claude la
forme. Une lectrice quantitative voit l'incohérence en une seconde.

**Correction** : « 34 décisions, dont 10 tranchées par l'auteur, 20 par
Claude, et 4 partagées (l'auteur sur la demande ou le fond, Claude sur la
forme) » ; calculer « seul l'auteur », « seul Claude », « partagée ».

### 15. Fond — agents : deux nombres contradictoires sur la même page

**Où** : tableau « Par session », session 1 : 8 agents (6 Opus, 2 Sonnet) ;
`JOURNAL.md`, session 1 : « **Agents** : 10 (8 Opus, 2 Sonnet) », et « fil
principal et 8 sous-agents dont la transcription est conservée ».

**Problème** : `bilan.py` compte les fichiers `*.meta.json` présents ; le
journal compte les lancements et dit que certaines transcriptions ne sont
pas conservées. La tuile « Agents lancés » (21) est donc au mieux « agents
dont la transcription subsiste », et son libellé « lancés » est faux pour la
session 1. Si des transcriptions manquent, le « Temps actif » de ces agents
manque aussi (le coût, lui, dépend de ce que couvre `cost-state`, non
vérifiable ici).

**Correction** : renommer « Agents relevés » avec la précision « d'après les
transcriptions conservées ; le journal en compte 10 pour la session 1, dont
des relances » ; ou réconcilier les deux définitions et corriger l'une des
deux sources.

### 16. Fond — « Temps de l'auteur, mesuré » n'est pas une borne basse

**Où** : tuile « Temps de l'auteur, mesuré » (« borne basse ») ; méthode « Ce
n'est qu'une borne basse » ; docstring de `bilan.py` l. 17-19.

**Problème** : l'indicateur compte **entièrement** tout intervalle de moins
de 30 min entre la dernière activité du fil principal et la demande suivante,
y compris une absence de 25 min (surestimation possible), et **rien** d'un
intervalle de 31 min passé à relire (sous-estimation). Il ne compte pas la
lecture faite pendant que Claude travaille. C'est donc un indicateur, ni
borne basse ni borne haute ; « mesuré » renforce une précision qu'il n'a pas.
Placée à côté de « Temps actif en session : 5 h 35 », la tuile invite en
outre à lire « l'auteur a passé 1 h 09 sur 5 h 35 ».

**Correction** : libellé « Temps de réponse de l'auteur en session » ;
précision : « intervalles de moins de 30 min entre la fin d'un tour de Claude
et la réponse de l'auteur : un ordre de grandeur, qui peut compter de courtes
absences et ignore les relectures plus longues ou hors session ». Si l'on
tient à une borne basse, plafonner chaque intervalle au lieu de l'écarter ne
suffit pas non plus : renoncer au mot.

### 17. Fond si confirmé — sémantique de `cost-state` et sessions enchaînées

**Où** : `bilan.py` l. 111-113 (dernier `cost-state` du fichier) et l. 249-254
(somme par session).

**Problème** : le code suppose que le dernier `cost-state` d'une transcription
couvre exactement cette transcription, agents compris. Si Claude Code tient
ce compteur par processus et non par conversation (cas `/clear`, ou reprise
avec `--resume`/`--continue`), deux transcriptions d'un même processus
partagent un compteur cumulatif et leur somme compte deux fois. Indice : la
session 2 finit à 12 h 09, la session 3 commence à 12 h 10, ce qui évoque un
`/clear` dans le même processus ; au relevé de fin de session 3, son coût
pourrait inclure celui de la session 2. Inversement, si le compteur repart de
zéro à une reprise, la partie antérieure est perdue. Aucun test ne couvre ces
cas, et je n'ai pas pu vérifier.

**Correction** : avant le relevé de fin de session 3, comparer le
`cost-state` de la transcription de la session 3 à celui de la session 2
(jetons Opus lus en cache : 218 M en session 2) ; s'il est cumulatif,
soustraire par différence entre transcriptions consécutives d'un même
processus. Écrire la conclusion dans la docstring et dans « Comment c'est
compté ».

### 18. Forme (latent) — rattachement des transcriptions aux sessions

**Où** : `bilan.py` l. 249, `min(debuts, key=abs(début − première demande))`.

**Problème** : (a) une transcription ouverte tard dans la session N, plus près
du début de N+1 que de N, est attribuée à N+1 (ex. : session 2 à 9 h 10,
session 3 à 12 h 13, transcription ouverte à 10 h 50 → session 3) ; il faut
la dernière session commencée avant la première demande, avec une tolérance
de quelques minutes (les en-têtes du journal sont approximatifs : 23 h 03
contre 23 h 10 relevé, 12 h 13 contre 12 h 10). (b) Une transcription qui
couvre deux sessions (reprise) est attribuée entière à la première : la
session 1 du JSON finit à 8 h 59 alors que le journal la clôt à 1 h 26, ce qui
signale de l'activité du matin rattachée à la session 1. (c) Les
transcriptions sans message « human » sont ignorées avec leur coût
(l. 247-248). (d) `sansCout` est calculé par session : une session avec une
transcription close et une en cours affiche un coût partiel comme complet,
sans avertissement.

**Correction** : rattacher par « dernier début ≤ première demande +
tolérance » ; découper les périodes aux bornes de session ; garder le coût
des transcriptions sans demande humaine (rattachées par horodatage) ; propager
un drapeau « incomplet » par transcription. Ajouter un test par cas.

### 19. Forme — l'avertissement « session en cours » est incomplet

**Où** : `EnBref.svelte` l. 175-179.

**Problème** : il dit que les jetons et le coût de la session 3 manquent, mais
« Travail des modèles » et « Commandes » de la session 3 manquent aussi (0 dans
le total), alors que « Temps actif », « Temps de l'auteur », signes et agents
l'incluent. Les tuiles mélangent donc deux périmètres.

**Correction** : « ses jetons, son coût, le travail des modèles et les
commandes ne sont pas encore comptés ; les durées, signes et agents le sont » ;
idéalement ne publier qu'un relevé de fin de session.

### 20. Forme — « Travail des modèles » : ce n'est pas du « temps de calcul »

**Où** : tuile « Travail des modèles », précision « temps de calcul cumulé ».

**Problème** : `totalAPIDuration` est la durée des requêtes aux modèles vue par
le client (attente, génération, réseau), pas un temps de calcul. La
lectrice peut y lire une mesure d'effort machine. « Travail » est aussi
anthropomorphique.

**Correction** : libellé « Durée cumulée des appels aux modèles » ;
précision « vue depuis Claude Code : génération et attente comprises ;
plusieurs agents en parallèle comptent chacun ».

### 21. Forme — « Jetons relus » : risque de contresens sur le volume

**Où** : tuile « Jetons relus » (384 M).

**Problème** : une non-développeuse peut lire « 384 millions de jetons de
documents lus », soit plus d'un milliard de caractères. C'est en réalité le
même contexte renvoyé à chaque appel. Les jetons écrits en cache (≈ 7 M) et
l'entrée non mise en cache (≈ 3 M, surtout Haiku) ne figurent nulle part.

**Correction** : précision « le même contexte (fichiers, échanges) renvoyé à
chaque appel et servi par un cache : ce n'est pas un volume de documents
distincts » ; mentionner les deux autres postes dans « Comment c'est compté ».

### 22. Forme — le ratio « 124 feuillets de Claude pour un feuillet de l'auteur »

**Où** : tuile « Textes écrits par Claude », `ratio` l. 60.

**Problème** : le numérateur compte tous les `.md` versionnés de `docs/`,
`making-of/`, `site/src/` : environ 70 % de ce volume (mesuré en octets) sont
les rapports bruts du spike et des relectures, écrits par des agents et non
publiés comme pages du site, plus les citations de l'auteur. Le dénominateur
exclut le brief (4,5 feuillets), affiché pourtant dans les tuiles de
l'auteur. Le rapport n'a pas de sens stable et sonne comme un indicateur de
productivité.

**Correction** : supprimer le ratio, ou ventiler « pages du site »
(enquêtes, méthode, making-of) / « rapports de travail » (spike, relectures)
et rapporter à l'auteur brief compris (285 ÷ 6,8 ≈ 42).

### 23. Forme — heures de début incohérentes avec le journal

**Où** : colonne « Début » (23 h 10, 12 h 10) contre en-têtes du journal
(23 h 03, 12 h 13), sur la même page.

**Correction** : afficher l'heure du journal, ou préciser « première
activité relevée dans les transcriptions ».

### 24. Forme — signes et choix de l'auteur

**Où** : `bilan.py` l. 120-123 et `_reponses_question`.

**Problème** : (a) un texte collé dans l'invite est-il marqué `typed` ? Si
oui, il est compté comme écrit par l'auteur (à vérifier sur une
transcription) ; (b) les commandes tapées (`/clear`, etc.) comptent comme
messages ; (c) une réponse à choix multiples (« A, B ») n'est pas dans
`libelles` et compte comme texte libre ; (d) la regex coupe une réponse
libre contenant `",` ou `".`.

**Correction** : exclure les commandes, découper les choix multiples sur
« , » avant comparaison, tester (a) et (c).

### 25. Forme — total d'agents et catégorie « autre »

**Où** : `nbAgents` (l. 46) compte « autre », `agents()` (l. 41-45) ne
l'affiche pas : le total peut dépasser la ventilation affichée.

**Correction** : afficher « N autres » quand la catégorie existe.

### 26. Forme — risques de fuite dans le JSON publié

- **Identifiant de modèle brut** : `bilan.py` l. 166, un modèle non reconnu
  devient une clé du JSON telle quelle. Avec un fournisseur tiers, cet
  identifiant peut contenir un numéro de compte ou une région (ARN). Repli
  sur « autre », et ajouter ce cas à `enbref.test.ts`.
- **Horaires** : `debut`/`fin` à la minute, dont une fin à 8 h 59 après une
  session de nuit. Le journal publie déjà les débuts ; les fins disent un peu
  plus des habitudes de l'auteur. Risque faible, à trancher par l'auteur
  (arrondir à l'heure, ou ne publier que la durée).
- **« `/cost` ne lui est pas disponible »** (méthode, et journal) : révèle le
  type d'abonnement de l'auteur. Anodin ; « l'auteur n'a pas de relevé de ce
  qu'il a payé » suffit.
- Pas de texte, de chemin ni d'identifiant de session dans le JSON actuel :
  vérifié par lecture.

### 27. Forme — brief « qui revient à l'auteur »

Le brief, « écrit par l'auteur avec Claude », porte le liseré jaune de
l'auteur. Préciser « co-écrit avec Claude sur claude.ai ; ni ce temps ni ce
coût ne sont comptés ici ».

---

## Verdict

**Message principal : non publiable en l'état ; publiable après réécriture**
selon les points 1 à 10 (le point 11 propose un texte), l'ajout au référentiel
des résultats d'adéquation 2030-2035 du BP2025 et, si on les cite, des
consommations totales de 2035, puis une relecture du texte réécrit. Le
défaut principal n'est pas un arrondi : le message raisonne à système figé
alors que la source primaire publie le calcul intégré, qui contredit sa
conclusion pour la trajectoire lente, et son titre contredit la conclusion
« énergie » de « Quand ? ».

**« En bref » : publiable après corrections** des points 14 à 16, et après
vérification du point 17 avant le prochain relevé. Les points de forme 18 à
27 peuvent suivre, en commençant par 18 et 19, qui fausseraient le prochain
relevé.

---

## Vérification des corrections (2026-11-26, même relectrice)

Lu : nouveau `docs/MESSAGE.md` ; les trois entrées `besoin_capacites_*` de
`chiffres.yaml` et leur valeur dans `data/export/chiffres.json` (2 à 4 GW,
1 à 6 GW, 0 GW) ; `pipeline/pc/bilan.py` révisé ; `test_bilan.py` (9 tests,
qui passent) ; `making-of/en-bref.json` régénéré ; `EnBref.svelte` ;
`making-of/+page.svelte` (décisions) ; l'entrée de `ERREURS.md`. Citations
de RTE recontrôlées dans le texte extrait du PDF (*Fonctionnement*, p. 26,
27 et 28 en pagination imprimée) : conformes au référentiel.

### A. Suivi des points 1 à 27

| Point | État | Remarque |
|---|---|---|
| 1 | traité | Résultats d'adéquation au référentiel et cités. « Quand ? » ne les cite toujours pas (hors périmètre ; ni corrigé ni porté au backlog : à ajouter). |
| 2 | traité, avec une erreur reprise de ma proposition | voir V2 |
| 3 | traité | quelques mots à revoir, voir V4 |
| 4 | traité | — |
| 5 | traité | titre et phrase sur les heures de surplus ; plafond sans son plancher, voir V6 |
| 6 | traité | « environ 5 à 7 % » (4,7 et 7,2 %) |
| 7 | traité, avec une erreur reprise de ma proposition | voir V1 |
| 8 | traité | « à l'échelle nationale » |
| 9 | traité | — |
| 10 | traité | profil, hypothèses des trajectoires, voisins, carbone marginal |
| 11 | utilisé | deux de ses phrases étaient fautives (V1, V2) : erreurs de la relectrice |
| 12, 13 | traités | — |
| 14 | traité | auteur seul, Claude seul, partagées (`every` et `Set`) ; la somme boucle |
| 15 | traité | « Agents distincts », et le journal compte les lancements ; 8 en session 1 cadre avec « 8 sous-agents dont la transcription est conservée » |
| 16 | traité | libellé et méthode corrects |
| 17 | traité | Réfuté pour la session 2. Le recoupement automatique (écart > 2 % → arrêt) couvre aussi le cas session 3 après `/clear`, qui m'inquiétait. |
| 18 | en partie | (a), (c) et (d) traités. (b) n'est pas traité : une conversation qui s'étend sur deux sessions va entière à la première. Docstring l. 9-11 : encore « la plus proche », ce qui contredit l. 33-34. Forme. |
| 19 | traité | — |
| 20, 21 | traités | jetons écrits en cache et lus hors cache désormais affichés dans la méthode |
| 22 | traité | ratio supprimé ; pages du site / rapports séparés |
| 23 | traité | plus d'horaires publiés |
| 24 | en partie | Commandes et choix multiples traités. Non traités : (a) texte collé compté comme tapé (non vérifié) et (d) regex des réponses libres. Forme. La méthode dit « les fichiers Markdown du dépôt, hors brief », alors que seuls `docs/`, `making-of/` et `site/src/` sont comptés. Forme. |
| 25, 26, 27 | traités | « autre » affiché ; modèle inconnu → « autre » ; dates seulement ; formule sur `/cost` retirée ; brief « coécrit » |

### B. Relecture du message réécrit

**V1. Fond — MW ≠ MWh, dans une phrase que j'avais proposée.** « [Les
trajectoires, 21 à 32 TWh] restent très en dessous des
{{dc_reserve_rte_2026_05}} réservés » compare une énergie annuelle à une
puissance. C'est la règle la plus élémentaire du projet, et l'erreur vient
de mon point 11. Correction : ne pas comparer, et dire ce que les
trajectoires supposent : « Elles supposent qu'une partie seulement des
projets se concrétise, et que les sites n'utilisent qu'une fraction de leur
puissance de raccordement ; les {{dc_reserve_rte_2026_05}} réservés auprès
de RTE en mai 2026 n'engagent pas à consommer. » On peut aussi écrire
« 2,4 à 3,7 GW en moyenne, à comparer avec prudence aux
{{dc_reserve_rte_2026_05}} de puissance réservée, une autre grandeur ». À
consigner dans `ERREURS.md`, comme erreur de l'agent relecteur.

**V2. Fond (mineur) — la borne « au plus 1,8 à 3,2 GW » est mal construite,
elle aussi dans ma proposition.** Pour majorer la hausse, il faut retrancher
de chaque trajectoire le niveau de 2024 le plus **bas** (4 TWh). Avec
(21 − 5), on obtient le bas de la fourchette lente, pas son maximum : la
hausse lente peut atteindre (21 − 4) ÷ 8,76 = 1,94 GW. « Au plus 1,8 » est
donc faux pour la trajectoire lente. Correction : « au plus 1,9 à 3,2 GW en
moyenne ((21 − 4) et (32 − 4) TWh répartis sur 8 760 heures) ». Les ratios
deviennent 1,94 ÷ 10 = 19 % et 3,20 ÷ 8 = 40 % : « d'un cinquième à deux
cinquièmes » reste juste. Dans `ERREURS.md`, remplacer « au plus 18 à 40 % »
par « au plus 19 à 40 % ».

**V3. Fond (mineur) — la conclusion dépasse encore RTE.** « Dans la
trajectoire rapide, ou si les data centers dépassent ces trajectoires, il
faudra que des consommations baissent aux heures de pointe ou que des
moyens nouveaux s'ajoutent. » Deux excès :
- dans la trajectoire rapide, RTE trouve aussi le besoin de 2030 « totalement
  résorbé » si la disponibilité hivernale du nucléaire atteint 55 GW
  (p. 27, déjà dans la note du référentiel), et une marge positive d'environ
  1 GW en 2035 au rythme R4 ;
- « si les data centers dépassent ces trajectoires » : un dépassement
  quelconque, dans la trajectoire lente, n'implique pas un besoin. RTE donne
  un besoin nul, pas la marge restante.

Correction proposée : « Dans la trajectoire rapide, RTE trouve un besoin de
quelques GW, sauf disponibilité nucléaire haute ou renouvelables plus
rapides. Des data centers nettement au-delà de ces trajectoires
réduiraient la marge d'environ un GW par GW consommé à la pointe. Ce besoin
se couvre par des moyens nouveaux ou par des consommations qui baissent aux
heures de pointe, celles des data centers comprises. »

**V4. Forme — trois phrases à relire.**
- « c'est une inférence de ce site, que RTE fait pour une hausse de la
  pointe » se lit comme si RTE faisait cette inférence. Écrire : « une
  inférence de ce site ; RTE fait le même passage pour une hausse de la
  pointe, pas pour une consommation ajoutée ».
- « Si elle était plate » : l'antécédent grammatical est « cette marge ».
  Écrire « Si cette hausse était plate ».
- « Ce calcul, RTE l'a fait » vient juste après « pas un calcul
  d'adéquation ». Écrire « Le calcul d'adéquation, RTE l'a fait ».

**V5. Forme — conditions de la trajectoire lente.** « si les renouvelables se
développent au rythme prévu » : R3 n'est pas « le rythme prévu », c'est le
rythme de la configuration de référence de RTE, parmi quatre (R1 à R4).
Écrire « au rythme de référence de RTE ». Le résultat suppose aussi une
disponibilité nucléaire médiane (≈ 51,5 GW l'hiver en 2030). À 46 GW, les
marges baissent d'environ 6 GW (note du référentiel). Le message vient de
rappeler la baisse de disponibilité de cet hiver (48,5 GW) : ajouter « et
une disponibilité nucléaire médiane » serait cohérent.

**V6. Forme (règle du projet) — plafond sans plancher.** « au plus
{{quand_part_j_5gw_2025}} » est publié sans ce qui rend le plafond lâche.
Le garde-fou de `ERREURS.md` exige pourtant qu'un « au plus » se publie
« avec ce qui le rend lâche, chiffré ». Ajouter « ({{quand_part_j_plancher_5gw_2025}}
en retranchant 1 GW jamais mobilisable) ». Ajouter aussi « des
renouvelables moins arrêtés » à « d'autres moyens ou d'exportations en
moins », comme dans les limites.

**V7. Forme — « la contrainte qui compte est donc la pointe d'hiver ».**
Le paragraphe précédent vient de dire que l'abondance ne suffit pas non plus
aux heures de surplus. Écrire « la contrainte la plus nette ».

Le reste a été vérifié et est exact : citations de RTE, 21 ÷ 442 et
32 ÷ 442, date et nature des marges, équivalence avec ses précautions,
limites et carbone marginal.

### Verdict de la vérification

**« En bref » : publiable.** Restent des points de forme : 18 (b), docstring
l. 9-11, 24 (a) et (d), et la définition des textes de Claude dans la
méthode.

**Message : publiable après correction de V1 à V3**, trois phrases dont deux
venaient de ma propre proposition. Les points V4 à V7 sont recommandés ;
V6 applique une règle déjà écrite du projet. Après ces corrections, une
nouvelle relecture adverse n'est pas nécessaire : il suffit de vérifier les
trois phrases.
