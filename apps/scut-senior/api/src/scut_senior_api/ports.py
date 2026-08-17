from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol
from uuid import UUID

from .contracts import (
    AnswerBlock,
    ConversationDetail,
    ConversationSummary,
    ExternalResource,
    WorkflowAttempt,
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
class RetrievalBatch:
    """One request-local, version-bound set of validated retrieval candidates."""

    sources: tuple[RetrievedSource, ...]
    corpus_version: str
    course_pack_version: str | None = None


@dataclass(frozen=True, slots=True)
class GeneratedAnswer:
    repository_answer: str
    related_topics: tuple[str, ...] = ()
    related_questions: tuple[str, ...] = ()
    bilibili_search_keywords: tuple[str, ...] = ()
    citation_ids: tuple[str, ...] = ()
    general_supplement: str = ""
    user_material_answer: str = ""
    personalized_analysis: str = ""


class HumanizerGateway(Protocol):
    def humanize(
        self,
        *,
        blocks: list[AnswerBlock],
        protected_terms: tuple[str, ...],
    ) -> list[AnswerBlock]: ...


@dataclass(frozen=True, slots=True)
class StoredModelCredential:
    user_id: UUID
    auth_session_id: UUID
    provider_id: str
    ciphertext: bytes = field(repr=False)
    nonce: bytes = field(repr=False)
    algorithm: str
    key_version: int
    expires_at: datetime


class IdentityProvider(Protocol):
    def current_user(self) -> UserIdentity: ...


class RetrievalGateway(Protocol):
    def is_course_available(self, course_id: str) -> bool: ...

    def search(self, course_ids: list[str], query: str) -> RetrievalBatch: ...


class ModelGateway(Protocol):
    def generate(
        self, request: WorkflowRunRequest, sources: list[RetrievedSource]
    ) -> GeneratedAnswer: ...


class UserKeyModelGateway(Protocol):
    def generate(
        self,
        *,
        api_key: str,
        request: WorkflowRunRequest,
        sources: list[RetrievedSource],
    ) -> GeneratedAnswer: ...


class ExternalResourceDiscovery(Protocol):
    def discover(
        self,
        *,
        course_id: str,
        course_title: str,
        keywords: tuple[str, ...],
    ) -> list[ExternalResource]: ...


class WorkflowRepository(Protocol):
    def create_conversation(
        self, user_id: str, course_id: str, title: str
    ) -> ConversationSummary: ...

    def list_conversations(self, user_id: str) -> list[ConversationSummary]: ...

    def get_conversation(
        self, user_id: str, conversation_id: UUID
    ) -> ConversationDetail | None: ...

    def rename_conversation(
        self, user_id: str, conversation_id: UUID, title: str
    ) -> ConversationSummary | None: ...

    def delete_conversation(self, user_id: str, conversation_id: UUID) -> bool: ...

    def save_run(
        self,
        user_id: str,
        request: WorkflowRunRequest,
        result: WorkflowResult,
        *,
        attempt_group_id: UUID | None = None,
        regenerated_from_run_id: UUID | None = None,
        auth_session_id: UUID | None = None,
    ) -> None: ...

    def get_run(self, user_id: str, run_id: UUID) -> WorkflowResult | None: ...

    def get_attempt(self, user_id: str, run_id: UUID) -> WorkflowAttempt | None: ...

    def discard_nonterminal_run(self, user_id: str, run_id: UUID) -> bool: ...


class ModelCredentialRepository(Protocol):
    def list_model_credentials(
        self, user_id: UUID, auth_session_id: UUID
    ) -> list[StoredModelCredential]: ...

    def get_model_credential(
        self, user_id: UUID, auth_session_id: UUID, provider_id: str
    ) -> StoredModelCredential | None: ...

    def upsert_model_credential(
        self,
        *,
        user_id: UUID,
        auth_session_id: UUID,
        provider_id: str,
        ciphertext: bytes,
        nonce: bytes,
        algorithm: str,
        key_version: int,
    ) -> StoredModelCredential: ...

    def delete_model_credential(
        self, user_id: UUID, auth_session_id: UUID, provider_id: str
    ) -> bool: ...

    def session_is_active(self, user_id: UUID, auth_session_id: UUID) -> bool: ...


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
