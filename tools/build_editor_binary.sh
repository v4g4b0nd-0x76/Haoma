#!/usr/bin/env bash
# Build a one-file Haoma editor binary with PyInstaller.
# Usage (from repo root): bash tools/build_editor_binary.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m pip install --quiet 'pyinstaller>=6.0'
OUT_NAME="${EDITOR_BIN_NAME:-haoma-editor}"
python3 -m PyInstaller \
  --onefile \
  --name "$OUT_NAME" \
  --add-data "tools/admin.html${PATHSEP:-:}" \
  --hidden-import encodings \
  --noconfirm \
  --clean \
  tools/editor.py
echo "Built: dist/${OUT_NAME}$( [[ "$(uname -s)" = MINGW* ]] || [[ "$(uname -s)" = MSYS* ]] && echo .exe || true )"
