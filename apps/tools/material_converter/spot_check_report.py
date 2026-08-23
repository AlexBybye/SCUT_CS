"""Stratified spot-check bundle for AI-transcribed formula LaTeX (SOP §12A Group D).

Samples accepted (image, latex) pairs from .ai_jobs/*/formulas.json across
courses, renders every sampled LaTeX through the SAME deterministic renderer
used by gate 3 (matplotlib mathtext), and emits:
  resources/evaluation/vision-spot-check/items.json      machine-readable samples
  resources/evaluation/vision-spot-check/sheet-*.png     contact sheets for human review
  resources/evaluation/vision-spot-check/index.html      side-by-side review page

The bundle records tool-assisted findings only; the final semantic-error
verdict belongs to the human reviewer per SOP §4.1 item 7.
"""
from __future__ import annotations

import base64
import html
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "material_converter"))

REPO = Path(__file__).resolve().parents[3]
K = REPO / "apps/scut-senior/knowledge"
JOBS = Path(__file__).resolve().parent / ".ai_jobs"
OUT = REPO / "apps/scut-senior/resources/evaluation/vision-spot-check"

SAMPLE_TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 30


def render_latex(latex: str, dest: Path) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        from matplotlib import pyplot as plt
        from matplotlib.mathtext import MathTextParser

        parser = MathTextParser("agg")
        parser.parse(f"${latex}$", dpi=120, prop=None)
        fig = plt.figure(figsize=(0.1, 0.1))
        fig.text(0, 0, f"${latex}$", fontsize=14)
        buf = dest.with_suffix(".tmp.png")
        fig.savefig(buf, dpi=140, bbox_inches="tight", pad_inches=0.08,
                    facecolor="white")
        plt.close(fig)
        buf.replace(dest)
        return True
    except Exception:
        dest.unlink(missing_ok=True)
        return False


def _recover_from_git(repo_path: str, dest: Path) -> bool:
    """Fetch a since-deleted asset's bytes from the newest commit holding it."""
    import subprocess

    try:
        touched = subprocess.run(
            ["git", "log", "--format=%H", "-n", "1", "--", repo_path],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        commit = touched.stdout.strip()
        if not commit:
            return False
        blob = subprocess.run(
            ["git", "show", f"{commit}^:{repo_path}"],
            cwd=REPO, capture_output=True, timeout=30,
        )
        if blob.returncode != 0 or not blob.stdout:
            return False
        dest.write_bytes(blob.stdout)
        return True
    except Exception:
        return False


def main() -> None:
    # pool = accepted transcriptions from the vision results log; the recorded
    # path IS the original asset image. Finalize deleted many transcribed
    # assets, so originals are recovered from git history when missing
    # (provenance recorded per item).
    latex_by_path: dict[str, str] = {}
    for line in (JOBS / "_vision_results.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("latex"):
            latex_by_path[r["path"]] = r["latex"]

    by_course: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for path, latex in latex_by_path.items():
        p = Path(path)
        try:
            parts = p.parts
            k_i = parts.index("knowledge")
            course, sid = parts[k_i + 1], parts[k_i + 3]
        except (ValueError, IndexError):
            continue
        by_course[course].append((path, latex, sid))

    rng = random.Random(20260823)  # fixed seed -> reproducible sample
    courses = sorted(by_course)
    per_course = max(1, SAMPLE_TARGET // len(courses))
    picked: list[tuple[str, str, str]] = []

    def try_pick(pool: list[tuple[str, str, str]], want: int) -> int:
        """Shuffle-pick entries whose original image is still retrievable."""
        got = 0
        cand = pool[:]
        rng.shuffle(cand)
        for img, latex, sid in cand:
            if got >= want:
                break
            p = Path(img)
            ok = p.exists()
            if not ok:
                probe = OUT / "_probe.png"
                ok = _recover_from_git(p.relative_to(REPO).as_posix(), probe)
                probe.unlink(missing_ok=True)
            if ok:
                picked.append((img, latex, sid))
                got += 1
        return got

    others_pool = [t for c in courses if c != "probability" for t in by_course[c]]
    got_others = try_pick(others_pool, SAMPLE_TARGET // 2)
    got_prob = try_pick(list(by_course.get("probability", [])),
                        SAMPLE_TARGET - len(picked))
    skipped_unrecoverable = (
        len(others_pool) - got_others if got_others < SAMPLE_TARGET // 2 else 0
    )
    while len(picked) > SAMPLE_TARGET:
        picked.pop(rng.randrange(len(picked)))

    OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for i, (img, latex, sid) in enumerate(picked, 1):
        src = Path(img)
        dest_orig = OUT / f"{i:02d}-original.png"
        recovered = False
        if src.exists():
            dest_orig.write_bytes(src.read_bytes())
        else:
            recovered = _recover_from_git(
                src.relative_to(REPO).as_posix(), dest_orig
            )
            if not recovered:
                continue  # unrecoverable original -> not reviewable, skip
        dest_render = OUT / f"{i:02d}-rendered.png"
        rendered = render_latex(latex, dest_render)
        items.append({
            "id": i,
            "source_id": sid,
            "image_repo_path": src.relative_to(REPO).as_posix(),
            "latex": latex,
            "rendered_ok": rendered,
            "original_recovered_from_git": recovered,
            "original_file": (Path("vision-spot-check") / f"{i:02d}-original.png").as_posix(),
            "rendered_file": (Path("vision-spot-check") / f"{i:02d}-rendered.png").as_posix(),
        })

    (OUT / "items.json").write_text(
        json.dumps({"sample_target": SAMPLE_TARGET, "seed": 20260823,
                    "courses": {c: len(v) for c, v in by_course.items()},
                    "unrecoverable_others_pool_surplus": skipped_unrecoverable,
                    "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    rows = []
    for it in items:
        orig_b64 = base64.b64encode((OUT / Path(it["original_file"]).name).read_bytes()).decode()
        rend = OUT / Path(it["rendered_file"]).name
        rend_b64 = base64.b64encode(rend.read_bytes()).decode() if rend.exists() else ""
        rows.append(f"""
<tr><td>{it['id']}<br><small>{html.escape(it['source_id'])}</small></td>
<td><img src="data:image/png;base64,{orig_b64}" style="max-width:260px"></td>
<td>{f'<img src="data:image/png;base64,{rend_b64}" style="max-width:300px">' if rend_b64 else '<b>RENDER FAILED</b>'}</td>
<td><code>{html.escape(it['latex'])}</code></td>
<td class="v"></td></tr>""")

    (OUT / "index.html").write_text(f"""<!doctype html><meta charset="utf-8">
<title>视觉转写抽查（{len(items)} 例）</title>
<style>body{{font-family:sans-serif;margin:16px}}table{{border-collapse:collapse}}
td,th{{border:1px solid #bbb;padding:6px;vertical-align:top}}td.v{{min-width:110px}}</style>
<h1>AI 转写公式抽查 — 原图 vs 渲染 vs LaTeX</h1>
<p>判定口径：<b>正确</b>＝语义一致；<b>轻微</b>＝仅排版/定界差异；<b>语义错误</b>＝结构、项数、上下标含义不符。终审由维护者逐项签署。</p>
<table><tr><th>#</th><th>原图</th><th>LaTeX 渲染</th><th>LaTeX 源码</th><th>判定</th></tr>
{''.join(rows)}</table>""", encoding="utf-8")
    print(f"samples={len(items)} courses={len(courses)} -> {OUT}")


if __name__ == "__main__":
    main()
