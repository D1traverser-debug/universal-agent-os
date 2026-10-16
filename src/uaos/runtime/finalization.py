from __future__ import annotations

from dataclasses import dataclass, replace

from uaos.kernel.cognition_case import (
    CognitionCase,
    CognitionCaseAdmissionError,
    EvidenceKind,
    require_cognition_case_admission,
)
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

    For a detected problem that is not blocked before cognition, controlled runtimes
    must supply the complete evidence-traced CognitionCase. The finalization seam
    recomputes admission from that case; callers cannot satisfy cognition by handing
    the gate a precomputed receipt. `work_remaining_without_user_input` remains a
    runtime fact, not a phrase inferred from the response.
    """

    context_selected: bool
    problem_signal_observed: bool = False
    user_input_required: bool = False
    work_remaining_without_user_input: bool = False
    cognition_case: CognitionCase | None = None
    closure_signals: ProblemClosureSignals | None = None


@dataclass(frozen=True, slots=True)
class FinalizationReceipt:
    closure_decision: ProblemClosureDecision
    adherence: SessionAdherenceResult


def _blocked_before_cognition(signals: ProblemClosureSignals) -> bool:
    return bool(signals.user_choice_required or (signals.hard_blocker and signals.hard_blocker.strip()))


def _bind_and_validate_cognition_case(
    closure: ProblemClosureSignals,
    case: CognitionCase,
) -> ProblemClosureSignals:
    try:
        receipt = require_cognition_case_admission(case)
    except (CognitionCaseAdmissionError, RuntimeError, ValueError) as exc:
        raise FinalizationBlocked(f"COGNITION_CASE_NOT_ADMITTED: {exc}") from exc

    evidence_by_id = {item.evidence_id: item for item in case.evidence_items}
    verification_kinds = {
        EvidenceKind.REPOSITORY_FACT,
        EvidenceKind.TOOL_RESULT,
        EvidenceKind.TEST_RESULT,
        EvidenceKind.RUNTIME_OBSERVATION,
        EvidenceKind.SCENARIO_RESULT,
        EvidenceKind.ANALYSIS_RESULT,
    }
    validation_kinds = {
        EvidenceKind.TEST_RESULT,
        EvidenceKind.RUNTIME_OBSERVATION,
        EvidenceKind.SCENARIO_RESULT,
        EvidenceKind.TOOL_RESULT,
    }

    for ref in closure.verification_evidence_refs:
        item = evidence_by_id.get(ref)
        if item is None:
            raise FinalizationBlocked(f"UNKNOWN_VERIFICATION_EVIDENCE:{ref}")
        if item.kind not in verification_kinds:
            raise FinalizationBlocked(f"INVALID_VERIFICATION_EVIDENCE_KIND:{ref}:{item.kind.value}")
    for ref in closure.validation_evidence_refs:
        item = evidence_by_id.get(ref)
        if item is None:
            raise FinalizationBlocked(f"UNKNOWN_VALIDATION_EVIDENCE:{ref}")
        if item.kind not in validation_kinds:
            raise FinalizationBlocked(f"INVALID_VALIDATION_EVIDENCE_KIND:{ref}:{item.kind.value}")

    return replace(closure, cognition_case_receipt=receipt)


def admit_final_response(response: str, context: FinalizationContext) -> FinalizationReceipt:
    """Fail closed when an actionable response is being finalized prematurely.

    This is the controlled-runtime enforcement seam. It recomputes cognition admission
    from the full problem case, composes that receipt with problem closure, and then
    checks user-visible session adherence. The assurance applies only to hosts that
    actually invoke this gate; native product hosts without a verified pre-send hook
    remain outside physical complete mediation.
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

        if not _blocked_before_cognition(closure):
            if context.cognition_case is None:
                raise FinalizationBlocked("MISSING_EVIDENCE_TRACED_COGNITION_CASE")
            closure = _bind_and_validate_cognition_case(closure, context.cognition_case)

        try:
            closure_decision = require_problem_finalization_admission(closure)
        except ProblemClosureError as exc:
            raise FinalizationBlocked(f"PROBLEM_CLOSURE_NOT_ADMITTED: {exc}") from exc
    elif closure is not None and closure.problem_detected:
        raise FinalizationBlocked("CLEAN_TURN_AND_CLOSURE_STATE_DISAGREE")
    elif context.cognition_case is not None:
        raise FinalizationBlocked("CLEAN_TURN_MUST_NOT_CARRY_PROBLEM_COGNITION_CASE")

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
        cognition_case_receipt=closure.cognition_case_receipt if closure is not None else None,
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
