from uaos.contracts.enums import ActionStatus
from uaos.contracts.models import ActionRecord
from uaos.execution import RetryPolicy, assess_retry
from uaos.runtime import CompatibilityMode, VersionCompatibilityPolicy


def action(status,*,attempt=1,key='idem',side='WRITE'):
    return ActionRecord('a','w','cap','hash','target',side,status,key,attempt=attempt)

def test_version_skew_is_direct_migrate_or_block_never_silent():
    p=VersionCompatibilityPolicy('v3',frozenset({'v2.1'}),{'v1':'mig-v1-v3'})
    assert p.decide('v3').mode is CompatibilityMode.DIRECT
    assert p.decide('v2.1').mode is CompatibilityMode.DIRECT
    assert p.decide('v1').mode is CompatibilityMode.MIGRATE
    assert p.decide('v0').mode is CompatibilityMode.BLOCK

def test_unknown_side_effect_is_reconciled_not_retried():
    d=assess_retry(action(ActionStatus.UNKNOWN),RetryPolicy('runtime',3))
    assert not d.allowed and d.action=='RECONCILE'

def test_side_effect_retry_requires_idempotency_and_budget():
    p=RetryPolicy('runtime',3)
    assert not assess_retry(action(ActionStatus.FAILED,key=None),p).allowed
    assert assess_retry(action(ActionStatus.FAILED,attempt=2,key='k'),p).allowed
    assert not assess_retry(action(ActionStatus.FAILED,attempt=3,key='k'),p).allowed
