"""Material -> Markdown batch converter (SOP v1.7 pipeline).

Usage (from apps/tools/material_converter/, with .venv active):
  python -m material_converter.convert                    # all courses, incremental
  python -m material_converter.convert --course 线性代数    # one 学科资料 folder
  python -m material_converter.convert --file <path>      # single file
  python -m material_converter.convert --dry              # no writes
  python -m material_converter.convert --validate         # run corpus validator after

Incremental by default: files whose original_path is already in
knowledge/manifest.csv are skipped. Byte/content duplicates are attributed to
one canonical copy per SOP step 1.7. New outputs are written as `pending`.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .courses import (IMAGE_ONLY_EXTS, TEXT_EXTS, knowledge_dir,
                      load_courses, source_prefix, subject_dirs)

from .courses import repo_root
REPO = repo_root()
KNOWLEDGE = REPO / "apps/scut-senior/knowledge"
MANIFEST = KNOWLEDGE / "manifest.csv"
CACHE = REPO / "apps/tools/material_converter/.work"          # gitignored scratch
FIELDS = ["source_id", "course", "title", "original_path", "format",
          "document_role", "year", "output_md", "locator_type", "method",
          "ocr_used", "ocr_confidence", "ocr_warning", "status",
          "reviewer", "notes"]

QUESTION_RX = re.compile(r"^[一二三四五六七八九十]{1,3}、")
EXAM_RX = re.compile(r"试卷|试题|期末|期中|考试|机试\d|Final Exam|EXAM")


def find_soffice() -> Path | None:
    env = os.environ.get("MMD_SOFFICE")
    cands = [
        Path(env) if env else None,
        REPO / ".cache/LibreOffice.app/Contents/MacOS/soffice",          # macOS (本仓缓存)
        Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),     # macOS 系统
        Path.home() / "Applications/LibreOffice.app/Contents/MacOS/soffice",
        _win_pf() / "LibreOffice/program/soffice.exe",                    # Windows
        _win_pf(86) / "LibreOffice/program/soffice.exe",
        Path("C:/Program Files/LibreOffice/program/soffice.exe"),
        Path("/usr/bin/soffice"),                                          # Linux
        Path("/usr/local/bin/soffice"),
    ]
    for c in cands:
        if c and c.exists():
            return c
    for name in ("soffice", "soffice.exe"):
        w = shutil.which(name)
        if w:
            return Path(w)
    return None


def _win_pf(bit=None) -> Path:
    key = "ProgramFiles(x86)" if bit == 86 else "ProgramFiles"
    return Path(os.environ.get(key, f"C:\\Program Files{'' if bit is None else ' (x86)'}"))


SOFFICE: Path | None = None


def soffice_convert(src: Path, target_ext: str, outdir: Path) -> Path | None:
    global SOFFICE
    if SOFFICE is None:
        SOFFICE = find_soffice()
    if SOFFICE is None:
        return None
    outdir.mkdir(parents=True, exist_ok=True)
    profile = (CACHE / "lo_profile")
    cmd = [str(SOFFICE), "--headless",
           f"-env:UserInstallation={profile.as_uri()}",
           "--convert-to", target_ext, "--outdir", str(outdir), str(src)]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return None
    expected = outdir / (src.stem + "." + target_ext.split(":")[0])
    return expected if expected.exists() else None


# ------------------------------------------------------------------ helpers


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def clean_title(fname: str) -> str:
    t = Path(fname).stem
    t = re.sub(r"^【包打听(分享)?】", "", t)
    t = t.replace("\u3000", " ").strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[（(]\d+[)）]$", "", t)
    t = re.sub(r"(?<=[^\d])\d{1,3}$", "", t)
    t = t.rstrip("-—_ .·")
    return t.strip() or Path(fname).stem


def guess_year(name: str) -> str:
    m = re.search(r"(?:19|20)\d{2}", name)
    return m.group(0) if m else ""


def guess_role(rel_path: str, fmt: str) -> str:
    base = os.path.basename(rel_path)
    if re.search(r"复习提纲|复习纲要|复习大纲|考试大纲|复习要点", base):
        return "review_outline"
    if EXAM_RX.search(base) or re.search(r"[A-Z]\s*卷|无答案|[A-Z]答案|[A-Z]解答", base):
        if re.search(r"模拟机试|模拟题|样卷", base):
            return "practice_exam"
        has_ans = bool(re.search(r"答案|解答|评分标准|附解答", base))
        return "past_exam_answer" if has_ans else "past_exam"
    if fmt == "pptx" or fmt == "ppt":
        return "lecture_slides" if "/PPT/" in rel_path else "note"
    if re.search(r"习题解答|习题与解答|习题课|题解", base):
        return "exercise_solution"
    if fmt in ("cpp", "c++"):
        return "exercise_solution"
    return "note"


PRIVACY_IDENTITY_PATTERNS = ("王杭",)  # extend as needed


def scrub_office_metadata(path: Path) -> bool:
    try:
        import zipfile
        zin = zipfile.ZipFile(path)
        items = zin.namelist()
        if "docProps/core.xml" not in items:
            zin.close()
            return False
        core = zin.read("docProps/core.xml").decode("utf-8", errors="ignore")
        orig = core

        def blank_if_identity(field_rx):
            nonlocal core
            for m in re.finditer(field_rx + r"([^<]*)</", core):
                val = m.group(1)
                if any(pat in val for pat in PRIVACY_IDENTITY_PATTERNS):
                    core = core.replace(m.group(0), field_rx + "</")

        blank_if_identity("<dc:creator>")
        blank_if_identity("<cp:lastModifiedBy>")
        for pat in PRIVACY_IDENTITY_PATTERNS:
            core = core.replace(pat, "")
        if core == orig:
            zin.close()
            return False
        tmp = path.with_suffix(path.suffix + ".tmp")
        zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
        for item in items:
            data = zin.read(item)
            if item == "docProps/core.xml":
                data = core.encode("utf-8")
            zout.writestr(item, data)
        zout.close()
        zin.close()
        tmp.replace(path)
        return True
    except Exception:
        return False


def scrub_pdf_metadata(path: Path) -> bool:
    try:
        import pymupdf
        doc = pymupdf.open(path)
        meta = doc.metadata or {}
        vals = " ".join(str(meta.get(k, "") or "") for k in
                        ("author", "creator", "producer", "lastModifyBy"))
        if not any(pat in vals for pat in PRIVACY_IDENTITY_PATTERNS):
            doc.close()
            return False
        for k in ("author", "lastModifyBy"):
            meta[k] = ""
        doc.set_metadata(meta)
        tmp = path.with_suffix(".scrub.pdf")
        doc.save(str(tmp), garbage=1, deflate=True)
        doc.close()
        tmp.replace(path)
        return True
    except Exception:
        return False


SEAL_LINE_RX = re.compile(
    r"(密\s*封\s*线|姓名\s*学号|姓名\n学号|Seal Line)", re.I)


def scan_privacy(text: str):
    """Return list of (kind, fragment). Distinguishes real identity from
    printed exam form templates."""
    hits = []
    for rx, label in [
        (re.compile(r"(?<!\d)20(?:1\d|2[0-6])\d{6}(?!\d)"), "student-id-like"),
        (re.compile(r"[\u4e00-\u9fff]{1,4}\d{1,2}班"), "class-label"),
    ]:
        for m in rx.finditer(text):
            frag = text[max(0, m.start() - 20):m.end() + 20].replace("\n", "⏎")
            hits.append((label, frag))
    return hits


def looks_like_template(hit_text: str) -> bool:
    return bool(SEAL_LINE_RX.search(hit_text))


# ------------------------------------------------------------------ dedup


NOANSWER_RX = re.compile(r"无答案")
CORE_RX = re.compile(r"无答案|参考答案|答案|解答|题解|评分标准")


def core_stem(name):
    return CORE_RX.sub("", Path(name).stem).strip()


def build_skip_set(files, existing_paths, manifest_rows=None):
    skip = {}
    manifest_rows = manifest_rows or []

    def noanswer_removed(name):
        return core_stem(name)

    def text_of(p, fmt):
        try:
            if fmt == "docx":
                md, _, _, _ = convert_docx(str(p), "")
                return re.sub(r"\s+", "", md)
            if fmt == "pdf":
                import pymupdf
                d = pymupdf.open(p)
                t = "".join(pg.get_text() for pg in d)
                d.close()
                return re.sub(r"\s+", "", t)
        except Exception:
            return ""
        return ""

    # 0) already-converted sources: match by hash and by no-answer basename
    manifest_md5 = {}
    manifest_basenames = {}
    manifest_by_dir = {}
    for r in manifest_rows:
        op = r.get("original_path") or ""
        src = REPO / op if op else None
        if src and src.exists():
            manifest_md5[md5(src)] = r["source_id"]
        base = Path(op).stem if op else ""
        if base:
            manifest_basenames.setdefault(noanswer_removed(base), []).append(
                {"sid": r["source_id"], "path": REPO / op if op else None,
                 "format": r.get("format", "/")})
        if op:
            parent_rel = str(Path(op).parent).replace(str(REPO), "").lstrip("/")
            manifest_by_dir.setdefault(parent_rel, []).append(
                {"sid": r["source_id"], "path": REPO / op if op else None,
                 "format": r.get("format", "/")})

    def manifest_text_of(entry):
        p = entry["path"]
        if not p or not p.exists():
            return ""
        if entry["format"] in ("docx", "pdf"):
            return text_of(p, entry["format"])
        return ""

    for f in files:
        if f["rel"] in skip:
            continue
        h = md5(f["path"])
        if h in manifest_md5:
            skip[f["rel"]] = f"byte-identical to already-converted {manifest_md5[h]}"
            continue
        cand = noanswer_removed(f["path"].name)
        # misfiled probability papers sitting in 工科数学分析I/13-19
        if "/工科数学分析I/历年试卷/13-19/" in f["rel"]:
            for base, ents in manifest_basenames.items():
                if cand == base:
                    for e in ents:
                        if e["sid"].startswith("probability-theory-"):
                            skip[f["rel"]] = ("misfiled probability duplicate; canonical "
                                              "already converted as " + e["sid"])
                    if f["rel"] in skip:
                        break
        entries = manifest_basenames.get(cand, [])
        if entries:
            # no-answer version whose matching answer version was already converted
            if NOANSWER_RX.search(f["path"].stem):
                skip[f["rel"]] = ("no-answer version; matching answer version already "
                                  "converted (" + ",".join(e["sid"] for e in entries) +
                                  "), SOP 1.7")
                continue
            # content duplicate of an already-converted source with same basename
            if f["format"] in ("docx", "pdf"):
                ft = text_of(f["path"], f["format"])
                if ft:
                    for e in entries:
                        mt = manifest_text_of(e)
                        if mt and mt == ft:
                            skip[f["rel"]] = f"content duplicate of already-converted {e['sid']}"
                            break

    # 1) byte duplicates among remaining candidates: prefer the one that is a
    #    canonical subject file (fewest path segments), else first sorted
    by_hash = {}
    for f in sorted(files, key=lambda x: (x["rel"].count("/"), x["rel"])):
        if f["rel"] in skip:
            continue
        h = md5(f["path"])
        by_hash.setdefault(h, []).append(f)
    for h, group in by_hash.items():
        if len(group) < 2:
            continue
        keep = group[0]
        for other in group[1:]:
            skip[other["rel"]] = f"byte-duplicate of {keep['rel']}"

    # 2) same-basename cross-course docx/pdf pairs with equal text content
    from .docx2md import convert_docx
    import pymupdf

    files_by_rel = {f["rel"]: f for f in files}
    by_name = {}
    for f in files:
        if f["format"] in ("docx", "pdf") and f["rel"] not in skip:
            by_name.setdefault(f["path"].name, []).append(f)
    for name, group in by_name.items():
        if len(group) < 2:
            continue
        keep = group[0]
        keep_text = None
        for other in group[1:]:
            if keep_text is None:
                keep_text = text_of(keep["path"], keep["format"])
            ot = text_of(other["path"], other["format"])
            if ot and keep_text and ot == keep_text:
                skip[other["rel"]] = f"content duplicate of {keep['rel']}"

    # 3) 无答案 strict subset of matching 答案 version (same directory stem)
    groups = {}
    for f in files:
        if f["rel"] in skip or NOANSWER_RX.search(f["path"].stem) is None:
            continue
        stem = NOANSWER_RX.sub("", f["path"].stem)
        for g in files:
            if g["rel"] in skip or g["format"] != f["format"]:
                continue
            if g["path"].parent != f["path"].parent:
                continue
            if NOANSWER_RX.search(g["path"].stem) is None and \
                    g["path"].stem.startswith(stem[:max(4, len(stem) - 4)]):
                groups.setdefault(f["rel"], []).append(g)
    for na_key, answers in groups.items():
        na_f = files_by_rel[na_key]
        # build answer candidates from same-dir files PLUS converted manifest sources
        ans_cands = list(answers)
        base = noanswer_removed(na_f["path"].name)

        def _cand_key(e):
            # plain file dicts (from `files`) have no "sid"; manifest entries do
            return (e.get("sid"), e["rel"])

        seen = {_cand_key(e) for e in ans_cands}
        for e in manifest_basenames.get(base, []):
            if e["path"] and e["path"].exists() and e["path"].parent == na_f["path"].parent:
                if (e["sid"], e["rel"]) not in seen:
                    ans_cands.append({"path": e["path"], "format": e["format"], "rel": e["sid"], "sid": e["sid"]})
        # same-dir answer whose filename prefix-matches (handles trailing numbers)
        parent_rel = str(na_f["path"].parent.relative_to(REPO))
        noans_stem = NOANSWER_RX.sub("", na_f["path"].stem)
        for e in manifest_by_dir.get(parent_rel, []):
            if e["sid"] in {c.get("sid") for c in ans_cands}:
                continue
            if e["path"] and e["path"].exists() and e["format"] == na_f["format"]:
                estem = NOANSWER_RX.sub("", e["path"].stem)
                if estem.startswith(noans_stem) or noans_stem.startswith(estem):
                    if "答案" in e["path"].stem or "解答" in e["path"].stem:
                        ans_cands.append({"path": e["path"], "format": e["format"],
                                          "rel": e["sid"], "sid": e["sid"]})
        if not ans_cands:
            continue
        ans = ans_cands[0]
        na_t = text_of(na_f["path"], na_f["format"])
        a_t = text_of(ans["path"], ans["format"])
        if na_t and a_t:
            paras = [p for p in na_t.split("。") if len(p) > 12]
            missing = [p for p in paras if p not in a_t]
            # tolerate page footers / filled blanks (whitespace-merged fragments)
            if len(paras) > 0 and len(missing) <= max(1, int(len(paras) * 0.30)):
                skip[na_key] = (
                    f"strict subset of {ans['rel']} (answer version wins, SOP 1.7)")
    return skip


# ------------------------------------------------------------------ assembly


def yaml_scalar(v) -> str:
    if v is None or v == "":
        return ""
    s = str(v)
    if re.match(r"^[A-Za-z0-9_\-]+$", s):
        return s
    return '"' + s.replace('"', '\\"') + '"'


def frontmatter_block(fm: dict) -> str:
    order = ["source_id", "course_id", "title", "original_file",
             "document_role", "year", "locator_type"]
    lines = ["---"]
    for k in order:
        v = fm.get(k)
        lines.append(f"{k}: {yaml_scalar(v)}")
    lines.append("---")
    return "\n".join(lines)


def clamp_headings(md: str) -> str:
    lines = md.split("\n")
    out, prev, fence = [], 0, False
    for ln in lines:
        if re.match(r"^\s*(```|~~~)", ln):
            fence = not fence
            out.append(ln)
            continue
        m = re.match(r"^(#{1,6}) (.*)$", ln)
        if m and not fence:
            lvl = len(m.group(1))
            if prev and lvl > prev + 1:
                lvl = prev + 1
            prev = lvl
            out.append("#" * lvl + " " + m.group(2))
        else:
            out.append(ln)
    return "\n".join(out)


_MERGE_BOLD = lambda s: re.sub(r"\*\*([^*]+)\*\*\*\*([^*]+)\*\*", r"**\1\2**", s)


def merge_emphasis(md: str) -> str:
    out, fence = [], False
    for ln in md.split("\n"):
        if re.match(r"^\s*(```|~~~)", ln):
            fence = not fence
            out.append(ln)
            continue
        if not fence and not ln.lstrip().startswith(("$$", "|")):
            prev = None
            while prev != ln:
                prev = ln
                ln = _MERGE_BOLD(ln)
        out.append(ln)
    return "\n".join(out)


def add_question_markers(md: str, sid: str, role: str):
    if role not in {"past_exam", "past_exam_answer", "practice_exam"}:
        return md, 0
    lines = md.split("\n")
    out, qn, fence = [], 0, False
    for ln in lines:
        if re.match(r"^\s*(```|~~~)", ln):
            fence = not fence
        if not fence and QUESTION_RX.match(ln.strip()) and len(ln.strip()) < 40:
            qn += 1
            out.append(f"<!-- question: {sid}-Q{qn} -->")
            out.append("")
        out.append(ln)
    return "\n".join(out), qn


# ------------------------------------------------------------------ convert


def detect_pdf_native(doc) -> tuple[bool, str]:
    """Return (native, reason). Detects corrupted (mojibake) text layers."""
    n_pages = max(1, len(doc))
    total = sum(len(p.get_text().strip()) for p in doc)
    sample = "".join(p.get_text() for p in doc[:min(4, n_pages)])
    nn = max(1, len(sample))
    latin_hi = sum(1 for ch in sample if "\u0080" <= ch <= "\u00ff")
    cjk = sum(1 for ch in sample if "\u4e00" <= ch <= "\u9fff")
    if total <= 40 * n_pages:
        return False, "image-only PDF"
    if latin_hi / nn > 0.03 and cjk / nn < 0.12:
        return False, "corrupted text layer (mojibake); rendered to images"
    return True, ""


def convert_file(f: dict, staging: Path):
    """Yield result dict for one candidate file."""
    from .docx2md import convert_docx
    from .pdf2md import convert_pdf
    p, fmt = f["path"], f["format"]
    if fmt == "docx":
        md, imgs, stats, _w = convert_docx(str(p), "")
        yield {"md": md, "images": imgs, "stats": stats,
               "method": "local OOXML extraction + omml2latex; OLE formulas kept as PNG preview fallback"}
    elif fmt == "doc":
        out = soffice_convert(p, "docx", staging / "doc")
        if not out:
            raise RuntimeError("LibreOffice doc->docx failed (is LibreOffice installed? set MMD_SOFFICE)")
        md, imgs, stats, _w = convert_docx(str(out), "")
        yield {"md": md, "images": imgs, "stats": stats,
               "method": "libreoffice doc->docx + OOXML extraction + omml2latex; OLE preview fallback"}
    elif fmt == "pptx":
        from .pptx2md import convert_pptx
        slides, imgs, stats = convert_pptx(str(p))
        yield {"slides": slides, "images": imgs, "stats": stats,
               "method": "python-pptx slide extraction"}
    elif fmt == "ppt":
        from .pptx2md import convert_pptx
        out = soffice_convert(p, "pptx", staging / "ppt")
        if not out:
            raise RuntimeError("LibreOffice ppt->pptx failed")
        slides, imgs, stats = convert_pptx(str(out))
        yield {"slides": slides, "images": imgs, "stats": stats,
               "method": "libreoffice ppt->pptx + python-pptx slide extraction"}
    elif fmt == "pdf":
        import pymupdf
        d = pymupdf.open(p)
        native, why = detect_pdf_native(d)
        d.close()
        pages, imgs, stats, native2 = convert_pdf(str(p), "", force_images=not native)
        method = ("pymupdf text-layer page extraction" if native else
                  f"pymupdf page rendering to JPEG assets ({why}; no OCR)")
        yield {"pages_md": pages, "images": imgs, "locator": "page",
               "stats": stats, "method": method}
    elif fmt in ("txt", "cpp", "c++"):
        text = p.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")
        lang = "cpp" if fmt in ("cpp", "c++") else "text"
        yield {"md": f"```{lang}\n{text}\n```", "images": [], "stats": {},
               "method": "plain-text/code normalization"}
    elif fmt == "md":
        text = p.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")
        yield {"md": text, "images": [], "stats": {},
               "method": "markdown normalization"}
    elif fmt.lstrip(".") in ("png", "jpg", "jpeg"):
        name = "page-001." + fmt
        yield {"md": f"![{name}](assets/{{ASSETS_DIR}}/{name})",
               "images": [(name, p.read_bytes())], "locator": "none",
               "stats": {}, "method": "single image embedded as stable asset"}


def flush_vector_png(vecs, workdir: Path):
    """Convert queued WMF/EMF assets to PNG. Returns {index: png_bytes}."""
    results = {}
    if not vecs:
        return results
    global SOFFICE
    if SOFFICE is None:
        SOFFICE = find_soffice()
    if SOFFICE is None:
        print(f"  ! LibreOffice missing; keeping {len(vecs)} WMF/EMF assets as-is")
        return results
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    jobs = []
    for i, apath in enumerate(vecs):
        src = workdir / f"job{i:05d}{apath.suffix.lower()}"
        shutil.copy2(apath, src)
        jobs.append((i, apath, src))
    CHUNK = 120
    for c in range(0, len(jobs), CHUNK):
        chunk = jobs[c:c + CHUNK]
        cmd = [str(SOFFICE), "--headless",
               f"-env:UserInstallation={(CACHE / 'lo_profile').as_uri()}",
               "--convert-to", "png", "--outdir", str(workdir)] + [str(s) for _, _, s in chunk]
        try:
            subprocess.run(cmd, capture_output=True, timeout=1800)
        except subprocess.TimeoutExpired:
            continue
    for i, apath, src in jobs:
        png = src.with_suffix(".png")
        if png.exists() and png.stat().st_size > 0:
            results[i] = (apath, png.read_bytes())
    shutil.rmtree(workdir, ignore_errors=True)
    return results
