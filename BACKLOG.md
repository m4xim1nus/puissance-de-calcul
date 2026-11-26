# Backlog

File d'attente : cycles à venir, idées, tâches refusées. Rien de livré.
Une ligne par item :

```
- [TAG] description courte (origine, date)
```

**Tags** : `[ ]` à trier, `[→Nom]` rangé dans un cycle, `[creuser]` à
réfléchir avant d'arbitrer, `[refusé]` tranché négatif. **Origines** :
`user:auteur`, `claude`, `brief`.

---

## À trier

- [ ] Onglet « À toi » : missions par difficulté croissante (Linky, hypothèse du simulateur, conviction à contredire) (brief, 2026-11-25)
- [ ] Glossaire replié (merit order, capture price, PPA, TURPE, CFE 24/7) ; y lier depuis l'accueil « prix de gros », « day-ahead », « prix négatif », « poste électrique », et depuis « Quand ? » et le simulateur « REMIT », « services système », « puissance certifiée », « plages PP », « solde des échanges » (brief, 2026-11-25 ; relecture, 2026-11-26)
- [ ] Méthode : préciser la cote A quand le recoupement porte sur un calcul (décompte des heures négatives : RTE et le site comptent sur les mêmes résultats d'enchère, Nord Pool chez RTE le 26/06/2024) (relecture, 2026-11-26)
- [→Session 3] Jeton ENTSO-E : **arrivé** le 26/11, rangé dans `source/entsoe_token` (non versionné), non testé. À faire : vérifier l'accès (agent Sonnet), brancher dans `pc download` prix et mix des voisins et flux transfrontaliers, pour l'enquête carbone, le recoupement des prix energy-charts et la question « qui servirait une consommation ajoutée » de « Quand ? » (user:auteur, 2026-11-26)
- [ ] `pc check` : recompter les heures négatives sur les CSV publiés (pas seulement avant arrondi) (claude, 2026-11-26)
- [ ] Composant « en chantier » : encart standard pour toute enquête ou module dont une source manque (donnée, raison, ce qui viendra) (user:auteur, 2026-11-26)
- [x] Recette sur téléphone de https://pdc.technoperchoir.fr : faite par l'auteur le 26/11, « ok » (claude, 2026-11-26)
- [→Étape 3] Accueil : la question d'abord et visible sans défiler, une phrase sur le pourquoi de l'heure par heure, puis la heatmap des prix ; aujourd'hui « obscur » pour un non-spécialiste (user:auteur, 2026-11-26)
- [→Étape 3] Making-of : décisions et erreurs en fiches (formats imposés → éléments d'interface), journal compact avec détail dépliable, brief intégré au journal et replié (user:auteur, 2026-11-26)
- [ ] Relecture « lecteur non spécialiste » en plus de la relecture « lectrice experte » avant publication d'une page (accroche, enchaînement, jargon hors glossaire) : l'auteur joue ce rôle aujourd'hui, un agent pourrait le préparer (claude, 2026-11-26)
- [ ] Making-of : garder les sauts de ligne d'une demande citée de l'auteur (aujourd'hui fondus au rendu, comme en Markdown standard) (relecture, 2026-11-26)
- [ ] Site : commentaire de `heatmap.ts` (« au centime entre −1 et 1 ») à corriger ; renommer `ECRETAGE` / `ecretees` ; « 1er » en exposant (claude, 2026-11-26)
- [ ] `pc check` : le contrôle de jonction historique / liste courante REMIT échouera vers le 07/12/2026 si EDF ne republie pas son historique (trimestriel) : relancer `pc download edf_remit` et voir (claude, 2026-11-26)
- [ ] Exports : 14,0 Mo pour une limite de test à 15 Mo ; décider avant d'ajouter une colonne (parquet seul, ou découpage) (claude, 2026-11-26)
- [ ] REMIT : biais de +0,1 à +0,4 pt du taux reconstruit sur RTE, inexpliqué ; l'heure répétée du passage à l'heure d'hiver est lue comme sa première occurrence (claude, 2026-11-26)
- [ ] Référentiel : la règle « confiance A = autre éditeur » compare les éditeurs comme des chaînes (« RTE (open data ODRÉ) » ≠ « RTE ») ; normaliser l'éditeur, test à l'appui (claude, 2026-11-26)
- [ ] éCO2mix : écart de bilan moyen de −65 à −80 MW depuis 2021 (quelques MW avant), et saut du gaz contre ses sous-filières ; cause non établie (batteries ?) (claude, 2026-11-26)
- [ ] Simulateur : règle d'effacement réaliste (seuil connu à l'avance, ex. celui de l'année précédente, et budget d'heures), à spécifier ; la v1 ne donne qu'une borne basse à prévision parfaite (relecture, 2026-11-26)
- [ ] Simulateur : les textes `site/src/lib/simulateur/*.md` recopient des passages de « Quand ? » ; tirer les phrases de fond d'une source unique (claude, 2026-11-26)
- [→Session 3] « Quand ? » et simulateur : chiffrer la limite « froid extrême » (pointe record de février 2012 et gradient de thermosensibilité RTE au référentiel ; curseur « vague de froid » dans le simulateur) ; écarté de la v1 faute d'entrée sourcée (relecture P8, 2026-11-26 ; plan validé par l'auteur, 2026-11-26)
- [→Session 3] Éditorial : les deux enquêtes sont faites ; l'auteur demande s'il est temps d'un discours tranché et soutenu (« ou déjà fait ? contraire à ce qui était prévu ? »). Rien n'est fait ; la décision du 26/11 prévoyait d'écrire le message principal après deux enquêtes. À proposer à l'auteur, qui tranche le fond (user:auteur, 2026-11-26)
- [→Session 3] Simulateur, forme : la page « fait enquête à la lecture », l'outil est noyé entre un long préambule et une longue suite ; il ne devrait pas défiler (tenir sur un écran : réglages et résultats ensemble ; préambule et lecture repliés ou ailleurs). Fond, données et texte jugés bons (user:auteur, 2026-11-26)
- [ ] Message principal (`docs/MESSAGE.md`) : le réviser à la fin des enquêtes carbone, « Où ? » et prix, dire sur la page ce qui a changé, et dater chaque version (user:auteur, 2026-11-26)
- [→Session 3] Making-of : section « En bref » en tête, d'un coup d'œil, pour une lectrice à l'aise avec les chiffres mais pas avec le développement : outils, temps de travail de l'IA, temps de l'auteur, jetons produits, « pages » écrites par l'auteur, vision d'ensemble (user:auteur, 2026-11-26)
- [→Session 3] « Quand ? » : estimer l'écrêtement (borne de la surestimation de la charge résiduelle aux heures de surplus, production renoncée publiée par RTE répartie sur les heures à prix négatif) (user:auteur, 2026-11-26)
- [→Session 3] Simulateur : plancher de nucléaire non mobilisable (1 GW, choix du site) en curseur (user:auteur, 2026-11-26)
- [ ] Enquête « stocks » : énergie hydraulique disponible sur un épisode de froid long (remplissage des réservoirs ENTSO-E, hebdomadaire) ; enquête à part, pas un réglage (user:auteur, 2026-11-26)
