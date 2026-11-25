# Décisions

Registre daté. Qui : **l'auteur** (arbitrage de fond) ou **Claude** (owner,
décision technique ou d'organisation, révisable).

| Date | Décision | Raisons | Qui |
|---|---|---|---|
| 2026-11-25 | Stack alignée sur `quifaitlaloi` : Python 3.12 + uv + polars → export versionné ; SvelteKit adapter-static + d3 ; Node 22 ; Cloudflare Pages. | Exigence du brief (s'aligner sur les projets voisins) ; chaîne déjà éprouvée, déployée et testée en CI ; l'auteur la connaît. | Claude |
| 2026-11-25 | Les données dérivées sont un **instantané versionné** : le pipeline tourne en local, le build du site ne télécharge rien. | Reproductibilité, diff lisible à chaque mise à jour des données, build Cloudflare rapide et sans jeton d'API. Convention de `quifaitlaloi`. | Claude |
| 2026-11-25 | Le brief est **versionné et publié** (`docs/BRIEF.md`), contrairement aux projets voisins où il reste privé. L'original et les jetons d'API vont dans `source/`, non versionné. | Le brief exige de le publier tel quel dans le making-of. | Claude |
| 2026-11-25 | Making-of en trois fichiers Markdown (`making-of/JOURNAL.md`, `DECISIONS.md`, `ERREURS.md`) lus par le site au prérendu. | Tenu au fil de l'eau dans le dépôt, donc daté et vérifiable par l'historique git ; une seule source pour le site. | Claude |
| 2026-11-25 | Pressenti : le simulateur (module signature) calcule **dans le navigateur** (TypeScript), avec une implémentation de référence en Python et des cas de test partagés. | Une simulation horaire sur quelques années (≈ 9 000 pas par an) avec règles de dispatch simples se calcule en millisecondes ; l'interactivité est totale sans précalcul combinatoire ; la mission « modifier une hypothèse du simulateur » devient faisable. À confirmer quand le modèle sera spécifié (une vraie optimisation pourrait imposer un précalcul). | Claude |
| 2026-11-25 | Grain temporel commun pressenti : **horaire, en UTC**, à confirmer par le spike. | Les sources ont des pas différents (15 min, 30 min, 1 h) et des fuseaux différents ; un grain unique en UTC évite les doublons et trous du changement d'heure. | Claude |
