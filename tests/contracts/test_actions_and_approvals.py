from datetime import UTC, datetime, timedelta
import pytest
from uaos.contracts.enums import ActionStatus
from uaos.contracts.models import ActionRecord, Approval
from uaos.contracts.state_machines import transition_action


def action() -> ActionRecord:
    return ActionRecord(action_id="a1", work_unit_id="w1", capability_id="github.write", request_hash="reqhash", target="repo:file", side_effect_class="WRITE", idempotency_key="idem-1")


def test_ambiguous_outcome_must_reconcile_before_confirmation():
    sent = transition_action(action(), ActionStatus.SENT, provider_ref="remote-1")
    unknown = transition_action(sent, ActionStatus.UNKNOWN, outcome="timeout-after-send")
    with pytest.raises(ValueError, match="invalid action transition"):
        transition_action(unknown, ActionStatus.CONFIRMED)
    reconciled = transition_action(unknown, ActionStatus.RECONCILED, outcome="remote-found")
    confirmed = transition_action(reconciled, ActionStatus.CONFIRMED, outcome="success")
    assert confirmed.status is ActionStatus.CONFIRMED


def test_failed_action_is_terminal():
    failed = transition_action(action(), ActionStatus.FAILED, outcome="preflight rejected")
    with pytest.raises(ValueError):
        transition_action(failed, ActionStatus.SENT)


def test_approval_is_bound_to_exact_action_target_and_parameter_hash():
    now = datetime.now(UTC)
    approval = Approval(approval_id="p1", action_id="a1", target="repo:file", parameter_hash="h1", approver="user", granted_at=now, expires_at=now + timedelta(minutes=10))
    assert approval.authorizes(action_id="a1", target="repo:file", parameter_hash="h1", now=now)
    assert not approval.authorizes(action_id="a2", target="repo:file", parameter_hash="h1", now=now)
    assert not approval.authorizes(action_id="a1", target="repo:other", parameter_hash="h1", now=now)
    assert not approval.authorizes(action_id="a1", target="repo:file", parameter_hash="h2", now=now)
