import pytest

from uaos.execution import (
    AssetLifecycle,
    AssetRole,
    CrudOperation,
    PersistentAssetDescriptor,
    PersistentAssetGate,
    PersistentAssetViolation,
    PersistentSurface,
)


def test_local_workspace_is_first_class_persistent_surface():
    asset = PersistentAssetDescriptor(
        asset_id="local-policy",
        resource_ref="file:///tmp/workspace/policy.txt",
        surface=PersistentSurface.LOCAL_WORKSPACE,
        role=AssetRole.EXTERNAL_RECORD,
        lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
        owner_authority="UAOS",
        allowed_operations=frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
    )
    PersistentAssetGate().require_descriptor(asset)
    assert asset.surface is PersistentSurface.LOCAL_WORKSPACE


def test_temp_sandbox_cannot_be_delivery_or_admit_output_migrate_archive():
    gate = PersistentAssetGate()
    for role in (
        AssetRole.AUTHORITY,
        AssetRole.DELIVERY,
        AssetRole.DELIVERY_HISTORY,
        AssetRole.MIGRATED_HISTORY,
        AssetRole.ARCHIVE,
    ):
        with pytest.raises(PersistentAssetViolation, match="TEMP_SANDBOX"):
            gate.require_descriptor(
                PersistentAssetDescriptor(
                    asset_id=f"tmp-{role.value}",
                    resource_ref=f"sandbox:/mnt/data/{role.value}",
                    surface=PersistentSurface.TEMP_SANDBOX,
                    role=role,
                    lifecycle=AssetLifecycle.TEMPORARY,
                    owner_authority="UAOS",
                    allowed_operations=frozenset({CrudOperation.READ}),
                )
            )

    for operation in (CrudOperation.OUTPUT, CrudOperation.MIGRATE, CrudOperation.ARCHIVE):
        with pytest.raises(PersistentAssetViolation, match="terminal/promotion"):
            gate.require_descriptor(
                PersistentAssetDescriptor(
                    asset_id=f"tmp-{operation.value}",
                    resource_ref=f"sandbox:/mnt/data/{operation.value}",
                    surface=PersistentSurface.TEMP_SANDBOX,
                    role=AssetRole.REFERENCE,
                    lifecycle=AssetLifecycle.TEMPORARY,
                    owner_authority="UAOS",
                    allowed_operations=frozenset({CrudOperation.READ, operation}),
                )
            )


def test_temp_sandbox_allows_internal_working_mutations_only():
    asset = PersistentAssetDescriptor(
        asset_id="tmp-working",
        resource_ref="sandbox:/mnt/data/work.tmp",
        surface=PersistentSurface.TEMP_SANDBOX,
        role=AssetRole.REFERENCE,
        lifecycle=AssetLifecycle.TEMPORARY,
        owner_authority="UAOS",
        allowed_operations=frozenset(
            {CrudOperation.READ, CrudOperation.CREATE, CrudOperation.UPDATE, CrudOperation.DELETE}
        ),
    )
    PersistentAssetGate().require_descriptor(asset)
