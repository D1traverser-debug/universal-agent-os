from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Mapping

from uaos.contracts.enums import KnowledgeState
from uaos.contracts.models import KnowledgeItem
from uaos.kernel.problem_space import CapabilityDiscoveryReceipt

from .gates import assess_promotion
from .lifecycle import post_promotion_recommendation, transition_proposal
from .models import (
    ChangeProposal,
    ComplexityBudget,
    EvaluationResult,
    PostPromotionObservation,
    PromotionAuthorization,
    ProposalState,
)


class EvolutionOriginKind(StrEnum):
    INCIDENT = "INCIDENT"
    CAPABILITY_GAP = "CAPABILITY_GAP"
    EVALUATED_KNOWLEDGE = "EVALUATED_KNOWLEDGE"


class EvolutionTransactionStage(StrEnum):
    FRAMED = "FRAMED"
    DISCOVERED = "DISCOVERED"
    PROPOSED = "PROPOSED"
    EVALUATED = "EVALUATED"
    AUTHORIZED = "AUTHORIZED"
    PROMOTED = "PROMOTED"
    OBSERVED = "OBSERVED"
    ROLLED_BACK = "ROLLED_BACK"
    RETIRED = "RETIRED"


class EvolutionTransactionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class EvolutionDepthTrace:
    governing_outcome: str
    raw_evidence_refs: tuple[str, ...]
    professional_method_refs: tuple[str, ...]
    external_judge_refs: tuple[str, ...]
    novelty_probe_refs: tuple[str, ...] = ()
    stretch_target: str | None = None
    stretch_target_feasibility_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.governing_outcome.strip():
            raise ValueError("governing outcome is required")
        for values, label in (
            (self.raw_evidence_refs, "raw evidence"),
            (self.professional_method_refs, "professional method"),
            (self.external_judge_refs, "external judge"),
        ):
            if not values or not all(value.strip() for value in values):
                raise ValueError(f"{label} references are required")
        if self.stretch_target is not None:
            if not self.stretch_target.strip():
                raise ValueError("stretch target cannot be blank")
            if not self.stretch_target_feasibility_refs:
                raise ValueError("stretch target requires feasibility evidence")


@dataclass(frozen=True, slots=True)
class EvolutionOrigin:
    kind: EvolutionOriginKind
    origin_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.origin_ids or not all(value.strip() for value in self.origin_ids):
            raise ValueError("evolution origin ids are required")
        if not self.evidence_refs or not all(value.strip() for value in self.evidence_refs):
            raise ValueError("evolution origin evidence is required")


@dataclass(frozen=True, slots=True)
class EvolutionTransaction:
    transaction_id: str
    origin: EvolutionOrigin
    depth_trace: EvolutionDepthTrace
    stage: EvolutionTransactionStage = EvolutionTransactionStage.FRAMED
    discovery_receipt: CapabilityDiscoveryReceipt | None = None
    proposal: ChangeProposal | None = None
    evaluations: tuple[EvaluationResult, ...] = ()
    authorization: PromotionAuthorization | None = None
    observations: tuple[PostPromotionObservation, ...] = ()
    recommendation: str | None = None

    def __post_init__(self) -> None:
        if not self.transaction_id.strip():
            raise ValueError("transaction id is required")


def _require_stage(tx: EvolutionTransaction, expected: EvolutionTransactionStage) -> None:
    if tx.stage is not expected:
        raise EvolutionTransactionError(f"expected stage {expected}, got {tx.stage}")


def admit_discovery(
    tx: EvolutionTransaction,
    receipt: CapabilityDiscoveryReceipt | None,
) -> EvolutionTransaction:
    _require_stage(tx, EvolutionTransactionStage.FRAMED)
    if tx.origin.kind is EvolutionOriginKind.CAPABILITY_GAP:
        if receipt is None:
            raise EvolutionTransactionError("capability-gap evolution requires outside-in discovery receipt")
        if len(receipt.lenses) < 2:
            raise EvolutionTransactionError("capability-gap evolution requires at least two discovery lenses")
        if not receipt.latent_gap_candidates:
            raise EvolutionTransactionError("capability-gap evolution requires latent gap candidates")
        if not tx.depth_trace.novelty_probe_refs:
            raise EvolutionTransactionError("proactive capability-gap evolution requires novelty/unknown-signal probes")
    return replace(tx, discovery_receipt=receipt, stage=EvolutionTransactionStage.DISCOVERED)


def admit_proposal(
    tx: EvolutionTransaction,
    proposal: ChangeProposal,
    *,
    knowledge_by_id: Mapping[str, KnowledgeItem] | None = None,
) -> EvolutionTransaction:
    _require_stage(tx, EvolutionTransactionStage.DISCOVERED)
    if tx.origin.kind is EvolutionOriginKind.INCIDENT:
        if not proposal.failure_class_ids:
            raise EvolutionTransactionError("incident-origin evolution requires failure-class linkage")
    elif tx.origin.kind is EvolutionOriginKind.EVALUATED_KNOWLEDGE:
        if not proposal.knowledge_ids:
            raise EvolutionTransactionError("knowledge-origin evolution requires knowledge ids")
        knowledge_by_id = knowledge_by_id or {}
        unresolved = tuple(item for item in proposal.knowledge_ids if item not in knowledge_by_id)
        if unresolved:
            raise EvolutionTransactionError(f"unresolved knowledge ids: {unresolved}")
        immature = tuple(
            item
            for item in proposal.knowledge_ids
            if knowledge_by_id[item].state not in {KnowledgeState.EVALUATED, KnowledgeState.CANONICAL}
        )
        if immature:
            raise EvolutionTransactionError(f"knowledge is not mature enough for evolution: {immature}")
    elif tx.origin.kind is EvolutionOriginKind.CAPABILITY_GAP:
        if tx.discovery_receipt is None:
            raise EvolutionTransactionError("capability-gap proposal requires admitted discovery")
        if not any(
            candidate in proposal.hypothesis or candidate in proposal.title
            for candidate in tx.discovery_receipt.latent_gap_candidates
        ):
            raise EvolutionTransactionError("proposal is not traceable to a discovered latent capability gap")

    if proposal.state is not ProposalState.DRAFT:
        raise EvolutionTransactionError("canonical evolution proposal must enter transaction as DRAFT")
    return replace(tx, proposal=proposal, stage=EvolutionTransactionStage.PROPOSED)


def admit_evaluation(
    tx: EvolutionTransaction,
    evaluations: tuple[EvaluationResult, ...],
    *,
    budget: ComplexityBudget,
    knowledge_by_id: Mapping[str, KnowledgeItem] | None = None,
) -> EvolutionTransaction:
    _require_stage(tx, EvolutionTransactionStage.PROPOSED)
    if tx.proposal is None:
        raise EvolutionTransactionError("missing proposal")
    evaluated_proposal = transition_proposal(tx.proposal, ProposalState.EVALUATED)
    authorization = assess_promotion(
        evaluated_proposal,
        evaluations,
        budget=budget,
        knowledge_by_id=knowledge_by_id,
    )
    if not authorization.approved:
        raise EvolutionTransactionError("promotion admission failed: " + "; ".join(authorization.reasons))
    return replace(
        tx,
        proposal=evaluated_proposal,
        evaluations=evaluations,
        authorization=authorization,
        stage=EvolutionTransactionStage.EVALUATED,
    )


def authorize(tx: EvolutionTransaction) -> EvolutionTransaction:
    _require_stage(tx, EvolutionTransactionStage.EVALUATED)
    if tx.proposal is None or tx.authorization is None or not tx.authorization.approved:
        raise EvolutionTransactionError("evaluated transaction lacks promotion authorization")
    return replace(
        tx,
        proposal=transition_proposal(tx.proposal, ProposalState.APPROVED),
        stage=EvolutionTransactionStage.AUTHORIZED,
    )


def record_promotion(tx: EvolutionTransaction, *, execution_evidence_refs: tuple[str, ...]) -> EvolutionTransaction:
    _require_stage(tx, EvolutionTransactionStage.AUTHORIZED)
    if tx.proposal is None:
        raise EvolutionTransactionError("missing approved proposal")
    if not execution_evidence_refs or not all(ref.strip() for ref in execution_evidence_refs):
        raise EvolutionTransactionError("promotion requires execution evidence")
    return replace(
        tx,
        proposal=transition_proposal(tx.proposal, ProposalState.PROMOTED),
        stage=EvolutionTransactionStage.PROMOTED,
    )


def observe(tx: EvolutionTransaction, observations: tuple[PostPromotionObservation, ...]) -> EvolutionTransaction:
    _require_stage(tx, EvolutionTransactionStage.PROMOTED)
    if tx.proposal is None:
        raise EvolutionTransactionError("missing promoted proposal")
    if not observations:
        raise EvolutionTransactionError("post-promotion observation is required")
    recommendation = post_promotion_recommendation(tx.proposal, observations)
    return replace(
        tx,
        observations=observations,
        recommendation=recommendation,
        stage=EvolutionTransactionStage.OBSERVED,
    )


def record_rollback(tx: EvolutionTransaction, *, rollback_evidence_refs: tuple[str, ...]) -> EvolutionTransaction:
    _require_stage(tx, EvolutionTransactionStage.OBSERVED)
    if tx.proposal is None or tx.recommendation != "ROLLBACK":
        raise EvolutionTransactionError("rollback requires an observed regression recommendation")
    if not rollback_evidence_refs:
        raise EvolutionTransactionError("rollback requires evidence")
    return replace(
        tx,
        proposal=transition_proposal(tx.proposal, ProposalState.ROLLED_BACK),
        stage=EvolutionTransactionStage.ROLLED_BACK,
    )


def retire(tx: EvolutionTransaction) -> EvolutionTransaction:
    if tx.stage not in {EvolutionTransactionStage.ROLLED_BACK, EvolutionTransactionStage.OBSERVED}:
        raise EvolutionTransactionError("retirement requires observed or rolled-back transaction")
    if tx.proposal is None:
        raise EvolutionTransactionError("missing proposal")
    proposal = tx.proposal
    if proposal.state is ProposalState.PROMOTED:
        proposal = transition_proposal(proposal, ProposalState.RETIRED)
    elif proposal.state is ProposalState.ROLLED_BACK:
        proposal = transition_proposal(proposal, ProposalState.RETIRED)
    else:
        raise EvolutionTransactionError(f"proposal cannot retire from {proposal.state}")
    return replace(tx, proposal=proposal, stage=EvolutionTransactionStage.RETIRED)
