from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, datetime
from enum import Enum
import hashlib
import json
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


def _canonical_value(value: object) -> object:
    """Convert request state to a stable, order-independent JSON-compatible form."""

    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {
            field.name: _canonical_value(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {
            str(key): _canonical_value(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, (set, frozenset)):
        normalized = [_canonical_value(item) for item in value]
        return sorted(
            normalized,
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), default=repr),
        )
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, bytes):
        return {"__bytes_sha256__": hashlib.sha256(value).hexdigest()}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


def _payload_digest(value: object) -> str:
    rendered = json.dumps(
        _canonical_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _request_fingerprint(request: ExecutionRequest) -> str:
    # The immutable original request remains the primary reconciliation binding.
    # This digest is an independently comparable durable receipt and therefore covers
    # every request field, including approval/routing/authority assertions.
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


class ActionCoordinator:
    """Policy boundary around executor adapters, ownership and safe fallback.

    Action mutability and CRUD semantics are capability-owned. The request's legacy
    ``side_effect_class`` and persistent fields are assertions/context only; they never
    decide whether mutation gates execute. Durable/external target identity comes from
    the selected adapter, while a trusted ``PersistentAssetCatalog`` supplies lifecycle,
    owner, role and operation permissions.
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
        # Outcome disposition is normalized before this method is entered.
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
        return CoordinatedExecution(
            registered.observation.capability_id,
            outcome,
            admission,
            request,
        )

    def execute(
        self,
        request: ExecutionRequest,
        *,
        approval: ApprovalGrant | None = None,
        now: datetime | None = None,
    ) -> CoordinatedExecution:
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
            # Mutation fallback can duplicate/redirect side effects. Use the same single
            # selected-provider semantics as execute(); UNKNOWN must reconcile instead.
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
        normalized_unknown = _normalize_outcome(unknown.outcome, source="unknown execution")
        if normalized_unknown.disposition is not ExecutionDisposition.UNKNOWN:
            raise ValueError("only UNKNOWN execution may be reconciled")
        if unknown.original_request is None:
            raise PersistentAssetViolation(
                "reconciliation requires the immutable originally executed request"
            )
        if request != unknown.original_request:
            raise PersistentAssetViolation(
                "reconciliation request must exactly equal the originally executed request"
            )
        if _request_fingerprint(request) != unknown.admission.request_fingerprint:
            raise PersistentAssetViolation(
                "reconciliation request fingerprint does not match original admission"
            )

        registered = self.registry.get(unknown.capability_id)
        if registered.registration_generation != unknown.admission.registration_generation:
            raise PersistentAssetViolation(
                "reconciliation capability registration generation changed since execution"
            )
        admission = self._admit(request, registered)
        if admission != unknown.admission:
            raise PersistentAssetViolation(
                "reconciliation admission no longer matches original execution admission"
            )

        now = now or datetime.now(UTC)
        self.approval_gate.require(request, approval, now=now)
        reconciler = getattr(registered.executor, "reconcile", None)
        if reconciler is None:
            return unknown
        outcome = _normalize_outcome(
            reconciler(request, normalized_unknown),
            source="reconciler",
        )
        outcome = self._enforce_migration_closure(admission, outcome)
        self.router.record_outcome(unknown.capability_id, outcome.disposition)
        return CoordinatedExecution(
            unknown.capability_id,
            outcome,
            admission,
            request,
        )
