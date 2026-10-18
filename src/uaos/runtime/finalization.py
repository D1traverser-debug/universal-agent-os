from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Mapping

from uaos.contracts.models import KnowledgeItem

from .epistemic_entry import (
    ControllerEpistemicEntry,
    EntryAdmissionError,
    TurnEvolutionCoverage,
    admit_turn_evolution_coverage,
    assess_controller_epistemic_entry,
)

from uaos.kernel.cognition_case import (
    CognitionCase,
    CognitionCaseAdmissionError,
    EvidenceKind,
    EvidenceItem,
    require_cognition_case_admission,
)
from uaos.kernel.domain_health import (
    DomainObservation,
    ProductOutcomeEvidence,
    require_product_outcome_completion,
)
from uaos.kernel.deep_task import (
    DeepTaskAdmissionError,
    DeepTaskCase,
    DeepTaskReceipt,
    DeepTaskSignals,
    assess_deep_task_requirement,
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
class PermittedContinuationStep:
    """Host-observed, independently authorized work after one blocked operation.

    A safety-denied write can never be substituted with a differently named write.
    Reference verification belongs to the controlled host, not the model text.
    """
    action_ref: str
    admission_ref: str
    read_only: bool
    attempted: bool = False
    outcome_evidence_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.action_ref.strip() or not self.admission_ref.strip():
            raise ValueError("continuation action requires source-backed authority")
        if self.attempted != bool(self.outcome_evidence_ref):
            raise ValueError("continuation attempt and outcome evidence must agree")


@dataclass(frozen=True, slots=True)
class BlockedOperationContinuity:
    """Evidence to evaluate whether a *specific* operation block truly ends work."""
    blocked_operation_ref: str
    blocker_evidence_ref: str
    checkpoint_ref: str
    safety_denial: bool
    remaining_permitted_steps: tuple[PermittedContinuationStep, ...] = ()

    def __post_init__(self) -> None:
        if not all((
            self.blocked_operation_ref.strip(),
            self.blocker_evidence_ref.strip(),
            self.checkpoint_ref.strip(),
        )):
            raise ValueError("blocked operation requires specific evidence and a resumable checkpoint")
        refs = [step.action_ref for step in self.remaining_permitted_steps]
        if len(refs) != len(set(refs)):
            raise ValueError("duplicate continuation step")


def _require_blocked_operation_continuity(
    case: BlockedOperationContinuity,
    evidence_verifier: Callable[[str], bool],
) -> None:
    refs = (
        case.blocked_operation_ref, case.blocker_evidence_ref, case.checkpoint_ref,
    )
    if not all(evidence_verifier(ref) for ref in refs):
        raise FinalizationBlocked("BLOCKED_OPERATION_EVIDENCE_UNVERIFIED")
    for step in case.remaining_permitted_steps:
        if not all(evidence_verifier(ref) for ref in (step.action_ref, step.admission_ref)):
            raise FinalizationBlocked("BLOCKED_OPERATION_ALTERNATIVE_NOT_ADMITTED")
        if case.safety_denial and not step.read_only:
            raise FinalizationBlocked("SAFETY_DENIED_MUTATION_MUST_NOT_BE_REROUTED")
        if not step.attempted:
            raise FinalizationBlocked("PERMITTED_INDEPENDENT_WORK_UNATTEMPTED")
        if not step.outcome_evidence_ref or not evidence_verifier(step.outcome_evidence_ref):
            raise FinalizationBlocked("PERMITTED_INDEPENDENT_WORK_OUTCOME_UNVERIFIED")


@dataclass(frozen=True, slots=True)
class FinalizationContext:
    """Evidence supplied by the runtime before a response may be finalized."""

    context_selected: bool
    problem_signal_observed: bool = False
    user_input_required: bool = False
    work_remaining_without_user_input: bool = False
    cognition_case: CognitionCase | None = None
    trusted_knowledge_resolver: Callable[[str], KnowledgeItem | None] | None = None
    closure_signals: ProblemClosureSignals | None = None
    deep_task_required: bool = False
    deep_task_signals: DeepTaskSignals | None = None
    deep_task_case: DeepTaskCase | None = None
    controller_selected: bool = False
    controller_epistemic_entry: ControllerEpistemicEntry | None = None
    entry_evidence_verifier: Callable[[str], bool] | None = None
    # Current-turn host enumeration + review, including user AND assistant words.
    # No new state/evolution owner; only a mandatory controlled boundary adapter.
    turn_evolution_coverage: TurnEvolutionCoverage | None = None
    observed_turn_source_refs: tuple[str, ...] | None = None
    turn_source_digest_verifier: Callable[[str, str], bool] | None = None
    turn_judgment_verifier: Callable[[str], bool] | None = None
    authoritative_task_ref: str | None = None
    read_authoritative_task: Callable[[str], Mapping[str, object] | None] | None = None
    blocked_tool_operation_observed: bool = False
    blocked_operation_continuity: BlockedOperationContinuity | None = None
    governed_product_outcome_completion_requested: bool = False
    governed_product_outcome_observation: DomainObservation | None = None
    governed_product_outcome_evidence: ProductOutcomeEvidence | None = None
    governed_product_outcome_verifier: Callable[[str], bool] | None = None


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
    *,
    trusted_knowledge_resolver: Callable[[str], KnowledgeItem | None] | None = None,
) -> ProblemClosureSignals:
    try:
        receipt = require_cognition_case_admission(case, resolve_trusted_knowledge=trusted_knowledge_resolver)
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


def _deep_task_required(context: FinalizationContext) -> bool:
    signal_required = False
    if context.deep_task_signals is not None:
        signal_required = assess_deep_task_requirement(context.deep_task_signals).required
    return bool(context.deep_task_required or signal_required)


def admit_final_response(response: str, context: FinalizationContext) -> FinalizationReceipt:
    """Fail closed when an actionable or explicitly deep response is finalized prematurely.

    Controlled runtimes recompute cognition admission from the full case, bind terminal
    closure to the admitted intervention, require V&V evidence to identify the exact
    methods planned before execution, and recompute deep-task activation from typed
    semantic signals when supplied. Native hosts that do not invoke this gate or do not
    supply current semantic signals remain outside the physical complete-mediation claim.
    """

    # Controlled UAOS route: a genuine entry receipt is required before the
    # existing cognition, Deep Task and finalization owners can close a turn.
    # Native ChatGPT is not physically intercepted by this repository code.
    if context.controller_selected:
        if not context.context_selected:
            raise FinalizationBlocked("CONTROLLER_ENTRY_WITHOUT_SELECTED_CONTEXT")
        if context.controller_epistemic_entry is None:
            raise FinalizationBlocked("MISSING_CONTROLLER_EPISTEMIC_ENTRY")
        if context.entry_evidence_verifier is None:
            raise FinalizationBlocked("MISSING_CONTROLLER_ENTRY_EVIDENCE_VERIFIER")
        entry_receipt = assess_controller_epistemic_entry(context.controller_epistemic_entry)
        refs = (
            *entry_receipt.evidence_refs,
            context.controller_epistemic_entry.objective_ref,
            context.controller_epistemic_entry.state_ref,
            context.controller_epistemic_entry.governing_assumption_review_ref,
            context.controller_epistemic_entry.next_action_ref,
        )
        if not all(context.entry_evidence_verifier(ref) for ref in refs):
            raise FinalizationBlocked("CONTROLLER_ENTRY_EVIDENCE_UNVERIFIED")
        if entry_receipt.problem_signal_observed and not context.problem_signal_observed:
            raise FinalizationBlocked("UNROUTED_RULE_OR_SYSTEM_CONTRADICTION")
        if entry_receipt.deep_learning_required and not _deep_task_required(context):
            raise FinalizationBlocked("UNROUTED_MATERIAL_KNOWLEDGE_GAP")
        if entry_receipt.work_remaining and not context.work_remaining_without_user_input:
            raise FinalizationBlocked("UNROUTED_UNFINISHED_AUTHORIZED_WORK")

    # When the controller's selected entry identifies an exact task, the
    # controlled host cannot skip task-to-visible-progress reconciliation by
    # omitting the resolver. Controller-root/index-only entries have no task.
    if context.controller_selected and context.controller_epistemic_entry is not None:
        exact_task_ref = context.controller_epistemic_entry.state_ref
        if exact_task_ref.startswith("state/tasks/"):
            if context.authoritative_task_ref != exact_task_ref:
                raise FinalizationBlocked("CONTROLLER_TASK_PROGRESS_SOURCE_NOT_BOUND")
            if context.read_authoritative_task is None:
                raise FinalizationBlocked("CONTROLLER_TASK_PROGRESS_READER_MISSING")

    # A tool-level block is an operation-local finding, never automatically a
    # task-global blocker. Continue independently authorized work, but do not
    # reroute safety-denied mutations through another tool/provider.
    if context.controller_selected and context.blocked_tool_operation_observed:
        if context.blocked_operation_continuity is None:
            raise FinalizationBlocked("MISSING_BLOCKED_OPERATION_CONTINUATION_EVIDENCE")
        if context.entry_evidence_verifier is None:
            raise FinalizationBlocked("MISSING_BLOCKED_OPERATION_EVIDENCE_VERIFIER")
        _require_blocked_operation_continuity(
            context.blocked_operation_continuity, context.entry_evidence_verifier
        )
    elif context.blocked_operation_continuity is not None:
        raise FinalizationBlocked("BLOCKED_OPERATION_EVIDENCE_WITHOUT_CONTROLLED_TRIGGER")

    # Product-outcome closure is a UAOS controller action. Technical CI success
    # and source-only receipts cannot certify a delivered reader/customer result.
    # This is enforced for controlled callers that explicitly attempt such closure;
    # native ChatGPT responses are not physically mediated by repository code.
    if context.governed_product_outcome_completion_requested:
        if not context.controller_selected:
            raise FinalizationBlocked("PRODUCT_OUTCOME_COMPLETION_REQUIRES_CONTROLLER_AUTHORITY")
        if (
            context.governed_product_outcome_observation is None
            or context.governed_product_outcome_evidence is None
        ):
            raise FinalizationBlocked("MISSING_CURRENT_PRODUCT_OUTCOME_EVIDENCE")
        try:
            require_product_outcome_completion(
                context.governed_product_outcome_observation,
                context.governed_product_outcome_evidence,
                verify_evidence=context.governed_product_outcome_verifier,
            )
        except ValueError as exc:
            raise FinalizationBlocked(f"PRODUCT_OUTCOME_NOT_VALIDATED: {exc}") from exc
    elif any((
        context.governed_product_outcome_observation is not None,
        context.governed_product_outcome_evidence is not None,
        context.governed_product_outcome_verifier is not None,
    )):
        raise FinalizationBlocked("UNSOLICITED_PRODUCT_OUTCOME_CLOSURE_EVIDENCE")

    if context.work_remaining_without_user_input and not context.user_input_required:
        raise FinalizationBlocked("ACTIONABLE_WORK_REMAINS_WITHOUT_USER_INPUT")

    deep_required = _deep_task_required(context)
    deep_task_receipt: DeepTaskReceipt | None = None
    if deep_required and not context.user_input_required:
        if context.deep_task_case is None:
            raise FinalizationBlocked("MISSING_DEEP_TASK_EVIDENCE_CASE")
        if (
            context.deep_task_signals is not None
            and context.deep_task_signals.comprehensive_knowledge_acquisition_required
            and context.deep_task_case.knowledge_acquisition_assessment is None
        ):
            raise FinalizationBlocked("MISSING_COMPREHENSIVE_KNOWLEDGE_ACQUISITION_EVIDENCE")
        deep_task_receipt = _bind_and_validate_deep_task(
            context.deep_task_case,
            context.cognition_case if context.problem_signal_observed else None,
        )
    elif context.deep_task_case is not None and not deep_required:
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
            closure = _bind_and_validate_cognition_case(closure, context.cognition_case, trusted_knowledge_resolver=context.trusted_knowledge_resolver)

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
        authoritative_task_ref=context.authoritative_task_ref,
        read_authoritative_task=context.read_authoritative_task,
    )
    adherence = evaluate_session_progress_response(response, expectation)
    if not adherence.passed:
        reasons = tuple(f"SESSION_ADHERENCE:{item.value}" for item in adherence.violations)
        raise FinalizationBlocked(*reasons)

    # Last-stage review is mandatory on a controlled selected controller turn:
    # inspect the exact outgoing text, not just the user's incoming prompt.
    if context.controller_selected:
        if context.turn_evolution_coverage is None:
            raise FinalizationBlocked("MISSING_ALL_UTTERANCE_EVOLUTION_REVIEW")
        try:
            review = admit_turn_evolution_coverage(
                context.turn_evolution_coverage,
                actual_assistant_response=response,
                host_observed_source_refs=context.observed_turn_source_refs,
                verify_source_digest=context.turn_source_digest_verifier,
                verify_judgment_ref=context.turn_judgment_verifier,
            )
        except EntryAdmissionError as exc:
            raise FinalizationBlocked(f"TURN_EVOLUTION_COVERAGE_NOT_ADMITTED: {exc}") from exc
        if review.problem_signal_observed and not context.problem_signal_observed:
            raise FinalizationBlocked("UNROUTED_POST_DRAFT_SYSTEM_OR_RULE_CONTRADICTION")
        if review.material_knowledge_gap_observed and not deep_required:
            raise FinalizationBlocked("UNROUTED_POST_DRAFT_KNOWLEDGE_GAP")
        if review.unfinished_authorized_work_observed and not context.work_remaining_without_user_input:
            raise FinalizationBlocked("UNROUTED_POST_DRAFT_UNFINISHED_AUTHORIZED_WORK")
        if (
            review.hypothesis_challenge_required
            and not (
                entry_receipt.hypothesis_challenge_required
                or context.problem_signal_observed
                or deep_required
            )
        ):
            raise FinalizationBlocked("UNROUTED_POST_DRAFT_CHALLENGE_SIGNAL")

    return FinalizationReceipt(
        closure_decision=closure_decision,
        adherence=adherence,
        deep_task_receipt=deep_task_receipt,
    )
