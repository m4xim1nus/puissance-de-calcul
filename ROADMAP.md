# Roadmap

Projet sans calendrier engageant. Étapes jusqu'à un premier livrable
visible, puis des cycles courts. Chaque étape se termine par un livrable
relu par l'auteur. Les idées non planifiées vont dans `BACKLOG.md`.

Principe du brief : un premier livrable vite visible, puis on
approfondit. **Plusieurs enquêtes justes valent mieux que toutes les
enquêtes à moitié.**

## Étape 0 : cadrage ✅ (2026-11-25)

Dépôt, conventions alignées sur quifaitlaloi, making-of ouvert, brief
publié (avec caviardage visible des détails personnels).

## Étape 1 : spike sources ✅ (2026-11-26)

Trois spikes (`docs/spike/`) et une contre-vérification adverse des
chiffres clés, qui a trouvé deux erreurs de fond avant publication
(`making-of/ERREURS.md`). Verdicts : séries horaires **GO** (éCO2mix
boucle à 0,01 % près avec ODRÉ hors Corse en 2024-2025, à 0,35 % près avant ;
heures à prix négatif identiques à RTE) ; data centers **riche mais documentaire** (aucun registre, file
RTE en agrégats) ; réseau **pauvre** (coordonnées des postes RTE
retirées, aucune capacité de soutirage publiée). Arbitrages de l'auteur :
« Combien ? » d'abord, pas de thèse avant les enquêtes, aucun contact
extérieur pour l'instant, jeton ENTSO-E.

## Étape 2 : premier livrable public — en cours

- [x] Référentiel des chiffres (`pipeline/referentiels/`, `pc/chiffres.py`) :
      unités contrôlées par nature de grandeur, confiance A/B/C, contraintes
      d'ordre ; export `data/export/chiffres.json`
- [x] Texte de l'enquête « Combien ? » (`docs/enquetes/combien.md`)
- [x] Pipeline des séries horaires (éCO2mix, prix) + `pc check` : 7 contrôles
- [x] Système visuel, page `/combien`, page `/methode`
- [x] Hero de l'accueil : heatmap horaire des prix 2015-2026
- [x] Relecture adverse « lectrice experte » : 27 points, dont 5 de fond, tous traités
- [x] Caviardage validé par l'auteur, historique réécrit, dépôt public
      `m4xim1nus/puissance-de-calcul`, CI verte
- [x] Cloudflare Pages relié au dépôt : en ligne sur
      https://pdc.technoperchoir.fr (2026-11-26)
- [ ] Recette sur téléphone du site en ligne
- [x] Relecture de l'auteur (2026-11-26, session 2) : « Combien ? » et
      « Méthode » sans remarque ; aucun retour sur un chiffre. Deux
      retours de lisibilité, traités en étape 3 (point 1)

## Étape 3 : « Quand ? » + simulateur — en cours (session 2)

Ordre de la session 2 :

1. **Retours de relecture de l'auteur** (cités dans le journal,
   session 2) :
   - [x] **Accueil** (en ligne le 26/11, après relecture adverse) : la question d'abord, visible sans défiler ; une
         ou deux phrases qui disent pourquoi regarder l'électricité
         heure par heure et ce que montre la carte des prix ; puis la
         heatmap, puis les enquêtes. Lisible par un non-spécialiste sans
         rien retirer pour l'experte ;
   - [x] **Making-of** (en ligne le 26/11 ; fidélité aux sources testée en CI) : rendu structuré au lieu du Markdown à plat.
         Décisions en fiches (date, décision, raisons, étiquette « l'auteur
         / Claude », filtre par auteur de la décision) ; erreurs en fiches
         (Faux / Repéré par / Correction / Garde-fou, étiquette de qui l'a
         repérée) ; journal compact (en-tête par session : date, durée,
         agents, coût ; demande citée visible ; détail dépliable) ; brief
         intégré au journal (session 1), replié par défaut. Les fichiers
         Markdown restent la source unique : le site les analyse, les
         formats imposés deviennent un contrat testé ;
   - [ ] Recette sur téléphone (reportée de l'étape 2), après ces deux
         chantiers.
2. **Jeton ENTSO-E** : pas arrivé au 26/11 matin. Point sauté ; l'étape 3
   n'en dépend pas. Quand il arrive (`source/entsoe_token`, jamais
   versionné) : vérification d'accès par un agent Sonnet, puis
   branchement dans `pc download` (prix et mix des voisins, flux
   transfrontaliers), pour l'enquête carbone et le recoupement des prix
   energy-charts.
3. **Enquête « Quand ? »** (`/quand`) : à quelles heures le système a de
   la marge et à quelles heures il n'en a pas. Monotones de charge et de
   prix, heures de tension et heures de surplus, ce qu'une charge plate
   de X GW change à ces heures. Données déjà disponibles : éCO2mix
   horaire 2015-2026 et prix. Spike Opus pour les sources de marge
   (tension, écrêtement, effacements), puis texte, référentiel,
   relecture adverse.
4. **Simulateur** (`/simulateur`) : un moteur TS dans le navigateur, et
   une référence Python dans `pipeline/` qui doit donner les mêmes
   résultats (test croisé). Profil de charge plat par défaut,
   hypothèses affichées et modifiables. Le simulateur dit ce qu'il ne
   modélise pas (réseau local, marginal).
5. Relecture adverse « lectrice experte » de chaque page avant
   publication.
