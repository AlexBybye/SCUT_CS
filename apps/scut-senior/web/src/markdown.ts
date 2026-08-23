import DOMPurify from "dompurify";
import katex from "katex";
// 样式与 JS 同块：本模块只经异步加载的 WorkflowResult 到达，KaTeX CSS 因此
// 随数学渲染块按需注入，不再从应用入口全局加载（迭代 7.5 路由级拆包）。
import "katex/dist/katex.min.css";
import { marked } from "marked";

type MathFragment = {
  placeholder: string;
  html: string;
};

const MATRIX_ENVIRONMENT_RE = /\\begin\{(matrix|pmatrix|bmatrix|Bmatrix|vmatrix|Vmatrix|smallmatrix)\}([\s\S]*?)\\end\{\1\}/g;
const BARE_BRACKET_BLOCK_RE = /(^|\n)\[\s*\n?([\s\S]*?)\n?\](?=\n|$)/g;
const BARE_INLINE_LATEX_RE = /\(([^()\r\n]*\\(?:operatorname|leftarrow|rightarrow|to|mapsto|frac|sqrt|sum|prod|int|cdot|times|leq|geq|neq)[^()\r\n]*(?:\([^()\r\n]*\)[^()\r\n]*)*)\)/g;
// A deliberately narrow recovery for prose such as “交换 (R_2) 与 (R_{3})”。
// It does not try to parse arbitrary parenthesized text, which would risk
// treating normal Markdown prose as TeX.
const BARE_SUBSCRIPTED_SYMBOL_RE = /\(([A-Z]_(?:\{[A-Za-z0-9]+\}|[A-Za-z0-9]))\)/g;

function repairMatrixRows(formula: string): string {
  return formula.replace(
    MATRIX_ENVIRONMENT_RE,
    (_match, environment: string, rows: string) => (
      `\\begin{${environment}}${rows.replace(
        /(^|[^\\])\\(?=\r?\n)/g,
        (_rowMatch, prefix: string) => `${prefix}\\\\`,
      )}\\end{${environment}}`
    ),
  );
}

function isMatrixFormula(formula: string): boolean {
  return /\\begin\{(?:matrix|pmatrix|bmatrix|Bmatrix|vmatrix|Vmatrix|smallmatrix)\}/.test(formula)
    && /\\end\{(?:matrix|pmatrix|bmatrix|Bmatrix|vmatrix|Vmatrix|smallmatrix)\}/.test(formula);
}

function renderMath(source: string, displayMode: boolean): string {
  try {
    return katex.renderToString(repairMatrixRows(source).trim(), {
      displayMode,
      throwOnError: false,
      strict: "ignore",
    });
  } catch {
    return source;
  }
}

/** Render model text as safe Markdown, including $...$ and $$...$$ LaTeX. */
export function renderAnswerMarkdown(source: string): string {
  const fragments: MathFragment[] = [];
  const saveMath = (formula: string, displayMode: boolean): string => {
    const placeholder = `SCUTMATHPLACEHOLDER${fragments.length}END`;
    fragments.push({ placeholder, html: renderMath(formula, displayMode) });
    return placeholder;
  };
  const blockMath = (formula: string): string => (
    `\n\n${saveMath(formula, true)}\n\n`
  );

  // Providers frequently emit TeX delimiters (\\[...\\], \\(...\\)) rather
  // than Markdown dollars. Handle those before marked treats the leading
  // backslashes as escapes. The bracket fallback is deliberately restricted
  // to matrix environments so ordinary Markdown links/references stay intact.
  const withMathPlaceholders = source
    .replace(/\$\$([\s\S]+?)\$\$/g, (_match, formula: string) => blockMath(formula))
    .replace(/\\\[([\s\S]+?)\\\]/g, (_match, formula: string) => blockMath(formula))
    .replace(/\\\(([\s\S]+?)\\\)/g, (_match, formula: string) => saveMath(formula, false))
    .replace(BARE_BRACKET_BLOCK_RE, (match, prefix: string, formula: string) => (
      isMatrixFormula(formula) ? `${prefix}${blockMath(formula)}` : match
    ))
    .replace(BARE_INLINE_LATEX_RE, (_match, formula: string) => saveMath(formula, false))
    .replace(BARE_SUBSCRIPTED_SYMBOL_RE, (_match, formula: string) => saveMath(formula, false))
    .replace(/(^|[^\\$])\$([^$\n]+?)\$/g, (_match, prefix: string, formula: string) => (
      `${prefix}${saveMath(formula, false)}`
    ));
  let html = marked.parse(withMathPlaceholders, { breaks: true, gfm: true }) as string;
  for (const fragment of fragments) {
    html = html.split(fragment.placeholder).join(fragment.html);
  }
  // DOMPurify is browser-bound. Vitest's SSR renderer has no DOM, while the
  // shipped Vite app always sanitizes before assigning v-html.
  if (typeof DOMPurify.sanitize !== "function") return html;
  return DOMPurify.sanitize(html, {
    // KaTeX uses SVG paths for stretchy matrix delimiters and MathML as an
    // accessibility fallback. The default HTML-only profile removes both.
    USE_PROFILES: { html: true, svg: true, mathMl: true },
  });
}
