from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable


class PersistentAssetViolation(ValueError):
    pass


class PersistentSurface(StrEnum):
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
    LOCAL_WORKSPACE = "LOCAL_WORKSPACE"
    OTHER_EXTERNAL = "OTHER_EXTERNAL"
    TEMP_SANDBOX = "TEMP_SANDBOX"


class AssetRole(StrEnum):
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


class AssetLifecycle(StrEnum):
    CURRENT = "CURRENT"
    ACTIVE_NON_AUTHORITY = "ACTIVE_NON_AUTHORITY"
    MIGRATED = "MIGRATED"
    DECOMMISSIONED = "DECOMMISSIONED"
    ARCHIVED = "ARCHIVED"
    DELETE_CANDIDATE = "DELETE_CANDIDATE"
    TEMPORARY = "TEMPORARY"


class CrudOperation(StrEnum):
    READ = "READ"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    OUTPUT = "OUTPUT"
    MIGRATE = "MIGRATE"
    ARCHIVE = "ARCHIVE"


class MutationPersistence(StrEnum):
    EPHEMERAL = "EPHEMERAL"
    DURABLE_OR_EXTERNAL = "DURABLE_OR_EXTERNAL"


@dataclass(frozen=True, slots=True)
class MutationContract:
    persistence: MutationPersistence
    operation: CrudOperation | None = None

    def __post_init__(self) -> None:
        try:
            persistence = (
                self.persistence
                if isinstance(self.persistence, MutationPersistence)
                else MutationPersistence(self.persistence)
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid mutation persistence: {self.persistence!r}") from exc
        object.__setattr__(self, "persistence", persistence)
        if self.operation is not None and not isinstance(self.operation, CrudOperation):
            try:
                object.__setattr__(self, "operation", CrudOperation(self.operation))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid CRUD operation: {self.operation!r}") from exc
        if persistence is MutationPersistence.EPHEMERAL:
            if self.operation is not None:
                raise ValueError("ephemeral mutation contract cannot declare persistent operation")
            return
        if self.operation is None or self.operation is CrudOperation.READ:
            raise ValueError("durable/external mutation contract requires a non-READ CRUD operation")


_RETIRED_LIFECYCLES = {
    AssetLifecycle.MIGRATED,
    AssetLifecycle.DECOMMISSIONED,
    AssetLifecycle.ARCHIVED,
    AssetLifecycle.DELETE_CANDIDATE,
}
_RETIRED_ALLOWED_OPS = {
    CrudOperation.READ,
    CrudOperation.ARCHIVE,
    CrudOperation.DELETE,
    CrudOperation.MIGRATE,
}
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
_TEMP_SANDBOX_FORBIDDEN_OPS = {
    CrudOperation.OUTPUT,
    CrudOperation.MIGRATE,
    CrudOperation.ARCHIVE,
}
_TEMP_SANDBOX_FORBIDDEN_ROLES = {
    AssetRole.AUTHORITY,
    AssetRole.DELIVERY,
    AssetRole.DELIVERY_HISTORY,
    AssetRole.MIGRATED_HISTORY,
    AssetRole.ARCHIVE,
}


@dataclass(frozen=True, slots=True)
class PersistentAssetDescriptor:
    asset_id: str
    resource_ref: str
    surface: PersistentSurface
    role: AssetRole
    lifecycle: AssetLifecycle
    owner_authority: str
    allowed_operations: frozenset[CrudOperation]
    canonical_authority_ref: str | None = None
    migration_target_ref: str | None = None


class PersistentAssetCatalog:
    """Trusted inventory keyed by canonical resource identity.

    Callers do not get to invent lifecycle/owner/role metadata at execution time.
    The coordinator resolves canonical targets through the selected capability and
    then obtains the descriptor from this catalog.
    """

    def __init__(self, assets: Iterable[PersistentAssetDescriptor] = ()) -> None:
        self._by_ref: dict[str, PersistentAssetDescriptor] = {}
        gate = PersistentAssetGate()
        for asset in assets:
            gate.require_descriptor(asset)
            if asset.resource_ref in self._by_ref:
                raise PersistentAssetViolation(
                    f"duplicate catalog resource_ref: {asset.resource_ref}"
                )
            self._by_ref[asset.resource_ref] = asset

    def resolve(self, resource_ref: str) -> PersistentAssetDescriptor:
        try:
            return self._by_ref[resource_ref]
        except KeyError as exc:
            raise PersistentAssetViolation(
                f"persistent asset is not registered in trusted catalog: {resource_ref}"
            ) from exc

    def all(self) -> tuple[PersistentAssetDescriptor, ...]:
        return tuple(self._by_ref.values())


@dataclass(frozen=True, slots=True)
class PersistentAssetRequest:
    operation: CrudOperation
    descriptor: PersistentAssetDescriptor
    active_authority: str | None
    target_authority: str | None
    canonical_execution_target: str


@dataclass(frozen=True, slots=True)
class MigrationObservation:
    source: PersistentAssetDescriptor
    target: PersistentAssetDescriptor
    target_verified: bool
    source_retired: bool
    observed_source_ref: str
    observed_target_ref: str


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
    """Fail-closed lifecycle/owner admission over trusted asset metadata."""

    def require_descriptor(self, descriptor: PersistentAssetDescriptor) -> None:
        if not _nonempty(descriptor.asset_id):
            raise PersistentAssetViolation("persistent asset requires asset_id")
        if not _nonempty(descriptor.resource_ref):
            raise PersistentAssetViolation("persistent asset requires resource_ref")
        if not _nonempty(descriptor.owner_authority):
            raise PersistentAssetViolation("persistent asset requires owner_authority")
        if not descriptor.allowed_operations:
            raise PersistentAssetViolation("persistent asset requires allowed_operations")
        if CrudOperation.READ not in descriptor.allowed_operations:
            raise PersistentAssetViolation("persistent asset must allow READ for reconciliation")

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
        if descriptor.surface is PersistentSurface.TEMP_SANDBOX:
            if descriptor.lifecycle is not AssetLifecycle.TEMPORARY:
                raise PersistentAssetViolation("TEMP_SANDBOX assets must be TEMPORARY")
            if descriptor.role in _TEMP_SANDBOX_FORBIDDEN_ROLES:
                raise PersistentAssetViolation(
                    "TEMP_SANDBOX cannot carry authority/delivery/archive roles"
                )
            forbidden = descriptor.allowed_operations & _TEMP_SANDBOX_FORBIDDEN_OPS
            if forbidden:
                names = ",".join(sorted(operation.value for operation in forbidden))
                raise PersistentAssetViolation(
                    f"TEMP_SANDBOX cannot admit terminal/promotion operations: {names}"
                )

    def require(self, request: PersistentAssetRequest) -> None:
        self.require_descriptor(request.descriptor)
        descriptor = request.descriptor
        operation = request.operation

        if descriptor.resource_ref != request.canonical_execution_target:
            raise PersistentAssetViolation(
                "trusted asset resource_ref must match canonical executor target"
            )
        if operation not in descriptor.allowed_operations:
            raise PersistentAssetViolation(
                f"operation={operation.value} is not admitted for asset={descriptor.asset_id}"
            )

        if operation is not CrudOperation.READ:
            if not _nonempty(request.active_authority):
                raise PersistentAssetViolation("durable mutation requires active_authority")
            if request.target_authority != descriptor.owner_authority:
                raise PersistentAssetViolation(
                    "target_authority must match trusted persistent asset owner_authority"
                )

        if descriptor.lifecycle in _RETIRED_LIFECYCLES and operation not in _RETIRED_ALLOWED_OPS:
            raise PersistentAssetViolation(
                f"retired asset lifecycle={descriptor.lifecycle.value} cannot perform {operation.value}"
            )
        if operation is CrudOperation.MIGRATE:
            if descriptor.lifecycle not in _RETIRED_LIFECYCLES:
                raise PersistentAssetViolation(
                    "MIGRATE is closure-only and requires a retired source lifecycle"
                )
            if not _nonempty(descriptor.migration_target_ref):
                raise PersistentAssetViolation(
                    "MIGRATE closure source requires migration_target_ref"
                )

        if descriptor.role in _NON_AUTHORITY_ROLES and descriptor.lifecycle is AssetLifecycle.CURRENT:
            raise PersistentAssetViolation("non-authority asset cannot become current business authority")

    def require_migration_closed(self, observation: MigrationObservation) -> None:
        self.require_descriptor(observation.source)
        self.require_descriptor(observation.target)
        source = observation.source
        target = observation.target

        if source.resource_ref == target.resource_ref:
            raise PersistentAssetViolation("migration source and target must be distinct")
        if not _nonempty(source.migration_target_ref):
            raise PersistentAssetViolation("migration source requires migration_target_ref")
        if source.migration_target_ref != target.resource_ref:
            raise PersistentAssetViolation(
                "migration target must match source.migration_target_ref"
            )
        if observation.observed_source_ref != source.resource_ref:
            raise PersistentAssetViolation("migration observation source identity mismatch")
        if observation.observed_target_ref != target.resource_ref:
            raise PersistentAssetViolation("migration observation target identity mismatch")
        if target.role is not AssetRole.AUTHORITY or target.lifecycle is not AssetLifecycle.CURRENT:
            raise PersistentAssetViolation("migration target must be CURRENT AUTHORITY")
        if not observation.target_verified:
            raise PersistentAssetViolation("migration target must be independently verified before closure")
        if not observation.source_retired:
            raise PersistentAssetViolation("migration source must be retired or archived before closure")
        if source.lifecycle not in _RETIRED_LIFECYCLES:
            raise PersistentAssetViolation("migration source catalog lifecycle must record retirement")


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
    seen_refs: set[str] = set()

    for asset in inventory:
        key = (asset.surface, asset.asset_id)
        if key in seen:
            violations.append(f"duplicate-asset:{asset.surface.value}:{asset.asset_id}")
            continue
        if asset.resource_ref in seen_refs:
            violations.append(f"duplicate-resource-ref:{asset.resource_ref}")
            continue
        seen.add(key)
        seen_refs.add(asset.resource_ref)
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
