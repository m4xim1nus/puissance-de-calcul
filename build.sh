#!/usr/bin/env bash
# Build du site statique dans site/build/ (Cloudflare Pages l'exécute à chaque push sur main).
# Aucun téléchargement de données ici : le making-of est lu depuis making-of/ et docs/.
# Reproductible : `bash build.sh`.
set -euo pipefail
cd "$(dirname "$0")"
node --version

echo "== Site"
cd site
npm ci --no-audit --no-fund
npm run build
echo "Fichiers dans site/build/ : $(find build -type f | wc -l)"
test -f build/index.html && test -f build/404.html && test -f build/_headers
