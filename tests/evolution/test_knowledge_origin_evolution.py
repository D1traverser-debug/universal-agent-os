from uaos.contracts.enums import KnowledgeState
from uaos.contracts.models import KnowledgeItem
from uaos.evolution import ChangeProposal, ComplexityBudget, ComplexityDelta, EvaluationResult, ProposalState, assess_promotion


def _proposal(*, knowledge_ids=("k1",)) -> ChangeProposal:
    return ChangeProposal(
        proposal_id="kp1",
        title="promote learned architecture improvement",
        failure_class_ids=(),
        hypothesis="evaluated knowledge indicates a reusable control-plane improvement",
        target_scope="control-plane",
        added_mechanisms=(),
        replaced_mechanisms=(),
        retired_mechanisms=(),
        why_not_reuse="",
        retirement_rationale="",
        rollback_plan="revert candidate commit",
        expected_benefit="improve cognition quality without fabricating an incident",
        new_failure_modes=("overgeneralizing knowledge",),
        required_scenarios=("scenario:knowledge-origin",),
        complexity_delta=ComplexityDelta(),
        evidence_refs=("knowledge-eval:k1",),
        state=ProposalState.EVALUATED,
        knowledge_ids=knowledge_ids,
    )


def _evaluation() -> EvaluationResult:
    return EvaluationResult(
        evaluation_id="ke1",
        proposal_id="kp1",
        scenario_refs=("scenario:knowledge-origin",),
        metrics_before={"coverage": 0.0},
        metrics_after={"coverage": 1.0},
        acceptance_checks={"knowledge_is_actionable": True},
        regression_failures=(),
        passed=True,
        evidence_refs=("eval:knowledge-origin",),
    )


def _knowledge(state: KnowledgeState) -> KnowledgeItem:
    return KnowledgeItem(
        knowledge_id="k1",
        content="bounded adaptive search improves fit between uncertainty and deliberation cost",
        source_refs=("research:method-comparison",),
        applicable_scope="UAOS cognition",
        state=state,
        confidence=0.9,
        usage_links=("eval:knowledge-origin",) if state is KnowledgeState.CANONICAL else (),
    )


def test_change_proposal_can_originate_from_evaluated_knowledge_without_fake_failure_class():
    decision = assess_promotion(
        _proposal(),
        (_evaluation(),),
        budget=ComplexityBudget(),
        knowledge_by_id={"k1": _knowledge(KnowledgeState.EVALUATED)},
    )
    assert decision.approved


def test_raw_or_unresolved_knowledge_cannot_authorize_evolution_promotion():
    raw = assess_promotion(
        _proposal(),
        (_evaluation(),),
        budget=ComplexityBudget(),
        knowledge_by_id={"k1": _knowledge(KnowledgeState.RAW_EVIDENCE)},
    )
    assert not raw.approved
    assert any("EVALUATED or CANONICAL" in reason for reason in raw.reasons)

    missing = assess_promotion(
        _proposal(),
        (_evaluation(),),
        budget=ComplexityBudget(),
        knowledge_by_id={},
    )
    assert not missing.approved
    assert any("unresolved knowledge ids" in reason for reason in missing.reasons)


def test_proposal_requires_at_least_one_real_origin():
    try:
        _proposal(knowledge_ids=())
    except ValueError as exc:
        assert "admitted origin" in str(exc)
    else:
        raise AssertionError("proposal without failure-class or knowledge origin must fail")
