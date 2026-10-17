from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, datetime
from enum import Enum
import hashlib
import json
import secrets
from threading import RLock
from types import MappingProxyType
from typing import Mapping

from .approvals import ApprovalGate, ApprovalGrant
from .authority import AuthorityScopeGate
from .models import ExecutionDisposition, ExecutionOutcome, ExecutionRequest
from .persistent_assets import (
    CrudOperation,
    MigrationObservation,
    MutationContract,
    MutationPersistence,
    PersistentAssetCatalog,
    PersistentAssetGate,
    PersistentAssetRequest,
    PersistentAssetViolation,
)
from .registry import (
    CapabilityRegistry,
    CapabilityRouter,
    CapabilityUnavailable,
    RegisteredCapability,
)


@dataclass(frozen=True, slots=True)
class ExecutionAdmissionReceipt:
    capability_id: str
    registration_generation: int
    request_fingerprint: str
    mutation_persistence: MutationPersistence | None
    canonical_target: str | None
    persistent_asset_id: str | None
    persistent_operation: CrudOperation | None


@dataclass(frozen=True, slots=True)
class CoordinatedExecution:
    capability_id: str
    outcome: ExecutionOutcome
    admission: ExecutionAdmissionReceipt
    original_request: ExecutionRequest | None = None
    execution_id: str | None = None


@dataclass(frozen=True, slots=True)
class _UnknownExecutionRecord:
    execution_id: str
    capability_id: str
    request: ExecutionRequest
    admission: ExecutionAdmissionReceipt
    outcome: ExecutionOutcome


def _canonical_value(value: object) -> object:
    """Encode request state without collapsing Python type identity."""

    if isinstance(value, Enum):
        return {
            "__enum__": f"{type(value).__module__}.{type(value).__qualname__}",
            "value": _canonical_value(value.value),
        }
    if is_dataclass(value):
        return {
            "__dataclass__": f"{type(value).__module__}.{type(value).__qualname__}",
            "fields": [
                [field.name, _canonical_value(getattr(value, field.name))]
                for field in fields(value)
            ],
        }
    if isinstance(value, Mapping):
        entries = [
            [_canonical_value(key), _canonical_value(item)]
            for key, item in value.items()
        ]
        entries.sort(
            key=lambda item: json.dumps(
                item[0], sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
        )
        return {"__mapping__": entries}
    if isinstance(value, tuple):
        return {"__tuple__": [_canonical_value(item) for item in value]}
    if isinstance(value, list):
        return {"__list__": [_canonical_value(item) for item in value]}
    if isinstance(value, (set, frozenset)):
        normalized = [_canonical_value(item) for item in value]
        normalized.sort(
            key=lambda item: json.dumps(
                item, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
        )
        return {
            "__frozenset__" if isinstance(value, frozenset) else "__set__": normalized
        }
    if isinstance(value, bytes):
        return {"__bytes__": value.hex()}
    if isinstance(value, bytearray):
        return {"__bytearray__": bytes(value).hex()}
    if value is None:
        return {"__none__": True}
    if isinstance(value, bool):
        return {"__bool__": value}
    if isinstance(value, int):
        return {"__int__": str(value)}
    if isinstance(value, float):
        return {"__float__": value.hex()}
    if isinstance(value, str):
        return {"__str__": value}
    raise PersistentAssetViolation(
        f"request contains unsupported fingerprint value type: {type(value).__module__}.{type(value).__qualname__}"
    )


def _snapshot_value(value: object) -> object:
    """Detach request data from caller-owned mutable containers."""

    if isinstance(value, Enum) or value is None or isinstance(value, (bool, int, float, str, bytes)):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if is_dataclass(value):
        values = {
            field.name: _snapshot_value(getattr(value, field.name))
            for field in fields(value)
        }
        try:
            return type(value)(**values)
        except TypeError as exc:
            raise PersistentAssetViolation(
                f"request dataclass cannot be snapshotted: {type(value).__module__}.{type(value).__qualname__}"
            ) from exc
    if isinstance(value, Mapping):
        snapshot = {
            _snapshot_value(key): _snapshot_value(item)
            for key, item in value.items()
        }
        return MappingProxyType(snapshot)
    if isinstance(value, tuple):
        return tuple(_snapshot_value(item) for item in value)
    if isinstance(value, list):
        return tuple(_snapshot_value(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_snapshot_value(item) for item in value)
    raise PersistentAssetViolation(
        f"request contains unsupported snapshot value type: {type(value).__module__}.{type(value).__qualname__}"
    )


def _snapshot_request(request: ExecutionRequest) -> ExecutionRequest:
    if not isinstance(request, ExecutionRequest):
        raise PersistentAssetViolation("execution requires ExecutionRequest")
    values = {
        field.name: _snapshot_value(getattr(request, field.name))
        for field in fields(request)
    }
    return ExecutionRequest(**values)


def _snapshot_admission(admission: ExecutionAdmissionReceipt) -> ExecutionAdmissionReceipt:
    """Return a detached value copy of a coordinator-owned admission receipt."""

    if not isinstance(admission, ExecutionAdmissionReceipt):
        raise PersistentAssetViolation("invalid execution admission receipt")
    return ExecutionAdmissionReceipt(
        capability_id=admission.capability_id,
        registration_generation=admission.registration_generation,
        request_fingerprint=admission.request_fingerprint,
        mutation_persistence=admission.mutation_persistence,
        canonical_target=admission.canonical_target,
        persistent_asset_id=admission.persistent_asset_id,
        persistent_operation=admission.persistent_operation,
    )


def _payload_digest(value: object) -> str:
    rendered = json.dumps(
        _canonical_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _request_fingerprint(request: ExecutionRequest) -> str:
    return _payload_digest(request)


def _normalize_persistence(value: MutationPersistence | str) -> MutationPersistence:
    try:
        return value if isinstance(value, MutationPersistence) else MutationPersistence(value)
    except (TypeError, ValueError) as exc:
        raise PersistentAssetViolation(f"invalid mutation_persistence assertion: {value!r}") from exc


def _normalize_operation(value: CrudOperation | str) -> CrudOperation:
    try:
        return value if isinstance(value, CrudOperation) else CrudOperation(value)
    except (TypeError, ValueError) as exc:
        raise PersistentAssetViolation(f"invalid persistent_operation assertion: {value!r}") from exc


def _normalize_outcome(outcome: ExecutionOutcome, *, source: str) -> ExecutionOutcome:
    if not isinstance(outcome, ExecutionOutcome):
        raise RuntimeError(f"{source} must return ExecutionOutcome")
    try:
        disposition = (
            outcome.disposition
            if isinstance(outcome.disposition, ExecutionDisposition)
            else ExecutionDisposition(outcome.disposition)
        )
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"{source} returned unsupported disposition: {outcome.disposition!r}") from exc
    if disposition is outcome.disposition:
        return outcome
    return ExecutionOutcome(
        disposition=disposition,
        output=outcome.output,
        provider_ref=outcome.provider_ref,
        evidence=outcome.evidence,
        error=outcome.error,
    )


def _snapshot_outcome(outcome: ExecutionOutcome) -> ExecutionOutcome:
    """Create an outcome instance detached from every other trust domain."""

    normalized = _normalize_outcome(outcome, source="outcome snapshot")
    return ExecutionOutcome(
        disposition=normalized.disposition,
        output=normalized.output,
        provider_ref=normalized.provider_ref,
        evidence=normalized.evidence,
        error=normalized.error,
    )


def _public_execution(
    *,
    capability_id: str,
    outcome: ExecutionOutcome,
    admission: ExecutionAdmissionReceipt,
    request: ExecutionRequest | None,
    execution_id: str | None,
) -> CoordinatedExecution:
    """Build a public receipt with no object alias to coordinator-owned state."""

    return CoordinatedExecution(
        capability_id=capability_id,
        outcome=_snapshot_outcome(outcome),
        admission=_snapshot_admission(admission),
        original_request=_snapshot_request(request) if request is not None else None,
        execution_id=execution_id,
    )


class ActionCoordinator:
    """Policy boundary around executor adapters, ownership and safe fallback.

    Action mutability and CRUD semantics are capability-owned. Request mutation labels are
    assertions/context only. Execution first snapshots the complete request into detached
    immutable containers, so admission, execution and later reconciliation all bind the
    same values even if caller-owned payload objects are subsequently changed.

    UNKNOWN reconciliation is coordinator-owned. A caller receives an opaque execution
    id plus detached public copies of request/admission/outcome; none of those public
    objects alias the authoritative internal record. A per-execution reconciliation claim
    prevents concurrent repair attempts for one id. The baseline record/claim store is
    process-local and fails closed after restart; a host requiring cross-process
    reconciliation must persist the same record and atomic claim state in its authority
    store.
    """

    def __init__(
        self,
        registry: CapabilityRegistry,
        *,
        router: CapabilityRouter | None = None,
        approval_gate: ApprovalGate | None = None,
        authority_gate: AuthorityScopeGate | None = None,
        persistent_asset_gate: PersistentAssetGate | None = None,
        persistent_asset_catalog: PersistentAssetCatalog | None = None,
        authority_context: str | None = None,
    ) -> None:
        self.registry = registry
        self.router = router or CapabilityRouter()
        self.approval_gate = approval_gate or ApprovalGate()
        self.authority_gate = authority_gate or AuthorityScopeGate()
        self.persistent_asset_gate = persistent_asset_gate or PersistentAssetGate()
        self.persistent_asset_catalog = persistent_asset_catalog
        self.authority_context = authority_context
        self._unknown_records: dict[str, _UnknownExecutionRecord] = {}
        self._reconciling_ids: set[str] = set()
        self._unknown_lock = RLock()

    @staticmethod
    def _trusted_contract(
        request: ExecutionRequest,
        registered: RegisteredCapability,
    ) -> MutationContract | None:
        return registered.mutation_contract_for(request.action_name)

    def _admit(
        self,
        request: ExecutionRequest,
        registered: RegisteredCapability,
    ) -> ExecutionAdmissionReceipt:
        contract = self._trusted_contract(request, registered)
        trusted_mutating = contract is not None
        self.authority_gate.require(
            request,
            active_authority=self.authority_context,
            trusted_mutating=trusted_mutating,
        )
        fingerprint = _request_fingerprint(request)

        if contract is None:
            if request.mutation_persistence is not None:
                raise PersistentAssetViolation(
                    "trusted read-only action cannot assert mutation_persistence"
                )
            if request.persistent_operation is not None:
                asserted = _normalize_operation(request.persistent_operation)
                if asserted is not CrudOperation.READ:
                    raise PersistentAssetViolation(
                        "trusted read-only action may only assert READ persistent_operation"
                    )
            return ExecutionAdmissionReceipt(
                registered.observation.capability_id,
                registered.registration_generation,
                fingerprint,
                None,
                None,
                None,
                CrudOperation.READ if request.persistent_operation is not None else None,
            )

        if request.mutation_persistence is not None:
            asserted_persistence = _normalize_persistence(request.mutation_persistence)
            if asserted_persistence is not contract.persistence:
                raise PersistentAssetViolation(
                    "request mutation_persistence does not match trusted capability contract"
                )

        if contract.persistence is MutationPersistence.EPHEMERAL:
            if request.persistent_asset is not None or request.persistent_operation is not None:
                raise PersistentAssetViolation(
                    "ephemeral mutation cannot attach persistent asset/CRUD assertions"
                )
            return ExecutionAdmissionReceipt(
                registered.observation.capability_id,
                registered.registration_generation,
                fingerprint,
                MutationPersistence.EPHEMERAL,
                None,
                None,
                None,
            )

        if contract.operation is None or contract.operation is CrudOperation.READ:
            raise PersistentAssetViolation(
                "trusted durable mutation contract requires a non-READ CRUD operation"
            )
        if registered.canonicalize_target is None:
            raise PersistentAssetViolation(
                "durable/external mutation capability requires trusted target canonicalizer"
            )
        if self.persistent_asset_catalog is None:
            raise PersistentAssetViolation(
                "durable/external mutation requires trusted PersistentAssetCatalog"
            )
        try:
            canonical_target = registered.canonicalize_target(request.target)
        except Exception as exc:
            raise PersistentAssetViolation(
                f"target canonicalization failed: {type(exc).__name__}: {exc}"
            ) from exc
        if not isinstance(canonical_target, str) or not canonical_target.strip():
            raise PersistentAssetViolation("target canonicalizer returned empty identity")

        descriptor = self.persistent_asset_catalog.resolve(canonical_target)
        if request.persistent_asset is not None and request.persistent_asset != descriptor:
            raise PersistentAssetViolation(
                "caller asset assertion does not match trusted catalog descriptor"
            )
        if request.persistent_operation is not None:
            asserted_operation = _normalize_operation(request.persistent_operation)
            if asserted_operation is not contract.operation:
                raise PersistentAssetViolation(
                    "caller persistent_operation does not match trusted capability CRUD operation"
                )

        self.persistent_asset_gate.require(
            PersistentAssetRequest(
                operation=contract.operation,
                descriptor=descriptor,
                active_authority=self.authority_context,
                target_authority=request.target_authority,
                canonical_execution_target=canonical_target,
            )
        )
        return ExecutionAdmissionReceipt(
            registered.observation.capability_id,
            registered.registration_generation,
            fingerprint,
            MutationPersistence.DURABLE_OR_EXTERNAL,
            canonical_target,
            descriptor.asset_id,
            contract.operation,
        )

    def _enforce_migration_closure(
        self,
        admission: ExecutionAdmissionReceipt,
        outcome: ExecutionOutcome,
    ) -> ExecutionOutcome:
        if (
            outcome.disposition is not ExecutionDisposition.CONFIRMED
            or admission.persistent_operation is not CrudOperation.MIGRATE
        ):
            return outcome
        if self.persistent_asset_catalog is None or admission.canonical_target is None:
            return ExecutionOutcome(
                ExecutionDisposition.UNKNOWN,
                output=outcome.output,
                provider_ref=outcome.provider_ref,
                evidence=outcome.evidence,
                error="migration closure missing trusted catalog/admission identity",
            )
        try:
            source = self.persistent_asset_catalog.resolve(admission.canonical_target)
            if source.migration_target_ref is None:
                raise PersistentAssetViolation("migration source requires migration_target_ref")
            target = self.persistent_asset_catalog.resolve(source.migration_target_ref)
            target_verified = outcome.evidence.get("migration_target_verified") is True
            source_retired = outcome.evidence.get("migration_source_retired") is True
            observed_source_ref = outcome.evidence.get("migration_source_ref")
            observed_target_ref = outcome.evidence.get("migration_target_ref")
            if not isinstance(observed_source_ref, str) or not isinstance(observed_target_ref, str):
                raise PersistentAssetViolation(
                    "migration outcome must report source/target canonical refs"
                )
            self.persistent_asset_gate.require_migration_closed(
                MigrationObservation(
                    source=source,
                    target=target,
                    target_verified=target_verified,
                    source_retired=source_retired,
                    observed_source_ref=observed_source_ref,
                    observed_target_ref=observed_target_ref,
                )
            )
        except PersistentAssetViolation as exc:
            return ExecutionOutcome(
                ExecutionDisposition.UNKNOWN,
                output=outcome.output,
                provider_ref=outcome.provider_ref,
                evidence=outcome.evidence,
                error=f"migration closure unverified: {exc}",
            )
        return outcome

    def _record_unknown(
        self,
        request: ExecutionRequest,
        registered: RegisteredCapability,
        admission: ExecutionAdmissionReceipt,
        outcome: ExecutionOutcome,
        *,
        execution_id: str | None = None,
    ) -> str:
        execution_id = execution_id or secrets.token_urlsafe(32)
        record = _UnknownExecutionRecord(
            execution_id=execution_id,
            capability_id=registered.observation.capability_id,
            request=request,
            admission=admission,
            outcome=_snapshot_outcome(outcome),
        )
        with self._unknown_lock:
            self._unknown_records[execution_id] = record
        return execution_id

    def _execute_registered(
        self,
        request: ExecutionRequest,
        registered: RegisteredCapability,
        *,
        approval: ApprovalGrant | None,
        now: datetime,
    ) -> CoordinatedExecution:
        admission = self._admit(request, registered)
        self.approval_gate.require(request, approval, now=now)
        outcome = _normalize_outcome(
            registered.executor.execute(request),
            source="executor",
        )
        outcome = self._enforce_migration_closure(admission, outcome)
        self.router.record_outcome(registered.observation.capability_id, outcome.disposition)
        execution_id = None
        if outcome.disposition is ExecutionDisposition.UNKNOWN:
            execution_id = self._record_unknown(
                request,
                registered,
                admission,
                outcome,
            )
        return _public_execution(
            capability_id=registered.observation.capability_id,
            outcome=outcome,
            admission=admission,
            request=request,
            execution_id=execution_id,
        )

    def execute(
        self,
        request: ExecutionRequest,
        *,
        approval: ApprovalGrant | None = None,
        now: datetime | None = None,
    ) -> CoordinatedExecution:
        request = _snapshot_request(request)
        now = now or datetime.now(UTC)
        registered = self.router.select(self.registry, request)
        return self._execute_registered(
            request,
            registered,
            approval=approval,
            now=now,
        )

    def execute_with_fallback(
        self,
        request: ExecutionRequest,
        *,
        approval: ApprovalGrant | None = None,
        now: datetime | None = None,
    ) -> CoordinatedExecution:
        request = _snapshot_request(request)
        now = now or datetime.now(UTC)
        ranked = self.router.ranked(self.registry, request)
        if not ranked:
            raise CapabilityUnavailable(
                f"no executable capability satisfies action={request.action_name!r}"
            )

        contracts = tuple(self._trusted_contract(request, item) for item in ranked)
        mutating_flags = {contract is not None for contract in contracts}
        if len(mutating_flags) != 1:
            raise CapabilityUnavailable(
                "candidate capabilities disagree on trusted mutability classification"
            )
        if True in mutating_flags:
            return self._execute_registered(
                request,
                ranked[0],
                approval=approval,
                now=now,
            )

        last: CoordinatedExecution | None = None
        for registered in ranked:
            current = self._execute_registered(
                request,
                registered,
                approval=approval,
                now=now,
            )
            if current.outcome.disposition is ExecutionDisposition.CONFIRMED:
                return current
            if current.outcome.disposition is ExecutionDisposition.UNKNOWN:
                return current
            last = current
        if last is None:
            raise CapabilityUnavailable(
                f"no executable capability for action={request.action_name!r}"
            )
        return last

    def reconcile(
        self,
        request: ExecutionRequest,
        unknown: CoordinatedExecution,
        *,
        approval: ApprovalGrant | None = None,
        now: datetime | None = None,
    ) -> CoordinatedExecution:
        request = _snapshot_request(request)
        execution_id = unknown.execution_id
        if not isinstance(execution_id, str) or not execution_id:
            raise PersistentAssetViolation(
                "reconciliation requires a coordinator-issued UNKNOWN execution_id"
            )

        with self._unknown_lock:
            record = self._unknown_records.get(execution_id)
            if record is None:
                raise PersistentAssetViolation(
                    "reconciliation UNKNOWN execution is not owned by this coordinator"
                )
            if execution_id in self._reconciling_ids:
                raise PersistentAssetViolation(
                    "reconciliation UNKNOWN execution is already being reconciled"
                )
            self._reconciling_ids.add(execution_id)

        try:
            if request != record.request:
                raise PersistentAssetViolation(
                    "reconciliation request must exactly equal the originally executed request"
                )
            if _request_fingerprint(request) != record.admission.request_fingerprint:
                raise PersistentAssetViolation(
                    "reconciliation request fingerprint does not match original admission"
                )

            registered = self.registry.get(record.capability_id)
            if registered.registration_generation != record.admission.registration_generation:
                raise PersistentAssetViolation(
                    "reconciliation capability registration generation changed since execution"
                )
            admission = self._admit(request, registered)
            if admission != record.admission:
                raise PersistentAssetViolation(
                    "reconciliation admission no longer matches original execution admission"
                )

            normalized_unknown = _normalize_outcome(
                record.outcome,
                source="coordinator-owned unknown execution",
            )
            if normalized_unknown.disposition is not ExecutionDisposition.UNKNOWN:
                raise PersistentAssetViolation(
                    "coordinator reconciliation record is no longer UNKNOWN"
                )

            now = now or datetime.now(UTC)
            self.approval_gate.require(record.request, approval, now=now)
            reconciler = getattr(registered.executor, "reconcile", None)
            if reconciler is None:
                return _public_execution(
                    capability_id=record.capability_id,
                    outcome=record.outcome,
                    admission=record.admission,
                    request=record.request,
                    execution_id=execution_id,
                )

            outcome = _normalize_outcome(
                reconciler(record.request, normalized_unknown),
                source="reconciler",
            )
            outcome = self._enforce_migration_closure(admission, outcome)
            self.router.record_outcome(record.capability_id, outcome.disposition)

            if outcome.disposition is ExecutionDisposition.UNKNOWN:
                self._record_unknown(
                    record.request,
                    registered,
                    admission,
                    outcome,
                    execution_id=execution_id,
                )
            else:
                with self._unknown_lock:
                    self._unknown_records.pop(execution_id, None)

            return _public_execution(
                capability_id=record.capability_id,
                outcome=outcome,
                admission=admission,
                request=record.request,
                execution_id=execution_id if outcome.disposition is ExecutionDisposition.UNKNOWN else None,
            )
        finally:
            with self._unknown_lock:
                self._reconciling_ids.discard(execution_id)
