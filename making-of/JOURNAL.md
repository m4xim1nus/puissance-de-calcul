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
- texte de « Quand ? » écrit par Claude (`docs/enquetes/quand.md`), sur
  les identifiants du référentiel. En relisant son premier jet, Claude
  retire ou source cinq affirmations tapées sans entrée : les causes de
  la crise nucléaire de 2022 (remplacées par le taux de disponibilité
  de RTE), « des centaines de scénarios », « l'essentiel du risque »
  (RTE écrit « près de 50 % », sur des plages plus étroites que celles
  du site : on prend les siennes), « la France exporte précisément à
  ces heures » (désormais un chiffre calculé), et Flamanville 3 « en
  essais » (« en montée en puissance »). Cinq chiffres de plus demandés
  à l'agent des indicateurs.
- l'agent des indicateurs livre les chiffres demandés et l'arrondi des
  valeurs publiées (la valeur non arrondie reste dans la fiche). Claude
  corrige deux phrases de son texte où un solde négatif (exportateur)
  aurait été lu « exportait −3,2 GW », puis relance l'agent du site
  avec son contexte pour la page `/quand` et ses trois graphiques
  (monotone, calendrier jour × heure, charge plate).
- l'agent du site livre `/quand` (trois graphiques, notes « calcul du
  site » avec méthode, données et valeur avant arrondi ; 99 tests). Il
  relève six phrases du texte de Claude ; Claude en corrige cinq :
  « elle ne simule rien » alors que la dernière section ajoute une
  consommation par le calcul ; une borne basse (J 2025 sans l'EPR)
  affichée comme une valeur ; « aucune vague de froid de l'ampleur de
  2012 », affirmation sans source, remplacée par une limite qui
  n'affirme rien sur la météo ; « comme en 2023 et 2024 » sans chiffre ;
  insécables entre heures et « h ». La sixième (pointe horaire plus
  basse que la pointe RTE, non chiffrée) reste qualitative.
- page `/quand` commitée, relecture adverse « lectrice experte » lancée
  (Opus) avec recalcul indépendant des chiffres clés. En parallèle,
  Claude écrit la spécification du simulateur (`docs/SIMULATEUR.md`) et
  lance un agent (Opus) pour la référence Python, le moteur TypeScript,
  la parité testée et la page `/simulateur`.
- la relecture adverse de `/quand` rend son verdict : publiable après
  corrections (rapport `docs/relectures/2026-11-26-quand.md`). Elle
  recalcule tous les chiffres clés sans écart, mais six points de fond
  portent sur ce qu'on leur fait dire. Claude vérifie à la source le
  plus grave (une contradiction prêtée à RTE, p. 16 du paramétrage du
  mécanisme de capacité : confirmé, consigné), puis réécrit le texte :
  conclusion en tête, équivalence consommation plate / marge rétablie,
  question des exportations laissée ouverte, plafonds chiffrés avec leur
  sensibilité, définitions précisées (fil de l'eau, effacements),
  nouvelle limite « le système change ». Les quatre raisonnements
  fautifs sont consignés. Les nouveaux chiffres attendent que l'agent
  du simulateur ait fini avec `pc/quand.py`.
- l'agent du simulateur rend la v1 : `simuler` dans la référence
  Python (5 cas calculés à la main, tests de propriétés), moteur
  TypeScript dont la parité est testée sur tous les cas partagés et sur
  2022 et 2025 réelles, page `/simulateur` (année, puissance appelée,
  effacement ; état dans l'adresse), CSV horaires servis par une route
  prérendue, sans copie dans le dépôt. Vérifié sur un clone propre avec
  `build.sh`. Il signale une erreur de son code attrapée par un
  parcours automatisé (adresse invalide bloquant le chargement) et des
  phrases mal accordées repérées sur captures. Commité ; non publié
  avant sa relecture adverse.
- l'agent des indicateurs produit les chiffres demandés par la relecture
  (maximum pluriannuel, plancher de 1 GW, nucléaire non produit aux
  heures chères, énergie nécessaire, production nucléaire 2025 et
  prévisions, relues par lui dans le PDF) et retire partout
  l'affirmation sur les exportations ; la parité du moteur du
  simulateur est étendue aux nouvelles sorties. Claude vérifie dans les
  données l'heure du maximum de 2018 avant d'écrire comment le système
  l'avait couvert (charbon, fioul, importations ; prix de 159 €/MWh,
  donc pas « extrêmes » comme en décembre 2022 : la première rédaction
  le disait, corrigée avant commit).
- la relecture adverse du simulateur rend son verdict : calculs justes
  (recalculés à l'identique sur 16 scénarios), fond pas encore. Il
  reprenait les erreurs de « Quand ? », spécifié avant la relecture de
  celle-ci, et ajoutait un effacement circulaire et un prix moyen qui se
  lisait comme une économie (consigné). Claude arbitre : spécification
  révisée, l'agent du simulateur relancé avec son contexte.
- l'agent du site rend les corrections des graphiques de `/quand` :
  zoom sur les 500 heures les plus tendues avec le maximum 2015-2025,
  palette des années refaite (motifs de trait pour les paires proches en
  vision daltonienne), fourchette avec et sans plancher, troisième
  panneau au-delà du maximum pluriannuel, mention « calcul du site, non
  recoupé » en clair, légende du changement d'heure rectifiée après
  vérification dans les données (éCO2mix ne publie rien sur l'heure
  répétée d'octobre), effacements retirés de ce qui « couvre » la charge
  résiduelle. Claude relit les captures.
- l'agent du simulateur rend ses corrections (138 tests du site, 100 du
  pipeline, 19 contrôles). Claude retire deux limites qu'il avait
  rédigées sans source (consommation « un peu plus forte par temps
  chaud », « déconnexions simultanées lors d'un creux de tension ») au
  profit de formulations qui n'affirment rien sur le comportement des
  data centers, et « des centaines de scénarios ». Une vérification
  des corrections, point par point contre les deux relectures, est
  lancée avant publication.
- la vérification des corrections conclut « non publiable en l'état,
  publiable après une dizaine de corrections de texte » : F1 à F6 et
  SF1 à SF6 sont corrigés, mais les corrections ont réintroduit des
  phrases fausses. Claude les vérifie dans les données (le nucléaire
  disponible non produit est nul 183 heures en 2025, dont 14 au-dessus
  de 150 €/MWh : « ne tombe jamais à zéro » était faux) et corrige :
  « pires années » affiché précisément quand on dépasse tout ce que le
  système a couvert ; deux légendes qui ramenaient l'idée d'un
  territoire inconnu ; « prix extrêmes » pour février 2018 encore dans
  une note ; « production de l'EPR non publiée à part » encore dans
  trois notes ; la p. 16 du paramétrage encore citée par le simulateur ;
  « dès quelques GW » ; accord « en les connaissant » pour une heure.
  Le froid extrême chiffré et le jargon du glossaire vont au backlog.
  Erreur consignée.
- « Quand ? » et le simulateur v1 sont poussés ensemble, après la
  vérification des corrections et le contrôle de caviardage.

**Fin de session : demande de l'auteur** (citée telle quelle) :

> pas de /cost dispo
> ok teléphone
> token mis dans un .txt dans source : mets le au bon format, au bon endroit, supprime le txt, indique ds les md, mais ne le traite pas : je ferai ça à partir des md dans une 3eme session.
> indique aussi dans backlog 2 retours qui seront traités dans la prochaine convo :
>  - maintenant que les enquête sont faites, ptetre possible de revoir l'aspect édito pour avoir un discours tranché et soutenu, ou déjà fait ? contraire à ce qui était prévu ?
>  - le simulateur ne devrait pas être scrollable, la page fait enquête à la lecture, le simulateur est noyé entre un long préambule et une longue suite. Fond data texte ok, forme à revoir
> confirme quand je peux clear

**Ce qu'elle recouvrait** :

- « ok teléphone » : la recette sur téléphone du site en ligne est
  faite par l'auteur, sans remarque ;
- jeton ENTSO-E : arrivé, déposé par l'auteur dans un fichier texte de
  `source/`. Claude vérifie qu'il a la forme attendue (identifiant de
  36 caractères), l'écrit dans `source/entsoe_token` (non versionné,
  droits restreints au propriétaire) et supprime le fichier texte. Le
  jeton n'est ni lu par le pipeline, ni testé : le branchement
  d'ENTSO-E est le travail de la session 3 ;
- « l'aspect édito » : l'accueil pose la question sans thèse, par
  décision de l'auteur, « jusqu'à ce que deux enquêtes soient faites ».
  C'est le cas : l'auteur demande s'il est temps d'écrire un discours
  tranché, et si cela contredit ce qui était prévu. Réponse : non, la
  décision du 26/11 prévoyait précisément d'écrire le message principal
  après deux enquêtes ; rien n'est encore fait. À trancher en session 3 ;
- simulateur : le fond (données, texte) convient ; la forme non. La
  page se lit comme une enquête, l'outil est pris entre un long
  préambule et une longue suite. Il devrait tenir sur un écran, sans
  défilement ;
- « confirme quand je peux clear » : l'auteur veut savoir quand le
  contexte de cette conversation peut être effacé sans rien perdre :
  quand tout est écrit dans les fichiers du dépôt et commité.

**Fait** : jeton rangé ; deux retours au backlog et à la roadmap de
l'étape 4 ; journal, roadmap et backlog à jour pour la session 3.

**Agents** : 10 lancés par Claude, tous Opus (site, relancé quatre fois
avec son contexte ; spike « Quand ? » ; relecture de l'accueil et du
making-of ; contre-vérification ; pipeline REMIT ; indicateurs, relancé
deux fois ; relecture de « Quand ? » ; simulateur, relancé une fois ;
relecture du simulateur ; vérification des corrections). Une onzième
transcription de sous-agent figure dans les fichiers locaux.

**Durée** : de 9 h 10 à 12 h 15 environ, soit à peu près 3 h de temps
réel, avec jusqu'à trois agents en parallèle.

**Coût** : non relevé (`/cost` indisponible pour l'auteur). Volumes
estimés à partir des transcriptions locales (fil principal et
11 transcriptions de sous-agents) : Opus, ≈ 1,2 M jetons produits,
≈ 216 M jetons lus en cache et ≈ 4,5 M écrits en cache. Comme en
session 1, la relecture du contexte en cache domine.

---

## Session 3 — 2026-11-26, à partir de 12 h 13 · éditorial, simulateur sur un écran, « En bref », ENTSO-E

**Demande de l'auteur** (citée telle quelle) :

> reprends à la session 3 de ROADMAP.md. en plus de ce qu'il y a déjà, ajoute un retour : il faut une 1ère section dans la page Making Of "En bref", qui donne en 1 coup d'oeil quelques infos à destination de la lectrice non dev mais quanti : outils utilisés, temps de "travail" IA, temps de travail humain, nombre tokens out, nombres "pages" écrites par moi en tout, etc vision d'ensemble. A intégrer à la session.

**Ce qu'elle recouvrait** :

- « reprends à la session 3 » : l'ordre de l'étape 4 de la roadmap
  (proposition éditoriale, simulateur sur un écran, branchement
  ENTSO-E, puis enquête carbone) ;
- « En bref » : une première section du making-of, lisible d'un coup
  d'œil par une lectrice à l'aise avec les chiffres mais pas avec le
  développement logiciel : avec quels outils le site est fait, combien
  de temps l'IA a travaillé, combien de temps l'auteur, combien de
  jetons le modèle a produits, combien de « pages » l'auteur a écrites
  au total (ses demandes et retours), et d'autres repères d'ensemble.
  Les guillemets de l'auteur (« travail », « pages ») signalent des
  mesures à définir : chaque chiffre dira comment il est compté, et
  ce qu'il ne compte pas.

**Fait** :
- deux agents lancés en parallèle : vérification d'accès à ENTSO-E
  (Sonnet) et simulateur sur un écran (Opus) ;
- **éditorial** : Claude relit les deux enquêtes et propose trois
  options (`docs/EDITO.md`) : tranchée, prudente, attendre. Réponse de
  l'auteur, citée telle quelle : *« Tranchée... mais laisser la place
  dans le backlog de la révision du message à la fin d'autres enquêtes,
  voire explicitement prudente sur les enquêtes manquantes à date »*.
  Explicitation : option A, avec un paragraphe qui dit ce que le message
  ne sait pas encore, et une révision prévue au backlog. Texte dans
  `docs/MESSAGE.md`. En le rédigeant, Claude retire de sa propre
  proposition « la France peut accueillir la vague à une condition » :
  aucune des deux enquêtes n'établit que l'énergie suffirait. Deux
  chiffres de la proposition étaient mal arrondis avant envoi à
  l'auteur (« quart à un peu plus du tiers » pour 24 à 46 %, « au plus
  la moitié » pour 52 %) ; corrigés avant qu'il la lise ;
- **« En bref »** : `pc bilan` (`pipeline/pc/bilan.py`, 5 tests) lit
  les transcriptions locales et écrit `making-of/en-bref.json`
  (agrégats seulement) ; section en tête du making-of, tuiles en trois
  groupes (temps, écriture, modèle), tableau par session, outils, et
  « comment c'est compté » replié. Le relevé de coût que Claude Code
  enregistre dans ses transcriptions donne, pour les sessions 1 et 2, un
  coût équivalent API (64 $ et 92 $) que le journal disait « non
  relevé » : ce n'est toujours pas le montant payé par l'auteur.
- **message sur l'accueil** : sous la question, titre « Ce
  qu'établissent les enquêtes, à ce jour », date et enquêtes sur
  lesquelles il repose, chiffres du référentiel avec leurs notes (même
  rendu que les enquêtes). Le garde-fou du rendu a refusé une ligne qui
  commençait par « 2024. » (elle serait devenue une liste numérotée) ;
- relecture adverse « lectrice experte » du message et de « En bref »
  lancée (Opus) avant publication.
- **simulateur sur un écran** : l'agent rend la nouvelle forme (deux
  colonnes, replis natifs ; 144 tests du site). À 1366×768, réglages et
  résultats chiffrés tiennent dans l'écran (fin de l'outil à 737 px ;
  dans une vraie fenêtre, environ 650 px utiles, la ligne des sources et
  le bas des réglages passent sous la ligne de flottaison). Son build
  échouait sur l'accueil, à cause du « 2024. » du message, corrigé
  entre-temps ; tout passe sur l'ensemble des changements. Claude relit
  les captures et révise la spécification (limites à un clic au lieu
  d'être dépliées) ;
- **question de l'auteur en cours de session** (citée telle quelle) :
  *« en relecture, dans "ce que le calcul ne dit pas", on prévoit de
  sourcer l'info précise pour la prendre en compte ? De l'estimer
  nous-mêmes, et/ou de laisser l'utilisateur changer cette hypothèse ?
  Du front avec toogle on/off ? sur ce point, ne fais rien, dis moi
  avant de changer la roadmap & implémenter »*. Explicitation : pour
  chaque limite listée à la fin de « Quand ? », l'auteur demande si on
  compte la lever, et comment (chiffre publié, estimation du site,
  réglage dans le simulateur), avant tout changement. Claude propose
  trois niveaux et un plan limite par limite ; réponse : *« ok pour ta
  reco, mets à jour roadmap et backlog »*. Roadmap (point 3 de
  l'étape 4), backlog et décisions mis à jour ; rien d'implémenté.
- **relecture adverse du message et de « En bref »** (27 points) :
  message non publiable en l'état ; « En bref » publiable après trois
  corrections de fond. Claude vérifie les points dans les sources avant
  de corriger : les trois citations d'adéquation du BP2025 sont exactes
  (*Fonctionnement*, p. 26 et 28) ; le point 17 (relevé de coût cumulé
  d'une conversation à l'autre) est réfuté (session 2 : 1 211 534 jetons
  Opus produits au relevé, 1 211 059 dans ses transcriptions). Erreur de
  fond consignée. Message réécrit à partir de la proposition de la
  relectrice. Sa conclusion change : la pointe d'hiver reste la
  contrainte nationale, mais RTE ne voit pas de besoin de moyens
  nouveaux d'ici 2035 dans la trajectoire lente. Le texte sera soumis à
  l'auteur. « En bref » corrigé (décisions sans double compte, libellés,
  rattachement des conversations, dates sans horaires, recoupement
  automatique du relevé de coût, textes du site séparés des rapports).
  La relectrice vérifie les corrections ;
- **ENTSO-E, accès** (agent Sonnet, `docs/spike/entsoe-acces.md`) : le
  jeton fonctionne. Prix day-ahead FR et voisins, production par
  filière, charge et flux physiques depuis 2015 ; capacités d'échange
  prévues seulement sur certaines frontières (rien pour FR↔BE et
  FR↔DE-LU, le flow-based Core n'est pas servi par cette API). Prix FR
  identiques à energy-charts sur deux semaines testées ; charge à
  −1,6 % d'éCO2mix sur une semaine de 2019, à +0,26 % en 2026, écart non
  expliqué. Claude vérifie que le jeton n'apparaît dans aucun fichier du
  dépôt. Branchement dans le pipeline confié à un agent Opus ;
- **vérification des corrections** (même agent) : « En bref » publiable ;
  message publiable après trois corrections, dont deux venues de la
  proposition de la relectrice elle-même (une énergie comparée à une
  puissance, une borne mal construite) et une conclusion qui allait
  encore au-delà de RTE. Corrigé, points de forme appliqués, erreur
  consignée ;
- **demande de l'auteur en cours de session** (citée telle quelle) :
  *« j'imagine le "En bref" du making-of comme une recette de
  cuisine : - Ingrédients : ordi, compte github, compte cloudflare, compte
  Antrhopic, Claude Code, Internet pour taper les données - Recette :
  xxh de cuisson (temps session, avec toutes les infos que tu as
  préparé) dont xxmin de cuisine (message de ma part de lancement,
  commentaires, tranchage + actions manuelles sur github+cloudflare) tu
  devrais pouvoir réutiliser ce que tu as fait »*. Explicitation : même
  contenu chiffré, mis en forme de fiche recette ; « cuisson » = temps
  actif des sessions, « cuisine » = la part de l'auteur, y compris ce
  qu'il fait hors conversation (comptes GitHub et Cloudflare). Fait :
  ingrédients, temps (cuisson, dont préparation par l'auteur, feu des
  modèles, commandes), étapes par session, valeurs nutritionnelles
  (jetons, coût), ce que ça donne. Les actions hors conversation ne se
  mesurent pas : elles sont listées d'après le journal
  (`making-of/actions-auteur.json`), et leurs minutes seront déclarées
  par l'auteur ;
- deux questions à l'auteur. Message révisé : *« Publier
  (Recommandé) »*. Minutes hors conversation, réponse citée telle
  quelle : *« Je tape vite, j'ai vraiment lu en diagonale, je maitrise
  bien les actions gh & cloudflare à faire : fais une estimation, même à
  l'arrache, sans ajouter des notes de bas de page sur ce chiffre,
  estime le sans explication sur le site »*. Claude estime 15, 20 et
  10 min (sessions 1 à 3), affichées « estimé » sans autre note ; la
  phrase de méthode déjà en place, qui disait « déclarée par l'auteur »,
  dit désormais « estimée » ;
- **ENTSO-E branché** (agent Opus, `docs/spike/entsoe-pipeline.md`) :
  410 fichiers, 26 min au premier passage, 3 min en incrémental ;
  `pc check` passe à 26 contrôles, `pytest` à 147 tests. Prix FR
  identiques à energy-charts de 2015 à 2026. Charge ENTSO-E sous
  éCO2mix (−0,4 à −2,4 % selon les années, hypothèse : temps réel non
  révisé). Biais du solde des flux non expliqué. Décalage d'une heure de
  la charge et de la production FR dans ENTSO-E en 2023-2024, que Claude
  vérifie dans les données. Licence vérifiée par Claude dans les PDF
  d'ENTSO-E : CC BY 4.0 pour les flux et capacités seulement. Erreurs
  de l'agent consignées ;
- **question de l'auteur** (citée telle quelle) : *« sache que si les
  licences de republication, pour entsoe comme pour d'autres sources,
  bloquent tes avancées, on peut facilement envisager de passer le site
  entier derrère un mdp, que je transmettrai à la lectrice. ça
  débloquerait des analyses ? Ne modifie rien au plan en cours, je veux
  juste ton pov là dessus »*. Réponse de Claude : non. Les sources
  branchées sont libres ; un mot de passe ne lève pas le droit du
  producteur de base de données ni un contrat qui interdit la
  communication à un tiers ; ce qui manque, ce sont des données qui
  n'existent pas ; et le dépôt public rendrait le mot de passe inutile.
  Recours proposés si un jeu le justifie un jour : agrégats, lien,
  autorisation, annexe privée en dernier ressort. Plan inchangé ;
  l'auteur : *« ok, continue le plan »* ;
- **limites de « Quand ? »** (point 3 de la roadmap) : agent Opus
  lancé pour le froid extrême (pointe record et gradient de
  thermosensibilité sourcés chez RTE, réglage « vague de froid » dans le
  simulateur), l'écrêtement (borne calculée par le site) et le plancher
  nucléaire en réglage ; relecture adverse prévue avant publication ;
- **question de l'auteur** (citée telle quelle) : *« ça fait donc 2
  enquêtes bridées par la licence ? Possible que ces enquêtes soient
  cachées derrière un mdp perso juste pour moi : le site reste top en
  public, mais avec le mdp il va plus loin ? Où en fait, ce qu'on rate
  avec pieds nuage et prix/production/consommation est négligeable ? »*.
  Explicitation : « pieds nuage » désigne la carte « Le nuage était sous
  nos pieds ». Réponse de Claude : aucune enquête n'est bridée. Pour le
  carbone, on publie des résultats calculés à partir des séries
  ENTSO-E, pas les séries brutes des voisins. Pour « Où ? », les sources
  primaires de la carte sont publiques, on perd du temps de collecte, pas
  du contenu. Un usage réservé à l'auteur est déjà possible en local,
  sans mot de passe. L'auteur : *« ok, choix compris & validé, continue
  le plan »* ;
- **spike carbone** lancé (agent Opus, `docs/spike/carbone.md`) :
  état de l'art moyen / marginal, méthodes faisables avec éCO2mix et
  ENTSO-E, prototypes jetables, proposition d'indicateurs compatibles
  avec la licence (agrégats seulement) ;
- **spike carbone rendu** (`docs/spike/carbone.md`, non relu de façon
  adverse) : aucun facteur marginal français récent publié ; méthode
  proposée : un plancher mesuré en France (0,06 à 0,10 tCO2eq/MWh pour
  1 MW de plus en 2023-2025, selon le spike, à vérifier) et des cas
  bornés pour les exportations perdues ; les émissions chez les voisins
  ne sont pas robustes (trois méthodes, de 0,08 à 0,90 t/MWh). Il signale
  que la disponibilité nucléaire déclarée par EDF contient des arrêts
  « pour modulation ». Claude le vérifie dans le fichier d'EDF : c'est
  exact, et cela touche « Quand ? », déjà publiée (erreur consignée,
  correction inscrite en priorité à la roadmap) ;
- **limites de « Quand ? » rendues** (agent Opus,
  `docs/relectures/2026-11-26-limites-agent.md`) : pointe record de
  février 2012 (102 098 MW) et gradient de 2 400 MW/°C saisis depuis
  RTE ; réglage « froid supplémentaire » appliqué aux 7 jours les plus
  tendus de l'année observée ; écrêtement estimé (5,8 GW en moyenne aux
  heures à prix négatif de 2025, borne haute) ; plancher nucléaire
  réglable de 0 à 3 GW. Doute signalé par l'agent : à 8 °C de froid
  supplémentaire, la consommation maximale dépasse le record de 2012
  dans 7 années sur 11 (double compte du froid déjà présent, gradient
  linéaire). Non publié : relecture adverse à venir, commune avec la
  correction des arrêts pour modulation, confiée à un agent Opus sur les
  mêmes fichiers ;
- **arrêts pour modulation** (agent Opus,
  `docs/relectures/2026-11-26-modulation-agent.md`) : 407 événements
  identifiés (règle testée), variante J_r et 88 chiffres ajoutés, aucun
  chiffre publié modifié, « au plus » requalifié dans « Quand ? », le
  simulateur, les notes et le graphique ; 29 contrôles, 185 tests du
  pipeline, 173 du site. Claude recoupe avec son estimation (10,4 contre
  ≈ 10 TWh en 2024) et requalifie lui-même le message d'accueil (« au
  plus 52 % selon la disponibilité déclarée par EDF ; 58 % en
  réintégrant les arrêts pour modulation »). Deux erreurs de plus
  consignées (note des exports, décompte du spike) ;
- **relecture adverse des limites et de la modulation**
  (`docs/relectures/2026-11-26-limites-modulation.md`) : publiable après
  trois corrections de fond. Repère de froid démenti par sa source, arrêts
  longs réintégrés comme réversibles, tournure de l'accueil. Claude
  vérifie les deux premiers à la source. Erreur consignée. Corrections
  renvoyées à l'agent de la modulation ; l'accueil est corrigé par
  Claude ;
- **corrections et vérification** : l'agent de la modulation traite
  F1, F2 et la forme. Les arrêts courts pour modulation (moins de 7
  jours, sans mention du combustible) sont réintégrés, les longs
  retranchés : J_r 2025 = 33,0 TWh, part 5 GW 55 % (43 % avec le
  plancher). Les repères de froid sont exprimés en consommation (5,5 °C
  de froid supplémentaire pour atteindre 100 GW en 2025). Claude réécrit
  le paragraphe d'accueil (F3). Vérification des corrections par la
  relectrice : publiable après une dernière correction, « relèvent de la
  gestion du combustible » écrit comme un fait alors que personne n'a lu
  les messages d'EDF. Claude la fait partout (sources, phrases du
  simulateur, notes générées), relance `pc build` : 29 contrôles,
  187 tests du pipeline, 173 du site. Un champ « Révision » ajouté par
  Claude à une erreur du registre cassait son format imposé, et le test
  de fidélité l'a vu : fondu dans « Correction » ;
- limites et correction des arrêts pour modulation **publiées**
  (commit `0d1f513`, en ligne vérifié). Relecture adverse du spike
  carbone lancée (agent Opus), préalable à l'écriture de l'enquête ;
- **retours de l'auteur sur le simulateur** (cités tels quels, avec
  deux captures) : *« continue, mais lance un ss agent pour régler 1
  point d'UIUX sur le simulateur : [captures] : passer d'un profil plat
  nul à non nul ajoute une ligne dans le sstitre de résultats, ce qui
  décale tout, pas agréable. Par ailleurs, pas de distinction claire
  visuellement entre hypôhtèses et résultats (en haut à droite ET tout
  en bas) Par ailleurs, le simulateur déborde en haut/bas : pas possible
  de le repenser pour se régler en pleine page non scrollable sur
  desktop ? Expérience testée vite fait sur le mobile, pas pratique du
  tout non plus (3 hauteur d'écran, donc pas de visibilité de l'output
  quand on touche aux hypothèses... mais ptetre plus difficile que pour
  le desktop, je laisse le ss agent et toi régler ça) »*. Explicitation :
  aucun réglage ne doit faire bouger la mise en page ; hypothèses et
  résultats, graphique compris, doivent se distinguer d'un coup d'œil ;
  sur desktop, l'outil entier tient dans la fenêtre sans défilement ; sur
  téléphone, l'effet d'un réglage doit rester visible. Agent Opus lancé,
  fond inchangé ;
- **relecture adverse du spike carbone** : chiffres recalculés à
  l'identique, lecture causale non établie (8 points de fond). Claude
  vérifie dans le spike le recoupement annoncé (démenti par son propre
  tableau) ; erreur consignée, spike annoté. Question à l'auteur sur le
  périmètre de l'enquête, réponse : *« Courte d'abord (Recommandé) »* ;
- **simulateur, UX** (agent Opus, `docs/relectures/2026-11-26-simulateur-ux-agent.md`) :
  phrase du scénario de hauteur fixe, sous les réglages ; réglages dans
  un panneau teinté, résultats et graphique sur le fond de page ; sur
  ordinateur, page sans défilement aux trois tailles testées, textes
  longs dans une notice latérale ; sur téléphone, réglages collés en
  haut en onglets, résultats et graphique visibles pendant qu'on règle ;
- simulateur pleine page **publié** (commit `fdb6a77`) ; Claude relit
  les captures (ordinateur et téléphone, clair et sombre) et corrige un
  renvoi devenu faux (« se règlent ci-dessous »). Enquête carbone courte
  confiée à un agent Opus, d'après le plan minimal de la relecture ;
- **enquête carbone courte rédigée** (agent Opus,
  `docs/relectures/2026-11-26-carbone-agent.md`) : intensités moyennes
  calculées depuis éCO2mix, ce que disent les institutions (sources
  relues par l'agent), encart « en préparation » sur le facteur
  marginal ; 48 chiffres ajoutés, aucun modifié ; 32 contrôles, 201 et
  184 tests. Une erreur de double arrondi repérée par l'agent lui-même,
  consignée. Claude remarque que la restriction par source du contrôle
  des chiffres « orphelins » laisse un trou pour une troisième source ;
  relecture adverse lancée ;
- **relecture adverse de l'enquête carbone**
  (`docs/relectures/2026-11-26-carbone.md`) : publiable après
  corrections ; citations exactes et non coupées, intensités recalculées
  à l'identique. Cinq points de fond, dont le rapport RTE-ADEME de 2020
  que la page oubliait. Claude relit ce rapport dans le PDF de RTE
  (p. 208-209) avant de corriger. Erreur consignée, corrections
  renvoyées à l'agent de l'enquête ;
- corrections de l'enquête carbone faites par l'agent (33 contrôles,
  202 et 185 tests), vérification lancée. Question à l'auteur sur la
  suite, réponse : *« Publier, suite réduite (Recommandé) »* : le calcul
  « si… alors » est abandonné. Le test de taille des exports, qui ne
  comptait qu'une partie des fichiers et allait casser dans quelques
  jours, porte désormais sur tout `data/export/` avec un budget de 20 Mo
  (décision de Claude) ;
- vérification des corrections de l'enquête carbone : publiable
  après retouches de forme. Claude les fait : le coefficient de 0,36 du
  règlement 2024/1408 devient un coefficient sans dimension (« 0,36 fois
  le prix d'un quota ») au lieu d'une valeur en tCO2eq/MWh qui se lisait
  comme un facteur d'émission ; le maximum de 58 g de RTE est dit « sans
  nommer la série » ; une phrase non établie sur la Corse est corrigée ;
  la page du JO est corrigée. 33 contrôles, 202 et 185 tests. **« Quel
  carbone ? » publiée** ;

**Fin de session : demande de l'auteur** (citée telle quelle) :

> je vais clore la session. Avant cela, d'accord pour dire que la session 4 sera sans doute la dernière avant partage du lien à la lectrice ?
> Si oui, avant la fin de cette session, clarifie la backlog & la roadmap en ce sens.
> Si oui, en fin de session (après le Ou & co), il faut revoir
>  - l'accueil, qui doit être bien plus attrayant et punchy. Là, c'est un titre, un "article" de 2 pages avec référence d'entrée de jeu, 2 paragraphes sur la raison d'être du site, 1 graphe sorti de nulle part, et des blocs d'enquête. Peut etre partir de 1 hot take chiffré par enquête avec lien vers l'enquête complète, un takeaway bien plus compact, la data viz direct d'un (ou plusieurs graphiques ? ou aucun ?), et pourquoi pas un texte plus long de résumé, mais secondaire par rapport à un acceuil qui doit donner envie de continuer la lecture, doit déjà impacter sur le contenu & le contenant.
>  - making of / Journel / Détail : possible de faire un peu plus clair/digeste, sans répétition par rapport à ce qu'il y a déjà sous Session (genre durée, agents, etc)
> Ces 2 points sont à mettre au backlog et à traiter à la session suivante. Go dernière intervention avant clear

**Ce qu'elle recouvrait** :

- « la dernière avant partage » : la session 4 prépare l'envoi du lien
  à la lectrice ; ce qui ne sert pas ce partage attend. Claude est
  d'accord, à condition d'y tenir la liste : « Où ? », message révisé,
  accueil, making-of, glossaire et « À toi » (exigences du brief),
  relecture finale de tout le site ;
- « Où & co » : l'enquête courte « Où ? » et ce qui reste avant le
  partage, puis l'accueil et le making-of en fin de session 4 ;
- « hot take » : un chiffre fort par enquête, qui donne envie de lire ;
  « takeaway » : le message à retenir, plus compact que l'actuel ;
- « Détail » du journal : le texte déplié de chaque session répète des
  informations que son en-tête affiche déjà.

**Fait** : backlog trié (items de la session 3 cochés, onze items
rangés en session 4, dont les deux retours ci-dessus) ; roadmap :
étape 5, « session 4, dernière avant l'envoi du lien », ordre de
travail et liste de ce qui attend après l'envoi ; relevé « En bref »
refait.

**Agents** : 13 lancés par Claude (11 Opus, 1 Sonnet, 1 de lecture de
pages web), dont 5 relancés avec leur contexte pour des corrections ou
des vérifications : accès ENTSO-E, simulateur sur un écran, relecture du
message et de « En bref », pipeline ENTSO-E, licence ENTSO-E, limites
de « Quand ? », spike carbone, arrêts pour modulation, relecture des
limites et de la modulation, relecture du spike carbone, interface du
simulateur, enquête carbone, relecture de l'enquête carbone. Le relevé
« En bref » compte 16 transcriptions d'agents distincts (certains
agents en lancent eux-mêmes).

**Durée** : de 12 h 13 à 18 h 25 environ, soit à peu près 6 h de temps
réel, avec jusqu'à trois agents en parallèle.

**Coût** : non relevé à la clôture. Claude Code n'écrit le relevé de
coût d'une conversation qu'à sa fermeture ; `pc bilan`, lancé au début
de la session 4, le reprendra. Jetons produits d'après les seules
transcriptions, Haiku exclu : ≈ 1,7 M pour Opus, ≈ 0,2 M pour Sonnet.

---

## Session 4 — 2026-11-26, à partir de 18 h 43 · « Où ? », message révisé, accueil, glossaire, « À toi », relecture finale

**Demande de l'auteur** (citée telle quelle) :

> reprends la session 4 de ROADMAP.md, go

**Ce qu'elle recouvrait** : l'ordre de l'étape 5 de la roadmap, dernière
session avant l'envoi du lien à la lectrice : relevé « En bref » et
contrôle REMIT, enquête courte « Où ? », message principal révisé,
accueil refait, making-of plus digeste, glossaire, onglet « À toi »,
relecture finale de tout le site.

**Fait** :

- relevé « En bref » refait (`pc bilan`, 4 sessions) ; `pc download
  edf_remit` relancé : l'historique d'EDF n'a pas changé en ligne
  (dernière publication le 07/09/2026), la liste courante remonte au
  28/08 : recouvrement de 10 jours, contrôle de jonction au vert. Le
  risque d'un trou reste pour début décembre si EDF ne republie pas son
  historique. `pc build` met à jour la fin de 2026, 33 contrôles sans
  échec ;
- enquête « Où ? » confiée à un agent Opus, glossaire à un autre agent
  Opus, en parallèle ;
- **making-of** (Claude) : le « Détail » de chaque session est découpé
  en parties titrées (« Ce qu'elle recouvrait », « Fait »…) ; Durée,
  Agents et Coût n'y gardent que ce qui suit leur première phrase, déjà
  dans l'en-tête, et disparaissent s'il n'y a rien de plus ; les
  demandes citées gardent leurs retours à la ligne. Le test de fidélité
  aux fichiers source est adapté : il recompose chaque session dans
  l'ordre du fichier, en-tête compris, et vérifie mot à mot ;
- **onglet « À toi »** (Claude) : cinq missions, de la courbe Linky à la
  chasse aux erreurs du site, chacune avec ce qu'il faut demander et ce
  qu'il faut vérifier soi-même ; texte dans `docs/A-TOI.md`, rendu par
  la page ;
- **glossaire** (agent Opus, `docs/relectures/2026-11-26-glossaire-agent.md`) :
  34 termes dans `docs/GLOSSAIRE.md`, source unique, rendus repliés sur
  « Méthode » avec une ancre par terme ; renvois en lien `glossaire:id`
  posés à la première occurrence sur l'accueil et les enquêtes, sans
  changer un mot du texte ; un identifiant absent fait échouer le
  build. L'agent signale cinq définitions écrites en partie de mémoire
  (jours PP, CFE 24/7, garanties d'origine, REMIT, S3REnR) : elles
  passeront par la relecture finale ;
- **« Où ? »** rédigée (agent Opus, `docs/relectures/2026-11-26-ou-agent.md`) :
  ce qui manque pour situer l'accueil (capacité en soutirage par poste,
  coordonnées des postes, registre des sites) et ce qui est publié
  malgré tout (totaux régionaux, sites de l'État, zones d'accueil
  mutualisées, règle de la file d'attente en refonte) ; 15 sources,
  13 chiffres, aucun chiffre existant modifié. L'agent signale que le
  bilan semestriel de RTE de juillet 2026 pourrait rendre daté le total
  de 18 GW réservés cité partout sur le site ; une erreur de son
  brouillon, corrigée par lui avant rendu, est consignée. Relecture
  adverse lancée, avec la vérification de ce point ;
- **message principal, version 2** (Claude, `docs/MESSAGE.md`) : trois
  sections contrôlées par le site, « À retenir » (quatre points),
  « Le message en détail » (la version 1, plus deux paragraphes sur le
  carbone et le poste électrique, et la liste des questions ouvertes
  mise à jour) et « Ce qui a changé » (une entrée datée par version).
  Aucun chiffre ni aucune conclusion de la version 1 ne change ;
- **accueil refait** (Claude) : la question et l'hypothèse du site,
  dite comme telle ; « À retenir » ; une carte par enquête avec un
  chiffre fort tiré du référentiel (champ `accroche` du front matter de
  chaque enquête, sources repliées sous le chiffre) ; le calendrier des
  prix, introduit par une phrase qui dit pourquoi regarder heure par
  heure ; le message complet replié en bas. Les notes sont numérotées
  dans l'ordre de lecture sur toute la page (test). Vérifié par captures
  d'écran, bureau et téléphone : un chiffre à unité longue débordait de
  sa carte, corrigé ;
- **méthode** (Claude, backlog) : la liste des sources compte aussi
  celles que les pages citent sans en tirer de chiffre (dont le rapport
  RTE-ADEME de 2020) ; « Quel carbone ? » précise que la Base Carbone de
  l'ADEME est aujourd'hui intégrée à sa Base Empreinte. Le point EU ETS
  du même item (seuils « dynamiques », baisse annuelle du seuil
  d'invalidation) demande de relire le texte du Conseil : confié à la
  relecture finale ;
- relectures finales lancées en parallèle (deux agents Opus) :
  « lectrice experte » sur la cohérence de tout le site et ce qui est
  nouveau aujourd'hui (message, accroches, glossaire, « À toi »),
  « lecteur non spécialiste » sur l'accueil ;
- relecture « lecteur non spécialiste » de l'accueil
  (`docs/relectures/2026-11-26-accueil-non-specialiste.md`, 11 points) :
  deux contresens induits par la page (« le surplus ne suffit pas » lu
  comme un manque de surplus ; 18 GW réservés comparés aux 8 à 10 GW de
  marge) et des cartes arrivées trop bas, qui répétaient « À retenir ».
  Corrigé par Claude : « À retenir » devient un paragraphe, les cartes
  portent le détail ; la mise en garde « n'engage pas à consommer » suit
  le chiffre de 18 GW ; chapeau explicite ; une phrase de lecture du
  calendrier (vérifiée sur les prix de 2025 : heures négatives surtout
  de 10 h à 17 h, d'avril à septembre ; les 500 heures les plus chères
  surtout en janvier-février, le matin et le soir) ; carte du simulateur
  ouverte sur 5 GW ; deux entrées de glossaire (consommation plate,
  nucléaire disponible non produit, vérifiée contre le calcul de
  `pc/quand.py`). Proposition retenue en partie : fusionner « À retenir »
  et les cartes (décision de forme, Claude) ;
- relecture adverse de « Où ? » (`docs/relectures/2026-11-26-ou.md`) :
  publiable après corrections ; citations exactes, constat central
  tenu (carte des zones favorables du schéma décennal non parue ; pas
  de capacité en soutirage poste par poste sur le réseau existant),
  mais trois constats d'absence faux (Toprac, Cartostock, capacités
  d'accueil des zones de mutualisation de RTE) et deux zones chiffrées
  avec une page périmée. Claude vérifie à la source (pages de RTE,
  fichier du 10/11/2026 lu ligne à ligne), consigne l'erreur, corrige
  le message et l'accueil qui la reprenaient, et renvoie les corrections
  de la page à l'agent rédacteur. Les 18 GW de « Combien ? » ne sont
  pas dépassés : le bilan semestriel de RTE les recoupe ;
- relecture finale « lectrice experte » (`docs/relectures/2026-11-26-finale-experte.md`) :
  envoyable après corrections ; les valeurs reprises d'une page à
  l'autre sont toutes identiques, les recalculs du message bouclent ;
  cinq points de fond, tous dans des textes courts qui coupaient du
  contexte (accroches, « À retenir », « À toi »), et douze de forme.
  Claude vérifie à la source (texte du Conseil 14944/26, délibération
  CRE n° 2026-43, rapport de paramétrage de RTE, note de RTE de juin
  2026, fichiers servis), consigne l'erreur et corrige : la carte
  « Quand ? » donne la fourchette 52 % à 55 % au plus, avec ce qui la
  fait varier ; « À retenir » rappelle que RTE, data centers compris, ne
  trouve pas de besoin de moyens nouveaux d'ici 2035 en trajectoire
  lente ; « À toi » corrige une unité (Wh, pas kWh) et un fichier de
  prix inexistant ; glossaire, paragraphe EU ETS, critère de sécurité
  d'approvisionnement, page Méthode (trois producteurs) et état des
  sites fast-track en juin 2026 corrigés ; trois points au backlog ;
- vérification des corrections, par les deux relecteurs : « Où ? »
  publiable (trois retouches de forme, faites : la file d'attente n'est
  publiée que par région et par zone ; des zones encore à l'étude ;
  accroche datée de 2025) ; site envoyable après trois retouches, dont
  une **erreur nouvelle de Claude** sur l'accueil (« maximum de
  consommation » pour « maximum de charge résiduelle » sur la carte du
  simulateur), consignée et corrigée ; « Ce qui a changé » dit désormais
  qu'une conclusion de la version 1 est corrigée (zones de
  mutualisation) ; page Méthode (trois producteurs, ligne EDF) ; renvoi
  à la délibération de la CRE dans le glossaire. 33 contrôles, 202 et
  204 tests, build ; site publié.

**Agents** : 5 lancés par Claude, tous Opus, dont 3 relancés avec leur
contexte pour des corrections ou des vérifications : « Où ? »
(rédaction puis corrections), glossaire, relecture adverse de « Où ? »,
relecture finale « lectrice experte », relecture de l'accueil
« lecteur non spécialiste ».

**Durée** : de 18 h 43 à 19 h 40 environ, soit à peu près 1 h de temps
réel, avec jusqu'à trois agents en parallèle.

**Coût** : non relevé à la clôture ; `pc bilan`, lancé au début de la
session suivante, le reprendra.

**Pour l'auteur, avant d'envoyer le lien** : relire l'accueil et
« Où ? » ; une question reste ouverte, qu'on ne tranche qu'en
demandant à RTE : la carte des zones favorables du schéma décennal
existe-t-elle ? (« Où ? » dit « à notre connaissance ».)

**Après la session** (même jour) : l'auteur, après relecture du site
en ligne : « ok il est temps d'envoyer le lien du site, merci ! ». Le
lien part à la lectrice ; la suite du travail attend ses retours
(roadmap, « Après l'envoi »).

**Après l'envoi** (même jour) : l'auteur signale « un seul défaut : le
surlignage jaune gache la lecture en sombre » (chiffres forts des
cartes de l'accueil). Le surlignage devient un soulignement épais de la
même couleur, lisible dans les deux modes ; vérifié par captures, clair
et sombre.
