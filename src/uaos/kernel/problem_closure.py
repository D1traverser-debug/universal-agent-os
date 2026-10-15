from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProblemClosureError(RuntimeError):
    """Raised when a detected problem is being finalized without an admissible closure."""


class ProblemClosureDecision(str, Enum):
    CLEAN_NO_PROBLEM = "CLEAN_NO_PROBLEM"
    REPAIR_NOW = "REPAIR_NOW"
    REPAIR_EXECUTED = "REPAIR_EXECUTED"
    BLOCKED_WITH_REASON = "BLOCKED_WITH_REASON"
    NO_CHANGE_WITH_EVIDENCE = "NO_CHANGE_WITH_EVIDENCE"


@dataclass(frozen=True, slots=True)
class ProblemClosureSignals:
    problem_detected: bool
    repair_path_available: bool = False
    repair_authorized: bool = False
    repair_attempted: bool = False
    repair_verified: bool = False
    user_choice_required: bool = False
    hard_blocker: str | None = None
    no_change_reason: str | None = None


def _present(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


def assess_problem_closure(signals: ProblemClosureSignals) -> ProblemClosureDecision:
    """Classify the next admissible action for a detected problem.

    This is deliberately small: deliberation decides *what* repair is justified;
    this gate prevents the controller from stopping at recommendation-only when an
    authorized repair path is available. It does not claim host-level physical
    mediation of natural-language output.
    """

    if not signals.problem_detected:
        return ProblemClosureDecision.CLEAN_NO_PROBLEM

    if signals.repair_attempted and signals.repair_verified:
        return ProblemClosureDecision.REPAIR_EXECUTED

    if signals.user_choice_required or _present(signals.hard_blocker):
        return ProblemClosureDecision.BLOCKED_WITH_REASON

    if _present(signals.no_change_reason):
        return ProblemClosureDecision.NO_CHANGE_WITH_EVIDENCE

    if signals.repair_path_available and signals.repair_authorized:
        return ProblemClosureDecision.REPAIR_NOW

    if signals.repair_attempted:
        raise ProblemClosureError(
            "repair was attempted but neither verified nor converted into an explicit blocker/no-change disposition"
        )

    raise ProblemClosureError(
        "detected problem has no admissible terminal disposition: provide an authorized repair path, explicit blocker/user-choice requirement, or evidence-backed no-change reason"
    )


def require_problem_finalization_admission(signals: ProblemClosureSignals) -> ProblemClosureDecision:
    """Reject recommendation-only finalization when repair can be executed now."""

    decision = assess_problem_closure(signals)
    if decision is ProblemClosureDecision.REPAIR_NOW:
        raise ProblemClosureError(
            "recommendation-only finalization is forbidden: an authorized repair path is available and must be attempted before closing the turn"
        )
    return decision
