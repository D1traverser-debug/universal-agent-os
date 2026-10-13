from __future__ import annotations
from dataclasses import dataclass
from .context import ContextPacket


@dataclass(frozen=True, slots=True)
class ContextBudget:
    max_artifact_refs: int = 32
    max_knowledge_items: int = 32
    max_unresolved_obligations: int = 32
    max_approvals: int = 16

    def __post_init__(self) -> None:
        if min(self.max_artifact_refs, self.max_knowledge_items, self.max_unresolved_obligations, self.max_approvals) < 0:
            raise ValueError("context budget values cannot be negative")


def validate_context_budget(packet: ContextPacket, budget: ContextBudget) -> None:
    checks = (
        ("artifact refs", len(packet.artifact_refs), budget.max_artifact_refs),
        ("knowledge items", len(packet.knowledge_ids), budget.max_knowledge_items),
        ("unresolved obligations", len(packet.unresolved_obligations), budget.max_unresolved_obligations),
        ("approvals", len(packet.approval_ids), budget.max_approvals),
    )
    exceeded = [f"{name}: {actual}>{limit}" for name, actual, limit in checks if actual > limit]
    if exceeded:
        raise ValueError("context budget exceeded: " + "; ".join(exceeded))
