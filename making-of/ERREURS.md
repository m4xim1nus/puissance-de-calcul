# Erreurs de Claude

La section la plus importante pour un lecteur critique. Chaque erreur de
Claude ou de ses sous-agents est consignée **dès qu'elle est repérée**,
sans embellir : ce qui était faux, comment c'est sorti (qui l'a vu,
quel test), la correction, et ce qui change pour éviter la récidive.

Format :

```
### AAAA-MM-JJ — titre court
- **Faux** : …
- **Repéré par** : L'auteur / test / relecture d'un agent / Claude lui-même
- **Correction** : … (commit)
- **Garde-fou ajouté** : … (ou « aucun », dit franchement)
```

---

### 2026-11-26 — « 18 GW réservés, dont 7 GW avant 2030 » : deux chiffres d'origine différente combinés
- **Faux** : le rapport du spike data centers (agent Opus) écrivait « environ 18 GW réservés (mai 2026), dont environ 7 GW visent une mise en service avant 2030 ». Les 7 GW se rapportent aux **14 GW** contractualisés en **novembre 2025** (tableau de bord RTE, p. 25), et ils **incluent les sites déjà raccordés**. Les 18 GW (mai 2026) viennent d'une autre page RTE, qui ne donne pas de ventilation par échéance.
- **Repéré par** : la contre-vérification adverse (agent Opus distinct, qui avait reçu les affirmations et les sources mais pas les conclusions), avant toute publication.
- **Correction** : rapport de spike annoté ; le référentiel `chiffres.yaml` porte les deux chiffres séparément, chacun avec sa date.
- **Garde-fou ajouté** : chaque chiffre du site vient d'une entrée unique du référentiel, avec sa date et sa source. Une phrase qui rapproche deux chiffres doit citer les deux entrées.

### 2026-11-26 — Ratio 0,035 / 0,63 GW : deux cohortes et deux grandeurs différentes
- **Faux** : le même rapport classait parmi les « chiffres clés candidats » (confiance B) le rapprochement « 0,035 GW appelés au maximum en 2024 pour 0,63 GW mis à disposition ». Or le numérateur est une **pointe 2024** des data centers raccordés en **2022-2024**. Le dénominateur est une **capacité de raccordement** cumulée sur **2022-2025**, arrêtée au 15/11/2025. Le ratio (≈ 6 %) mélange les cohortes, les années et les grandeurs, et RTE ne le calcule nulle part. De plus, la barre du graphique RTE vaut ≈ 0,76 GW, pas 0,63 : la source est elle-même incohérente.
- **Repéré par** : la contre-vérification adverse.
- **Correction** : ratio retiré. Les deux chiffres sont gardés séparément, avec leurs définitions ; pour un taux d'utilisation, on cite celui que publie RTE (22 %, rapport moyen) en signalant qu'on ne le retrouve pas (≈ 15 % par le calcul simple).
- **Garde-fou ajouté** : le référentiel distingue `puissance_appelee_max`, `puissance_appelee_moyenne` et `puissance_raccordee` ; un ratio entre deux chiffres n'est publiable que si la source le publie ou si le site le calcule explicitement, en rendant visibles les deux termes.

### 2026-11-26 — Chiffres rapprochés sans leurs dates dans une question à l'auteur
- **Faux** : en soumettant les arbitrages à l'auteur, Claude (session principale) a écrit « environ 18 GW réservés chez RTE, 0,77 GW raccordés au transport, environ 0,11 GW appelés en moyenne ». Chaque chiffre est juste, mais ils ont trois dates différentes (mai 2026, fin 2025, année 2025), et la phrase les présentait comme une photographie unique. Sans conséquence sur la décision, mais c'est exactement le raccourci que le site s'interdit.
- **Repéré par** : Claude lui-même, en relisant la contre-vérification.
- **Correction** : aucune à faire dans le dépôt ; la pyramide du site affiche la date de chaque étage (`docs/CONCEPTION.md`, principe 3).
- **Garde-fou ajouté** : aucun mécanisme, seulement la règle de rédaction déjà écrite ; dit franchement.

### 2026-11-26 — Hypothèse « éCO2mix compte le CO2 seul » (mineure)
- **Faux** : le rapport du spike système avançait comme cause possible de l'écart d'intensité carbone que `taux_co2` compterait le CO2 seul, et non le CO2eq. La méthode RTE parle bien de CO2 équivalent (émissions directes). L'écart vient pour environ 3/4 (2024) à 9/10 (2025) de la production au fioul de la Corse, absente d'éCO2mix, et pour le reste des facteurs d'émission.
- **Repéré par** : la contre-vérification adverse. L'hypothèse était signalée comme non vérifiée : elle n'aurait pas été publiée en l'état.
- **Correction** : rapport annoté.
- **Garde-fou ajouté** : aucun nouveau.

### 2026-11-26 — Confiance A attribuée sans recoupement indépendant (mineure)
- **Faux** : en saisissant le référentiel, Claude a coté **A** la consommation brute 2024 (442,2 TWh). Son seul recoupement (somme éCO2mix + Corse) vient du même éditeur, RTE. La règle publiée exige un autre éditeur pour A.
- **Repéré par** : le test `test_referentiel_du_depot_est_valide` (règle codée dans `pc/chiffres.py`), avant tout commit.
- **Correction** : cotée B.
- **Garde-fou ajouté** : aucun nouveau ; c'est le garde-fou existant qui a joué.

### 2026-11-26 — « éCO2mix boucle à 0,002 % » : un constat d'une année généralisé à toutes
- **Faux** : le spike système avait vérifié la consommation éCO2mix contre les totaux ODRÉ pour **2024 et 2025** (écarts de 7 et 2 GWh) et en avait tiré des tolérances (± 0,05 % ; nucléaire < 5 MW). Claude a repris le constat sans année, dans une question à l'auteur et dans `ROADMAP.md` (« éCO2mix boucle à 0,002 % avec RTE hors Corse »). Sur 2015-2023, l'écart va de −0,33 % à +0,27 % (jusqu'à 1,5 TWh), et l'écart nucléaire de 56 à 126 MW.
- **Repéré par** : `pc check`, lancé sur toutes les années par l'agent du pipeline, qui n'a pas élargi les tolérances de lui-même et a signalé l'échec.
- **Correction** : tolérances recalibrées et justifiées dans `pc/check.py` (± 0,05 % pour 2024-2025, années de référence du site ; ± 0,5 % avant ; nucléaire relatif au niveau moyen, la convention d'horodatage étant vérifiée à part). L'écart reste affiché année par année. Sa cause n'est pas établie. `ROADMAP.md` est corrigé.
- **Garde-fou ajouté** : les contrôles portent sur toutes les années disponibles, pas sur l'année de calibration.

### 2026-11-26 — Trois imprécisions dans le texte de « Combien ? », écrit par Claude
- **Faux** :
  1. le texte présentait 0,8 TWh (transport) et 3 TWh (Enedis) comme la décomposition des « 4 à 5 TWh », alors que leur somme (3,8 TWh) tombe sous la fourchette ;
  2. il écrivait « sur les réservations de novembre 2025, 7 GW visaient une mise en service avant 2030 », et le référentiel contenait la contrainte « 7 GW ≤ 14 GW, motif : "dont" ». Or les 7 GW comptent les sites déjà raccordés, que les 14 GW excluent : ce n'est pas une part des réservations. Claude avait pourtant lu cette précision dans la contre-vérification ; il a suivi le « dont » de la source ;
  3. les 0,9 GW d'Enedis étaient rangés sans réserve parmi les puissances « raccordées », alors que la source dit seulement « en fonctionnement ».
- **Repéré par** : l'agent qui a construit la page (Opus), chargé de signaler sans corriger toute erreur du texte. Repéré avant publication.
- **Correction** : texte réécrit (l'écart de 3,8 TWh est montré et dit non expliqué ; les 7 GW sont présentés à part ; « en fonctionnement » est cité) ; contrainte « dont » retirée du référentiel.
- **Garde-fou ajouté** : la relecture adverse « lectrice experte » de chaque page avant publication devient une étape de la roadmap. Pour le point 1, aucune règle automatique : additionner deux chiffres sourcés pour en vérifier un troisième reste une relecture humaine (ou d'agent).

### 2026-11-26 — Prix horaires arrondis au centime : des heures négatives perdaient leur signe
- **Faux** : le pipeline (agent Opus) arrondissait au centime le prix horaire, moyenne de 4 quarts d'heure depuis le 1er octobre 2025. Une moyenne de −0,0025 €/MWh devenait `-0.0`, indiscernable d'un zéro flottant négatif. Lu tel quel, le CSV donnait 506 heures négatives en 2025 au lieu de 513. `pc check`, qui compte avant l'arrondi, ne pouvait pas le voir.
- **Repéré par** : l'agent du site, en confrontant son décompte au référentiel (513 h, RTE). Avant publication.
- **Correction** : moyenne arrondie à 4 décimales (exacte pour 4 prix au centime) puis normalisée (`+ 0.0`) dès le calcul horaire ; le CSV donne directement 513 h (2025) et 568 h (2026, provisoire).
- **Garde-fou ajouté** : aucun test automatique nouveau. Un contrôle « décompte sur le CSV publié = décompte de `pc check` » serait le bon garde-fou ; noté au backlog.

### 2026-11-26 — Citation non caviardée dans le journal
- **Faux** : en consignant les réponses de l'auteur sur le caviardage, Claude les a citées « telles quelles », ce qui remettait dans le journal ce que le caviardage venait de retirer (une mention personnelle, le prénom, une adresse électronique).
- **Repéré par** : Claude lui-même, en relisant le fichier avant le commit (une recherche du prénom a remonté la ligne).
- **Correction** : citation caviardée à l'intérieur des guillemets, marques visibles. Rien n'a été commité ni publié dans l'état fautif.
- **Garde-fou ajouté** : avant chaque push, recherche du prénom, de « wiki » et de « @ » dans les fichiers versionnés (ajoutée à la section « Making-of » de `CLAUDE.md`).

### 2026-11-26 — Relecture « lectrice experte » : cinq erreurs de fond avant publication
- **Faux** : cinq erreurs de fond dans le site construit, avant publication :
  1. **Fouju** : les 1 400 MW, présentés comme un palier du contrat signé, ne sont que le dimensionnement des ouvrages (« conçues de manière à permettre, à terme ») ; le palier signé de 700 MW avant fin 2029 manquait. Erreur du référentiel saisi par Claude, alors que la contre-vérification citait la phrase exacte.
  2. **Taux de concrétisation** (30 % / 60 %) : Claude a omis la restriction « dont la mise en service est prévue avant 2030 », pourtant présente dans la citation qu'il avait lui-même vérifiée. L'assiette réelle est d'environ 7 à 8 GW ; appliqués aux 14 GW de réservations, ces taux contredisent les 15 TWh affichés.
  3. **Enedis 0,9 GW** : une **surcorrection** de Claude. L'agent du site avait signalé que la nature de la puissance n'était « pas précisée » dans le référentiel. Claude a corrigé le texte dans ce sens sans rouvrir la page source, dont le graphique s'intitule « Puissance raccordée pour des datacenters ». Le site affirmait donc faussement que la source ne précisait rien.
  4. **Rendu** : une ligne du Markdown commençant par « 2035. » était lue comme une liste numérotée ; l'année disparaissait de la page.
  5. **ADEME** : la note affichait « 9,91 TWh (8,16 inventoriés + 3,5 modélisés) », une somme fausse. Les 3,5 TWh extrapolés remplacent les centres privés et publics de l'inventaire ; ils ne s'y ajoutent pas (6,46 + 3,5 ≈ 10). Erreur du spike, recopiée par Claude.
- **Repéré par** : la relecture adverse du site construit (agent Opus, rôle de la lectrice cible ; rapport : `docs/relectures/2026-11-26-lectrice-experte.md`) a relevé 27 points : 5 de fond, 14 de précision, 8 de forme. Claude a revérifié dans les PDF les deux points qui contredisaient ses propres notes (Enedis, ADEME) avant de corriger. Les cinq erreurs de fond :
- **Correction** : texte et référentiel corrigés (nouveau chiffre `dc_signe_fouju_2029`, nouvelle grandeur `puissance_dimensionnement`, assiette des taux explicitée, définition des cotes révisée : B = « source primaire, sans recoupement indépendant »). Les points de précision et de forme sont traités dans le même commit ou listés au backlog.
- **Garde-fou ajouté** : (a) toute correction issue d'un signalement se vérifie à la source, jamais sur la seule foi du signalement (ajouté à `CLAUDE.md`) ; (b) test du rendu Markdown qui refuse une ligne commençant par « nombre de 3 chiffres ou plus + point » hors liste voulue ; (c) la relecture « lectrice experte » reste obligatoire avant chaque publication d'une page.
