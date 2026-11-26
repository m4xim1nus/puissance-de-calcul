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
- [ ] Relecture de l'auteur : retours à traiter en ouverture de session 2
      (chaque retour sur un chiffre se vérifie à la source avant correction)

## Étape 3 : « Quand ? » + simulateur

Ordre prévu pour la session 2 :

1. **Retours de relecture de l'auteur** sur l'étape 2. On les cite dans
   le journal, on les traite, et on consigne dans `ERREURS.md` ce qui
   en relève.
2. **Jeton ENTSO-E** : s'il est arrivé (`source/entsoe_token`, jamais
   versionné), on vérifie l'accès avec un agent Sonnet, puis on branche
   la source dans `pc download` (prix et mix des voisins, flux
   transfrontaliers). Il sert à l'enquête carbone et au recoupement des
   prix energy-charts. Sinon, on ne fait rien : l'étape 3 n'en dépend pas.
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
