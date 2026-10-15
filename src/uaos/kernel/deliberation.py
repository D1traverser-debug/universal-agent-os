from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class ProblemLayer(str, Enum):
    LOCAL_IMPLEMENTATION = "LOCAL_IMPLEMENTATION"
    DOMAIN_WORKFLOW = "DOMAIN_WORKFLOW"
    DOMAIN_ARCHITECTURE = "DOMAIN_ARCHITECTURE"
    COMMON_CAPABILITY = "COMMON_CAPABILITY"
    CONTROL_PLANE = "CONTROL_PLANE"
    HOST = "HOST"
    REQUIREMENT_OR_GOAL = "REQUIREMENT_OR_GOAL"
    UNKNOWN = "UNKNOWN"


class HypothesisDisposition(str, Enum):
    PLAUSIBLE = "PLAUSIBLE"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


class RootScopeAdmissionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DeliberationSignals:
    """Risk/evidence signals. They trigger depth; they do not prescribe the questions."""

    user_correction: bool = False
    repeated_failure_count: int = 0
    goal_progress_uncertain: bool = False
    scope_expanding: bool = False
    cross_subsystem: bool = False
    complexity_increasing: bool = False
    conflicting_evidence: bool = False
    unknown_failure_class: bool = False
    knowledge_gap: bool = False
    architecture_gap: bool = False
    high_risk: bool = False
    change_proposal: bool = False
    material_problem: bool = False

    def __post_init__(self) -> None:
        if self.repeated_failure_count < 0:
            raise ValueError("repeated_failure_count cannot be negative")


@dataclass(frozen=True, slots=True)
class DeliberationDirective:
    required: bool
    micro_diagnosis_required: bool
    macro_alignment_required: bool
    governing_assumptions_challenge_required: bool
    external_research_required: bool
    counterexample_search_required: bool
    independent_verification_required: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DeliberationEvidence:
    """Evidence that the required epistemic escalations were actually performed."""

    by_dimension: Mapping[str, tuple[str, ...]]

    def __post_init__(self) -> None:
        for dimension, refs in self.by_dimension.items():
            if not dimension.strip():
                raise ValueError("deliberation evidence dimension cannot be empty")
            if not refs or not all(ref.strip() for ref in refs):
                raise ValueError(
                    f"deliberation evidence for {dimension!r} requires non-empty references"
                )


@dataclass(frozen=True, slots=True)
class ProblemHypothesis:
    hypothesis_id: str
    layer: ProblemLayer
    statement: str
    disposition: HypothesisDisposition
    supporting_evidence_refs: tuple[str, ...]
    falsification_or_rejection_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip() or not self.statement.strip():
            raise ValueError("hypothesis identity and statement are required")
        if self.layer is ProblemLayer.UNKNOWN:
            raise ValueError("hypothesis layer must be explicit")
        if not self.supporting_evidence_refs:
            raise ValueError("hypothesis requires supporting evidence")
        if not self.falsification_or_rejection_refs:
            raise ValueError("hypothesis requires falsification/rejection evidence")


@dataclass(frozen=True, slots=True)
class RootScopeAssessment:
    hypotheses: tuple[ProblemHypothesis, ...]
    selected_hypothesis_id: str
    architecture_reassessment_refs: tuple[str, ...] = ()
    direct_user_or_external_claim_promoted_without_test: bool = False


@dataclass(frozen=True, slots=True)
class RootScopeReceipt:
    selected_hypothesis_id: str
    selected_layer: ProblemLayer
    hypothesis_count: int
    compared_layers: tuple[ProblemLayer, ...]
    architecture_reassessment_performed: bool
    durable_problem_record_required: bool
    evidence_refs: tuple[str, ...]


def assess_deliberation(signals: DeliberationSignals) -> DeliberationDirective:
    """Select evidence/method depth while leaving framing/questions dynamic."""

    reasons: list[str] = []
    if signals.user_correction:
        reasons.append("USER_CORRECTION")
    if signals.repeated_failure_count >= 2:
        reasons.append("REPEATED_FAILURE")
    elif signals.repeated_failure_count == 1:
        reasons.append("FAILURE")
    if signals.goal_progress_uncertain:
        reasons.append("GOAL_PROGRESS_UNCERTAIN")
    if signals.scope_expanding:
        reasons.append("SCOPE_EXPANSION")
    if signals.cross_subsystem:
        reasons.append("CROSS_SUBSYSTEM")
    if signals.complexity_increasing:
        reasons.append("COMPLEXITY_GROWTH")
    if signals.conflicting_evidence:
        reasons.append("CONFLICTING_EVIDENCE")
    if signals.unknown_failure_class:
        reasons.append("UNKNOWN_FAILURE_CLASS")
    if signals.knowledge_gap:
        reasons.append("KNOWLEDGE_GAP")
    if signals.architecture_gap:
        reasons.append("ARCHITECTURE_GAP")
    if signals.high_risk:
        reasons.append("HIGH_RISK")
    if signals.change_proposal:
        reasons.append("CHANGE_PROPOSAL")
    if signals.material_problem:
        reasons.append("MATERIAL_PROBLEM")

    required = bool(reasons)
    problem_detected = any((
        signals.user_correction,
        signals.repeated_failure_count >= 1,
        signals.goal_progress_uncertain,
        signals.complexity_increasing,
        signals.conflicting_evidence,
        signals.unknown_failure_class,
        signals.knowledge_gap,
        signals.architecture_gap,
        signals.material_problem,
    ))

    macro = problem_detected or any((signals.scope_expanding, signals.cross_subsystem))
    assumptions = problem_detected
    external = problem_detected
    counterexample = any((
        signals.change_proposal,
        signals.user_correction,
        signals.repeated_failure_count >= 1,
        signals.conflicting_evidence,
        signals.high_risk,
        signals.material_problem,
    ))
    independent = any((
        signals.high_risk,
        signals.conflicting_evidence,
        signals.cross_subsystem,
        signals.material_problem,
    ))

    return DeliberationDirective(
        required=required,
        micro_diagnosis_required=required,
        macro_alignment_required=macro,
        governing_assumptions_challenge_required=assumptions,
        external_research_required=external,
        counterexample_search_required=counterexample,
        independent_verification_required=independent,
        reason_codes=tuple(reasons),
    )


def required_deliberation_dimensions(directive: DeliberationDirective) -> tuple[str, ...]:
    dimensions: list[str] = []
    if directive.micro_diagnosis_required:
        dimensions.append("MICRO_DIAGNOSIS")
    if directive.macro_alignment_required:
        dimensions.append("MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT")
    if directive.governing_assumptions_challenge_required:
        dimensions.append("GOVERNING_ASSUMPTION_CHALLENGE")
    if directive.external_research_required:
        dimensions.append("EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH")
    if directive.counterexample_search_required:
        dimensions.append("COUNTEREXAMPLE_SEARCH")
    if directive.independent_verification_required:
        dimensions.append("INDEPENDENT_VERIFICATION")
    return tuple(dimensions)


def require_deliberation_admission(
    signals: DeliberationSignals,
    evidence: DeliberationEvidence | None = None,
) -> DeliberationDirective:
    """Fail closed until every required deliberation dimension has evidence."""

    directive = assess_deliberation(signals)
    if not directive.required:
        return directive

    required = required_deliberation_dimensions(directive)
    available = evidence.by_dimension if evidence is not None else {}
    missing = tuple(dimension for dimension in required if not available.get(dimension))
    if missing:
        raise RuntimeError(
            "deliberation admission blocked; missing evidence for: "
            + ", ".join(missing)
        )
    return directive


def architecture_reassessment_required(signals: DeliberationSignals) -> bool:
    """Return whether the current failure pattern must explicitly test architecture/upstream scope."""

    return any((
        signals.material_problem,
        signals.architecture_gap,
        signals.cross_subsystem,
        signals.complexity_increasing,
        signals.repeated_failure_count >= 2,
        signals.scope_expanding,
    ))


def durable_problem_record_required(signals: DeliberationSignals) -> bool:
    """Derive durable causal-evidence need from problem/risk signals, not caller preference."""

    return any((
        signals.material_problem,
        signals.repeated_failure_count >= 2,
        signals.cross_subsystem,
        signals.complexity_increasing,
        signals.conflicting_evidence,
        signals.unknown_failure_class,
        signals.architecture_gap,
        signals.scope_expanding,
        signals.high_risk,
    ))


def require_root_scope_admission(
    signals: DeliberationSignals,
    evidence: DeliberationEvidence,
    assessment: RootScopeAssessment,
) -> RootScopeReceipt:
    """Admit action only after the problem layer is evidence-tested rather than assumed.

    The user's framing, an external method, and the first repairable symptom are evidence,
    not authority. Material/systemic problems must compare competing hypotheses across
    layers and explicitly test whether the architecture/control plane is implicated.
    """

    require_deliberation_admission(signals, evidence)

    if assessment.direct_user_or_external_claim_promoted_without_test:
        raise RootScopeAdmissionError(
            "root-scope admission blocked: user/external framing was promoted without falsification"
        )
    if not assessment.hypotheses:
        raise RootScopeAdmissionError("root-scope admission requires hypotheses")
    if len({item.hypothesis_id for item in assessment.hypotheses}) != len(assessment.hypotheses):
        raise RootScopeAdmissionError("hypothesis identifiers must be unique")

    selected = [
        item for item in assessment.hypotheses
        if item.hypothesis_id == assessment.selected_hypothesis_id
    ]
    if len(selected) != 1 or selected[0].disposition is not HypothesisDisposition.SELECTED:
        raise RootScopeAdmissionError("exactly one selected hypothesis must match selected_hypothesis_id")
    if sum(item.disposition is HypothesisDisposition.SELECTED for item in assessment.hypotheses) != 1:
        raise RootScopeAdmissionError("exactly one hypothesis may be SELECTED")

    systemic = architecture_reassessment_required(signals)
    compared_layers = tuple(sorted({item.layer for item in assessment.hypotheses}, key=lambda x: x.value))
    if systemic:
        if len(assessment.hypotheses) < 2 or len(compared_layers) < 2:
            raise RootScopeAdmissionError(
                "systemic/material problem requires competing hypotheses across at least two layers"
            )
        if not any(item.disposition is HypothesisDisposition.REJECTED for item in assessment.hypotheses):
            raise RootScopeAdmissionError(
                "systemic/material problem requires at least one evidence-rejected alternative"
            )
        upstream_layers = {
            ProblemLayer.DOMAIN_ARCHITECTURE,
            ProblemLayer.COMMON_CAPABILITY,
            ProblemLayer.CONTROL_PLANE,
            ProblemLayer.HOST,
            ProblemLayer.REQUIREMENT_OR_GOAL,
        }
        if not any(item.layer in upstream_layers for item in assessment.hypotheses):
            raise RootScopeAdmissionError(
                "systemic/material problem must test at least one architecture/upstream hypothesis"
            )
        if not assessment.architecture_reassessment_refs:
            raise RootScopeAdmissionError(
                "architecture reassessment evidence is required for systemic/material problems"
            )

    evidence_refs = tuple(sorted({
        *selected[0].supporting_evidence_refs,
        *selected[0].falsification_or_rejection_refs,
        *assessment.architecture_reassessment_refs,
    }))
    return RootScopeReceipt(
        selected_hypothesis_id=selected[0].hypothesis_id,
        selected_layer=selected[0].layer,
        hypothesis_count=len(assessment.hypotheses),
        compared_layers=compared_layers,
        architecture_reassessment_performed=bool(assessment.architecture_reassessment_refs),
        durable_problem_record_required=durable_problem_record_required(signals),
        evidence_refs=evidence_refs,
    )
