from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from uaos.contracts.models import KnowledgeItem
from enum import Enum

from .problem_space import (MethodTransferAssessment, MethodTransferAdmissionError, require_method_transfer_admission)

from .architecture_experience import (
    ArchitectureCandidate,
    ArchitectureConcern,
    ArchitectureExperienceAdmissionError,
    ArchitectureScenario,
    InputSignal,
    Representation,
    require_architecture_experience_admission,
)
from .deliberation import (
    ActionCandidate,
    CognitiveSearchMode,
    DeliberationEvidence,
    DeliberationSignals,
    ProblemLayer,
    architecture_reassessment_required,
    durable_problem_record_required,
    require_deliberation_admission,
)


class CognitionCaseAdmissionError(RuntimeError):
    """Raised when a problem case cannot prove its causal/intervention admission."""


class EvidenceKind(str, Enum):
    USER_CLAIM = "USER_CLAIM"
    REQUIREMENT = "REQUIREMENT"
    REPOSITORY_FACT = "REPOSITORY_FACT"
    TOOL_RESULT = "TOOL_RESULT"
    EXTERNAL_SOURCE = "EXTERNAL_SOURCE"
    TEST_RESULT = "TEST_RESULT"
    RUNTIME_OBSERVATION = "RUNTIME_OBSERVATION"
    SCENARIO_RESULT = "SCENARIO_RESULT"
    ANALYSIS_RESULT = "ANALYSIS_RESULT"


class CausalFactorDisposition(str, Enum):
    PLAUSIBLE = "PLAUSIBLE"
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    evidence_id: str
    kind: EvidenceKind
    statement: str
    source_ref: str
    method_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.evidence_id.strip() or not self.statement.strip() or not self.source_ref.strip():
            raise ValueError("evidence identity, statement and source_ref are required")
        if self.method_ref is not None and not self.method_ref.strip():
            raise ValueError("method_ref cannot be empty when supplied")


@dataclass(frozen=True, slots=True)
class CausalFactor:
    factor_id: str
    layer: ProblemLayer
    statement: str
    disposition: CausalFactorDisposition
    supporting_evidence_ids: tuple[str, ...]
    falsification_or_rejection_evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.factor_id.strip() or not self.statement.strip():
            raise ValueError("causal factor identity and statement are required")
        if self.layer is ProblemLayer.UNKNOWN:
            raise ValueError("causal factor layer must be explicit")
        if not self.supporting_evidence_ids:
            raise ValueError("causal factor requires supporting evidence")
        if not self.falsification_or_rejection_evidence_ids:
            raise ValueError("causal factor requires falsification/rejection evidence")


@dataclass(frozen=True, slots=True)
class EngineeringTrace:
    """Trace the governing outcome to the selected mechanism and its V&V plan."""

    governing_outcome: str
    requirement_or_goal_evidence_ids: tuple[str, ...]
    mechanism_candidate_id: str
    verification_methods: tuple[str, ...]
    validation_methods: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.governing_outcome.strip():
            raise ValueError("engineering trace requires a governing outcome")
        if not self.requirement_or_goal_evidence_ids:
            raise ValueError("engineering trace requires requirement/goal evidence")
        if not self.mechanism_candidate_id.strip():
            raise ValueError("engineering trace requires the selected mechanism candidate")
        if not self.verification_methods or not all(item.strip() for item in self.verification_methods):
            raise ValueError("engineering trace requires at least one verification method")
        if any(not item.strip() for item in self.validation_methods):
            raise ValueError("validation methods cannot contain empty values")


@dataclass(frozen=True, slots=True)
class ArchitectureExperienceCase:
    """Raw architecture-experience inputs that must be re-admitted for architecture actions."""

    signals: tuple[InputSignal, ...]
    concerns: tuple[ArchitectureConcern, ...]
    scenarios: tuple[ArchitectureScenario, ...]
    representations: tuple[Representation, ...]
    candidates: tuple[ArchitectureCandidate, ...]


@dataclass(frozen=True, slots=True)
class CognitionCase:
    """One evidence-traced problem -> causal model -> intervention transaction.

    Causal explanation and intervention are intentionally separate: several contributing
    causes may remain supported while exactly one bounded action/no-change candidate is
    selected for the current work cycle.
    """

    case_id: str
    signals: DeliberationSignals
    evidence: DeliberationEvidence
    evidence_items: tuple[EvidenceItem, ...]
    causal_factors: tuple[CausalFactor, ...]
    action_candidates: tuple[ActionCandidate, ...]
    selected_action_candidate_id: str
    engineering_trace: EngineeringTrace
    architecture_reassessment_evidence_ids: tuple[str, ...] = ()
    architecture_experience: ArchitectureExperienceCase | None = None
    method_transfer: MethodTransferAssessment | None = None

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("cognition case id is required")
        if not self.selected_action_candidate_id.strip():
            raise ValueError("selected action candidate id is required")


@dataclass(frozen=True, slots=True)
class CognitionCaseReceipt:
    case_id: str
    search_mode: CognitiveSearchMode
    supported_factor_ids: tuple[str, ...]
    rejected_factor_ids: tuple[str, ...]
    compared_layers: tuple[ProblemLayer, ...]
    intervention_candidate_id: str
    intervention_layer: ProblemLayer
    intervention_no_change_baseline: bool
    architecture_reassessment_performed: bool
    architecture_experience_admitted: bool
    durable_problem_record_required: bool
    evidence_ids: tuple[str, ...]
    verification_methods: tuple[str, ...]
    validation_methods: tuple[str, ...]
    systemic: bool
    method_transfer_disposition: str | None = None
    transferred_knowledge_id: str | None = None


_CAUSAL_EVIDENCE_KINDS = {
    EvidenceKind.REPOSITORY_FACT,
    EvidenceKind.TOOL_RESULT,
    EvidenceKind.TEST_RESULT,
    EvidenceKind.RUNTIME_OBSERVATION,
    EvidenceKind.SCENARIO_RESULT,
    EvidenceKind.ANALYSIS_RESULT,
}
_INDEPENDENT_EVIDENCE_KINDS = {
    EvidenceKind.REPOSITORY_FACT,
    EvidenceKind.TOOL_RESULT,
    EvidenceKind.TEST_RESULT,
    EvidenceKind.RUNTIME_OBSERVATION,
    EvidenceKind.SCENARIO_RESULT,
}
_INTERVENTION_SUPPORT_EVIDENCE_KINDS = {
    EvidenceKind.REPOSITORY_FACT,
    EvidenceKind.TOOL_RESULT,
    EvidenceKind.TEST_RESULT,
    EvidenceKind.RUNTIME_OBSERVATION,
    EvidenceKind.SCENARIO_RESULT,
    EvidenceKind.ANALYSIS_RESULT,
}
_TRADEOFF_EVIDENCE_KINDS = _INTERVENTION_SUPPORT_EVIDENCE_KINDS | {EvidenceKind.EXTERNAL_SOURCE}
_UPSTREAM_LAYERS = {
    ProblemLayer.DOMAIN_ARCHITECTURE,
    ProblemLayer.COMMON_CAPABILITY,
    ProblemLayer.CONTROL_PLANE,
    ProblemLayer.HOST,
    ProblemLayer.REQUIREMENT_OR_GOAL,
}
_ARCHITECTURE_INTERVENTION_LAYERS = {
    ProblemLayer.DOMAIN_ARCHITECTURE,
    ProblemLayer.COMMON_CAPABILITY,
    ProblemLayer.CONTROL_PLANE,
    ProblemLayer.HOST,
}


def _index_evidence(items: tuple[EvidenceItem, ...]) -> dict[str, EvidenceItem]:
    result: dict[str, EvidenceItem] = {}
    for item in items:
        if item.evidence_id in result:
            raise CognitionCaseAdmissionError(f"duplicate evidence id: {item.evidence_id}")
        result[item.evidence_id] = item
    return result


def _require_known_refs(refs: tuple[str, ...], index: dict[str, EvidenceItem], label: str) -> None:
    missing = tuple(ref for ref in refs if ref not in index)
    if missing:
        raise CognitionCaseAdmissionError(
            f"{label} references unknown evidence: {', '.join(missing)}"
        )


def _require_any_evidence_kind(
    refs: tuple[str, ...],
    index: dict[str, EvidenceItem],
    allowed: set[EvidenceKind],
    label: str,
) -> None:
    if not any(index[ref].kind in allowed for ref in refs):
        raise CognitionCaseAdmissionError(
            f"{label} requires substantive current-system evidence; user claims or authority labels alone are insufficient"
        )


def _admit_architecture_experience(
    architecture: ArchitectureExperienceCase,
    evidence_by_id: dict[str, EvidenceItem],
    selected_action_id: str,
) -> None:
    for representation in architecture.representations:
        if representation.evidence_ref not in evidence_by_id:
            raise CognitionCaseAdmissionError(
                f"architecture representation references unknown evidence: {representation.evidence_ref}"
            )
        if evidence_by_id[representation.evidence_ref].kind is EvidenceKind.USER_CLAIM:
            raise CognitionCaseAdmissionError(
                "architecture representation cannot be proven only by a user claim"
            )
    for candidate in architecture.candidates:
        refs = tuple(candidate.tradeoff_evidence_refs)
        _require_known_refs(refs, evidence_by_id, f"architecture candidate {candidate.candidate_id}")
        _require_any_evidence_kind(
            refs,
            evidence_by_id,
            _TRADEOFF_EVIDENCE_KINDS,
            f"architecture candidate {candidate.candidate_id} tradeoff",
        )
    try:
        receipt = require_architecture_experience_admission(
            signals=architecture.signals,
            concerns=architecture.concerns,
            scenarios=architecture.scenarios,
            representations=architecture.representations,
            material_control_plane_or_agent_experience_change=True,
            candidates=architecture.candidates,
        )
    except ArchitectureExperienceAdmissionError as exc:
        raise CognitionCaseAdmissionError(f"architecture experience not admitted: {exc}") from exc
    if selected_action_id not in receipt.candidate_ids:
        raise CognitionCaseAdmissionError(
            "selected architecture intervention was not evaluated by architecture-experience admission"
        )


def require_cognition_case_admission(
    case: CognitionCase, *, resolve_trusted_knowledge: Callable[[str], KnowledgeItem | None] | None = None
) -> CognitionCaseReceipt:
    """Recompute cognition admission from raw case evidence instead of trusting a receipt."""

    directive = require_deliberation_admission(case.signals, case.evidence)
    evidence_by_id = _index_evidence(case.evidence_items)
    if not evidence_by_id:
        raise CognitionCaseAdmissionError("cognition case requires typed evidence items")

    for dimension, refs in case.evidence.by_dimension.items():
        _require_known_refs(refs, evidence_by_id, f"deliberation dimension {dimension}")
    if directive.external_research_required:
        external_refs = case.evidence.by_dimension.get("EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH", ())
        if not external_refs or not any(
            evidence_by_id[ref].kind is EvidenceKind.EXTERNAL_SOURCE for ref in external_refs
        ):
            raise CognitionCaseAdmissionError(
                "structured cognition requires externally sourced research evidence, not a label-only reference"
            )
    if directive.independent_verification_required:
        independent_refs = case.evidence.by_dimension.get("INDEPENDENT_VERIFICATION", ())
        if not independent_refs or not any(
            evidence_by_id[ref].kind in _INDEPENDENT_EVIDENCE_KINDS for ref in independent_refs
        ):
            raise CognitionCaseAdmissionError(
                "independent verification must bind to repository/tool/test/runtime/scenario evidence"
            )

    if not case.causal_factors:
        raise CognitionCaseAdmissionError("cognition case requires causal factors")
    if len({item.factor_id for item in case.causal_factors}) != len(case.causal_factors):
        raise CognitionCaseAdmissionError("causal factor identifiers must be unique")
    if len(case.causal_factors) < directive.min_hypotheses:
        raise CognitionCaseAdmissionError(
            f"{directive.search_mode.value.lower()} cognition requires at least {directive.min_hypotheses} causal factors"
        )
    if len(case.causal_factors) > directive.max_hypotheses:
        raise CognitionCaseAdmissionError(
            f"bounded cognition permits at most {directive.max_hypotheses} causal factors"
        )

    supported = tuple(
        item for item in case.causal_factors if item.disposition is CausalFactorDisposition.SUPPORTED
    )
    rejected = tuple(
        item for item in case.causal_factors if item.disposition is CausalFactorDisposition.REJECTED
    )
    if not supported:
        raise CognitionCaseAdmissionError("at least one causal factor must be evidence-supported")
    if directive.counterexample_search_required and not rejected:
        raise CognitionCaseAdmissionError(
            "counterexample search requires at least one evidence-rejected causal alternative"
        )

    for factor in case.causal_factors:
        _require_known_refs(factor.supporting_evidence_ids, evidence_by_id, f"causal factor {factor.factor_id}")
        _require_known_refs(
            factor.falsification_or_rejection_evidence_ids,
            evidence_by_id,
            f"causal factor {factor.factor_id} falsification",
        )
        if factor.disposition is CausalFactorDisposition.SUPPORTED:
            _require_any_evidence_kind(
                factor.supporting_evidence_ids,
                evidence_by_id,
                _CAUSAL_EVIDENCE_KINDS,
                f"supported causal factor {factor.factor_id}",
            )

    if len({item.candidate_id for item in case.action_candidates}) != len(case.action_candidates):
        raise CognitionCaseAdmissionError("action candidate identifiers must be unique")
    if len(case.action_candidates) < directive.min_action_candidates:
        raise CognitionCaseAdmissionError(
            f"{directive.search_mode.value.lower()} cognition requires at least {directive.min_action_candidates} action candidates"
        )
    if directive.no_change_baseline_required and not any(
        item.no_change_baseline for item in case.action_candidates
    ):
        raise CognitionCaseAdmissionError(
            "structured cognition requires an explicit NO_CHANGE baseline candidate"
        )
    selected_actions = tuple(
        item for item in case.action_candidates if item.candidate_id == case.selected_action_candidate_id
    )
    if len(selected_actions) != 1:
        raise CognitionCaseAdmissionError("exactly one bounded intervention candidate must be selected")
    selected_action = selected_actions[0]
    for candidate in case.action_candidates:
        _require_known_refs(candidate.evidence_refs, evidence_by_id, f"action candidate {candidate.candidate_id}")
        _require_known_refs(candidate.tradeoff_refs, evidence_by_id, f"action tradeoff {candidate.candidate_id}")
    _require_any_evidence_kind(
        selected_action.evidence_refs,
        evidence_by_id,
        _INTERVENTION_SUPPORT_EVIDENCE_KINDS,
        f"selected intervention {selected_action.candidate_id}",
    )
    _require_any_evidence_kind(
        selected_action.tradeoff_refs,
        evidence_by_id,
        _TRADEOFF_EVIDENCE_KINDS,
        f"selected intervention {selected_action.candidate_id} tradeoff",
    )

    compared_layers = tuple(sorted({item.layer for item in case.causal_factors}, key=lambda item: item.value))
    systemic = architecture_reassessment_required(case.signals)
    if systemic:
        if len(compared_layers) < 2:
            raise CognitionCaseAdmissionError(
                "systemic/material problem requires causal alternatives across at least two layers"
            )
        if not any(item.layer in _UPSTREAM_LAYERS for item in case.causal_factors):
            raise CognitionCaseAdmissionError(
                "systemic/material problem must test at least one architecture/upstream causal factor"
            )
        if not case.architecture_reassessment_evidence_ids:
            raise CognitionCaseAdmissionError(
                "systemic/material problem requires architecture reassessment evidence"
            )
        _require_known_refs(
            case.architecture_reassessment_evidence_ids,
            evidence_by_id,
            "architecture reassessment",
        )

    trace = case.engineering_trace
    _require_known_refs(
        trace.requirement_or_goal_evidence_ids,
        evidence_by_id,
        "engineering trace goal/requirement",
    )
    if not any(
        evidence_by_id[ref].kind in {EvidenceKind.USER_CLAIM, EvidenceKind.REQUIREMENT}
        for ref in trace.requirement_or_goal_evidence_ids
    ):
        raise CognitionCaseAdmissionError(
            "engineering trace must bind the selected mechanism to explicit governing goal/requirement evidence"
        )
    if trace.mechanism_candidate_id != selected_action.candidate_id:
        raise CognitionCaseAdmissionError(
            "engineering trace mechanism must match the selected intervention candidate"
        )
    if directive.search_mode is CognitiveSearchMode.STRUCTURED and not trace.validation_methods:
        raise CognitionCaseAdmissionError(
            "structured/material cognition requires an explicit validation method in addition to verification"
        )

    architecture_experience_admitted = False
    if selected_action.target_layer in _ARCHITECTURE_INTERVENTION_LAYERS:
        if case.architecture_experience is None:
            raise CognitionCaseAdmissionError(
                "architecture/control intervention requires executable architecture-experience admission"
            )
        _admit_architecture_experience(
            case.architecture_experience,
            evidence_by_id,
            selected_action.candidate_id,
        )
        architecture_experience_admitted = True

    # Previous repairs are candidates for method transfer, not proof of fit.
    # Repeated failures must provide *evidence* of reuse/adaptation or a bounded
    # no-reusable-method finding. One-off cases do not pay this research cost.
    method_receipt = None
    needs_method_transfer = (
        case.signals.repeated_failure_count >= 2
        or (
            case.signals.material_problem
            and (
                case.signals.architecture_gap
                or case.signals.cross_subsystem
                or case.signals.unknown_failure_class
            )
        )
    )
    if needs_method_transfer and case.method_transfer is None:
        raise CognitionCaseAdmissionError(
            "repeated or material-systemic failure requires prior-method transfer or evidence-backed NO_REUSABLE_METHOD"
        )
    if case.method_transfer is not None:
        if case.method_transfer.current_problem_ref != case.case_id:
            raise CognitionCaseAdmissionError("method transfer problem identity differs from cognition case")
        try:
            method_receipt = require_method_transfer_admission(
                case.method_transfer, verify_current_evidence=lambda ref: (
                    ref in evidence_by_id and evidence_by_id[ref].kind in {
                        EvidenceKind.REPOSITORY_FACT,
                        EvidenceKind.TOOL_RESULT,
                        EvidenceKind.TEST_RESULT,
                        EvidenceKind.RUNTIME_OBSERVATION,
                        EvidenceKind.SCENARIO_RESULT,
                        EvidenceKind.ANALYSIS_RESULT,
                    }
                ),
                resolve_trusted_knowledge=resolve_trusted_knowledge,
            )
        except (MethodTransferAdmissionError, ValueError) as exc:
            raise CognitionCaseAdmissionError(f"method transfer not admitted: {exc}") from exc


    used_ids = {
        *(ref for refs in case.evidence.by_dimension.values() for ref in refs),
        *(ref for factor in case.causal_factors for ref in factor.supporting_evidence_ids),
        *(ref for factor in case.causal_factors for ref in factor.falsification_or_rejection_evidence_ids),
        *(ref for candidate in case.action_candidates for ref in candidate.evidence_refs),
        *(ref for candidate in case.action_candidates for ref in candidate.tradeoff_refs),
        *case.architecture_reassessment_evidence_ids,
        *trace.requirement_or_goal_evidence_ids,
        *(method_receipt.evidence_refs if method_receipt is not None else ()),
    }
    return CognitionCaseReceipt(
        case_id=case.case_id,
        search_mode=directive.search_mode,
        supported_factor_ids=tuple(item.factor_id for item in supported),
        rejected_factor_ids=tuple(item.factor_id for item in rejected),
        compared_layers=compared_layers,
        intervention_candidate_id=selected_action.candidate_id,
        intervention_layer=selected_action.target_layer,
        intervention_no_change_baseline=selected_action.no_change_baseline,
        architecture_reassessment_performed=bool(case.architecture_reassessment_evidence_ids),
        architecture_experience_admitted=architecture_experience_admitted,
        durable_problem_record_required=durable_problem_record_required(case.signals),
        evidence_ids=tuple(sorted(used_ids)),
        verification_methods=trace.verification_methods,
        validation_methods=trace.validation_methods,
        systemic=systemic,
        method_transfer_disposition=method_receipt.disposition.value if method_receipt else None,
        transferred_knowledge_id=method_receipt.selected_knowledge_id if method_receipt else None,
    )
