#!/bin/sh
# Rebuild the report from checked-in evidence with pinned compact renderers.
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"

if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'Python 3 is required to assemble the report.' >&2
    exit 1
fi
python3 report/build_report.py

source_file=report/Bingeling-report.md
typst_file=report/Bingeling-report.typ
pdf_file=report/Bingeling-report.pdf
if command -v pandoc >/dev/null 2>&1; then
    pandoc "$source_file" -o "$typst_file" --from=markdown+raw_attribute \
        --to=typst --standalone --wrap=none --resource-path=report:.
elif command -v docker >/dev/null 2>&1; then
    docker run --rm --user "$(id -u):$(id -g)" \
        --volume "$root:/workspace" --workdir /workspace \
        pandoc/minimal:3.8 "$source_file" -o "$typst_file" \
        --from=markdown+raw_attribute --to=typst --standalone --wrap=none \
        --resource-path=report:.
else
    printf '%s\n' 'Install pandoc or Docker to convert Markdown to Typst.' >&2
    exit 1
fi

typst_bin=
if [ "${BINGELING_FORCE_TYPST_DOWNLOAD:-}" != 1 ] && command -v typst >/dev/null 2>&1; then
    typst_bin=typst
else
    typst_bin="$root/report/.build/typst-x86_64-unknown-linux-musl/typst"
    if [ ! -x "$typst_bin" ]; then
        mkdir -p "$root/report/.build"
        curl -fsSL "https://github.com/typst/typst/releases/download/v0.13.1/typst-x86_64-unknown-linux-musl.tar.xz" \
            | tar -xJ -C "$root/report/.build"
    fi
fi
"$typst_bin" compile --root "$root" "$typst_file" "$pdf_file"
printf 'Built %s\n' "$pdf_file"
