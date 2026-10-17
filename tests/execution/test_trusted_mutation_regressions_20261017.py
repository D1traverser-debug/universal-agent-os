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


def _coordinator_for_local(tmp_path: Path, target: str, operations: frozenset[CrudOperation]):
    registry = CapabilityRegistry()
    register_local_workspace_capability(registry, tmp_path)
    registered = registry.get("local.workspace")
    assert registered.canonicalize_target is not None
    descriptor = _asset(registered.canonicalize_target(target), operations)
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((descriptor,)),
    )
    return registry, coordinator


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
    assert created.outcome.evidence["commit_semantics"] == "ATOMIC_CREATE_NO_REPLACE"
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
    assert updated.outcome.evidence["commit_semantics"] == "BOUND_PARENT_ATOMIC_RENAME"
    assert (tmp_path / "policy.txt").read_text(encoding="utf-8") == "v2"


def test_local_create_never_overwrites_existing_target(tmp_path: Path):
    target = tmp_path / "existing.txt"
    target.write_text("original", encoding="utf-8")
    _, coordinator = _coordinator_for_local(
        tmp_path,
        "existing.txt",
        frozenset({CrudOperation.READ, CrudOperation.CREATE}),
    )
    result = coordinator.execute(
        ExecutionRequest(
            "create-existing",
            "local.create_text",
            "existing.txt",
            {"content": "attacker"},
            required_permissions=("workspace:write",),
            target_authority="UAOS",
        )
    )
    assert result.outcome.disposition is ExecutionDisposition.FAILED
    assert "already exists" in (result.outcome.error or "")
    assert target.read_text(encoding="utf-8") == "original"


def test_local_workspace_refuses_symlink_parent_escape(tmp_path: Path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir(exist_ok=True)
    link = tmp_path / "redirect"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable on this platform")

    registry = CapabilityRegistry()
    register_local_workspace_capability(registry, tmp_path)
    registered = registry.get("local.workspace")
    assert registered.canonicalize_target is not None
    canonical = registered.canonicalize_target("redirect/escape.txt")
    descriptor = _asset(canonical, frozenset({CrudOperation.READ, CrudOperation.CREATE}))
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((descriptor,)),
    )
    result = coordinator.execute(
        ExecutionRequest(
            "escape",
            "local.create_text",
            "redirect/escape.txt",
            {"content": "blocked"},
            required_permissions=("workspace:write",),
            target_authority="UAOS",
        )
    )
    assert result.outcome.disposition is ExecutionDisposition.FAILED
    assert not (outside / "escape.txt").exists()
