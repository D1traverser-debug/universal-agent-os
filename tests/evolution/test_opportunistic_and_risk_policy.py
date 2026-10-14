from datetime import UTC,datetime,timedelta
from uaos.evolution import ChangeIntent,SelfChangeDisposition,assess_opportunistic_maintenance,decide_self_change

def test_due_maintenance_defers_behind_foreground_work():
    decision=assess_opportunistic_maintenance(now=datetime(2026,1,2,tzinfo=UTC),last_success=datetime(2026,1,1,tzinfo=UTC),max_interval=timedelta(hours=12),foreground_runnable=1)
    assert decision.due and not decision.run_now and "deferred behind foreground work" in decision.reasons

def test_recovery_runs_immediately_when_idle():
    now=datetime.now(UTC); decision=assess_opportunistic_maintenance(now=now,last_success=now,recovery_required=True,foreground_runnable=0)
    assert decision.run_now and decision.priority=="HIGH"

def test_low_risk_auto_applies_after_eval():
    assert decide_self_change(ChangeIntent("cache_index",True,True),evaluation_passed=True).disposition is SelfChangeDisposition.AUTO_APPLY

def test_medium_risk_stays_candidate_until_canary_and_rollback():
    assert decide_self_change(ChangeIntent("workflow_route",True,False),evaluation_passed=True).disposition is SelfChangeDisposition.SANDBOX_EVALUATE

def test_high_risk_requires_explicit_approval():
    assert decide_self_change(ChangeIntent("state_authority",True,True),evaluation_passed=True,explicit_approval=False).disposition is SelfChangeDisposition.REQUIRE_EXPLICIT_APPROVAL

def test_high_risk_can_apply_only_after_approval():
    assert decide_self_change(ChangeIntent("state_authority",True,True),evaluation_passed=True,explicit_approval=True).disposition is SelfChangeDisposition.APPLY_WITH_APPROVAL

def test_system_cannot_approve_own_authority_expansion():
    assert decide_self_change(ChangeIntent("permission_boundary",True,True,expands_authority=True),evaluation_passed=True,explicit_approval=True).disposition is SelfChangeDisposition.DENY_SELF_ESCALATION
