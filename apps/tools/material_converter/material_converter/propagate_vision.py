"""Propagate accepted vision transcriptions into .ai_jobs/<sid>/formulas.json.

Uses content-hash dedup: one transcription covers every identical PNG anywhere
in the knowledge base. Only entries that got a verified LaTeX string are filled;
everything else stays empty -> finalize leaves those images untouched (SOP 4.2).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from material_converter.courses import knowledge_dir

REPO = Path(__file__).resolve().parents[4]
K = REPO / "apps/scut-senior/knowledge"
JOBS = Path(__file__).resolve().parent.parent / ".ai_jobs"


def main() -> None:
    uniq = json.loads((JOBS / "_unique_images.json").read_text(encoding="utf-8"))
    latex_by_hash: dict[str, str] = {}
    for line in (JOBS / "_vision_results.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r.get("latex"):
            latex_by_hash[r["path"]] = r["latex"]
    # representative-path -> hash lookup
    hash_of: dict[str, str] = {}
    for h, paths in uniq.items():
        for p in paths:
            hash_of[p] = h

    def _direct(h: str) -> str:
        # results are keyed by representative path; map hash->latex once
        rep = uniq.get(h, [None])[0]
        return latex_by_hash.get(rep, "")

    total_imgs = filled = sids_touched = 0
    for jf in sorted(JOBS.glob("*/formulas.json")):
        sid = jf.parent.name
        meta = json.loads((jf.parent / "meta.json").read_text(encoding="utf-8"))
        course_dir = knowledge_dir(meta["course"])
        d = json.loads(jf.read_text(encoding="utf-8"))
        changed = False
        for name in list(d):
            if d[name]:
                continue
            total_imgs += 1
            ap = K / course_dir / "assets" / sid / name
            if not ap.exists():
                continue
            h = hashlib.md5(ap.read_bytes()).hexdigest()
            lat = _direct(h)
            if lat:
                d[name] = lat
                filled += 1
                changed = True
        if changed:
            jf.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                          encoding="utf-8")
            sids_touched += 1
    print(f"empty slots scanned={total_imgs} filled={filled} "
          f"({filled / max(1, total_imgs):.1%}) sids touched={sids_touched}")


if __name__ == "__main__":
    main()
