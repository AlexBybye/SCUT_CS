"""迭代 7（SOP §12）测试：临时材料治理与贡献待处理队列。

覆盖：契约校验、确定性预览、状态机、7 天／30 天 TTL 实际清理、
所有权隔离、维护者队列边界（无自动 PR、PR 链接固定形态）与泄漏检查。
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from scut_senior_api.adapters.sqlite import SQLiteWorkflowRepository
from scut_senior_api.auth import GitHubUserProfile, SESSION_COOKIE_NAME
from scut_senior_api.config import Settings
from scut_senior_api.contributions import (
    CONTRIBUTION_REVIEW_COPY_TTL_DAYS,
    TEMPORARY_MATERIAL_TTL_DAYS,
    ContributionTransitionError,
    build_contribution_preview,
    normalize_contribution_markdown,
    validate_contribution_transition,
    validate_github_pr_url,
)
from scut_senior_api.contracts import ContributionState
from scut_senior_api.main import create_app


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------


class MutableClock:
    def __init__(self, current: datetime):
        self.current = current

    def __call__(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> None:
        self.current += delta


def mock_app(tmp_path: Path, database_name: str = "iteration-7.db"):
    app = create_app(
        Settings(app_env="test", database_path=tmp_path / database_name)
    )
    return TestClient(app, base_url="https://testserver")


def oauth_settings(database_path: Path) -> Settings:
    return Settings(
        app_env="test",
        identity_mode="github_oauth",
        storage_mode="sqlite",
        database_path=database_path,
        github_client_id="test-client-id",
        github_client_secret="test-client-secret",
        github_callback_url="https://testserver/api/v1/auth/github/callback",
        post_login_redirect_url="https://testserver/",
        maintainer_github_logins=("maintainer",),
    )


def authenticated_client(app, github_id: int, login: str) -> TestClient:
    repository = app.state.repository
    user_id = repository.upsert_github_user(GitHubUserProfile(github_id, login))
    session = repository.issue_session(user_id)
    client = TestClient(app, base_url="https://testserver")
    client.cookies.set(SESSION_COOKIE_NAME, session.token, path="/")
    return client


def create_conversation(client: TestClient) -> dict:
    response = client.post("/api/v1/conversations", json={"course_id": "linear_algebra"})
    assert response.status_code == 201, response.text
    return response.json()


def save_material(
    client: TestClient, conversation_id: str, *, content: str | None = None
) -> dict:
    payload = {
        "conversation_id": conversation_id,
        "course_id": "linear_algebra",
        "title": "特征值复习提纲",
        "content": content or ("# 特征值复习提纲\n" + "矩阵对角化要点。\n" * 10),
    }
    response = client.post("/api/v1/temporary-materials", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


FULL_CONFIRMATIONS = {
    "course_confirmed": True,
    "source_confirmed": True,
    "public_share_rights_confirmed": True,
    "no_sensitive_info_confirmed": True,
    "public_pr_visibility_acknowledged": True,
}


# ---------------------------------------------------------------------------
# 纯规则：预览、规范化、状态机、PR 链接
# ---------------------------------------------------------------------------


def test_preview_normalization_is_deterministic() -> None:
    raw = "# 标题\r\n\r\n正文行   \n\n\n\n下一行\r"
    first = build_contribution_preview(
        course_id="linear_algebra", title=None, content=raw
    )
    second = build_contribution_preview(
        course_id="linear_algebra", title=None, content=raw
    )
    assert first == second
    assert "\r" not in first.normalized_content
    assert "\n\n\n" not in first.normalized_content
    assert first.normalized_content.endswith("\n")
    # 规范化不改写语义内容。
    assert "# 标题" in first.normalized_content
    assert "正文行" in first.normalized_content


def test_preview_reports_missing_title_question_markers_short_body_and_html() -> None:
    preview = build_contribution_preview(
        course_id="linear_algebra", title=None, content="<b>短</b>"
    )
    assert preview.has_h1_title is False
    assert any("标题" in warning for warning in preview.warnings)
    assert any("题目标记" in warning for warning in preview.warnings)
    assert any("过短" in warning for warning in preview.warnings)
    assert any("HTML" in warning for warning in preview.warnings)

    good = build_contribution_preview(
        course_id="linear_algebra",
        title="给定标题",
        content=(
            "# 给定标题\n\nquestion 1: 求特征值。\n"
            + "详细解答内容，足够长，不需要警告。\n" * 5
        ),
    )
    assert good.question_marker_count >= 1
    assert not any("标题" in warning for warning in good.warnings)


def test_normalize_markdown_keeps_semantic_content() -> None:
    normalized = normalize_contribution_markdown("# A\r\nbody \n\n\n\nmore")
    assert normalized == "# A\nbody\n\nmore\n"


def test_state_machine_rejects_invalid_transitions() -> None:
    validate_contribution_transition(ContributionState.DRAFT, action="submit")
    validate_contribution_transition(ContributionState.SUBMITTED, action="mark_pr_open")
    validate_contribution_transition(ContributionState.SUBMITTED, action="reject")
    validate_contribution_transition(ContributionState.PR_OPEN, action="merge")

    with pytest.raises(ContributionTransitionError):
        validate_contribution_transition(ContributionState.SUBMITTED, action="merge")
    with pytest.raises(ContributionTransitionError):
        validate_contribution_transition(ContributionState.DRAFT, action="mark_pr_open")
    with pytest.raises(ContributionTransitionError):
        validate_contribution_transition(ContributionState.MERGED, action="reject")
    with pytest.raises(ContributionTransitionError):
        validate_contribution_transition(ContributionState.REJECTED, action="merge")
    with pytest.raises(ContributionTransitionError):
        validate_contribution_transition(ContributionState.EXPIRED, action="submit")


def test_pr_url_only_accepts_fixed_github_pull_form() -> None:
    valid = "https://github.com/AlexBybye/SCUT_CS/pull/42"
    assert validate_github_pr_url(valid) == valid

    for bad in (
        "http://github.com/o/r/pull/1",
        "https://evil.com/o/r/pull/1",
        "https://github.com/o/r/pulls/1",
        "https://github.com/o/r/pull/0",
        "https://github.com/o/r/pull/1?x=1",
        "https://github.com/o/r/pull/1#issuecomment-1",
        "https://user:pass@github.com/o/r/pull/1",
    ):
        with pytest.raises(ContributionTransitionError):
            validate_github_pr_url(bad)


def test_confirmation_contract_requires_every_item() -> None:
    fields = dict(FULL_CONFIRMATIONS)
    for key in fields:
        broken = {**fields, key: False}
        with pytest.raises(ValidationError):
            from scut_senior_api.contracts import ContributionConfirmations

            ContributionConfirmations(**broken)


# ---------------------------------------------------------------------------
# 仓储与 TTL：7 天材料物理删除；30 天贡献副本载荷清空
# ---------------------------------------------------------------------------


def material_repository(clock: MutableClock, tmp_path: Path) -> SQLiteWorkflowRepository:
    return SQLiteWorkflowRepository(
        tmp_path / "materials.db",
        clock=clock,
    )


def test_temporary_material_expires_after_seven_days_and_is_physically_deleted(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 23, tzinfo=UTC))
    repository = material_repository(clock, tmp_path)
    material = repository.save_temporary_material(
        user_id="user-a",
        conversation_id=uuid4(),
        course_id="linear_algebra",
        title="提纲",
        content="# 提纲\n" + "内容。\n" * 20,
    )

    expected_expiry = datetime(2026, 8, 23, tzinfo=UTC) + timedelta(
        days=TEMPORARY_MATERIAL_TTL_DAYS
    )
    assert material.expires_at == expected_expiry

    clock.advance(timedelta(days=TEMPORARY_MATERIAL_TTL_DAYS, minutes=1))
    counts = repository.cleanup_material_records()
    assert counts.materials == 1
    assert repository.get_temporary_material("user-a", material.material_id) is None

    with sqlite3.connect(tmp_path / "materials.db") as connection:
        remaining = connection.execute(
            "SELECT COUNT(*) FROM temporary_materials"
        ).fetchone()[0]
    assert remaining == 0


def test_submitted_contribution_copy_is_cleared_after_thirty_days(
    tmp_path: Path,
) -> None:
    clock = MutableClock(datetime(2026, 8, 23, tzinfo=UTC))
    repository = material_repository(clock, tmp_path)
    contribution = repository.create_contribution(
        user_id="user-a",
        material_id=None,
        course_id="linear_algebra",
        proposed_source_id="linear_algebra-contribution-00000000",
        title="提交的材料",
        content_snapshot="# 提交的材料\n" + "内容。\n" * 30,
        state=ContributionState.SUBMITTED,
    )
    assert contribution.expires_at == datetime(2026, 8, 23, tzinfo=UTC) + timedelta(
        days=CONTRIBUTION_REVIEW_COPY_TTL_DAYS
    )
    assert contribution.char_count > 0

    clock.advance(timedelta(days=CONTRIBUTION_REVIEW_COPY_TTL_DAYS, minutes=1))
    counts = repository.cleanup_material_records()

    assert counts.contributions_cleared == 1
    expired = repository.get_contribution("user-a", contribution.contribution_id)
    assert expired is not None
    assert expired.state == ContributionState.EXPIRED
    # 载荷实际清空：字符计数归零，不能只在 UI 隐藏。
    assert expired.char_count == 0
    with sqlite3.connect(tmp_path / "materials.db") as connection:
        row = connection.execute(
            "SELECT content_snapshot FROM contributions WHERE contribution_id = ?",
            (str(contribution.contribution_id),),
        ).fetchone()
    assert row is not None
    assert row[0] == ""


def test_draft_contribution_inherits_seven_day_horizon(tmp_path: Path) -> None:
    clock = MutableClock(datetime(2026, 8, 23, tzinfo=UTC))
    repository = material_repository(clock, tmp_path)
    draft = repository.create_contribution(
        user_id="user-a",
        material_id=None,
        course_id="linear_algebra",
        proposed_source_id="linear_algebra-contribution-00000001",
        title="草稿",
        content_snapshot="# 草稿\n内容。\n" * 5,
        state=ContributionState.DRAFT,
    )
    assert draft.expires_at == datetime(2026, 8, 23, tzinfo=UTC) + timedelta(
        days=TEMPORARY_MATERIAL_TTL_DAYS
    )


# ---------------------------------------------------------------------------
# API：mock 身份下的完整用户路径
# ---------------------------------------------------------------------------


def test_material_lifecycle_and_contribution_flow_via_api(tmp_path: Path) -> None:
    client = mock_app(tmp_path)
    conversation = create_conversation(client)

    material = save_material(client, conversation["conversation_id"])
    assert material["title"] == "特征值复习提纲"
    assert material["expires_at"] > material["created_at"]
    assert "content" not in material  # 列表/记录视图不回传全文。

    detail_response = client.get(
        f"/api/v1/temporary-materials/{material['material_id']}"
    )
    assert detail_response.status_code == 200
    assert "特征值复习提纲" in detail_response.json()["content"]

    listed = client.get("/api/v1/temporary-materials").json()
    assert [item["material_id"] for item in listed] == [material["material_id"]]

    # 预览端点接受显式内容而非引用存储（预览不落库）。
    preview = client.post(
        "/api/v1/contributions/preview",
        json={
            "course_id": "linear_algebra",
            "title": "特征值复习提纲",
            "content": "# 特征值复习提纲\n" + "内容。\n" * 10,
        },
    )
    assert preview.status_code == 200
    assert preview.json()["proposed_source_id"].startswith("linear_algebra-contribution-")

    # 缺少确认 → 契约拒绝，不产生任何记录。
    incomplete = client.post(
        "/api/v1/contributions",
        json={
            "material_id": material["material_id"],
            "course_id": "linear_algebra",
            "confirmations": {
                **FULL_CONFIRMATIONS,
                "public_share_rights_confirmed": False,
            },
        },
    )
    assert incomplete.status_code == 422
    assert client.get("/api/v1/contributions").json() == []

    submitted = client.post(
        "/api/v1/contributions",
        json={
            "material_id": material["material_id"],
            "course_id": "linear_algebra",
            "confirmations": FULL_CONFIRMATIONS,
        },
    )
    assert submitted.status_code == 201, submitted.text
    record = submitted.json()
    assert record["state"] == "submitted"
    assert record["pr_url"] is None
    assert "content" not in record  # 记录视图永不回传私有载荷。

    # 维护者队列在 mock 身份下不可用（需要真实 GitHub 登录）。
    queue_forbidden = client.get("/api/v1/maintainer/contributions")
    assert queue_forbidden.status_code == 401

    deleted = client.delete(f"/api/v1/temporary-materials/{material['material_id']}")
    assert deleted.status_code == 204
    assert (
        client.get(f"/api/v1/temporary-materials/{material['material_id']}").status_code
        == 404
    )


def test_draft_submission_requires_full_confirmations(tmp_path: Path) -> None:
    client = mock_app(tmp_path, "draft.db")
    conversation = create_conversation(client)
    material = save_material(client, conversation["conversation_id"])

    draft = client.post(
        "/api/v1/contributions",
        json={
            "material_id": material["material_id"],
            "course_id": "linear_algebra",
            "as_draft": True,
            "confirmations": FULL_CONFIRMATIONS,
        },
    )
    assert draft.status_code == 201
    assert draft.json()["state"] == "draft"

    submitted = client.post(
        f"/api/v1/contributions/{draft.json()['contribution_id']}/submit",
        json={"confirmations": FULL_CONFIRMATIONS},
    )
    assert submitted.status_code == 200
    assert submitted.json()["state"] == "submitted"

    # 已提交后不能再重复 submit。
    repeat = client.post(
        f"/api/v1/contributions/{draft.json()['contribution_id']}/submit",
        json={"confirmations": FULL_CONFIRMATIONS},
    )
    assert repeat.status_code == 409


def test_unauthenticated_requests_are_rejected(tmp_path: Path) -> None:
    # mock 身份模式天然等价于已登录；未登录边界必须在 github_oauth 模式下验证。
    app = create_app(oauth_settings(tmp_path / "anon.db"))
    anonymous = TestClient(app, base_url="https://testserver")

    assert anonymous.get("/api/v1/temporary-materials").status_code == 401
    assert anonymous.get("/api/v1/contributions").status_code == 401
    assert (
        anonymous.post(
            "/api/v1/temporary-materials",
            json={
                "conversation_id": str(uuid4()),
                "course_id": "linear_algebra",
                "content": "# 内容\n" + "正文。\n" * 5,
            },
        ).status_code
        == 401
    )
    assert anonymous.post(
        "/api/v1/contributions",
        json={
            "material_id": str(uuid4()),
            "course_id": "linear_algebra",
            "confirmations": FULL_CONFIRMATIONS,
        },
    ).status_code == 401
    assert anonymous.get("/api/v1/maintainer/contributions").status_code == 401


# ---------------------------------------------------------------------------
# 所有权隔离（oauth 双用户）
# ---------------------------------------------------------------------------


def test_private_materials_and_contributions_are_user_scoped(tmp_path: Path) -> None:
    app = create_app(oauth_settings(tmp_path / "ownership.db"))
    alice = authenticated_client(app, 1001, "alice")
    bob = authenticated_client(app, 1002, "bob")

    conversation = create_conversation(alice)
    material = save_material(alice, conversation["conversation_id"])

    # Bob 不能读取 Alice 的材料：等同不存在。
    assert (
        bob.get(f"/api/v1/temporary-materials/{material['material_id']}").status_code
        == 404
    )
    assert bob.get("/api/v1/temporary-materials").json() == []
    assert bob.delete(
        f"/api/v1/temporary-materials/{material['material_id']}"
    ).status_code == 404

    contribution = alice.post(
        "/api/v1/contributions",
        json={
            "material_id": material["material_id"],
            "course_id": "linear_algebra",
            "confirmations": FULL_CONFIRMATIONS,
        },
    ).json()

    assert (
        bob.get(f"/api/v1/contributions/{contribution['contribution_id']}").status_code
        == 404
    )
    assert bob.get("/api/v1/contributions").json() == []

    # Alice 自己可见。
    assert alice.get("/api/v1/contributions").json() != []
    assert (
        alice.get(f"/api/v1/contributions/{contribution['contribution_id']}").status_code
        == 200
    )


# ---------------------------------------------------------------------------
# 维护者队列（oauth 登录）：人工推进、固定 PR 形态、无自动合并
# ---------------------------------------------------------------------------


def test_non_allowlisted_github_user_cannot_access_maintainer_queue(tmp_path: Path) -> None:
    app = create_app(oauth_settings(tmp_path / "allowlist.db"))
    ordinary_user = authenticated_client(app, 2003, "ordinary-user")
    response = ordinary_user.get("/api/v1/maintainer/contributions")
    assert response.status_code == 403


def test_maintainer_queue_manual_progression_without_auto_merge(
    tmp_path: Path,
) -> None:
    app = create_app(oauth_settings(tmp_path / "queue.db"))
    maintainer = authenticated_client(app, 2001, "maintainer")
    author = authenticated_client(app, 2002, "author")

    conversation = create_conversation(author)
    material = save_material(author, conversation["conversation_id"])
    contribution = author.post(
        "/api/v1/contributions",
        json={
            "material_id": material["material_id"],
            "course_id": "linear_algebra",
            "confirmations": FULL_CONFIRMATIONS,
        },
    ).json()
    contribution_id = contribution["contribution_id"]

    queue = maintainer.get("/api/v1/maintainer/contributions")
    assert queue.status_code == 200
    assert [item["contribution_id"] for item in queue.json()] == [contribution_id]
    # 队列条目不回传私有载荷全文。
    assert "content" not in queue.json()[0]

    # 没有 PR 就不能“合并”：队列永远不自动合并仓库。
    direct_merge = maintainer.post(
        f"/api/v1/maintainer/contributions/{contribution_id}/transition",
        json={"action": "merge"},
    )
    assert direct_merge.status_code == 409

    # mark_pr_open 必须携带固定形态的 GitHub PR 链接。
    missing_url = maintainer.post(
        f"/api/v1/maintainer/contributions/{contribution_id}/transition",
        json={"action": "mark_pr_open"},
    )
    assert missing_url.status_code == 409

    pr_open = maintainer.post(
        f"/api/v1/maintainer/contributions/{contribution_id}/transition",
        json={
            "action": "mark_pr_open",
            "pr_url": "https://github.com/AlexBybye/SCUT_CS/pull/7",
            "note": "人工创建的贡献 PR。",
        },
    )
    assert pr_open.status_code == 200
    assert pr_open.json()["state"] == "pr_open"
    assert (
        pr_open.json()["pr_url"]
        == "https://github.com/AlexBybye/SCUT_CS/pull/7"
    )

    merged = maintainer.post(
        f"/api/v1/maintainer/contributions/{contribution_id}/transition",
        json={"action": "merge"},
    )
    assert merged.status_code == 200
    assert merged.json()["state"] == "merged"

    # 终态之后不再接受任何迁移；已处理条目退出默认队列。
    after_merge = maintainer.post(
        f"/api/v1/maintainer/contributions/{contribution_id}/transition",
        json={"action": "reject"},
    )
    assert after_merge.status_code == 409
    assert maintainer.get("/api/v1/maintainer/contributions").json() == []


def test_maintainer_can_reject_from_queue(tmp_path: Path) -> None:
    app = create_app(oauth_settings(tmp_path / "reject.db"))
    maintainer = authenticated_client(app, 3001, "maintainer")
    author = authenticated_client(app, 3002, "author")

    conversation = create_conversation(author)
    material = save_material(author, conversation["conversation_id"])
    contribution = author.post(
        "/api/v1/contributions",
        json={
            "material_id": material["material_id"],
            "course_id": "linear_algebra",
            "confirmations": FULL_CONFIRMATIONS,
        },
    ).json()

    rejected = maintainer.post(
        f"/api/v1/maintainer/contributions/{contribution['contribution_id']}/transition",
        json={"action": "reject", "note": "内容与原件无法对应。"},
    )
    assert rejected.status_code == 200
    body = rejected.json()
    assert body["state"] == "rejected"
    assert body["maintainer_note"] == "内容与原件无法对应。"

    statuses = {c["contribution_id"]: c["state"] for c in author.get("/api/v1/contributions").json()}
    assert statuses[contribution["contribution_id"]] == "rejected"


# ---------------------------------------------------------------------------
# 泄漏检查与检索隔离
# ---------------------------------------------------------------------------


def test_contribution_records_never_expose_payload_or_credentials(
    tmp_path: Path,
) -> None:
    client = mock_app(tmp_path, "leak.db")
    conversation = create_conversation(client)
    secret_marker = "TOP-SECRET-MARKER"
    material = save_material(
        client,
        conversation["conversation_id"],
        content=f"# 材料\n包含标记 {secret_marker} 的内容。\n" * 5,
    )
    record = client.post(
        "/api/v1/contributions",
        json={
            "material_id": material["material_id"],
            "course_id": "linear_algebra",
            "confirmations": FULL_CONFIRMATIONS,
        },
    ).json()

    serialized = str(record)
    assert secret_marker not in serialized
    for forbidden_key in ("api_key", "ciphertext", "access_token", "client_secret"):
        assert forbidden_key not in serialized


def test_private_material_never_enters_retrieval_sources(tmp_path: Path) -> None:
    """临时材料不进入公共索引或检索候选：运行后所有来源均来自语料库。"""

    client = mock_app(tmp_path, "isolation.db")
    conversation = create_conversation(client)
    unique_marker = "UNIQUE-PRIVATE-MARKER-ZZ9"
    material = save_material(
        client,
        conversation["conversation_id"],
        content=f"# 私有材料 {unique_marker}\n只有用户自己能看的内容。\n" * 5,
    )

    run_request = {
        "workflow_type": "temporary_material_reading",
        "course_scope": "single",
        "course_id": "linear_algebra",
        "allowed_course_ids": [],
        "conversation_id": conversation["conversation_id"],
        "model_source": "platform_default",
        "provider_id": "mock",
        "model_id": "deterministic-fixture-v1",
        "user_input": "这份材料写了什么？说得对不对？",
        "answer_mode": "detailed",
        "tone": "teaching_assistant",
        "knowledge_scope": "course_first",
        "include_bilibili_resources": False,
        "context_refs": [],
        "attachments": [],
        "workflow_payload": {
            "material_title": "私有材料",
            "material_text": f"# 私有材料 {unique_marker}\n只有用户自己能看的内容。",
            "reading_goal": "核对与课程资料冲突之处",
        },
    }
    run = client.post("/api/v1/workflow-runs", json=run_request)
    assert run.status_code == 201, run.text

    sources = run.json().get("citations", [])
    assert all(source["chunk_id"] for source in sources)
    # 检索候选全部来自课程语料，不含用户私有材料文本。
    assert all(unique_marker not in str(source) for source in sources)


# ---------------------------------------------------------------------------
# add file 语义：学科资料落点推导与维护者导出包
# ---------------------------------------------------------------------------


def test_proposed_repo_path_uses_course_registry_mapping(tmp_path: Path) -> None:
    client = mock_app(tmp_path, "repopath.db")
    conversation = create_conversation(client)
    material = save_material(client, conversation["conversation_id"])

    preview = client.post(
        "/api/v1/contributions/preview",
        json={
            "course_id": "linear_algebra",
            "title": "特征值复习提纲",
            "content": "# 特征值复习提纲\n" + "内容。\n" * 10,
        },
    ).json()

    assert preview["proposed_repo_path"] == (
        "学科资料/线性代数/特征值复习提纲.md"
    )

    submitted = client.post(
        "/api/v1/contributions",
        json={
            "material_id": material["material_id"],
            "course_id": "linear_algebra",
            "confirmations": FULL_CONFIRMATIONS,
        },
    ).json()
    assert submitted["proposed_repo_path"].startswith("学科资料/线性代数/")
    assert "/" in submitted["proposed_repo_path"]


def test_contribution_filename_is_sanitized_and_extension_sniffed() -> None:
    from scut_senior_api.contributions import (
        derive_contribution_filename,
        derive_proposed_repo_path,
    )

    messy = derive_contribution_filename('A/B:*c?"<>|', "# 标题\n正文")
    assert messy.endswith(".md")
    assert "/" not in messy and ":" not in messy and '"' not in messy
    # 纯文本无 Markdown 痕迹 → .txt
    plain = derive_contribution_filename("课堂笔记", "第一节 概念介绍，没有任何标记")
    assert plain.endswith(".txt")
    # 未登记 repository_paths 的课程退到 _待归类
    path = derive_proposed_repo_path(
        (), course_id="some_course", title="笔记", content="x" * 80
    )
    assert path == "学科资料/_待归类/some_course/笔记.txt"


def test_maintainer_export_package_returns_path_content_and_commands(
    tmp_path: Path,
) -> None:
    app = create_app(oauth_settings(tmp_path / "export.db"))
    maintainer = authenticated_client(app, 4001, "maintainer")
    author = authenticated_client(app, 4002, "author")

    conversation = create_conversation(author)
    material = save_material(author, conversation["conversation_id"])
    contribution = author.post(
        "/api/v1/contributions",
        json={
            "material_id": material["material_id"],
            "course_id": "linear_algebra",
            "confirmations": FULL_CONFIRMATIONS,
        },
    ).json()
    contribution_id = contribution["contribution_id"]

    exported = maintainer.get(
        f"/api/v1/maintainer/contributions/{contribution_id}/export"
    )
    assert exported.status_code == 200
    body = exported.json()
    assert body["repo_path"] == contribution["proposed_repo_path"]
    assert "矩阵对角化要点" in body["content_snapshot"]
    assert any("git add" in command for command in body["suggested_commands"])
    assert body["suggested_branch"].startswith("contribution-")

    # 匿名/mock 不可导出；普通成员也不应看到他人贡献内容（作者端点无全文）。
    anonymous = TestClient(app, base_url="https://testserver")
    assert (
        anonymous.get(
            f"/api/v1/maintainer/contributions/{contribution_id}/export"
        ).status_code
        == 401
    )
