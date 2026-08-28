"""Iteration 5 contract tests: deterministic exam-review planning (SOP §10).

Covers the §10.3 必验场景: syllabus-first path priority, the honest
no-syllabus statement, objective statistics traceable to question sources,
the no-prediction boundary, private-input isolation from public course packs
and caches, and the shared Runtime/Trace/Bilibili contracts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from scut_senior_api.adapters.exam_facts import (
    ExamFactsUnavailable,
    FixtureExamFactsProvider,
    LocalCorpusExamFactsProvider,
)
from scut_senior_api.config import Settings
from scut_senior_api.exam_review import (
    ExamCorpusFacts,
    ExamQuestionFact,
    ExamSourceFact,
    build_exam_review_plan,
    compose_retrieval_query,
    render_exam_review_appendix,
)
from scut_senior_api.main import create_app
from scut_senior_api.paths import CONTRACT_ROOT
from scut_senior_worker.corpus_builder import (
    activate_candidate,
    build_candidate,
    set_course_enabled,
)
from scut_senior_worker.corpus_validator import MANIFEST_HEADERS


COURSE_ID = "linear_algebra"


def _facts() -> ExamCorpusFacts:
    return ExamCorpusFacts(
        course_id=COURSE_ID,
        corpus_version="corpus-test",
        course_pack_version="pack-test",
        sources=(
            ExamSourceFact("exam-2013", "2013 期末 A 卷", "past_exam", 2013),
            ExamSourceFact("exam-2023", "2023 期末 A 卷", "past_exam", 2023),
            ExamSourceFact("note-001", "矩阵复习笔记", "note", None),
        ),
        questions=(
            ExamQuestionFact(
                "Q1", "exam-2013", "2013 期末 A 卷", 2013,
                ("2013 期末 A 卷", "一、填空题（每空3分，共15分）", "矩阵的秩"),
                "page", 1, 1,
            ),
            ExamQuestionFact(
                "Q2", "exam-2013", "2013 期末 A 卷", 2013,
                ("2013 期末 A 卷", "二、计算题（10分）"), "page", 2, 2,
            ),
            ExamQuestionFact(
                "Q3", "exam-2023", "2023 期末 A 卷", 2023,
                ("2023 期末 A 卷", "一、填空题（每空2分，共10分）", "矩阵的秩"),
                "page", 1, 1,
            ),
            ExamQuestionFact(
                "Q4", "exam-2023", "2023 期末 A 卷", 2023,
                ("2023 期末 A 卷", "三、"), "page", 3, None,
            ),
        ),
        heading_topics=("矩阵的秩", "初等行变换", "特征值与特征向量"),
    )


def _plan(
    syllabus: str | None,
    weak: list[str] | None = None,
    **kwargs,
):
    return build_exam_review_plan(
        course_id=COURSE_ID,
        payload_syllabus=syllabus,
        payload_weak_topics=weak or [],
        payload_available_hours=kwargs.pop("available_hours", None),
        knowledge_scope_allows_general=kwargs.pop("general", True),
        facts=kwargs.pop("facts", _facts()),
        payload_review_question=kwargs.pop("review_question", None),
    )


# ---------------------------------------------------------------------------
# Path selection and evidence priority (SOP §10.2 / §10.3)
# ---------------------------------------------------------------------------


def test_with_syllabus_path_puts_user_syllabus_first() -> None:
    plan = _plan("矩阵的秩、特征值")

    assert plan.path.value == "with_syllabus"
    assert plan.priority_order[0] == "user_syllabus"
    assert plan.priority_order[1:3] == ("course_material", "past_exam")


def test_without_syllabus_path_puts_past_exam_first_and_disclaims_scope() -> None:
    plan = _plan(None, ["初等行变换"])

    assert plan.path.value == "without_syllabus"
    assert plan.priority_order[0] == "past_exam"
    assert plan.priority_order[1] == "course_material"
    assert "不是官方考试范围" in plan.scope_statement
    assert "不构成考试重点预测" in plan.scope_statement


def test_general_step_only_enters_priority_when_scope_allows() -> None:
    with_general = _plan(None, general=True)
    course_only = _plan(None, general=False)

    assert with_general.priority_order[-1] == "general"
    assert "general" not in course_only.priority_order


def test_retrieval_query_follows_the_selected_path() -> None:
    with_syllabus = _plan("矩阵的秩")
    without_syllabus = _plan(None, ["初等行变换"])
    empty = build_exam_review_plan(
        course_id=COURSE_ID,
        payload_syllabus=None,
        payload_weak_topics=[],
        payload_available_hours=None,
        knowledge_scope_allows_general=True,
        facts=_facts(),
    )

    with_query = compose_retrieval_query(
        syllabus="矩阵的秩", weak_topics=[], plan=with_syllabus
    )
    assert with_query.startswith("矩阵的秩")

    without_query = compose_retrieval_query(
        syllabus=None, weak_topics=["初等行变换"], plan=without_syllabus
    )
    # 薄弱点在前，客观题组主题补充进检索词，保持无大纲路径可检索。
    assert without_query.startswith("初等行变换")
    assert "矩阵的秩" in without_query

    empty_query = compose_retrieval_query(
        syllabus=None, weak_topics=[], plan=empty
    )
    assert empty_query  # past-exam topics keep the no-syllabus path searchable


def test_review_question_leads_the_retrieval_query() -> None:
    plan = _plan(None, ["初等行变换"])

    query = compose_retrieval_query(
        syllabus=None,
        weak_topics=["初等行变换"],
        plan=plan,
        review_question="泊松分布怎么复习？",
    )

    # 复习提问永远排在检索词第一位（NFKC 归一化会把全角问号转半角）。
    assert query.startswith("泊松分布怎么复习?")
    assert "初等行变换" in query


def test_retrieval_query_without_plan_or_facts_stays_payload_only() -> None:
    query = compose_retrieval_query(
        syllabus=None, weak_topics=["矩阵的秩"], plan=None
    )
    assert query == "矩阵的秩"


# ---------------------------------------------------------------------------
# Objective statistics (SOP §10.2 / §10.3)
# ---------------------------------------------------------------------------


def test_stats_show_sample_years_counts_and_question_sources() -> None:
    plan = _plan(None)
    stats = plan.past_exam_stats

    assert stats["question_count"] == 4
    assert stats["sample_years"] == [2013, 2023]
    coverage = {item["year"]: item["count"] for item in stats["year_coverage"]}
    assert coverage == {2013: 2, 2023: 2}
    for question in stats["questions"]:
        # 每条统计都能回到题目来源。
        assert question["source_id"]
        assert question["question_id"]
        assert question["locator_type"] in {"page", "slide", "heading", "question", "none"}


def test_type_distribution_counts_only_reviewed_headings() -> None:
    plan = _plan(None)
    distribution = {
        item["key"]: item["count"] for item in plan.past_exam_stats["type_distribution"]
    }

    assert distribution["filling_blank"] == 2
    assert distribution["calculation"] == 1
    # “三、”没有题型信息，必须诚实计入未标注，不得猜测。
    assert distribution["untyped"] == 1


def test_appendix_renders_objective_counts_and_never_predicts() -> None:
    plan = _plan("矩阵的秩、酉空间")
    appendix = render_exam_review_appendix(plan)

    assert "备考复习统计（系统生成）" in appendix
    assert "2013（2 题）" in appendix and "2023（2 题）" in appendix
    assert "客观出现次数" in appendix
    assert "不输出命题概率" in appendix
    # “必考”只允许出现在否定句中。
    for line in appendix.splitlines():
        if "必考" in line:
            assert "没有“必考”预测" in line
    # 未被资料覆盖的大纲条目如实列出。
    assert "酉空间" in appendix
    # AI 样题边界必须明确。
    assert "AI 生成" in appendix and "非历年真题" in appendix


def test_empty_past_exam_corpus_is_reported_honestly() -> None:
    facts = ExamCorpusFacts(
        course_id=COURSE_ID,
        corpus_version="c",
        course_pack_version=None,
        sources=(ExamSourceFact("note-001", "矩阵复习笔记", "note", None),),
        questions=(),
        heading_topics=("矩阵的秩",),
    )
    plan = _plan(None, facts=facts)
    appendix = render_exam_review_appendix(plan)

    assert plan.past_exam_stats["question_count"] == 0
    assert "没有可统计的历年题" in appendix


def test_knowledge_points_carry_layers_locations_and_order() -> None:
    plan = _plan(None, ["矩阵的秩"])
    points = plan.knowledge_points

    assert points
    first = points[0]
    assert first["topic"] == "矩阵的秩"
    assert first["weak_topic_matched"] is True
    assert first["order_reasons"] and "匹配薄弱点" in first["order_reasons"]
    assert 1 <= first["layer"] <= 3
    assert first["material_locations"]
    location = first["material_locations"][0]
    assert location["source_id"] == "exam-2013"
    assert first["questions"][0]["question_id"]


def test_question_type_headings_never_become_knowledge_point_topics() -> None:
    # 真实语料常见形态：题目只挂在“卷名 + 题型”标题下。题型是统计维度，
    # 卷名不是知识点；两者都必须诚实降级为题组，不得伪装成知识点分层。
    type_only_facts = ExamCorpusFacts(
        course_id=COURSE_ID,
        corpus_version="corpus-test",
        course_pack_version="pack-test",
        sources=(ExamSourceFact("exam-2022", "2022 期末 B 卷", "past_exam", 2022),),
        questions=(
            ExamQuestionFact(
                "Q11", "exam-2022", "2022 期末 B 卷", 2022,
                ("2022 期末 B 卷", "二、填空题（每空3分）"), "heading", None, None,
            ),
            ExamQuestionFact(
                "Q21", "exam-2022", "2022 期末 B 卷", 2022,
                ("2022 期末 B 卷", "三、计算题"), "heading", None, None,
            ),
        ),
        heading_topics=(),
    )
    plan = _plan(None, facts=type_only_facts)

    assert plan.past_exam_stats["question_count"] == 2
    assert plan.knowledge_points == ()
    appendix = render_exam_review_appendix(plan)
    assert "没有可按知识点归组的标题" in appendix
    assert "历年题题组" in appendix
    assert "《2022 期末 B 卷》" in appendix
    assert "代表题号：Q11、Q21" in appendix


def test_paper_title_heading_with_year_prefix_never_becomes_topic() -> None:
    # 线上真实语料回归（iteration 5 实测）：卷名 H1 带 “2022级” 前缀时，
    # 剥序不一致会让 “级大学物理…” 漏过卷名比对，把整份卷当成一个知识点。
    paper_title = "2022级大学物理（一）期末试卷答案及评分标准（B卷）"
    facts = ExamCorpusFacts(
        course_id=COURSE_ID,
        corpus_version="corpus-test",
        course_pack_version="pack-test",
        sources=(
            ExamSourceFact("exam-2022-b", paper_title, "past_exam_answer", 2022),
        ),
        questions=tuple(
            ExamQuestionFact(
                question_id, "exam-2022-b", paper_title, 2022,
                (paper_title, section), "heading", None, None,
            )
            for question_id, section in (
                ("2022-B-Q1-Q10", "一、选择题"),
                ("2022-B-Q11", "二、填空题"),
                ("2022-B-Q21", "三、计算题"),
            )
        ),
        heading_topics=(),
    )
    plan = _plan(None, review_question="泊松分布怎么复习", facts=facts)

    assert plan.knowledge_points == ()
    appendix = render_exam_review_appendix(plan)
    assert paper_title not in appendix.split("### 历年题客观统计")[0]
    assert "《2022级大学物理（一）期末试卷答案及评分标准（B卷）》" in appendix


def test_review_question_boosts_matching_knowledge_point_order() -> None:
    plan = _plan(None, review_question="矩阵的秩怎么复习？")
    points = plan.knowledge_points

    assert points
    first = points[0]
    assert first["topic"] == "矩阵的秩"
    assert first["question_matched"] is True
    assert "匹配你的提问" in first["order_reasons"]


def test_review_question_never_enters_public_plan_output() -> None:
    plan = _plan(None, review_question="私有提问背景甲乙丙")

    serialized = json.dumps(plan.to_output_dict(), ensure_ascii=False)
    assert "私有提问背景甲乙丙" not in serialized


def test_uncovered_syllabus_items_are_listed_only_with_syllabus() -> None:
    with_plan = _plan("矩阵的秩、酉空间")
    without_plan = _plan(None)

    assert with_plan.uncovered_items == ("酉空间",)
    assert without_plan.uncovered_items == ()


# ---------------------------------------------------------------------------
# Private input isolation (SOP §10.2 / §10.3)
# ---------------------------------------------------------------------------


def test_trace_and_public_outputs_stay_free_of_private_payload() -> None:
    syllabus = "私有大纲内容甲乙丙"
    plan = _plan(syllabus, ["私有薄弱点丁"])

    # Trace-safe fields: only path code and objective counts/years.
    output = plan.to_output_dict()
    serialized = json.dumps(output, ensure_ascii=False)
    # 未覆盖内容允许回显给同一用户；除此之外不得携带大纲/薄弱点原文。
    assert "私有薄弱点丁" not in serialized
    for item in plan.uncovered_items:
        assert item  # uncovered items are derived, user-scoped echoes


def test_course_pack_files_unchanged_after_exam_review_runs(tmp_path: Path) -> None:
    client = _client(tmp_path)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    ).json()

    def pack_digests() -> dict[str, str]:
        store = tmp_path / "store"
        return {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((store / "active").glob("**/*.json"))
        }

    before = pack_digests()
    for syllabus in (None, "私有大纲内容甲乙丙"):
        response = client.post(
            "/api/v1/workflow-runs",
            json=_exam_request(conversation["conversation_id"], syllabus=syllabus),
        )
        assert response.status_code == 201, response.text
    assert pack_digests() == before


def test_runtime_cache_stays_disabled_for_private_inputs(tmp_path: Path) -> None:
    client = _client(tmp_path)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    ).json()
    result = _run_exam(client, conversation["conversation_id"], syllabus=None)

    cache_event = next(
        event for event in result["trace"] if event["node"] == "cache_policy"
    )
    assert cache_event["result"]["cache_hit"] is False
    assert cache_event["result"]["reason_code"] == "runtime_cache_not_configured"


def test_worker_course_pack_build_never_uses_models_or_byok() -> None:
    import scut_senior_worker.corpus_builder as builder

    source = Path(builder.__file__).read_text(encoding="utf-8")
    assert "byok" not in source.casefold()
    assert "api_key" not in source.casefold()
    # The builder signature exposes no model gateway or credential input.
    assert "model_gateway" not in source
    assert "credential" not in source.casefold()


# ---------------------------------------------------------------------------
# Runtime integration: plan node, appendix, degradation and flag (SOP §4.2)
# ---------------------------------------------------------------------------


def test_exam_review_run_carries_plan_appendix_and_safe_trace(tmp_path: Path) -> None:
    client = _client(tmp_path)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    ).json()
    result = _run_exam(
        client, conversation["conversation_id"], syllabus="矩阵的秩、酉空间"
    )

    plan = result["workflow_output"]["exam_review"]
    assert plan["path"] == "with_syllabus"
    assert plan["priority_order"][0] == "user_syllabus"
    assert plan["past_exam_stats"]["question_count"] == 2

    repository = next(
        block
        for block in result["answer_blocks"]
        if block["type"] == "repository"
    )
    assert "备考复习统计（系统生成）" in repository["content"]
    assert "酉空间" in repository["content"]

    plan_event = next(
        event for event in result["trace"] if event["node"] == "exam_review_plan"
    )
    assert plan_event["status"] == "completed"
    assert plan_event["result"]["review_path"] == "with_syllabus"
    assert plan_event["result"]["sample_years"] == [2023]
    # 私有大纲原文不进入 Trace。
    assert "矩阵的秩" not in json.dumps(plan_event["result"], ensure_ascii=False)

    # 共用契约不受影响：引用 Guard、证据状态与持久化节点照常。
    node_names = [event["node"] for event in result["trace"]]
    assert "citation_guard" in node_names
    assert "persistence" in node_names
    assert result["evidence_status"] in {"sufficient", "partial"}


def test_exam_review_plan_preview_requires_explicit_confirmation_before_run(
    tmp_path: Path,
) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "preview.db"))
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": "linear_algebra"}
    ).json()
    response = client.post(
        "/api/v1/exam-review/plan/preview",
        json=_exam_request(conversation["conversation_id"], syllabus="矩阵与线性方程组"),
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["confirmation_required"] is True
    assert payload["plan"]["plan_version"] == "exam-review-plan-v1"
    assert client.get(
        f"/api/v1/conversations/{conversation['conversation_id']}"
    ).json()["runs"] == []


def test_without_syllabus_run_declares_non_official_scope(tmp_path: Path) -> None:
    client = _client(tmp_path)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    ).json()
    result = _run_exam(client, conversation["conversation_id"], syllabus=None)

    repository = next(
        block
        for block in result["answer_blocks"]
        if block["type"] == "repository"
    )
    assert "不是官方考试范围" in repository["content"]
    assert "不构成考试重点预测" in repository["content"]
    assert result["workflow_output"]["exam_review"]["path"] == "without_syllabus"


def test_facts_failure_degrades_without_failing_the_run(tmp_path: Path) -> None:
    app = create_app(Settings(app_env="test", database_path=tmp_path / "db.sqlite"))
    class _BrokenProvider:
        def load(self, course_id: str) -> None:
            raise ExamFactsUnavailable("boom")

    app.state.service.exam_facts = _BrokenProvider()
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    ).json()
    result = _run_exam(client, conversation["conversation_id"], syllabus=None)

    assert result["run_status"] == "completed"
    assert "exam_review" not in result["workflow_output"]
    plan_event = next(
        event for event in result["trace"] if event["node"] == "exam_review_plan"
    )
    assert plan_event["status"] == "skipped"
    assert plan_event["result"]["degradation_code"] == "exam_review_facts_unavailable"


def test_feature_flag_off_restores_pre_iteration5_behaviour(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            app_env="test",
            database_path=tmp_path / "db.sqlite",
            exam_review_plan_enabled=False,
        )
    )
    client = TestClient(app)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    ).json()
    result = _run_exam(client, conversation["conversation_id"], syllabus=None)

    assert result["run_status"] == "completed"
    assert "exam_review" not in result["workflow_output"]
    assert all(
        event["node"] != "exam_review_plan" for event in result["trace"]
    )
    repository = next(
        block
        for block in result["answer_blocks"]
        if block["type"] == "repository"
    )
    assert "备考复习统计（系统生成）" not in repository["content"]


def test_other_workflows_never_get_a_plan_node(tmp_path: Path) -> None:
    client = _client(tmp_path)
    conversation = client.post(
        "/api/v1/conversations", json={"course_id": COURSE_ID}
    ).json()
    request = _exam_request(conversation["conversation_id"], syllabus=None)
    request["workflow_type"] = "knowledge_qa"
    request["workflow_payload"] = {"question": "什么是矩阵的秩？"}
    response = client.post("/api/v1/workflow-runs", json=request)
    assert response.status_code == 201, response.text
    result = response.json()

    assert all(event["node"] != "exam_review_plan" for event in result["trace"])
    assert "exam_review" not in result["workflow_output"]


# ---------------------------------------------------------------------------
# Facts providers
# ---------------------------------------------------------------------------


def test_fixture_provider_serves_reviewed_past_exam_facts() -> None:
    provider = FixtureExamFactsProvider()
    facts = provider.load(COURSE_ID)

    assert facts.corpus_version == "fixture-corpus-v1"
    past_exams = [
        source for source in facts.sources if source.document_role == "past_exam"
    ]
    assert past_exams and past_exams[0].year == 2023
    assert facts.questions
    for question in facts.questions:
        assert question.source_title
        assert question.heading_path


def test_fixture_provider_rejects_courses_without_fixture_corpus() -> None:
    provider = FixtureExamFactsProvider()
    try:
        provider.load("cpp")
    except ExamFactsUnavailable:
        return
    raise AssertionError("cpp has no fixture corpus and must not serve facts")


def test_local_provider_reads_active_course_pack(tmp_path: Path) -> None:
    store, corpus_version, pack_version = _build_store_with_past_exam(tmp_path)
    provider = LocalCorpusExamFactsProvider(store)
    facts = provider.load(COURSE_ID)

    assert facts.corpus_version == corpus_version
    assert facts.course_pack_version == pack_version
    assert facts.questions
    assert all(question.year == 2023 for question in facts.questions)
    assert facts.heading_topics


def test_local_provider_fails_closed_for_missing_course(tmp_path: Path) -> None:
    store, _, _ = _build_store_with_past_exam(tmp_path)
    provider = LocalCorpusExamFactsProvider(store)
    try:
        provider.load("probability_theory")
    except ExamFactsUnavailable:
        return
    raise AssertionError("unregistered course must not serve facts")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _client(tmp_path: Path) -> TestClient:
    app = create_app(
        Settings(
            app_env="test",
            database_path=tmp_path / "db.sqlite",
            corpus_store_path=_build_store_with_past_exam(tmp_path)[0],
            retrieval_mode="local_corpus",
        )
    )
    return TestClient(app)


def _exam_request(conversation_id: str, *, syllabus: str | None) -> dict[str, object]:
    return {
        "workflow_type": "exam_review",
        "course_scope": "single",
        "course_id": COURSE_ID,
        "allowed_course_ids": [],
        "conversation_id": conversation_id,
        "model_source": "platform_default",
        "provider_id": "mock",
        "model_id": "deterministic-fixture-v1",
        "user_input": "帮我备考",
        "answer_mode": "detailed",
        "tone": "teaching_assistant",
        "knowledge_scope": "course_first",
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {
            "syllabus": syllabus,
            "exam_date": None,
            "available_hours": 6,
            "goals": [],
            "weak_topics": ["矩阵的秩"],
        },
    }


def _run_exam(
    client: TestClient, conversation_id: str, *, syllabus: str | None
) -> dict[str, object]:
    response = client.post(
        "/api/v1/workflow-runs",
        json=_exam_request(conversation_id, syllabus=syllabus),
    )
    assert response.status_code == 201, response.text
    return response.json()


def _git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _build_store_with_past_exam(tmp_path: Path) -> tuple[Path, str, str]:
    """Build and activate a minimal local corpus with one past exam."""

    repository = tmp_path / "repository"
    knowledge = repository / "apps" / "scut-senior" / "knowledge"
    markdown = knowledge / COURSE_ID / "exam.md"
    markdown.parent.mkdir(parents=True)
    markdown.write_text(
        """---
source_id: linear-algebra-exam-2023
course_id: linear_algebra
title: 2023 线性代数期末 A 卷
original_file: 学科资料/线代/2023A.docx
document_role: past_exam
year: 2023
locator_type: page
---

<!-- page: 1 -->

# 2023 线性代数期末 A 卷

<!-- question: Q1 -->

## 一、填空题（每空3分，共15分）

设合成矩阵为单位矩阵，说明它的秩。

<!-- page: 2 -->

<!-- question: Q2 -->

## 二、计算题（10分）

求合成矩阵的特征值。
""",
        encoding="utf-8",
    )
    note = knowledge / COURSE_ID / "note.md"
    note.write_text(
        """---
source_id: linear-algebra-note-001
course_id: linear_algebra
title: 矩阵复习笔记
original_file: 学科资料/线代/笔记.docx
document_role: note
year:
locator_type: heading
---

# 矩阵的秩

矩阵的秩由非零行数定义。

# 初等行变换

初等行变换不改变矩阵的秩。
""",
        encoding="utf-8",
    )
    row_past = {
        "source_id": "linear-algebra-exam-2023",
        "course": COURSE_ID,
        "title": "2023 线性代数期末 A 卷",
        "original_path": "学科资料/线代/2023A.docx",
        "format": "docx",
        "document_role": "past_exam",
        "year": "2023",
        "output_md": f"{COURSE_ID}/exam.md",
        "locator_type": "page",
        "method": "synthetic-test",
        "ocr_used": "false",
        "ocr_confidence": "",
        "ocr_warning": "",
        "preview": "false",
        "status": "passed",
        "reviewer": "iteration5-test",
        "notes": "synthetic past exam",
    }
    row_note = {
        **row_past,
        "source_id": "linear-algebra-note-001",
        "title": "矩阵复习笔记",
        "original_path": "学科资料/线代/笔记.docx",
        "document_role": "note",
        "year": "",
        "output_md": f"{COURSE_ID}/note.md",
        "locator_type": "heading",
    }
    with (knowledge / "manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_HEADERS)
        writer.writeheader()
        writer.writerow(row_past)
        writer.writerow(row_note)

    contracts = repository / "apps/scut-senior/packages/contracts/v1"
    contracts.mkdir(parents=True)
    (contracts / "courses.json").write_bytes(
        (CONTRACT_ROOT / "courses.json").read_bytes()
    )
    worker_input = repository / "apps/scut-senior/worker"
    worker_input.mkdir(parents=True)
    (worker_input / "BUILD_INPUT").write_text(
        "synthetic fixed worker input\n", encoding="utf-8"
    )

    _git(repository, "init", "-b", "master")
    _git(repository, "config", "user.name", "Iteration5 Test")
    _git(repository, "config", "user.email", "iteration5@example.invalid")
    _git(
        repository,
        "add",
        "apps/scut-senior/knowledge",
        "apps/scut-senior/worker",
        "apps/scut-senior/packages/contracts/v1",
    )
    _git(repository, "commit", "-m", "fixed reviewed corpus")
    commit = _git(repository, "rev-parse", "HEAD")
    store = tmp_path / "store"
    candidate = build_candidate(
        manifest_path=knowledge / "manifest.csv",
        knowledge_root=knowledge,
        store_root=store,
        source_commit=commit,
        repository_root=repository,
        max_chunk_chars=200,
    )
    activate_candidate(
        store,
        candidate.corpus_version,
        repository_root=repository,
        trusted_master_ref="refs/heads/master",
    )
    set_course_enabled(store, COURSE_ID, enabled=True)
    return (
        store,
        candidate.corpus_version,
        candidate.metadata["course_pack_versions"][COURSE_ID],
    )
