from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


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
    """Evidence that the required epistemic escalations were actually performed.

    Keys are the stable dimension names returned by ``required_deliberation_dimensions``.
    Values are evidence references; the gate does not treat an empty declaration as proof.
    """

    by_dimension: Mapping[str, tuple[str, ...]]

    def __post_init__(self) -> None:
        for dimension, refs in self.by_dimension.items():
            if not dimension.strip():
                raise ValueError("deliberation evidence dimension cannot be empty")
            if not refs or not all(ref.strip() for ref in refs):
                raise ValueError(
                    f"deliberation evidence for {dimension!r} requires non-empty references"
                )


def assess_deliberation(signals: DeliberationSignals) -> DeliberationDirective:
    """Select evidence/method depth while leaving framing/questions dynamic.

    This deliberately does not encode a finite question list or architecture catalog.
    Unknown method/architecture gaps explicitly escalate to external research.
    """

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

    required = bool(reasons)
    macro = any((
        signals.user_correction,
        signals.repeated_failure_count >= 2,
        signals.goal_progress_uncertain,
        signals.scope_expanding,
        signals.cross_subsystem,
        signals.complexity_increasing,
        signals.architecture_gap,
    ))
    assumptions = any((
        signals.user_correction,
        signals.repeated_failure_count >= 2,
        signals.goal_progress_uncertain,
        signals.architecture_gap,
    ))
    external = any((
        signals.unknown_failure_class,
        signals.knowledge_gap,
        signals.architecture_gap,
    ))
    counterexample = any((
        signals.change_proposal,
        signals.user_correction,
        signals.repeated_failure_count >= 1,
        signals.conflicting_evidence,
        signals.high_risk,
    ))
    independent = any((
        signals.high_risk,
        signals.conflicting_evidence,
        signals.cross_subsystem,
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


def required_deliberation_dimensions(
    directive: DeliberationDirective,
) -> tuple[str, ...]:
    """Return the exact evidence dimensions required by a directive."""

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
    """Fail closed until every required deliberation dimension has evidence.

    This is the executable admission counterpart to ``assess_deliberation``. It does not
    decide *how* to reason; it prevents a caller from observing a required directive and
    then silently promoting a material change without satisfying that directive.
    """

    directive = assess_deliberation(signals)
    if not directive.required:
        return directive

    required = required_deliberation_dimensions(directive)
    available = evidence.by_dimension if evidence is not None else {}
    missing = tuple(
        dimension
        for dimension in required
        if not available.get(dimension)
    )
    if missing:
        raise RuntimeError(
            "deliberation admission blocked; missing evidence for: "
            + ", ".join(missing)
        )
    return directive
