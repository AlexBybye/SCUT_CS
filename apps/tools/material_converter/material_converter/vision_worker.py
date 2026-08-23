"""GLM-4V vision worker: formula-image -> LaTeX with consensus gating.

Pipeline per unique image (SOP §4: transcribe only what can be read reliably):
  1. two independent GLM-4V reads of the same image
  2. light normalization; accept ONLY if both agree
  3. deterministic checks (balanced delimiters, no CJK prose, sane length)
  4. anything else -> stays as PNG preview (SOP 4.2 fallback)

Results are appended as JSONL to .ai_jobs/_vision_results.jsonl so the run is
resumable; propagation into formulas.json + finalize happens as a separate step.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
# GLM4V_ENV / GLM4V_RESULTS let side experiments (e.g. the glm-4.6V probe rerun
# of the PNG-fallback waiver queue) run fully isolated from the historical
# glm-4v-flash configuration and results file.
ENV_FILE = Path(os.environ.get("GLM4V_ENV") or (REPO / ".cache/glm4v.env"))
JOBS = Path(__file__).resolve().parent.parent / ".ai_jobs"
RESULTS = Path(os.environ.get("GLM4V_RESULTS") or (JOBS / "_vision_results.jsonl"))

PROMPT = (
    "你是数学公式OCR引擎。识别图片中的数学表达式，只输出它的 LaTeX 代码："
    "不要 $ 定界符，不要任何解释或标点说明，不要换行；"
    "使用 \\frac{}{}、\\sqrt{}、上下标 _^ 、\\sum、\\int、\\lim 等标准命令。"
    "若图像模糊、非数学内容、或无法确信识别，只输出一个词：UNSURE"
)

_cfg = None


def load_cfg() -> dict:
    global _cfg
    if _cfg:
        return _cfg
    cfg = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    missing = [k for k in ("GLM_BASE_URL", "GLM_MODEL", "GLM_API_KEY") if not cfg.get(k)]
    if missing:
        raise SystemExit(f"glm4v.env missing: {missing}")
    _cfg = cfg
    return cfg


def _call_glm(image_path: Path, timeout: int = 60) -> str:
    cfg = load_cfg()
    mime = mimetypes.guess_type(str(image_path))[0] or "image/png"
    b64 = base64.b64encode(image_path.read_bytes()).decode()
    body = json.dumps({
        "model": cfg["GLM_MODEL"],
        "messages": [{"role": "user", "content": [
            {"type": "image_url",
             "image_url": {"url": f"data:{mime};base64,{b64}"}},
            {"type": "text", "text": PROMPT},
        ]}],
        "temperature": 0.1,
        "max_tokens": 512,
    }).encode()
    req = urllib.request.Request(
        cfg["GLM_BASE_URL"].rstrip("/") + "/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {cfg['GLM_API_KEY']}",
                 "Content-Type": "application/json"},
    )
    last_err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            if e.code in (429, 500, 502, 503, 504):
                # free-tier vision endpoints rate-limit aggressively; back off
                # hard on 429 so a full waiver-queue rerun can grind through
                time.sleep(min(90, (8 if e.code == 429 else 3) * (attempt + 1)))
                continue
            raise
        except Exception as e:  # noqa: BLE001
            last_err = str(e)[:120]
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"glm call failed after retries: {last_err}")


_WS = re.compile(r"\s+")
_CJK = re.compile(r"[\u4e00-\u9fff]")
_CMD = re.compile(r"\\[A-Za-z]+")


_GLUE = re.compile(
    r"\\(partial|nabla|prime|ell)([A-Za-z])")

_DISPLAY = re.compile(r"^\\[\[\(\$]+|\\[\]\)\$]+$")

def normalize(latex: str) -> str:
    s = latex.strip().strip("$ ").strip()
    s = _DISPLAY.sub("", s).strip()
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    s = _WS.sub("", s)
    # split glued no-arg commands AFTER whitespace removal (\partialz -> \partial z)
    s = _GLUE.sub(r"\\\1 \2", s)
    return s


_MATHTEXT = None

_ENV_RX = re.compile(r"\\begin\{(\w+)\}(?:\{[^}]*\})?(.*?)\\end\{\1\}", re.S)
_MATRIX_ENVS = {"bmatrix", "pmatrix", "vmatrix", "Bmatrix", "Vmatrix",
                "matrix", "smallmatrix", "array", "cases"}


def renders(latex: str) -> bool:
    """Deterministic gate: parse directly, or validate matrix env cell-by-cell."""
    global _MATHTEXT
    try:
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib.mathtext import MathTextParser
        if _MATHTEXT is None:
            os.environ.setdefault("MPLCONFIGDIR", str(REPO / ".cache/mpl"))
            Path(REPO / ".cache/mpl").mkdir(parents=True, exist_ok=True)
            _MATHTEXT = MathTextParser("agg")
        try:
            _MATHTEXT.parse(f"${latex}$", dpi=100, prop=None)
            return True
        except Exception:
            pass
        # mathtext lacks \begin{matrix}-style environments: validate cells instead
        m = _ENV_RX.search(latex)
        if not m or m.group(1) not in _MATRIX_ENVS:
            return False
        body = m.group(2)
        rest = _ENV_RX.sub("", latex)
        if _CMD.search(rest.replace("\\begin", "").replace("\\end", "")) and rest.strip():
            # non-env remainder must still render
            if rest.strip() and not renders(rest):
                return False
        for row in re.split(r"\\\\", body):
            for cell in row.split("&"):
                cell = cell.strip()
                if not cell:
                    continue
                if _CJK.search(cell) or len(cell) > 120:
                    return False
                try:
                    _MATHTEXT.parse(f"${cell}$", dpi=100, prop=None)
                except Exception:
                    return False
        return True
    except Exception:
        return False


def plausible(latex: str) -> bool:
    if not latex or latex.upper() == "UNSURE":
        return False
    if len(latex) > 400 or _CJK.search(latex):
        return False
    for a, b in (("{", "}"), ("[", "]"), ("(", ")")):
        if latex.count(a) != latex.count(b):
            return False
    for cmd in _CMD.findall(latex):
        if len(cmd) < 2 or len(cmd) > 20:
            return False
    if re.search(r"[；。，、！？：]", latex):
        return False
    return True


_NO_MATH = re.compile(r"没有(显示|任何)?(具体)?的?数学表达式|不包含数学|无法提取")


def transcribe_one(image_path: Path) -> dict:
    """Majority vote of up to 3 reads; accept only on agreement+plausibility+render."""
    votes = []
    try:
        for _ in range(3):
            votes.append(normalize(_call_glm(image_path)))
            if len(votes) >= 2 and votes[-1] == votes[-2] and plausible(votes[-1]):
                break  # early consensus on two is enough
    except Exception as e:  # noqa: BLE001
        return {"path": str(image_path), "latex": "", "why": f"api-error: {e}"}
    if any(_NO_MATH.search(v) for v in votes):
        return {"path": str(image_path), "latex": "", "why": "no-math-content"}
    if all(v.upper() == "UNSURE" for v in votes):
        return {"path": str(image_path), "latex": "", "why": "unsure"}
    # majority: any value appearing >=2 times wins the vote
    winner, hits = None, 0
    for v in set(votes):
        if votes.count(v) > hits:
            winner, hits = v, votes.count(v)
    if winner and hits >= 2 and plausible(winner) and renders(winner):
        return {"path": str(image_path), "latex": winner, "why": "majority+render"}
    if winner and hits == 1:
        return {"path": str(image_path), "latex": "", "why": "disagree"}
    return {"path": str(image_path), "latex": "", "why": "implausible-or-render"}


def run(limit: int | None = None, workers: int = 4,
        targets_file: str | None = None) -> None:
    uniq = json.loads((JOBS / "_unique_images.json").read_text(encoding="utf-8"))
    done = set()
    if RESULTS.exists():
        for line in RESULTS.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                # transient transport failures (e.g. HTTP 429) must not mark
                # an image as done, or a resumed run would silently skip it
                if str(rec.get("why", "")).startswith("api-error"):
                    continue
                done.add(rec["path"])
            except Exception:
                pass
    if targets_file:
        # explicit rerun list (e.g. the PNG-fallback waiver queue); accepts a
        # hash->path dict, hash->[paths] dict or a plain path list
        raw = json.loads(Path(targets_file).read_text(encoding="utf-8"))
        vals = raw.values() if isinstance(raw, dict) else raw
        wanted = [Path(v[0] if isinstance(v, list) else v) for v in vals]
    else:
        wanted = [
            Path(paths[0] if isinstance(paths, list) else paths)
            for paths in uniq.values()
        ]
    todo = [p for p in wanted if str(p) not in done]
    if limit:
        todo = todo[:limit]
    print(f"todo={len(todo)} done={len(done)} workers={workers}", flush=True)
    ok = bad = 0
    _model_tag = load_cfg().get("GLM_MODEL", "")
    with RESULTS.open("a", encoding="utf-8") as out, \
            ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(transcribe_one, p): p for p in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            r["model"] = _model_tag
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            out.flush()
            if r["latex"]:
                ok += 1
            else:
                bad += 1
            if i % 50 == 0 or i == len(todo):
                print(f"[{i}/{len(todo)}] accepted={ok} rejected={bad}", flush=True)
    print(f"FINAL accepted={ok} rejected={bad} pass_rate={ok / max(1, ok + bad):.1%}",
          flush=True)


if __name__ == "__main__":
    lim = None
    wk = 4
    tf = None
    args = sys.argv[1:]
    if "--sample" in args:
        lim = int(args[args.index("--sample") + 1])
    if "--workers" in args:
        wk = int(args[args.index("--workers") + 1])
    if "--targets" in args:
        tf = args[args.index("--targets") + 1]
    run(limit=lim, workers=wk, targets_file=tf)
