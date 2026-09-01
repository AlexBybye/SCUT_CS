import { describe, expect, it } from "vitest";
import { formatWorkflowOutputForCopy } from "../workflowOutputCopy";

describe("formatWorkflowOutputForCopy", () => {
  it("copies readable answer blocks and citation labels only", () => {
    const text = formatWorkflowOutputForCopy(
      [
        { type: "repository", content: "  有证据的课程结论。  " },
        { type: "general", content: "通用补充。" },
      ],
      [
        {
          citation_id: "S1",
          source_id: "source-1",
          chunk_id: "chunk-1",
          source_title: "矩阵讲义",
          course_id: "linear_algebra",
          course_title: "线性代数",
          locator_type: "page",
          locator_start: "12",
          locator_end: null,
        },
      ],
    );

    expect(text).toBe(
      "课程资料回答\n\n有证据的课程结论。\n\n通用知识补充\n\n通用补充。\n\n引用来源\n\n- 线性代数：《矩阵讲义》（12）",
    );
    expect(text).not.toContain("S1");
    expect(text).not.toContain("source-1");
  });

  it("returns empty text when no readable output exists", () => {
    expect(formatWorkflowOutputForCopy([{ type: "repository", content: "   " }], [])).toBe("");
  });
});
