"""Transfer past *methods*, not past fixes: source-bounded negative and positive controls."""
from dataclasses import replace

import pytest

from uaos.contracts.enums import KnowledgeState
from uaos.contracts.models import KnowledgeItem
from uaos.kernel.problem_space import (
    MethodTransferAdmissionError,
    MethodTransferAssessment,
    MethodTransferCandidate,
    MethodTransferDisposition,
    require_method_transfer_admission,
)


def method(*, state=KnowledgeState.CANONICAL, scope="UAOS", usages=("issue:known-positive",)):
    return KnowledgeItem(
        knowledge_id="method:causal-boundary-analysis",
        content="Examine interface plus executable constraint and disconfirming sibling paths, not just patch caller",
        source_refs=("docs:prior-analysis",),
        applicable_scope=scope,
        state=state,
        confidence=0.9,
        usage_links=usages,
    )


def candidate(**changes):
    data = {
        "knowledge": method(),
        "method_family": "systems-causal-analysis",
        "failure_class": "DECLARED_VS_EXECUTED",
        "fit_evidence_refs": ("repo:current-gate-bypass",),
        "misfit_or_falsification_refs": ("scenario:counterexample"),
        "fit_condition": "current behavior bypasses installed gate",
        "nonfit_condition": "gate was actually mediated and failure came from stale source data",
    }
    data.update(changes)
    return MethodTransferCandidate(**data)


def assessment(**changes):
    data = {
        "current_problem_ref": "case:controller-20261018",
        "target_scope": "UAOS",
        "observed_failure_classes": ("DECLARED_VS_EXECUTED",),
        "lookup_evidence_refs": ("repo:prior-method-lookup",),
        "candidates": (candidate(),),
        "selected_knowledge_id": "method:causal-boundary-analysis",
        "disposition": MethodTransferDisposition.REUSE_CANONICAL_CANDIDATE,
        "novelty_probe_refs": ("scenario:unknown-sibling-path",),
        "selection_rationale": "prior interface method fits, with an explicit misfit counterexample",
    }
    data.update(changes)
    return MethodTransferAssessment(**data)


ALL_REF = {
    "repo:current-gate-bypass", "scenario:counterexample",
    "repo:prior-method-lookup", "scenario:unknown-sibling-path",
}


def verify(ref):
    return ref in ALL_REF


def test_promoted_prior_method_can_be_transferred_as_bounded_candidate_not_live_proof():
    receipt = require_method_transfer_admission(assessment(), verify_current_evidence=verify)
    assert receipt.selected_knowledge_id == "method:causal-boundary-analysis"
    assert receipt.disposition is MethodTransferDisposition.REUSE_CANONICAL_CANDIDATE
    assert "scenario:counterexample" in receipt.evidence_refs


def test_rejects_declared_inheritance_without_current_source_checks():
    with pytest.raises(MethodTransferAdmissionError, match="verification"):
        require_method_transfer_admission(assessment(), verify_current_evidence=None)
    with pytest.raises(MethodTransferAdmissionError, match="unverified"):
        require_method_transfer_admission(assessment(), verify_current_evidence=lambda x: x != "scenario:counterexample")


def test_rejects_wrong_scope_retired_and_uncertified_methods():
    for bad in (
        candidate(knowledge=method(scope="DOMAIN:video")),
        candidate(knowledge=method(state=KnowledgeState.RETIRED)),
        candidate(knowledge=method(state=KnowledgeState.EVALUATED)),
        candidate(knowledge=method(usages=())),
    ):
        with pytest.raises(MethodTransferAdmissionError):
            require_method_transfer_admission(assessment(candidates=(bad,)), verify_current_evidence=verify)


def test_adaptation_is_provisional_and_raw_rules_cannot_be_selected():
    provisional = candidate(knowledge=method(state=KnowledgeState.EVALUATED))
    receipt = require_method_transfer_admission(
        assessment(candidates=(provisional,), disposition=MethodTransferDisposition.ADAPT_PROVISIONALLY),
        verify_current_evidence=verify,
    )
    assert receipt.disposition is MethodTransferDisposition.ADAPT_PROVISIONALLY
    with pytest.raises(MethodTransferAdmissionError, match="raw"):
        require_method_transfer_admission(
            assessment(candidates=(candidate(knowledge=method(state=KnowledgeState.RAW_EVIDENCE)),),
                       disposition=MethodTransferDisposition.ADAPT_PROVISIONALLY),
            verify_current_evidence=verify,
        )


def test_no_analogue_is_a_documented_outcome_not_a_invented_reuse():
    no_reuse = assessment(
        selected_knowledge_id=None,
        disposition=MethodTransferDisposition.NO_REUSABLE_METHOD,
        candidates=(),
        selection_rationale="prior-method index read and novelty probe found no adequate fit",
    )
    receipt = require_method_transfer_admission(no_reuse, verify_current_evidence=verify)
    assert receipt.selected_knowledge_id is None
    with pytest.raises(MethodTransferAdmissionError, match="cannot select"):
        require_method_transfer_admission(
            replace(no_reuse, selected_knowledge_id="method:causal-boundary-analysis"),
            verify_current_evidence=verify,
        )


def test_analogy_cannot_conjure_a_failure_class_and_candidate_ids_are_unique():
    with pytest.raises(MethodTransferAdmissionError, match="unobserved"):
        require_method_transfer_admission(
            assessment(candidates=(candidate(failure_class="NEVER_OBSERVED"),)), verify_current_evidence=verify
        )
    with pytest.raises(MethodTransferAdmissionError, match="duplicate"):
        require_method_transfer_admission(
            assessment(candidates=(candidate(), candidate())), verify_current_evidence=verify
        )
