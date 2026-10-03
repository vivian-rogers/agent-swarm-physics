#!/usr/bin/env bash
# Rebuild data/processed/ai-village/ai-village-overview.pdf.
# Needs data/processed/ai-village/turns_stats.json (from scan_turns.py; slow, run once).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/data/processed/ai-village"
BUILD="$OUT/overview_build"
mkdir -p "$BUILD"
uv run --quiet --with matplotlib python "$ROOT/infra/ai_village_overview/figures.py" "$BUILD"
cp "$ROOT/infra/ai_village_overview/overview.tex" "$BUILD/"
(cd "$BUILD" && pdflatex -interaction=nonstopmode overview.tex >/dev/null && pdflatex -interaction=nonstopmode overview.tex | grep "Output written")
cp "$BUILD/overview.pdf" "$OUT/ai-village-overview.pdf"
