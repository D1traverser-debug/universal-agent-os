"""Small, evidence-sensitive adapter at the controlled UAOS entry boundary.

This does not own cognition, knowledge acquisition or evolution and does not
intercept native ChatGPT. The host must supply observations and invoke it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Callable, Mapping

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
    EvidenceKind.TOOL_RESULT,
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


class UtteranceOrigin(StrEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    TOOL = "TOOL"
    STATE = "STATE"


@dataclass(frozen=True, slots=True)
class TurnUtteranceAssessment:
    """Host-bound assessment of a user/assistant/tool/state utterance.

    A classification is a routing judgment, not proof that the message's claim
    is true or that a durable evolution transaction has been promoted.
    """
    source_ref: str
    origin: UtteranceOrigin
    source_sha256: str
    signal: EntrySignal
    judgment_evidence_ref: str
    alternative_or_no_gap_reason_ref: str

    def __post_init__(self) -> None:
        if not all((self.source_ref.strip(), self.judgment_evidence_ref.strip(),
                    self.alternative_or_no_gap_reason_ref.strip())):
            raise EntryAdmissionError("every utterance needs source, judgment and self-challenge references")
        if len(self.source_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.source_sha256):
            raise EntryAdmissionError("utterance digest must be lowercase sha256")


@dataclass(frozen=True, slots=True)
class TurnEvolutionCoverage:
    """One turn's all-input/output evolution triage, without an extra evolution owner."""
    observed_source_refs: tuple[str, ...]
    assessments: tuple[TurnUtteranceAssessment, ...]
    assistant_final_ref: str
    evolution_routing_ref: str

    def __post_init__(self) -> None:
        if not self.assistant_final_ref.strip() or not self.evolution_routing_ref.strip():
            raise EntryAdmissionError("turn evolution needs output identity and lifecycle routing")
        if (
            not isinstance(self.observed_source_refs, tuple)
            or not self.observed_source_refs
            or any(not isinstance(x, str) or not x.strip() for x in self.observed_source_refs)
        ):
            raise EntryAdmissionError("turn evolution needs a tuple of actual observed source references")


@dataclass(frozen=True, slots=True)
class TurnEvolutionCoverageReceipt:
    assessed_count: int
    covered_sources: tuple[str, ...]
    problem_signal_observed: bool
    material_knowledge_gap_observed: bool
    unfinished_authorized_work_observed: bool
    hypothesis_challenge_required: bool
    evolution_routing_ref: str


def admit_turn_evolution_coverage(
    review: TurnEvolutionCoverage,
    *,
    actual_assistant_response: str,
    host_observed_source_refs: tuple[str, ...] | None,
    verify_source_digest: Callable[[str, str], bool] | None,
    verify_judgment_ref: Callable[[str], bool] | None,
    host_observed_source_origins: Mapping[str, UtteranceOrigin] | None = None,
) -> TurnEvolutionCoverageReceipt:
    """Every observed utterance is evaluated, including the outgoing assistant text.

    The controlled host must enumerate sources independently of the Agent's
    classifications and verify message digests, original message roles and
    review refs. A host-authoritative role map must not come from the agent's
    self-reported assessments. This detects omissions/role spoofing on supplied
    traces; it cannot hook native
    ChatGPT or prove semantic completeness of a host-supplied enumeration.
    """

    if host_observed_source_refs is None or verify_source_digest is None or verify_judgment_ref is None:
        raise EntryAdmissionError("all-turn evolution requires independently enumerated host sources and verifiers")
    if not host_observed_source_refs or len(set(host_observed_source_refs)) != len(host_observed_source_refs):
        raise EntryAdmissionError("host source enumeration must be complete, non-empty and unique")
    expected = set(host_observed_source_refs)
    given = review.observed_source_refs
    if len(given) != len(set(given)) or set(given) != expected:
        raise EntryAdmissionError("reviewed source enumeration differs from host-observed turn")
    assessed = {item.source_ref: item for item in review.assessments}
    if len(assessed) != len(review.assessments) or set(assessed) != expected:
        raise EntryAdmissionError("not every user/assistant/tool/state utterance was assessed")
    if review.assistant_final_ref not in assessed:
        raise EntryAdmissionError("outgoing assistant message is missing from evolution assessment")
    if assessed[review.assistant_final_ref].origin is not UtteranceOrigin.ASSISTANT:
        raise EntryAdmissionError("final response must be assessed as assistant output")
    if not any(item.origin is UtteranceOrigin.USER for item in review.assessments):
        raise EntryAdmissionError("user input must be included in the turn assessment")

    digest = sha256(actual_assistant_response.encode("utf-8")).hexdigest()
    if assessed[review.assistant_final_ref].source_sha256 != digest:
        raise EntryAdmissionError("assistant's actual draft differs from the reviewed output")
    if host_observed_source_origins is None or not isinstance(host_observed_source_origins, Mapping):
        raise EntryAdmissionError("turn evolution requires independently observed host origins")
    if set(host_observed_source_origins) != expected:
        raise EntryAdmissionError("host origin enumeration must match observed turn sources")
    if any(not isinstance(origin, UtteranceOrigin) for origin in host_observed_source_origins.values()):
        raise EntryAdmissionError("host origin records require typed origins")
    for source_ref, record in assessed.items():
        if record.origin is not host_observed_source_origins[source_ref]:
            raise EntryAdmissionError(f"host origin mismatch for utterance: {source_ref}")
    for item in review.assessments:
        # The final response bytes are already bound above. Other sources must
        # be proven by the host, not accepted as agent-supplied content claims.
        if item.source_ref != review.assistant_final_ref and not verify_source_digest(
            item.source_ref, item.source_sha256
        ):
            raise EntryAdmissionError(f"unverified utterance source: {item.source_ref}")
        if not (
            verify_judgment_ref(item.judgment_evidence_ref)
            and verify_judgment_ref(item.alternative_or_no_gap_reason_ref)
        ):
            raise EntryAdmissionError(f"unverified evolution or self-challenge judgment: {item.source_ref}")
    if not verify_judgment_ref(review.evolution_routing_ref):
        raise EntryAdmissionError("evolution routing disposition is not backed by host evidence")

    return TurnEvolutionCoverageReceipt(
        assessed_count=len(assessed),
        covered_sources=tuple(sorted(expected)),
        problem_signal_observed=any(
            item.signal is EntrySignal.SYSTEM_OR_RULE_CONTRADICTION
            for item in review.assessments
        ),
        material_knowledge_gap_observed=any(
            item.signal is EntrySignal.MATERIAL_KNOWLEDGE_GAP
            for item in review.assessments
        ),
        unfinished_authorized_work_observed=any(
            item.signal is EntrySignal.UNFINISHED_AUTHORIZED_WORK
            for item in review.assessments
        ),
        hypothesis_challenge_required=any(
            item.signal is not EntrySignal.NO_MATERIAL_GAP
            for item in review.assessments
        ),
        evolution_routing_ref=review.evolution_routing_ref,
    )
