# Relecture adverse finale : cohérence du site avant envoi du lien (26/11/2026)

Relecture « lectrice experte » (marchés de l'électricité, modélisation énergétique), par un agent
Opus distinct des rédacteurs, avant que l'auteur envoie le lien. Elle ne refait pas les relectures
page par page de `docs/relectures/` : elle couvre la cohérence **entre** pages, ce qui est nouveau
le 26/11 (message version 2, accroches des cartes de l'accueil, glossaire, « À toi », page
Méthode), et le rendu du site construit. « Où ? » n'est lu que pour sa cohérence avec le reste
(une autre relecture adverse est en cours). Aucun autre fichier modifié, rien commité.

**État relu.** Les sources ont changé pendant la relecture : `docs/MESSAGE.md`, les quatre
enquêtes et `docs/GLOSSAIRE.md` ont été réécrits à 19 h 23, après le build servi
(`site/build/`, 19 h 17). Les lignes citées ci-dessous sont celles des fichiers **à 19 h 24**
(copie figée dans le scratchpad de l'agent) ; les constats de rendu valent pour le build de
19 h 17. Exemple de décalage : le build affiche « À retenir » en quatre puces (« RTE en prévoit
21 TWh à 32 TWh en 2035 »), la source est désormais un paragraphe sans « prévoit ».

**Lu** : `CLAUDE.md` ; `docs/MESSAGE.md` (et `git diff HEAD`) ; `docs/enquetes/combien.md`,
`quand.md`, `carbone.md` en entier, `ou.md` pour la cohérence ; `docs/GLOSSAIRE.md` (36 entrées
à 19 h 24, 34 dans le build) ; `docs/A-TOI.md` ; `data/export/chiffres.json` (414 chiffres :
valeur, unité, période, source, recoupement) ; entrées concernées de `chiffres.yaml` et
`sources.yaml` ; `data/export/horaire/LISEZMOI.md` ; `site/src/lib/simulateur/Simulateur.svelte`
(gabarit du scénario). Pages servies sur `localhost:4318` : les neuf pages, texte rendu, notes
retirées puis lues à part pour l'accueil.

**Sources primaires relues pour cette relecture** :

- Conseil de l'UE, doc. 14944/26 du 28/10/2026 (`data/raw/carbone/conseil_14944_26_en.pdf`, lu en
  entier : considérants 3, 3a, 3b, articles 1er et 2) ;
- RTE, *Mécanisme de capacité — rapport de paramétrage PL 2026/2027*
  (`data/raw/spike_quand/pdf/rte_parametrage_mecapa_2026-02-12.pdf`, p. 3, 5-7, 10) ;
- CRE, délibération n° 2026-43 sur le paramétrage du mécanisme de capacité
  (`data/raw/spike_quand/pdf/cre_2026-43_parametrage.pdf`, § 1.2 et § 3) ;
- RTE, *BP2025 — Fonctionnement du système électrique*, p. 2 et note 38 (p. 30) ;
- RTE, *SDDR — note d'accompagnement en réponse à la CPDP*, juin 2026, p. 20
  (`data/raw/ou/2026-06-12-nte-accompagnement-reponse-cpdp.pdf`) ;
- RTE, fiche « fast-track » 5 sites (`data/raw/spike/datacenters/docs/rte_fiche_fast-track_5sites_2025-12.pdf`) ;
- RTE, *SDDR 2025 — synthèse*, p. 19, figure 5 ;
- EUR-Lex, règlement (UE) 2024/1106 (titre, date, modifications de l'article 4 du règlement
  1227/2011), consulté le 26/11/2026 ;
- article L. 321-7 du code de l'énergie (S3REnR), via des citations de la CRE et d'Enedis
  (Légifrance non servi aux accès automatisés).

Classement : **fond** = faux, ou dit plus que la source ou que l'enquête : à corriger avant
d'envoyer le lien ; **forme** = à corriger, ne bloque pas.

---

## Verdict

**Envoyable après corrections**, en quatre temps : les cinq points de fond (F1 à F5), puis un
**nouveau build** (le site servi ne reflète pas les sources), `pc check` et les tests, et une
lecture de l'accueil reconstruit. Aucun chiffre n'est faux : les 414 valeurs reprises d'une page à
l'autre sont identiques (valeur, unité, période), les recalculs en clair du message bouclent, et
les catégories annonce / réservation / signature / raccordement et moyen / marginal sont tenues
dans les enquêtes. Les défauts sont aux endroits qui **coupent du contexte** : accroches, « À
retenir », glossaire, « À toi ».

---

## Points de fond

### F1. Accroche « Combien ? » : « Leur consommation » rattache 4 à 5 TWh aux 18 GW réservés

**Où** : `docs/enquetes/combien.md`, ligne 5 (front matter `accroche`), carte de l'accueil.

> 18 GW de puissance réservée auprès de RTE pour des data centers en mai 2026 : un droit d'accès
> au réseau, qui n'engage pas à consommer. **Leur** consommation de 2024 : 4 à 5 TWh […]

**Problème** : « Leur » renvoie aux projets qui détiennent les 18 GW de réservations, c'est-à-dire
surtout des projets pas encore construits. Or `dc_conso_sites_dedies_2024` est la consommation de
**tous les data centers en service sur sites dédiés**, dont environ 3 TWh sur le réseau d'Enedis
(`dc_conso_rpd_2024`, BE2025 p. 18), hors de toute réservation chez RTE. L'accroche met côte à
côte deux catégories que l'enquête sépare (pyramide, étages « réservée » et « appelée »). C'est le
mélange que `CLAUDE.md` interdit. Une lectrice qui ne lit que la carte en tire un taux d'usage
implicite (4,5 TWh pour 18 GW, soit environ 3 %), qui n'a aucun sens.

**Correction prête à coller** :

```
accroche: {{dc_reserve_rte_2026_05}} de [puissance réservée](glossaire:puissance-reservee) auprès de RTE pour des data centers en mai 2026 : un droit d'accès au réseau, qui n'engage pas à consommer. Les data centers en service sur des sites dédiés, eux, ont consommé {{dc_conso_sites_dedies_2024}} en 2024, de l'ordre de 1 % de la consommation du pays.
```

### F2. « 52 % au plus » : l'accroche, le message et le glossaire présentent comme un plafond un chiffre que le site dépasse lui-même (55 %)

**Où** :
- `docs/enquetes/quand.md`, ligne 5 (accroche) : « {{quand_part_j_5gw_2025}} au plus : la part de
  l'énergie… » ;
- `docs/MESSAGE.md`, lignes 76-79 : « {{quand_part_j_5gw_2025}} au plus de l'énergie… », suivi
  trois lignes plus bas de « ces parts montent à {{quand_part_j_reintegre_5gw_2025}} » ;
- build servi, « À retenir » (puce 2) : « au plus 52 % » sans réserve ;
- `docs/GLOSSAIRE.md`, entrée « Nucléaire disponible non produit » (l. 172-178) : « C'est une borne
  haute de ce que le parc aurait pu produire en plus ».

**Problème** : `quand_part_j_5gw_2025` = 52 % ; `quand_part_j_reintegre_5gw_2025` = 55 %
(`chiffres.json`). Le « au plus » ne vaut **qu'avec la disponibilité telle qu'EDF la déclare** :
c'est ce que dit l'enquête (l. 167-171, « avec la disponibilité déclarée par EDF »). Sur la carte
et dans le message, il devient un plafond absolu, et le même message donne ensuite un chiffre
au-dessus. Pour une experte, c'est la contradiction la plus visible du site, et elle tombe sur
l'indicateur phare de « Quand ? ». Même défaut dans le glossaire : la « borne haute » est
dépassée par la variante réintégrée que publient l'enquête et le simulateur.

**Corrections prêtes à coller** :

Accroche de `quand.md` :

```
accroche: Environ la moitié au plus ({{quand_part_j_5gw_2025}} avec la disponibilité déclarée par EDF, {{quand_part_j_reintegre_5gw_2025}} en réintégrant les arrêts courts qu'il déclare pour modulation) : la part de l'énergie d'une [consommation plate](glossaire:consommation-plate) de 5 GW qui aurait trouvé, en 2025, du [nucléaire disponible et non produit](glossaire:nucleaire-disponible-non-produit). Le reste serait venu d'autres moyens, de renouvelables moins arrêtés ou d'exportations en moins.
```

`MESSAGE.md`, lignes 76-79, remplacer « Avec les données de 2025 et la disponibilité déclarée par
EDF, {{quand_part_j_5gw_2025}} au plus de l'énergie » par :

```
Avec les données de 2025, au plus {{quand_part_j_5gw_2025}} de l'énergie
```

et, après « ces parts montent à {{quand_part_j_reintegre_5gw_2025}} et
{{quand_part_j_plancher_reintegre_5gw_2025}} », ajouter : « : le plafond dépend de la frontière,
fixée par EDF, entre indisponible et modulé ». Si une puce « À retenir » reprend ce chiffre, elle
écrit « environ la moitié au plus », jamais « au plus 52 % » seul.

Glossaire, dernière phrase de « Nucléaire disponible non produit » :

```
C'est une borne haute de ce que le parc aurait pu produire en plus à cette heure, à frontière d'EDF entre « indisponible » et « modulé » donnée : en réintégrant les arrêts courts qu'EDF déclare indisponibles pour modulation, l'écart est plus grand ; à l'inverse, tout ce qui est déclaré disponible n'est pas mobilisable à toute heure, et le combustible limite l'énergie sur l'année.
```

### F3. « À retenir » (version 2) : la marge est citée sans le calcul de RTE qui la tempère

**Où** : `docs/MESSAGE.md`, lignes 26-35 (paragraphe « À retenir » à 19 h 24) ; même défaut dans la
puce 1 du build.

**Problème** : le paragraphe donne l'inférence du site (« chaque GW consommé en permanence retire à
peu près autant à la marge », 8 à 10 GW), mais pas le résultat de RTE, qui fait le calcul
d'adéquation **avec** les data centers : aucun besoin de moyens nouveaux d'ici 2035 en
décarbonation lente (`besoin_capacites_lente_r3_2030_2035` = 0 GW), 1 à 6 GW en 2035 en
décarbonation rapide. C'était le point de fond n° 1 de la relecture du message
(`2026-11-26-message-en-bref.md`). La version 1 l'a corrigé dans le corps, mais la version 2 le
réintroduit à l'endroit le plus lu. Seul, le paragraphe laisse entendre que la vague entame une
marge déjà étroite. Le détail dit l'inverse pour la trajectoire lente.

Accessoirement, le build (puce 1) écrit « RTE en **prévoit** 21 TWh à 32 TWh en 2035 », ce qui
contredit le titre de « Combien ? » (« des trajectoires, pas des prévisions »). La source de
19 h 24 n'a plus cette phrase : vérifier le rendu au prochain build.

**Correction prête à coller** (à la place des lignes 26-35) :

```
**Moins une question d'énergie annuelle que de pointe d'hiver, d'heure
et de lieu.** Les data centers pèsent peu dans la consommation
d'électricité de l'année. À la pointe, chaque GW consommé en permanence
retire à peu près autant à la [marge de sécurité](glossaire:adequation)
de l'hiver (inférence de ce site), que RTE évaluait à
{{marge_rte_hiver_2026_2027}} pour 2026-2027, avant la baisse de
disponibilité nucléaire prévue cet hiver ; avec ses propres trajectoires,
data centers compris, RTE ne trouve pas de besoin de moyens nouveaux
d'ici 2035 en décarbonation lente, et un besoin de
{{besoin_capacites_rapide_2035}} en 2035 en décarbonation rapide. Aux
heures de surplus, le nucléaire disponible et non produit n'en
servirait qu'une partie ; le carbone d'une consommation ajoutée n'est
pas connu ; et les données publiques ne disent pas à quel poste il
reste de la place.
```

### F4. « À toi », mission 1 : la conversion d'unité est fausse

**Où** : `docs/A-TOI.md`, lignes 49-52.

> Une courbe de charge donne souvent une **puissance moyenne** par demi-heure (en W), pas une
> énergie : pour passer aux kWh, il faut multiplier par 0,5 heure.

**Problème** : des W multipliés par 0,5 h donnent des **Wh**, pas des kWh. Il manque la division
par 1 000, et l'erreur est d'un facteur 1 000 sur la page qui apprend à vérifier les unités.
L'onglet n'a pas d'enjeu de fond pour la thèse, mais l'experte le lira comme un test du sérieux
du site. Deuxième piège, absent de la page : le fichier du site horodate le **début** de l'heure
(`LISEZMOI.md`). Il faut donc demander quelle convention suit le fichier d'Enedis (début ou fin de
la demi-heure). Ce site a eu le même problème avec éCO2mix. Ce point n'a pas été vérifié dans un
export Enedis réel (espace client non accessible) : la correction pose la question sans
affirmer la réponse.

**Correction prête à coller** (lignes 49-55) :

```
- l'unité. Une courbe de charge donne souvent une **puissance moyenne**
  par demi-heure (en W), pas une énergie : chaque valeur multipliée par
  0,5 heure donne des Wh, à diviser par 1 000 pour des kWh. Additionne une
  journée à la main et compare avec ta consommation affichée par Enedis
  pour ce jour-là ;
- l'heure. Le fichier du site est en heure UTC, et chaque ligne marque le
  **début** de l'heure ; celui d'Enedis est en heure française. Demande à
  Claude si l'heure d'Enedis marque le début ou la fin de chaque
  demi-heure, comment il a aligné les deux, et regarde ce qu'il fait le
  jour d'un changement d'heure.
```

### F5. « À toi », mission 1 : le fichier de prix proposé n'existe pas pour des mesures récentes

**Où** : `docs/A-TOI.md`, lignes 35-36 et 42-44 (« fichier /donnees/horaire/2025.csv ou l'année qui
correspond »).

**Problème** : le site ne sert que `/donnees/horaire/2015.csv` à `2025.csv` (`site/build/donnees/horaire/`,
pas de `2026.csv`). Une personne qui active aujourd'hui sa courbe de charge, comme la page le
propose (« quelques jours ou quelques semaines »), aura des mesures de fin novembre 2026. Aucun
fichier du site ne les couvre, et le dernier prix publié date de l'extraction du 26/11/2026. La
mission échoue à la première étape, ou pousse Claude à improviser une source.

**Correction prête à coller** (dans le bloc « Demande à Claude », lignes 42-44) :

```
> Ensuite, récupère les prix de gros heure par heure de la zone France
> pour les mêmes jours : sur pdc.technoperchoir.fr (fichiers
> /donnees/horaire/AAAA.csv, années closes seulement) si mes mesures sont
> d'une année close, sinon sur energy-charts.info (prix day-ahead, zone
> France), et dis-moi d'où viennent ceux que tu as pris. Puis dis-moi
```

(ou publier `2026.csv` en le disant provisoire, comme le calendrier de l'accueil le fait déjà avec
`/donnees/prix/2026.json`).

---

## Points de forme

### 1. « Quel carbone ? », paragraphe ETS : traduire « dynamic parameters » et rendre la demande de baisse annuelle (demande du coordinateur)

**Où** : `docs/enquetes/carbone.md`, lignes 285-290.

> Le texte de compromis […] la garde, mais n'annule plus que les quotas détenus au-delà de
> {{ets_seuil_invalidation_compromis}} à son entrée en vigueur, et annonce des seuils de réserve
> « dynamiques » dans une révision plus large proposée en juillet 2026

**Ce que dit le texte du Conseil** (doc. 14944/26, annexe, p. 5-6, relu en entier) :

- considérant 3 : « allowances held in the reserve above 700 million allowances should no longer
  be valid as from the date of entry into force of this decision » ; article 1er : 400 millions
  jusqu'à la veille de l'entrée en vigueur, 700 millions « From [ … the date of entry into force] » ;
- considérant 3a : « The July 2026 proposal for a Directive […] includes dynamic parameters for
  the upper threshold, lower threshold and corresponding buffers and the release quantity for the
  Market Stability Reserve. That amendment **should also include** an annual decrease of the
  threshold for the invalidation of excess ETS allowances in the Market Stability Reserve to
  ensure a consistent overall approach. »

**Problèmes** :
1. Les guillemets autour de « dynamiques » présentent la traduction du site comme une citation
   (le document est en anglais seulement).
2. Le compromis n'« annonce » rien. Il constate que la proposition de juillet prévoit des
   paramètres dynamiques, et **demande** que la révision prévoie aussi une baisse annuelle du
   seuil d'invalidation. La formulation proposée par la relecture précédente
   (`2026-11-26-carbone.md`, l. 478-480 : « une révision plus large […] qui ferait baisser
   chaque année le seuil d'annulation ») va trop loin : selon le considérant 3a, la proposition
   de juillet **ne contient pas** cette baisse. Les colégislateurs la demandent.
3. « au-delà de 700 millions à son entrée en vigueur » peut se lire comme une invalidation
   ponctuelle. Le texte fixe une règle durable « à partir de » l'entrée en vigueur.

**Correction prête à coller** (lignes 285-290) :

```
  l'annulation {{source:ce-tnac-2025|section 2}}. Le texte de compromis
  approuvé par les représentants des États membres le 28 octobre 2026 la
  garde : à partir de son entrée en vigueur, seuls les quotas que la
  réserve détient au-delà de {{ets_seuil_invalidation_compromis}} ne sont
  plus valides. Il rappelle que la révision plus large proposée par la
  Commission en juillet 2026 rend dynamiques les seuils haut et bas de la
  réserve, leurs marges et la quantité qu'elle remet sur le marché, et
  demande que cette révision prévoie aussi une baisse annuelle du seuil
  d'invalidation {{source:conseil-14944-26|annexe, considérants 3 et 3a, article 1er}}.
```

(La phrase suivante, « Si ce texte entre en vigueur, il peut n'y avoir aucune annulation tant que
la réserve reste sous le nouveau seuil », reste juste. Une baisse annuelle future du seuil, si
elle était adoptée, raccourcirait ce « court terme » : on peut ajouter « ou tant qu'une baisse du
seuil, demandée mais pas adoptée, ne le ramène pas sous la réserve ».)

### 2. Glossaire « Mécanisme de capacité » : la phrase sur les coefficients mélange les filières

**Où** : `docs/GLOSSAIRE.md`, lignes 149-152.

> pour un moyen thermique ou un effacement, sa disponibilité moyenne aux heures PP multipliée par
> un coefficient de filière, inférieur à 1 notamment pour le nucléaire, le fil de l'eau et le
> stockage.

**Problème** (rapport de paramétrage RTE, p. 5-7 et 10 ; CRE 2026-43, § 4) : pour la PL 2026/2027,
le coefficient est de **1,00 pour le thermique à flamme**, 0,95 pour le nucléaire, 0,80 pour le
fil de l'eau en certification standard. Le fil de l'eau n'est pas un moyen thermique. Les
renouvelables variables (et le fil de l'eau, au choix) sont certifiés en méthode **normative**,
sur la **puissance installée** (coefficients de 0,05 pour le solaire à 0,40 pour le fil de
l'eau). Les moyens à stock, effacements compris, ont un abaque de durée Kj en plus du
coefficient. Rien n'est chiffré faux, mais une spécialiste du mécanisme y verra une description
approximative.

**Correction prête à coller** (à la place de « : pour un moyen thermique […] le stockage. ») :

```
: pour un moyen pilotable, sa disponibilité moyenne aux [heures PP](glossaire:plages-pp) multipliée par un coefficient de filière (égal à 1 pour le thermique à flamme, inférieur à 1 pour le nucléaire ou le fil de l'eau) ; pour l'éolien et le solaire, sa puissance installée multipliée par un coefficient bien plus faible ; pour un stockage ou un effacement, un coefficient de plus tient compte de la durée pendant laquelle il peut tenir.
```

### 3. Glossaire « Jours et heures PP (PP1, PP2) » : ne dit pas que la distinction a disparu

**Où** : `docs/GLOSSAIRE.md`, lignes 129-136.

**Problème** : depuis la PL 2026/2027, la CRE paramètre le mécanisme sur « 22 jours PP signalés
entre le 1er novembre de l'année N et le 31 mars de l'année N+1 », heures de 7 h à 10 h et de
17 h à 20 h (délibération 2026-43, § 3) : une seule catégorie de jours. Le titre et la phrase
« Dans le mécanisme d'origine, les jours PP1… » laissent penser que PP1 et PP2 existent encore.
Heures 7-10 h et 17-20 h : **exactes** (BP2025 *Fonctionnement*, note 38 : « [7h-10[ et
[17h-20h[ »). « Signalés la veille pour le lendemain » : exact (CRE 2026-43 : « le tirage des
jours PP s'effectue la veille pour le lendemain »).

**Correction prête à coller** (titre et 2e phrase) :

```
## Jours et heures PP {#plages-pp}
```

```
Dans le mécanisme d'origine, les jours PP1 servaient à calculer l'obligation des fournisseurs et les jours PP2, plus nombreux, à certifier les capacités ; le mécanisme centralisé, depuis la période de livraison 2026-2027, n'a plus qu'une catégorie de jours PP, 22 jours signalés entre le 1er novembre et le 31 mars.
```

(et ajouter en source : CRE, délibération n° 2026-43, § 3.)

### 4. « Combien ? » : « Leur état en novembre 2026 n'est pas publié » omet ce que RTE a publié en juin

**Où** : `docs/enquetes/combien.md`, lignes 63-64 ; même document cité par « Où ? » (l. 171-174,
p. 20).

**Problème** : RTE, note d'accompagnement SDDR en réponse à la CPDP (juin 2026), p. 20 : « RTE
s'est également engagé à lancer 5 grands projets fast-track […]. A date, 4 sites ont déjà fait
l'objet de la signature d'un engagement de raccordement. » L'état de novembre n'est pas publié,
c'est vrai, mais celui de juin l'est, et « Où ? » cite la même page sans ce passage. Garder le
mot de RTE (« engagement de raccordement ») : il ne dit pas s'il s'agit d'une PTF acceptée ou
d'un contrat.

**Correction prête à coller** :

```
   « [fast-track](glossaire:fast-track) », pour une durée limitée. En juin 2026, RTE écrivait que
   quatre d'entre eux avaient « déjà fait l'objet de la signature d'un engagement de
   raccordement », sans dire lesquels ni de quel engagement il s'agit
   {{source:rte-sddr-reponse-cpdp-2026|p. 20}} ; leur état en novembre 2026 n'est pas publié.
   Fouju figure à la fois parmi ces sites et à l'étage suivant, avec son contrat.
```

### 5. Accroche « Quel carbone ? » et message : « publié » au lieu de « publié par une institution »

**Où** : `docs/enquetes/carbone.md`, ligne 5 (« aucun facteur marginal récent n'est publié pour la
France, à notre connaissance ») ; `docs/MESSAGE.md`, ligne 128 (« le carbone marginal, qu'aucune
institution ne publie »).

**Problème** : l'enquête limite son constat aux institutions (« après une recherche non exhaustive
chez RTE, l'ADEME, la CRE et le ministère », l. 306-309 de `carbone.md`). Des fournisseurs de données commerciaux
et des travaux académiques publient des signaux « marginaux » pour la France. L'accroche élargit
le constat à tout le monde. Dans le message, « qu'aucune institution ne publie » oublie que RTE
et l'ADEME en ont publié un en 2007, ce que le paragraphe précédent dit lui-même.

**Corrections prêtes à coller** :

```
accroche: {{intensite_prod_rte_2025}} en moyenne pour la production française de 2025. C'est une moyenne : elle ne dit pas ce qu'émettrait une consommation ajoutée, et aucune institution ne publie de [facteur marginal](glossaire:facteur-moyen-marginal) récent pour la France, à notre connaissance.
```

`MESSAGE.md`, l. 127-129 : « le carbone marginal, dont aucune institution ne publie
d'estimation récente à notre connaissance, et que ce site ne sait pas encore estimer ».

### 6. 18 GW ou « près de 18 GW »

**Où** : accroche de `combien.md` (l. 5), `combien.md` l. 55, `MESSAGE.md` l. 48 : « 18 GW » ;
`ou.md` l. 152-153 : « près de 18 GW ». Citation de la source (`chiffres.yaml`, `dc_reserve_rte_2026_05`) :
« RTE avait réservé **près de** 18 GW ».

**Correction** : écrire « près de {{dc_reserve_rte_2026_05}} » dans l'accroche de « Combien ? »,
dans « Combien ? » et dans le message, comme dans « Où ? ».

### 7. Glossaire « Puissance réservée » : « PTF signée » ne recoupe pas « Combien ? » et brouille « signée »

**Où** : `docs/GLOSSAIRE.md`, lignes 283-285. « Combien ? » (l. 48-50) définit la réservation par
« l'acceptation d'une PTF de RTE et le versement d'un premier acompte » ; le glossaire, par une
« PTF signée ». L'entrée suivante, « Puissance signée », désigne le **contrat** de
raccordement. Une lectrice qui parcourt le glossaire voit « signée » à deux étages.

**Correction prête à coller** :

```
Capacité d'accès au réseau réservée par le gestionnaire pour un projet, une fois sa proposition technique et financière ([PTF](glossaire:ptf)) acceptée et le premier acompte versé. C'est un droit d'accès, avec une place dans la file d'attente ; il n'engage pas à consommer et peut être abandonné. À ne pas confondre avec la [puissance signée](glossaire:puissance-signee), celle du contrat de raccordement.
```

### 8. Critère de sécurité d'approvisionnement : « Quand ? » n'en donne que la moitié

**Où** : `docs/enquetes/quand.md`, lignes 45-47 (« une espérance de trois heures de défaillance par
an »). Le glossaire (« Adéquation ») et la CRE (2026-43, § 3 : « double critère public de
sécurité d'approvisionnement de 2 heures de délestage et 3 heures de défaillance ») donnent les
deux.

**Correction** : « …[critère public de sécurité d'approvisionnement](glossaire:adequation), une
espérance de trois heures de défaillance et de deux heures de délestage par an ».

### 9. Glossaire « REMIT » : « sans délai » n'est pas la lettre de l'article 4

**Où** : `docs/GLOSSAIRE.md`, ligne 296. L'article 4, § 1, du règlement 1227/2011 dit « de manière
effective et en temps utile ». Depuis le règlement (UE) 2024/1106 (11 avril 2024, JO L du
17.4.2024, **confirmé** sur EUR-Lex), la publication passe par des plateformes d'informations
privilégiées (IIP). La référence 2024/1106 est exacte.

**Correction** : « …et oblige les acteurs à rendre publiques, de manière effective et en temps
utile, les informations privilégiées, dont… ».

### 10. Page Méthode : « deux producteurs » et fichiers non servis

**Où** : `/methode`, section « Données » (rendu du build), « Les séries horaires (hero de
l'accueil, enquêtes à venir) viennent de deux producteurs ». Les séries comptent un troisième
producteur, EDF (indisponibilités REMIT, colonne `nucleaire_disponible`, décrite dans le tableau
juste en dessous), et elles servent déjà à « Quand ? », « Quel carbone ? » et au simulateur. La
copie de `LISEZMOI.md` renvoie à `../meta.json` et `../systeme_horaire.parquet`, que le site ne
sert pas (seuls `/donnees/horaire/` et `/donnees/prix/` existent).

**Correction** : « Les séries horaires (accueil, « Quand ? », « Quel carbone ? », simulateur)
viennent de trois producteurs, sous licence ouverte : RTE, EDF et, pour les prix,
Bundesnetzagentur / SMARD via energy-charts. » Ajouter une ligne pour EDF (opendata.edf.fr,
Licence Ouverte 2.0, date d'extraction) et préciser que `meta.json` et `systeme_horaire.parquet`
sont dans le dépôt (`data/export/`), lien GitHub.

### 11. « Où ? » : accroche sans date et site de Dunkerque nommé de deux façons

**Où** : `docs/enquetes/ou.md`, l. 5 : « La carte des zones favorables qu'il annonçait en février
2025 n'est pas parue, à notre connaissance ». L'accueil et l'enquête datent ce constat (« au 26
novembre 2026 »), l'accroche ne le fait pas. Le texte (l. 171-172) nomme « Bourbourg ». La note
du chiffre `dc_fasttrack_prereserve_2025_12`, affichée sur la même page, dit « Dunkerque ». La
fiche RTE de décembre 2025 parle de la « zone du Grand Port Maritime de Dunkerque », la note
RTE de juin 2026 (p. 20) de « Bourbourg ».

**Corrections** : accroche « …n'est pas parue au 26 novembre 2026, à notre connaissance. » ;
`chiffres.yaml`, périmètre de `dc_fasttrack_prereserve_2025_12` : « …Escaudain, Bourbourg (zone
Grande Industrie du Grand Port Maritime de Dunkerque) (700 MW chacun)… ».

### 12. Simulateur : le gabarit invisible porte un scénario fictif

**Où** : `site/src/lib/simulateur/Simulateur.svelte`, l. 667-668 (`GABARIT`). Le HTML servi contient,
masqué par CSS et `aria-hidden`, « consommation ajoutée de 12,5 GW à toutes les heures sauf
pendant les 500 heures […] (au moins 45,3 GW). Froid supplémentaire de 11,5 °C […] du 28 déc.
2024 au 4 janv. 2025 : 27,6 GW ». Ce texte reste visible en mode lecture du navigateur, sans
CSS, à la copie de la page et pour les moteurs de recherche. Il ressemble à un résultat (dates
qui débordent sur 2024 pour l'année 2025, seuil chiffré).

**Correction** : un gabarit sans chiffres plausibles (par exemple des tirets, ou la phrase des
défauts répétée), ou une hauteur réservée en CSS (`min-height` en `lh`).

---

## Ce qui a été vérifié et tient

- **Chiffres repris d'une page à l'autre** (accueil, message, quatre enquêtes, simulateur) :
  mêmes valeurs, unités et périodes (tous viennent de `chiffres.json`). Recalculs en clair du
  message : (21 − 4) / 8,76 = 1,94 GW ; (28) / 8,76 = 3,20 GW ; 1,9 / 10 ≈ 1/5, 3,2 / 8 = 2/5 ;
  5 GW × 8 760 h = 43,8 TWh, × 52 % = 22,8 TWh, × 55 % = 24,1 TWh ; 21/442 ≈ 4,8 %, 32/442 ≈
  7,2 % (« environ 5 à 7 % »). Tout boucle.
- **Dates croisées** : maximum de charge résiduelle et heure la plus carbonée le 14/01/2025 au
  matin (« Quand ? », « Quel carbone ? », `pointe_conso_2025`) ; disponibilité 2022 de 54,2 %
  (« Quand ? » et « Quel carbone ? ») ; 20 % (décembre 2025) et 22 % (mars 2026) de taux
  d'utilisation, présentés de la même façon dans « Combien ? » et « Quand ? » ; 513 heures
  négatives en 2025 (accueil, décompte du site = RTE ; « Quand ? »).
- **Catégories** : réservée / pré-réservée / signée / raccordée / appelée tenues dans « Combien ? »,
  le glossaire et « Où ? » (hors F1 et point 7) ; moyen / marginal tenu partout (accroche et
  message disent « moyenne », le CSV `taux_co2` dit « pas un facteur marginal »).
- **Glossaire, à la source** : critère 3 h de défaillance + 2 h de délestage (BP2025 p. 2 ; CRE
  2026-43) ; mécanisme centralisé depuis la PL 2026/2027, courbe de demande fixée par le
  ministre, taxe répartie selon la consommation (CRE 2026-43, § 1.2 ; RTE, rapport de
  paramétrage, p. 3) ; heures PP 7-10 h et 17-20 h (note 38) ; REMIT modifié par 2024/1106 ;
  S3REnR élaboré par RTE en accord avec les gestionnaires de distribution, ouvrages à créer ou
  à renforcer, capacités réservées et quote-part (L. 321-7) ; corrélation temporelle mensuelle
  jusqu'à fin 2029 puis horaire (2023/1184, art. 6, cohérent avec « Quel carbone ? ») ;
  délibération fast-track n° 2025-120 du 7 mai 2025 (cohérent avec « Où ? ») ; SDDR synthèse
  p. 19 : « ~ 50 — Le nombre de postes capables d'accueillir 250 MW », repris pareil dans le
  message, l'accroche et « Où ? ».
- **Liens** : aucun lien interne cassé sur les neuf pages servies (pages et ancres, renvois
  `/methode#g-…` compris) ; liens externes du glossaire et de « À toi » : tous en HTTP 200.
  Aucun `{{…}}`, `glossaire:` ou `:::` non résolu dans le HTML.

## Non vérifié

- **Rendu des sources de 19 h 23** : non reconstruit par l'agent (consigne : ne rien modifier).
  Accroches, « À retenir » et nouvelles entrées du glossaire (« Consommation plate », « Nucléaire
  disponible non produit ») lues en source seulement.
- **Export Enedis réel** (unité, convention de début ou de fin d'intervalle) : espace client non
  accessible ; F4 pose la question sans trancher.
- **Garanties d'origine** : définition conforme à l'article 19 de la directive 2018/2001. La
  modification de cet article par la directive 2023/2413 (granularité, horodatage) n'a pas été
  relue. Si elle autorise des garanties d'origine plus fines que le MWh ou datées à l'heure,
  « sans contrainte d'heure » doit devenir « sans correspondance horaire imposée ».
- **CFE 24/7** : gouvernance du *24/7 Carbon-Free Energy Compact* (ONU-Énergie, SEforALL) non
  relue ; la définition du score est conforme à l'usage courant.
- **« comme RTE »** pour la moyenne simple des quatre quarts d'heure (glossaire « Prix
  day-ahead », page Méthode) : non relu à la source.
- **Résultats du simulateur en JavaScript** : pas de navigateur ; seuls le texte rendu côté
  serveur et le code du gabarit ont été lus.
- **« Où ? »** : relu pour sa cohérence seulement ; la relecture adverse en cours fait foi pour le
  reste.

---

## Vérification des corrections

Relu le 26/11/2026 vers 19 h 40 : `git diff HEAD -- docs/ site/src/`, les sources de 19 h 29-19 h 31
(comparées ligne à ligne à la copie relue à 19 h 24), et le build de 19 h 35 servi sur
`localhost:4318` (accueil, Méthode avec le glossaire, « À toi », cartes de l'accueil lues dans le
HTML). Dernière entrée de `making-of/ERREURS.md` : conforme (ce qui était faux, qui l'a repéré,
garde-fou), sans embellissement.

**Verdict : envoyable après trois retouches** (R1 à R3 ci-dessous, textes prêts à coller), puis
un nouveau build. R1 est une erreur nouvelle sur l'accueil. R2 rend inexact le journal des
versions du message. Aucune ne touche un chiffre.

### Point par point

| Point | Correction | Verdict |
|---|---|---|
| F1 accroche « Combien ? » | « Les data centers en service sur des sites dédiés, eux, ont consommé… » ; « Près de 18 GW » | **Juste** (rendu vérifié) |
| F2 « 52 % au plus » | Carte : « 52 % à 55 % au plus », puis quel chiffre correspond à quelle hypothèse ; message : « le plafond dépend de la frontière, fixée par EDF » ; glossaire « Nucléaire disponible non produit » : « à frontière donnée… » ; « À retenir » : « environ la moitié, au plus » | **Juste**. Le détail du message garde « avec la disponibilité déclarée par EDF, 52 % au plus » : c'est correct, puisque la condition est dite |
| F3 « À retenir » sans RTE | Résultat de RTE ajouté (lente : pas de besoin ; rapide : 1 à 6 GW en 2035) | **Juste**, réserve de forme R4 |
| F4 unité Linky | Wh puis ÷ 1 000 ; début ou fin de demi-heure posé en question | **Juste** |
| F5 prix 2026 | Années closes sur le site, sinon energy-charts | **Juste** (`/donnees/horaire/` sert bien 2015 à 2025) |
| Forme 1 ETS | Mon texte, à l'identique (`carbone.md` l. 285-293) | **Juste** : conforme aux considérants 3 et 3a et à l'article 1er du doc. 14944/26 |
| Forme 2 coefficients | Repris | **Juste** (rapport de paramétrage, p. 5-7 et 10) |
| Forme 3 PP1/PP2 | Repris, titre sans « (PP1, PP2) » | **Juste** ; la ligne Source ne couvre pas les « 22 jours » (R5) |
| Forme 4 fast-track | Repris (`combien.md` l. 63-67) | **Juste** |
| Forme 5 « institution » | Accroche et message repris | **Juste** |
| Forme 6 « près de 18 GW » | Accroche, « Combien ? » l. 54, message l. 53-55 | **Juste** |
| Forme 7 puissance réservée | Repris | **Juste** |
| Forme 8 critère | `quand.md` l. 46-47 : 3 h de défaillance et 2 h de délestage | **Juste** (BP2025 *Fonctionnement*, p. 2) |
| Forme 9 REMIT | « de manière effective et en temps utile » | **Juste** |
| Forme 10 page Méthode | **Pas appliqué** : `site/src/routes/methode/+page.svelte` l. 85 (modifié à 19 h 16) et le build de 19 h 35 disent encore « (hero de l'accueil, enquêtes à venir) viennent de deux producteurs » | **Restant** (R3) |
| Nouvelle entrée « Zone de mutualisation » | Articles L. 342-2 et L. 342-18 (cités par la CRE, délibération 2026-173, § 3.4) ; décret n° 2024-524 du 7 juin 2024 (confirmé : texte d'application de ces articles, quote-part = coût des ouvrages mutualisés ÷ capacité offerte) | **Juste** sur les références. Contenu des fichiers de RTE non relu ici (relecture de « Où ? ») |

### R1 (fond, erreur nouvelle). Carte « Simulateur » de l'accueil : « maximum de consommation » au lieu de maximum de charge résiduelle

**Où** : `site/src/routes/+page.svelte`, l. 69, rendu sur l'accueil : « les heures au-delà du maximum
de consommation observé ». La formulation vient de la relecture « non spécialiste »
(`2026-11-26-accueil-non-specialiste.md`, l. 288), qui notait elle-même, l. 295 : « À vérifier ».

**Problème** : le simulateur compte les heures où la **charge résiduelle** (consommation − éolien −
solaire − nucléaire disponible) dépasse son maximum de l'année et le maximum 2015-2025
(`phrases.ts`, l. 158-255, `sim.rn_max_mw` ; « Quand ? » l. 208-217). Il ne compte pas les
heures au-delà du maximum de consommation. Ce n'est pas la même grandeur : en 2025, le maximum
de charge résiduelle est de 31,4 GW, la pointe de consommation de 88 GW. Une experte qui ouvre le
simulateur depuis cette carte voit la contradiction tout de suite.

**Correction prête à coller** (l. 68-69) :

```
        et regarde ce qui change&#8239;: l’énergie, la part trouvée dans le nucléaire disponible non produit,
        les heures où la <a class="glossaire" href="/methode#g-charge-residuelle">charge résiduelle</a> dépasse son maximum observé, les prix. Les hypothèses sont affichées,
```

(Si le lien du glossaire est déjà donné plus haut dans la carte, garder le texte sans le lien.)

### R2 (forme, importante). « Ce qui a changé » dit qu'aucune conclusion de la version 1 ne change : c'est devenu faux

**Où** : `docs/MESSAGE.md`, entrée « Version 2 » de « Ce qui a changé ».

**Problème** : la version 1 disait du réseau local : « ce que peut recevoir chaque poste électrique,
que personne, à notre connaissance, ne publie en données ouvertes ». La version 2 corrige ce
constat : RTE publie, pour quelques zones de mutualisation, la capacité d'accueil en soutirage
offerte, attribuée et restante (erreur consignée dans `ERREURS.md`, « Où ? : trois absences
qui n'en étaient pas »). Le site s'engage à dire ce qui change d'une version à l'autre. Une
phrase qui affirme le contraire le jour même d'une correction est la première chose qu'une
lectrice attentive vérifiera.

**Correction prête à coller** (fin de l'entrée « Version 2 ») :

```
  documentés comme des manques). Une conclusion de la version 1 est
  corrigée : elle disait que personne ne publie ce que peut recevoir un
  poste électrique ; RTE le publie pour quelques zones où il renforce le
  réseau pour plusieurs clients (making-of, erreurs du 26/11). Aucun
  chiffre de la version 1 ne change.
```

### R3 (forme). Page Méthode : « deux producteurs », « enquêtes à venir »

Inchangé depuis le rapport (point de forme 10). **Correction prête à coller**
(`site/src/routes/methode/+page.svelte`, l. 85) :

```
    Les séries horaires (accueil, « Quand ? », « Quel carbone ? », simulateur) viennent de trois producteurs, sous
```

puis ajouter, après le paragraphe RTE, une ligne : « Disponibilité nucléaire déclarée : EDF,
indisponibilités REMIT (opendata.edf.fr), Licence Ouverte 2.0. » La date d'extraction est dans
`meta.json`. Les renvois `../meta.json` de la copie de `LISEZMOI.md` restent sans cible sur le
site : ajouter sous le tableau « (fichiers du dépôt, `data/export/`, sur GitHub) ».

### R4 (forme). « À retenir » : « hypothèses de référence » ne couvre pas la fourchette de 1 à 6 GW

`docs/MESSAGE.md`, « À retenir » : « Avec ses propres trajectoires, data centers compris, et ses
hypothèses de référence, RTE ne trouve pas de besoin […] en décarbonation lente, et un besoin de
1 à 6 GW en 2035 en décarbonation rapide. » En décarbonation rapide, la fourchette de 1 à 6 GW
**est** la variation du rythme des renouvelables (R1 à R3, BP2025 *Fonctionnement*, p. 28). Elle ne
découle pas d'une seule hypothèse de référence. **Correction** : « …et un besoin de
{{besoin_capacites_rapide_2035}} en 2035 en décarbonation rapide, selon le rythme des
renouvelables. »

### R5 (forme). Glossaire « Jours et heures PP » : la source ne porte pas les 22 jours

La ligne Source (BP2025 *Fonctionnement*, note 38) donne les heures, pas la fin de PP1/PP2 ni les
22 jours. Ces deux faits viennent de la délibération CRE n° 2026-43, § 3. Le format du glossaire
n'admet qu'une ligne Source : citer la CRE dans la phrase. **Correction** : « …n'a plus qu'une
catégorie de jours PP, 22 jours signalés entre le 1er novembre et le 31 mars (CRE, délibération
n° 2026-43). »

### Rien d'autre de nouveau

Accueil rendu relu en entier, notes retirées : chiffres et notes à jour (« Près de 18 GW »,
« 52 % à 55 % au plus », « 1 à 6 GW »). Aucun `{{…}}` ni lien `glossaire:` non résolu. Lien
« Ouvrir le simulateur avec 5 GW » → `/simulateur?x=5`, paramètre `x` lu par
`simulateur/etat.ts`. Glossaire : 37 entrées rendues. « À toi » rendu conforme à la source.
Non revérifié : « Où ? » (relecture dédiée) et le gabarit du simulateur (mis au backlog).
