from datetime import UTC, datetime
import pytest
from uaos.contracts.enums import IntentType, RequirementState, ScopeType, TaskStatus
from uaos.contracts.models import RequirementRecord
from uaos.kernel import (
    AmbiguousControlTarget, ControlCommand, RequirementContext, SubsystemDescriptor,
    TopologyRegistry, TaskCandidate, effective_requirements, resolve_control_target,
)

NOW=datetime(2026,10,14,tzinfo=UTC)
def cand(task_id,domain,kind,*,default=False,status=TaskStatus.RUNNING):
    return TaskCandidate(task_id,domain,kind,status,NOW,True,default)

def test_new_task_and_maintenance_never_resume_business_task():
    candidates=(cand('old','financial_writing','article',default=True),)
    assert resolve_control_target(ControlCommand(IntentType.NEW_TASK,'financial_writing'),candidates).mode=='CREATE_NEW'
    m=resolve_control_target(ControlCommand(IntentType.SYSTEM_MAINTENANCE,'financial_writing'),candidates)
    assert m.mode=='MAINTENANCE' and m.task_id is None

def test_bare_continue_uses_single_explicit_default_not_recency_guess():
    candidates=(cand('a','financial_writing','article',default=True),cand('b','video','short_video'))
    assert resolve_control_target(ControlCommand(IntentType.CONTINUE),candidates).task_id=='a'
    with pytest.raises(AmbiguousControlTarget):
        resolve_control_target(ControlCommand(IntentType.CONTINUE),(cand('a','x','t'),cand('b','y','t')))

def test_effective_requirements_apply_scope_and_explicit_supersession():
    reqs=(
        RequirementRecord('g','global',ScopeType.GLOBAL,priority=10),
        RequirementRecord('old','old-video',ScopeType.SUBSYSTEM,'video',priority=20),
        RequirementRecord('new','new-video',ScopeType.SUBSYSTEM,'video',priority=20,supersedes=('old',)),
        RequirementRecord('task','task-only',ScopeType.TASK,'v1',priority=30),
        RequirementRecord('other','other',ScopeType.SUBSYSTEM,'novel',priority=100),
    )
    result=effective_requirements(reqs,RequirementContext('video','short_video','v1'))
    assert [r.requirement_id for r in result]==['task','new','g']

def test_topology_locates_owner_and_computes_transitive_change_impact():
    r=TopologyRegistry()
    r.register(SubsystemDescriptor('kernel','core','src/uaos/kernel',state_refs=('postgres:task',),validation_refs=('tests:kernel',)))
    r.register(SubsystemDescriptor('video','video-owner','domains/video',parent_id='kernel',dependencies=('kernel',),rule_refs=('domains/video/policy.json',)))
    r.register(SubsystemDescriptor('video-render','video-owner','adapters/render',parent_id='video',dependencies=('video',)))
    r.bind_authority('task.truth','kernel')
    assert r.authority_owner('task.truth')=='kernel'
    assert r.impact_closure('kernel')==frozenset({'kernel','video','video-render'})
    with pytest.raises(ValueError,match='dependents'):
        r.retire('kernel')

def test_authority_rebinding_is_explicit():
    r=TopologyRegistry(); r.register(SubsystemDescriptor('old','a','old')); r.register(SubsystemDescriptor('new','b','new'))
    r.bind_authority('knowledge.truth','old')
    with pytest.raises(ValueError,match='already bound'):
        r.bind_authority('knowledge.truth','new')
    r.bind_authority('knowledge.truth','new',replace_existing=True)
    assert r.authority_owner('knowledge.truth')=='new'
