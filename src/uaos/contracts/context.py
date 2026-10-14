from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    snapshot_id: str
    source_uri: str
    content_hash: str
    observed_at: datetime
    storage_uri: str
    media_type: str = "application/octet-stream"
    content_max_available_at: datetime | None = None
    completeness: str = "UNKNOWN"
    gaps: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all((self.snapshot_id.strip(), self.source_uri.strip(), self.content_hash.strip(), self.storage_uri.strip())):
            raise ValueError("snapshot identity, source, hash and storage are required")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.content_max_available_at is not None:
            if self.content_max_available_at.tzinfo is None:
                raise ValueError("content_max_available_at must be timezone-aware")
            if self.content_max_available_at > self.observed_at:
                raise ValueError("content_max_available_at cannot be after observation")
        if self.completeness not in {"FULL", "PARTIAL", "UNKNOWN"}:
            raise ValueError("invalid completeness")
        if self.completeness == "FULL" and self.gaps:
            raise ValueError("FULL snapshot cannot declare gaps")

    def assert_usable_for(self, freeze_at: datetime, *, require_full: bool = True) -> None:
        if freeze_at.tzinfo is None:
            raise ValueError("freeze_at must be timezone-aware")
        if self.content_max_available_at is None:
            raise ValueError("snapshot has no knowledge-availability boundary")
        if self.content_max_available_at > freeze_at:
            raise ValueError("snapshot contains information unavailable at freeze boundary")
        if require_full and self.completeness != "FULL":
            raise ValueError(f"snapshot completeness is {self.completeness}, not FULL")


@dataclass(frozen=True, slots=True)
class ProgressCursor:
    source_id: str
    source_hash: str
    position: str
    next_position: str | None
    coverage: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.coverage <= 1.0:
            raise ValueError("coverage must be between 0 and 1")

    def assert_source(self, source_id: str, source_hash: str) -> None:
        if self.source_id != source_id or self.source_hash != source_hash:
            raise ValueError("progress cursor source identity/hash mismatch")


@dataclass(frozen=True, slots=True)
class CompactionArtifact:
    compaction_id: str
    source_context_hash: str
    content_hash: str
    retained_obligations: tuple[str, ...]
    retained_approval_ids: tuple[str, ...]
    tool_result_pairs: tuple[tuple[str, str], ...]
    provenance_refs: tuple[str, ...]
    next_actions: tuple[str, ...]
    version: int = 1


@dataclass(frozen=True, slots=True)
class GovernanceFrame:
    """Minimum parent guidance needed to keep delegated work on the governing track."""

    parent_goal: str
    local_goal_link: str
    non_goals: tuple[str, ...] = ()
    invariants: tuple[str, ...] = ()
    autonomy_bounds: tuple[str, ...] = ()
    escalation_conditions: tuple[str, ...] = ()
    stop_conditions: tuple[str, ...] = ()
    verification_expectations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.parent_goal.strip() or not self.local_goal_link.strip():
            raise ValueError("parent_goal and local_goal_link are required")

    @property
    def item_count(self) -> int:
        return sum(
            len(items)
            for items in (
                self.non_goals,
                self.invariants,
                self.autonomy_bounds,
                self.escalation_conditions,
                self.stop_conditions,
                self.verification_expectations,
            )
        ) + 2


@dataclass(frozen=True, slots=True)
class ParentUpcall:
    """Child-to-parent guidance request that does not transfer child task ownership."""

    task_id: str
    child_authority: str
    problem_statement: str
    requested_outcome: str
    evidence_refs: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    current_hypothesis: str | None = None

    def __post_init__(self) -> None:
        if not all((self.task_id.strip(), self.child_authority.strip(), self.problem_statement.strip(), self.requested_outcome.strip())):
            raise ValueError("parent upcall requires task, child authority, problem and requested outcome")


@dataclass(frozen=True, slots=True)
class ParentGuidance:
    parent_authority: str
    task_id: str
    directive: str
    goal_link: str
    constraints: tuple[str, ...] = ()
    plan_changes: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    external_research_required: bool = False
    independent_verification_required: bool = False
    child_may_resume: bool = True

    def __post_init__(self) -> None:
        if not all((self.parent_authority.strip(), self.task_id.strip(), self.directive.strip(), self.goal_link.strip())):
            raise ValueError("parent guidance requires parent authority, task, directive and goal linkage")


@dataclass(frozen=True, slots=True)
class ContextPacket:
    task_id: str
    work_unit_id: str
    goal: str
    done_condition: str
    requirement_ids: tuple[str, ...]
    artifact_refs: tuple[str, ...]
    knowledge_ids: tuple[str, ...]
    unresolved_obligations: tuple[str, ...]
    approval_ids: tuple[str, ...]
    metadata: Mapping[str, str]
    governance: GovernanceFrame | None = None
