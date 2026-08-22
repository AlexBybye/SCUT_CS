#!/usr/bin/env bash
# material_converter 环境引导（macOS/Linux）：在仓库根创建 .venv 并安装依赖
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$REPO"

PY="${PYTHON:-python3}"
[[ -x "$PY" ]] || PY=python3
if [[ ! -d .venv ]]; then
  "$PY" -m venv .venv
fi
"./.venv/bin/pip" install -q --upgrade pip
"./.venv/bin/pip" install -q -r apps/tools/material_converter/requirements.txt
echo "[setup] python libs ok (.venv @ repo root)"

SOFFICE="${MMD_SOFFICE:-}"
if [[ -z "$SOFFICE" ]]; then
  for c in \
    "$REPO/.cache/LibreOffice.app/Contents/MacOS/soffice" \
    "/Applications/LibreOffice.app/Contents/MacOS/soffice" \
    "$HOME/Applications/LibreOffice.app/Contents/MacOS/soffice" \
    /usr/bin/soffice /usr/local/bin/soffice; do
    [[ -x "$c" ]] && SOFFICE="$c" && break
  done
  [[ -z "$SOFFICE" ]] && SOFFICE="$(command -v soffice || true)"
fi
if [[ -z "$SOFFICE" ]]; then
  echo "[warn] LibreOffice 未找到：doc/ppt 与 WMF/EMF 公式将失败"
  echo "       安装后 export MMD_SOFFICE=<soffice 路径>"
else
  echo "[ok]   LibreOffice: $SOFFICE （建议写入 shell profile 的 MMD_SOFFICE）"
fi

echo "[ok]   dry-run sanity:"
(cd apps/tools/material_converter && MMD_SOFFICE="${MMD_SOFFICE:-$SOFFICE}" \
  "$REPO/.venv/bin/python" -m material_converter.main --dry | head -1) || true
echo "[done] 用法见 apps/tools/material_converter/README.md"
