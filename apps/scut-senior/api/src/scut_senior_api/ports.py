from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from .contracts import (
    ConversationDetail,
    ConversationSummary,
    ExternalResource,
    WorkflowResult,
    WorkflowRunRequest,
)


class CapabilityUnavailable(RuntimeError):
    def __init__(self, capability: str, detail: str):
        super().__init__(detail)
        self.capability = capability
        self.detail = detail


@dataclass(frozen=True, slots=True)
class UserIdentity:
    user_id: str
    display_name: str
    is_mock: bool


@dataclass(frozen=True, slots=True)
class RetrievedSource:
    chunk_id: str
    course_id: str
    source_id: str
    source_title: str
    text: str
    locator_type: str
    locator_start: int | str | None
    locator_end: int | str | None
    question_id: str | None
    heading_path: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GeneratedAnswer:
    repository_answer: str
    related_topics: tuple[str, ...] = ()
    related_questions: tuple[str, ...] = ()


class IdentityProvider(Protocol):
    def current_user(self) -> UserIdentity: ...


class RetrievalGateway(Protocol):
    def search(self, course_ids: list[str], query: str) -> list[RetrievedSource]: ...


class ModelGateway(Protocol):
    def generate(
        self, request: WorkflowRunRequest, sources: list[RetrievedSource]
    ) -> GeneratedAnswer: ...


class ExternalResourceCatalog(Protocol):
    @property
    def catalog_version(self) -> str: ...

    def match(
        self, course_id: str, query: str, limit: int = 3
    ) -> list[ExternalResource]: ...


class WorkflowRepository(Protocol):
    def create_conversation(
        self, user_id: str, course_id: str
    ) -> ConversationSummary: ...

    def get_conversation(
        self, user_id: str, conversation_id: UUID
    ) -> ConversationDetail | None: ...

    def save_run(
        self, user_id: str, request: WorkflowRunRequest, result: WorkflowResult
    ) -> None: ...

    def get_run(self, user_id: str, run_id: UUID) -> WorkflowResult | None: ...


class VectorIndex(Protocol):
    def search(self, *_: object, **__: object) -> list[object]: ...


class ObjectStore(Protocol):
    def put(self, *_: object, **__: object) -> str: ...


class TaskQueue(Protocol):
    def enqueue(self, *_: object, **__: object) -> str: ...


class ContributionPublisher(Protocol):
    def create_pull_request(self, *_: object, **__: object) -> str: ...


class DisabledCapability:
    """Explicit placeholder for iteration-0 choices that remain unconfirmed."""

    def __init__(self, capability: str):
        self.capability = capability

    def __getattr__(self, _: str) -> object:
        raise CapabilityUnavailable(
            self.capability,
            f"{self.capability} is disabled until its decision gate is confirmed",
        )

