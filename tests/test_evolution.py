import pytest
from uaos.evolution import (
    ChangeProposal, ComplexityBudget, ComplexityDelta, EvaluationResult,
    EvolutionCatalog, FailureClass, Incident, MaintenanceRequest, MaintenanceRisk,
    PostPromotionObservation, ProposalState, assess_maintenance, assess_promotion,
    post_promotion_recommendation, transition_proposal,
)


def incident(i, fp="same"):
    return Incident(i,"recurring failure",fp,(f"evidence:{i}",))


def proposal(delta=ComplexityDelta(), *, added=(), replaced=(), retired=(), why="reuse insufficient", retirement="no overlap exists; reviewed", state=None):
    kwargs={'state': state if state is not None else ProposalState.EVALUATED}
    return ChangeProposal(
        "p1","repair root cause",("f1",),"mechanism X causes failure","kernel",
        added,replaced,retired,why,retirement,"revert commit and schema","eliminate recurrence",
        ("migration risk",),("scenario:recurrence","scenario:cross-domain"),delta,("incident:f1",),**kwargs
    )


def passed_eval(*, regressions=(), passed=True):
    return EvaluationResult("e1","p1",("scenario:recurrence","scenario:cross-domain"),{"failure_rate":1.0},{"failure_rate":0.0},{"primary_goal_met": True},regressions,passed,("eval:trace",))


def test_repeated_incidents_raise_systemic_failure_class():
    cat=EvolutionCatalog(); cat.add_incident(incident("i1")); cat.add_incident(incident("i2"))
    cat.add_failure_class(FailureClass("f1","same recurrence","execution",("i1",),"raw path bypasses gate"))
    assert not cat.is_systemic("f1")
    cat.attach_incident("f1","i2")
    assert cat.is_systemic("f1")
    assert len(cat.matching_incidents("same"))==2


def test_new_mechanism_requires_reuse_and_retirement_analysis():
    with pytest.raises(ValueError,match="why-not-reuse"):
        proposal(added=("new gate",),why="")
    with pytest.raises(ValueError,match="retirement"):
        proposal(added=("new gate",),retirement="")


def test_promotion_requires_real_eval_not_proposal_self_claim():
    decision=assess_promotion(proposal(),(),budget=ComplexityBudget())
    assert not decision.approved
    assert any("no evaluation" in reason for reason in decision.reasons)


def test_regression_blocks_promotion_even_when_primary_eval_passes():
    decision=assess_promotion(proposal(),(passed_eval(regressions=("resume regression",)),),budget=ComplexityBudget())
    assert not decision.approved
    assert "regression failures remain" in decision.reasons


def test_complexity_budget_blocks_growth_without_proportional_control():
    p=proposal(ComplexityDelta(added_components=4,removed_components=0,added_state_surfaces=3,maintenance_cost_delta=5))
    d=assess_promotion(p,(passed_eval(),),budget=ComplexityBudget(max_net_components=1,max_net_state_surfaces=1,max_maintenance_cost_delta=1))
    assert not d.approved
    assert len(d.reasons)>=3


def test_passing_candidate_only_authorizes_controlled_promotion_route():
    p=proposal(ComplexityDelta(added_components=1,removed_components=1),added=("mechanical gate",),retired=("prompt-only guard",),retirement="retire prompt-only guard after cutover")
    d=assess_promotion(p,(passed_eval(),),budget=ComplexityBudget())
    assert d.approved
    assert d.required_action_route=="execution.action_authority"


def test_idle_maintenance_requires_real_background_capability_and_yields_to_foreground():
    missing=assess_maintenance(MaintenanceRequest("m1","system","IDLE",MaintenanceRisk.LOW,False,False))
    assert not missing.allowed and "background" in missing.reasons[0]
    busy=assess_maintenance(MaintenanceRequest("m2","system","IDLE",MaintenanceRisk.LOW,True,True))
    assert not busy.allowed and any("foreground" in r for r in busy.reasons)


def test_maintenance_without_mutation_only_diagnoses_and_proposes():
    d=assess_maintenance(MaintenanceRequest("m1","video","EVENT",MaintenanceRisk.HIGH,True,False,False))
    assert d.allowed and d.mode=="DIAGNOSE_AND_PROPOSE"


def test_high_risk_production_maintenance_needs_exact_approval():
    blocked=assess_maintenance(MaintenanceRequest("m1","kernel","EVENT",MaintenanceRisk.HIGH,True,False,True))
    assert not blocked.allowed
    allowed=assess_maintenance(MaintenanceRequest("m2","kernel","EVENT",MaintenanceRisk.HIGH,True,False,True,"approval:change-1"))
    assert allowed.allowed and allowed.mode=="CONTROLLED_MUTATION"


def test_passing_evaluation_requires_all_acceptance_checks_true():
    with pytest.raises(ValueError, match="failed acceptance"):
        EvaluationResult("bad","p1",("scenario:x",),{"x":1.0},{"x":0.0},{"root_fixed":False},(),True,("trace",))


def test_proposal_lifecycle_forbids_skipping_evaluation_and_approval():
    draft=proposal(state=ProposalState.DRAFT)
    with pytest.raises(ValueError, match="invalid proposal transition"):
        transition_proposal(draft, ProposalState.PROMOTED)
    evaluated=transition_proposal(draft, ProposalState.EVALUATED)
    approved=transition_proposal(evaluated, ProposalState.APPROVED)
    promoted=transition_proposal(approved, ProposalState.PROMOTED)
    assert promoted.state is ProposalState.PROMOTED


def test_post_promotion_regression_recommends_rollback():
    p=proposal(state=ProposalState.DRAFT)
    p=transition_proposal(transition_proposal(transition_proposal(p,ProposalState.EVALUATED),ProposalState.APPROVED),ProposalState.PROMOTED)
    clean=PostPromotionObservation("o1","p1",True,{"error_rate":0.0},("obs:1",))
    assert post_promotion_recommendation(p,(clean,))=="KEEP_OBSERVING"
    bad=PostPromotionObservation("o2","p1",False,{"error_rate":0.2},("obs:2",),("regression:resume",))
    assert post_promotion_recommendation(p,(clean,bad))=="ROLLBACK"


def test_promotion_requires_declared_scenario_coverage():
    p=proposal()
    narrow=EvaluationResult("e2","p1",("scenario:recurrence",),{"failure_rate":1.0},{"failure_rate":0.0},{"root_fixed":True},(),True,("trace:narrow",))
    d=assess_promotion(p,(narrow,),budget=ComplexityBudget())
    assert not d.approved
    assert any("scenarios missing" in reason for reason in d.reasons)
