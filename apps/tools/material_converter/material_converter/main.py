"""CLI entrypoint for the material converter."""
from __future__ import annotations

import argparse
import csv
import re
import os
import shutil
import sys
from pathlib import Path

from .courses import IMAGE_ONLY_EXTS, TEXT_EXTS, knowledge_dir, load_courses, source_prefix, subject_dirs
from .convert import (CACHE, FIELDS, KNOWLEDGE, MANIFEST, REPO,
                      SOFFICE, add_question_markers,
                      build_skip_set, clean_title, clamp_headings,
                      convert_file, find_soffice, flush_vector_png,
                      frontmatter_block, guess_role, guess_year,
                      looks_like_template, merge_emphasis, md5,
                      scan_asset_integrity, scrub_office_metadata,
                      scrub_pdf_metadata, scan_privacy)


def collect_files(only_folder=None):
    files = []
    dirs = subject_dirs()
    for cid, folder in sorted(dirs.items()):
        if only_folder and folder != only_folder:
            continue
        base = REPO / "学科资料" / folder
        if not base.exists():
            continue
        for f in os_walk(base):
                ext = f.suffix.lower()
                if f.name.startswith(("._", "~$")) or f.name == ".DS_Store":
                    continue
                if ext in TEXT_EXTS or ext in IMAGE_ONLY_EXTS:
                    rel = str(f.relative_to(REPO))
                    files.append({"path": f, "rel": rel, "course": cid,
                                  "format": ext[1:], "size": f.stat().st_size})
    return files


def os_walk(base: Path):
    stack = [base]
    while stack:
        d = stack.pop()
        for child in sorted(d.iterdir()):
            if child.is_dir():
                if child.name.startswith(".") or child.name == "__MACOSX":
                    continue
                stack.append(child)
            else:
                yield child


def load_manifest():
    with open(MANIFEST, newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def next_counters(rows):
    used = {}
    for r in rows:
        m = re.match(r"^(.*)-(\d{3})$", r["source_id"])
        if m:
            pre, num = m.group(1), int(m.group(2))
            used[pre] = max(used.get(pre, 0), num)
    return used


def run(args):
    global SOFFICE
    SOFFICE = find_soffice()

    only = args.course
    files = collect_files(only_folder=only)
    if args.file:
        target = str(Path(args.file).resolve().relative_to(REPO))
        files = [f for f in files if f["rel"] == target]
        if not files:
            print(f"file not a candidate under 学科资料: {args.file}")
            return 2

    rows = load_manifest()
    existing_paths = {r["original_path"] for r in rows}
    counters = next_counters(rows)

    # incremental skip + dedup decisions
    todo = []
    for f in files:
        if f["rel"] in existing_paths:
            continue
        todo.append(f)
    skip = build_skip_set(todo, existing_paths, manifest_rows=rows)

    print(f"candidates={len(todo)} already_in_manifest={len(files)-len(todo)} "
          f"dedup_skipped={len(skip)} soffice={'yes' if SOFFICE else 'NO'}")

    staging = CACHE / "staging"
    vec_queue = []      # (abs_asset_path)
    new_rows, report = [], []

    for f in todo:
        rel = f["rel"]
        if rel in skip:
            report.append({"path": rel, "action": "skip", "reason": skip[rel]})
            continue

        # privacy pre-pass on source metadata
        if f["format"] in ("docx", "pptx"):
            scrub_office_metadata(f["path"])
        elif f["format"] == "pdf":
            scrub_pdf_metadata(f["path"])

        try:
            res = next(convert_file(f, staging))
        except Exception as e:
            report.append({"path": rel, "action": "error", "reason": str(e)[:200]})
            continue

        prefix = source_prefix(f["course"])
        counters[prefix] = counters.get(prefix, 0) + 1
        sid = f"{prefix}-{counters[prefix]:03d}"
        title = clean_title(f["path"].name)
        role = guess_role(rel, f["format"])
        year = guess_year(f["path"].name)

        kdir = knowledge_dir(f["course"])
        assets_abs = kdir / "assets" / sid
        assets_abs.mkdir(parents=True, exist_ok=True)
        assets_rel = f"assets/{sid}"

        images_out = []
        vec_idx = []
        for name, data in res.get("images", []):
            apath = assets_abs / name
            apath.write_bytes(data)
            images_out.append(name)
            if name.lower().endswith((".wmf", ".emf")):
                vec_idx.append(apath)

        stats = res.get("stats", {})
        method = res.get("method", "")

        # ---- body
        if "pages_md" in res:
            body = "\n".join(res["pages_md"]).replace("{ASSETS_DIR}", sid)
            locator = "page"
        elif "slides" in res:
            chunks = []
            for no, lines, notes in res["slides"]:
                filtered = []
                for ln in lines:
                    t = ln.strip()
                    if t in ("<number>", "&lt;number&gt;"):
                        continue
                    if t.isdigit() and int(t) == no:
                        continue
                    filtered.append(ln.replace("{ASSETS_DIR}", sid))
                chunk = [f"<!-- slide: {no} -->", ""]
                chunk += filtered
                if notes:
                    chunk += ["", f"> 备注：{notes}"]
                chunks.append("\n".join(chunk).rstrip())
            body = "\n\n".join(chunks)
            locator = "slide"
        else:
            body = res["md"].replace("{ASSETS_DIR}", sid)
            has_heading = bool(re.search(r"^#{1,6} ", body, re.M))
            locator = res.get("locator") or ("heading" if has_heading else "none")
            if locator == "heading" and not has_heading:
                locator = "none"

        warnings = []
        hits = scan_privacy(body)
        real_hits = [(k, v) for k, v in hits if not looks_like_template(v)]
        tpl_hits = len(hits) - len(real_hits)
        if real_hits:
            warnings.append("PRIVACY-HIT(needs manual de-identification): "
                            + ";".join(k for k, _ in real_hits[:5]))
        if tpl_hits:
            warnings.append(f"{tpl_hits} printed form-template fields kept (not personal data)")

        body, qn = add_question_markers(body, sid, role)
        if qn:
            warnings.append(f"{qn} tool-proposed question boundaries need human confirmation")
        ole = int(stats.get("ole_objects", 0))
        omml = int(stats.get("math_inline", 0)) + int(stats.get("math_display", 0))

        fm = frontmatter_block({
            "source_id": sid, "course_id": f["course"], "title": title,
            "original_file": rel, "document_role": role, "year": year,
            "locator_type": locator})
        md = fm + "\n\n# " + title + "\n\n" + body.strip() + "\n"
        md = merge_emphasis(clamp_headings(md))
        md = re.sub(r"\]\(assets/assets/", "](assets/", md)

        out_rel = str(kdir.relative_to(KNOWLEDGE) / f"{sid}.md")
        out_path = KNOWLEDGE / out_rel
        if not args.dry:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")

        notes = ["AI-assisted batch conversion, pending human review."]
        if ole:
            notes.append(f"{ole} OLE/MathType formula objects preserved as preview-image fallback")
        if omml:
            notes.append(f"{omml} native OMML formulas converted to LaTeX")
        notes.extend(warnings)
        row = {
            "source_id": sid, "course": f["course"], "title": title,
            "original_path": rel, "format": f["format"], "document_role": role,
            "year": year, "output_md": out_rel, "locator_type": locator,
            "method": method, "ocr_used": "false", "ocr_confidence": "",
            "ocr_warning": "", "preview": "false", "status": "pending",
            "reviewer": "",
            "notes": ("; ".join(notes))[:1400],
        }
        new_rows.append(row)

        if vec_idx:
            vec_queue.extend(vec_idx)
        report.append({"path": rel, "action": "converted", "source_id": sid,
                       "locator": locator, "images": len(images_out),
                       "ole_fallback": ole, "omml_latex": omml})

    # vector -> png + ref rewrite
    if vec_queue and not args.dry:
        results = flush_vector_png(vec_queue, CACHE / "wmf_batch")
        ok = fail = 0
        by_dir = {}
        for apath in vec_queue:
            by_dir.setdefault(apath.parent, []).append(apath)
        for i, (apath, png_bytes) in results.items():
            png_path = apath.with_suffix(".png")
            png_path.write_bytes(png_bytes)
            apath.unlink(missing_ok=True)
            md_file = apath.parent.parent.parent / (apath.parent.name + ".md")
            if md_file.exists():
                t = md_file.read_text(encoding="utf-8")
                t = t.replace(apath.name, png_path.name)
                md_file.write_text(t, encoding="utf-8")
            ok += 1
        fail = len(vec_queue) - ok
        print(f"vector->png ok={ok} kept-as-vector={fail}")

    # 资产完整性扫描（教训：坏引用曾静默入库）
    broken = scan_asset_integrity()
    if broken:
        print(f"asset-broken={len(broken)}")
        for b in broken[:10]:
            print("  !", b)
    if not args.dry and new_rows:
        with open(MANIFEST, "a", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=list(FIELDS))
            w.writerows(new_rows)

    conv_n = sum(1 for r in report if r["action"] == "converted")
    err_n = sum(1 for r in report if r["action"] == "error")
    skip_n = sum(1 for r in report if r["action"] == "skip")
    print(f"converted={conv_n} skipped={skip_n} errors={err_n}")
    for r in report:
        if r["action"] in ("error", "skip"):
            print("  ", r["action"], r["path"], "|", r.get("reason", "")[:120])
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "last_run_report.json").write_text(
        __import__("json").dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    if args.validate:
        return run_validator()
    return 0


def run_validator() -> int:
    import subprocess
    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    env["PYTHONPATH"] = str(REPO / "apps/scut-senior/worker/src")
    r = subprocess.run([sys.executable, "-c",
                        "from pathlib import Path;"
                        "from scut_senior_worker.corpus_validator import validate_corpus;"
                        "rep=validate_corpus(Path(r'%s'),Path(r'%s'));"
                        "print('validator OK:',rep.ok,'errors:',len(rep.errors));"
                        "[print(' -',e[:160]) for e in rep.errors[:20]]"
                        % (MANIFEST, KNOWLEDGE)],
                       env=env, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip()[:500])
    return r.returncode


def main(argv=None):
    ap = argparse.ArgumentParser(prog="material_converter",
                                 description="学科资料 -> knowledge Markdown 批量转换（SOP v1.7）")
    ap.add_argument("--course", help="只处理某学科资料文件夹名，如 线性代数")
    ap.add_argument("--file", help="只转换单个文件（相对仓库根或绝对路径）")
    ap.add_argument("--dry", action="store_true", help="只报告，不写任何文件")
    ap.add_argument("--validate", action="store_true", help="结束后运行 corpus validator")
    ap.add_argument("--emit-ai-jobs", nargs="?", const="", help="导出AI任务包到 .ai_jobs/<sid>/（可限定课程）")
    ap.add_argument("--finalize", nargs="?", const="", help="把 .ai_jobs/ 中AI回填结果应用到 knowledge + manifest（可限定课程）")
    ap.add_argument("--vision-run", nargs="?", const="all", help="GLM-4V 视觉转写全部待转公式（可给数字限制张数，如 --vision-run 20）")
    ap.add_argument("--vision-workers", type=int, default=4, help="视觉转写并发数（默认4）")
    ap.add_argument("--vision-propagate", action="store_true", help="把转写结果按内容哈希传播进 formulas.json")
    args = ap.parse_args(argv)
    if args.emit_ai_jobs is not None:
        from .ai_stage import emit_ai_jobs
        em = emit_ai_jobs(args.emit_ai_jobs or None)
        print(f"emitted AI jobs: {len(em)}")
        for s in em: print("  ", s)
        return 0
    if args.vision_run is not None:
        os.environ.setdefault("MPLCONFIGDIR", str(REPO / ".cache/mpl"))
        (REPO / ".cache/mpl").mkdir(parents=True, exist_ok=True)
        from .vision_worker import run as vision_run
        lim = None if args.vision_run == "all" else int(args.vision_run)
        vision_run(limit=lim, workers=args.vision_workers)
        return 0
    if args.vision_propagate:
        from .propagate_vision import main as prop
        prop()
        return 0
    if args.finalize is not None:
        from .ai_stage import finalize_ai
        fn = finalize_ai(args.finalize or None)
        print(f"finalized AI: {len(fn)}")
        for sid, changed in fn: print("  ", sid, changed)
        return 0
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
