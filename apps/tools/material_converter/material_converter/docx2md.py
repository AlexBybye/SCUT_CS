"""DOCX -> normalized Markdown converter.

Structural, faithful extraction: headings, paragraphs, lists, tables,
images, OMML math (via omml2latex) and OLE-object fallback images.
No summarizing, no correction, no invention.
"""
from __future__ import annotations

import os
import re
import shutil
import zipfile
from dataclasses import dataclass, field
from xml.etree import ElementTree as ET

from .omml2latex import convert_omml_element

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
V = "{urn:schemas-microsoft-com:vml}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
O = "{urn:schemas-microsoft-com:office:office}"


@dataclass
class ImageOut:
    src_member: str
    data: bytes
    ext: str


@dataclass
class ConvertResult:
    blocks: list = field(default_factory=list)  # list of dicts
    images: list = field(default_factory=list)  # ImageOut list in order
    stats: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)


def _local(tag):
    return tag.split("}", 1)[-1]


class DocxConverter:
    def __init__(self, path: str):
        self.path = path
        self.z = zipfile.ZipFile(path)
        self.doc_xml = self.z.read("word/document.xml")
        self.root = ET.fromstring(self.doc_xml)
        self.rels = {}
        self._load_rels()
        self.result = ConvertResult()
        self.image_index = 0
        self.stats = {
            "math_inline": 0,
            "math_display": 0,
            "ole_objects": 0,
            "images": 0,
            "tables": 0,
            "footnote_refs": 0,
        }
        self.warnings: list[str] = []

    def _load_rels(self):
        try:
            rels_xml = self.z.read("word/_rels/document.xml.rels")
        except KeyError:
            return
        root = ET.fromstring(rels_xml)
        for rel in root:
            rid = rel.get("Id")
            target = rel.get("Target")
            if rid and target:
                self.rels[rid] = target

    def close(self):
        self.z.close()

    # ------------------------------------------------------------- helpers
    def _member_bytes(self, target: str):
        target = target.lstrip("/")
        if target.startswith("word/"):
            member = target
        else:
            member = "word/" + target
        try:
            return self.z.read(member)
        except KeyError:
            try:
                return self.z.read(target)
            except KeyError:
                return None

    def _save_image(self, rid: str | None, member_hint: str | None = None) -> str | None:
        data = None
        ext = ".png"
        member = None
        if rid and rid in self.rels:
            target = self.rels[rid]
            member = "word/" + target.lstrip("/") if not target.startswith("word/") else target
            try:
                data = self.z.read(member)
            except KeyError:
                data = None
            if data is not None:
                ext = os.path.splitext(member)[1].lower() or ".png"
        if data is None and member_hint:
            try:
                data = self.z.read(member_hint)
                member = member_hint
                ext = os.path.splitext(member)[1].lower() or ".png"
            except KeyError:
                return None
        if data is None:
            return None
        self.image_index += 1
        name = f"image-{self.image_index:03d}{ext}"
        self.result.images.append(ImageOut(member or "", data, ext))
        self.stats["images"] += 1
        return name

    # ------------------------------------------------------------- inline
    def _inline(self, el, bold=False, italic=False) -> str:
        out = []
        tag_local = _local(el.tag)
        if tag_local == "r":
            out.append(self._run(el, bold, italic))
            return "".join(out)
        if tag_local == "oMath":
            latex, _ = convert_omml_element(el)
            self.stats["math_inline"] += 1
            return f"${latex}$"
        if tag_local == "hyperlink":
            rid = el.get(R + "id")
            url = self.rels.get(rid, "") if rid else ""
            inner = "".join(self._inline(c, bold, italic) for c in el)
            inner = inner.strip() or url
            if url.startswith("http"):
                return f"[{inner}]({url})"
            return inner
        if tag_local in ("drawing", "pict"):
            name = self._drawing_image(el)
            if name:
                out.append(f"![image](assets/{{ASSETS_DIR}}/{name})")
            return "".join(out)
        if tag_local == "object":
            self.stats["ole_objects"] += 1
            # OLE object: use its fallback image (formula preview or icon)
            name = self._object_image(el)
            if name:
                out.append(f"![formula-object](assets/{{ASSETS_DIR}}/{name})")
            return "".join(out)
        if tag_local == "br":
            t = el.get(W + "type", "")
            return "\n" if t != "page" else "\n"
        if tag_local == "tab":
            return "\t"
        if tag_local == "footnoteReference":
            self.stats["footnote_refs"] += 1
            return ""
        if tag_local == "sym":
            ch = el.get(W + "char", "")
            try:
                return chr(int(ch, 16))
            except ValueError:
                return ""
        # smartTag, sdt content, etc: recurse
        for c in el:
            out.append(self._inline(c, bold, italic))
        return "".join(out)

    def _run(self, el, bold, italic) -> str:
        rpr = el.find(W + "rPr")
        b, i = bold, italic
        if rpr is not None:
            if rpr.find(W + "b") is not None:
                v = rpr.find(W + "b").get(W + "val", "1")
                b = b or v not in ("0", "false")
            if rpr.find(W + "i") is not None:
                v = rpr.find(W + "i").get(W + "val", "1")
                i = i or v not in ("0", "false")
            if rpr.find(W + "vanish") is not None:
                v = rpr.find(W + "vanish").get(W + "val", "1")
                if v not in ("0", "false"):
                    return ""
        parts = []
        for c in el:
            local = _local(c.tag)
            if local == "t":
                parts.append(c.text or "")
            elif local == "tab":
                parts.append("\t")
            elif local == "br":
                t = c.get(W + "type", "")
                if t == "page":
                    parts.append("\n")
                else:
                    parts.append(" ")
            elif local == "drawing":
                parts.append(self._inline(c, b, i))
            elif local in ("object", "pict"):
                parts.append(self._inline(c, b, i))
            elif local == "sym":
                parts.append(self._inline(c, b, i))
            elif local == "footnoteReference":
                self.stats["footnote_refs"] += 1
            elif local == "noBreakHyphen":
                parts.append("-")
            # rPr, others ignored
        text = "".join(parts)
        text = text.replace("\u00a0", " ")
        if not text.strip():
            return text
        core = text
        if i and not b:
            core = f"*{core.strip()}*" if core.strip() else core
        elif b and not i:
            core = f"**{core.strip()}**" if core.strip() else core
        elif b and i:
            core = f"***{core.strip()}***" if core.strip() else core
        # preserve leading/trailing whitespace outside emphasis
        lead = text[: len(text) - len(text.lstrip())]
        trail = text[len(text.rstrip()):]
        return lead + core + trail

    def _drawing_image(self, el) -> str | None:
        # a:blip embed
        for blip in el.iter(A + "blip"):
            rid = blip.get(R + "embed")
            return self._save_image(rid)
        # VML imagedata (in pict)
        for imd in el.iter(V + "imagedata"):
            rid = imd.get(R + "id")
            return self._save_image(rid)
        return None

    def _object_image(self, el) -> str | None:
        for shape in el.iter(V + "shape"):
            imd = shape.find(V + "imagedata")
            if imd is not None:
                rid = imd.get(R + "id")
                name = self._save_image(rid)
                if name:
                    return name
        for pict in el.iter():
            if _local(pict.tag) == "imagedata":
                rid = pict.get(R + "id")
                name = self._save_image(rid)
                if name:
                    return name
        return None

    # ------------------------------------------------------------- blocks
    def _para(self, p) -> dict:
        ppr = p.find(W + "pPr")
        style = ""
        num_id = ilvl = None
        if ppr is not None:
            ps = ppr.find(W + "pStyle")
            if ps is not None:
                style = ps.get(W + "val", "")
            npr = ppr.find(W + "numPr")
            if npr is not None:
                nid = npr.find(W + "numId")
                il = npr.find(W + "ilvl")
                num_id = nid.get(W + "val") if nid is not None else None
                ilvl = il.get(W + "val") if il is not None else "0"
        # gather inline content
        parts = []
        has_display_math = False
        for c in p:
            local = _local(c.tag)
            if local == "oMathPara":
                for om in c.findall(M + "oMath"):
                    latex, _ = convert_omml_element(om)
                    parts.append(("DISPLAY", latex))
                    self.stats["math_display"] += 1
                    has_display_math = True
            elif local == "oMath":
                parts.append(("TEXT", self._inline(c, False, False)))
            else:
                parts.append(("TEXT", self._inline(c, False, False)))
        text = "".join(v for k, v in parts if k == "TEXT")
        display = [v for k, v in parts if k == "DISPLAY"]

        level = None
        m = re.match(r"Heading(\d)", style)
        if m:
            level = int(m.group(1))
        elif style == "Title":
            level = 1

        return {
            "kind": "para",
            "text": text,
            "display_math": display,
            "heading_level": level,
            "style": style,
            "num_id": num_id,
            "ilvl": int(ilvl) if ilvl and ilvl.isdigit() else None,
        }

    def _table(self, tbl) -> dict:
        self.stats["tables"] += 1
        rows = []
        has_merge = False
        has_math = False
        for tr in tbl.findall(W + "tr"):
            cells = []
            for tc in tr.findall(W + "tc"):
                tcpr = tc.find(W + "tcPr")
                span = 1
                vmerge = None
                if tcpr is not None:
                    gs = tcpr.find(W + "gridSpan")
                    if gs is not None:
                        span = int(gs.get(W + "val", "1"))
                    vm = tcpr.find(W + "vMerge")
                    if vm is not None:
                        vmerge = vm.get(W + "val", "continue")
                paras = []
                for p in tc.findall(W + "p"):
                    d = self._para(p)
                    if d["display_math"]:
                        has_math = True
                    t = d["text"].strip()
                    if d["display_math"]:
                        t = " ".join(d["display_math"]) + (" " + t if t else "")
                    if t:
                        paras.append(t)
                cell = "<br>".join(paras)
                cell = cell.replace("|", "\\|")
                if span > 1 or vmerge is not None:
                    has_merge = True
                cells.append((cell, span))
            rows.append(cells)
        return {"kind": "table", "rows": rows, "complex": has_merge or has_math}

    def convert(self) -> ConvertResult:
        body = self.root.find(W + "body")
        for child in body:
            local = _local(child.tag)
            if local == "p":
                self.result.blocks.append(self._para(child))
            elif local == "tbl":
                self.result.blocks.append(self._table(child))
            elif local == "sectPr":
                continue
            else:
                # sdt etc: recurse into content
                for sub in child.iter(W + "p"):
                    self.result.blocks.append(self._para(sub))
        self.result.stats = self.stats
        self.result.warnings = self.warnings
        return self.result


def _numbering_map(z: zipfile.ZipFile) -> dict:
    """numId -> 'ol' if decimal else 'ul'."""
    result = {}
    try:
        root = ET.fromstring(z.read("word/numbering.xml"))
    except KeyError:
        return result
    WNS = W
    abstract_fmt = {}
    for an in root.findall(WNS + "abstractNum"):
        aid = an.get(WNS + "abstractNumId")
        lvl0 = an.find(WNS + "lvl")
        if aid is not None and lvl0 is not None:
            fmt = lvl0.find(WNS + "numFmt")
            if fmt is not None:
                abstract_fmt[aid] = fmt.get(WNS + "val", "bullet")
    for num in root.findall(WNS + "num"):
        nid = num.get(WNS + "numId")
        ref = num.find(WNS + "abstractNumId")
        if nid is not None and ref is not None:
            aid = ref.get(WNS + "val")
            fmt = abstract_fmt.get(aid, "bullet")
            result[nid] = "ol" if fmt in ("decimal", "chicago", "romanLower", "romanUpper", "letterLower", "letterUpper") else "ul"
    return result


def md_escape_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", "<br>")


def render_markdown(res: ConvertResult, assets_dir: str, numbering: dict) -> tuple[str, list[str]]:
    """Render blocks to markdown. Returns (markdown, image_filenames)."""
    lines = []
    images = []
    pending_list = None  # ('ul'|'ol', indent_level)

    def flush_list():
        nonlocal pending_list
        pending_list = None

    for blk in res.blocks:
        if blk["kind"] == "table":
            flush_list()
            lines.append("")
            rows = blk["rows"]
            if not rows:
                continue
            ncols = max(len(r) for r in rows)
            if blk["complex"] or ncols == 0:
                # HTML table
                lines.append("<table>")
                for r in rows:
                    lines.append("<tr>" + "".join(f"<td>{c}</td>" for c, s in r) + "</tr>")
                lines.append("</table>")
                lines.append("")
                continue
            def row_md(r):
                cells = [c for c, s in r] + [""] * (ncols - len(r))
                return "| " + " | ".join(cells) + " |"
            lines.append(row_md(rows[0]))
            lines.append("|" + "---|" * ncols)
            for r in rows[1:]:
                lines.append(row_md(r))
            lines.append("")
        else:
            text = blk["text"].strip()
            display = blk["display_math"]
            if blk["heading_level"]:
                flush_list()
                lvl = min(blk["heading_level"], 6)
                if text:
                    lines.append("")
                    lines.append("#" * lvl + " " + text)
                    lines.append("")
            elif display:
                flush_list()
                for d in display:
                    lines.append("")
                    lines.append("$$")
                    lines.append(d)
                    lines.append("$$")
                    lines.append("")
                if text:
                    lines.append(text)
                    lines.append("")
            else:
                if blk["num_id"] and blk["num_id"] in numbering:
                    flush_list()
                    kind = numbering[blk["num_id"]]
                    indent = "  " * (blk["ilvl"] or 0)
                    marker = "1." if kind == "ol" else "-"
                    if text:
                        lines.append(f"{indent}{marker} {text}")
                else:
                    if pending_list and not text:
                        flush_list()
                    elif text:
                        flush_list()
                        lines.append(text)
                        lines.append("")
                    else:
                        pass
            if text and blk["num_id"] not in (numbering or {}):
                pass

    md = "\n".join(lines)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = md.replace("{ASSETS_DIR}", assets_dir)
    return md, [im.src_member for im in res.images]


def convert_docx(path: str, assets_dir: str) -> tuple[str, list[tuple[str, bytes]], dict, list[str]]:
    """Convert DOCX to markdown.

    Returns (markdown, [(asset_name, bytes)], stats, warnings).
    """
    conv = DocxConverter(path)
    res = conv.convert()
    numbering = _numbering_map(conv.z)
    stats = dict(conv.stats)
    warnings = list(conv.warnings)
    md_lines = []
    image_files = []
    # second pass render with real asset names
    name_map = {}
    for idx, img in enumerate(res.images, 1):
        name = f"image-{idx:03d}{img.ext}"
        name_map[img.src_member] = name
        image_files.append((name, img.data))
    # render
    lines = []
    pending_list = None
    for blk in res.blocks:
        if blk["kind"] == "table":
            pending_list = None
            lines.append("")
            rows = blk["rows"]
            if not rows:
                continue
            ncols = max(len(r) for r in rows)
            if blk["complex"] or ncols == 0:
                lines.append("<table>")
                for r in rows:
                    lines.append("<tr>" + "".join(f"<td>{c}</td>" for c, s in r) + "</tr>")
                lines.append("</table>")
                lines.append("")
                continue
            def row_md(r):
                cells = [c for c, s in r] + [""] * (ncols - len(r))
                return "| " + " | ".join(cells) + " |"
            lines.append(row_md(rows[0]))
            lines.append("|" + "---|" * ncols)
            for r in rows[1:]:
                lines.append(row_md(r))
            lines.append("")
        else:
            text = blk["text"]
            display = blk["display_math"]
            if blk["heading_level"]:
                pending_list = None
                lvl = min(blk["heading_level"], 6)
                t = text.strip()
                if t:
                    lines.append("")
                    lines.append("#" * lvl + " " + t)
                    lines.append("")
            elif display:
                pending_list = None
                for d in display:
                    lines.append("")
                    lines.append("$$")
                    lines.append(d)
                    lines.append("$$")
                    lines.append("")
                t = text.strip()
                if t:
                    lines.append(t)
                    lines.append("")
            else:
                t = text.strip()
                if blk["num_id"] and blk["num_id"] in numbering:
                    kind = numbering[blk["num_id"]]
                    indent = "  " * (blk["ilvl"] or 0)
                    marker = "1." if kind == "ol" else "-"
                    if t:
                        lines.append(f"{indent}{marker} {t}")
                else:
                    if t:
                        pending_list = None
                        lines.append("")
                        lines.append(t)
    md = "\n".join(lines)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = postprocess_md(md)
    stats["image_count"] = len(image_files)
    conv.close()
    return md, image_files, stats, warnings


_MERGE_BOLD = re.compile(r"\*\*(?:[^*]|\*(?!\*))+\*\*")
def _merge_pass(md: str) -> str:
    # merge adjacent bold spans: **a****b** -> **ab**
    changed = True
    while changed:
        new = re.sub(r"(\*\*(?:[^*]+?)\*\*)\*\*((?:[^*]+?)\*\*)", r"\1\2\3", md) if False else md
        # simpler: replace '**x****y**' pairs iteratively via regex on non-greedy groups
        new = re.sub(r"\*\*([^*]+)\*\*\*\*([^*]+)\*\*", r"**\1\2**", md)
        if new == md:
            changed = False
        md = new
    changed = True
    while changed:
        new = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)\*([^*\n]+)\*(?!\*)", r"*\1\2*", md)
        if new == md:
            changed = False
        md = new
    return md


def postprocess_md(md: str) -> str:
    """Merge fragmented emphasis runs produced by run-level bold/italic."""
    lines = md.split("\n")
    out = []
    in_fence = False
    for ln in lines:
        if re.match(r"^\s*(```|~~~)", ln):
            in_fence = not in_fence
            out.append(ln)
            continue
        if in_fence or ln.startswith("$$") or ln.startswith("|"):
            out.append(ln)
            continue
        out.append(_merge_pass(ln))
    return "\n".join(out)
