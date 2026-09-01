import type { AnswerBlock, AnswerBlockType, Citation } from "./contracts";

const blockLabels: Record<AnswerBlockType, string> = {
  repository: "课程资料回答",
  user_material: "用户材料",
  general: "通用知识补充",
  personalized_analysis: "个性化分析",
};

/** Build the readable, user-facing portion of one completed workflow output. */
export function formatWorkflowOutputForCopy(
  answerBlocks: AnswerBlock[],
  citations: Citation[],
): string {
  const sections = answerBlocks
    .filter((block) => block.content.trim())
    .map((block) => `${blockLabels[block.type]}\n\n${block.content.trim()}`);
  if (!sections.length) return "";

  const sources = citations.map((citation) => {
    const locator = citation.locator_start ? `（${citation.locator_start}）` : "";
    return `- ${citation.course_title}：《${citation.source_title}》${locator}`;
  });
  if (sources.length) sections.push(`引用来源\n\n${sources.join("\n")}`);
  return sections.join("\n\n");
}

export async function copyWorkflowOutput(text: string): Promise<void> {
  if (!text.trim()) throw new Error("本次没有可复制的回答内容。");
  if (!navigator.clipboard?.writeText) {
    throw new Error("当前浏览器不支持直接复制，请手动选择回答文本。 ");
  }
  await navigator.clipboard.writeText(text);
}
