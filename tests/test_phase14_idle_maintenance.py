import pytest
from uaos.evolution import MaintenanceRequest, MaintenanceRisk, assess_idle_maintenance
from uaos.kernel import RunnableWork, assess_idle_capacity


def test_idle_capacity_blocks_any_foreground_runnable_work():
    evidence=assess_idle_capacity((RunnableWork('t','foreground:1',200),))
    assert not evidence.allowed and evidence.foreground_work_ids==('foreground:1',)


def test_idle_capacity_allows_only_maintenance_when_resources_are_free():
    evidence=assess_idle_capacity((RunnableWork('m','maintenance:1',1,100,('maintenance-db',),'MAINTENANCE'),), maintenance_resource_keys=('maintenance-db',))
    assert evidence.allowed


def test_idle_capacity_blocks_resource_conflict_even_without_foreground_work():
    evidence=assess_idle_capacity((),active_resource_keys=('gpu:video',),maintenance_resource_keys=('gpu:video',))
    assert not evidence.allowed and evidence.conflicting_resources==('gpu:video',)


def test_idle_maintenance_requires_scheduler_admission_receipt():
    request=MaintenanceRequest('m1','system','IDLE',MaintenanceRisk.LOW,True,False)
    blocked=assess_idle_maintenance(request,idle_admission_verified=False)
    assert not blocked.allowed and any('scheduling authority' in reason for reason in blocked.reasons)
    allowed=assess_idle_maintenance(request,idle_admission_verified=True)
    assert allowed.allowed and allowed.mode=='DIAGNOSE_AND_PROPOSE'
