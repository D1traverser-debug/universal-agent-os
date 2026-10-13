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
