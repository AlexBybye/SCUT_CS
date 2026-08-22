#!/usr/bin/env bash
# Bootstrap the material_converter environment.
# Creates a local venv, installs deps, and verifies the suite + LibreOffice.
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
if [[ ! -d .venv ]]; then
  "$PY" -m venv .venv
fi
"./.venv/bin/pip" install -q -r requirements.txt

echo "[setup] python libs ok"

# LibreOffice detection (only a warning if absent; doc/ppt/wmf need it)
SOFFICE="${MMD_SOFFICE:-}"
if [[ -z "$SOFFICE" ]]; then
  for c in \
    "/Applications/LibreOffice.app/Contents/MacOS/soffice" \
    "$HOME/Applications/LibreOffice.app/Contents/MacOS/soffice" \
    "$(pwd)/../../.cache/LibreOffice.app/Contents/MacOS/soffice"; do
    [[ -x "$c" ]] && SOFFICE="$c" && break
  done
  [[ -z "$SOFFICE" ]] && SOFFICE="$(command -v soffice || true)"
fi
if [[ -z "$SOFFICE" ]]; then
  echo "[warn] LibreOffice not found; .doc/.ppt and WMF/EMF preview images will fail."
  echo "       Install LibreOffice or export MMD_SOFFICE=<path/to/soffice>"
else
  echo "[ok]   LibreOffice: $SOFFICE"
fi

echo "[ok]   dry-run sanity:"
"./.venv/bin/python" -m material_converter.main --dry | head -1 || true
echo "[done] ready. See README.md"
