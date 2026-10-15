from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .deliberation import RootScopeReceipt


class ProblemClosureError(RuntimeError):
    """Raised when a detected problem is being acted on/finalized without an admissible closure."""


class ProblemClosureDecision(str, Enum):
    CLEAN_NO_PROBLEM = "CLEAN_NO_PROBLEM"
    REPAIR_NOW = "REPAIR_NOW"
    REPAIR_EXECUTED = "REPAIR_EXECUTED"
    BLOCKED_WITH_REASON = "BLOCKED_WITH_REASON"
    NO_CHANGE_WITH_EVIDENCE = "NO_CHANGE_WITH_EVIDENCE"


class EvolutionDisposition(str, Enum):
    LOCAL_LEARNING_ONLY = "LOCAL_LEARNING_ONLY"
    NO_DURABLE_EVOLUTION_WITH_EVIDENCE = "NO_DURABLE_EVOLUTION_WITH_EVIDENCE"
    DURABLE_EVOLUTION_CANDIDATE = "DURABLE_EVOLUTION_CANDIDATE"
    DURABLE_EVOLUTION_UPDATED = "DURABLE_EVOLUTION_UPDATED"
    PARENT_OR_COMMON_UPCALL = "PARENT_OR_COMMON_UPCALL"


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
    root_scope_receipt: RootScopeReceipt | None = None
    evolution_disposition: EvolutionDisposition | None = None
    problem_record_required: bool = False
    problem_record_ref: str | None = None


def _present(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _durable_record_required(signals: ProblemClosureSignals) -> bool:
    receipt_requires = bool(
        signals.root_scope_receipt
        and signals.root_scope_receipt.durable_problem_record_required
    )
    # Backward-compatible callers may request stronger evidence, but cannot weaken
    # the requirement already derived by root-scope admission.
    return receipt_requires or signals.problem_record_required


def _require_cognition_and_learning(signals: ProblemClosureSignals) -> None:
    if signals.root_scope_receipt is None:
        raise ProblemClosureError(
            "problem action blocked: root-scope cognitive admission is missing"
        )
    if not isinstance(signals.evolution_disposition, EvolutionDisposition):
        raise ProblemClosureError(
            "problem action blocked: a valid evolution/learning disposition is missing"
        )
    if _durable_record_required(signals) and not _present(signals.problem_record_ref):
        raise ProblemClosureError(
            "problem action blocked: material/evolution-relevant problem requires durable problem evidence"
        )


def assess_problem_closure(signals: ProblemClosureSignals) -> ProblemClosureDecision:
    """Classify the next admissible action for a detected problem.

    Finding a feasible edit is not cognitive admission. A repair/no-change decision may
    execute only after deliberation has produced an evidence-tested root-scope receipt and
    the problem has been assessed for durable learning/evolution. Obvious external blockers
    may still be surfaced without pretending the root cause has been established.
    """

    if not signals.problem_detected:
        return ProblemClosureDecision.CLEAN_NO_PROBLEM

    if signals.user_choice_required or _present(signals.hard_blocker):
        if _durable_record_required(signals) and not _present(signals.problem_record_ref):
            raise ProblemClosureError(
                "material blocked problem requires durable problem evidence before handoff"
            )
        return ProblemClosureDecision.BLOCKED_WITH_REASON

    if signals.repair_attempted:
        _require_cognition_and_learning(signals)
        if signals.repair_verified:
            return ProblemClosureDecision.REPAIR_EXECUTED
        raise ProblemClosureError(
            "repair was attempted but not verified; preserve failure evidence or convert to an explicit blocker/no-change disposition"
        )

    if _present(signals.no_change_reason):
        _require_cognition_and_learning(signals)
        return ProblemClosureDecision.NO_CHANGE_WITH_EVIDENCE

    if signals.repair_path_available and signals.repair_authorized:
        _require_cognition_and_learning(signals)
        return ProblemClosureDecision.REPAIR_NOW

    raise ProblemClosureError(
        "detected problem has no admissible terminal disposition: establish root scope and learning disposition, then provide an authorized repair path, explicit blocker/user-choice requirement, or evidence-backed no-change reason"
    )


def require_problem_finalization_admission(signals: ProblemClosureSignals) -> ProblemClosureDecision:
    """Reject recommendation-only finalization when a cognitively admitted repair can run now."""

    decision = assess_problem_closure(signals)
    if decision is ProblemClosureDecision.REPAIR_NOW:
        raise ProblemClosureError(
            "recommendation-only finalization is forbidden: an authorized cognitively-admitted repair path is available and must be attempted before closing the turn"
        )
    return decision
