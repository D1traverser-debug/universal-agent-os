from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class PersistentAssetViolation(ValueError):
    pass


class PersistentSurface(str, Enum):
    GITHUB = "GITHUB"
    CHAT = "CHAT"
    LIBRARY = "LIBRARY"
    MEMORY = "MEMORY"
    CUSTOM_INSTRUCTIONS = "CUSTOM_INSTRUCTIONS"
    AUTOMATION = "AUTOMATION"
    NOTION = "NOTION"
    GOOGLE_DRIVE = "GOOGLE_DRIVE"
    GMAIL = "GMAIL"
    GOOGLE_CALENDAR = "GOOGLE_CALENDAR"
    OTHER_EXTERNAL = "OTHER_EXTERNAL"
    TEMP_SANDBOX = "TEMP_SANDBOX"


class AssetRole(str, Enum):
    AUTHORITY = "AUTHORITY"
    BOOTSTRAP = "BOOTSTRAP"
    REFERENCE = "REFERENCE"
    SHARED_RESOURCE = "SHARED_RESOURCE"
    DELIVERY = "DELIVERY"
    DELIVERY_HISTORY = "DELIVERY_HISTORY"
    MIGRATED_HISTORY = "MIGRATED_HISTORY"
    ARCHIVE = "ARCHIVE"
    AUTOMATION = "AUTOMATION"
    EXTERNAL_RECORD = "EXTERNAL_RECORD"


class AssetLifecycle(str, Enum):
    CURRENT = "CURRENT"
    ACTIVE_NON_AUTHORITY = "ACTIVE_NON_AUTHORITY"
    MIGRATED = "MIGRATED"
    DECOMMISSIONED = "DECOMMISSIONED"
    ARCHIVED = "ARCHIVED"
    DELETE_CANDIDATE = "DELETE_CANDIDATE"
    TEMPORARY = "TEMPORARY"


class CrudOperation(str, Enum):
    READ = "READ"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    OUTPUT = "OUTPUT"
    MIGRATE = "MIGRATE"
    ARCHIVE = "ARCHIVE"


_RETIRED_LIFECYCLES = {
    AssetLifecycle.MIGRATED,
    AssetLifecycle.DECOMMISSIONED,
    AssetLifecycle.ARCHIVED,
    AssetLifecycle.DELETE_CANDIDATE,
}
_RETIRED_ALLOWED_OPS = {CrudOperation.READ, CrudOperation.ARCHIVE, CrudOperation.DELETE}
_NON_AUTHORITY_ROLES = {
    AssetRole.BOOTSTRAP,
    AssetRole.REFERENCE,
    AssetRole.SHARED_RESOURCE,
    AssetRole.DELIVERY,
    AssetRole.DELIVERY_HISTORY,
    AssetRole.MIGRATED_HISTORY,
    AssetRole.ARCHIVE,
    AssetRole.AUTOMATION,
    AssetRole.EXTERNAL_RECORD,
}


@dataclass(frozen=True, slots=True)
class PersistentAssetDescriptor:
    asset_id: str
    surface: PersistentSurface
    role: AssetRole
    lifecycle: AssetLifecycle
    owner_authority: str
    allowed_operations: frozenset[CrudOperation]
    canonical_authority_ref: str | None = None
    migration_target_ref: str | None = None


@dataclass(frozen=True, slots=True)
class PersistentAssetRequest:
    operation: CrudOperation
    descriptor: PersistentAssetDescriptor
    active_authority: str | None
    target_authority: str | None


@dataclass(frozen=True, slots=True)
class MigrationObservation:
    source: PersistentAssetDescriptor
    target: PersistentAssetDescriptor
    target_verified: bool
    source_retired: bool


@dataclass(frozen=True, slots=True)
class AssetReconciliationReport:
    current_authority_assets: tuple[str, ...]
    non_authority_assets: tuple[str, ...]
    retired_assets: tuple[str, ...]
    temporary_assets: tuple[str, ...]
    violations: tuple[str, ...]

    @property
    def admitted(self) -> bool:
        return not self.violations


def _nonempty(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


class PersistentAssetGate:
    """Fail-closed classification/admission for durable assets across surfaces.

    This gate governs what is being mutated and where it lives. It does not replace
    AuthorityScopeGate, owner-specific approvals, repository checks, or connector
    permissions; those remain independent gates.
    """

    def require_descriptor(self, descriptor: PersistentAssetDescriptor) -> None:
        if not _nonempty(descriptor.asset_id):
            raise PersistentAssetViolation("persistent asset requires asset_id")
        if not _nonempty(descriptor.owner_authority):
            raise PersistentAssetViolation("persistent asset requires owner_authority")
        if not descriptor.allowed_operations:
            raise PersistentAssetViolation("persistent asset requires allowed_operations")

        if descriptor.role is AssetRole.AUTHORITY:
            if descriptor.lifecycle is not AssetLifecycle.CURRENT:
                raise PersistentAssetViolation("authority asset must use CURRENT lifecycle")
            if not _nonempty(descriptor.canonical_authority_ref):
                raise PersistentAssetViolation("authority asset requires canonical_authority_ref")
            if descriptor.surface is PersistentSurface.TEMP_SANDBOX:
                raise PersistentAssetViolation("TEMP_SANDBOX cannot own current authority")
        elif descriptor.lifecycle is AssetLifecycle.CURRENT:
            raise PersistentAssetViolation("CURRENT lifecycle is reserved for authority assets")

        if descriptor.role is AssetRole.MIGRATED_HISTORY and descriptor.lifecycle not in _RETIRED_LIFECYCLES:
            raise PersistentAssetViolation("MIGRATED_HISTORY must be retired/migrated lifecycle")
        if descriptor.role is AssetRole.ARCHIVE and descriptor.lifecycle not in {
            AssetLifecycle.ARCHIVED,
            AssetLifecycle.DECOMMISSIONED,
            AssetLifecycle.DELETE_CANDIDATE,
        }:
            raise PersistentAssetViolation("ARCHIVE role requires archived/decommissioned lifecycle")
        if descriptor.surface is PersistentSurface.TEMP_SANDBOX and descriptor.lifecycle is not AssetLifecycle.TEMPORARY:
            raise PersistentAssetViolation("TEMP_SANDBOX assets must be TEMPORARY")

    def require(self, request: PersistentAssetRequest) -> None:
        self.require_descriptor(request.descriptor)
        descriptor = request.descriptor
        operation = request.operation

        if operation not in descriptor.allowed_operations:
            raise PersistentAssetViolation(
                f"operation={operation.value} is not admitted for asset={descriptor.asset_id}"
            )

        if operation is not CrudOperation.READ:
            if not _nonempty(request.active_authority):
                raise PersistentAssetViolation("durable mutation requires active_authority")
            if request.target_authority != descriptor.owner_authority:
                raise PersistentAssetViolation(
                    "target_authority must match persistent asset owner_authority"
                )

        if descriptor.lifecycle in _RETIRED_LIFECYCLES and operation not in _RETIRED_ALLOWED_OPS:
            raise PersistentAssetViolation(
                f"retired asset lifecycle={descriptor.lifecycle.value} cannot perform {operation.value}"
            )

        if descriptor.role in _NON_AUTHORITY_ROLES and descriptor.lifecycle is AssetLifecycle.CURRENT:
            raise PersistentAssetViolation("non-authority asset cannot become current business authority")

    def require_migration_closed(self, observation: MigrationObservation) -> None:
        self.require_descriptor(observation.source)
        self.require_descriptor(observation.target)
        if observation.target.role is not AssetRole.AUTHORITY and observation.target.lifecycle is AssetLifecycle.CURRENT:
            raise PersistentAssetViolation("migration target CURRENT lifecycle must be authority")
        if not observation.target_verified:
            raise PersistentAssetViolation("migration target must be verified before closure")
        if not observation.source_retired:
            raise PersistentAssetViolation("migration source must be retired or archived before closure")
        if observation.source.lifecycle not in _RETIRED_LIFECYCLES:
            raise PersistentAssetViolation("migration source lifecycle must record retirement")


def reconcile_asset_inventory(
    assets: Iterable[PersistentAssetDescriptor],
    *,
    expected_current_authority_refs: frozenset[str] = frozenset(),
) -> AssetReconciliationReport:
    inventory = tuple(assets)
    gate = PersistentAssetGate()
    current: list[str] = []
    non_authority: list[str] = []
    retired: list[str] = []
    temporary: list[str] = []
    violations: list[str] = []
    seen: set[tuple[PersistentSurface, str]] = set()

    for asset in inventory:
        key = (asset.surface, asset.asset_id)
        if key in seen:
            violations.append(f"duplicate-asset:{asset.surface.value}:{asset.asset_id}")
            continue
        seen.add(key)
        try:
            gate.require_descriptor(asset)
        except PersistentAssetViolation as exc:
            violations.append(f"{asset.asset_id}:{exc}")
            continue

        if asset.role is AssetRole.AUTHORITY:
            current.append(asset.asset_id)
            if expected_current_authority_refs and asset.canonical_authority_ref not in expected_current_authority_refs:
                violations.append(f"unexpected-authority-ref:{asset.asset_id}:{asset.canonical_authority_ref}")
        elif asset.lifecycle in _RETIRED_LIFECYCLES:
            retired.append(asset.asset_id)
        elif asset.lifecycle is AssetLifecycle.TEMPORARY:
            temporary.append(asset.asset_id)
        else:
            non_authority.append(asset.asset_id)

    if expected_current_authority_refs:
        actual_refs = {
            asset.canonical_authority_ref
            for asset in inventory
            if asset.role is AssetRole.AUTHORITY and asset.lifecycle is AssetLifecycle.CURRENT
        }
        for ref in sorted(expected_current_authority_refs - actual_refs):
            violations.append(f"missing-authority-ref:{ref}")

    return AssetReconciliationReport(
        current_authority_assets=tuple(sorted(current)),
        non_authority_assets=tuple(sorted(non_authority)),
        retired_assets=tuple(sorted(retired)),
        temporary_assets=tuple(sorted(temporary)),
        violations=tuple(sorted(violations)),
    )
