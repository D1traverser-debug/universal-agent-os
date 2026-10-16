from __future__ import annotations

from dataclasses import dataclass

from uaos.kernel.problem_closure import (
    ProblemClosureDecision,
    ProblemClosureError,
    ProblemClosureSignals,
    require_problem_finalization_admission,
)
from uaos.observability.session_adherence import (
    SessionAdherenceResult,
    SessionProgressExpectation,
    evaluate_session_progress_response,
)


class FinalizationBlocked(RuntimeError):
    """Raised when a candidate user-visible final response is not admissible."""

    def __init__(self, *reasons: str) -> None:
        self.reasons = tuple(reason for reason in reasons if reason)
        super().__init__("; ".join(self.reasons) or "finalization blocked")


@dataclass(frozen=True, slots=True)
class FinalizationContext:
    """Evidence supplied by the runtime before a response may be finalized.

    The gate composes existing owners rather than creating another cognition state
    machine: problem_closure owns problem terminal admission and session_adherence owns
    user-visible report consistency. `work_remaining_without_user_input` is a runtime
    fact, not a phrase inferred from the response.
    """

    context_selected: bool
    problem_signal_observed: bool = False
    user_input_required: bool = False
    work_remaining_without_user_input: bool = False
    closure_signals: ProblemClosureSignals | None = None


@dataclass(frozen=True, slots=True)
class FinalizationReceipt:
    closure_decision: ProblemClosureDecision
    adherence: SessionAdherenceResult


def _blocked_before_cognition(signals: ProblemClosureSignals) -> bool:
    return bool(signals.user_choice_required or (signals.hard_blocker and signals.hard_blocker.strip()))


def admit_final_response(response: str, context: FinalizationContext) -> FinalizationReceipt:
    """Fail closed when an actionable response is being finalized prematurely.

    This is the runtime enforcement seam. A host that invokes this function before
    emitting user-visible output gets a non-bypassable gate for that host path. It does
    not claim that every external host invokes the gate.
    """

    if context.work_remaining_without_user_input and not context.user_input_required:
        raise FinalizationBlocked("ACTIONABLE_WORK_REMAINS_WITHOUT_USER_INPUT")

    closure_decision = ProblemClosureDecision.CLEAN_NO_PROBLEM
    closure = context.closure_signals

    if context.problem_signal_observed:
        if closure is None:
            raise FinalizationBlocked("MISSING_PROBLEM_CLOSURE_SIGNALS")
        if not closure.problem_detected:
            raise FinalizationBlocked("PROBLEM_SIGNAL_AND_CLOSURE_STATE_DISAGREE")
        if context.user_input_required and not closure.user_choice_required:
            raise FinalizationBlocked("USER_INPUT_REQUIREMENT_AND_CLOSURE_STATE_DISAGREE")
        try:
            closure_decision = require_problem_finalization_admission(closure)
        except ProblemClosureError as exc:
            raise FinalizationBlocked(f"PROBLEM_CLOSURE_NOT_ADMITTED: {exc}") from exc
    elif closure is not None and closure.problem_detected:
        raise FinalizationBlocked("CLEAN_TURN_AND_CLOSURE_STATE_DISAGREE")

    cognition_required = bool(
        context.problem_signal_observed
        and closure is not None
        and not _blocked_before_cognition(closure)
    )

    expectation = SessionProgressExpectation(
        context_selected=context.context_selected,
        problem_signal_observed=context.problem_signal_observed,
        user_input_required=context.user_input_required,
        no_op_continuation_disallowed=not context.user_input_required,
        cognition_admission_required=cognition_required,
        root_scope_receipt=closure.root_scope_receipt if closure is not None else None,
        evolution_disposition=closure.evolution_disposition if closure is not None else None,
        problem_record_ref=closure.problem_record_ref if closure is not None else None,
    )
    adherence = evaluate_session_progress_response(response, expectation)
    if not adherence.passed:
        reasons = tuple(f"SESSION_ADHERENCE:{item.value}" for item in adherence.violations)
        raise FinalizationBlocked(*reasons)

    return FinalizationReceipt(
        closure_decision=closure_decision,
        adherence=adherence,
    )
