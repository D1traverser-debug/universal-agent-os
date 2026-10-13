from __future__ import annotations
from dataclasses import replace
from .models import ChangeProposal, PostPromotionObservation, ProposalState

_PROPOSAL_TRANSITIONS = {
    ProposalState.DRAFT: frozenset({ProposalState.EVALUATED, ProposalState.REJECTED}),
    ProposalState.EVALUATED: frozenset({ProposalState.APPROVED, ProposalState.REJECTED}),
    ProposalState.APPROVED: frozenset({ProposalState.PROMOTED, ProposalState.REJECTED}),
    ProposalState.PROMOTED: frozenset({ProposalState.ROLLED_BACK, ProposalState.RETIRED}),
    ProposalState.ROLLED_BACK: frozenset({ProposalState.RETIRED}),
    ProposalState.REJECTED: frozenset(),
    ProposalState.RETIRED: frozenset(),
}


def transition_proposal(proposal: ChangeProposal, to_state: ProposalState) -> ChangeProposal:
    if to_state not in _PROPOSAL_TRANSITIONS[proposal.state]:
        raise ValueError(f"invalid proposal transition: {proposal.state} -> {to_state}")
    return replace(proposal, state=to_state)


def post_promotion_recommendation(proposal: ChangeProposal, observations: tuple[PostPromotionObservation, ...]) -> str:
    if proposal.state is not ProposalState.PROMOTED:
        raise ValueError("post-promotion observation requires PROMOTED proposal")
    relevant = tuple(o for o in observations if o.proposal_id == proposal.proposal_id)
    if not relevant:
        return "KEEP_OBSERVING"
    if any(o.regression_refs or not o.healthy for o in relevant):
        return "ROLLBACK"
    return "KEEP_OBSERVING"
