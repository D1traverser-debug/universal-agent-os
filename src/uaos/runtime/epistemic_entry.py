"""Small, evidence-sensitive adapter at the controlled UAOS entry boundary.

This does not own cognition, knowledge acquisition or evolution and does not
intercept native ChatGPT. The host must supply observations and invoke it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from uaos.kernel.cognition_case import EvidenceItem, EvidenceKind


class EntryAdmissionError(ValueError):
    pass


class EntrySignal(StrEnum):
    CLAIM_OR_CAUSAL_SUGGESTION = "CLAIM_OR_CAUSAL_SUGGESTION"
    SYSTEM_OR_RULE_CONTRADICTION = "SYSTEM_OR_RULE_CONTRADICTION"
    MATERIAL_KNOWLEDGE_GAP = "MATERIAL_KNOWLEDGE_GAP"
    UNFINISHED_AUTHORIZED_WORK = "UNFINISHED_AUTHORIZED_WORK"
    NO_MATERIAL_GAP = "NO_MATERIAL_GAP"


_FACT_KINDS = frozenset({
    EvidenceKind.REPOSITORY_FACT,
    EvidenceKind.TEST_RESULT,
    EvidenceKind.RUNTIME_OBSERVATION,
})


@dataclass(frozen=True, slots=True)
class EntryObservation:
    signal: EntrySignal
    evidence: EvidenceItem

    def __post_init__(self) -> None:
        if not self.evidence.evidence_id.strip() or not self.evidence.source_ref.strip():
            raise EntryAdmissionError("entry observations require canonical attributable evidence")


@dataclass(frozen=True, slots=True)
class ControllerEpistemicEntry:
    objective_ref: str
    state_ref: str
    observations: tuple[EntryObservation, ...]
    governing_assumption_review_ref: str
    next_action_ref: str

    def __post_init__(self) -> None:
        if not all((
            self.objective_ref.strip(),
            self.state_ref.strip(),
            self.governing_assumption_review_ref.strip(),
            self.next_action_ref.strip(),
        )):
            raise EntryAdmissionError(
                "controlled controller entry requires objective, state, assumption challenge and next-action references"
            )
        if not self.observations:
            raise EntryAdmissionError("controlled controller entry needs current observations")


@dataclass(frozen=True, slots=True)
class ControllerEpistemicReceipt:
    objective_ref: str
    evidence_refs: tuple[str, ...]
    problem_signal_observed: bool
    deep_learning_required: bool
    work_remaining: bool
    hypothesis_challenge_required: bool


def assess_controller_epistemic_entry(
    entry: ControllerEpistemicEntry,
) -> ControllerEpistemicReceipt:
    """Derive routing from supplied evidence, without accepting a suggested fix as fact.

    This is a bounded pre-cognition router. Material fact-backed gaps invoke the
    existing cognition/deep-task controls; benign assertions remain hypotheses.
    A host-supplied record is not independently verified merely by this call.
    """

    problems = False
    learning = False
    continuation = False
    challenge = False
    ref_seen: set[str] = set()

    for item in entry.observations:
        if item.evidence.source_ref in ref_seen:
            raise EntryAdmissionError("entry evidence references must be distinct")
        ref_seen.add(item.evidence.source_ref)
        is_fact = item.evidence.kind in _FACT_KINDS
        if item.signal is EntrySignal.NO_MATERIAL_GAP:
            if any((
                problems, learning, continuation,
            )):
                raise EntryAdmissionError("no-material-gap signal contradicts observed material issue")
            continue
        if item.signal is EntrySignal.CLAIM_OR_CAUSAL_SUGGESTION:
            challenge = True
            continue
        if not is_fact:
            # A user or assistant theory cannot be promoted into an observed cause.
            challenge = True
            continue
        if item.signal is EntrySignal.SYSTEM_OR_RULE_CONTRADICTION:
            problems = True
            challenge = True
        elif item.signal is EntrySignal.MATERIAL_KNOWLEDGE_GAP:
            learning = True
            challenge = True
        elif item.signal is EntrySignal.UNFINISHED_AUTHORIZED_WORK:
            continuation = True
    if any(item.signal is EntrySignal.NO_MATERIAL_GAP for item in entry.observations):
        if problems or learning or continuation:
            raise EntryAdmissionError("clean classification contradicts fact-backed issue")
    return ControllerEpistemicReceipt(
        objective_ref=entry.objective_ref,
        evidence_refs=tuple(sorted(ref_seen)),
        problem_signal_observed=problems,
        deep_learning_required=learning,
        work_remaining=continuation,
        hypothesis_challenge_required=challenge,
    )
