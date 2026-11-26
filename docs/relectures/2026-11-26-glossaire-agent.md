# Glossaire replié : rapport de l'agent (2026-11-26)

Agent chargé du glossaire (ROADMAP, session 4, point 6 ; BACKLOG « Glossaire replié »).
Rien n'est commité. Les définitions sont à relire avant publication (relecture adverse
« lectrice experte »), en commençant par celles listées en fin de rapport.

## Fichiers touchés

- `docs/GLOSSAIRE.md` (nouveau) : source unique, 34 entrées, format décrit en tête du fichier.
- `site/src/lib/server/glossaire.ts` (nouveau) : lecture et validation du format, résolveur des
  renvois, rendu pour `/methode`.
- `site/src/lib/server/glossaire.test.ts` (nouveau) : 11 tests (voir plus bas).
- `site/src/lib/markdown.ts` : option `glossaire` (deux retouches ciblées ; le fichier était
  modifié en même temps par un autre agent, option `citationsLigneALigne`, laissée intacte).
- `site/src/lib/server/enquetes.ts` : `rendreCorps` passe le résolveur (enquêtes, message de
  l'accueil, textes du simulateur).
- `site/src/routes/methode/+page.server.ts`, `+page.svelte` : le glossaire codé en dur (12
  entrées) est remplacé par le rendu du fichier ; les 12 définitions existantes y sont reprises
  mot pour mot, quatre complétées d'une phrase pour atteindre le minimum de deux (puissance
  appelée, fast-track, RPD, RPT).
- `site/src/app.css` : style `a.glossaire` (soulignement pointillé, mêmes jetons que les liens).
- Liens posés (balisage seul, texte inchangé, vérifié par comparaison à `HEAD` après retrait du
  balisage) : `docs/MESSAGE.md` (1), `docs/enquetes/quand.md` (14), `combien.md` (11),
  `carbone.md` (7), `site/src/lib/simulateur/en-tete.md` (4), `lecture.md` (6),
  `site/src/routes/+page.svelte` (3, en HTML : prix de gros, day-ahead, prix négatif).

## Syntaxe choisie : `[texte](glossaire:id)`

C'est un lien Markdown ordinaire avec un schéma propre. Raisons :

- le parseur reconnaît déjà `[texte](url)` ; sans l'option, un schéma inconnu est rendu en texte
  seul : aucun rendu existant ne change (making-of, LISEZMOI) et rien ne fuit en clair ;
- le test de fidélité du making-of (`texteMd`) retire déjà `[x](url)` : la syntaxe y est neutre ;
- `[[terme|id]]` aurait demandé une règle de plus dans `enLigne`, avec un risque de collision
  avec les crochets des citations caviardées (`[caviardé : …]`).

Rendu : `<a class="glossaire" href="/methode#g-id">`. Un identifiant inconnu lève une erreur au
prérendu (le build échoue) et dans les tests. Les liens de l'accueil écrits en Svelte sont
contrôlés par un test qui parcourt `site/src/**/*.svelte`.

Sur `/methode` : `<details>` natif fermé par défaut, une ancre `id="g-<id>"` par entrée ; un
`$effect` sur `page.url.hash` déplie le repli et fait défiler jusqu'au terme quand on arrive
par `#g-…` (chargement direct ou navigation interne). Sans JavaScript, la page reste lisible ;
Chrome déplie de lui-même un `<details>` visé par une ancre, d'autres navigateurs non. Comportement
dans un vrai navigateur non vérifié par l'agent (pas de navigateur dans la session) : à essayer.

## Règles posées et testées

- Format : titre `## Terme {#id}`, un paragraphe de 2 à 5 phrases, ligne `Source :` facultative
  avec un lien https ; identifiants uniques ; ordre alphabétique (`localeCompare` fr) ; ni
  `{{chiffre}}` ni directive ; renvois internes vers des entrées existantes ; 20 à 35 entrées.
- Un terme n'est lié qu'une fois par page (accueil = message + `+page.svelte` ; simulateur =
  en-tête + lecture ; enquêtes avec leurs fragments inclus).
- Les fragments partagés (`docs/enquetes/partage/`) ne portent aucun renvoi : ils vivent dans deux
  pages, et le premier renvoi d'une page ne serait plus le premier dans l'autre. Conséquence :
  « écrêtement » n'est pas lié sur `/simulateur` (sa seule occurrence y est dans un fragment).
- Les encarts « en préparation » refusent déjà tout lien : rien n'y est posé.

## Termes (34)

Adéquation, défaillance, délestage · CFE 24/7 · Charge résiduelle · Écrêtement, production
renoncée · Effacement · Facteur d'émission moyen et marginal · Fast-track · Garanties d'origine ·
Intensité carbone · Jours et heures PP (PP1, PP2) · Mécanisme de capacité, puissance certifiée ·
Monotone · MW et MWh · Poste électrique, poste source · PPA · Préséance économique (merit order) ·
Prix capté (capture price) · Prix day-ahead · Prix de gros · Prix négatif · PTF · Puissance
appelée · Puissance pré-réservée · Puissance raccordée · Puissance recherchée · Puissance réservée
· Puissance signée · REMIT · RPD · RPT · S3REnR · Services système · Solde des échanges · TURPE.

Non liés faute d'occurrence hors citation : merit order (seule occurrence dans une citation de
RTE, « ordre de préséance économique », que l'agent n'a pas voulu baliser) ; PPA, TURPE, CFE 24/7,
garanties d'origine, S3REnR (absents des pages publiées). Plages PP et puissance certifiée
n'apparaissent pas dans les textes du simulateur, seulement dans « Quand ? » (« certifiés » est
couvert par le lien « mécanisme de capacité » posé juste avant). Les phrases générées par
`phrases.ts` (résultats du simulateur) ne sont pas balisées.

## Définitions dont l'agent doute (à vérifier à la source)

1. **Jours et heures PP** : le rôle des PP1 (obligation des fournisseurs) et des PP2 (certification,
   « plus nombreux ») dans le mécanisme d'origine est écrit de mémoire, sans source primaire lue.
   Les heures 2026-2027 (7-10 h, 17-20 h), la période novembre-mars et le signalement la veille sont
   sourcés (BP2025 « Fonctionnement », note 38 p. 30 ; CRE n° 2026-43, p. 6 et note 4).
2. **Mécanisme de capacité** : « auparavant, chaque fournisseur devait détenir des garanties de
   capacité… aux jours de pointe » est de mémoire. Le reste (centralisé depuis la période
   2026-2027, enchères de RTE, courbe de demande fixée par le ministre, taxe ; volume certifié =
   disponibilité aux heures PP × coefficient de filière ; coefficients inférieurs à 1 pour
   nucléaire, fil de l'eau, stockage) est lu dans CRE n° 2026-43 (p. 3, 6) et le rapport de
   paramétrage de RTE (p. 10).
3. **CFE 24/7** : la mention de Google et du « 24/7 Carbon-Free Energy Compact » est de mémoire ;
   la phrase sur le règlement 2023/1184 (article 6, rédaction 2024/1408) s'appuie sur le
   référentiel du site (`ue_correlation_seuil_prix`).
4. **Garanties d'origine** : « sans contrainte d'heure » décrit l'usage courant (appariement
   annuel) ; le droit permet des garanties à granularité plus fine. À nuancer si la lectrice y
   voit une inexactitude.
5. **Solde des échanges** : « frontière par frontière, ils diffèrent des échanges commerciaux » est
   exact dans le principe ; non chiffré.
6. **Charge résiduelle** : l'opposition à « la charge nette courante qui ne retranche que l'éolien
   et le solaire » suppose une convention qui varie selon les auteurs.
7. **Adéquation** : la définition de la marge (« écart, en capacité, entre le parc simulé et celui
   qui respecterait exactement ce critère ») est une paraphrase de l'agent ; le critère (3 h de
   défaillance, 2 h de délestage) est lu p. 2 du BP2025 « Fonctionnement ».
8. **Services système** : FCR et aFRR rangés sous « réglage primaire » et « secondaire » ; la
   réserve tertiaire (mFRR, mécanisme d'ajustement) est volontairement laissée hors du terme.
9. **Prix négatif** : liste des causes (tarifs d'achat, contraintes techniques, cogénérations)
   donnée sans source ; S3REnR et TURPE sans source primaire liée.
10. **REMIT** : article 4 du règlement 1227/2011 (publication des informations privilégiées) et
    modification par 2024/1106 : de mémoire, liens ELI non ouverts (EUR-Lex refuse les accès
    automatisés, cf. `sources.yaml`).

## Vérifications

Depuis `site/` : `npm run check` (0 erreur), `npm test` (19 fichiers, 201 tests), `npm run
format:check`, `npm run build` (34 ancres `g-` dans `build/methode.html` ; liens : accueil 4,
« Quand ? » 14, simulateur 10, « Combien ? » 11, « Quel carbone ? » 7). Tous verts au moment du
rapport, avec le travail en cours des autres agents. `docs/enquetes/ou.md` n'existait pas encore :
aucun lien n'y est posé.
