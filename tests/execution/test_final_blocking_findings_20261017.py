from __future__ import annotations

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
)


class _UnknownThenConfirmedExecutor:
    def __init__(self) -> None:
        self.reconciled_unknown = None

    def execute(self, request: ExecutionRequest) -> ExecutionOutcome:
        return ExecutionOutcome(
            ExecutionDisposition.UNKNOWN,
            evidence={"operation_ref": "owned"},
            error="ambiguous",
        )

    def reconcile(self, request: ExecutionRequest, unknown: ExecutionOutcome) -> ExecutionOutcome:
        self.reconciled_unknown = unknown
        return ExecutionOutcome(ExecutionDisposition.CONFIRMED, output="resolved")


def _coordinator_fixture():
    registry = CapabilityRegistry()
    executor = _UnknownThenConfirmedExecutor()
    registry.register(
        CapabilityObservation(
            capability_id="writer",
            health=CapabilityHealth.AVAILABLE,
            observed_at_epoch=1.0,
            supported_actions=("write",),
            permissions=("repo:write",),
            quality_score=1.0,
            estimated_cost=0.0,
            executor_kind="test",
        ),
        executor,
        mutation_contracts={
            "write": MutationContract(
                MutationPersistence.DURABLE_OR_EXTERNAL,
                CrudOperation.UPDATE,
            )
        },
        canonicalize_target=lambda target: target,
    )
    catalog = PersistentAssetCatalog(
        (
            PersistentAssetDescriptor(
                asset_id="repo:file",
                resource_ref="repo:file",
                surface=PersistentSurface.GITHUB,
                role=AssetRole.AUTHORITY,
                lifecycle=AssetLifecycle.CURRENT,
                owner_authority="UAOS",
                allowed_operations=frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
                canonical_authority_ref="github://D1traverser-debug/universal-agent-os@main",
            ),
        )
    )
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=catalog,
    )
    request = ExecutionRequest(
        action_id="write-1",
        action_name="write",
        target="repo:file",
        payload={"content": "x"},
        required_permissions=("repo:write",),
        target_authority="UAOS",
    )
    return registry, coordinator, request, executor


def test_registry_has_no_public_provider_invocation_bypass():
    registry, _, _, _ = _coordinator_fixture()
    public = registry.get("writer")
    assert public.registration_generation > 0
    assert not hasattr(registry, "execute_trusted")
    assert not hasattr(registry, "reconcile_trusted")


def test_public_disposition_singleton_mutation_does_not_alias_owned_unknown_truth():
    _, coordinator, request, executor = _coordinator_fixture()
    public_unknown = coordinator.execute(request)
    assert public_unknown.outcome.disposition is ExecutionDisposition.UNKNOWN
    member = public_unknown.outcome.disposition
    object.__setattr__(member, "mutable_aux", {"provider": "forged"})
    try:
        resolved = coordinator.reconcile(request, public_unknown)
        assert resolved.outcome.disposition is ExecutionDisposition.CONFIRMED
        retained = executor.reconciled_unknown
        assert retained is not None
        assert retained.disposition == ExecutionDisposition.UNKNOWN
        assert retained.disposition is not member
        assert not hasattr(retained.disposition, "mutable_aux")
    finally:
        try:
            delattr(member, "mutable_aux")
        except AttributeError:
            pass
