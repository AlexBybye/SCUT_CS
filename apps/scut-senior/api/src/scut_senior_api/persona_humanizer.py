from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import AnswerBlock, Tone


_TOKEN_PREFIX = "[[SCUT_PROTECTED_"
_PROTECTED_RE = re.compile(
    r"```[\s\S]*?```|`[^`]+`|\$\$[\s\S]*?\$\$|\$[^$\n]+\$|"
    r"\\\([^\n]+?\\\)|\\\[[\s\S]+?\\\]|"
    r"\\begin\{[^{}]+\}[\s\S]*?\\end\{[^{}]+\}|"
    r"(?:\[|【)S\d+(?:\]|】)|"
    r"https?://[^\s<>)]+|(?<![\w])www\.[^\s<>)]+|"
    r"(?<=\]\()[^)]+(?=\))|"
    r"(?<![A-Za-z0-9_])[-+]?(?:\d+(?:\.\d+)?|\.\d+)"
    r"(?:[eE][-+]?\d+)?(?:%|[a-zA-Z\u4e00-\u9fff]+)?"
)

_CORE = """你只负责忠实润色下方中文回答。
- 不摘要、不扩写、不补充知识、不做事实核查，不改变结论和不确定程度。
- 保持 Markdown 标题、列表、段落、代码、公式和占位符的原有结构与顺序。
- 所有 [[SCUT_PROTECTED_*]] 占位符必须逐字保留，数量和顺序不得变化。
- 已经自然的内容少改或不改，只输出润色后的回答块。"""

_OVERLAYS: dict[Tone, str] = {
    Tone.STUDY_PARTNER: """当前人格：学妹（复习搭子）。
保留轻快、陪伴、鼓励和适度督促；语气词自然分布，不要句句卖萌。
人格话术总量控制在 1～3 句，可以自然加入一次“杂鱼”式吐槽。
不得删推导步骤，不在公式、定义或引用附近堆语气词。""",
    Tone.SENIOR_STUDENT: """当前人格：学长。
像熟悉课程的过来人顺着主线讲，使用自然口语并指出常见坑。
删去机械重复的“学长提醒”等模板话术，人格话术总量控制在 1～3 句。
每段保留定义、判断条件、检查点或下一步，不省略严谨条件。""",
    Tone.TEACHING_ASSISTANT: """当前人格：助教。
保持严格、直接、依据优先，按定义、前提、符号、结论的顺序表达。
缩短冗长句和重复解释；人格话术总量控制在 1～3 句。
吐槽针对错误步骤，也可以针对学生人格或能力，公式推导中不插话。""",
}


def compose_persona_humanizer_prompt(tone: Tone) -> str:
    return f"{_CORE}\n\n{_OVERLAYS[tone]}"


@dataclass(frozen=True, slots=True)
class PreparedHumanizerInput:
    blocks: tuple[AnswerBlock, ...]
    replacements: tuple[tuple[tuple[str, str], ...], ...]

    def restore(self, candidate: list[AnswerBlock]) -> list[AnswerBlock]:
        if len(candidate) != len(self.blocks):
            raise ValueError("block_count_changed")
        restored: list[AnswerBlock] = []
        for expected, current, replacements in zip(
            self.blocks, candidate, self.replacements, strict=True
        ):
            if expected.type != current.type:
                raise ValueError("block_type_changed")
            content = current.content
            actual_tokens = re.findall(r"\[\[SCUT_PROTECTED_\d{4}\]\]", content)
            expected_tokens = [token for token, _ in replacements]
            if actual_tokens != expected_tokens or any(
                content.count(token) != 1 for token in expected_tokens
            ):
                raise ValueError("placeholder_changed")
            for token, original in replacements:
                content = content.replace(token, original)
            if _TOKEN_PREFIX in content:
                raise ValueError("placeholder_added")
            restored.append(current.model_copy(update={"content": content}))
        return restored


def prepare_humanizer_input(
    blocks: list[AnswerBlock], protected_terms: tuple[str, ...]
) -> PreparedHumanizerInput:
    prepared: list[AnswerBlock] = []
    all_replacements: list[tuple[tuple[str, str], ...]] = []
    token_index = 0
    for block in blocks:
        if _TOKEN_PREFIX in block.content:
            raise ValueError("reserved_placeholder_in_input")
        spans = [(match.start(), match.end()) for match in _PROTECTED_RE.finditer(block.content)]
        for term in sorted((term for term in protected_terms if term), key=len, reverse=True):
            spans.extend((match.start(), match.end()) for match in re.finditer(re.escape(term), block.content))
        merged: list[tuple[int, int]] = []
        for start, end in sorted(spans):
            if merged and start < merged[-1][1]:
                if end > merged[-1][1]:
                    merged[-1] = (merged[-1][0], end)
                continue
            merged.append((start, end))

        content = block.content
        replacements: list[tuple[str, str]] = []
        for start, end in reversed(merged):
            token_index += 1
            token = f"{_TOKEN_PREFIX}{token_index:04d}]]"
            original = content[start:end]
            replacements.insert(0, (token, original))
            content = content[:start] + token + content[end:]
        prepared.append(block.model_copy(update={"content": content}))
        all_replacements.append(tuple(replacements))
    return PreparedHumanizerInput(tuple(prepared), tuple(all_replacements))


def has_humanizable_chinese(blocks: tuple[AnswerBlock, ...]) -> bool:
    text = "\n".join(block.content for block in blocks)
    chinese_count = len(re.findall(r"[\u3400-\u9fff]", text))
    protected_count = len(re.findall(r"\[\[SCUT_PROTECTED_\d{4}\]\]", text))
    return chinese_count >= 20 and chinese_count >= protected_count * 2
