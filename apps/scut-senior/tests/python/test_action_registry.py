from scut_senior_api.action_registry import ACTION_REGISTRY, ActionPolicy, ActionRegistry
from scut_senior_api.agent_loop import parse_model_action


def test_registry_is_the_phase_and_workflow_source_of_truth():
    assert ACTION_REGISTRY.allowed_actions("knowledge_qa", "post_retrieval") == (
        "retrieve_with_query_rewrite", "generate_answer"
    )
    assert ACTION_REGISTRY.allowed_actions("temporary_material_reading", "post_retrieval") == (
        "generate_answer",
    )
    assert not ACTION_REGISTRY.admits("knowledge_qa", "retrieve", "post_retrieval")
    assert not ACTION_REGISTRY.admits("unknown", "generate_answer", "generate")


def test_historical_actions_have_no_executor_admission():
    assert "finish" in ACTION_REGISTRY.action_kinds
    assert not ACTION_REGISTRY.admits("knowledge_qa", "finish")
    assert parse_model_action("finish", workflow_type="knowledge_qa", phase="post_retrieval") is None


def test_model_parser_fails_closed_on_phase_or_prose():
    assert parse_model_action("generate_answer", workflow_type="knowledge_qa", phase="post_retrieval") == "generate_answer"
    assert not ACTION_REGISTRY.admits("knowledge_qa", "retrieve", "post_retrieval")
    assert parse_model_action("I choose generate_answer", workflow_type="knowledge_qa", phase="post_retrieval") is None


def test_registry_rejects_duplicate_names():
    try:
        ActionRegistry((ActionPolicy("retrieve", frozenset(), frozenset()),
                        ActionPolicy("retrieve", frozenset(), frozenset())))
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate action must fail closed")
