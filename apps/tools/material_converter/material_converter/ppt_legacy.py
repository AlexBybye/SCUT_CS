"""Legacy binary PowerPoint (.ppt) text extraction.

Scans the PowerPoint Document stream for TextCharsAtom / TextBytesAtom /
CString records. Record order approximates deck order; reliable per-slide
attribution is NOT guaranteed -> caller should use locator_type none unless
converted to PPTX by LibreOffice.
"""
from __future__ import annotations


def extract_ppt_texts(path: str):
    import olefile

    ole = olefile.OleFileIO(path)
    try:
        if not ole.exists("PowerPoint Document"):
            return [], {"error": "no PowerPoint Document stream"}
        data = ole.openstream("PowerPoint Document").read()
    finally:
        ole.close()

    TEXT_CHARS = 0x0FA0
    TEXT_BYTES = 0x0FA8
    CString = 0x0FBA
    texts = []

    i = 0
    n = len(data)
    while i + 8 <= n:
        ver_inst = int.from_bytes(data[i:i + 2], "little")
        rectype = int.from_bytes(data[i + 2:i + 4], "little")
        reclen = int.from_bytes(data[i + 4:i + 8], "little")
        body_start = i + 8
        if rectype in (TEXT_CHARS, TEXT_BYTES, CString):
            body = data[body_start:body_start + reclen]
            if rectype == TEXT_BYTES:
                try:
                    s = body.decode("cp1252", errors="replace")
                except Exception:
                    s = ""
            else:
                try:
                    s = body.decode("utf-16-le", errors="replace")
                except Exception:
                    s = ""
            # normalize CR/VT to newlines
            s = s.replace("\r", "\n").replace("\x0b", "\n")
            if s.strip():
                texts.append(s)
            i = body_start + reclen
            continue
        if rectype == 0x0001 or ver_inst & 0x000F == 0x000F:
            # container record (version nibble 0xF): descend
            i = body_start
        else:
            i = body_start + reclen
    stats = {"text_records": len(texts)}
    return texts, stats
