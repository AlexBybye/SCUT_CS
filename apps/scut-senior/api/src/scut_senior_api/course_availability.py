from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .ports import RetrievalGateway, WorkflowRepository
from .registry import CourseRecord, CourseRegistry


RetrievalAvailability = Literal["fixture", "local_corpus", "unavailable"]


@dataclass(frozen=True, slots=True)
class CourseRuntimeAvailability:
    """Student-safe availability for one registered course at this instant.

    The static course registry says what the project knows about a course. This
    runtime projection says whether the configured retrieval adapter can serve
    it now and whether its plugin remains loaded. It deliberately does not
    infer local-corpus readiness from a fixture flag or a configured mode.
    """

    course: CourseRecord
    retrieval_availability: RetrievalAvailability
    retrieval_available: bool
    plugin_loaded: bool
    selectable: bool

    def as_public_dict(self) -> dict[str, object]:
        return {
            "course_id": self.course.course_id,
            "display_name": self.course.display_name,
            "aliases": list(self.course.aliases),
            # These are immutable registry metadata, retained for compatibility
            # and display only. They are not UI selection gates.
            "is_open": self.course.is_open,
            "mock_available": self.course.fixture_available,
            "retrieval_availability": self.retrieval_availability,
            "retrieval_available": self.retrieval_available,
            "plugin_loaded": self.plugin_loaded,
            "selectable": self.selectable,
        }


def derive_course_runtime_availability(
    registry: CourseRegistry,
    retrieval: RetrievalGateway,
    repository: WorkflowRepository,
    *,
    retrieval_mode: str,
) -> tuple[CourseRuntimeAvailability, ...]:
    """Project current gateway/plugin state onto the immutable course registry.

    Course listing must remain available when a local corpus pointer is absent,
    malformed, or cannot be read. Any adapter or repository exception therefore
    makes only that state unavailable; it never fabricates a usable course.
    """

    availability_mode: RetrievalAvailability | None
    if retrieval_mode == "fixture":
        availability_mode = "fixture"
    elif retrieval_mode == "local_corpus":
        availability_mode = "local_corpus"
    else:
        availability_mode = None

    states: list[CourseRuntimeAvailability] = []
    for course in registry.records:
        retrieval_available = _safe_retrieval_available(retrieval, course.course_id)
        plugin_loaded = _safe_plugin_loaded(repository, course.course_id)
        retrieval_availability: RetrievalAvailability = (
            availability_mode
            if availability_mode is not None and retrieval_available
            else "unavailable"
        )
        states.append(
            CourseRuntimeAvailability(
                course=course,
                retrieval_availability=retrieval_availability,
                retrieval_available=retrieval_available,
                plugin_loaded=plugin_loaded,
                selectable=retrieval_available and plugin_loaded,
            )
        )
    return tuple(states)


def _safe_retrieval_available(retrieval: RetrievalGateway, course_id: str) -> bool:
    try:
        # Require the adapter's exact boolean contract. A malformed test double
        # or an accidental truthy return must not advertise a usable course.
        return retrieval.is_course_available(course_id) is True
    except Exception:
        return False


def _safe_plugin_loaded(repository: WorkflowRepository, course_id: str) -> bool:
    try:
        return repository.is_course_plugin_loaded(course_id) is True
    except Exception:
        return False
