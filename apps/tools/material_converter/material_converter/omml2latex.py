"""OMML (Office Math Markup Language) -> LaTeX converter.

Faithful structural conversion only: it renders what the OMML tree contains.
It never invents content. Unknown constructs degrade to their inner text so
nothing is silently dropped.
"""
from __future__ import annotations

import re
from xml.etree import ElementTree as ET

M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

# ---------------------------------------------------------------- char map
_GREEK = {
    "α": r"\alpha ", "β": r"\beta ", "γ": r"\gamma ", "δ": r"\delta ",
    "ε": r"\varepsilon ", "ζ": r"\zeta ", "η": r"\eta ", "θ": r"\theta ",
    "ι": r"\iota ", "κ": r"\kappa ", "λ": r"\lambda ", "μ": r"\mu ",
    "ν": r"\nu ", "ξ": r"\xi ", "π": r"\pi ", "ρ": r"\rho ",
    "σ": r"\sigma ", "τ": r"\tau ", "υ": r"\upsilon ", "φ": r"\varphi ",
    "χ": r"\chi ", "ψ": r"\psi ", "ω": r"\omega ",
    "Γ": r"\Gamma ", "Δ": r"\Delta ", "Θ": r"\Theta ", "Λ": r"\Lambda ",
    "Ξ": r"\Xi ", "Π": r"\Pi ", "Σ": r"\Sigma ", "Φ": r"\Phi ",
    "Ψ": r"\Psi ", "Ω": r"\Omega ", "ϕ": r"\phi ", "ϵ": r"\epsilon ",
    "ϑ": r"\vartheta ", "ϖ": r"\varpi ", "ϱ": r"\varrho ", "ς": r"\varsigma ",
    "Υ": r"\Upsilon ", "ϝ": r"\digamma ",
}
_SYMBOLS = {
    "∞": r"\infty ", "×": r"\times ", "÷": r"\div ", "±": r"\pm ",
    "∓": r"\mp ", "≤": r"\le ", "≥": r"\ge ", "≠": r"\neq ", "≈": r"\approx ",
    "≡": r"\equiv ", "∼": r"\sim ", "∝": r"\propto ", "∈": r"\in ",
    "∉": r"\notin ", "⊂": r"\subset ", "⊃": r"\supset ", "⊆": r"\subseteq ",
    "⊇": r"\supseteq ", "∪": r"\cup ", "∩": r"\cap ", "∅": r"\emptyset ",
    "∀": r"\forall ", "∃": r"\exists ", "∇": r"\nabla ", "→": r"\to ",
    "←": r"\leftarrow ", "↔": r"\leftrightarrow ", "⇒": r"\Rightarrow ",
    "⇐": r"\Leftarrow ", "⇔": r"\Leftrightarrow ", "↑": r"\uparrow ",
    "↓": r"\downarrow ", "⇀": r"\rightharpoonup ", "↦": r"\mapsto ",
    "∂": r"\partial ", "°": r"^{\circ} ", "·": r"\cdot ", "⋅": r"\cdot ",
    "…": r"\ldots ", "⋯": r"\cdots ", "⋮": r"\vdots ", "⋱": r"\ddots ",
    "′": "'", "″": "''", "‴": "'''", "←": r"\leftarrow ",
    "⇋": r"\rightleftharpoons ", "⊥": r"\perp ", "∥": r"\parallel ",
    "∠": r"\angle ", "△": r"\triangle ", "⊙": r"\odot ", "∘": r"\circ ",
    "⊕": r"\oplus ", "⊗": r"\otimes ", "−": "-", "–": "-", "—": "-",
    "“": '"', "”": '"', "‘": "'", "’": "'", "　": r"\quad ",
    "∵": r"\because ", "∴": r"\therefore ", "≜": r"\triangleq ",
    "≐": r"\doteq ", "≲": r"\lesssim ", "≳": r"\gtrsim ", "⋆": r"\star ",
    "⁄": "/", "√": r"\sqrt ", "∛": r"\sqrt[3] ", "∜": r"\sqrt[4] ",
    "ℏ": r"\hbar ", "ℓ": r"\ell ", "ℜ": r"\Re ", "ℑ": r"\Im ",
    "℘": r"\wp ", "ℤ": r"\mathbb{Z}", "ℝ": r"\mathbb{R}",
    "ℕ": r"\mathbb{N}", "ℚ": r"\mathbb{Q}", "ℂ": r"\mathbb{C}",
    "𝟙": r"\mathbb{1}", "⟨": r"\langle ", "⟩": r"\rangle ",
    "⌊": r"\lfloor ", "⌋": r"\rfloor ", "⌈": r"\lceil ", "⌉": r"\rceil ",
    "{": r"\{ ", "}": r"\} ", "\\": r"\backslash ", "^": r"^", "_": r"_",
    "&": r"\& ", "%": r"\% ", "#": r"\# ", "$": r"\$ ", "~": r"\sim ",
    "～": r"\sim ", "｜": "|", "│": "|",
}
_NARY = {
    "∑": r"\sum ", "∏": r"\prod ", "∫": r"\int ", "∬": r"\iint ",
    "∭": r"\iiint ", "∮": r"\oint ", "⋃": r"\bigcup ", "⋂": r"\bigcap ",
    "⋁": r"\bigvee ", "⋀": r"\bigwedge ", "⨁": r"\bigoplus ",
    "⨂": r"\bigotimes ", "⨄": r"\biguplus ",
}

_MATH_ALNUM_BLOCKS = [
    (0x1D538, 0x1D56B, "bold"),        # bold
    (0x1D56C, 0x1D59F, "italic-bold"),
    (0x1D608, 0x1D63B, "italic"),      # actually italic block start 1D434
    (0x1D434, 0x1D467, "italic"),
    (0x1D400, 0x1D433, "bold"),
    (0x1D49C, 0x1D4CF, "script"),      # script + fraktur + double-struck region
    (0x1D6A8, 0x1D7CB, "greek-bold-italic"),
]


def _map_math_alnum(ch: str) -> str:
    cp = ord(ch)
    # Mathematical Alphanumeric Symbols (excluding already-inserted holes)
    if 0x1D400 <= cp <= 0x1D7FF:
        # Determine base letter by known offset tables
        import unicodedata
        name = unicodedata.name(ch, "")
        # e.g. "MATHEMATICAL BOLD CAPITAL A", "MATHEMATICAL ITALIC SMALL X"
        parts = name.split()
        if len(parts) >= 3 and parts[0] == "MATHEMATICAL":
            letter = parts[-1]
            if len(letter) == 1 and letter.isalpha():
                style = " ".join(parts[1:-1])
                if "FRAKTUR" in style:
                    cmd = "mathfrak"
                elif "SCRIPT" in style or "CALLIGRAPHIC" in style:
                    cmd = "mathcal"
                elif "DOUBLE-STRUCK" in style:
                    cmd = "mathbb"
                elif "MONOSPACE" in style:
                    cmd = "mathtt"
                elif "SANS-SERIF" in style:
                    cmd = "mathsf"
                elif "BOLD" in style and "ITALIC" in style:
                    cmd = "boldsymbol"
                    return r"\boldsymbol{" + letter + "}"
                elif "BOLD" in style:
                    cmd = "mathbf"
                    return r"\mathbf{" + letter + "}"
                elif "ITALIC" in style:
                    return letter + " "
                else:
                    return letter + " "
                return "\\" + cmd + "{" + letter + "}"
    return ch


def _esc_text(t: str) -> str:
    out = []
    for ch in t:
        if ch in _GREEK:
            out.append(_GREEK[ch])
        elif ch in _SYMBOLS:
            out.append(_SYMBOLS[ch])
        elif ch in _NARY:
            out.append(_NARY[ch])
        elif ord(ch) >= 0x1D400:
            out.append(_map_math_alnum(ch))
        elif ch.isdigit() or ch.isalpha():
            out.append(ch)
        elif ch == " ":
            out.append(" ")
        elif ch in "()[],.|<>+=-/*'!?:;":
            out.append(ch)
        else:
            out.append(ch)  # pass through unknown punctuation
    return "".join(out)


def _q(tag: str) -> str:
    return M + tag


def _first_child(el, tag):
    return el.find(_q(tag))


def _children(el, tag):
    return el.findall(_q(tag))


def _txt(el) -> str:
    """Concatenate all m:t under element (used for fName etc.)."""
    parts = []
    for t in el.iter(_q("t")):
        parts.append(t.text or "")
    return "".join(parts)


class Converter:
    def __init__(self):
        self.warnings: list[str] = []

    def convert(self, omath) -> str:
        body = self._el(omath)
        return _tidy(body)

    # ------------------------------------------------------------- elements
    def _el(self, el) -> str:
        tag = el.tag
        if tag == _q("r"):
            return self._run(el)
        if tag == _q("f"):
            num = self._of(el, "num")
            den = self._of(el, "den")
            ftype = ""
            pr = _first_child(el, "fPr")
            if pr is not None:
                t = pr.find(_q("type"))
                if t is not None:
                    ftype = t.get(M + "val", "")
            if ftype == "skw":
                return r"{}^{}/{}".format(num, den, "") if False else f"{num}/{den}"
            if ftype == "lin":
                return f"{num}/{den}"
            return rf"\frac {{{num}}} {{{den}}}"
        if tag == _q("sSup"):
            return "{" + self._of(el, "e") + "}^{" + self._of(el, "sup") + "}"
        if tag == _q("sSub"):
            return "{" + self._of(el, "e") + "}_{" + self._of(el, "sub") + "}"
        if tag == _q("sSubSup"):
            return ("{" + self._of(el, "e") + "}_{" + self._of(el, "sub")
                    + "}^{" + self._of(el, "sup") + "}")
        if tag == _q("rad"):
            deg = self._of(el, "deg") if el.find(_q("deg")) is not None else ""
            pr = _first_child(el, "radPr")
            hide_deg = False
            if pr is not None:
                hd = pr.find(_q("degHide"))
                hide_deg = hd is not None and hd.get(M + "val") in ("1", "on", "true")
            e = self._of(el, "e")
            if hide_deg or not deg.strip():
                return rf"\sqrt {{{e}}}"
            return rf"\sqrt [{deg}] {{{e}}}"
        if tag == _q("d"):
            return self._delim(el)
        if tag == _q("nary"):
            return self._nary(el)
        if tag == _q("func"):
            name = self._of(el, "fName")
            e = self._of(el, "e")
            return f"{name} {e}"
        if tag == _q("limLow"):
            e = self._of(el, "e")
            lim = self._of(el, "lim")
            base_txt = _txt(el.find(_q("e"))).strip()
            if base_txt in ("lim", "Lim", "LIM"):
                return rf"\lim_ {{{lim}}} {e if e.strip()!=base_txt else ''}"
            if base_txt in ("max", "min"):
                return rf"\{base_txt}_ {{{lim}}} "
            return f"{e}_{{{lim}}}"
        if tag == _q("limUpp"):
            e = self._of(el, "e")
            lim = self._of(el, "lim")
            return f"{e}^{{{lim}}}"
        if tag == _q("acc"):
            pr = _first_child(el, "accPr")
            ch = "̂"
            if pr is not None:
                c = pr.find(_q("chr"))
                if c is not None:
                    ch = c.get(M + "val", "̂")
            e = self._of(el, "e")
            accmap = {"̂": r"\hat ", "́": r"\acute ", "̄": r"\bar ",
                      "̇": r"\dot ", "̈": r"\ddot ", "̈": r"\ddot ",
                      "̃": r"\tilde ", "⃗": r"\vec ", "̆": r"\breve ",
                      "̀": r"\grave ", "̌": r"\check ", "̑": r"\widehat "}
            cmd = accmap.get(ch, r"\hat ")
            wide = {"⃗": r"\overrightarrow "}.get(ch)
            if wide:
                return rf"{wide} {{{e}}}"
            return rf"{cmd}{{{e}}}"
        if tag == _q("bar"):
            pr = _first_child(el, "barPr")
            pos = "top"
            if pr is not None:
                p = pr.find(_q("pos"))
                if p is not None:
                    pos = p.get(M + "val", "top")
            e = self._of(el, "e")
            return rf"\overline {{{e}}}" if pos == "top" else rf"\underline {{{e}}}"
        if tag == _q("m"):
            return self._matrix(el)
        if tag == _q("eqArr"):
            rows = [self._el(c) for c in list(el) if c.tag == _q("e")]
            body = r" \\ ".join(r for r in rows if r.strip())
            return rf"\begin {{gathered}} {body} \end {{gathered}}"
        if tag in (_q("box"), _q("groupChr"), _q("borderBox"), _q("sPre")):
            if tag == _q("groupChr"):
                pr = _first_child(el, "groupChrPr")
                ch = None
                if pr is not None:
                    c = pr.find(_q("chr"))
                    if c is not None:
                        ch = c.get(M + "val")
                e = self._of(el, "e")
                if ch == "⏞":
                    return rf"\overbrace {{{e}}}"
                if ch == "⏟":
                    return rf"\underbrace {{{e}}}"
                return e
            if tag == _q("sPre"):
                sub = self._of(el, "sub")
                sup = self._of(el, "sup")
                e = self._of(el, "e")
                return f"{{}}_{{{sub}}}^{{{sup}}}{{{e}}}"
            inner = []
            for c in el:
                if c.tag in (_q("boxPr"), _q("groupChrPr"), _q("borderBoxPr")):
                    continue
                inner.append(self._el(c))
            return "".join(inner)
        if tag == _q("phant"):
            e = self._of(el, "e")
            return rf"\phantom {{{e}}}"
        if tag == _q("e"):
            return "".join(self._el(c) for c in el)
        # containers / unknown: recurse
        parts = []
        for c in el:
            parts.append(self._el(c))
        return "".join(parts)

    def _run(self, el) -> str:
        parts = []
        pr = el.find(_q("rPr"))
        style = ""
        if pr is not None:
            sty = pr.find(_q("sty"))
            if sty is not None:
                style = sty.get(M + "val", "")
        txt = _txt(el)
        body = _esc_text(txt)
        if style in ("b", "bi"):
            body = rf"\mathbf {{{body}}}"
        elif style == "p":
            body = rf"\mathrm {{{body}}}"
        return body

    def _of(self, el, tag) -> str:
        child = el.find(_q(tag))
        if child is None:
            return ""
        return "".join(self._el(c) for c in child)

    def _delim(self, el) -> str:
        pr = _first_child(el, "dPr")
        beg, end, sep = "(", ")", "|"
        if pr is not None:
            b = pr.find(_q("begChr"))
            e_ = pr.find(_q("endChr"))
            s = pr.find(_q("sepChr"))
            if b is not None:
                beg = b.get(M + "val", "(")
            if e_ is not None:
                end = e_.get(M + "val", ")")
            if s is not None:
                sep = s.get(M + "val", "|")
        inner = []
        for i, e_child in enumerate(_children(el, "e")):
            if i > 0:
                inner.append(rf"\middle {sep} " if sep not in (".", "") else r"\middle| ")
            inner.append(self._el(e_child))
        body = "".join(inner)

        def wall(ch):
            if ch == "{":
                return r"\{"
            if ch == "}":
                return r"\}"
            if ch == "|":
                return "|"
            if ch == ".":
                return "."
            if ch == "<":
                return "<"
            if ch == ">":
                return ">"
            if ch == "[":
                return "["
            if ch == "]":
                return "]"
            if ch == "|":
                return r"\|"
            return ch

        bl, el_ = wall(beg), wall(end)
        if beg == "." :
            return rf"\right. {{{body}}}\right {el_}" if False else rf"\left. {{{body}}}\right {el_}"
        if end == ".":
            return rf"\left {bl} {{{body}}}\right."
        return rf"\left {bl} {{{body}}}\right {el_}"

    def _nary(self, el) -> str:
        pr = _first_child(el, "naryPr")
        chr_ = "∫"
        subhide = suphide = False
        if pr is not None:
            c = pr.find(_q("chr"))
            if c is not None:
                chr_ = c.get(M + "val", "∫")
            sh = pr.find(_q("subHide"))
            if sh is not None and sh.get(M + "val") in ("1", "on", "true"):
                subhide = True
            ph = pr.find(_q("supHide"))
            if ph is not None and ph.get(M + "val") in ("1", "on", "true"):
                suphide = True
        op = _NARY.get(chr_, r"\int ")
        sub = self._of(el, "sub")
        sup = self._of(el, "e" if False else "sup")
        e = self._of(el, "e")
        out = op
        if not subhide and sub.strip():
            out += f"_{{{sub}}} "
        if not suphide and sup.strip():
            out += f"^{{{sup}}} "
        return out + e

    def _matrix(self, el) -> str:
        pr = _first_child(el, "mPr")
        cspan = ""
        if pr is not None:
            mc = pr.find(_q("mcs"))
            if mc is not None:
                cspan = _txt(mc)
        rows = []
        for mr in _children(el, "mr"):
            cells = [self._el(c) for c in _children(mr, "e")]
            rows.append(" & ".join(cells))
        body = r" \\ ".join(rows)
        return rf"\begin {{matrix}} {body} \end {{matrix}}"


def _tidy(s: str) -> str:
    s = re.sub(r"\s+", " ", s)
    s = s.replace("{ }", "{}")
    # collapse like  \frac { a } { b }  -> \frac{a}{b}? keep readable spacing
    s = re.sub(r"\s+", " ", s).strip()
    return s


def convert_omml_element(omath) -> tuple[str, list[str]]:
    conv = Converter()
    return conv.convert(omath), conv.warnings


def omath_para_is_display(omathpara) -> bool:
    return True
