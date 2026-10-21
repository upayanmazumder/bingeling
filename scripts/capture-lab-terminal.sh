#!/usr/bin/env bash
# Capture screenshots from the "Lab Terminal (sonder)" desktop app on Hyprland.
# Requirements: running Lab Terminal window, hyprctl, wtype, grim, ImageMagick, loaded database.
# The script types real commands into the focused terminal and captures that window only.
set -euo pipefail
cd "$(dirname "$0")/.."
root="$PWD"

window_json="$(hyprctl clients -j)"
read -r address x y w h < <(python3 - "$window_json" <<'PY'
import json, sys
for c in json.loads(sys.argv[1]):
    if c["class"] == "kitty" and c["title"] == "Lab Terminal":
        print(c["address"], c["at"][0], c["at"][1], c["size"][0], c["size"][1])
        break
else:
    sys.exit("Lab Terminal window not found. Start the app first.")
PY
)
region="${x},${y} ${w}x${h}"
terminal_workspace="$(hyprctl clients -j | python3 -c 'import json,sys
for c in json.load(sys.stdin):
    if c["address"] == sys.argv[1]:
        print(c["workspace"]["name"])' "$address")"
original_workspace="$(hyprctl activeworkspace -j | python3 -c 'import json,sys; print(json.load(sys.stdin)["name"])')"
trap 'hyprctl dispatch "hl.dsp.focus({ workspace = '"'"'${original_workspace}'"'"' })" >/dev/null' EXIT

focus() {
  # Focus follows the mouse, so show the terminal workspace and move the pointer into it first.
  local active
  for _ in 1 2 3 4 5; do
    hyprctl dispatch "hl.dsp.focus({ workspace = '${terminal_workspace}' })" >/dev/null
    hyprctl dispatch "hl.dsp.cursor.move({ x = $((x + w / 2)), y = $((y + h / 2)) })" >/dev/null
    hyprctl dispatch "hl.dsp.focus({ window = 'address:${address}' })" >/dev/null
    sleep 0.4
    active="$(hyprctl activewindow -j | python3 -c 'import json,sys; print(json.load(sys.stdin).get("address", ""))')"
    [[ "$active" == "$address" ]] && return 0
  done
  echo "Lab Terminal is not focused. Stop." >&2
  exit 1
}

pad_image() {
  # Keep every image at least 900 px wide so the report shows a readable frame.
  local file="$1" bg
  bg="$(magick "$file" -format '%[pixel:p{2,2}]' info:)"
  magick "$file" -background "$bg" -gravity west -extent "%[fx:max(w,900)]x%[h]" "$file"
}

run_and_capture() {
  local name="$1" command="$2" wait="$3"
  focus
  wtype -M ctrl l -m ctrl
  sleep 0.3
  focus
  wtype "$command"
  wtype -k Return
  sleep "$wait"
  focus
  grim -g "$region" "/tmp/${name}.raw.png"
  magick "/tmp/${name}.raw.png" -resize 1700x -shave 6x6 -fuzz 4% -trim +repage \
    -bordercolor "$(magick "/tmp/${name}.raw.png" -format '%[pixel:p{40,1100}]' info:)" -border 24 \
    "screenshots/${name}.png"
  pad_image "screenshots/${name}.png"
  rm -f "/tmp/${name}.raw.png"
  echo "Captured screenshots/${name}.png"
}

focus
wtype "cd '${root}'"
wtype -k Return
sleep 0.5
# Open one mongosh session in the MongoDB container. Every query below runs inside it.
wtype "docker compose exec mongo mongosh --quiet bingeling"
wtype -k Return
sleep 4

run_and_capture population \
  "db.getCollectionNames().sort().map(n => ({collection:n, count:db.getCollection(n).countDocuments({})}))" 3
for file in queries/simple/q0[1-5]-*.js queries/complex/q{06,07,08,09}-*.js queries/complex/q10-*.js queries/extra/q1[12]-*.js; do
  [[ -f "$file" ]] || { echo "Missing query: $file" >&2; exit 1; }
  run_and_capture "$(basename "${file%.js}")" "load('${file}')" 6
done
focus
wtype "exit"
wtype -k Return
