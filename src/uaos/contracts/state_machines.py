from __future__ import annotations

from dataclasses import replace

from .enums import ActionStatus, KnowledgeState
from .models import ActionRecord, KnowledgeItem

_ACTION_TRANSITIONS = {
    ActionStatus.PREPARED: frozenset({ActionStatus.SENT, ActionStatus.FAILED}),
    ActionStatus.SENT: frozenset({ActionStatus.CONFIRMED, ActionStatus.UNKNOWN, ActionStatus.FAILED}),
    ActionStatus.UNKNOWN: frozenset({ActionStatus.RECONCILED}),
    ActionStatus.RECONCILED: frozenset({ActionStatus.CONFIRMED, ActionStatus.FAILED, ActionStatus.COMPENSATED}),
    ActionStatus.CONFIRMED: frozenset({ActionStatus.COMPENSATED}),
    ActionStatus.FAILED: frozenset(),
    ActionStatus.COMPENSATED: frozenset(),
}


def transition_action(action: ActionRecord, to_status: ActionStatus, *, provider_ref: str | None = None, outcome: str | None = None) -> ActionRecord:
    if to_status not in _ACTION_TRANSITIONS[action.status]:
        raise ValueError(f"invalid action transition: {action.status} -> {to_status}")
    return replace(action, status=to_status, provider_ref=provider_ref or action.provider_ref, outcome=outcome)

_KNOWLEDGE_TRANSITIONS = {
    KnowledgeState.RAW_EVIDENCE: frozenset({KnowledgeState.CANDIDATE, KnowledgeState.RETIRED}),
    KnowledgeState.CANDIDATE: frozenset({KnowledgeState.EVALUATED, KnowledgeState.RETIRED}),
    KnowledgeState.EVALUATED: frozenset({KnowledgeState.CANONICAL, KnowledgeState.RETIRED}),
    KnowledgeState.CANONICAL: frozenset({KnowledgeState.RETIRED}),
    KnowledgeState.RETIRED: frozenset(),
}


def transition_knowledge(item: KnowledgeItem, to_state: KnowledgeState, *, usage_links: tuple[str, ...] | None = None) -> KnowledgeItem:
    if to_state not in _KNOWLEDGE_TRANSITIONS[item.state]:
        raise ValueError(f"invalid knowledge transition: {item.state} -> {to_state}")
    updated = replace(
        item,
        state=to_state,
        usage_links=usage_links if usage_links is not None else item.usage_links,
    )
    if to_state is KnowledgeState.CANONICAL and not updated.usage_links:
        raise ValueError("canonical knowledge requires at least one validated usage/evaluation link")
    return updated
