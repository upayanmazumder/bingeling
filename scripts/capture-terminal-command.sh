#!/usr/bin/env bash
set -uo pipefail
file="$1" ready="$2" status="$3"
if [[ "$file" == population ]]; then
  cmd='db.getCollectionNames().sort().map(n => ({collection:n, count:db.getCollection(n).countDocuments({})}))'
  printf '$ mongosh --quiet --host 127.0.0.1 bingeling --eval "%s"\n\n' "$cmd"
  mongosh --quiet --host 127.0.0.1 bingeling --eval "$cmd"
  code=$?
else
  printf '$ mongosh --quiet bingeling %s | awk "NR<=14"\n' "$file"
  printf 'Output excerpt: first 14 lines. Full output: docs/query-output/%s.txt\n\n' "$(basename "${file%.js}")"
  mongosh --quiet --host 127.0.0.1 bingeling "$file" |
    awk 'NR <= 14 { print } END { if (NR > 14) printf "... %d more output lines (see saved output)\n", NR - 14 }'
  code=$?
fi
printf '\nExit status: %s\n' "$code"
printf '%s\n' "$code" > "$status"
touch "$ready"
sleep 300
