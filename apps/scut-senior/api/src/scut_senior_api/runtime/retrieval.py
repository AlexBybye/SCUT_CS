"""Retrieval orchestration for one workflow execution.

This module owns only the request-local retrieval sequence: primary search,
bounded recovery searches, corpus-version consistency and source authorization.
It accepts narrow callbacks for the lifecycle decisions and trace sink so it
does not depend on the service facade or model-generation code.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import re
from time import perf_counter

from ..action_registry import ACTION_REGISTRY
from ..config import Settings
from ..contracts import TraceEvent, TraceEventStatus, WorkflowRunRequest
from ..ports import ConversationTurn, RetrievedSource, RetrievalBatch, RetrievalGateway, WorkflowRepository
from .errors import ContractConflict


TraceSink = Callable[..., TraceEvent]
Decision = Callable[..., str]
ActionRecorder = Callable[[str], None]
ObservationRecorder = Callable[[], None]
OptionalWorkAllowed = Callable[[], bool]


@dataclass(frozen=True, slots=True)
class RetrievalOutcome:
    sources: tuple[RetrievedSource, ...]
    corpus_version: str
    course_pack_version: str | None
    generation_decision_ready: bool


@dataclass(slots=True)
class RetrievalCoordinator:
    """Execute retrieval without exposing candidates outside authorized scope."""

    settings: Settings
    retrieval: RetrievalGateway
    repository: WorkflowRepository
    trace: TraceSink

    def retrieve(
        self,
        *,
        user_id: str,
        request: WorkflowRunRequest,
        course_ids: list[str],
        course_display_name: str,
        retrieval_query: str,
        history: tuple[ConversationTurn, ...],
        has_exam_plan: bool,
        use_user_key: bool,
        initial_corpus_version: str,
        initial_course_pack_version: str | None,
        decide: Decision,
        record_action: ActionRecorder,
        record_observation: ObservationRecorder,
        optional_work_allowed: OptionalWorkAllowed,
    ) -> RetrievalOutcome:
        """Return only course-authorized, version-bound evidence sources."""

        corpus_version = initial_corpus_version
        course_pack_version = initial_course_pack_version
        generation_decision_ready = False
        started = perf_counter()
        retrieval_batch = self.retrieval.search(course_ids, retrieval_query)
        sources, corpus_version, course_pack_version = self._resolve_batch(
            retrieval_batch,
            corpus_version=corpus_version,
            course_pack_version=course_pack_version,
        )
        record_action("retrieve")
        if (
            self.settings.agent_decision_mode in {"rule", "shadow"}
            and (not sources or is_followup_reference_query(retrieval_query))
            and history
            and not has_exam_plan
            and self.settings.retrieval_mode == "local_corpus"
        ):
            context_query = compose_context_carry_query(retrieval_query, history)
            if context_query:
                if not optional_work_allowed():
                    self.trace(
                        node="retrieval_context_carry",
                        status=TraceEventStatus.SKIPPED,
                        result={
                            "hit_count": 0,
                            "candidate_count": 0,
                            "reason_code": "runtime_soft_limit",
                        },
                    )
                else:
                    retry_started = perf_counter()
                    try:
                        context_batch = self.retrieval.search(course_ids, context_query)
                        context_sources = self._resolve_rewrite_batch(
                            context_batch,
                            corpus_version=corpus_version,
                            course_pack_version=course_pack_version,
                        )
                        _assert_authorized_sources(context_sources, course_ids)
                    except Exception:
                        # With legal primary evidence, historical anchoring is
                        # optional: retain the first version-bound batch rather
                        # than making a short follow-up fail wholesale.
                        if not sources:
                            raise
                        self.trace(
                            node="retrieval_context_carry",
                            status=TraceEventStatus.FAILED,
                            duration_ms=_elapsed_ms(retry_started),
                            result={
                                "candidate_count": len(sources),
                                "failure_code": "retrieval_augmentation_failed",
                            },
                        )
                    else:
                        sources = dedupe_sources([*sources, *context_sources])[:8]
                        record_action("retrieve_with_query_rewrite")
                        self.trace(
                            node="retrieval_context_carry",
                            result={
                                "hit_count": len(context_sources),
                                "candidate_count": len(sources),
                                "rewritten_query": context_query[:200],
                            },
                            duration_ms=_elapsed_ms(retry_started),
                        )

        private_search = getattr(self.repository, "list_private_knowledge_sources", None)
        if callable(private_search):
            private_sources = private_search(user_id=user_id, course_ids=course_ids)
            sources.extend(_select_relevant_private_sources(retrieval_query, private_sources))
        _assert_authorized_sources(sources, course_ids)
        sources = dedupe_sources(sources)[:8]
        record_observation()

        if (
            self.settings.agent_decision_mode in {"model", "shadow", "deterministic"}
            and ACTION_REGISTRY.admits(request.workflow_type.value, "retrieve_with_query_rewrite", "post_retrieval")
        ):
            if optional_work_allowed():
                next_action = decide(
                    "post_retrieval",
                    "generate_answer",
                    sources=sources,
                    allow_model=True,
                    accepted_actions=frozenset(ACTION_REGISTRY.allowed_actions(
                        request.workflow_type.value, "post_retrieval"
                    )),
                )
                generation_decision_ready = next_action == "generate_answer"
                if next_action == "retrieve_with_query_rewrite":
                    rewritten_query = compose_agent_rewrite_query(
                        retrieval_query, history, course_display_name
                    )
                    rewrite_started = perf_counter()
                    try:
                        rewritten_batch = self.retrieval.search(course_ids, rewritten_query)
                        rewritten_sources = self._resolve_rewrite_batch(
                            rewritten_batch,
                            corpus_version=corpus_version,
                            course_pack_version=course_pack_version,
                        )
                        _assert_authorized_sources(rewritten_sources, course_ids)
                    except Exception:
                        # A second search is an enhancement only when the
                        # first search already produced authorized evidence.
                        # Retain that ledger on timeout, provider failure, or
                        # corpus-version drift; never combine uncertain new
                        # candidates with the first version-bound batch.
                        if not sources:
                            raise
                        self.trace(
                            node="agent_query_rewrite",
                            status=TraceEventStatus.FAILED,
                            duration_ms=_elapsed_ms(rewrite_started),
                            result={
                                "candidate_count": len(sources),
                                "failure_code": "retrieval_augmentation_failed",
                            },
                        )
                    else:
                        sources = dedupe_sources([*sources, *rewritten_sources])[:8]
                        record_action("retrieve_with_query_rewrite")
                        record_observation()
                        self.trace(
                            node="agent_query_rewrite",
                            duration_ms=_elapsed_ms(rewrite_started),
                            result={
                                "hit_count": len(rewritten_sources),
                                "candidate_count": len(sources),
                                "rewritten_query": rewritten_query[:200],
                            },
                        )
            else:
                self.trace(
                    node="agent_query_rewrite",
                    status=TraceEventStatus.SKIPPED,
                    result={
                        "candidate_count": len(sources),
                        "reason_code": "runtime_soft_limit",
                    },
                )

        self._append_retrieval_trace(
            sources=sources,
            started=started,
        )
        return RetrievalOutcome(
            sources=tuple(sources),
            corpus_version=corpus_version,
            course_pack_version=course_pack_version,
            generation_decision_ready=generation_decision_ready,
        )

    def _resolve_batch(
        self,
        retrieval_batch: RetrievalBatch | list[RetrievedSource],
        *,
        corpus_version: str,
        course_pack_version: str | None,
    ) -> tuple[list[RetrievedSource], str, str | None]:
        if not isinstance(retrieval_batch, RetrievalBatch):
            if self.settings.retrieval_mode == "local_corpus":
                raise ContractConflict(
                    "local corpus retrieval returned an unversioned candidate set"
                )
            return list(retrieval_batch), corpus_version, course_pack_version
        resolved_corpus_version = retrieval_batch.corpus_version
        resolved_course_pack_version = retrieval_batch.course_pack_version
        _validate_version_binding(
            resolved_corpus_version,
            resolved_course_pack_version,
            require_course_pack=self.settings.retrieval_mode == "local_corpus",
        )
        return (
            list(retrieval_batch.sources),
            resolved_corpus_version,
            resolved_course_pack_version,
        )

    def _resolve_rewrite_batch(
        self,
        retrieval_batch: RetrievalBatch | list[RetrievedSource],
        *,
        corpus_version: str,
        course_pack_version: str | None,
    ) -> list[RetrievedSource]:
        if isinstance(retrieval_batch, RetrievalBatch):
            if (
                retrieval_batch.corpus_version != corpus_version
                or retrieval_batch.course_pack_version != course_pack_version
            ):
                raise ContractConflict("query rewrite retrieval changed corpus version")
            return list(retrieval_batch.sources)
        if self.settings.retrieval_mode == "local_corpus":
            raise ContractConflict(
                "local corpus query rewrite returned an unversioned candidate set"
            )
        return list(retrieval_batch)

    def _append_retrieval_trace(
        self, *, sources: list[RetrievedSource], started: float
    ) -> None:
        retrieval_node = (
            "local_corpus_retrieval"
            if self.settings.retrieval_mode == "local_corpus"
            else "fixture_retrieval"
        )
        self.trace(
            node=retrieval_node,
            duration_ms=_elapsed_ms(started),
            result={
                **(
                    {"mode": "synthetic_fixture_only"}
                    if self.settings.retrieval_mode == "fixture"
                    else {}
                ),
                "hit_count": len(sources),
                "candidate_order": [f"S{index}" for index in range(1, len(sources) + 1)],
                "sources": [
                    {
                        "course_id": source.course_id,
                        "title": source.source_title,
                        "locator": source.locator_start,
                    }
                    for source in sources
                ],
            },
        )
        self.trace(
            node="source_authorization_guard",
            result={"candidate_count": len(sources), "accepted_count": len(sources)},
        )
        self.trace(
            node="cache_policy",
            status=TraceEventStatus.SKIPPED,
            result={"cache_hit": False, "reason_code": "runtime_cache_not_configured"},
        )


def _validate_version_binding(
    corpus_version: object,
    course_pack_version: object,
    *,
    require_course_pack: bool,
) -> None:
    if (
        not isinstance(corpus_version, str)
        or not corpus_version.strip()
        or (
            course_pack_version is not None
            and (
                not isinstance(course_pack_version, str)
                or not course_pack_version.strip()
            )
        )
    ):
        raise ContractConflict("retrieval returned an invalid corpus version binding")
    if require_course_pack and course_pack_version is None:
        raise ContractConflict("local corpus retrieval returned no course pack version")


def _assert_authorized_sources(
    sources: list[RetrievedSource], course_ids: list[str]
) -> None:
    if any(source.course_id not in course_ids for source in sources):
        raise ContractConflict(
            "source authorization guard rejected a source outside the selected courses"
        )


def dedupe_sources(sources: list[RetrievedSource]) -> list[RetrievedSource]:
    """Keep the first occurrence of each chunk in the evidence ledger."""

    seen: set[str] = set()
    unique: list[RetrievedSource] = []
    for source in sources:
        chunk_id = getattr(source, "chunk_id", None)
        if not isinstance(chunk_id, str) or not chunk_id:
            unique.append(source)
            continue
        if chunk_id in seen:
            continue
        seen.add(chunk_id)
        unique.append(source)
    return unique


def _select_relevant_private_sources(
    query: str, sources: list[RetrievedSource], *, limit: int = 3
) -> list[RetrievedSource]:
    """Keep private notes within the shared evidence budget by lexical overlap.

    Private notes remain user-owned, non-authoritative evidence.  This small
    deterministic filter is intentionally separate from the course-corpus
    ranker and never indexes conversation history or other users' material.
    """

    query_pairs = _meaningful_pairs(query)
    if not query_pairs:
        return []
    scored: list[tuple[int, int, RetrievedSource]] = []
    for index, source in enumerate(sources):
        source_pairs = _meaningful_pairs(f"{source.source_title} {source.text}")
        overlap = len(query_pairs & source_pairs)
        if overlap:
            scored.append((overlap, -index, source))
    scored.sort(reverse=True, key=lambda item: (item[0], item[1]))
    return [source for _, _, source in scored[:limit]]


def _meaningful_pairs(text: str) -> set[str]:
    compact = re.sub(r"\s+", "", text.casefold())
    return {
        compact[index : index + 2]
        for index in range(len(compact) - 1)
        if compact[index : index + 2].strip()
    }


_CONTEXT_CARRY_QUERY_CHARS = 1_200
_CONTEXT_CARRY_USER_TURNS = 2
_FOLLOWUP_REFERENCE_RE = re.compile(
    r"(?:这道题|上一题|上题|这一步|上一步|第二步|第[一二三四五六七八九十0-9]+步|"
    r"这个条件|上述条件|继续讲|重新讲|接着讲|第二种情况)"
)


def is_followup_reference_query(query: str) -> bool:
    """Identify explicit references that benefit from the prior question anchor."""

    return bool(_FOLLOWUP_REFERENCE_RE.search(query))


def compose_context_carry_query(
    current_query: str, history: tuple[ConversationTurn, ...]
) -> str:
    """Prepend bounded prior user turns to a follow-up retrieval query."""

    prior = [
        turn.content[:400]
        for turn in reversed(history)
        if turn.role == "user" and turn.content.strip()
    ][-_CONTEXT_CARRY_USER_TURNS:]
    if not prior:
        return ""
    return " ".join([*reversed(prior), current_query])[:_CONTEXT_CARRY_QUERY_CHARS].strip()


def compose_agent_rewrite_query(
    current_query: str,
    history: tuple[ConversationTurn, ...],
    course_title: str,
) -> str:
    """Build the bounded query executed when the model selects rewrite."""

    base = compose_context_carry_query(current_query, history) or current_query
    return f"{course_title} {base} 核心概念 典型题 易错点"[:_CONTEXT_CARRY_QUERY_CHARS].strip()


def _elapsed_ms(started: float) -> int:
    return max(int((perf_counter() - started) * 1000), 0)
