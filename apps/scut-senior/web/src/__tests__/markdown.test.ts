// @vitest-environment jsdom

import { describe, expect, it } from "vitest";

import { renderAnswerMarkdown } from "../markdown";

describe("renderAnswerMarkdown", () => {
  it("renders Markdown and display LaTeX instead of showing their source", () => {
    const html = renderAnswerMarkdown("## 结论\n\n$$x^2 + y^2 = 1$$");

    expect(html).toContain("<h2>结论</h2>");
    expect(html).toContain("katex-display");
    expect(html).not.toContain("$$x^2 + y^2 = 1$$");
  });

  it("normalizes the model's bare matrix block and row-operation TeX", () => {
    const source = [
      "示例：",
      "[",
      "A=\\begin{pmatrix}",
      "1&2&3\\",
      "2&4&6\\",
      "1&1&1",
      "\\end{pmatrix}",
      "]",
      "",
      "(R_2 \\leftarrow R_2-2R_1)",
      "(\\operatorname{rank}(A)=2)",
    ].join("\n");

    const html = renderAnswerMarkdown(source);

    expect(html.match(/katex-display/g)).toHaveLength(1);
    expect(html.match(/class=\"katex\"/g)).toHaveLength(3);
    expect(html.match(/<mtr>/g)).toHaveLength(3);
    expect(html).not.toContain("<p>[<br>");
    expect(html).not.toContain("<p>(R_2");
  });

  it("handles conventional TeX delimiters before Markdown consumes them", () => {
    const html = renderAnswerMarkdown(
      "\\[x^2+y^2=1\\]，并且 \\(x=y+1\\) 。",
    );

    expect(html).toContain("katex-display");
    expect(html.match(/class=\"katex\"/g)).toHaveLength(2);
    expect(html).not.toContain("\\[x^2+y^2=1\\]");
  });

  it("recovers only bare parenthesized matrix row symbols with subscripts", () => {
    const html = renderAnswerMarkdown("交换 (R_2) 与 (R_{3}) 后继续消元。");

    expect(html.match(/class=\"katex\"/g)).toHaveLength(2);
    expect(html).not.toContain("<p>交换 (R_2)");
    expect(renderAnswerMarkdown("普通说明（第 2 步）")).not.toContain("katex");
  });

  it("does not mistake ordinary Markdown links for formulas", () => {
    const html = renderAnswerMarkdown("[课程主页](https://example.test/course)");

    expect(html).toContain('<a href="https://example.test/course">课程主页</a>');
    expect(html).not.toContain("katex");
  });

  it("keeps KaTeX matrix SVG while sanitizing untrusted Markdown", () => {
    const source = [
      "[",
      "A=\\begin{pmatrix}",
      "1&2&3\\",
      "2&4&6\\",
      "1&1&1",
      "\\end{pmatrix}",
      "]",
      '<img src="x" onerror="alert(1)"><script>alert(1)</script>',
    ].join("\n");

    const html = renderAnswerMarkdown(source);

    expect(html).toContain("<svg");
    expect(html).toContain("<path");
    expect(html).not.toContain("<script");
    expect(html).not.toContain("onerror=");
  });
});
