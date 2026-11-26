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
- [ ] Glossaire replié (merit order, capture price, PPA, TURPE, CFE 24/7) ; y lier depuis l'accueil « prix de gros », « day-ahead », « prix négatif », « poste électrique » (brief, 2026-11-25 ; relecture, 2026-11-26)
- [ ] Méthode : préciser la cote A quand le recoupement porte sur un calcul (décompte des heures négatives : RTE et le site comptent sur les mêmes résultats d'enchère, Nord Pool chez RTE le 26/06/2024) (relecture, 2026-11-26)
- [ ] Jeton ENTSO-E : compte créé par l'auteur le 26/11, jeton attendu sous ~3 jours, toujours en attente le 26/11 après la session 1 et au début de la session 2 ; à déposer dans `source/entsoe_token`, puis brancher prix et mix des voisins (enquête carbone) (user:auteur, 2026-11-26)
- [ ] `pc check` : recompter les heures négatives sur les CSV publiés (pas seulement avant arrondi) (claude, 2026-11-26)
- [ ] Composant « en chantier » : encart standard pour toute enquête ou module dont une source manque (donnée, raison, ce qui viendra) (user:auteur, 2026-11-26)
- [→Étape 3] Recette sur téléphone de https://pdc.technoperchoir.fr (heatmap au doigt, notes repliées, tableaux) (claude, 2026-11-26)
- [→Étape 3] Accueil : la question d'abord et visible sans défiler, une phrase sur le pourquoi de l'heure par heure, puis la heatmap des prix ; aujourd'hui « obscur » pour un non-spécialiste (user:auteur, 2026-11-26)
- [→Étape 3] Making-of : décisions et erreurs en fiches (formats imposés → éléments d'interface), journal compact avec détail dépliable, brief intégré au journal et replié (user:auteur, 2026-11-26)
- [ ] Relecture « lecteur non spécialiste » en plus de la relecture « lectrice experte » avant publication d'une page (accroche, enchaînement, jargon hors glossaire) : l'auteur joue ce rôle aujourd'hui, un agent pourrait le préparer (claude, 2026-11-26)
- [ ] Making-of : garder les sauts de ligne d'une demande citée de l'auteur (aujourd'hui fondus au rendu, comme en Markdown standard) (relecture, 2026-11-26)
- [ ] Site : commentaire de `heatmap.ts` (« au centime entre −1 et 1 ») à corriger ; renommer `ECRETAGE` / `ecretees` ; « 1er » en exposant (claude, 2026-11-26)
- [ ] `pc check` : le contrôle de jonction historique / liste courante REMIT échouera vers le 07/12/2026 si EDF ne republie pas son historique (trimestriel) : relancer `pc download edf_remit` et voir (claude, 2026-11-26)
- [ ] Exports : 14,0 Mo pour une limite de test à 15 Mo ; décider avant d'ajouter une colonne (parquet seul, ou découpage) (claude, 2026-11-26)
- [ ] REMIT : biais de +0,1 à +0,4 pt du taux reconstruit sur RTE, inexpliqué ; l'heure répétée du passage à l'heure d'hiver est lue comme sa première occurrence (claude, 2026-11-26)
