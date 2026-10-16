from __future__ import annotations

from dataclasses import dataclass, replace

from uaos.kernel.cognition_case import (
    CognitionCase,
    CognitionCaseAdmissionError,
    EvidenceKind,
    EvidenceItem,
    require_cognition_case_admission,
)
from uaos.kernel.deep_task import (
    DeepTaskAdmissionError,
    DeepTaskCase,
    DeepTaskReceipt,
    require_deep_task_admission,
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
    """Evidence supplied by the runtime before a response may be finalized."""

    context_selected: bool
    problem_signal_observed: bool = False
    user_input_required: bool = False
    work_remaining_without_user_input: bool = False
    cognition_case: CognitionCase | None = None
    closure_signals: ProblemClosureSignals | None = None
    deep_task_required: bool = False
    deep_task_case: DeepTaskCase | None = None


@dataclass(frozen=True, slots=True)
class FinalizationReceipt:
    closure_decision: ProblemClosureDecision
    adherence: SessionAdherenceResult
    deep_task_receipt: DeepTaskReceipt | None = None


def _blocked_before_cognition(signals: ProblemClosureSignals) -> bool:
    return bool(signals.user_choice_required or (signals.hard_blocker and signals.hard_blocker.strip()))


def _validate_method_evidence(
    *,
    refs: tuple[str, ...],
    evidence_by_id: dict[str, EvidenceItem],
    allowed_kinds: set[EvidenceKind],
    planned_methods: tuple[str, ...],
    label: str,
    require_complete_coverage: bool,
) -> None:
    observed_methods: set[str] = set()
    for ref in refs:
        item = evidence_by_id.get(ref)
        if item is None:
            raise FinalizationBlocked(f"UNKNOWN_{label.upper()}_EVIDENCE:{ref}")
        if item.kind not in allowed_kinds:
            raise FinalizationBlocked(
                f"INVALID_{label.upper()}_EVIDENCE_KIND:{ref}:{item.kind.value}"
            )
        if item.method_ref is None:
            raise FinalizationBlocked(f"UNBOUND_{label.upper()}_EVIDENCE_METHOD:{ref}")
        if item.method_ref not in planned_methods:
            raise FinalizationBlocked(
                f"UNPLANNED_{label.upper()}_EVIDENCE_METHOD:{ref}:{item.method_ref}"
            )
        observed_methods.add(item.method_ref)
    if require_complete_coverage:
        missing = tuple(method for method in planned_methods if method not in observed_methods)
        if missing:
            raise FinalizationBlocked(
                f"MISSING_{label.upper()}_METHOD_EVIDENCE:" + ",".join(missing)
            )


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

    _validate_method_evidence(
        refs=closure.verification_evidence_refs,
        evidence_by_id=evidence_by_id,
        allowed_kinds=verification_kinds,
        planned_methods=receipt.verification_methods,
        label="verification",
        require_complete_coverage=bool(closure.repair_attempted and closure.repair_verified),
    )
    _validate_method_evidence(
        refs=closure.validation_evidence_refs,
        evidence_by_id=evidence_by_id,
        allowed_kinds=validation_kinds,
        planned_methods=receipt.validation_methods,
        label="validation",
        require_complete_coverage=bool(
            closure.repair_attempted
            and closure.repair_verified
            and receipt.systemic
        ),
    )

    return replace(closure, cognition_case_receipt=receipt)


def _bind_and_validate_deep_task(
    case: DeepTaskCase,
    cognition_case: CognitionCase | None,
) -> DeepTaskReceipt:
    try:
        receipt = require_deep_task_admission(case)
    except (DeepTaskAdmissionError, RuntimeError, ValueError) as exc:
        raise FinalizationBlocked(f"DEEP_TASK_NOT_ADMITTED: {exc}") from exc

    if cognition_case is not None:
        if case.governing_outcome != cognition_case.engineering_trace.governing_outcome:
            raise FinalizationBlocked(
                "DEEP_TASK_AND_COGNITION_OUTCOME_DISAGREE"
            )
        cognition_evidence = {
            item.evidence_id: (item.kind, item.source_ref, item.method_ref)
            for item in cognition_case.evidence_items
        }
        for item in case.evidence_items:
            expected = cognition_evidence.get(item.evidence_id)
            if expected is None:
                raise FinalizationBlocked(
                    f"DEEP_TASK_EVIDENCE_NOT_BOUND_TO_COGNITION:{item.evidence_id}"
                )
            observed = (item.kind, item.source_ref, item.method_ref)
            if expected != observed:
                raise FinalizationBlocked(
                    f"DEEP_TASK_EVIDENCE_CONTRADICTS_COGNITION:{item.evidence_id}"
                )
    return receipt


def admit_final_response(response: str, context: FinalizationContext) -> FinalizationReceipt:
    """Fail closed when an actionable or explicitly deep response is finalized prematurely.

    Controlled runtimes recompute cognition admission from the full case, bind terminal
    closure to the admitted intervention, require V&V evidence to identify the exact
    methods planned before execution, and require an evidence-complete DeepTaskCase when
    the runtime classifies the task as explicitly deep. Native hosts that do not invoke
    this gate remain outside the physical complete-mediation claim.
    """

    if context.work_remaining_without_user_input and not context.user_input_required:
        raise FinalizationBlocked("ACTIONABLE_WORK_REMAINS_WITHOUT_USER_INPUT")

    deep_task_receipt: DeepTaskReceipt | None = None
    if context.deep_task_required and not context.user_input_required:
        if context.deep_task_case is None:
            raise FinalizationBlocked("MISSING_DEEP_TASK_EVIDENCE_CASE")
        deep_task_receipt = _bind_and_validate_deep_task(
            context.deep_task_case,
            context.cognition_case if context.problem_signal_observed else None,
        )
    elif context.deep_task_case is not None and not context.deep_task_required:
        raise FinalizationBlocked("UNEXPECTED_DEEP_TASK_CASE_WITHOUT_DEEP_TASK_REQUIREMENT")

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
        deep_task_receipt=deep_task_receipt,
    )
