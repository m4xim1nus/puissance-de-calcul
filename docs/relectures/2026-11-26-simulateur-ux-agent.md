# Simulateur : mise en page en pleine fenêtre, stabilité, hypothèses et résultats distingués, téléphone (rapport d'agent, 2026-11-26)

Retours de l'auteur traités (captures en thème sombre, ordinateur, 2019, 2,5 GW, effacement 0 puis
24 h) :

> passer d'un profil plat nul à non nul ajoute une ligne dans le sstitre de résultats, ce qui décale tout, pas agréable.
> Par ailleurs, pas de distinction claire visuellement entre hypôhtèses et résultats (en haut à droite ET tout en bas)
> Par ailleurs, le simulateur déborde en haut/bas : pas possible de le repenser pour se régler en pleine page non scrollable sur desktop ?
> Expérience testée vite fait sur le mobile, pas pratique du tout non plus (3 hauteur d'écran, donc pas de visibilité de l'output quand on touche aux hypothèses... mais ptetre plus difficile que pour le desktop, je laisse le ss agent et toi régler ça)

**Fichiers modifiés.** `site/src/lib/simulateur/Simulateur.svelte` (mise en page, notice, pupitre du
téléphone ; calcul inchangé), `site/src/lib/simulateur/MonotoneAvantApres.svelte` (n'utilise plus
le cadre partagé `Figure` : en-tête compact, tracé à la hauteur restante),
`site/src/routes/simulateur/+page.svelte`, `site/src/app.css` (deux jetons : `--pupitre`,
`--pupitre-bord`, clair et sombre), `docs/SIMULATEUR.md` (deux passages qui décrivaient la forme).
Ajoutés : `site/src/lib/simulateur/TableauMonotone.svelte` (le tableau de données du graphique, sorti
du graphique pour aller dans la notice) et `site/src/lib/simulateur/rangs.ts` (recherche de rang,
partagée par les deux). Rien dans `moteur.ts`, `phrases.ts`, `etat.ts`, les `.md`, `docs/enquetes/`,
`making-of/`, `pipeline/`. Toutes les phrases de l'ancien `Simulateur.svelte` et les sous-titre,
remarques et note du tableau de l'ancien graphique sont reprises mot pour mot (vérifié par une
comparaison phrase à phrase avec `HEAD`) ; les qualificatifs (« au plus », « à peu près ») et la
seconde valeur (« disponibilité déclarée par EDF ; … ») restent visibles avec la valeur.

## Ce qui ne va pas, et ce qui est fait

### 1. Un réglage faisait sauter la mise en page

**Problème.** La phrase du scénario, en tête des résultats, passe d'une à trois lignes selon les
réglages (effacement, froid) ; tout ce qui est dessous descend. Même effet, moins visible : la ligne
des tuiles dont la seconde valeur change de longueur, l'apparition de la tuile « Consommation horaire
maximale » avec le froid, et le remplacement de tout le bloc par « Chargement… » quand on change
d'année.

**Solution retenue.**
- La phrase du scénario sort des résultats et passe sous le pupitre, titrée « Scénario appliqué à
  l'année » : c'est la traduction des réglages dans l'année (seuil d'effacement, dates de l'épisode
  de froid), à sa place entre ce qu'on règle et ce que le calcul rend. Sa hauteur est réservée par un
  **gabarit** invisible (`aria-hidden`, `visibility: hidden`) posé dans la même case de grille : la
  phrase la plus longue possible (500 h d'effacement, froid, épisode à cheval sur deux années). La
  case a donc toujours la hauteur du pire cas, à chaque largeur, sans calcul en JavaScript.
- Tuiles à hauteur fixe : titre sur deux lignes réservées, valeur sur une ligne (`nowrap`, chiffres
  tabulaires), seconde valeur réservée sur la tuile du nucléaire, qu'elle soit là ou non (« — » quand
  X = 0). Les tuiles d'une rangée prenant la hauteur de la plus haute, la réserve vaut pour la
  rangée. La huitième tuile (froid) remplit une case vide de la deuxième rangée : rien ne bouge.
- Pendant le chargement d'une autre année, les résultats précédents restent en place, atténués
  (`aria-busy`), et une ligne d'état dit « Chargement des séries de 2019… » dans l'en-tête des
  résultats. Avant le premier calcul, des tuiles vides de même gabarit tiennent la place.

**Mesure.** Positions et hauteurs de tous les blocs relevées dans la page, sans rechargement, sur la
séquence : 2019 et 2,5 GW, effacement 0 → 24 h, froid 0 → 4 °C, X → 0, X → 20 GW, année → 2015,
année → 2022, effacement 500 h et froid 12 °C. À 1366×768, 1440×900, 1920×1080, 390×844 et
360×740 : **aucune position ni hauteur ne change** (pupitre, scénario, chaque tuile, graphique,
sources), aucune valeur ne déborde de sa tuile.

**Alternatives écartées.** Garder la phrase en tête des résultats avec une hauteur réservée (essayé :
trois lignes réservées à 1366 px, prises au graphique) ; la tronquer ou la faire défiler (perte de
texte) ; mesurer la phrase en JavaScript (fragile, et le gabarit fait la même chose en CSS).

### 2. Hypothèses et résultats se confondaient

**Problème.** Réglages et résultats sur le même papier, mêmes filets ; la monotone, tout en bas sur
toute la largeur, n'était rattachée à rien.

**Solution retenue.** Les hypothèses sont un **pupitre** : panneau teinté (`--pupitre`, ni la couleur
de fond ni le `--signal`, réservé à la mise en évidence), encadré, coins arrondis, champs de saisie
sur le papier ; titre « Hypothèses », sous-titre « À régler. Le lien de la page porte le
scénario. ». Les résultats restent sur le papier, tuiles à filet d'encre, titre « Résultats »,
sous-titre « Ce que le calcul en tire, heure par heure, sur l'année observée. ». **La monotone passe
dans la colonne des résultats**, sous les tuiles, avec la ligne des sources : tout ce qui est à droite
est calculé. Sur téléphone, le pupitre teinté collé en haut et le titre « Résultats » dessous gardent
la même séparation. Contrastes du texte sur le pupitre : `--encre-2` 5,3:1 (clair), 6,65:1 (sombre) ;
`--encre` 12:1.

**Alternatives écartées.** Une flèche ou un pictogramme entre les deux zones (interdit par la
direction visuelle) ; colorer les résultats (une seule mise en évidence sur le site).

### 3. Ordinateur : l'outil entier dans la fenêtre, sans défilement

**Solution retenue.** Sur un écran d'au moins 62rem de large et 36rem de haut, la page prend
exactement la hauteur de la fenêtre (`body` en colonne flexible, `min-height: 100dvh`) ; sous le
bandeau du site : une ligne de titre avec trois liens (« Ce que fait le simulateur, et ce qu'il ne
modélise pas », « Lire ces résultats », « Définitions et sources ») ; puis deux colonnes : pupitre
(22rem) et scénario à gauche ; à droite, tuiles (quatre par rangée), monotone qui **prend toute la
hauteur restante** (mesurée, le tracé est en position absolue pour ne pas peser sur la hauteur de son
conteneur), et une ligne de sources courte avec un lien vers le détail. La page s'élargit jusqu'à
100rem : à 1920 px, les deux panneaux de la monotone font 600 px de large et 650 px de haut.

Les textes longs vont dans une **notice** : panneau latéral à droite (46rem au plus), ouvert par les
liens de la tête, par le lien « Détail » de chaque tuile (ouvre la notice sur ce résultat : valeur,
qualificatif, seconde valeur, détail, notes de sources), par « Lire le graphique, sources, données »
(sous-titre et remarques du graphique, sources, tableau de données) et par le lien des sources. Elle
contient, dans l'ordre : ce que fait le simulateur et ce qu'il ne modélise pas (`en-tete.md`), le
détail de tous les résultats, la lecture (`lecture.md`, ses trois sections), les définitions et les
heures renseignées, les sources et les données. Elle est **non modale** : le pupitre reste visible et
utilisable à gauche, et le détail des résultats suit les réglages en direct. Focus porté sur le titre
de la section ouverte, Échap ou « Fermer » la referme et rend le focus au lien d'origine. Les
anciennes ancres (`#presentation`, `#lecture-1`…) ouvrent la notice à la bonne section ; l'état dans
l'adresse est inchangé.

Les raisons des réglages restent des replis natifs dans le pupitre, à côté de leur réglage : déplié,
le pupitre défile en interne, pas la page (mesuré : document 900 px pour une fenêtre de 900 px avec
la raison du froid dépliée). Le pied de page du site est masqué sur cette page quand JavaScript est
actif (il ferait défiler la page d'une ligne).

**Mesures** (Chromium sans tête, zone d'affichage de la taille indiquée, thèmes clair et sombre,
défauts et scénario 2019, 2,5 GW, 24 h, 4 °C, 0,5 GW) :

| Fenêtre | Hauteur du document | Pupitre (contenu / visible) | Hauteur de la monotone (bloc) |
|---|---|---|---|
| 1366×768 | 768 | 484 / 484 | 358 px |
| 1440×900 | 900 | 616 / 616 | 490 px |
| 1920×1080 | 1 080 | 796 / 796 | 670 px |
| 1366×650 (zone réelle d'un portable 1366×768) | 650 | 477 / 366 : le pupitre défile en interne | 240 px |

Identique dans les deux thèmes, avec les défauts et avec le scénario.

**Alternatives écartées.** Une page liée pour les textes (on quitte l'outil pour lire une limite) ;
des infobulles ou `popover` par tuile (pas de lecture continue, positionnement incertain sans ancrage
CSS) ; une notice modale (les réglages deviendraient inertes pendant la lecture) ; garder les replis
dans le flux (la page redéfile dès qu'on en ouvre un).

### 4. Téléphone : voir l'effet en réglant

**Solution retenue.** Le pupitre est **collé en haut de l'écran** pendant tout le défilement des
résultats, et compact : une rangée de cinq onglets qui affichent **toutes les valeurs réglées**
(Année 2019, Puissance 2,5 GW, Effacement 24 h, Froid 4 °C, Plancher 0,5 GW) et, dessous, le
réglage choisi (nom complet, curseur, saisie, défaut et « Raison »). 136 px de haut à 390 et 360 px
de large, soit 16 % et 18 % de l'écran : on fait défiler jusqu'aux tuiles ou à la monotone, on touche
un onglet, on règle, on voit l'effet dessous. Une raison dépliée agrandit le pupitre jusqu'à 60 % de
l'écran, avec défilement interne. « Revenir aux défauts » est en tête du scénario, juste sous le
pupitre. Les onglets sont des boutons (`aria-expanded`, `aria-controls`), le nom complet du réglage
est lu par les lecteurs d'écran quand l'onglet porte un nom court (« Plancher (Nucléaire non
mobilisable) »). La notice s'ouvre en plein écran.

**Pourquoi pas une barre de résultats collante ?** Il faudrait choisir trois ou quatre des huit
résultats ; chaque réglage agit sur des résultats différents (le plancher sur le nucléaire,
l'effacement et le froid sur les heures au-delà des maxima), la monotone resterait invisible, et les
qualificatifs (« au plus », la seconde valeur) se tasseraient mal dans une barre. Le pupitre collé
laisse **tous** les résultats, monotone comprise, sous le pouce. Pas non plus de tiroir de réglages
escamotable : il cache ce qu'il faut voir au moment où on règle.

**Mesures.** 390×844 : document 2 050 px ; 360×740 : 2 069 px (le téléphone défile, c'est voulu) ;
pupitre 136 px ; positions stables sur toute la séquence de réglages (point 1).

## Accessibilité

Clavier : tous les contrôles sont natifs (liens, boutons, `select`, curseurs, saisies, replis) ; la
notice se parcourt au clavier et se ferme par Échap, focus rendu. Lecteur d'écran : l'annonce différée
des résultats (`aria-live`) est conservée telle quelle ; la ligne d'état du chargement est un
`role="status"` ; l'erreur de chargement reste un `role="alert"` ; chaque lien « Détail » est lu
« Détail et sources : <titre du résultat> » ; le titre du graphique lu garde le libellé du scénario.
`prefers-reduced-motion` : seule transition ajoutée, l'atténuation des résultats périmés, désactivée.
Rien ne dépend du survol. Sans JavaScript : pas de pleine fenêtre forcée, réglages (inactifs) avec
leurs raisons, puis la notice dans le flux, lisible en entier (capture `1440x900-light-sans-js.png`).

## Tests

Dans `site/` : `npm run check` (0 erreur, 0 avertissement), `npm test` (15 fichiers, 173 tests),
`npm run format:check`, `npm run build` : tout passe. Aucun test modifié.

## Captures

Dossier temporaire de session `scratchpad/simulateur-ux/` (25 fichiers) : `WxH-{dark,light}-{defaut,scenario}.png`
aux trois tailles d'ordinateur ; `1366x650-dark-scenario.png` ; `1440x900-dark-notice-detail.png`
(notice ouverte sur un résultat) ; `1440x900-dark-raison-ouverte.png` ;
`{390x844,360x740}-{dark,light}-{defaut,scenario-defile}.png` (pupitre collé au-dessus des tuiles) ;
`390x844-dark-notice.png` ; `1440x900-light-sans-js.png`. État d'avant : `scratchpad/simulateur-ux/avant/`.

## Doutes

1. **Pied de page masqué** sur `/simulateur` (ordinateur, avec JavaScript) : la mention « aucun
   traceur, aucune ressource tierce » n'y est plus visible. À trancher par l'auteur.
2. **`en-tete.md` dit « les hypothèses se règlent ci-dessous »** : dans la notice, elles sont à
   gauche. Un mot à changer dans un fichier de texte que je n'avais pas le droit de toucher.
3. **Lien « Détail » au lieu de « Détail et sources »** sur les tuiles, faute de place dans la ligne
   du titre (le texte lu dit « Détail et sources ») ; les sources sont à un clic, dans la notice.
4. **Légende de la monotone : « avec le scénario »** au lieu du libellé complet (« avec 2,5 GW,
   effacés 24 heures, froid supplémentaire de 4 °C »), dont la longueur variable ferait bouger
   l'en-tête du graphique ; le libellé reste dans le titre lu, l'infobulle, la notice et le tableau.
5. **Réserve de la tuile du nucléaire liée à son rang** (`RESERVE = 5`, ordre de `phrases.ts`) : si
   l'ordre des tuiles change, la réserve est à déplacer (commentaire dans le code).
6. **Portable réel 1366×768** (zone d'affichage d'environ 650 px) : la page ne défile pas, mais le
   pupitre défile en interne (le dernier réglage demande un défilement) et la monotone n'a que 240 px.
   Sous 36rem de haut ou 62rem de large, retour à la page qui défile.
7. **Vides réservés** : sur téléphone, la seconde valeur du nucléaire réserve cinq lignes et la phrase
   du scénario environ sept à 360 px ; sans JavaScript, la case du scénario reste vide. C'est le prix
   de la stabilité.
8. « 2015-2025 » peut se couper au trait d'union dans un titre de tuile (1440 px).
9. Le filet du pupitre (`--pupitre-bord`) est sous 3:1 contre le fond : il est décoratif, la teinte et
   le titre portent la distinction.
10. Vérifié dans Chromium sans tête seulement (tactile émulé) ; ni Safari ni Firefox, ni appareil réel.
    La page utilise `:has()`, les requêtes de conteneur et `dvh`, disponibles dans leurs versions
    récentes.
