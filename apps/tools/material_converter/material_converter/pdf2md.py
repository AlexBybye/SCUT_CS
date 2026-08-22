"""PDF -> Markdown.

Native-text PDFs: per-page block extraction with page markers.
Image-only PDFs: page rendering to stable JPEG assets with page markers.
No OCR, no invention; faithful ordering by layout blocks.
"""
from __future__ import annotations

import re


def _clean(text: str) -> str:
    text = text.replace("\u00a0", " ")
    # drop form feed artifacts, collapse spaces
    lines = []
    for ln in text.splitlines():
        ln = ln.rstrip()
        if ln.strip():
            lines.append(ln)
    return "\n".join(lines)


def convert_pdf(path: str, assets_dir: str, dpi: int = 150, force_images: bool = False):
    """Return (pages_md:list[str], images:list[(name,bytes)], stats, native_text:bool)."""
    import pymupdf

    doc = pymupdf.open(path)
    pages_md = []
    images = []
    total_chars = 0
    for page in doc:
        total_chars += len(page.get_text().strip())
    native = (total_chars > 40 * len(doc)) and not force_images

    img_idx = 0
    if not native:
        # image-only: render each page
        zoom = dpi / 72.0
        mat = pymupdf.Matrix(zoom, zoom)
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=mat)
            name = f"page-{i:03d}.jpg"
            data = pix.tobytes("jpeg", jpg_quality=85)
            images.append((name, data))
            marker = f"<!-- page: {i} -->"
            body = [marker, "", f"![{name}](assets/{{ASSETS_DIR}}/{name})", ""]
            pages_md.append("\n".join(body))
        stats = {"pages": len(doc), "native_text": False, "rendered_pages": len(images)}
        doc.close()
        return pages_md, images, stats, False

    for i, page in enumerate(doc, 1):
        parts = [f"<!-- page: {i} -->", ""]
        try:
            blocks = page.get_text("blocks")
        except Exception:
            blocks = []
        blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))
        for b in blocks:
            x0, y0, x1, y1, text, bno, btype = b[:7]
            t = _clean(text)
            if not t:
                continue
            parts.append(t)
            parts.append("")
        md = "\n".join(parts).rstrip() + "\n"
        pages_md.append(md)

        # extract meaningful raster images on the page (photos/diagrams)
        try:
            for img in page.get_images(full=True):
                xref = img[0]
                base = doc.extract_image(xref)
                if base and base.get("image") and len(base["image"]) > 8000:
                    img_idx += 1
                    ext = "." + (base.get("ext") or "png")
                    name = f"image-{img_idx:03d}{ext}"
                    images.append((name, base["image"]))
                    pages_md[-1] += f"\n![image](assets/{{ASSETS_DIR}}/{name})\n"
        except Exception:
            pass
    stats = {"pages": len(doc), "native_text": True}
    doc.close()
    return pages_md, images, stats, True
