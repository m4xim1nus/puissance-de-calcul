# Relecture de l'accueil : lecteur non spécialiste (agent, 26/11/2026)

Relecture faite par un agent dans la peau d'un lecteur curieux, à l'aise avec les chiffres, qui ne
connaît ni les marchés de l'électricité ni leur jargon. Page lue : http://localhost:4318/ (build
local du 26/11/2026), sources `site/src/routes/+page.svelte`, `docs/MESSAGE.md`, champ `accroche`
de `docs/enquetes/{combien,quand,carbone,ou}.md`. Captures à 390 × 844, 390 × 5200, 1366 × 768 et
1366 × 3600 (Chromium headless, non versionnées).

Contrainte respectée : aucun chiffre modifié, aucune formulation prudente retirée (« au plus »,
« à notre connaissance », « inférence de ce site ») ; des précautions sont parfois **ajoutées**
quand elles existent déjà ailleurs sur la page. Les réécritures sont prêtes à coller ; celles qui
touchent au fond sont signalées « à vérifier ».

## Ce que je comprends

**En 30 secondes, sans défiler.** Sur ordinateur (1366 × 768) : la question, le chapeau, le premier
point d'« À retenir » et le début du second. Aucun chiffre fort de carte, aucune image. Sur
téléphone (390 × 844) : la question, le chapeau et trois lignes du premier point. Ce que j'en
retiens : « un site sérieux qui pose une question ; la réponse se joue à l'heure, au poste et au
prix ». Je ne sais pas encore ce que veut dire « la moyenne annuelle ne tranche rien » (moyenne de
quoi ?).

**Après « À retenir » et les cartes, ma reformulation en deux phrases :**

> Les data centers consomment peu aujourd'hui (1 % de l'électricité), mais en puissance, l'hiver,
> chaque GW permanent mange la marge de sécurité, et 18 GW sont déjà réservés alors que cette
> marge est de 8 à 10 GW. La France n'a pas assez de surplus pour les alimenter, on ne connaît pas
> leur carbone réel et on ne sait pas où les brancher.

Deux contresens dans cette reformulation, tous deux induits par la page :

- « **La France n'a pas assez de surplus** » : faux. Le titre « Le surplus ne suffit pas » me le
  fait conclure, alors que la phrase dit seulement que le *nucléaire* disponible non produit n'en
  couvre qu'une partie, le reste pouvant venir… d'autres surplus (renouvelables moins arrêtés,
  exportations en moins). Point 1.
- « **18 GW réservés contre 8 à 10 GW de marge** » : comparaison que la page ne fait pas mais
  qu'elle provoque, en mettant le 18 GW en chiffre fort et la marge en GW dans « À retenir », avec
  la mise en garde (« Une réservation n'engage pas à consommer ») en dernière phrase de la carte.
  Point 2.

## Points, du plus bloquant au moins bloquant

### 1. « Le surplus ne suffit pas » induit un contresens ; deux notions clés ne sont expliquées nulle part

Le titre du deuxième point généralise au « surplus » ce qui n'est mesuré que pour le nucléaire. Le
non-spécialiste comprend « la France manque d'électricité en trop », ce que la phrase ne dit pas
(et l'experte relèvera que les renouvelables moins arrêtés et les exportations en moins sont aussi
du surplus). Par ailleurs, « consommation plate » et « nucléaire disponible et non produit » sont
les deux notions sur lesquelles repose le chiffre le plus fort de la page, et aucune n'a d'entrée au
glossaire ni de glose.

`docs/MESSAGE.md`, « À retenir », deuxième point, actuel :

> **Le surplus ne suffit pas.** En 2025, au plus {{quand_part_j_5gw_2025}} de l'énergie d'une
> consommation plate de 5 GW aurait trouvé du nucléaire disponible et non produit ; le reste
> serait venu d'autres moyens, de renouvelables moins arrêtés ou d'exportations en moins.

Réécriture :

```markdown
- **Le nucléaire inutilisé n'aurait pas suffi.** En 2025, au plus
  {{quand_part_j_5gw_2025}} de l'énergie d'une [consommation plate](glossaire:consommation-plate)
  de 5 GW, identique à toute heure, aurait trouvé du
  [nucléaire disponible et non produit](glossaire:nucleaire-disponible-non-produit) :
  de la puissance que EDF déclarait disponible, mais qui ne produisait pas à cette heure. Le reste
  serait venu d'autres moyens, de renouvelables moins arrêtés ou d'exportations en moins.
```

Carte « Quand ? » (`docs/enquetes/quand.md`, `accroche`), actuel : « … Le reste serait venu
d'ailleurs. » « D'ailleurs » est la seule phrase de la carte qui ne dit rien ; réécriture (les liens
du glossaire ne sont pas répétés, règle « première occurrence ») :

```yaml
accroche: {{quand_part_j_5gw_2025}} au plus : la part de l'énergie d'une consommation plate de 5 GW qui aurait trouvé, en 2025, du nucléaire disponible et non produit. Le reste serait venu d'autres moyens, de renouvelables moins arrêtés ou d'exportations en moins.
```

Deux entrées de glossaire à créer (`docs/GLOSSAIRE.md`, ordre alphabétique : après « Charge
résiduelle » et après « MW et MWh »). **À vérifier** contre la méthode de « Quand ? » avant
publication, notamment la deuxième :

```markdown
## Consommation plate {#consommation-plate}

Consommation dont la puissance est la même à chaque heure de l'année. C'est le profil que ce site
suppose pour une consommation ajoutée, faute de courbe de charge publiée des data centers ; ce
n'est pas un profil observé.

## Nucléaire disponible non produit {#nucleaire-disponible-non-produit}

À une heure donnée, écart entre la puissance nucléaire qu'EDF déclare disponible (publications
[REMIT](glossaire:remit)) et la production nucléaire observée par RTE, ramené à zéro s'il est
négatif. C'est une borne haute de ce que le parc aurait pu produire en plus : tout ce qui est
déclaré disponible n'est pas mobilisable à toute heure.
```

### 2. Premier point : le passage des TWh aux GW est sauté, et la carte « Combien ? » invite à comparer 18 GW et 8 à 10 GW

Le premier point donne la consommation en TWh (4 à 5, puis 21 à 32), puis la marge en GW (8 à 10).
Le non-spécialiste ne sait pas convertir et ne sait donc pas si 21 à 32 TWh, c'est peu ou beaucoup
face à 8 à 10 GW : l'étape qui donne son sens au titre (« pointe plus qu'énergie ») est dans le
message replié (« 1,9 à 3,2 GW… d'un cinquième à deux cinquièmes de cette marge »). Le seul GW qu'il
trouve à comparer est le 18 GW de la carte, d'où le contresens. « Marge de sécurité » n'est pas liée
au glossaire, qui l'explique pourtant bien (entrée « Adéquation »). Enfin, l'imparfait « évaluait »
est la seule trace, ici, de la baisse de disponibilité nucléaire de cet hiver ; le message détaillé
le dit, « À retenir » non.

`docs/MESSAGE.md`, « À retenir », premier point, réécriture (ajoute une phrase sans nouveau
chiffre ; les fractions viennent du message détaillé) :

```markdown
- **Une question de pointe d'hiver plus que d'énergie annuelle.** Les data centers des
  sites dédiés ont consommé {{dc_conso_sites_dedies_2024}} en 2024, de l'ordre de 1 % de
  l'électricité française ; RTE en prévoit {{traj_bp2025_lente_2035}} à
  {{traj_bp2025_rapide_2035}} en 2035. Mais en puissance, chaque GW consommé en permanence
  retire à peu près autant à la [marge de sécurité](glossaire:adequation) de l'hiver
  (inférence de ce site), que RTE évaluait à {{marge_rte_hiver_2026_2027}} pour 2026-2027,
  avant la baisse de disponibilité nucléaire prévue cet hiver. La hausse prévue d'ici 2035,
  si elle était plate, en prendrait d'un cinquième à deux cinquièmes : un ordre de grandeur,
  détaillé plus bas.
```

Si la convention de `MESSAGE.md` (« les nombres en clair sont des calculs expliqués dans la
phrase », dans le message en détail) exclut ces fractions d'« À retenir », garder au moins la
première modification (lien et « avant la baisse… »).

Carte « Combien ? » (`docs/enquetes/combien.md`, `accroche`) : remonter la mise en garde juste
après le chiffre fort, et lier « puissance réservée » (première occurrence sur la page) :

```yaml
accroche: {{dc_reserve_rte_2026_05}} de [puissance réservée](glossaire:puissance-reservee) auprès de RTE pour des data centers en mai 2026 : un droit d'accès au réseau, qui n'engage pas à consommer. Leur consommation de 2024 : {{dc_conso_sites_dedies_2024}}, de l'ordre de 1 % de celle du pays.
```

(À vérifier : que `rendreCorps` rend bien un lien `glossaire:` dans une accroche, et que
`accroche()` découpe toujours le chiffre fort au premier `</sup>`.)

### 3. Rien de fort au premier écran ; les cartes arrivent tard et répètent « À retenir »

Mesuré sur les captures : sur ordinateur, les cartes commencent vers 1 000 px et le calendrier
vers 1 900 px ; sur téléphone, les cartes commencent vers 1 770 px (troisième écran) et le
calendrier vers 3 500 px (cinquième écran). L'auteur demandait un chiffre fort par enquête et une
visualisation qui donne envie de continuer : ni l'un ni l'autre n'est visible sans défiler. Et
quatre des cinq chiffres des cartes (1 %, 52 %, 19,6 g, carte non parue) sont déjà dans « À
retenir » : à la lecture, on lit deux fois la même chose, la seconde fois en plus gros.

Deux options, par ordre de coût :

- **A, minimale.** Raccourcir la ligne de méta sous « À retenir » (point 8) et le chapeau (point 5) :
  sur téléphone, on gagne environ quatre lignes avant le premier point ; ça ne fait pas monter les
  cartes au premier écran.
- **B, recommandée, à trancher par l'auteur.** Fusionner « À retenir » et les cartes : chaque carte
  porte en tête le titre en gras du point correspondant (« Une question de pointe d'hiver… », « Le
  nucléaire inutilisé n'aurait pas suffi », « Le carbone d'une consommation ajoutée n'est pas
  connu », « Où l'accueillir, les données publiques ne le disent pas »), puis le chiffre fort, puis
  la phrase et les sources. Les quatre points correspondent déjà un à un aux quatre enquêtes. Le
  texte complet des points reste dans le message en détail. Coût : `MESSAGE.md` et ses contrôles
  (`SECTIONS_MESSAGE`) à adapter, et le point 1 (pointe d'hiver) porte à la fois sur « Combien ? »
  et sur le calcul d'adéquation de RTE, ce que la carte devra dire.

### 4. Le calendrier des prix : je comprends ce qu'il montre, pas ce qu'il faut y voir

Ce qu'il montre, oui : une case par heure, une ligne par jour, couleur = prix ; la légende est
claire. Pourquoi il est là, à moitié : le paragraphe « Pourquoi regarder heure par heure ? » dit
qu'une consommation continue passe par toutes les heures, puis s'arrête. Il manque la clé de
lecture (où regarder) et la conséquence. Sans elle, je vois une masse orangée striée de vert, et je
ne relie pas l'image au message (qui ne parle pas de prix). Le chapeau annonce « au prix » ; c'est
le seul élément de prix de la page, et rien ne dit qu'il n'y a pas encore d'enquête sur le prix.

Autre détail de hiérarchie : sous le calendrier, les deux lignes sur le changement d'heure (« Gris :
pas de prix… », « Le jour du passage à l'heure d'hiver… ») viennent **avant** le fait marquant
(« En 2025, le prix day-ahead a été strictement négatif pendant 513 heures »). Les inverser dans
`HeroPrix.svelte`.

`site/src/routes/+page.svelte`, section `.pourquoi`, réécriture. **À vérifier** sur les données de
2025 (je l'ai lu sur la capture : vert entre environ 10 h et 16 h de mars à septembre ; teintes les
plus foncées en janvier-février et le matin et le soir) ; la phrase est datée « en 2025 » parce que le
calendrier peut afficher une autre année :

```svelte
  <p>
    Pourquoi regarder heure par heure&#8239;? Parce qu’une consommation qui tourne jour et nuit
    passe par toutes les heures de l’année, les plus chères comme celles à
    <a class="glossaire" href="/methode#g-prix-negatif">prix négatif</a>. Le calendrier ci-dessous
    en montre un signal&#8239;: le
    <a class="glossaire" href="/methode#g-prix-de-gros">prix de gros</a>
    <a class="glossaire" href="/methode#g-day-ahead">day-ahead</a> en France, fixé la veille pour le lendemain,
    une case par heure, une ligne par jour.
  </p>
  <p>
    En 2025, les heures à prix négatif (en vert) tombent surtout en milieu de journée, du printemps à
    la fin de l’été&#8239;; les plus chères (les plus foncées), le matin et le soir, et en hiver. Le
    prix n’a pas encore son enquête&#8239;: ce calendrier en est la matière première.
  </p>
```

### 5. Le chapeau est elliptique

> Ce site part d'une hypothèse : la moyenne annuelle ne tranche rien, la question se joue à
> l'heure, au poste électrique et au prix.

« La moyenne annuelle » de quoi ? Le lecteur n'a pas l'argument que cette moyenne est censée
trancher (électricité abondante et décarbonée, formulation du brief). Premier « poste électrique »
de la page : c'est ici que le lien du glossaire doit aller (règle « première occurrence ») ; il est
aujourd'hui dans le message replié.

```svelte
  <p class="chapeau">
    Ce site part d’une hypothèse&#8239;: en moyenne sur l’année, l’électricité française est
    abondante et décarbonée, mais cette moyenne ne tranche rien&#8239;; la question se joue à
    l’heure, au <a class="glossaire" href="/methode#g-poste-electrique">poste électrique</a> et au
    prix. Il vérifie, chiffre et date ce qu’en disent les données publiques, et dit où elles
    manquent.
  </p>
```

(Le lien du message détaillé, `[poste électrique](glossaire:poste-electrique)`, devient alors une
seconde occurrence ; le retirer ou non selon la façon dont le contrôle compte les occurrences.)

### 6. Carte « Où ? » : « 400 kV » et une phrase à double sens

> Environ 50 postes du réseau à 400 kV pourraient accueillir un projet d'environ 250 MW, selon
> RTE. Il n'en publie ni la liste ni la carte, annoncée en février 2025.

« 400 kV » ne dit rien au non-spécialiste (lien vers l'entrée « RPT » utile, sans retirer la
précision). « Ni la liste ni la carte, annoncée en février 2025 » : je ne sais pas de quelle carte
il s'agit, ni si c'est la liste ou la carte qui a été annoncée. « À notre connaissance », présent
dans « À retenir » pour le même fait, manque ici.

```yaml
accroche: Environ {{sddr_postes_250mw}} du [réseau de transport](glossaire:rpt) à 400 kV pourraient accueillir un projet d'environ 250 MW, selon RTE, qui n'en publie pas la liste. La carte des zones favorables qu'il annonçait en février 2025 n'est pas parue, à notre connaissance.
```

Dans « À retenir », quatrième point, « une capacité d'accueil pour une consommation » accroche
aussi ; réécriture sans changer le fond :

```markdown
- **Où l'accueillir, les données publiques ne le disent pas.** La capacité d'accueil d'une
  nouvelle consommation n'est publiée nulle part poste par poste, et la carte des zones
  favorables annoncée par RTE en février 2025 n'est pas parue au 26 novembre 2026, à notre
  connaissance.
```

### 7. Carte et point « Quel carbone ? » : le chiffre fort dit l'inverse du message

Le chiffre fort (19,6 g, très bas) est précisément celui que la carte dit ne pas répondre à la
question. Le lecteur pressé retient « c'est très bas ». Ce n'est pas un défaut à corriger en
changeant le chiffre (la carte est honnête), mais la phrase suivante doit attaquer tout de suite :
« Ce chiffre » est trop faible. « Facteur marginal » n'est lié nulle part : le lier dans « À
retenir » (première occurrence).

`docs/MESSAGE.md`, troisième point : remplacer « de facteur marginal récent » par
« de [facteur marginal](glossaire:facteur-moyen-marginal) récent ».

```yaml
accroche: {{intensite_prod_rte_2025}} en moyenne pour la production française de 2025. C'est une moyenne : elle ne dit pas ce qu'émettrait une consommation ajoutée, et aucun facteur marginal récent n'est publié pour la France, à notre connaissance.
```

### 8. La ligne de méta sous « À retenir » est longue et jargonneuse

> Au 26 novembre 2026, version 2, d'après « Combien ? », « Quand ? », « Quel carbone ? » et
> « Où ? », et le calcul d'adéquation du Bilan prévisionnel 2025 de RTE. Le message en détail ↓

Quatre lignes sur téléphone avant le premier point, et « calcul d'adéquation » sans lien (le front
matter n'est pas rendu en Markdown). `docs/MESSAGE.md`, front matter :

```yaml
repose_sur: les quatre enquêtes et le Bilan prévisionnel 2025 de RTE
```

La précision « calcul d'adéquation » reste dans le premier paragraphe du message détaillé, qui
l'explique.

### 9. Carte « Simulateur » : « X GW » ressemble à un texte à remplir, et la fin est une liste de noms

« X GW de plus », en gris, se lit comme un gabarit oublié ou une carte désactivée. « énergie,
nucléaire disponible non produit, maximum observé, prix » : quatre noms sans verbe ; « maximum
observé » ne dit pas de quoi. Le simulateur accepte `?x=5` (`lib/simulateur/etat.ts`) : relier la
carte au scénario de la carte « Quand ? » donne une raison de cliquer. « Effacement » apparaît ici
pour la première fois : le lier.

```svelte
    <article class="carte-enquete simulateur">
      <h3><a href="/simulateur">Simulateur</a></h3>
      <p class="fort">Et avec 5&#8239;GW de plus&#8239;?</p>
      <p class="suite">
        Ajoute une consommation plate à une année observée, heure par heure, avec ou sans
        <a class="glossaire" href="/methode#g-effacement">effacement</a> aux heures les plus
        tendues, et regarde ce qui change&#8239;: l’énergie, la part trouvée dans le nucléaire
        disponible non produit, les heures au-delà du maximum de consommation observé, les prix.
        Les hypothèses sont affichées, et plusieurs se règlent.
      </p>
      <a class="lire" href="/simulateur?x=5">Ouvrir le simulateur avec 5&#8239;GW →</a>
    </article>
```

(À vérifier : « heures au-delà du maximum de consommation observé » est bien ce que mesure le
simulateur ; la meta description du simulateur dit « heures au-delà du maximum observé ». Retirer
la règle CSS `.simulateur .fort { color: var(--encre-2); }` si le titre doit cesser de paraître
grisé.)

### 10. Grille des cartes sur ordinateur : 3 + 2 avec un trou, hauteurs inégales

À 1366 px, `repeat(auto-fill, minmax(min(100%, 17rem), 1fr))` donne trois cartes, puis deux et une
case vide ; la carte « Où ? » laisse un grand blanc au-dessus de son lien. Proposition : deux
colonnes pour les quatre enquêtes, simulateur en bandeau pleine largeur.

```css
  .grille {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr));
    gap: 1rem;
  }
  .carte-enquete.simulateur {
    grid-column: 1 / -1;
  }
```

### 11. Détails mineurs

- « Les data centers **des sites dédiés** » (« À retenir », premier point) : pour un non-spécialiste,
  « sites dédiés » ne dit pas ce qui est exclu. Facultatif : « Les data centers (sites dédiés, hors
  salles informatiques d'entreprise) ont consommé… », formulation du périmètre de la note 1.
- Le titre du message replié, « Ce qu'on peut en dire, à ce jour », ne dit pas qu'il s'agit du
  message développé ; la ligne grise en dessous le dit. Rien à changer si le libellé reste visible.

## Hors périmètre, à vérifier à la source

Notes 5 et 9 (calcul du site, `quand_part_j_5gw_2025`) : l'en-tête dit « Calcul du site, non
recoupé », mais le badge et la ligne de confiance disent « Confiance B : source primaire, sans
recoupement indépendant ». Un calcul du site n'est pas une source primaire au sens des autres
notes ; la lectrice experte le relèvera. Constaté sur la page rendue, non vérifié dans
`pipeline/referentiels/chiffres.yaml` ni dans `site/src/lib/notes`.
