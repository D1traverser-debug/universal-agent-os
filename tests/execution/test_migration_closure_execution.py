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


class MigrationExecutor:
    def __init__(self, evidence, disposition=ExecutionDisposition.CONFIRMED):
        self.evidence = evidence
        self.disposition = disposition
        self.calls = 0

    def execute(self, request):
        self.calls += 1
        return ExecutionOutcome(
            self.disposition,
            output="migration-close-attempt",
            evidence=self.evidence,
        )


def source_and_target():
    target = PersistentAssetDescriptor(
        asset_id="financial-main",
        resource_ref="repo:financial-main",
        surface=PersistentSurface.GITHUB,
        role=AssetRole.AUTHORITY,
        lifecycle=AssetLifecycle.CURRENT,
        owner_authority="UAOS",
        allowed_operations=frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
        canonical_authority_ref="github://financial@main",
    )
    source = PersistentAssetDescriptor(
        asset_id="legacy-pointer",
        resource_ref="library:legacy-pointer",
        surface=PersistentSurface.LIBRARY,
        role=AssetRole.MIGRATED_HISTORY,
        lifecycle=AssetLifecycle.DECOMMISSIONED,
        owner_authority="UAOS",
        allowed_operations=frozenset({CrudOperation.READ, CrudOperation.MIGRATE}),
        migration_target_ref=target.resource_ref,
    )
    return source, target


def coordinator_for(evidence, *, disposition=ExecutionDisposition.CONFIRMED):
    source, target = source_and_target()
    registry = CapabilityRegistry()
    executor = MigrationExecutor(evidence, disposition=disposition)
    registry.register(
        CapabilityObservation(
            capability_id="migration.closer",
            health=CapabilityHealth.AVAILABLE,
            observed_at_epoch=1.0,
            supported_actions=("migration.close",),
            permissions=("migration:close",),
            quality_score=1.0,
            estimated_cost=0.0,
            executor_kind="migration_test",
        ),
        executor,
        mutation_contracts={
            "migration.close": MutationContract(
                MutationPersistence.DURABLE_OR_EXTERNAL,
                CrudOperation.MIGRATE,
            )
        },
        canonicalize_target=lambda target_ref: target_ref,
    )
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((source, target)),
    )
    request = ExecutionRequest(
        action_id="close-migration",
        action_name="migration.close",
        target=source.resource_ref,
        payload={},
        required_permissions=("migration:close",),
        side_effect_class="WRITE",
        target_authority="UAOS",
    )
    return coordinator, request, source, target, executor


def test_executor_confirmed_is_downgraded_when_migration_closure_evidence_missing():
    coordinator, request, _, _, executor = coordinator_for({})
    result = coordinator.execute(request)
    assert executor.calls == 1
    assert result.outcome.disposition is ExecutionDisposition.UNKNOWN
    assert "migration closure unverified" in result.outcome.error


def test_string_confirmed_is_normalized_before_migration_closure_gate():
    coordinator, request, _, _, executor = coordinator_for({}, disposition="CONFIRMED")
    result = coordinator.execute(request)
    assert executor.calls == 1
    assert result.outcome.disposition is ExecutionDisposition.UNKNOWN
    assert "migration closure unverified" in result.outcome.error


def test_migration_closure_rejects_observed_target_identity_mismatch():
    coordinator, request, source, _, _ = coordinator_for(
        {
            "migration_target_verified": True,
            "migration_source_retired": True,
            "migration_source_ref": "library:legacy-pointer",
            "migration_target_ref": "repo:wrong-target",
        }
    )
    result = coordinator.execute(request)
    assert result.outcome.disposition is ExecutionDisposition.UNKNOWN
    assert source.resource_ref in request.target


def test_migration_closure_can_only_confirm_with_catalog_bound_complete_evidence():
    coordinator, request, source, target, _ = coordinator_for(
        {
            "migration_target_verified": True,
            "migration_source_retired": True,
            "migration_source_ref": "library:legacy-pointer",
            "migration_target_ref": "repo:financial-main",
        }
    )
    result = coordinator.execute(request)
    assert result.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert result.admission.persistent_operation is CrudOperation.MIGRATE
    assert result.admission.canonical_target == source.resource_ref
    assert target.resource_ref == "repo:financial-main"
