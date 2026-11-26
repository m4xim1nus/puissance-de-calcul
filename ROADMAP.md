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
- [ ] Cloudflare Pages relié au dépôt, `pdc.technoperchoir.fr` (l'auteur)
- [ ] Recette sur téléphone du site en ligne, puis relecture de l'auteur

## Étape 3 : « Quand ? » + simulateur

À détailler après l'étape 2.
