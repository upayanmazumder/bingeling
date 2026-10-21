#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p docs/query-output
count=0
for file in queries/simple/q0[1-5]-*.js queries/complex/q{06,07,08,09}-*.js queries/complex/q10-*.js; do
  [[ -f "$file" ]] || { echo "Missing query: $file" >&2; exit 1; }
  name="$(basename "${file%.js}")"
  output="docs/query-output/$name.txt"
  printf 'Command: docker compose exec -T mongo mongosh --quiet bingeling %s\n' "$file" | tee "$output"
  docker compose exec -T mongo mongosh --quiet bingeling "$file" | tee -a "$output"
  [[ $(wc -l < "$output") -gt 1 ]] || { echo "Empty result: $file" >&2; exit 1; }
  printf 'PASS %s\n' "$name"
  count=$((count + 1))
done
[[ "$count" -eq 10 ]] || { echo "Expected 10 queries, found $count" >&2; exit 1; }
echo 'All 10 queries passed.'
