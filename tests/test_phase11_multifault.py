import time

from uaos.contracts.enums import ActionStatus
from uaos.contracts.models import ActionRecord
from uaos.execution import (
    ActionCoordinator,
    AssetLifecycle,
    AssetRole,
    CapabilityHealth,
    CapabilityObservation,
    CapabilityRegistry,
    CrudOperation,
    ExecutionDisposition,
    ExecutionOutcome,
    ExecutionRequest,
    MutationContract,
    MutationPersistence,
    PersistentAssetCatalog,
    PersistentAssetDescriptor,
    PersistentSurface,
    RetryPolicy,
    assess_retry,
)


class UnknownExecutor:
    def execute(self, request):
        return ExecutionOutcome(
            ExecutionDisposition.UNKNOWN,
            provider_ref="fallback:req-1",
            evidence={"sent": True},
        )

    def reconcile(self, request, unknown):
        return unknown


class NeverCalled:
    def execute(self, request):
        raise AssertionError("unavailable provider must never execute")


def test_provider_outage_plus_ambiguous_fallback_fails_closed_to_reconciliation():
    reg = CapabilityRegistry()
    now = time.time()
    reg.register(
        CapabilityObservation(
            "primary",
            CapabilityHealth.UNAVAILABLE,
            now,
            ("publish",),
            ("write",),
            1.0,
            1.0,
            "provider",
        ),
        NeverCalled(),
        mutation_contracts={
            "publish": MutationContract(
                MutationPersistence.DURABLE_OR_EXTERNAL, CrudOperation.OUTPUT
            )
        },
        canonicalize_target=lambda target: f"remote://{target}",
    )
    reg.register(
        CapabilityObservation(
            "fallback",
            CapabilityHealth.AVAILABLE,
            now,
            ("publish",),
            ("write",),
            0.9,
            2.0,
            "provider",
        ),
        UnknownExecutor(),
        mutation_contracts={
            "publish": MutationContract(
                MutationPersistence.DURABLE_OR_EXTERNAL, CrudOperation.OUTPUT
            )
        },
        canonicalize_target=lambda target: f"remote://{target}",
    )
    external_record = PersistentAssetDescriptor(
        asset_id="remote:item",
        resource_ref="remote://remote:item",
        surface=PersistentSurface.OTHER_EXTERNAL,
        role=AssetRole.EXTERNAL_RECORD,
        lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
        owner_authority="UAOS",
        allowed_operations=frozenset({CrudOperation.READ, CrudOperation.OUTPUT}),
    )
    request = ExecutionRequest(
        "a1",
        "publish",
        "remote:item",
        {"x": 1},
        required_permissions=("write",),
        parameter_hash="h",
        side_effect_class="WRITE",
        idempotency_key="idem",
        target_authority="UAOS",
        mutation_persistence=MutationPersistence.DURABLE_OR_EXTERNAL,
        persistent_asset=external_record,
        persistent_operation=CrudOperation.OUTPUT,
    )
    result = ActionCoordinator(
        reg,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((external_record,)),
    ).execute(request)
    assert result.capability_id == "fallback"
    assert result.outcome.disposition is ExecutionDisposition.UNKNOWN
    action = ActionRecord(
        "a1",
        "w1",
        "fallback",
        "h",
        "remote:item",
        "WRITE",
        ActionStatus.UNKNOWN,
        "idem",
    )
    retry = assess_retry(action, RetryPolicy("execution-fabric", 3))
    assert retry.action == "RECONCILE" and not retry.allowed
