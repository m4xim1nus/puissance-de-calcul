# Journal des sessions

Tenu au fil de l'eau par Claude Code (owner du projet). Chaque demande de
l'auteur est citée telle quelle ; quand elle est elliptique, on écrit ce
qu'elle recouvrait. Le coût est celui relevé par `/cost` quand l'auteur le
fournit ; sinon il est marqué « non relevé ».

> **Caviardage.** Le dépôt et le site sont publics. À la demande de
> l'auteur, son prénom est remplacé par « l'auteur » dans tout le
> making-of, une précision sur la lectrice est caviardée dans le brief et
> une mention personnelle a été supprimée du journal. L'historique git a
> été réécrit en conséquence le 26/11/2026, avant la première
> publication : aucun commit public ne contient la version d'origine.

---

## Session 1 — 2026-11-25, à partir de 23 h 03 · lancement

**Demande de l'auteur** (citée telle quelle) :

> lis le md dans /source/, créé avec un chat Claude. Initie ce projet,
> dont tu es maintenant l'owner. Utilise des ss agents Opus et Sonnet
> quand cela est approprié

**Ce qu'elle recouvrait** :

- « le md dans /source/ » : le fichier `source/BRIEF.md` du dossier du
  projet (pas un dossier `/source` à la racine du système), rédigé par
  l'auteur dans une conversation avec Claude sur claude.ai ;
- « initie ce projet » : poser le dépôt, les conventions, le phasage, et
  lancer le premier travail utile — sans attendre une validation pour ce
  qui relève de l'owner ;
- « ss agents Opus et Sonnet quand cela est approprié » : déléguer à des
  sous-agents, en choisissant le modèle selon la tâche. Règle retenue :
  Opus là où le jugement sur un chiffre compte, Sonnet pour le
  mécanique (voir `CLAUDE.md`, « Sous-agents »).

**Fait** :

- lecture du brief et des conventions de `quifaitlaloi` et
  `leurs-voix-nos-droits` (structure, stack, suivi, déploiement) ;
- dépôt git initialisé, squelette, `CLAUDE.md`, `ROADMAP.md`,
  `BACKLOG.md`, making-of ouvert ;
- trois spikes de sources lancés en parallèle (deux Opus, un Sonnet) :
  système électrique horaire, data centers, réseau/géo/météo.

- deux questions posées à l'auteur pendant les spikes. Réponses :
  - nom : « Puissance de calcul » conservé (option recommandée) ;
  - publication, réponse citée telle quelle : *« Public dès le premier
    livrable, avec caviardage de détails trop perso qui serait publiés
    dans le making-of »*. Explicitation : dépôt et site publics dès la
    première enquête relue ; le making-of (journal, brief) ne doit pas
    exposer de détails personnels. Claude a choisi un caviardage
    **visible** plutôt qu'une réécriture, pour ne pas trahir le « tel
    quel » du brief (règle dans `CLAUDE.md`).

- échafaudage du site (agent Sonnet) et du pipeline (Claude), commités ;
- les trois spikes rendent leurs rapports (`docs/spike/`). Claude relit,
  vérifie lui-même un point surprenant (les postes RTE sur ODRÉ n'ont
  plus de coordonnées : confirmé, retrait « pour des raisons de sécurité
  publique »), corrige une mention devenue fausse dans un rapport (le
  `.gitignore` existait déjà, l'agent avait regardé avant sa création) ;
- contre-vérification adverse des chiffres clés confiée à un agent Opus
  qui reçoit les affirmations et les sources, pas les conclusions ;
- après minuit, quatre arbitrages de fond soumis à l'auteur (registre dans
  `DECISIONS.md`). Réponses : « Combien ? » d'abord, puis « Quand ? » et
  le simulateur ; pas de thèse avant les enquêtes ; il crée un jeton
  ENTSO-E. Sur les sollicitations extérieures, réponse citée telle
  quelle : *« Aucun pour l'instant, "Le nuage était sous nos pieds"
  n'est pas réutilisable sans leur accord, pour ce micro-projet ? Je
  suis ta reco »*. Explicitation : L'auteur demande si l'absence de licence
  interdit vraiment la réutilisation pour un projet de cette taille, et
  s'en remet à la recommandation de Claude (lien, pas d'extraction,
  sourçage primaire de chaque projet).

- la contre-vérification rend son rapport : la plupart des chiffres sont
  confirmés à la source, mais **deux erreurs de fond** du spike sont
  repérées (« 18 GW dont 7 GW avant 2030 », ratio 0,035 / 0,63 GW), plus
  une imprécision de Claude lui-même et une mineure. Toutes consignées
  dans `ERREURS.md` avant correction ; rapports de spike annotés
  d'errata plutôt que réécrits ;
- conception du site (`docs/CONCEPTION.md`) : Claude rejette son premier
  jet (fond crème, serif, accent chaud, gros chiffre en hero), qu'il juge
  trop proche du gabarit par défaut. Retenu : hero = une année heure par
  heure (heatmap), papier calque froid et encre bleu de Prusse, notes
  marginales portant la source de chaque chiffre ;
- référentiel des chiffres (`pc/chiffres.py`) : 32 chiffres, 22 sources,
  unités contrôlées par nature de grandeur. Sa règle « confiance A =
  recoupement d'un autre éditeur » attrape aussitôt une surcote de
  Claude (consignée) ;
- texte de « Combien ? » écrit par Claude. Une citation de RTE est
  vérifiée par Claude dans le PDF, car la contre-vérification ne
  l'avait pas couverte. En relisant, Claude trouve trois hypothèses du
  BP2025 tapées à la main dans le texte : vérifiées dans le PDF, elles
  passent au référentiel ;
- deux agents lancés : pipeline des séries horaires (Opus) ; système
  visuel et page « Combien ? » (Opus, avec captures d'écran et relecture
  visuelle).

- L'auteur signale, message cité tel quel : *« J'ai créé un compte sur
  https://transparency.entsoe.eu/, mais pour avoir le security token (ce
  qui était nécessaire ?), il y a un délai potentiel de 3 jours. Il
  faudrait pouvoir gérer le déploiement dégradé sans cette donnée, avec
  des WIP là où nécessaire. »* Explicitation : L'auteur demande si le jeton
  est vraiment indispensable (oui, pour l'API, pas pour l'interface web)
  et veut que la mise en ligne n'attende pas : les parties qui en
  dépendent s'affichent « en chantier » (WIP).

- pipeline commité ; `pc check` sur toutes les années révèle des
  tolérances calibrées sur une seule année (consigné, recalibré) ;
- page « Combien ? » et système visuel livrés par l'agent du site, qui
  signale trois imprécisions dans le texte de Claude (consignées,
  corrigées), puis hero de l'accueil (heatmap des prix 2015-2026) ;
  l'agent du site repère aussi un défaut d'arrondi des prix du pipeline
  (consigné, corrigé à la source) ;
- caviardage : liste proposée par Claude, arbitrée par l'auteur (réponse
  citée telle quelle, caviardée : *« Profil : je suis ta proposition.
  [caviardé : mention personnelle] : à complétmeent supprimer.
  [caviardé : prénom] : remplacer par l'auteur. Projets voisins à
  conserver. »*, et pour l'adresse du site : *« pdc. »*). Explicitation :
  l'auteur choisit une suppression pure pour un passage, sans marque, ce
  qui déroge à la règle du caviardage visible ; Claude l'applique et le
  signale globalement dans la note ci-dessus. Premier passage du script :
  il remplaçait aussi un « Max » qui voulait dire « maximum » (en-tête de
  tableau) et mettait une majuscule fautive en début de ligne ; repéré
  sur un clone d'essai, corrigé avant application. Second défaut :
  Claude avait écrit dans le registre des décisions le nom de ce qu'on
  supprimait ; reformulé, filtre repassé ;
- l'auteur demande de garder l'identité git habituelle : *« ok, garde
  l'adresse [caviardé : adresse électronique] »* ;
- en écrivant cette entrée, Claude a d'abord cité ces deux réponses
  sans les caviarder, remettant dans le journal ce que le caviardage
  retire. Repéré par Claude à la relecture, avant tout commit
  (consigné dans `ERREURS.md`) ;
- relecture adverse « lectrice experte » du site construit lancée (Opus)
  avant toute publication.

- la relecture « lectrice experte » rend son verdict : publiable après
  corrections, 27 points dont 5 de fond (consignés). Claude revérifie
  dans les PDF les points qui contredisent ses propres notes, corrige le
  texte et le référentiel ; l'agent du site corrige le rendu ;
- dépôt public créé (`m4xim1nus/puissance-de-calcul`), premier push,
  CI verte. Le site attend le branchement de Cloudflare Pages par
  l'auteur (Claude n'a pas accès à son compte Cloudflare).

**Agents** : 10 (8 Opus, 2 Sonnet). L'agent du site a été relancé trois
fois avec son contexte (page « Combien ? », hero, corrections).

**Durée** : de 23 h 03 à 1 h 26, soit environ 2 h 25 de temps réel, avec
jusqu'à quatre agents en parallèle.

**Coût** : pas de montant en euros, aucun relevé `/cost` n'a été
transmis. Volumes estimés à partir des transcriptions locales (fil
principal et 8 sous-agents dont la transcription est conservée) :
Opus, ≈ 0,81 M jetons produits, ≈ 152 M jetons lus en cache et ≈ 2,4 M
écrits en cache ; Sonnet, ≈ 0,07 M produits, ≈ 10,7 M lus en cache et
≈ 0,24 M écrits en cache. La lecture du contexte en cache domine
largement le volume.

**Après la session** (même jour) : l'auteur branche Cloudflare Pages.
Le site est en ligne sur `pdc.technoperchoir.fr`, et toutes les routes
répondent (404 compris). Jeton ENTSO-E toujours attendu. La relecture
de l'auteur et la recette sur téléphone ouvriront la session 2.

---

## Session 2 — 2026-11-26, à partir de 9 h 10 · retours de l'auteur, « Quand ? », simulateur

**Demande de l'auteur** (citée telle quelle) :

> reprends la session 2 selon ROADMAP.md
> retours de lecture :
>  - ok dans l'ensemble - même si j'ai une lecture naïve, aucune expertise dans le domaine
>  - sur la home, pas clair pour moi pourquoi ça commence par un gros graphique du Prix de gros day-ahead, certes clair et joli, avant ce qui semble être la phrase d'accroche "Le système français...", qui se trouve tout en bas de la page/accessible en scroll. Peut être logique pour un expert, obscur pour moi
>  - enquête combien ras
>  - méthode ras
>  - making of : contenu intéressant sans doute, mais forme trop à plat, illisible pour un humain : effort graphique pour lire plus facilement, eg utiliser les formats imposés pour les décisions/erreurs/autres? pour faire des élements UI. Intégrer le brief au journal, avec toogle pour afficher/masquer. Pour le journal, il y a sans doute plus clair compact à faire aussi.
> jeton pas encore arrivé
>
> go intégrer mes retours aux md, pour reprendre la session 2 (retours, enquête Quand, simulateur, etc)

**Ce qu'elle recouvrait** :

- « lecture naïve » : l'auteur relit en non-spécialiste. Ses retours ne
  portent sur aucun chiffre ; ils portent sur la lisibilité. La lectrice
  cible reste l'experte, mais une page d'accueil qui ne se comprend
  qu'avec l'expertise rate aussi l'experte pressée ;
- accueil : la phrase-question (« Le système électrique français
  peut-il accueillir… ») arrive après la heatmap, sa légende et ses
  cas particuliers, donc hors de l'écran à l'ouverture. Rien ne dit
  pourquoi le site s'ouvre sur des prix de gros. À refaire : la
  question d'abord, une ou deux phrases qui disent pourquoi regarder
  l'électricité **heure par heure** et ce que montre la carte, puis la
  carte ;
- « Combien ? » et « Méthode » : rien à signaler (« ras ») ;
- making-of : aujourd'hui trois fichiers Markdown rendus bruts, à la
  suite. Les décisions et les erreurs ont un format fixe (tableau daté,
  champs Faux / Repéré par / Correction / Garde-fou) : s'en servir pour
  en faire des éléments d'interface (fiches, étiquettes, filtres) au
  lieu de texte à plat. Le brief n'est plus une section à part : il
  entre dans le journal, à l'endroit où il a servi (session 1), replié
  par défaut et dépliable. Le journal lui-même : une présentation plus
  compacte (en-tête de session avec date, durée, agents, coût ; détail
  dépliable) ;
- « jeton pas encore arrivé » : le jeton ENTSO-E n'est pas dans
  `source/` ; l'étape 2 de l'ordre prévu (branchement ENTSO-E) est
  sautée, comme prévu par la roadmap ;
- « intégrer mes retours aux md » : consigner ces retours dans le
  journal, la roadmap, le backlog, les décisions et la conception, puis
  enchaîner sur la suite de la session 2 (retours, « Quand ? »,
  simulateur).

**Fait** :

- retours consignés : journal (cette entrée), `ROADMAP.md` (étape 2
  close côté relecture, étape 3 réordonnée), `BACKLOG.md`,
  `DECISIONS.md` (ordre de l'accueil, making-of structuré),
  `docs/CONCEPTION.md` (maquette de l'accueil, page making-of) ;
- aucun retour ne porte sur un chiffre : rien à vérifier à la source,
  rien à consigner dans `ERREURS.md` à ce stade. Les deux défauts
  relevés sont des défauts de conception (lisibilité), pas des erreurs
  de fond ; ils sont tracés ici et dans `DECISIONS.md`.
- deux agents lancés en parallèle (Opus) : site (accueil réordonné,
  making-of structuré, brief replié dans le journal) ; spike de sources
  de « Quand ? » (marge à la pointe, disponibilité du parc, surplus et
  écrêtement, effacements, ce que RTE dit d'une charge plate
  supplémentaire, indicateurs de marge défendables).
- l'agent du site rend son travail (tests, vérification de types, build
  et format au vert ; captures aux deux tailles, clair et sombre, et
  sans JS). Accueil : la question devient le titre visible, suivie de
  deux phrases sans chiffre, puis la carte. Making-of : décisions et
  erreurs en fiches filtrables, journal en sessions repliables, brief
  replié dans la session 1 ; le contrat des formats est testé sur les
  vrais fichiers. Claude relit les captures et reprend deux points :
  - une phrase de l'accueil disait le système « tantôt tendu, tantôt en
    excédent ». L'agent l'avait lui-même signalée comme un constat que
    la carte ne démontre pas pour « tendu », et c'est la question de
    « Quand ? ». Remplacée par « l'état du système change d'une heure à
    l'autre » ;
  - le test du contrat a trouvé une entrée d'`ERREURS.md` hors format
    (la relecture « lectrice experte » : préambule et liste au lieu des
    champs Faux et Repéré par). Claude la remet au format sans changer
    son texte : le préambule devient le champ Repéré par, la liste
    passe sous Faux ;
  - l'agent signale un défaut de la session 1 : l'ancienne page
    making-of utilisait un jeton de couleur inexistant (`--filet`), si
    bien que le filet entre sections ne s'affichait pas. Sans effet sur
    le contenu ; disparu avec la nouvelle page.
