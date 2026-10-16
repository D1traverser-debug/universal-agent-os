from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ArchitectureExperienceAdmissionError(RuntimeError):
    pass


class SignalKind(str, Enum):
    EXPLICIT_REQUIREMENT = "EXPLICIT_REQUIREMENT"
    GOAL_OR_OUTCOME = "GOAL_OR_OUTCOME"
    EXAMPLE = "EXAMPLE"
    OBSERVATION = "OBSERVATION"
    HYPOTHESIS = "HYPOTHESIS"
    CONSTRAINT = "CONSTRAINT"


STRUCTURAL_VIEWS = {
    "AUTHORITY_MAP",
    "CONTEXT_MAP",
    "COMPONENT_VIEW",
    "DEPENDENCY_GRAPH",
    "DATA_OR_ARTIFACT_GRAPH",
}

TEMPORAL_VIEWS = {"SEQUENCE", "STATE_MACHINE", "EVENT_TRACE", "LIFECYCLE", "TIMELINE"}
COGNITIVE_VIEWS = {"COGNITIVE_WALKTHROUGH", "TASK_JOURNEY", "RECOVERY_WALKTHROUGH"}


@dataclass(frozen=True, slots=True)
class InputSignal:
    signal_id: str
    kind: SignalKind
    statement: str
    promoted_to_requirement: bool = False


@dataclass(frozen=True, slots=True)
class ArchitectureConcern:
    concern_id: str
    description: str
    structural_relationships_material: bool = False
    temporal_behavior_material: bool = False
    actor_operability_material: bool = False


@dataclass(frozen=True, slots=True)
class WalkthroughStep:
    step_id: str
    actor: str
    action: str
    expected_progress_signal: str
    failure_or_confusion_risk: str
    recovery_or_next_evidence: str


@dataclass(frozen=True, slots=True)
class ArchitectureScenario:
    scenario_id: str
    scenario_class: str
    governing_outcome: str
    start_authority_or_state: str
    steps: tuple[WalkthroughStep, ...]
    concern_ids: frozenset[str]


@dataclass(frozen=True, slots=True)
class Representation:
    kind: str
    concern_ids: frozenset[str]
    evidence_ref: str


@dataclass(frozen=True, slots=True)
class ArchitectureCandidate:
    candidate_id: str
    mechanism_summary: str
    concern_ids: frozenset[str]
    tradeoff_evidence_refs: tuple[str, ...]
    no_change_baseline: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id.strip() or not self.mechanism_summary.strip():
            raise ValueError("architecture candidate identity and mechanism summary are required")
        if not self.tradeoff_evidence_refs or not all(ref.strip() for ref in self.tradeoff_evidence_refs):
            raise ValueError("architecture candidate requires tradeoff evidence")


@dataclass(frozen=True, slots=True)
class ArchitectureExperienceReceipt:
    scenario_ids: tuple[str, ...]
    representation_kinds: tuple[str, ...]
    dogfood_present: bool
    user_examples_kept_nonbinding: tuple[str, ...]
    candidate_ids: tuple[str, ...] = ()


def require_architecture_experience_admission(
    *,
    signals: tuple[InputSignal, ...],
    concerns: tuple[ArchitectureConcern, ...],
    scenarios: tuple[ArchitectureScenario, ...],
    representations: tuple[Representation, ...],
    material_control_plane_or_agent_experience_change: bool,
    candidates: tuple[ArchitectureCandidate, ...] = (),
) -> ArchitectureExperienceReceipt:
    if not concerns:
        raise ArchitectureExperienceAdmissionError("material architecture evaluation requires explicit concerns")
    if not scenarios:
        raise ArchitectureExperienceAdmissionError("material architecture evaluation requires scenario walkthroughs")

    invalid_promotions = [
        signal.signal_id
        for signal in signals
        if signal.kind in {SignalKind.EXAMPLE, SignalKind.OBSERVATION, SignalKind.HYPOTHESIS}
        and signal.promoted_to_requirement
    ]
    if invalid_promotions:
        raise ArchitectureExperienceAdmissionError(
            "illustrative/non-authoritative input was promoted directly to a requirement: "
            + ", ".join(sorted(invalid_promotions))
        )

    concern_by_id = {concern.concern_id: concern for concern in concerns}
    if len(concern_by_id) != len(concerns):
        raise ArchitectureExperienceAdmissionError("concern identifiers must be unique")

    representation_kinds_by_concern: dict[str, set[str]] = {key: set() for key in concern_by_id}
    for representation in representations:
        if not representation.evidence_ref.strip():
            raise ArchitectureExperienceAdmissionError("representations require evidence references")
        unknown = representation.concern_ids.difference(concern_by_id)
        if unknown:
            raise ArchitectureExperienceAdmissionError(f"representation references unknown concerns: {sorted(unknown)}")
        for concern_id in representation.concern_ids:
            representation_kinds_by_concern[concern_id].add(representation.kind)

    for concern in concerns:
        kinds = representation_kinds_by_concern[concern.concern_id]
        if concern.structural_relationships_material and not kinds.intersection(STRUCTURAL_VIEWS):
            raise ArchitectureExperienceAdmissionError(
                f"concern {concern.concern_id} needs structural relationship evidence"
            )
        if concern.temporal_behavior_material and not kinds.intersection(TEMPORAL_VIEWS):
            raise ArchitectureExperienceAdmissionError(
                f"concern {concern.concern_id} needs temporal/behavioral evidence"
            )
        if concern.actor_operability_material and not kinds.intersection(COGNITIVE_VIEWS):
            raise ArchitectureExperienceAdmissionError(
                f"concern {concern.concern_id} needs a cognitive/task walkthrough"
            )

    scenario_ids: list[str] = []
    dogfood_present = False
    covered_concerns: set[str] = set()
    for scenario in scenarios:
        if not scenario.governing_outcome.strip() or not scenario.start_authority_or_state.strip():
            raise ArchitectureExperienceAdmissionError(
                f"scenario {scenario.scenario_id} must bind governing outcome and start authority/state"
            )
        if not scenario.steps:
            raise ArchitectureExperienceAdmissionError(f"scenario {scenario.scenario_id} has no steps")
        unknown = scenario.concern_ids.difference(concern_by_id)
        if unknown:
            raise ArchitectureExperienceAdmissionError(f"scenario references unknown concerns: {sorted(unknown)}")
        for step in scenario.steps:
            if not all(
                value.strip()
                for value in (
                    step.actor,
                    step.action,
                    step.expected_progress_signal,
                    step.failure_or_confusion_risk,
                    step.recovery_or_next_evidence,
                )
            ):
                raise ArchitectureExperienceAdmissionError(
                    f"scenario {scenario.scenario_id} step {step.step_id} lacks progress/risk/recovery evidence"
                )
            if step.actor == "CURRENT_AGENT":
                dogfood_present = True
        covered_concerns.update(scenario.concern_ids)
        scenario_ids.append(scenario.scenario_id)

    missing_scenario_coverage = set(concern_by_id).difference(covered_concerns)
    if missing_scenario_coverage:
        raise ArchitectureExperienceAdmissionError(
            "concerns lack scenario coverage: " + ", ".join(sorted(missing_scenario_coverage))
        )

    if material_control_plane_or_agent_experience_change and not dogfood_present:
        raise ArchitectureExperienceAdmissionError(
            "material control-plane/agent-experience change requires CURRENT_AGENT dogfooding"
        )

    candidate_ids: tuple[str, ...] = ()
    if material_control_plane_or_agent_experience_change:
        if len(candidates) < 2:
            raise ArchitectureExperienceAdmissionError(
                "material control-plane/agent-experience change requires at least two architecture candidates"
            )
        if len(candidates) > 5:
            raise ArchitectureExperienceAdmissionError(
                "architecture candidate comparison is bounded to at most five candidates"
            )
        if len({candidate.candidate_id for candidate in candidates}) != len(candidates):
            raise ArchitectureExperienceAdmissionError("architecture candidate identifiers must be unique")
        if not any(candidate.no_change_baseline for candidate in candidates):
            raise ArchitectureExperienceAdmissionError(
                "material control-plane/agent-experience change requires an explicit NO_CHANGE baseline"
            )
        covered_by_candidates: set[str] = set()
        for candidate in candidates:
            unknown = candidate.concern_ids.difference(concern_by_id)
            if unknown:
                raise ArchitectureExperienceAdmissionError(
                    f"architecture candidate references unknown concerns: {sorted(unknown)}"
                )
            covered_by_candidates.update(candidate.concern_ids)
        missing_candidate_coverage = set(concern_by_id).difference(covered_by_candidates)
        if missing_candidate_coverage:
            raise ArchitectureExperienceAdmissionError(
                "architecture concerns lack candidate tradeoff coverage: "
                + ", ".join(sorted(missing_candidate_coverage))
            )
        candidate_ids = tuple(candidate.candidate_id for candidate in candidates)

    nonbinding = tuple(
        signal.signal_id
        for signal in signals
        if signal.kind in {SignalKind.EXAMPLE, SignalKind.OBSERVATION, SignalKind.HYPOTHESIS}
        and not signal.promoted_to_requirement
    )
    return ArchitectureExperienceReceipt(
        scenario_ids=tuple(scenario_ids),
        representation_kinds=tuple(sorted({representation.kind for representation in representations})),
        dogfood_present=dogfood_present,
        user_examples_kept_nonbinding=nonbinding,
        candidate_ids=candidate_ids,
    )
