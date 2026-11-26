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

**Agents** : 9 (7 Opus, 2 Sonnet).

**Durée / coût** : en cours.
