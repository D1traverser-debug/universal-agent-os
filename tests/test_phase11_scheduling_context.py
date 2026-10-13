import pytest
from uaos.contracts.context import ContextPacket
from uaos.contracts.context_budget import ContextBudget, validate_context_budget
from uaos.kernel import RunnableWork, select_non_conflicting


def test_scheduler_resolves_priority_and_shared_resource_competition():
    high=RunnableWork('high','h:1',200,100,('gpu:video',))
    low=RunnableWork('low','l:1',100,100,('gpu:video',))
    independent=RunnableWork('other','o:1',150,100,('web:search',))
    result=select_non_conflicting((low,independent,high),max_slots=2)
    assert [x.work_unit_id for x in result.selected]==['h:1','o:1']
    assert [x.work_unit_id for x in result.deferred]==['l:1']


def test_scheduler_parallelizes_non_conflicting_work_only_to_slot_limit():
    items=tuple(RunnableWork('t',f'w{i}',100,100,(f'r{i}',)) for i in range(4))
    result=select_non_conflicting(items,max_slots=3)
    assert len(result.selected)==3 and len(result.deferred)==1


def test_context_packet_must_fit_explicit_budget_instead_of_dumping_everything():
    packet=ContextPacket('t','w','goal','done',('r1',),('a1','a2'),('k1',),('ob1',),('ap1',),{})
    validate_context_budget(packet,ContextBudget(max_artifact_refs=2,max_knowledge_items=1,max_unresolved_obligations=1,max_approvals=1))
    with pytest.raises(ValueError,match='artifact refs'):
        validate_context_budget(packet,ContextBudget(max_artifact_refs=1,max_knowledge_items=1,max_unresolved_obligations=1,max_approvals=1))
