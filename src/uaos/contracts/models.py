from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Mapping

from .enums import (
    ActionStatus,
    ArtifactState,
    IntentType,
    KnowledgeState,
    Lane,
    RequirementState,
    ScopeType,
    TaskStatus,
    WorkStatus,
)


def utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class RequirementRecord:
    requirement_id: str
    content: str
    scope_type: ScopeType
    scope_id: str | None = None
    priority: int = 100
    lifecycle_state: RequirementState = RequirementState.ACTIVE
    supersedes: tuple[str, ...] = ()
    effective_from: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if not self.requirement_id.strip():
            raise ValueError("requirement_id is required")
        if not self.content.strip():
            raise ValueError("requirement content is required")
        if self.scope_type is ScopeType.GLOBAL and self.scope_id is not None:
            raise ValueError("GLOBAL requirement must not have scope_id")
        if self.scope_type is not ScopeType.GLOBAL and not self.scope_id:
            raise ValueError(f"{self.scope_type} requirement requires scope_id")
        if self.requirement_id in self.supersedes:
            raise ValueError("requirement cannot supersede itself")


@dataclass(frozen=True, slots=True)
class TaskRecord:
    task_id: str
    intent: IntentType
    owner_domain: str
    goal: str
    done_condition: str
    requirement_snapshot: tuple[str, ...]
    priority: int = 100
    status: TaskStatus = TaskStatus.PENDING
    current_stage: str = "CREATED"
    next_action: str | None = None
    workflow_id: str | None = None
    plan_version: int = 1
    completion_evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("task_id", self.task_id),
            ("owner_domain", self.owner_domain),
            ("goal", self.goal),
            ("done_condition", self.done_condition),
        ):
            if not value.strip():
                raise ValueError(f"{name} is required")
        if self.plan_version < 1:
            raise ValueError("plan_version must be >= 1")
        if self.status is TaskStatus.COMPLETE and not self.completion_evidence:
            raise ValueError("COMPLETE task requires completion_evidence")


@dataclass(frozen=True, slots=True)
class WorkUnit:
    work_unit_id: str
    task_id: str
    name: str
    dependencies: tuple[str, ...] = ()
    required_inputs: tuple[str, ...] = ()
    expected_outputs: tuple[str, ...] = ()
    executor_constraints: tuple[str, ...] = ()
    risk: str = "LOW"
    status: WorkStatus = WorkStatus.PENDING

    def __post_init__(self) -> None:
        if not self.work_unit_id.strip() or not self.task_id.strip() or not self.name.strip():
            raise ValueError("work_unit_id, task_id and name are required")
        if self.work_unit_id in self.dependencies:
            raise ValueError("work unit cannot depend on itself")


@dataclass(frozen=True, slots=True)
class Plan:
    plan_id: str
    task_id: str
    version: int
    work_units: tuple[WorkUnit, ...]
    external_inputs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.plan_id.strip() or not self.task_id.strip():
            raise ValueError("plan_id and task_id are required")
        if self.version < 1:
            raise ValueError("version must be >= 1")


@dataclass(frozen=True, slots=True)
class Approval:
    approval_id: str
    action_id: str
    target: str
    parameter_hash: str
    approver: str
    expires_at: datetime
    granted_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.expires_at <= self.granted_at:
            raise ValueError("approval expires_at must be after granted_at")

    def authorizes(self, *, action_id: str, target: str, parameter_hash: str, now: datetime | None = None) -> bool:
        now = now or utcnow()
        return now < self.expires_at and self.action_id == action_id and self.target == target and self.parameter_hash == parameter_hash


@dataclass(frozen=True, slots=True)
class ActionRecord:
    action_id: str
    work_unit_id: str
    capability_id: str
    request_hash: str
    target: str
    side_effect_class: str
    status: ActionStatus = ActionStatus.PREPARED
    idempotency_key: str | None = None
    approval_id: str | None = None
    attempt: int = 1
    provider_ref: str | None = None
    outcome: str | None = None

    def __post_init__(self) -> None:
        required = {"action_id": self.action_id, "work_unit_id": self.work_unit_id, "capability_id": self.capability_id, "request_hash": self.request_hash, "target": self.target, "side_effect_class": self.side_effect_class}
        for name, value in required.items():
            if not value.strip():
                raise ValueError(f"{name} is required")
        if self.attempt < 1:
            raise ValueError("attempt must be >= 1")


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    artifact_id: str
    kind: str
    version: int
    content_hash: str
    storage_uri: str
    producer_action: str | None = None
    lineage: tuple[str, ...] = ()
    state: ArtifactState = ArtifactState.DRAFT
    visibility_state: str = "INTERNAL"

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("artifact version must be >= 1")
        if not all((self.artifact_id, self.kind, self.content_hash, self.storage_uri)):
            raise ValueError("artifact identity, kind, hash and storage URI are required")


@dataclass(frozen=True, slots=True)
class KnowledgeItem:
    knowledge_id: str
    content: str
    source_refs: tuple[str, ...]
    applicable_scope: str
    state: KnowledgeState = KnowledgeState.RAW_EVIDENCE
    confidence: float = 0.0
    supersedes: tuple[str, ...] = ()
    usage_links: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.knowledge_id.strip() or not self.content.strip():
            raise ValueError("knowledge_id and content are required")
        if not self.source_refs:
            raise ValueError("knowledge requires source provenance")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0 and 1")
        if self.state is KnowledgeState.CANONICAL and self.confidence <= 0:
            raise ValueError("canonical knowledge requires positive confidence")


@dataclass(frozen=True, slots=True)
class CapabilityDescriptor:
    capability_id: str
    executor_kind: str
    supported_actions: tuple[str, ...]
    lane: Lane = Lane.PRODUCTION
    permissions: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)
