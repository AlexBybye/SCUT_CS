from datetime import UTC, datetime, timedelta
from pathlib import Path

from scut_senior_api.adapters.sqlite import SQLiteWorkflowRepository


def test_private_knowledge_is_filtered_by_user_and_selected_courses(tmp_path: Path) -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    repository = SQLiteWorkflowRepository(tmp_path / "private.db", clock=lambda: now)
    alice = "alice"
    bob = "bob"
    repository.save_private_knowledge(
        user_id=alice, course_id="linear_algebra", title="Alice 矩阵笔记", content="矩阵秩"
    )
    repository.save_private_knowledge(
        user_id=alice, course_id="probability_theory", title="Alice 概率笔记", content="随机变量"
    )
    repository.save_private_knowledge(
        user_id=bob, course_id="linear_algebra", title="Bob 矩阵笔记", content="另一份内容"
    )

    selected = repository.list_private_knowledge_sources(
        user_id=alice, course_ids=["probability_theory"]
    )
    assert [source.course_id for source in selected] == ["probability_theory"]
    assert selected[0].text == "随机变量"
    assert repository.list_private_knowledge_sources(
        user_id=bob, course_ids=["probability_theory"]
    ) == []


def test_expired_private_knowledge_is_not_retrieved_and_is_physically_deleted(
    tmp_path: Path,
) -> None:
    current = [datetime(2026, 1, 1, tzinfo=UTC)]
    repository = SQLiteWorkflowRepository(tmp_path / "private-expiry.db", clock=lambda: current[0])
    repository.save_private_knowledge(
        user_id="alice", course_id="linear_algebra", title="过期笔记", content="旧内容"
    )
    current[0] += timedelta(days=8)
    assert repository.list_private_knowledge_sources(
        user_id="alice", course_ids=["linear_algebra"]
    ) == []
    repository.cleanup_material_records()
    with repository.connect() as connection:
        assert connection.execute("SELECT COUNT(*) FROM private_knowledge_items").fetchone()[0] == 0
