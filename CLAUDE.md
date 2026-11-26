# CLAUDE.md

Guide pour Claude Code dans ce dépôt.

## Le projet

**Puissance de calcul** (nom de travail) est un site de données sur une
question : **le système électrique français peut-il accueillir la vague
de data centers, et à quelles conditions ?** Hypothèse de travail : la
moyenne annuelle (électricité abondante et décarbonée) ne tranche rien ;
la question se joue **à l'heure, au poste électrique et au prix**. Le
site vérifie, chiffre, date, et dit où les données contredisent
l'hypothèse ou manquent. Instrument de preuve, pas un tract.

En ligne : https://pdc.technoperchoir.fr (Cloudflare Pages, build à chaque
push sur `main`). Dépôt public : `m4xim1nus/puissance-de-calcul`.

Le brief est dans `docs/BRIEF.md` : figé, **publié tel quel** dans le
making-of (exigence du brief). L'original est dans `source/BRIEF.md`
(dossier privé, non versionné). En cas d'écart, le brief prime.

Claude est **owner** du projet : stack, architecture, phasage. L'auteur
tranche ce qui engage le fond (périmètre des enquêtes, thèse de
l'accueil, nom). Le reste, Claude décide et l'écrit dans
`making-of/DECISIONS.md`.

## Lectrice cible et exigence

Une ingénieure experte des marchés de l'électricité et de la
modélisation énergétique. **Une seule erreur de fond et le site perd
toute valeur.** D'où :

- chaque chiffre affiché est **sourcé et daté** (source, date de
  publication ou d'extraction, lien) ;
- chaque hypothèse est **affichée**, et modifiable quand c'est possible ;
- unités explicites partout : **MW (puissance) ≠ MWh (énergie)** ; une
  série au pas de 30 min en MW se somme en MWh avec un facteur 0,5 ;
- **facteur d'émission moyen ≠ marginal** : ne jamais présenter l'un
  pour l'autre ; tout chiffre carbone dit lequel il est ;
- **annonce ≠ demande de raccordement ≠ raccordement signé ≠ mise en
  service** : ne jamais additionner ces catégories ;
- limites et incertitudes **écrites**, pas cachées ;
- pas de vulgarisation des bases (merit order, capture price, PPA,
  TURPE) : glossaire replié.

## Règles dures

- **Données** : open data et publications officielles en source
  primaire (RTE/ODRÉ, ENTSO-E, CRE, AIE, Commission européenne,
  Météo-France). Presse et bases sectorielles : pour les annonces de
  projets seulement, toujours citées comme telles.
- **Tests de cohérence obligatoires** sur les chiffres clés (`pc check`) :
  bilans qui bouclent, ordres de grandeur recoupés entre deux sources.
  Un chiffre clé sans recoupement est marqué « non recoupé » sur le site.
- **Making-of tenu au fil de l'eau**, jamais reconstruit à la fin (voir
  « Making-of »). Les erreurs de Claude y sont consignées **sans
  embellir**, dès qu'elles sont repérées.
- FOSS, aucun tracker, aucun CDN tiers. Aucun secret dans le dépôt :
  jetons d'API dans `source/` ou `.env`.

## Making-of

Trois fichiers dans `making-of/`, lus par le site (onglet « Making-of ») :

| Fichier | Contenu | Quand l'écrire |
|---|---|---|
| `JOURNAL.md` | Une entrée par session : demandes de l'auteur **citées telles quelles**, puis explicitées si elles sont elliptiques ; ce qui a été fait ; durée ; agents lancés ; coût (relevé `/cost` si l'auteur le fournit, sinon ordre de grandeur signalé comme estimé). | En début de session (demande), puis au fil de la session. |
| `DECISIONS.md` | Registre daté : décision, raisons, qui a tranché (l'auteur / Claude). | Au moment où la décision est prise. |
| `ERREURS.md` | Erreurs de Claude (et de ses agents) : ce qui était faux, comment c'est sorti, la correction, ce qui a changé pour éviter la récidive. | Dès qu'une erreur est repérée, avant de la corriger. |

**Caviardage** (décision de l'auteur, 2026-11-25) : le dépôt et le site sont
publics, le making-of ne publie pas de détails trop personnels sur l'auteur
ou des tiers (chemins de sa machine, autres projets privés, personnes identifiables). On caviarde **visiblement**
(`[caviardé : motif]`), jamais en réécrivant en silence, y compris dans
le brief « publié tel quel » et les demandes citées. En cas de doute,
on demande à l'auteur avant le push.
Avant chaque push : `git grep -n -w -i -e max -e wiki -e '@'` sur les
fichiers versionnés (hors `package-lock.json`), et lecture des
résultats. Une citation de l'auteur est caviardée **à l'intérieur** des
guillemets si elle contient un élément caviardé.

L'onglet « À toi » (missions à faire soi-même avec Claude Code) est
rédigé en tutoiement, ton direct, zéro jargon de dev.

## Sous-agents

- **Opus** : recherche où le jugement sur un chiffre compte (sources,
  trajectoires, carbone, méthodo), revue critique « lectrice experte ».
- **Sonnet** : vérification d'accès, extraction, code bien spécifié,
  mise en forme.
- Tout agent écrit dans un fichier qui lui est propre, ne commite pas,
  et signale ses doutes. Ses chiffres sont relus avant d'entrer dans
  `docs/` ou sur le site.
- Un signalement (d'agent, de relecture, de test) se vérifie **à la
  source** avant correction : on ne corrige jamais sur la seule foi du
  signalement (erreur du 26/11/2026, surcorrection Enedis).
- Avant chaque publication d'une page : relecture adverse « lectrice
  experte » par un agent Opus, rapport dans `docs/relectures/`.

## Arborescence

```
source/              privé, non versionné : original du brief, jetons d'API
docs/BRIEF.md        brief de lancement, figé, publié
docs/SOURCES.md      fiche des sources (après le spike)
docs/METHODO.md      méthodes et hypothèses, base des pages méthodo
docs/CONCEPTION.md   conception du site : récit, pages, direction visuelle
docs/spike/          rapports bruts du spike sources (étape 1)
making-of/           journal, décisions, erreurs (lus par le site)
data/raw/            sources téléchargées (cache local, non versionné)
data/export/         données dérivées pour le site (versionnées)
pipeline/pc/         package Python (CLI download / build / check)
pipeline/explo/      scripts jetables (spike, graphiques de relecture)
pipeline/tests/      pytest
site/                SvelteKit adapter-static + d3
build.sh             build Cloudflare Pages (site seulement, aucun téléchargement)
```

## Stack

Alignée sur `~/dev/quifaitlaloi` (en cas de doute sur une convention —
build.sh, CI, tests, prettier — copier quifaitlaloi) : Python 3.12 + uv +
polars → `data/export/` versionné ; site SvelteKit adapter-static + d3,
Node 22, versions épinglées ; Cloudflare Pages relié au dépôt, dont le
build ne télécharge rien.

## Suivi

Comme quifaitlaloi : `ROADMAP.md` porte l'étape ou le cycle en cours ;
`BACKLOG.md` est la file brute (`- [TAG] description (origine, date)`) ;
`CHANGELOG.md` naît au premier tag. On commite en nommant les fichiers
(`git add <chemins>`, jamais `git add -A`).

## Commandes

Pipeline (depuis `pipeline/`, Python 3.12 + uv) :

```sh
uv run pc download [clés…] [--force]  # sources → data/raw/ + data/raw/manifeste.json
uv run pc build                       # data/raw/ → data/export/
uv run pc check                       # contrôles de cohérence ; code de retour ≠ 0 si échec
uv run pytest                         # tests (synthétiques + `donnees`, sautés sans data/export/)
uv run pytest -m "not donnees"        # tests synthétiques seuls, sans réseau ni données
```

- Clés de `pc download` : `eco2mix_cons_def`, `eco2mix_tr`, `prix_fr`,
  `odre_nucleaire`, `odre_ges_conso`, `odre_conso_annuelle`,
  `odre_conso_annuelle_regionale` (défaut : toutes).
- Incrémental : une année close déjà téléchargée n'est pas refaite (pour
  éCO2mix, seulement si elle était entièrement « définitive ») ; l'année en
  cours et les instantanés sont toujours retéléchargés. `--force` refait tout.
  energy-charts limite à 2 requêtes/min : compter ≈ 6 min pour un `--force`
  sur les prix.
- Exports : `data/export/systeme_horaire.parquet`, `horaire/AAAA.csv` (unités
  dans `horaire/LISEZMOI.md`), `prix_quart_horaire.csv`, `meta.json`.
- Convention d'horodatage éCO2mix : constante `HORODATAGE_ECO2MIX` dans
  `pipeline/pc/build.py`, seul endroit à changer.
