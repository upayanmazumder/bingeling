#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# This removes only the named volume in this Compose project.
echo 'Resetting the Bingeling database volume.'
docker compose down -v
docker compose up -d --wait
bash scripts/load.sh
docker compose exec -T mongo mongosh --quiet bingeling scripts/validate.js
bash scripts/run-queries.sh
echo 'Empty-database demonstration passed.'
