"""AI stage: the semantic/normalization layer on top of deterministic extraction.

convert.main produces the faithful skeleton (text/headings/tables/images,
native OMML->LaTeX, page/slide markers). It does NOT do AI-only work: OCR
correction, formula-image->LaTeX transcription, reading-order/heading
restoration, question-boundary proposal. This module bridges the two stages.

  * emit_ai_jobs  -> write an AI job package under .ai_jobs/<sid>/ for every file
    that benefits: source.md (rough body), formulas.json ({name:""} for each OLE
    formula preview needing LaTeX), ocr_pages.json (image-only pages to OCR),
    meta.json.
  * finalize_ai   -> apply AI answers: formulas.json {name: latex} replaces the
    image reference with $...$ / $$...$$ and deletes the now-unused formula
    asset; notes.md appends to manifest notes. status stays pending (SOP 4.2).

Guardrails: transcribe/restore/propose only -- never invent/summarize/correct.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path

from .courses import normalize_course_arg
from .convert import KNOWLEDGE, MANIFEST, REPO

AI_JOBS = Path(__file__).resolve().parent.parent / ".ai_jobs"
FORMULA_REF_RX = re.compile(r"!\[formula-object\]\(([^)]+?)\)")


def emit_ai_jobs(course=None) -> list[str]:
    course = normalize_course_arg(course)
    rows = _load_rows()
    emitted = []
    for r in rows:
        if course and r["course"] != course:
            continue
        if r["status"] != "pending":
            continue
        md_path = KNOWLEDGE / r["output_md"]
        if not md_path.exists():
            continue
        try:
            body = md_path.read_text(encoding="utf-8").split("---", 2)[-1]
        except Exception:
            continue
        sid = r["source_id"]
        formula_names = []
        for m in FORMULA_REF_RX.finditer(body):
            name = m.group(1).rsplit("/", 1)[-1]
            if name.lower().endswith(".png"):
                formula_names.append(name)
        ocr_pages = [{"page_image": m.group(1), "kind": "scan_page"}
                     for m in re.finditer(r"\]\(assets/[^)]*/(page-\d{3}\.jpg)\)", body)]
        if not formula_names and not ocr_pages:
            continue
        sid_dir = AI_JOBS / sid
        if sid_dir.exists():
            shutil.rmtree(sid_dir)
        sid_dir.mkdir(parents=True)
        (sid_dir / "source.md").write_text(body, encoding="utf-8")
        (sid_dir / "formulas.json").write_text(
            json.dumps({n: "" for n in dict.fromkeys(formula_names)},
                       ensure_ascii=False, indent=1), encoding="utf-8")
        (sid_dir / "ocr_pages.json").write_text(
            json.dumps(ocr_pages, ensure_ascii=False, indent=1), encoding="utf-8")
        (sid_dir / "meta.json").write_text(
            json.dumps({"source_id": sid, "course": r["course"],
                        "title": r["title"], "document_role": r["document_role"],
                        "original_path": r["original_path"],
                        "output_md": r["output_md"]}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        emitted.append(sid)
    return emitted


def _load_rows():
    return list(csv.DictReader(open(MANIFEST, encoding="utf-8-sig")))


def _save_rows(rows):
    fields = ["source_id", "course", "title", "original_path", "format",
              "document_role", "year", "output_md", "locator_type", "method",
              "ocr_used", "ocr_confidence", "ocr_warning", "status",
              "reviewer", "notes"]
    with open(MANIFEST, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _latex_block(latex, standalone):
    latex = str(latex).strip()
    return f"\n$$\n{latex}\n$$\n" if standalone else f"${latex}$"


def finalize_ai(course=None) -> list:
    course = normalize_course_arg(course)
    rows = _load_rows()
    by_sid = {r["source_id"]: r for r in rows}
    finalized = []
    if not AI_JOBS.exists():
        return finalized
    for sid_dir in sorted(AI_JOBS.iterdir()):
        if not sid_dir.is_dir():
            continue
        sid = sid_dir.name
        r = by_sid.get(sid)
        if not r:
            continue
        if course and r["course"] != course:
            continue
        formulas_json = sid_dir / "formulas.json"
        notes_md = sid_dir / "notes.md"
        if not formulas_json.exists() and not notes_md.exists():
            continue
        md_path = KNOWLEDGE / r["output_md"]
        if not md_path.exists():
            continue
        changed = []
        md = md_path.read_text(encoding="utf-8")
        assets_dir = KNOWLEDGE / r["course"] / "assets" / sid
        if formulas_json.exists():
            try:
                formulas = json.loads(formulas_json.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                formulas = {}
            for name, latex in formulas.items():
                latex = str(latex or "").strip()
                if not latex:
                    continue
                pattern = re.compile(r"!\[formula-object\]\(assets/" + re.escape(sid)
                                     + "/" + re.escape(name) + r"\)")
                matches = list(pattern.finditer(md))
                standalone = False
                if matches:
                    line = md[matches[0].start():].split("\n", 1)[0]
                    standalone = not line.replace("![", "").replace("]", "").strip()
                    md = pattern.sub(lambda _: _latex_block(latex, standalone), md)
                else:
                    pattern2 = re.compile(r"!\[formula-object\]\([^)]*/" + re.escape(name) + r"\)")
                    if pattern2.search(md):
                        md = pattern2.sub(lambda _: _latex_block(latex, False), md)
                apath = assets_dir / name
                if apath.exists() and f"![formula-object](assets/{sid}/{name})" not in md:
                    apath.unlink(missing_ok=True)
                changed.append(name)
        if notes_md.exists():
            extra = notes_md.read_text(encoding="utf-8").strip()
            if extra:
                r["notes"] = (r["notes"] + "; " + extra)[:1400]
        if changed or notes_md.exists():
            if changed:
                r["notes"] = (r["notes"] + "; " +
                              f"AI-transcribed {len(changed)} formula images to LaTeX; "
                              "needs human re-check per SOP 4.2")[:1400]
                r["status"] = "pending"
            md_path.write_text(md, encoding="utf-8")
            finalized.append((sid, changed))
    _save_rows(rows)
    return finalized
