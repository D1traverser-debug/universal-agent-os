from __future__ import annotations
from dataclasses import dataclass

from uaos.contracts.enums import ActionStatus
from uaos.contracts.models import ActionRecord


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    retry_owner: str
    max_attempts: int
    require_idempotency_for_side_effects: bool = True

    def __post_init__(self) -> None:
        if not self.retry_owner.strip():
            raise ValueError("retry_owner is required")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")


@dataclass(frozen=True, slots=True)
class RetryDecision:
    action: str
    allowed: bool
    reason: str


def assess_retry(action: ActionRecord, policy: RetryPolicy) -> RetryDecision:
    if action.status is ActionStatus.UNKNOWN:
        return RetryDecision("RECONCILE", False, "UNKNOWN outcome must be reconciled before any retry")
    if action.status is not ActionStatus.FAILED:
        return RetryDecision("NO_RETRY", False, f"action status {action.status} is not retryable")
    if action.attempt >= policy.max_attempts:
        return RetryDecision("STOP", False, "retry budget exhausted")
    if policy.require_idempotency_for_side_effects and action.side_effect_class.upper() != "READ" and not action.idempotency_key:
        return RetryDecision("STOP", False, "side-effect retry requires idempotency/deduplication evidence")
    return RetryDecision("RETRY", True, f"retry owned by {policy.retry_owner}")
