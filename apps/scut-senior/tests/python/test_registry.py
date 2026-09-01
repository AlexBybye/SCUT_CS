import pytest

from scut_senior_api.registry import CourseRegistry, UnknownCourseError


def test_registry_freezes_fifty_five_course_units() -> None:
    registry = CourseRegistry.load()

    assert len(registry.records) == 55
    assert all(course.is_open is False for course in registry.records)
    assert [course.course_id for course in registry.records if course.fixture_available] == [
        "linear_algebra",
    ]


@pytest.mark.parametrize(
    ("alias", "course_id"),
    [
        ("工数上", "engineering_math_analysis_1"),
        ("工科数学分析Ⅱ", "engineering_math_analysis_2"),
        ("C++", "cpp"),
        ("信息安全", "information_security_intro"),
    ],
)
def test_alias_resolution_is_normalized_exact_match(
    alias: str, course_id: str
) -> None:
    registry = CourseRegistry.load()

    assert registry.resolve(alias).course_id == course_id


@pytest.mark.parametrize(
    "unknown_course",
    # 信息安全数学基础已注册为正式课程；此处保留「文件夹名/模板名 ≠ 别名」的反例。
    ["大物上实验合辑", "优秀寒招资料模板"],
)
def test_alias_resolution_rejects_substrings_and_excluded_courses(
    unknown_course: str,
) -> None:
    registry = CourseRegistry.load()

    with pytest.raises(UnknownCourseError):
        registry.resolve(unknown_course)
