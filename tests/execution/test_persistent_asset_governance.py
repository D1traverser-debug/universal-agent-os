import json
from pathlib import Path

import pytest

from uaos.execution import (
    AssetLifecycle,
    AssetRole,
    CrudOperation,
    MigrationObservation,
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
    surface=PersistentSurface.GITHUB,
    role=AssetRole.AUTHORITY,
    lifecycle=AssetLifecycle.CURRENT,
    owner="DOMAIN:financial_writing",
    ops=frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
    ref="github://D1traverser-debug/financial-writing-agent@main",
):
    return PersistentAssetDescriptor(
        asset_id=asset_id,
        surface=surface,
        role=role,
        lifecycle=lifecycle,
        owner_authority=owner,
        allowed_operations=ops,
        canonical_authority_ref=ref if role is AssetRole.AUTHORITY else None,
    )


def test_current_authority_requires_canonical_ref_and_non_temporary_surface():
    gate = PersistentAssetGate()
    with pytest.raises(PersistentAssetViolation, match="canonical_authority_ref"):
        gate.require_descriptor(
            PersistentAssetDescriptor(
                asset_id="missing-ref",
                surface=PersistentSurface.GITHUB,
                role=AssetRole.AUTHORITY,
                lifecycle=AssetLifecycle.CURRENT,
                owner_authority="UAOS",
                allowed_operations=frozenset({CrudOperation.READ}),
            )
        )
    with pytest.raises(PersistentAssetViolation, match="TEMP_SANDBOX"):
        gate.require_descriptor(
            PersistentAssetDescriptor(
                asset_id="tmp-authority",
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
    for role in (AssetRole.BOOTSTRAP, AssetRole.DELIVERY, AssetRole.DELIVERY_HISTORY, AssetRole.MIGRATED_HISTORY):
        with pytest.raises(PersistentAssetViolation):
            gate.require_descriptor(asset(asset_id=role.value, role=role, lifecycle=AssetLifecycle.CURRENT))


def test_decommissioned_drive_or_library_asset_cannot_update_or_output():
    gate = PersistentAssetGate()
    old_router = asset(
        asset_id="old-drive-router",
        surface=PersistentSurface.GOOGLE_DRIVE,
        role=AssetRole.MIGRATED_HISTORY,
        lifecycle=AssetLifecycle.DECOMMISSIONED,
        ops=frozenset({CrudOperation.READ, CrudOperation.UPDATE, CrudOperation.OUTPUT, CrudOperation.ARCHIVE}),
    )
    for operation in (CrudOperation.UPDATE, CrudOperation.OUTPUT):
        with pytest.raises(PersistentAssetViolation, match="retired asset"):
            gate.require(
                PersistentAssetRequest(
                    operation=operation,
                    descriptor=old_router,
                    active_authority="DOMAIN:financial_writing",
                    target_authority="DOMAIN:financial_writing",
                )
            )


def test_mutation_requires_target_authority_matching_asset_owner():
    gate = PersistentAssetGate()
    current = asset()
    with pytest.raises(PersistentAssetViolation, match="active_authority"):
        gate.require(PersistentAssetRequest(CrudOperation.UPDATE, current, None, "DOMAIN:financial_writing"))
    with pytest.raises(PersistentAssetViolation, match="target_authority"):
        gate.require(PersistentAssetRequest(CrudOperation.UPDATE, current, "UAOS", "UAOS"))


def test_reading_chat_memory_or_reference_is_allowed_but_not_authority():
    gate = PersistentAssetGate()
    for surface in (PersistentSurface.CHAT, PersistentSurface.MEMORY, PersistentSurface.NOTION):
        reference = asset(
            asset_id=f"ref-{surface.value}",
            surface=surface,
            role=AssetRole.REFERENCE,
            lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
            ops=frozenset({CrudOperation.READ}),
        )
        gate.require(PersistentAssetRequest(CrudOperation.READ, reference, None, None))
        assert reference.role is not AssetRole.AUTHORITY


def test_library_docx_is_delivery_history_not_task_state():
    gate = PersistentAssetGate()
    delivery = asset(
        asset_id="cross-border-final.docx",
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
        )
    )
    assert delivery.canonical_authority_ref is None


def test_custom_instructions_is_bootstrap_only():
    gate = PersistentAssetGate()
    bootstrap = asset(
        asset_id="uaos-custom-instructions",
        surface=PersistentSurface.CUSTOM_INSTRUCTIONS,
        role=AssetRole.BOOTSTRAP,
        lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
        ops=frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
        owner="UAOS",
    )
    gate.require(PersistentAssetRequest(CrudOperation.UPDATE, bootstrap, "UAOS", "UAOS"))
    assert bootstrap.role is AssetRole.BOOTSTRAP


def test_automation_role_cannot_become_business_state_authority():
    gate = PersistentAssetGate()
    automation = asset(
        asset_id="uaos-capability-audit",
        surface=PersistentSurface.AUTOMATION,
        role=AssetRole.AUTOMATION,
        lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
        ops=frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
        owner="UAOS",
    )
    gate.require(PersistentAssetRequest(CrudOperation.READ, automation, None, None))
    assert automation.role is not AssetRole.AUTHORITY


def test_migration_cannot_close_until_target_verified_and_source_retired():
    gate = PersistentAssetGate()
    source = asset(
        asset_id="legacy-library-pointer",
        surface=PersistentSurface.LIBRARY,
        role=AssetRole.MIGRATED_HISTORY,
        lifecycle=AssetLifecycle.DECOMMISSIONED,
        ops=frozenset({CrudOperation.READ, CrudOperation.ARCHIVE, CrudOperation.DELETE}),
    )
    target = asset(asset_id="financial-main")
    with pytest.raises(PersistentAssetViolation, match="target must be verified"):
        gate.require_migration_closed(MigrationObservation(source, target, False, True))
    with pytest.raises(PersistentAssetViolation, match="source must be retired"):
        gate.require_migration_closed(MigrationObservation(source, target, True, False))
    gate.require_migration_closed(MigrationObservation(source, target, True, True))


def test_reconciliation_detects_stale_or_unexpected_authority_and_works_with_generator():
    current = asset(asset_id="financial-main")
    old = asset(
        asset_id="drive-router",
        surface=PersistentSurface.GOOGLE_DRIVE,
        role=AssetRole.MIGRATED_HISTORY,
        lifecycle=AssetLifecycle.DECOMMISSIONED,
        ops=frozenset({CrudOperation.READ, CrudOperation.ARCHIVE}),
    )
    report = reconcile_asset_inventory(
        (item for item in (current, old)),
        expected_current_authority_refs=frozenset({"github://D1traverser-debug/financial-writing-agent@main"}),
    )
    assert report.admitted
    assert report.current_authority_assets == ("financial-main",)
    assert report.retired_assets == ("drive-router",)


def test_policy_declares_cross_surface_invariants_and_executable_refs():
    policy = json.loads((ROOT / "config/PERSISTENT_ASSET_POLICY.json").read_text(encoding="utf-8"))
    assert policy["status"] == "CANDIDATE"
    assert "SEARCH_PRESENCE_IS_NOT_AUTHORITY" in policy["invariants"]
    assert "MIGRATION_CLOSURE_REQUIRES_TARGET_VERIFIED_AND_SOURCE_RETIRED_OR_EXPLICITLY_ARCHIVED" in policy["invariants"]
    assert policy["executable_ref"].endswith("#PersistentAssetGate")
    assert "TEMP_SANDBOX" in policy["surfaces"]
