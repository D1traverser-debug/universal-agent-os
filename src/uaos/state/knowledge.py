from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Mapping

from uaos.contracts.context import CompactionArtifact, SourceSnapshot
from uaos.contracts.enums import KnowledgeState
from uaos.contracts.models import KnowledgeItem
from uaos.contracts.state_machines import transition_knowledge


def snapshot_bytes(
    *,
    snapshot_id: str,
    source_uri: str,
    content: bytes,
    storage_uri: str,
    media_type: str = "application/octet-stream",
    observed_at: datetime | None = None,
    content_max_available_at: datetime | None = None,
    completeness: str = "UNKNOWN",
    gaps: tuple[str, ...] = (),
    metadata: Mapping[str, str] | None = None,
) -> SourceSnapshot:
    return SourceSnapshot(
        snapshot_id=snapshot_id,
        source_uri=source_uri,
        content_hash=hashlib.sha256(content).hexdigest(),
        observed_at=observed_at or datetime.now(UTC),
        storage_uri=storage_uri,
        media_type=media_type,
        content_max_available_at=content_max_available_at,
        completeness=completeness,
        gaps=gaps,
        metadata=dict(metadata or {}),
    )


class KnowledgeCatalog:
    def __init__(self) -> None:
        self._items: dict[str, KnowledgeItem] = {}

    def add(self, item: KnowledgeItem) -> None:
        if not item.source_refs:
            raise ValueError("knowledge requires provenance")
        if item.knowledge_id in self._items:
            raise ValueError(f"duplicate knowledge_id: {item.knowledge_id}")
        self._items[item.knowledge_id] = item

    def get(self, knowledge_id: str) -> KnowledgeItem:
        return self._items[knowledge_id]

    def transition(self, knowledge_id: str, to_state: KnowledgeState, *, usage_links: tuple[str, ...] | None = None) -> KnowledgeItem:
        updated = transition_knowledge(self.get(knowledge_id), to_state, usage_links=usage_links)
        self._items[knowledge_id] = updated
        return updated

    def retrieve(self, *, scopes: set[str] | frozenset[str], include_candidate: bool = False) -> tuple[KnowledgeItem, ...]:
        allowed_states = {KnowledgeState.CANONICAL}
        if include_candidate:
            allowed_states.update({KnowledgeState.CANDIDATE, KnowledgeState.EVALUATED})
        return tuple(sorted(
            (
                item for item in self._items.values()
                if item.applicable_scope in scopes and item.state in allowed_states
            ),
            key=lambda item: item.knowledge_id,
        ))


def validate_compaction(
    artifact: CompactionArtifact,
    *,
    required_obligations: set[str] | frozenset[str],
    required_approval_ids: set[str] | frozenset[str],
    required_tool_result_pairs: set[tuple[str, str]] | frozenset[tuple[str, str]],
    required_provenance_refs: set[str] | frozenset[str],
) -> None:
    checks = (
        ("obligations", set(artifact.retained_obligations), set(required_obligations)),
        ("approvals", set(artifact.retained_approval_ids), set(required_approval_ids)),
        ("tool/result pairs", set(artifact.tool_result_pairs), set(required_tool_result_pairs)),
        ("provenance", set(artifact.provenance_refs), set(required_provenance_refs)),
    )
    for label, retained, required in checks:
        missing = required - retained
        if missing:
            raise ValueError(f"compaction lost required {label}: {sorted(missing)}")
