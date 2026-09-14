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
from scut_senior_api.workflow_focus import (
    build_response_control_directive,
    build_tone_visible_callout,
)


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


@pytest.mark.parametrize("tone", list(Tone))
def test_persona_callout_is_masked_and_shared_voice_reaches_both_prompts(tone: Tone) -> None:
    request = WorkflowRunRequest.model_validate({**_request_payload(), "tone": tone})
    generation = build_response_control_directive(request)
    rewrite = compose_persona_humanizer_prompt(tone)
    from scut_senior_api.persona_style import PERSONA_PROFILES

    assert PERSONA_PROFILES[tone] in generation
    assert PERSONA_PROFILES[tone] in rewrite
    callout = build_tone_visible_callout(tone)
    blocks = [AnswerBlock(type=AnswerBlockType.GENERAL, content=f"解释正文。\n\n{callout}")]
    prepared = prepare_humanizer_input(blocks, ())
    assert callout not in prepared.blocks[0].content
    assert prepared.restore(list(prepared.blocks)) == blocks


@pytest.mark.parametrize("banter", [
    "杂鱼学长，思路还在门口罚站呢？咱们把线索理清楚。",
    "哥们，你这脑子开省电模式了？咱们给思路接上电。",
    "脑子到岗。气势收好，依据摆齐。",
])
def test_persona_banter_can_replace_neutral_transition_without_losing_evidence(banter: str) -> None:
    knowledge = "矩阵的秩为 3，计算见 $A^3=I$，参考 [S1]。"
    original = [AnswerBlock(type=AnswerBlockType.REPOSITORY, content=f"接下来整理思路。\n\n{knowledge}")]
    candidate = [AnswerBlock(type=AnswerBlockType.REPOSITORY, content=f"{banter}\n\n{knowledge}")]
    outcome = protect_humanizer_output(original=original, candidate=candidate, protected_terms=("矩阵",))
    assert outcome.applied
    changed_fact = [candidate[0].model_copy(update={"content": candidate[0].content.replace("为 3", "为 4")})]
    assert protect_humanizer_output(original=original, candidate=changed_fact, protected_terms=("矩阵",)).fallback
