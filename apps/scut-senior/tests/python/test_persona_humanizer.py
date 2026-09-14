from __future__ import annotations

import pytest

from scut_senior_api.contracts import (
    AnswerBlock,
    AnswerBlockType,
    Tone,
    WorkflowRunRequest,
)
from scut_senior_api.persona_humanizer import (
    compose_persona_humanizer_prompt,
    prepare_humanizer_input,
)
from scut_senior_api.runtime_guards import protect_humanizer_output


def _request_payload() -> dict[str, object]:
    return {
        "workflow_type": "knowledge_qa",
        "course_scope": "single",
        "course_id": "linear_algebra",
        "allowed_course_ids": [],
        "conversation_id": "11111111-1111-1111-1111-111111111111",
        "model_source": "platform_default",
        "provider_id": "mock",
        "model_id": "deterministic-fixture-v1",
        "user_input": "解释矩阵的秩",
        "answer_mode": "detailed",
        "tone": "senior_student",
        "knowledge_scope": "course_first",
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {"question": "解释矩阵的秩"},
    }


def test_old_request_defaults_to_single_pass() -> None:
    request = WorkflowRunRequest.model_validate(_request_payload())
    assert request.persona_enhancement.value == "standard"


def test_persona_prompt_combines_shared_contract_and_overlay() -> None:
    prompt = compose_persona_humanizer_prompt(Tone.SENIOR_STUDENT)
    assert "不摘要、不扩写" in prompt
    assert "当前人格：学长" in prompt
    assert "1～3 句" in prompt


def test_placeholders_round_trip_protected_content() -> None:
    original = [
        AnswerBlock(
            type=AnswerBlockType.REPOSITORY,
            content="矩阵秩为 3，公式 $A^3=I$，见 [S1]。",
        )
    ]
    prepared = prepare_humanizer_input(original, ("矩阵秩",))
    masked = prepared.blocks[0].content
    assert "矩阵秩" not in masked
    assert "$A^3=I$" not in masked
    assert "[S1]" not in masked
    assert prepared.restore(list(prepared.blocks)) == original


def test_placeholder_mutation_fails_closed() -> None:
    original = [AnswerBlock(type=AnswerBlockType.GENERAL, content="矩阵秩为 3。")]
    prepared = prepare_humanizer_input(original, ("矩阵秩",))
    candidate = [
        prepared.blocks[0].model_copy(
            update={"content": prepared.blocks[0].content.replace("0001", "9999")}
        )
    ]
    with pytest.raises(ValueError, match="placeholder_changed"):
        prepared.restore(candidate)


def test_low_risk_chinese_rewrite_is_applied() -> None:
    original = [
        AnswerBlock(
            type=AnswerBlockType.GENERAL,
            content="这个地方的表达比较绕，接下来我们把思路整理清楚。",
        )
    ]
    candidate = [
        AnswerBlock(
            type=AnswerBlockType.GENERAL,
            content="这里说得有点绕，我们接着把思路理清楚。",
        )
    ]
    outcome = protect_humanizer_output(
        original=original,
        candidate=candidate,
        protected_terms=(),
    )
    assert outcome.applied is True
    assert outcome.fallback is False
    assert list(outcome.blocks) == candidate
