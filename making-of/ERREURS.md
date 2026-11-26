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
- **Faux** : Les cinq erreurs de fond :
  1. **Fouju** : les 1 400 MW, présentés comme un palier du contrat signé, ne sont que le dimensionnement des ouvrages (« conçues de manière à permettre, à terme ») ; le palier signé de 700 MW avant fin 2029 manquait. Erreur du référentiel saisi par Claude, alors que la contre-vérification citait la phrase exacte.
  2. **Taux de concrétisation** (30 % / 60 %) : Claude a omis la restriction « dont la mise en service est prévue avant 2030 », pourtant présente dans la citation qu'il avait lui-même vérifiée. L'assiette réelle est d'environ 7 à 8 GW ; appliqués aux 14 GW de réservations, ces taux contredisent les 15 TWh affichés.
  3. **Enedis 0,9 GW** : une **surcorrection** de Claude. L'agent du site avait signalé que la nature de la puissance n'était « pas précisée » dans le référentiel. Claude a corrigé le texte dans ce sens sans rouvrir la page source, dont le graphique s'intitule « Puissance raccordée pour des datacenters ». Le site affirmait donc faussement que la source ne précisait rien.
  4. **Rendu** : une ligne du Markdown commençant par « 2035. » était lue comme une liste numérotée ; l'année disparaissait de la page.
  5. **ADEME** : la note affichait « 9,91 TWh (8,16 inventoriés + 3,5 modélisés) », une somme fausse. Les 3,5 TWh extrapolés remplacent les centres privés et publics de l'inventaire ; ils ne s'y ajoutent pas (6,46 + 3,5 ≈ 10). Erreur du spike, recopiée par Claude.
- **Repéré par** : la relecture adverse du site construit (agent Opus, rôle de la lectrice cible ; rapport : `docs/relectures/2026-11-26-lectrice-experte.md`) a relevé 27 points : 5 de fond, 14 de précision, 8 de forme. Claude a revérifié dans les PDF les deux points qui contredisaient ses propres notes (Enedis, ADEME) avant de corriger.
- **Correction** : texte et référentiel corrigés (nouveau chiffre `dc_signe_fouju_2029`, nouvelle grandeur `puissance_dimensionnement`, assiette des taux explicitée, définition des cotes révisée : B = « source primaire, sans recoupement indépendant »). Les points de précision et de forme sont traités dans le même commit ou listés au backlog.
- **Garde-fou ajouté** : (a) toute correction issue d'un signalement se vérifie à la source, jamais sur la seule foi du signalement (ajouté à `CLAUDE.md`) ; (b) test du rendu Markdown qui refuse une ligne commençant par « nombre de 3 chiffres ou plus + point » hors liste voulue ; (c) la relecture « lectrice experte » reste obligatoire avant chaque publication d'une page.

### 2026-11-26 — Accueil : l'hypothèse du brief écrite comme un fait
- **Faux** : l'ouverture réécrite de l'accueil disait « En moyenne sur l'année, la France produit une électricité abondante et largement décarbonée. Mais […] la question se joue à l'heure, au poste électrique et au prix. » C'est l'hypothèse de travail du brief, affirmée sans réserve, alors que l'auteur a décidé le 26/11 que l'accueil pose la question sans thèse. La formule venait de la consigne que Claude a donnée à l'agent du site ; Claude, en relisant, a corrigé la moitié de la phrase (« tantôt tendu, tantôt en excédent ») et laissé l'autre. « Largement décarbonée » n'était ni daté ni sourcé, et faux pour 2022, année que le calendrier propose.
- **Repéré par** : la relecture adverse « lectrice experte » de l'accueil (agent Opus), avant publication.
- **Correction** : ouverture réécrite en description de ce que fait le site (vérifier, chiffrer, dater ; dire où les données manquent), sans affirmation sur le système.
- **Garde-fou ajouté** : une consigne à un agent qui rédige un texte public ne contient plus de formulation de fond toute faite : Claude donne le but et les décisions de l'auteur qui le bornent, et relit la phrase produite contre ces décisions.

### 2026-11-26 — « Sans changer son texte » : une phrase ajoutée en remettant une erreur au format
- **Faux** : en remettant au format l'entrée « Relecture "lectrice experte" : cinq erreurs de fond », Claude a ajouté en tête du champ Faux une phrase de son cru (« cinq erreurs de fond dans le site construit, avant publication : ») et laissé la phrase d'origine « Les cinq erreurs de fond : » orpheline à la fin de Repéré par. Le journal disait dans le même temps « sans changer son texte ».
- **Repéré par** : la relecture adverse du making-of (agent Opus), avant publication.
- **Correction** : texte d'origine rétabli, seulement réordonné ; le journal le dit.
- **Garde-fou ajouté** : le script de fidélité de la relecture (comparaison mot à mot des Markdown et du HTML rendu) est relancé avant chaque push qui touche le making-of. Il ne voit pas un ajout à la source : une modification d'une entrée déjà écrite se relit en `git diff` avant commit.

### 2026-11-26 — « Combien ? » : étages de la pyramide mal numérotés en ligne
- **Faux** : sur la page publiée `/combien`, la pyramide des puissances (liste numérotée de 1 à 5) était coupée en deux par le paragraphe « Cas particulier, la pré-réservation ». Le Markdown maison du site ne savait pas garder dans un item un paragraphe indenté après une ligne vide : les étages « Signée », « Raccordée » et « Appelée » s'affichaient numérotés 1, 2, 3 au lieu de 3, 4, 5. Aucun chiffre touché, mais l'ordre des étages, qui est le propos de la pyramide, était brouillé.
- **Repéré par** : l'agent du site, en corrigeant le même défaut de rendu signalé dans le brief par la relecture du making-of ; vérifié en rendant `docs/enquetes/combien.md` avec l'ancien code.
- **Correction** : le Markdown garde les paragraphes de continuation dans leur item ; les notes marginales qu'ils portent restent dans l'ordre du texte. Tests ajoutés.
- **Garde-fou ajouté** : test de fidélité du making-of en CI (mot à mot, Markdown contre HTML rendu). Rien d'équivalent pour les enquêtes : une relecture du rendu de chaque page reste nécessaire, et la relecture adverse de la session 1 ne l'a pas vu.

### 2026-11-26 — Spike « Quand ? » : jeu REMIT d'EDF dit « EDF SA seulement »
- **Faux** : le rapport du spike « Quand ? » (agent Opus) décrivait le jeu des indisponibilités d'EDF comme « EDF SA seulement ». Il contient aussi des unités de Luminus en Belgique (Seraing, Ringvaart, Nobelwind) : 984 lignes dans l'historique, 59 dans la liste courante (recomptées par Claude, motifs « Seraing », « Ringvaart », « Nobelwind »). Sans effet sur le nucléaire ; un agrégat gaz ou éolien en mer tiré de ce jeu aurait été faux.
- **Repéré par** : la contre-vérification adverse (agent Opus distinct, sans accès aux conclusions du spike).
- **Correction** : rapport du spike annoté ; l'agent du pipeline filtre explicitement la filière nucléaire et les tranches françaises.
- **Garde-fou ajouté** : aucun nouveau ; la contre-vérification indépendante avant usage d'un chiffre de spike a fonctionné.

### 2026-11-26 — Spike « Quand ? » : Fessenheim exclue à tort, dépassements de 2025 attribués à l'EPR
- **Faux** : le prototype du spike « Quand ? » (agent Opus) excluait Fessenheim de toutes les années, au motif qu'elle n'a plus d'événement après sa fermeture ; elle a pourtant fonctionné jusqu'en 2020, ce qui faussait le dénominateur du taux de disponibilité de 2015 à 2020. Le même rapport écrivait que les 185 heures de 2025 où la production dépasse la disponibilité reconstruite « signal[aient] un traitement incertain de l'EPR » : l'analyse de la production régionale de Normandie n'en explique que 6,5 %, et des dépassements du même ordre existent en 2016-2018, 2022 et 2023.
- **Repéré par** : l'agent du pipeline, en reprenant la reconstruction pour `pc build`.
- **Correction** : Fessenheim comptée jusqu'à son dernier événement (22/02 et 29/06/2020) ; l'EPR compté à partir de son premier événement ; les dépassements bornés par un contrôle `pc check` calibré sur toutes les années. Rapport du spike annoté.
- **Garde-fou ajouté** : aucun nouveau. Les chiffres d'un spike n'entrent sur le site qu'après passage dans le pipeline et `pc check` (règle déjà écrite dans le spike lui-même) : elle a joué.

### 2026-11-26 — « Quand ? » : une contradiction prêtée à RTE
- **Faux** : le texte de « Quand ? » écrit par Claude affirmait que la méthode de RTE « contredit en partie » l'équivalence « un GW consommé en permanence, un GW de marge en moins », en citant la p. 16 du rapport de paramétrage du mécanisme de capacité. Cette page décrit le calcul d'un vecteur de températures extrêmes, qui sert à pondérer les consommations sensibles au froid ; elle ne dit rien contre l'équivalence pour une consommation plate, qui est au contraire le cas où elle est la plus proche de l'exactitude dans un calcul d'adéquation. La contre-vérification avait présenté cette page comme un « contre-indice » ; Claude en a fait une contradiction, sans relire la page.
- **Repéré par** : la relecture adverse « lectrice experte » de `/quand` (agent Opus), avant publication ; Claude a relu la p. 16 dans le PDF avant de corriger.
- **Correction** : paragraphe réécrit : l'équivalence est légitime pour une consommation plate, RTE ne l'écrit pas pour la consommation mais fait le passage inverse (hausse de pointe → besoin de capacité, BP2025 « Fonctionnement », p. 25) ; elle cesse d'être exacte dès que la consommation n'est plus plate.
- **Garde-fou ajouté** : une phrase qui fait dire quelque chose à une source (« RTE contredit », « RTE confirme ») se vérifie sur la page citée par Claude lui-même, même quand un agent l'a déjà lue.

### 2026-11-26 — « Quand ? » : quatre raisonnements qui ne tenaient pas
- **Faux** : dans le texte soumis à relecture, (1) le nombre d'heures où la charge résiduelle augmentée de X dépasse « son maximum de l'année » dépendait d'une seule matinée (le 14/01/2025) et faisait paraître 2024 plus exposée que 2025 ; (2) « au plus 87 % » pour 1 GW mesurait surtout un plancher : le nucléaire disponible non produit ne tombe jamais à zéro, même aux heures les plus chères ; (3) la part « tenue » ignorait la contrainte d'énergie : servir 5 GW plats de cette façon suppose une production nucléaire annuelle au-delà des prévisions de l'exploitant ; (4) « une consommation ajoutée serait d'abord servie, en partie, par moins d'exportations » était affirmé sans preuve et peut être faux si les interconnexions sont saturées. Les chiffres étaient justes (tous recalculés à l'identique par la relecture) ; ce qu'on leur faisait dire ne l'était pas. Les indicateurs venaient du spike et de la décision de Claude du 26/11 ; le (4) figurait dans cette décision.
- **Repéré par** : la relecture adverse « lectrice experte » de `/quand` (agent Opus), avant publication.
- **Correction** : seuil pluriannuel ajouté et dépendance à une seule heure dite ; sensibilité à un plancher de 1 GW et nucléaire non produit aux heures chères chiffrés ; énergie nucléaire supplémentaire comparée à la production 2025 et aux prévisions ; la question « qui servirait cette consommation » laissée ouverte tant que les données des voisins manquent. Nouveaux chiffres produits par `pc build`.
- **Garde-fou ajouté** : un indicateur construit sur un extremum (maximum, première heure) se publie avec sa sensibilité au seuil ; un plafond (« au plus ») se publie avec ce qui le rend lâche, chiffré.

### 2026-11-26 — Simulateur : les erreurs de « Quand ? » reprises, et un effacement circulaire
- **Faux** : le simulateur v1, spécifié par Claude avant la relecture de « Quand ? », reprenait les mêmes raisonnements fautifs (exportations « d'abord » réduites, plafond « au plus 87 % » sans plancher ni contrainte d'énergie, seuil sur le seul maximum de l'année, qui donnait « 1 heure » dès l'ouverture puisque l'heure du maximum se dépasse elle-même). S'y ajoutaient deux défauts propres : l'effacement à prévision parfaite efface exactement les heures que l'indicateur compte (résultat circulaire, présenté comme « borne optimiste » sans le dire), et le prix moyen pondéré, comparé « sans effacement », se lisait comme une économie alors que les prix sont observés, sans effet en retour.
- **Repéré par** : la relecture adverse « lectrice experte » du simulateur (agent Opus), avant publication.
- **Correction** : alignement sur le texte corrigé de « Quand ? » ; effacement présenté comme borne basse, énergie effacée dite perdue ; prix moyen supprimé ; résultat « marge » ajouté (spécification révisée, registre des décisions).
- **Garde-fou ajouté** : un module qui reprend les indicateurs d'une enquête attend la relecture de cette enquête avant d'être spécifié en détail ; une phrase de fond n'est pas recopiée d'une page à l'autre mais tirée d'une source unique (à faire : les textes du simulateur citent encore des passages de « Quand ? » à la main, backlog).

### 2026-11-26 — Corrections de « Quand ? » et du simulateur : erreurs réintroduites
- **Faux** : en corrigeant les deux pages après leurs relectures, Claude et ses agents ont écrit de nouvelles phrases fausses : « le nucléaire disponible non produit ne tombe jamais à zéro » (il est nul 183 heures en 2025, dont 14 au-dessus de 150 €/MWh ; seule sa moyenne reste positive) ; « c'est demander au système ce qu'il n'a fourni que dans ses pires années », affiché par le simulateur justement quand la charge dépasse tout ce que le système a couvert ; deux légendes qui reprenaient l'idée d'un territoire « jamais vu » pour le maximum de l'année ; la p. 16 du paramétrage, retirée de « Quand ? », encore citée par le simulateur ; et, dans les notes générées par le pipeline, « prix extrêmes » pour février 2018 et « production de l'EPR non publiée à part », déjà corrigés dans le texte.
- **Repéré par** : la vérification des corrections avant publication (agent Opus), qui a recalculé les nombres et confronté chaque point des deux relectures aux pages construites.
- **Correction** : phrases réécrites dans le texte, les légendes, les phrases du simulateur et les notes du pipeline ; vérifié dans les données par Claude.
- **Garde-fou ajouté** : une correction de fond se reporte partout où la phrase vit (texte, légendes, notes générées, textes du simulateur) : `git grep` de la formule fautive avant commit. Et une vérification des corrections avant publication reste systématique après une relecture qui a trouvé du fond.

### 2026-11-26 — Proposition éditoriale : deux pourcentages mal dits
- **Faux** : dans la première rédaction de `docs/EDITO.md`, Claude écrivait que les trajectoires de RTE pour 2035 (2,4 à 3,7 GW moyens) représentaient « le quart à un peu plus du tiers » des marges de 8 à 10 GW : le calcul donne 24 à 46 %, soit « d'un quart à près de la moitié ». Il écrivait aussi qu'au plus « la moitié » de l'énergie d'une charge plate de 5 GW trouverait du nucléaire disponible non produit en 2025 : le référentiel dit 52 %. Les deux phrases venaient de mémoire, sans relire les chiffres.
- **Repéré par** : Claude lui-même, en vérifiant les valeurs dans `data/export/chiffres.json` avant de soumettre la proposition à l'auteur.
- **Correction** : phrases corrigées avant que l'auteur les lise ; le message publié (`docs/MESSAGE.md`) tire ses chiffres du référentiel par leurs identifiants.
- **Garde-fou ajouté** : aucun mécanisme pour un document de travail ; la règle existante (un chiffre se relit à la source avant d'être écrit) vaut aussi pour les propositions à l'auteur, dit franchement.

### 2026-11-26 — Message principal : une condition que la source contredit, et un calcul à système figé
- **Faux** : le message proposé pour l'accueil (`docs/MESSAGE.md`, issu de l'option A de `docs/EDITO.md`) concluait que « l'accueil de la vague se joue d'abord » à la pointe d'hiver, « soit les data centers réduisent leur consommation aux heures de pointe, soit des moyens nouveaux s'ajoutent ». Or le Bilan prévisionnel 2025 de RTE, dont viennent les trajectoires citées, fait déjà le calcul d'adéquation avec toute la consommation de ces trajectoires : besoin de capacités nouvelles **nul** en 2030-2035 dans la trajectoire lente à rythme R3 des renouvelables, 2 à 4 GW en 2030 et 1 à 6 GW en 2035 dans la trajectoire rapide (*Fonctionnement*, p. 26 et 28). Le message refaisait ce calcul à la main, à système figé, et comptait deux fois la consommation déjà incluse dans les marges de 2026-2027 (« d'un quart à près de la moitié » : la seule hausse depuis 2024 donne au plus 19 à 40 %). Autres défauts de fond : titre « pas une question d'énergie » contraire à la conclusion énergie de « Quand ? » ; « au plus 7 % » faux (32 ÷ 442,2 = 7,2 %) et présenté comme un plafond ; équivalence « un GW consommé retire un GW de marge » sans les précautions de « Quand ? » ; date des marges absente du texte ; « la vague » non définie ; « d'abord » et « que personne ne publie » non établis ; profil des data centers absent des limites. Aucune des deux enquêtes ne citait ces résultats d'adéquation : le message prétendait les résumer en tirant une conclusion qu'elles ne portent pas.
- **Repéré par** : la relecture adverse « lectrice experte » (agent Opus), avant publication (`docs/relectures/2026-11-26-message-en-bref.md`, points 1 à 10). Claude a vérifié les trois citations de RTE dans le PDF avant de corriger.
- **Correction** : résultats d'adéquation saisis au référentiel (`besoin_capacites_*`, nouvelle grandeur) ; message réécrit et soumis à l'auteur, puisque sa conclusion change.
- **Garde-fou ajouté** : un message de synthèse se relit contre les conclusions **et** contre les calculs intégrés de la source dont il tire ses chiffres ; quand la source publie le calcul (adéquation, scénario), on le cite au lieu de le refaire à la main. Une conclusion transversale ne s'écrit pas sans relecture adverse, ce qui a fonctionné ici.

### 2026-11-26 — Relecture adverse : une énergie comparée à une puissance, et une borne mal construite
- **Faux** : la proposition de texte de l'agent relecteur (point 11 de `docs/relectures/2026-11-26-message-en-bref.md`), reprise par Claude dans le message réécrit, disait des trajectoires de 21 à 32 TWh qu'elles « restent très en dessous des 18 GW réservés » : une énergie annuelle comparée à une puissance, la confusion MW ≠ MWh que le projet s'interdit en premier. Elle majorait aussi la hausse de la trajectoire lente en retranchant le niveau de 2024 le plus haut (5 TWh) au lieu du plus bas (4 TWh) : « au plus 1,8 GW » au lieu de 1,9. Et sa conclusion (« il faudra que des consommations baissent… ») allait encore au-delà de RTE, qui trouve le besoin de la trajectoire rapide résorbé si le nucléaire est plus disponible.
- **Repéré par** : le même agent, à la vérification des corrections ; Claude, qui avait repris le texte, ne l'avait pas vu.
- **Correction** : comparaison retirée (les trajectoires « supposent… », la puissance réservée « n'engage pas à consommer ») ; borne recalculée (1,9 à 3,2 GW, 19 à 40 %) ; conclusion ramenée à ce que dit RTE. Points de forme V4 à V7 appliqués, dont le plancher de 39 % à côté du plafond de 52 % (règle déjà écrite).
- **Garde-fou ajouté** : un texte proposé par un relecteur se vérifie comme un texte de Claude, chiffre par chiffre et unité par unité, avant d'être repris ; la vérification des corrections par un agent reste systématique, et elle a servi ici.

### 2026-11-26 — Commit fait avec un test en échec
- **Faux** : Claude a enchaîné tests et commit dans une même commande dont la condition portait sur l'affichage du résumé des tests, pas sur leur résultat : le commit est parti alors que le test de fidélité du making-of échouait. Cause du test : une citation de l'auteur, recomposée sur plusieurs lignes, faisait commencer une ligne par « - », que le rendu lisait comme une liste ; l'italique de la citation n'était plus fermé.
- **Repéré par** : un test (fidélité de la page making-of à ses fichiers source), avant tout envoi : rien n'a été poussé.
- **Correction** : citation recomposée sans « - » en début de ligne ; commit refait après des tests au vert.
- **Garde-fou ajouté** : le commit ne se chaîne qu'au code de retour des tests (`npm test && …`), jamais à un filtre de leur sortie.

### 2026-11-26 — Pipeline ENTSO-E : une règle de lecture fausse et un build trop gourmand, avant publication
- **Faux** : l'agent qui branchait ENTSO-E (Opus) a d'abord retenu, pour les prix day-ahead publiés en plusieurs séquences, une règle qui gardait en Espagne une enchère infrajournalière au lieu du prix du couplage day-ahead ; sa première version du build montait à 16,9 Go de mémoire, et ses processus de lecture se bloquaient sous `pc build`.
- **Repéré par** : les contrôles écrits par l'agent lui-même (prix ENTSO-E comparés à energy-charts, point à point) et ses essais, avant tout commit.
- **Correction** : règle documentée (série sans numéro de séquence si elle existe, sinon séquence 1 ; recoupée avec energy-charts) ; build ramené à 4,8 Go au pic ; processus lancés en `spawn`. Claude a vérifié lui-même, après coup, la licence (PDF d'ENTSO-E) et le décalage d'une heure signalé dans la source (corrélations à 0, −1 et +1 h).
- **Garde-fou ajouté** : contrôle permanent `pc check` « prix FR ENTSO-E = energy-charts, point à point » ; aucune donnée ENTSO-E dans les exports publiés tant qu'une page ne l'exige.

### 2026-11-26 — « Quand ? » : un plafond qui dépend de ce qu'EDF déclare indisponible
- **Faux** : « Quand ? » et le simulateur présentent le nucléaire disponible et non produit (J) comme une borne haute de ce qu'une consommation ajoutée trouverait (« au plus 52 % » de l'énergie d'une charge plate de 5 GW en 2025). Or EDF déclare dans REMIT, comme indisponibilités planifiées, des **arrêts pour modulation** (« Le placement et la durée de cet arrêt pour modulation seront réinterrogés et la tranche sera redémarrée si les conditions économiques le justifient ») : 380 événements actifs dans l'historique, de l'ordre de 10 TWh en 2024 et 5 TWh en 2025 (estimation brute de Claude, chevauchements non traités), contre 25,1 et 29,1 TWh de J publiés. Ces arrêts sortent de J : le « plafond » n'en est pas un au sens physique. Le texte disait bien que la frontière entre indisponible et modulé est fixée par EDF, mais pas là où il écrit « au plus ».
- **Repéré par** : l'agent du spike carbone (Opus), en cherchant pourquoi la disponibilité déclarée n'était pas exogène ; Claude a vérifié dans le fichier d'EDF (texte des événements, décompte, ordre de grandeur). Le spike annonçait 928 événements, Claude en compte 380 actifs (501 identifiants, toutes versions) : écart de décompte à éclaircir.
- **Correction** : variante J_r réintégrant 407 arrêts pour modulation (2019-2026 ; 10,4 TWh en 2024, 7,8 TWh en 2025) ; Σ J passe de 25,1 à 35,6 TWh (2024) et de 29,1 à 37,0 TWh (2025) ; la part d'une charge plate de 5 GW en 2025, de 52 à 58 % (39 à 47 % avec le plancher). Aucun chiffre publié modifié : variantes ajoutées, « au plus » requalifié dans « Quand ? », le simulateur, les notes, le graphique et le message d'accueil ; deux contrôles `pc check` (J_r ≥ J, comparaison à la modulation publiée par EDF). Le décompte de 928 du spike était faux (essais à puissance stable et liens comptés), celui de 380 de Claude incomplet (liste courante et versions antérieures oubliées). Révision : les valeurs de J_r ci-dessus sont celles d'une première version, jamais publiée ; voir l'entrée « Limites de « Quand ? » : un repère de froid démenti… » ci-dessous (arrêts courts seuls : J_r 2025 = 33,0 TWh, 55 %).
- **Garde-fou ajouté** : une borne se publie avec ce dont elle dépend, au même endroit ; une série déclarée par un acteur de marché (REMIT) se lit dans son texte libre avant de servir de référence physique.

### 2026-11-26 — Note des exports : « la modulation n'est pas retranchée de la disponibilité déclarée »
- **Faux** : la limite écrite dans `data/export/meta.json` (générée par `pc build`) affirmait que la modulation économique n'est pas retranchée de la disponibilité déclarée par EDF. C'est faux depuis 2019 : EDF déclare des arrêts pour modulation comme indisponibilités planifiées.
- **Repéré par** : l'agent de la correction des arrêts pour modulation (Opus), en reprenant toutes les phrases qui parlent de modulation.
- **Correction** : phrase réécrite dans `pipeline/pc/build.py`, `meta.json` régénéré.
- **Garde-fou ajouté** : le même que l'entrée précédente : `git grep` de la notion corrigée dans le code qui génère des textes, pas seulement dans les pages.

### 2026-11-26 — Spike carbone : 928 « arrêts pour modulation » comptés à tort
- **Faux** : le spike carbone (agent Opus) comptait 928 événements « pour modulation » dans REMIT, dont 461 essais à puissance stable et 54 textes réduits à un lien ; il en tirait 72 TWh cumulés.
- **Repéré par** : Claude (décompte différent : 380) puis l'agent de la correction, qui a reproduit exactement les 928 et identifié les faux positifs.
- **Correction** : annotation en tête de `docs/spike/carbone.md` ; règle d'identification écrite et testée dans `pipeline/pc/remit.py`.
- **Garde-fou ajouté** : une recherche de mots dans un texte libre se publie avec ses faux positifs examinés à la main ; un spike n'entre dans une page qu'après relecture adverse.

### 2026-11-26 — Limites de « Quand ? » : un repère de froid démenti par sa propre source, et des arrêts longs réintégrés comme réversibles
- **Faux** : (1) le réglage « froid supplémentaire » du simulateur proposait le repère « 8 °C, février 2012 » en citant une phrase de RTE coupée avant sa conclusion. Ajouté aux sept jours les plus tendus d'une année qui contient déjà son propre froid, ce repère porte la consommation de 2025 à 106,6 GW. Or RTE écrit que des froids comme ceux du début des années 2010 donneraient aujourd'hui des pointes « sensiblement inférieures à 100 GW ». (2) La variante J_r réintégrait comme réversibles des arrêts longs déclarés « pour modulation » qui relèvent de la gestion du combustible : Chooz 2, du 18/04 au 26/06/2025, 2,5 TWh, cause « Maintenance prévisionnelle », sans la clause « la tranche sera redémarrée ». (3) Le message d'accueil disait qu'EDF déclare des réacteurs indisponibles « alors qu'il les arrête pour des raisons économiques », tournure qui insinue une déclaration abusive, alors que cette déclaration est conforme à REMIT.
- **Repéré par** : la relecture adverse « lectrice experte » (agent Opus, `docs/relectures/2026-11-26-limites-modulation.md`), avant publication. Claude a vérifié (1) dans la synthèse RTE hiver 2026-2027 et (2) dans le fichier d'EDF, toutes versions de l'événement.
- **Correction** : citation de RTE complétée et nouvelle source au référentiel (pointes « sensiblement inférieures à 100 GW » avec des froids comme ceux du début des années 2010) ; repères 8 °C et 12 °C retirés, repère exprimé en consommation (froid supplémentaire nécessaire pour atteindre 100 GW, 5,5 °C en 2025) ; arrêts pour modulation séparés en courts (moins de 7 jours, sans mention du combustible : réintégrés) et longs (retranchés) : en 2025, 3,9 TWh de chaque ; J_r 2025 = 33,0 TWh (au lieu de 37,0 dans la version non publiée), part 5 GW 55 % (43 % avec le plancher) ; message d'accueil réécrit sans la tournure en cause.
- **Garde-fou ajouté** : une citation se reproduit jusqu'à sa conclusion, jamais coupée avant ; un réglage qui ajoute un effet à une année observée se teste sur toutes les années (le même réglage ne doit pas changer de sens d'une année à l'autre sans que la page le dise).
