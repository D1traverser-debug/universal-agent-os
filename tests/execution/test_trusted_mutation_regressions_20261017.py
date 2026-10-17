from pathlib import Path

import pytest

from uaos.execution import (
    ActionCoordinator,
    AssetLifecycle,
    AssetRole,
    CapabilityRegistry,
    CrudOperation,
    ExecutionDisposition,
    ExecutionRequest,
    PersistentAssetCatalog,
    PersistentAssetDescriptor,
    PersistentAssetViolation,
    PersistentSurface,
    register_local_workspace_capability,
)


def test_json_string_descriptor_enums_are_normalized_before_identity_checks():
    descriptor = PersistentAssetDescriptor(
        asset_id="forged-temp-authority",
        resource_ref="sandbox:/mnt/data/current.json",
        surface="TEMP_SANDBOX",
        role="AUTHORITY",
        lifecycle="CURRENT",
        owner_authority="UAOS",
        allowed_operations=frozenset({"READ"}),
        canonical_authority_ref="sandbox:/mnt/data/current.json",
    )
    assert descriptor.surface is PersistentSurface.TEMP_SANDBOX
    assert descriptor.role is AssetRole.AUTHORITY
    assert descriptor.lifecycle is AssetLifecycle.CURRENT
    assert descriptor.allowed_operations == frozenset({CrudOperation.READ})
    with pytest.raises(PersistentAssetViolation, match="TEMP_SANDBOX"):
        PersistentAssetCatalog((descriptor,))


def _asset(resource_ref: str, operations: frozenset[CrudOperation]):
    return PersistentAssetDescriptor(
        asset_id=f"local:{resource_ref}",
        resource_ref=resource_ref,
        surface=PersistentSurface.LOCAL_WORKSPACE,
        role=AssetRole.EXTERNAL_RECORD,
        lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
        owner_authority="UAOS",
        allowed_operations=operations,
    )


def test_local_create_and_update_are_distinct_trusted_actions(tmp_path: Path):
    registry = CapabilityRegistry()
    register_local_workspace_capability(registry, tmp_path)
    registered = registry.get("local.workspace")
    assert registered.mutation_contracts["local.create_text"].operation is CrudOperation.CREATE
    assert registered.mutation_contracts["local.update_text"].operation is CrudOperation.UPDATE
    assert registered.canonicalize_target is not None

    canonical = registered.canonicalize_target("policy.txt")
    update_only = _asset(canonical, frozenset({CrudOperation.READ, CrudOperation.UPDATE}))
    update_coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((update_only,)),
    )
    create_request = ExecutionRequest(
        "create",
        "local.create_text",
        "policy.txt",
        {"content": "v1"},
        required_permissions=("workspace:write",),
        side_effect_class="READ",
        target_authority="UAOS",
    )
    with pytest.raises(PersistentAssetViolation, match="not admitted"):
        update_coordinator.execute(create_request)
    assert not (tmp_path / "policy.txt").exists()

    create_allowed = _asset(canonical, frozenset({CrudOperation.READ, CrudOperation.CREATE}))
    create_coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((create_allowed,)),
    )
    created = create_coordinator.execute(create_request)
    assert created.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert (tmp_path / "policy.txt").read_text(encoding="utf-8") == "v1"

    update_request = ExecutionRequest(
        "update",
        "local.update_text",
        "policy.txt",
        {"content": "v2"},
        required_permissions=("workspace:write",),
        side_effect_class="NONE",
        target_authority="UAOS",
    )
    with pytest.raises(PersistentAssetViolation, match="not admitted"):
        create_coordinator.execute(update_request)

    updated = update_coordinator.execute(update_request)
    assert updated.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert (tmp_path / "policy.txt").read_text(encoding="utf-8") == "v2"
