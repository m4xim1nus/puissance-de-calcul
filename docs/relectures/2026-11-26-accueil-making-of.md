# Relecture adverse — ouverture de l'accueil et fidélité du making-of

Date : 26/11/2026. Relecture faite par un agent Opus, en deux rôles successifs : la lectrice
cible (ingénieure marchés de l'électricité et modélisation), puis un lecteur non spécialiste.
S'y ajoute une vérification mécanique de la page `/making-of` contre ses fichiers source.

Périmètre : `site/src/routes/+page.svelte` (titre-question et deux paragraphes),
`site/src/lib/graphiques/HeroPrix.svelte` (façon dont la carte est introduite et légendée),
`site/src/lib/server/makingof.ts` et la page `/making-of`. Le site a été construit
(`npm run build`) sur l'état du dépôt au commit `a835eca` plus l'arbre de travail du moment.
Les pages prérendues `site/build/index.html` et `making-of.html` ont été lues, et l'accueil
servi par `vite preview` a été capturé dans Chromium headless (1280 × 800 et 390 × 844).

Gravités : **FOND** = erreur qui ferait perdre confiance, ou écart à une décision de l'auteur ;
**PRÉCISION** = imprécision qu'une experte relèverait ; **FORME** = maladresse.

Les sources du making-of ont changé **pendant** la relecture : nouvelles lignes de
`DECISIONS.md`, nouveaux paragraphes de la session 2. Un premier passage sur un build périmé
a signalé ces écarts ; ils ont disparu après reconstruction. Le résultat ci-dessous vaut pour
le build final. Il faut relancer le script après toute modification (commande en fin de
rapport).

---

## Verdict

**Publiable après corrections.** Aucune erreur factuelle sur le marché : « day-ahead, fixé
la veille pour le lendemain » est juste, le pas de 15 min depuis le 1er octobre 2025
(livraison) aussi, de même que les jours de 23 et 25 heures et le décompte de 513 h, égal au
chiffre de RTE. Un point de **fond** porte sur la décision de l'auteur : l'accueil affirme
l'hypothèse de travail du brief au lieu de la poser. Le making-of est fidèle mot pour mot
(brief, 2 sessions, 26 décisions, 10 erreurs, intros), sans perte, troncature ni doublon.
Deux défauts de structure déplacent pourtant du texte : une citation de l'auteur est
recomposée, et une entrée d'`ERREURS.md` a été modifiée après publication alors que le
journal dit le contraire.

---

## Rôle 1 — lectrice experte

### 1. L'hypothèse de travail du brief est affirmée comme un fait — **FOND** (décision de l'auteur)

- **Endroit** : `+page.svelte`, 1er paragraphe : « En moyenne sur l'année, la France produit
  une électricité abondante et largement décarbonée. Mais une consommation supplémentaire
  s'ajoute à chaque heure, et l'état du système change d'une heure à l'autre : **la question
  se joue à l'heure, au poste électrique et au prix**. »
- **Problème** : c'est mot pour mot l'*hypothèse de travail* du brief (« Hypothèse de
  travail : la question se joue ailleurs, à l'heure, au poste électrique et au prix »). Or
  `DECISIONS.md` (2026-11-26, l'auteur) retient « Pas de thèse affichée avant les enquêtes :
  l'accueil pose la question ». L'option écartée parmi les trois était justement « hypothèse
  du brief + axe "au guichet" ». La tournure « En moyenne… Mais… » ajoute un jugement :
  la moyenne serait trompeuse. Le brief demande au contraire de « dire où les données
  contredisent l'hypothèse ». Et « au poste électrique » est affirmé alors que « Où ? » est
  déjà jugé pauvre en open data : le site ne pourra peut-être pas le vérifier. Énoncer
  l'hypothèse n'est pas faux ; la présenter comme acquise, si.
- **Correction proposée** (à faire trancher par l'auteur, car cela engage le fond) :
  « La moyenne annuelle ne suffit pas à répondre : une consommation supplémentaire s'ajoute à
  toutes les heures, et l'état du système change d'une heure à l'autre. Notre hypothèse de
  travail est que la réponse se joue à l'heure, au poste électrique et au prix ; le site la
  met à l'épreuve et dit où les données la contredisent ou manquent. » Autre option, plus
  neutre : supprimer la proposition après les deux-points et garder seulement « l'état du
  système change d'une heure à l'autre ».

### 2. « Abondante et largement décarbonée » : sans date ni source, et faux pour une année que la carte propose — **PRÉCISION**

- **Endroit** : `+page.svelte`, 1re phrase.
- **Problème** : la phrase est au présent intemporel et sans note, alors que la règle du site
  veut que chaque affirmation chiffrable soit sourcée et datée. Elle est défendable pour 2024
  et 2025 (production très majoritairement bas-carbone, solde exportateur record). Elle ne
  l'est pas pour 2022 (disponibilité nucléaire au plus bas, France importatrice nette), année
  que les boutons de la carte proposent juste en dessous, avec des prix presque partout
  au-dessus de 200 €/MWh. Le référentiel (`pipeline/referentiels/chiffres.yaml`) n'a aucune
  entrée sur la part bas-carbone de la production ni sur le solde des échanges.
- **Correction** : dater la phrase (« En 2024 et en 2025, la France a produit… ») et
  l'adosser à deux entrées du référentiel : part bas-carbone de la production et solde
  exportateur, tirées de RTE, *Bilan électrique 2025*, avec un recoupement ODRÉ ou ENTSO-E.
  Le compte rendu ne fixe pas ces valeurs : elles sont à relever dans la source.

### 3. « La carte en montre une année » : le prix présenté comme l'état du système — **PRÉCISION**

- **Endroit** : `+page.svelte`, 2e paragraphe : « La carte ci-dessous en montre une
  année ». Le « en » renvoie à « l'état du système ». `docs/CONCEPTION.md` dit aussi « une
  année du système électrique heure par heure ».
- **Problème** : la carte montre un prix, pas l'état du système. Le prix day-ahead de la zone
  France sort du couplage européen (SDAC). Il reflète aussi les conditions des zones voisines
  dès que les interconnexions ne sont pas saturées, ainsi que les offres des producteurs (prix
  négatifs liés aux mécanismes de soutien et à l'inflexibilité). Une experte lira « prix =
  état du système français » comme un raccourci.
- **Correction** : « La carte ci-dessous montre l'un de ces signaux, le prix de gros
  day-ahead de la zone France, issu du couplage des marchés européens et fixé la veille pour
  le lendemain : une case par heure, une ligne par jour. »

### 4. « Une case par heure… le prix… fixé la veille » : depuis le 1er octobre 2025, la case est une moyenne calculée par le site — **PRÉCISION**

- **Endroits** : `+page.svelte`, 2e paragraphe ; `HeroPrix.svelte`, note de source :
  « Depuis le 1er octobre 2025, le prix d'une heure est la moyenne de ses quatre quarts
  d'heure. »
- **Problème** : depuis la livraison du 1er octobre 2025, le day-ahead fixe un prix par
  quart d'heure ; aucun prix horaire n'est plus fixé. La note présente la moyenne comme un
  fait de marché, alors que c'est une convention du site (moyenne arithmétique, non pondérée
  par les volumes). L'année affichée par défaut (2025) contient trois mois dans ce cas.
- **Correction** (note de source) : « Depuis le 1er octobre 2025, le marché day-ahead fixe
  un prix par quart d'heure ; chaque case est la moyenne arithmétique, non pondérée, des
  quatre prix de l'heure, calculée par le site. » Dans l'ouverture, ajouter « (moyenne des
  quarts d'heure depuis octobre 2025) » ou renvoyer à la note.

### 5. « Prix planchers » pour des prix entre −0,10 et 0 €/MWh — **PRÉCISION**

- **Endroit** : `HeroPrix.svelte`, paragraphe `.planchers` : « Dont 285 heures à des prix
  compris entre −0,10 €/MWh (inclus) et 0 €/MWh (exclu) : prix planchers, décompte du
  site. » La constante `PLANCHER` est dans `site/src/lib/heatmap.ts`.
- **Problème** : pour une experte, le « prix plancher » du day-ahead est le prix minimal
  harmonisé du SDAC (−500 €/MWh). Le seuil de −0,10 est un choix du site, ni sourcé ni
  expliqué, et le décompte n'est pas recoupé.
- **Correction** : « Dont 285 heures à peine négatives (entre −0,10 et 0 €/MWh, seuil choisi
  par le site ; décompte du site, non recoupé). » Dire en une phrase, sourcée, pourquoi ces
  prix se concentrent juste sous zéro, ou renvoyer à « Quand ? ».

### 6. « La couleur est écrêtée » : un faux ami dans ce domaine — **PRÉCISION**

- **Endroits** : `HeroPrix.svelte`, légende (« Au-delà de 200 €/MWh, la couleur est
  écrêtée ») et paragraphe `.ecretage`.
- **Problème** : en système électrique, l'écrêtement désigne la limitation de la production
  renouvelable (curtailment), un thème de « Quand ? » (le brief le nomme). Une experte bute
  sur le mot, et un non-spécialiste qui le retrouvera dans « Quand ? » confondra les deux
  sens.
- **Correction** : « Au-delà de 200 €/MWh, la couleur sature : la valeur exacte reste dans
  l'infobulle. » Renommer de même les identifiants (`ECRETAGE`, `ecretees`) dans un second
  temps.

### 7. Recoupement des 513 h coté « A » : même donnée de base — **PRÉCISION** (doute)

- **Endroit** : note de source des heures négatives sous la carte : « Recoupement
  indépendant : 513 h (recalcul du site sur les prix SMARD / energy-charts). Confiance A ».
- **Problème** : RTE et SMARD partent des mêmes résultats d'enchère (EPEX / SDAC). Le
  recalcul prouve que le pipeline est juste, pas que la donnée l'est. « Autre éditeur, autre
  méthode » est vrai à la lettre ; la donnée, elle, n'est pas indépendante. Le chiffre n'est
  pas en cause, seule la cote se discute. Le périmètre affiché (« une heure est négative si la
  moyenne de ses quarts d'heure l'est ») est-il celui de RTE ou une déduction du site ? Je ne
  l'ai pas vérifié dans le PDF.
- **Correction** : écrire « recoupement de calcul (mêmes résultats d'enchère, autre
  éditeur) ». Si la définition de A doit exiger une donnée indépendante, coter B.
  Attribuer explicitement la règle des quarts d'heure (RTE, ou « hypothèse du site, cohérente
  avec le chiffre de RTE »).

### Vérifié, sans remarque

- « Prix de gros day-ahead […] fixé la veille pour le lendemain » : exact (enchère couplée
  de J−1, résultats publiés en début d'après-midi).
- Jours de 23 h (case 2 h inexistante) et de 25 h (case 2 h coupée en deux, été puis hiver) :
  exacts, et le code (`grille`, `decalageParis`) les traite bien.
- 513 heures négatives en 2025 : décompte du site égal au chiffre publié par RTE.
- La question en titre est celle du brief ; elle ne contient pas de thèse. *Doute* :
  « la vague » présuppose une vague, alors que le site distingue annonces, réservations et
  raccordements. C'est le libellé choisi par l'auteur ; je le signale sans le corriger.

---

## Rôle 2 — lecteur non spécialiste

À l'ouverture, on comprend de quoi parle le site : la question est le titre, visible sans
défiler en bureau comme sur téléphone (captures 1280 × 800 et 390 × 844). Le progrès est net
par rapport à la version précédente. On comprend moins pourquoi la carte des prix est là.

### 8. « La carte » juste après « poste électrique » : on attend une carte de France — **FORME**

- **Endroit** : `+page.svelte`, 2e paragraphe (« La carte ci-dessous… »), qui suit
  immédiatement « au poste électrique ».
- **Correction** : « Le calendrier ci-dessous » ou « Le graphique ci-dessous », ou bien
  « carte de chaleur » à la première mention.

### 9. Le lien entre data centers et carte des prix n'est pas dit — **FORME**

- **Endroit** : `+page.svelte`, 1er paragraphe. « Une consommation supplémentaire s'ajoute à
  chaque heure » peut se lire « augmente d'heure en heure », et rien ne dit qu'un data center
  consomme à peu près en continu.
- **Correction** : « Un data center consomme à peu près en continu (aucune courbe de charge
  n'est publiée) : il s'ajoute à toutes les heures, les chères comme celles à prix
  négatif. » Cela reste un constat, pas une thèse.

### 10. Jargon non expliqué — **FORME**

- « prix de gros », « poste électrique », et pourquoi un prix peut être négatif. « day-ahead »
  est expliqué (« fixé la veille pour le lendemain »), c'est bien.
- **Correction** : la lectrice cible n'a pas besoin qu'on vulgarise (règle du brief). Il
  suffit de renvoyer ces trois termes au glossaire replié de `/methode`, par un lien ou une
  infobulle, sans alourdir l'ouverture.

---

## Fidélité du making-of

### Méthode

Script jetable :
`[caviardé : dossier temporaire local]/fidelite.py`.
Il compare, **mot pour mot** (balisage Markdown retiré d'un côté, texte HTML de l'autre,
espaces insécables normalisées), unité par unité :

- le brief entier (1 038 mots) ;
- l'intro du journal, puis chaque session : titre, date, horaire, et demande et détail dans
  l'ordre de la source ;
- l'intro des décisions, puis chaque ligne du tableau : date, décision, raisons, colonne
  « Qui » et étiquettes ;
- l'intro des erreurs, puis chaque entrée : date, titre, champs, étiquette « repérée par ».

Dans les listes numérotées rendues, le script réinsère le numéro (« N. ») pour détecter une
ligne prise à tort pour une liste (le cas « 2035. »). Il vérifie aussi que chaque résumé
d'en-tête de session (Durée, Agents, Coût) est bien le début du paragraphe complet. La
structure a été contrôlée en complément, en lisant le HTML : citations, listes imbriquées,
marques Markdown résiduelles (aucune : ni `*`, ni `` ` ``, ni `|`, ni `#`), attribut
`hidden` au prérendu (aucun, donc tout reste lisible sans JavaScript).

### Résultat

- **Mots** : identiques partout. Brief rendu une seule fois et en entier ; 2 sessions sur 2,
  26 décisions sur 26, 10 erreurs sur 10, les trois intros identiques. Les dates affichées
  correspondent aux dates source.
- **Étiquettes dérivées** : les 26 « tranchée par » correspondent à la colonne « Qui », y
  compris « l'auteur (demande), Claude (forme) » rendue en deux étiquettes avec leur rôle.
  Les 10 « repérée par » sont justes : contre-vérification adverse, agent du site, agent de
  la page et relecture → « un agent » ; test du référentiel et `pc check` → « un test » ;
  deux fois « Claude lui-même ». Pour l'erreur 6, `pc check` lancé par l'agent du pipeline
  est classé « un test », ce qui est défendable : c'est le contrôle qui a échoué.
- **Résumés de session** : Durée, Agents et Coût reprennent la première phrase du paragraphe,
  qui reste en entier dans le détail. Ce doublon est voulu et ne trompe pas.

### 11. Citation de l'auteur recomposée (session 2) — **PRÉCISION**

- **Endroit** : session 2, « Demande de l'auteur ». Dans `JOURNAL.md`, « jeton pas encore
  arrivé » est une ligne à part, après la liste des retours. Le Markdown maison la traite
  comme la suite du dernier item (continuation paresseuse, comme le ferait CommonMark). Rendu :
  « …il y a sans doute plus clair compact à faire aussi. jeton pas encore arrivé », à
  l'intérieur de l'item « making of ». Le saut de ligne entre « selon ROADMAP.md » et
  « retours de lecture : » disparaît aussi (« ROADMAP.md retours de lecture : »).
- **Pourquoi c'est grave ici** : une demande citée « telle quelle » doit garder sa
  structure. La phrase sur le jeton se retrouve dans le retour sur le making-of. Le journal
  lui-même la traite pourtant à part (« jeton pas encore arrivé : le jeton ENTSO-E… »).
- **Correction** : rendre le bloc cité de la demande en mode verbatim. Les messages de
  l'auteur ne sont pas du Markdown : une ligne source donne une ligne rendue (`<br>` ou
  `white-space: pre-line`), sans continuation paresseuse. Ajouter un test qui vérifie qu'à
  chaque ligne source de la citation correspond une ligne rendue. Solution minimale, sans
  toucher aux mots : insérer une ligne `>` vide avant « jeton pas encore arrivé » dans
  `JOURNAL.md`.

### 12. Entrée d'`ERREURS.md` modifiée après publication, alors que le journal dit « sans changer son texte » — **PRÉCISION**

- **Endroits** : `ERREURS.md`, dernière entrée (« Relecture « lectrice experte » : cinq
  erreurs de fond avant publication ») ; `JOURNAL.md`, session 2 : « Claude la remet au
  format sans changer son texte : le préambule devient le champ Repéré par, la liste passe
  sous Faux ».
- **Problème** (vérifié par `git diff HEAD~1 HEAD` au commit `da10ffe`) : la remise au format
  a **ajouté** une phrase (« cinq erreurs de fond dans le site construit, avant
  publication : »). L'ancienne phrase d'annonce, « Les cinq erreurs de fond : », est restée
  à la fin de « Repéré par ». Sur la page, ce deux-points annonce donc le champ
  « Correction », et non la liste. L'entrée avait déjà été publiée (commit `b8297b9`).
  Modifier un registre d'erreurs publié est admissible, à condition de le dire exactement.
- **Correction** : supprimer la phrase ajoutée dans « Faux » et y mettre la phrase d'origine
  « Les cinq erreurs de fond : », retirée de « Repéré par ». Le texte redevient identique à
  l'original, seulement réordonné. Corriger le journal : « remise au format : préambule et
  liste réordonnés, aucune phrase ajoutée ni retirée ». Si l'on garde la phrase ajoutée, le
  journal doit dire « une phrase d'introduction ajoutée au champ Faux » et la phrase orpheline
  doit disparaître.

### 13. Brief : un paragraphe sort de sa liste — **FORME**

- **Endroit** : brief, section « Le site ». Le paragraphe indenté « Le journal est tenu **au
  fil de l'eau**, pas reconstruit à la fin. » appartient à l'item « Un onglet « Making-of » ».
  Le Markdown maison, qui ne gère pas les items de plusieurs paragraphes, le rend hors liste,
  entre deux `<ul>`. Les mots sont intacts et le sens est conservé, mais pour un texte
  « publié tel quel », la structure change.
- **Correction** : gérer dans `liste()` (`site/src/lib/markdown.ts`) les paragraphes de
  continuation indentés après une ligne vide. À défaut, l'accepter et le savoir.

### 14. Le bloc « Format » d'`ERREURS.md` n'est pas publié, sans que la page le dise — **FORME**

- **Endroit** : `analyserErreurs`, l'intro s'arrête à « Format : ». La page `/making-of`
  annonce : « Cette page les met en forme sans changer leur texte. » Le gabarit, qui contient
  la liste des catégories de repérage, est omis.
- **Correction** : ajouter « (le gabarit de format d'`ERREURS.md` n'est pas repris) » à la
  phrase d'introduction, ou rendre le gabarit replié.

### 15. Session 2 sans durée, agents ni coût, sans mention « en cours » — **FORME**

- **Endroit** : en-tête de la session 2 (pas de `dl.resume`).
- **Correction** : afficher « session en cours » quand le paragraphe Durée manque.

### 16. « Reprend deux points » suivi de trois sous-items — **FORME**

- **Endroit** : `JOURNAL.md`, session 2 : « Claude relit les captures et reprend deux
  points : ». Le troisième sous-item (jeton `--filet`) est un défaut signalé par l'agent, pas
  une reprise de Claude.
- **Correction** : « reprend deux points et note un défaut signalé par l'agent : ».

### Mineur (hors page publiée)

- `site/src/lib/heatmap.ts`, commentaire de `AnneePrix.prix` : « au centime entre −1 et 1 »,
  alors que le code et la note publiée disent quatre décimales. Le commentaire est à
  corriger.
- « 1er janvier », « 1er octobre » sans exposant (sous-titre et note de la carte).

---

## Doutes

- L'attribution « Bundesnetzagentur / SMARD.de via energy-charts.info » des prix français
  n'a pas été revérifiée en ligne : la relecture s'est faite hors réseau.
- La date de passage du SDAC au pas de 15 min (livraison du 1er octobre 2025, enchère du
  30 septembre) est vérifiée de mémoire, pas à la source.
- La vérification mécanique compare des suites de mots. Elle ne détecte pas un changement
  d'imbrication de liste qui garderait l'ordre des mots. Ces changements ont été cherchés à la
  main, ce qui a donné les points 11 et 13 ; il peut en rester ailleurs, dans des listes à
  plusieurs niveaux du journal (session 1, « Fait »).

Relancer la vérification après toute modification des sources :

```sh
cd site && npm run build && cd .. && \
python3 -I [caviardé : dossier temporaire local]/fidelite.py "$PWD"
```

---

## Suites données (Claude, 2026-11-26)

Chaque point vérifié dans le code ou les fichiers avant correction.

| # | Suite |
|---|---|
| 1 | **Corrigé**. Ouverture réécrite en description de ce que fait le site, sans affirmation sur le système. Consigné dans `ERREURS.md` (la formule venait de la consigne de Claude). |
| 2 | **Corrigé** par suppression de la phrase (pas d'ajout au référentiel). |
| 3 | **Corrigé** : « l'un des signaux de l'état du système électrique ». |
| 4 | **Corrigé** : la note de source dit que la moyenne horaire des quarts d'heure est un calcul du site (convention RTE ; vérifié dans `pipeline/pc/build.py`). |
| 5 | **Corrigé** : « prix à peine négatifs, seuil choisi par le site, décompte non recoupé ». |
| 6 | **Corrigé** : « la couleur sature ». |
| 7 | **Maintenu**, avec réserve notée au backlog. Il n'existe qu'un résultat d'enchère ; ce que l'on recoupe est le décompte, fait indépendamment par RTE et par le site. RTE retient en outre Nord Pool pendant le découplage d'EPEX du 26/06/2024 : les données ne sont pas strictement les mêmes. La définition de la cote A sera précisée sur la page méthode. |
| 8 | **Corrigé** dans `JOURNAL.md` : ligne `>` vide avant « jeton pas encore arrivé », qui sépare la phrase de la liste comme dans le message d'origine. |
| 9 | **Corrigé** : texte d'origine rétabli, seulement réordonné ; journal rectifié ; consigné dans `ERREURS.md`. |
| 10 | **Corrigé** : « calendrier ». |
| 11 | Lien données-prix : **corrigé** par la nouvelle ouverture. Liens vers le glossaire : **backlog** (le glossaire n'existe pas encore). |
| 12 | **Corrigé** : rendu des paragraphes de continuation dans une liste (test ajouté) ; l'intro du making-of signale le bloc « Format » non affiché. |
| 13 | **Corrigé** : session sans durée marquée « en cours » ; « deux points » reformulé. |
