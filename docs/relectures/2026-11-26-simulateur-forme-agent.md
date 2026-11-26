# Simulateur : forme revue pour tenir sur un écran (rapport d'agent, 2026-11-26)

Retour de l'auteur traité : « le simulateur ne devrait pas être scrollable, la page fait enquête à
la lecture, le simulateur est noyé entre un long préambule et une longue suite. Fond data texte ok,
forme à revoir ».

**Fichiers modifiés.** `site/src/routes/simulateur/+page.svelte` et `+page.server.ts`,
`site/src/lib/simulateur/Simulateur.svelte`. Fichiers ajoutés : `site/src/lib/simulateur/sections.ts`
et `sections.test.ts`, qui découpent le texte de lecture rendu en sections, une par titre de niveau 2,
sans rien perdre ni ajouter (testé). Aucun changement dans `moteur.ts`, `phrases.ts`, `en-tete.md`,
`lecture.md`, ni dans les phrases de `Simulateur.svelte` (vérifié par une comparaison phrase à phrase
avec l'ancienne version).

**Solution retenue.** L'outil passe en tête de page, sur deux colonnes à partir de 62rem : réglages
à gauche, résultats à droite (scénario, sept tuiles titre + valeur, sources). La page s'élargit à
76rem pour mettre trois tuiles par ligne. Le reste est replié en `<details>` natifs : la raison de
chaque réglage (« Raison »), le détail de chaque tuile avec ses notes (« Détail », ou « Détail et
sources » ; un bouton les déplie tous), les définitions et heures renseignées. Le préambule
(`en-tete.md`) est un repli juste sous le titre (« Ce que fait le simulateur, et ce qu'il ne modélise
pas »), à un clic. La monotone suit l'outil, puis `lecture.md` en trois replis titrés par ses propres
titres (titres `h2` dans les `summary`) ; un lien « Lire ces résultats » sous les tuiles ouvre le
premier. Pourquoi : des replis natifs marchent sans JavaScript (la spécification veut hypothèses et
limites lisibles sans JS), au clavier, et gardent tout le texte dans la page (recherche, liens) ;
des onglets auraient caché la monotone et demandé du JS.

**À l'écran** (captures dans le dossier temporaire de session `scratchpad/simulateur/`, Chromium
sans tête, fenêtre = zone d'affichage) : 1366×768, réglages et résultats finissent à 737 px (760 px
pour un scénario 2022, 8 GW, 200 h, dont la phrase fait deux lignes) ; 1440×900, idem, avec le haut
de la monotone. 390×844 : titre, repli des limites, réglages, puis résultats (dès 845 px), monotone,
lecture ; un détail de tuile déplié prend toute la largeur.

**Tests.** `npm run check`, `npm test` (15 fichiers, 144 tests), `npm run format:check` passent dans
le dépôt. `npm run build` échoue dans le dépôt sur la page d'accueil (`docs/MESSAGE.md`, ligne
commençant par « 2024. »), modifiée par un travail parallèle hors de mon périmètre ; dans un arbre de
travail isolé (HEAD + mes seuls fichiers), les quatre commandes passent, build compris.

**Doutes.** (1) La spécification (`docs/SIMULATEUR.md`) demande les limites « en tête de page, pas
en note » et chaque hypothèse « avec sa justification » : elles sont en tête et à un clic, mais
repliées ; à valider par l'auteur, puis à reporter dans la spécification. (2) Les réserves des tuiles
(« pas une défaillance », « borne basse ») ne se voient plus sans clic : seuls le qualificatif (« au
plus », « à peu près ») et la valeur restent visibles. (3) Pas de phrase d'introduction visible :
celle du préambule fait trois lignes, et je n'ai pas voulu en écrire une nouvelle. (4) Dans une vraie
fenêtre 1366×768, la zone d'affichage fait environ 650 px : les tuiles tiennent (fin à 574 px), pas
la ligne des sources ni le bas des réglages. (5) À 76rem, la page déborde de la colonne du bandeau de
navigation : c'est voulu, mais c'est la seule page dans ce cas.
