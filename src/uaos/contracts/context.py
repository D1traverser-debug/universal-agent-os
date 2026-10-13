from __future__ import annotations

from dataclasses import dataclass
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
