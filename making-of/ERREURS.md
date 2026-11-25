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
