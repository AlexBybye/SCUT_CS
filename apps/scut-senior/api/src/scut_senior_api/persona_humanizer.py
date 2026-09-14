from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import AnswerBlock, Tone
from .persona_style import PERSONA_PLAY_RULES, PERSONA_PROFILES


_TOKEN_PREFIX = "[[SCUT_PROTECTED_"
_PROTECTED_RE = re.compile(
    r"(?m:^[ \t]*>[ \t]*\*\*(?:助教提示|学长提醒|复习搭子提醒)：\*\*[^\n]*)|"
    r"```[\s\S]*?```|`[^`]+`|\$\$[\s\S]*?\$\$|\$[^$\n]+\$|"
    r"\\\([^\n]+?\\\)|\\\[[\s\S]+?\\\]|"
    r"\\begin\{[^{}]+\}[\s\S]*?\\end\{[^{}]+\}|"
    r"(?:\[|【)S\d+(?:\]|】)|"
    r"https?://[^\s<>)]+|(?<![\w])www\.[^\s<>)]+|"
    r"(?<=\]\()[^)]+(?=\))|"
    r"(?<![A-Za-z0-9_])[-+]?(?:\d+(?:\.\d+)?|\.\d+)"
    r"(?:[eE][-+]?\d+)?(?:%|[a-zA-Z\u4e00-\u9fff]+)?"
)

_CORE = """【humanizer-zh 忠实润色内核】
你负责保留知识内容，并按当前人格润色下方中文回答。
- 按整段语境调整不自然的从句顺序、重复主语、名词化和空泛套语，不机械替换词语，不抹平作者声音。
- 原文的主张、归因、立场、条件、例外、因果关系和引文归属全部保留；若自然表达会改变含义，保留原表达。
- 知识正文不摘要、不扩写、不补充知识、不做事实核查，不改变结论和不确定程度。
- 用户允许鲜明、跳脱和损人的角色表达：保留原文的挖苦与挑衅，可以替换僵硬的性格话术，不要把它们洗成中性客服语气。已有角色感时少改，角色感弱时优先重写连接句，避免额外追加一轮吐槽。
- 不能为了角色效果新增个人经历、课程轶事、用户行为、成绩或来源。仅看得到当前回答时，不能从例句推断用户做错题、跳步或漏条件。
- 必须、应当、可以、可能、否定等词的语义强度保持原样；这些受检查的词即使在玩笑里也不要新增、删减或调换顺序。不新增“别”“不许”“必须”等命令凑角色感。公式、引用、数字和专业术语保持原样。
- 固定的助教提示、学长提醒、复习搭子提醒引用块保持原样，不改写或重复，系统还会统一校准。
- 保持 Markdown 标题、列表、段落、代码、公式和占位符的原有结构与顺序。
- 所有 [[SCUT_PROTECTED_*]] 占位符必须逐字保留，数量和顺序不得变化。
- 已经自然的内容少改或不改，只输出润色后的回答块。"""

_OVERLAYS = PERSONA_PROFILES


def compose_persona_humanizer_prompt(tone: Tone) -> str:
    return f"{_CORE}\n\n{PERSONA_PLAY_RULES}\n\n{_OVERLAYS[tone]}\n\n人格只调整声音，忠实润色与受保护内容规则始终优先。"


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
