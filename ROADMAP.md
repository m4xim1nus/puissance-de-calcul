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
boucle à 0,002 % avec RTE hors Corse ; heures à prix négatif identiques
à RTE) ; data centers **riche mais documentaire** (aucun registre, file
RTE en agrégats) ; réseau **pauvre** (coordonnées des postes RTE
retirées, aucune capacité de soutirage publiée). Arbitrages de l'auteur :
« Combien ? » d'abord, pas de thèse avant les enquêtes, aucun contact
extérieur pour l'instant, jeton ENTSO-E.

## Étape 2 : premier livrable public — en cours

- [x] Référentiel des chiffres (`pipeline/referentiels/`, `pc/chiffres.py`) :
      unités contrôlées par nature de grandeur, confiance A/B/C, contraintes
      d'ordre ; export `data/export/chiffres.json`
- [x] Texte de l'enquête « Combien ? » (`docs/enquetes/combien.md`)
- [ ] Pipeline des séries horaires (éCO2mix, prix) + `pc check` (agent en cours)
- [ ] Système visuel, page `/combien`, page `/methode` (agent en cours)
- [ ] Hero de l'accueil : heatmap horaire 2025
- [ ] Relecture adverse « lectrice experte » de la page avant publication
- [ ] Caviardage du making-of validé par l'auteur, puis dépôt public et
      Cloudflare Pages (`puissance-de-calcul.technoperchoir.fr`, à confirmer)

## Étape 3 : « Quand ? » + simulateur

À détailler après l'étape 2.
