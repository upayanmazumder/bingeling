#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${1:-}" != '--inside' ]]; then
  docker build -q -f scripts/screenshot.Dockerfile -t bingeling-capture .
  docker run --rm --network container:bingeling-mongo \
    --mount "type=bind,src=$PWD,dst=/workspace" \
    bingeling-capture bash scripts/capture-screenshots.sh --inside
  exit
fi

export DISPLAY=:98
Xvfb :98 -screen 0 1400x850x24 -nolisten tcp &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT
for n in $(seq 1 40); do
  if xdpyinfo -display :98 >/dev/null 2>&1; then break; fi
  sleep 0.2
done
mkdir -p screenshots

capture() {
  local name="$1" path="$2" ready="/tmp/${1}.ready" status="/tmp/${1}.status"
  rm -f "$ready" "$status"
  xterm -display :98 -geometry 128x42+5+5 -fa 'DejaVu Sans Mono' -fs 12 \
    -bg '#ffffff' -fg '#121212' -title "$name" \
    -e bash scripts/capture-terminal-command.sh "$path" "$ready" "$status" &
  local terminal_pid=$!
  local n
  for n in $(seq 1 600); do
    if [[ -f "$ready" ]]; then break; fi
    sleep 0.2
  done
  if [[ ! -f "$ready" ]]; then
    kill "$terminal_pid" 2>/dev/null || true
    echo "Terminal timed out: $name" >&2
    exit 1
  fi
  if [[ "$(cat "$status")" != 0 ]]; then
    kill "$terminal_pid" 2>/dev/null || true
    echo "Query failed in terminal: $name" >&2
    exit 1
  fi
  sleep 0.5
  import -display :98 -window root "screenshots/${name}.png"
  kill "$terminal_pid" 2>/dev/null || true
  echo "Captured screenshots/${name}.png"
}

capture population population
for file in queries/simple/q0[1-5]-*.js queries/complex/q{06,07,08,09}-*.js queries/complex/q10-*.js; do
  [[ -f "$file" ]] || { echo "Missing query: $file" >&2; exit 1; }
  capture "$(basename "${file%.js}")" "$file"
done
