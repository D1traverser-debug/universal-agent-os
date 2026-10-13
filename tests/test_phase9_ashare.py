from datetime import UTC, datetime, timedelta
from pathlib import Path
import json
import pytest

from uaos.contracts.context import SourceSnapshot
from uaos.contracts.enums import IntentType, WorkStatus
from uaos.domain_sdk import DomainRegistry, load_domain_package
from uaos.kernel import expand_fanout

ROOT=Path(__file__).resolve().parents[1]

def reg():
    manifest, templates=load_domain_package(ROOT/'domains'/'ashare')
    r=DomainRegistry(); r.register(manifest,templates); return r

def test_source_snapshot_enforces_point_in_time_boundary_and_completeness():
    observed=datetime(2026,10,14,8,0,tzinfo=UTC)
    snap=SourceSnapshot('s','https://source','h',observed,'store://s',content_max_available_at=observed-timedelta(minutes=10),completeness='FULL')
    snap.assert_usable_for(observed-timedelta(minutes=5))
    with pytest.raises(ValueError,match='unavailable'):
        snap.assert_usable_for(observed-timedelta(minutes=20))
    partial=SourceSnapshot('p','https://source','h2',observed,'store://p',content_max_available_at=observed-timedelta(minutes=10),completeness='PARTIAL',gaps=('image table unread',))
    with pytest.raises(ValueError,match='not FULL'):
        partial.assert_usable_for(observed)

def test_full_snapshot_cannot_hide_gaps():
    now=datetime.now(UTC)
    with pytest.raises(ValueError,match='FULL'):
        SourceSnapshot('s','u','h',now,'store',content_max_available_at=now,completeness='FULL',gaps=('missing',))

def test_premarket_ticker_analysis_expands_as_first_class_work_units():
    r=reg(); plan=r.resolve_new_task('ashare',intent=IntentType.NEW_TASK,task_type='premarket').compile(task_id='m1',plan_id='p1')
    merge=next(u for u in plan.work_units if u.work_unit_id=='m1:rank_candidates')
    assert merge.status is WorkStatus.HOLD
    expanded=expand_fanout(plan,source_unit_id='m1:recall',source_artifact='candidate_universe',merge_unit_id='m1:rank_candidates',item_keys=('600000.SH','000001.SZ'),child_name='Analyze ticker',executor_constraints=('ashare.stock_analysis',),output_namespace='ticker_analysis',new_plan_id='p2',risk='HIGH')
    children=[u for u in expanded.work_units if ':fanout:' in u.work_unit_id]
    assert {dict(u.bindings)['item_key'] for u in children}=={'600000.SH','000001.SZ'}
    selection=next(u for u in expanded.work_units if u.work_unit_id=='m1:selection')
    assert 'm1:rank_candidates' in selection.dependencies

def test_postclose_is_separate_workflow_bound_to_frozen_decision():
    r=reg(); p=r.resolve_new_task('ashare',intent=IntentType.NEW_TASK,task_type='postclose_review').compile(task_id='r1',plan_id='p1')
    units={u.work_unit_id.split(':',1)[1]:u for u in p.work_units}
    assert 'frozen_decision_ref' in p.external_inputs
    assert set(units['reconcile'].dependencies)=={'r1:load_frozen','r1:outcomes'}
    assert 'premarket_cassette' in units['attribution'].required_inputs
    assert 'outcome_snapshot' not in units['load_frozen'].required_inputs

def test_single_day_learning_cannot_be_policy_promoted():
    policy=json.loads((ROOT/'domains'/'ashare'/'policy.json').read_text())
    assert policy['single_day_promotion_forbidden'] is True
    assert policy['future_contamination_forbidden'] is True
    assert policy['min_replay_cases']>=5
