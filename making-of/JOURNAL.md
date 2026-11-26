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
>
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
  vrais fichiers. Claude relit les captures ; trois points en sortent,
  deux repris par Claude, un signalé par l'agent :
  - une phrase de l'accueil disait le système « tantôt tendu, tantôt en
    excédent ». L'agent l'avait lui-même signalée comme un constat que
    la carte ne démontre pas pour « tendu », et c'est la question de
    « Quand ? ». Remplacée par « l'état du système change d'une heure à
    l'autre » ;
  - le test du contrat a trouvé une entrée d'`ERREURS.md` hors format
    (la relecture « lectrice experte » : préambule et liste au lieu des
    champs Faux et Repéré par). Claude la remet au format. Premier
    essai fautif : Claude avait ajouté une phrase de son cru en tête
    de Faux et laissé « Les cinq erreurs de fond : » à la fin de
    Repéré par, tout en écrivant ici « sans changer son texte »
    (repéré par la relecture adverse, consigné). Version finale : le
    texte d'origine, seulement réordonné (la phrase « Les cinq erreurs
    de fond : » et la liste sous Faux, le préambule sous Repéré par) ;
  - l'agent signale un défaut de la session 1 : l'ancienne page
    making-of utilisait un jeton de couleur inexistant (`--filet`), si
    bien que le filet entre sections ne s'affichait pas. Sans effet sur
    le contenu ; disparu avec la nouvelle page.
- relecture adverse avant publication lancée (Opus) : ouverture de
  l'accueil en lectrice experte puis en lecteur non spécialiste, et
  fidélité mécanique du making-of rendu à ses fichiers source (rien de
  perdu, tronqué ou déplacé, brief compris).
- le spike « Quand ? » rend son rapport (`docs/spike/quand.md`). La
  trouvaille principale : les indisponibilités nucléaires déclarées
  par EDF au titre de REMIT sont en accès libre (Licence Ouverte), et
  la disponibilité horaire qu'on en reconstruit retombe sur les taux
  annuels de RTE à 0,3 point près depuis 2018. Aucune série horaire
  publique de « marge » n'existe : la marge de RTE est le résultat
  d'une simulation, publiée en quelques chiffres par hiver. L'agent
  propose trois indicateurs et en écarte un (une « marge horaire »
  capacité moins charge). Deux points restent ouverts : le fuseau des
  dates REMIT, non documenté, et Flamanville 3 en 2025. Ses calculs
  n'ont été relus par personne ; ils n'entrent pas dans `docs/` tels
  quels.
- deux agents lancés en parallèle (Opus) : contre-vérification adverse
  de 17 affirmations du spike, sans accès à ses conclusions
  (`docs/spike/quand-contre-verification.md`) ; branchement des
  indisponibilités REMIT d'EDF dans le pipeline (série horaire du
  nucléaire disponible, contrôle contre les taux du Bilan électrique
  2025), avec mission de trancher le fuseau des dates et le cas de
  Flamanville 3.
- la relecture adverse rend son verdict : publiable après corrections
  (rapport : `docs/relectures/2026-11-26-accueil-making-of.md`). Les
  affirmations sur le marché sont justes, et la comparaison mot à mot
  du making-of rendu avec ses sources ne trouve rien de perdu. Un point
  de fond : l'ouverture de l'accueil affirmait « la question se joue à
  l'heure, au poste électrique et au prix », l'hypothèse du brief
  présentée comme un fait, alors que l'auteur a décidé que l'accueil
  ne pose pas de thèse. La phrase venait de la consigne de Claude à
  l'agent du site (consigné). Claude vérifie chaque point dans le code
  et les fichiers, et les arbitre : ouverture réécrite en description
  de ce que fait le site ; « carte » devient « calendrier » (après
  « poste électrique », on attendait une carte de France) ; « couleur
  écrêtée » devient « la couleur sature » ; « prix planchers » devient
  « prix à peine négatifs » ; la moyenne horaire des quarts d'heure est
  dite calcul du site ; une citation de l'auteur et un paragraphe du
  brief mal rendus sont corrigés ; la session en cours est marquée
  comme telle. L'agent du site est relancé avec son contexte pour ces
  corrections.
- l'agent du site rend les corrections. Elles ont fait apparaître un
  défaut déjà en ligne sur « Combien ? » (étages de la pyramide
  numérotés 1, 2, 3 au lieu de 3, 4, 5 ; consigné). La fidélité du
  making-of à ses sources est désormais un test de la CI. Reste au
  backlog : les sauts de ligne d'une demande citée sont fondus au
  rendu (« selon ROADMAP.md » et « retours de lecture : » sur une même
  ligne) ;
- la contre-vérification rend son rapport
  (`docs/spike/quand-contre-verification.md`) : aucun chiffre faux sur
  17, mais des pièges de sens. Le jeu EDF contient aussi des unités
  belges (vérifié par Claude dans le fichier, consigné) ; les 8 à
  10 GW de marge viennent du BP2025 et précèdent la synthèse de
  l'hiver 2026-2027, qui ne donne plus de marge en GW ; RTE n'écrit
  nulle part qu'1 GW de consommation à la pointe retire 1 GW de marge,
  et sa méthode traite différemment une charge plate et une charge
  sensible au froid ; les 3 TWh d'EnR non produites à prix négatif et
  les 0,1 TWh écrêtés à la demande de RTE se recouvrent. Le fuseau des
  dates REMIT est établi en heure de Paris par un test sur 121
  déclenchements de réacteurs. Informations transmises à l'agent du
  pipeline.
- l'agent du pipeline rend la source `edf_remit` : série horaire
  `nucleaire_disponible`, 4 nouveaux contrôles (12 au total, tous
  passés), 59 tests. Taux annuels reconstruits à +0,07 à +0,38 point
  de ceux de RTE sur 2015-2025. Le fuseau des dates est établi en
  heure de Paris par un second test indépendant, concordant avec la
  contre-vérification. Il corrige deux erreurs du spike (Fessenheim,
  attribution des dépassements à l'EPR ; consignées) et en signale
  trois de son propre code, attrapées par ses tests ou à la lecture de
  `pc check` avant tout usage. Il propose une correction manuelle de
  la donnée EDF (Golfech 1, 2020) : Claude la vérifie dans le fichier
  et la retient (registre des décisions). Claude relance `pc build`,
  `pc check` et les tests, et passe les 11 taux de RTE en
  « contre-vérifiés » dans le référentiel.
- agent lancé (Opus) : indicateurs de « Quand ? » dans le pipeline
  (`pipeline/pc/quand.py`, fonction de référence pure qui servira de
  modèle au simulateur, cas de test partagés), chiffres calculés
  produits par `pc build` dans le référentiel, chiffres de RTE cités
  à partir des citations de la contre-vérification, contrôles. Claude
  écrira le texte de l'enquête sur ces chiffres.
- l'agent des indicateurs rend `quand.json` (337 Ko), la fonction de
  référence `pc/quand.py` et 7 cas de test partagés pour le futur
  simulateur, 30 chiffres calculés produits par `pc build`, 13 chiffres
  de RTE cités (revérifiés dans les PDF), 6 contrôles de plus (18 au
  total) et 84 tests. Il signale cinq erreurs de son propre code,
  toutes attrapées avant commit. Claude relance contrôles et tests, et
  recalcule à part, sur les CSV publiés, la charge résiduelle maximale
  2022-2025 avec sa date, le nucléaire disponible non produit et la
  part tenue pour 5 GW : identiques.
