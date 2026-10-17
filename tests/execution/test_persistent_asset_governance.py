import json
from pathlib import Path

import pytest

from uaos.execution import (
    AssetLifecycle,
    AssetRole,
    CrudOperation,
    MigrationObservation,
    MutationContract,
    MutationPersistence,
    PersistentAssetCatalog,
    PersistentAssetDescriptor,
    PersistentAssetGate,
    PersistentAssetRequest,
    PersistentAssetViolation,
    PersistentSurface,
    reconcile_asset_inventory,
)

ROOT = Path(__file__).resolve().parents[2]


def asset(
    *,
    asset_id="a",
    resource_ref="repo:file",
    surface=PersistentSurface.GITHUB,
    role=AssetRole.AUTHORITY,
    lifecycle=AssetLifecycle.CURRENT,
    owner="DOMAIN:financial_writing",
    ops=frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
    ref="github://D1traverser-debug/financial-writing-agent@main",
    migration_target_ref=None,
):
    return PersistentAssetDescriptor(
        asset_id=asset_id,
        resource_ref=resource_ref,
        surface=surface,
        role=role,
        lifecycle=lifecycle,
        owner_authority=owner,
        allowed_operations=ops,
        canonical_authority_ref=ref if role is AssetRole.AUTHORITY else None,
        migration_target_ref=migration_target_ref,
    )


def test_mutation_contract_separates_ephemeral_from_durable_and_rejects_read_mutation():
    assert MutationContract(MutationPersistence.EPHEMERAL).operation is None
    with pytest.raises(ValueError, match="ephemeral"):
        MutationContract(MutationPersistence.EPHEMERAL, CrudOperation.UPDATE)
    with pytest.raises(ValueError, match="non-READ"):
        MutationContract(MutationPersistence.DURABLE_OR_EXTERNAL, CrudOperation.READ)


def test_descriptor_requires_resource_identity_readability_and_current_authority_ref():
    gate = PersistentAssetGate()
    with pytest.raises(PersistentAssetViolation, match="resource_ref"):
        gate.require_descriptor(
            PersistentAssetDescriptor(
                asset_id="missing-resource",
                resource_ref="",
                surface=PersistentSurface.GITHUB,
                role=AssetRole.REFERENCE,
                lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
                owner_authority="UAOS",
                allowed_operations=frozenset({CrudOperation.READ}),
            )
        )
    with pytest.raises(PersistentAssetViolation, match="allow READ"):
        gate.require_descriptor(
            PersistentAssetDescriptor(
                asset_id="write-only",
                resource_ref="repo:write-only",
                surface=PersistentSurface.GITHUB,
                role=AssetRole.REFERENCE,
                lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
                owner_authority="UAOS",
                allowed_operations=frozenset({CrudOperation.UPDATE}),
            )
        )
    with pytest.raises(PersistentAssetViolation, match="canonical_authority_ref"):
        gate.require_descriptor(
            PersistentAssetDescriptor(
                asset_id="missing-ref",
                resource_ref="repo:file",
                surface=PersistentSurface.GITHUB,
                role=AssetRole.AUTHORITY,
                lifecycle=AssetLifecycle.CURRENT,
                owner_authority="UAOS",
                allowed_operations=frozenset({CrudOperation.READ}),
            )
        )


def test_current_authority_cannot_live_in_temporary_sandbox():
    gate = PersistentAssetGate()
    with pytest.raises(PersistentAssetViolation, match="TEMP_SANDBOX"):
        gate.require_descriptor(
            PersistentAssetDescriptor(
                asset_id="tmp-authority",
                resource_ref="sandbox:/mnt/data/current.json",
                surface=PersistentSurface.TEMP_SANDBOX,
                role=AssetRole.AUTHORITY,
                lifecycle=AssetLifecycle.CURRENT,
                owner_authority="UAOS",
                allowed_operations=frozenset({CrudOperation.READ}),
                canonical_authority_ref="sandbox:/mnt/data/current.json",
            )
        )


def test_bootstrap_delivery_and_history_cannot_claim_current_lifecycle():
    gate = PersistentAssetGate()
    for role in (
        AssetRole.BOOTSTRAP,
        AssetRole.DELIVERY,
        AssetRole.DELIVERY_HISTORY,
        AssetRole.MIGRATED_HISTORY,
    ):
        with pytest.raises(PersistentAssetViolation):
            gate.require_descriptor(
                asset(asset_id=role.value, role=role, lifecycle=AssetLifecycle.CURRENT)
            )


def test_catalog_is_trusted_single_descriptor_per_canonical_resource():
    one = asset(asset_id="one", resource_ref="repo:same")
    two = asset(asset_id="two", resource_ref="repo:same")
    with pytest.raises(PersistentAssetViolation, match="duplicate catalog resource_ref"):
        PersistentAssetCatalog((one, two))
    catalog = PersistentAssetCatalog((one,))
    assert catalog.resolve("repo:same") == one
    with pytest.raises(PersistentAssetViolation, match="not registered"):
        catalog.resolve("repo:missing")


def test_gate_binds_trusted_descriptor_to_canonical_executor_target():
    gate = PersistentAssetGate()
    descriptor = asset(resource_ref="repo:allowed")
    with pytest.raises(PersistentAssetViolation, match="canonical executor target"):
        gate.require(
            PersistentAssetRequest(
                CrudOperation.UPDATE,
                descriptor,
                "DOMAIN:financial_writing",
                "DOMAIN:financial_writing",
                "repo:different",
            )
        )


def test_decommissioned_drive_or_library_asset_cannot_update_or_output():
    gate = PersistentAssetGate()
    old_router = asset(
        asset_id="old-drive-router",
        resource_ref="drive:old-router",
        surface=PersistentSurface.GOOGLE_DRIVE,
        role=AssetRole.MIGRATED_HISTORY,
        lifecycle=AssetLifecycle.DECOMMISSIONED,
        ops=frozenset(
            {
                CrudOperation.READ,
                CrudOperation.UPDATE,
                CrudOperation.OUTPUT,
                CrudOperation.ARCHIVE,
            }
        ),
    )
    for operation in (CrudOperation.UPDATE, CrudOperation.OUTPUT):
        with pytest.raises(PersistentAssetViolation, match="retired asset"):
            gate.require(
                PersistentAssetRequest(
                    operation=operation,
                    descriptor=old_router,
                    active_authority="DOMAIN:financial_writing",
                    target_authority="DOMAIN:financial_writing",
                    canonical_execution_target="drive:old-router",
                )
            )


def test_mutation_requires_target_authority_matching_trusted_asset_owner():
    gate = PersistentAssetGate()
    current = asset()
    with pytest.raises(PersistentAssetViolation, match="active_authority"):
        gate.require(
            PersistentAssetRequest(
                CrudOperation.UPDATE,
                current,
                None,
                "DOMAIN:financial_writing",
                "repo:file",
            )
        )
    with pytest.raises(PersistentAssetViolation, match="trusted persistent asset owner"):
        gate.require(
            PersistentAssetRequest(
                CrudOperation.UPDATE,
                current,
                "UAOS",
                "UAOS",
                "repo:file",
            )
        )


def test_library_delivery_is_output_history_not_task_state():
    gate = PersistentAssetGate()
    delivery = asset(
        asset_id="cross-border-final.docx",
        resource_ref="library:/Financial/cross-border-final.docx",
        surface=PersistentSurface.LIBRARY,
        role=AssetRole.DELIVERY_HISTORY,
        lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
        ops=frozenset({CrudOperation.READ, CrudOperation.OUTPUT}),
    )
    gate.require(
        PersistentAssetRequest(
            CrudOperation.OUTPUT,
            delivery,
            "DOMAIN:financial_writing",
            "DOMAIN:financial_writing",
            delivery.resource_ref,
        )
    )
    assert delivery.canonical_authority_ref is None


def test_migration_closure_binds_declared_and_observed_source_target_identities():
    gate = PersistentAssetGate()
    target = asset(asset_id="financial-main", resource_ref="repo:financial-main")
    source = asset(
        asset_id="legacy-library-pointer",
        resource_ref="library:/Financial/legacy-pointer.md",
        surface=PersistentSurface.LIBRARY,
        role=AssetRole.MIGRATED_HISTORY,
        lifecycle=AssetLifecycle.DECOMMISSIONED,
        ops=frozenset({CrudOperation.READ, CrudOperation.ARCHIVE, CrudOperation.DELETE}),
        migration_target_ref=target.resource_ref,
    )
    with pytest.raises(PersistentAssetViolation, match="independently verified"):
        gate.require_migration_closed(
            MigrationObservation(
                source,
                target,
                False,
                True,
                source.resource_ref,
                target.resource_ref,
            )
        )
    with pytest.raises(PersistentAssetViolation, match="target identity mismatch"):
        gate.require_migration_closed(
            MigrationObservation(
                source,
                target,
                True,
                True,
                source.resource_ref,
                "repo:other",
            )
        )
    wrong_target = asset(asset_id="other", resource_ref="repo:other")
    with pytest.raises(PersistentAssetViolation, match="migration_target_ref"):
        gate.require_migration_closed(
            MigrationObservation(
                source,
                wrong_target,
                True,
                True,
                source.resource_ref,
                wrong_target.resource_ref,
            )
        )
    gate.require_migration_closed(
        MigrationObservation(
            source,
            target,
            True,
            True,
            source.resource_ref,
            target.resource_ref,
        )
    )


def test_reconciliation_detects_stale_or_unexpected_authority_and_works_with_generator():
    current = asset(asset_id="financial-main", resource_ref="repo:financial-main")
    old = asset(
        asset_id="drive-router",
        resource_ref="drive:legacy-router",
        surface=PersistentSurface.GOOGLE_DRIVE,
        role=AssetRole.MIGRATED_HISTORY,
        lifecycle=AssetLifecycle.DECOMMISSIONED,
        ops=frozenset({CrudOperation.READ, CrudOperation.ARCHIVE}),
    )
    report = reconcile_asset_inventory(
        (item for item in (current, old)),
        expected_current_authority_refs=frozenset(
            {"github://D1traverser-debug/financial-writing-agent@main"}
        ),
    )
    assert report.admitted
    assert report.current_authority_assets == ("financial-main",)
    assert report.retired_assets == ("drive-router",)


def test_policy_declares_cross_surface_invariants_and_executable_refs():
    policy = json.loads(
        (ROOT / "config/PERSISTENT_ASSET_POLICY.json").read_text(encoding="utf-8")
    )
    assert "SEARCH_PRESENCE_IS_NOT_AUTHORITY" in policy["invariants"]
    assert (
        "MIGRATION_CLOSURE_REQUIRES_TARGET_VERIFIED_AND_SOURCE_RETIRED_OR_EXPLICITLY_ARCHIVED"
        in policy["invariants"]
    )
    assert policy["executable_ref"].endswith("#PersistentAssetGate")
    assert "TEMP_SANDBOX" in policy["surfaces"]
