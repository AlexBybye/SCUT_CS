"""迭代 7（SOP §12）贡献流程的确定性规则。

本模块只包含纯函数与常量：转换预览、状态机迁移和 PR 链接校验。
不做任何 I/O、不调用模型、不修改原始资料；真正的 PR 创建属于
GitHub App 决策门之后的自动链路，当前迭代一律进入维护者待处理队列。
"""

from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit

from .contracts import ContributionState, ContributionPreview

# 普通临时材料 7 天 TTL；贡献待审副本最长 30 天（SOP §3.4 / §12.3）。
TEMPORARY_MATERIAL_TTL_DAYS = 7
CONTRIBUTION_REVIEW_COPY_TTL_DAYS = 30

# 状态机：draft 只能提交；submitted/pr_open 可被维护者推进或拒绝；
# merged/rejected/expired 是终态。合并永远只能由人工在仓库侧完成，
# 应用内没有任何“自动合并”路径。
_CONTRIBUTION_TRANSITIONS: dict[ContributionState, frozenset[ContributionState]] = {
    ContributionState.DRAFT: frozenset({ContributionState.SUBMITTED}),
    ContributionState.SUBMITTED: frozenset(
        {ContributionState.PR_OPEN, ContributionState.REJECTED}
    ),
    ContributionState.PR_OPEN: frozenset(
        {ContributionState.MERGED, ContributionState.REJECTED}
    ),
    ContributionState.MERGED: frozenset(),
    ContributionState.REJECTED: frozenset(),
    ContributionState.EXPIRED: frozenset(),
}

# 维护者动作 → 目标状态。merge 只能从 pr_open 进入：
# 没有 PR 就没有可合并对象，待处理队列本身永远不会“被合并”。
# “submit”是用户把自己的 draft 推进到 submitted 的动作，不属于维护者动作集。
_ACTION_TARGET: dict[str, ContributionState] = {
    "submit": ContributionState.SUBMITTED,
    "mark_pr_open": ContributionState.PR_OPEN,
    "merge": ContributionState.MERGED,
    "reject": ContributionState.REJECTED,
}

_GITHUB_PR_URL_RE = re.compile(r"^/[^/\s]+/[^/\s]+/pull/[1-9][0-9]*$")

_QUESTION_MARKER_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:question|题目?)[ \t]*\d*[::]",
    re.MULTILINE | re.IGNORECASE,
)

_HTML_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")

MIN_CONTRIBUTION_CHARS = 50


class ContributionTransitionError(ValueError):
    """状态机拒绝该迁移时抛出；由 API 层映射为 409。"""


def next_contribution_states(state: ContributionState) -> frozenset[ContributionState]:
    return _CONTRIBUTION_TRANSITIONS[state]


def states_allowed_for_target(target: ContributionState) -> frozenset[ContributionState]:
    """反向查询：允许迁移到 target 的全部来源状态。"""

    return frozenset(
        source
        for source, targets in _CONTRIBUTION_TRANSITIONS.items()
        if target in targets
    )


def resolve_transition_target(action: str) -> ContributionState:
    target = _ACTION_TARGET.get(action)
    if target is None:
        raise ContributionTransitionError(f"unknown maintainer action: {action}")
    return target


def validate_contribution_transition(
    current: ContributionState,
    *,
    action: str,
) -> ContributionState:
    target = resolve_transition_target(action)
    if target not in _CONTRIBUTION_TRANSITIONS[current]:
        raise ContributionTransitionError(
            f"cannot transition contribution from {current.value} "
            f"to {target.value}"
        )
    return target


def validate_github_pr_url(raw_url: str) -> str:
    """只接受 github.com 上的固定 PR 链接形态，不接受任意地址。"""

    parsed = urlsplit(raw_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "github.com"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port is not None
        or bool(parsed.fragment)
        or bool(parsed.query)
        or not _GITHUB_PR_URL_RE.fullmatch(parsed.path or "")
    ):
        raise ContributionTransitionError(
            "pr_url must be a https://github.com/<owner>/<repo>/pull/<number> link"
        )
    return raw_url


def normalize_contribution_markdown(content: str) -> str:
    """确定性 Markdown 规范化：换行统一、行尾空白、压缩空行、单一结尾换行。

    不改写正文内容本身：不动公式、不动标题文字、不增删段落语义。
    """

    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


def derive_proposed_source_id(course_id: str, normalized_content: str) -> str:
    """提议来源 ID：由课程与内容哈希确定，最终编号仍由人工审核阶段分配。"""

    digest = hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()[:8]
    return f"{course_id}-contribution-{digest}"


_FILENAME_FORBIDDEN_RE = re.compile(r'[/\\:*?\"<>|\x00-\x1f]')
_MARKDOWN_HINT_RE = re.compile(
    r"(^#{1,6}\s+\S)|(^[-*]\s+\S)|(```)|(\[[^\]]+\]\([^)]+\))",
    re.MULTILINE,
)


def derive_contribution_filename(title: str | None, content: str) -> str:
    """从标题推导安全的仓库文件名；正文只用于嗅探扩展名。"""

    import unicodedata

    normalized_title = unicodedata.normalize("NFKC", (title or "").strip())
    cleaned = _FILENAME_FORBIDDEN_RE.sub("-", normalized_title)
    cleaned = re.sub(r"\s+", "-", cleaned)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-.")
    if not cleaned:
        cleaned = "contribution"
    stem = cleaned[:80].rstrip("-.")
    extension = ".md" if _MARKDOWN_HINT_RE.search(content) else ".txt"
    return f"{stem}{extension}"


def derive_proposed_repo_path(
    repository_paths: tuple[str, ...],
    *,
    course_id: str,
    title: str | None,
    content: str,
) -> str:
    """贡献落点：当前会话课程在学科资料下对应的目录（add file 语义）。

    优先使用课程注册表 repository_paths 的第一项；未登记路径的课程退到
    “学科资料/_待归类/<course_id>/”，避免把文件误放进错误学科。
    """

    base = (
        repository_paths[0] if repository_paths else f"学科资料/_待归类/{course_id}"
    )
    base = base.rstrip("/")
    return f"{base}/{derive_contribution_filename(title, content)}"


def build_contribution_preview(
    *,
    course_id: str,
    title: str | None,
    content: str,
) -> ContributionPreview:
    normalized = normalize_contribution_markdown(content)
    h1_match = re.search(r"^#\s+(\S.*)$", normalized, re.MULTILINE)
    has_h1_title = h1_match is not None
    effective_title = (title or "").strip()
    warnings: list[str] = []
    if not has_h1_title and not effective_title:
        warnings.append("材料缺少一级标题且未提供标题：审核时将无法回查资料名。")
    question_marker_count = len(_QUESTION_MARKER_RE.findall(normalized))
    if question_marker_count == 0:
        warnings.append("未检测到题目标记：如为试卷类资料，请确认题目边界供人工复核。")
    if len(normalized.strip()) < MIN_CONTRIBUTION_CHARS:
        warnings.append("材料过短：贡献应提供可直接人工审核的完整内容。")
    if _HTML_TAG_RE.search(normalized):
        warnings.append("检测到 HTML 标签：请确认为有意保留的标记而非粘贴残留。")
    return ContributionPreview(
        course_id=course_id,
        proposed_source_id=derive_proposed_source_id(course_id, normalized),
        normalized_content=normalized,
        has_h1_title=has_h1_title,
        question_marker_count=question_marker_count,
        warnings=warnings,
    )
