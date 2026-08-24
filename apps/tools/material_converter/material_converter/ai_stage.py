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
    # FIELDS is the single source of truth for manifest columns (incl. preview)
    from .convert import FIELDS
    with open(MANIFEST, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def _latex_block(latex, standalone):
    latex = str(latex).strip()
    return f"\n$$\n{latex}\n$$\n" if standalone else f"${latex}$"


_REF_RX = re.compile(r"!\[formula-object\]\((assets/[^)]+?)\)")


def _apply_formulas(md: str, latex_by_ref: dict) -> tuple[str, list]:
    """Per-reference conservative replacement.

    - replace ONLY refs that have a verified latex string
    - whole-line display ($$...$$) wrapping happens only when the line consists
      of exactly one ref and nothing else
    - refs without latex stay as images; no $ chars are ever added around them
    """
    changed = []

    def repl(match):
        ref = match.group(1)
        name = ref.rsplit("/", 1)[-1]
        latex = latex_by_ref.get(name)
        if not latex:
            return match.group(0)
        changed.append(name)
        return f"${latex}$"

    out_lines = []
    for line in md.split("\n"):
        if "![formula-object]" in line:
            new_line = _REF_RX.sub(repl, line)
            stripped = new_line.strip()
            # display block only for a single now-latex-only line
            if ("$" in stripped and "![formula-object]" not in stripped
                    and _REF_RX.search(line) is not None
                    and len(_REF_RX.findall(line)) == 1
                    and re.fullmatch(r"\$[^$]+\$", stripped)):
                inner = stripped[1:-1]
                new_line = f"$$\n{inner}\n$$"
            out_lines.append(new_line)
        else:
            out_lines.append(line)
    return "\n".join(out_lines), changed


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
        md = md_path.read_text(encoding="utf-8")
        assets_dir = KNOWLEDGE / r["course"] / "assets" / sid

        latex_by_name = {}
        if formulas_json.exists():
            try:
                raw = json.loads(formulas_json.read_text(encoding="utf-8"))
                latex_by_name = {k: str(v or "").strip() for k, v in raw.items()
                                 if str(v or "").strip()}
            except json.JSONDecodeError:
                latex_by_name = {}

        changed = []
        if latex_by_name:
            md, changed = _apply_formulas(md, latex_by_name)

        if notes_md.exists():
            extra = notes_md.read_text(encoding="utf-8").strip()
            if extra:
                r["notes"] = (r["notes"] + "; " + extra)[:1400]

        if changed or notes_md.exists():
            if changed:
                r["notes"] = (r["notes"] + "; " +
                              f"AI-transcribed {len(changed)} formula images to LaTeX "
                              "(GLM-4V majority-vote + render gate); pending human "
                              "re-check per SOP 4.2")[:1400]
                r["status"] = "pending"
                for name in changed:
                    apath = assets_dir / name
                    if apath.exists() and f"/{name})" not in md:
                        apath.unlink(missing_ok=True)
            md_path.write_text(md, encoding="utf-8")
            finalized.append((sid, changed))

    _save_rows(rows)
    return finalized
