#!/usr/bin/env bash
# Replace only the six Bingeling collections. Import Extended JSON as BSON.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for collection in users titles watch_events reviews plans payments; do
  if [[ ! -s "$ROOT/data/$collection.json" ]]; then
    printf 'Missing seed array: %s\n' "$ROOT/data/$collection.json" >&2
    exit 1
  fi
done
for collection in users titles watch_events reviews plans payments; do
  docker compose -f "$ROOT/docker-compose.yml" exec -T mongo \
    mongoimport --db bingeling --collection "$collection" --jsonArray \
    --drop --file "/workspace/data/$collection.json"
done
docker compose -f "$ROOT/docker-compose.yml" exec -T mongo \
  mongosh --quiet bingeling /workspace/scripts/schema.js
printf 'Loaded Bingeling collections. Validate: docker compose exec -T mongo mongosh --quiet bingeling scripts/validate.js\n'
