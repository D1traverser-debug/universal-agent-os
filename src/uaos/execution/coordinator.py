from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json

from .approvals import ApprovalGate, ApprovalGrant
from .authority import AuthorityScopeGate
from .models import ExecutionDisposition, ExecutionOutcome, ExecutionRequest
from .persistent_assets import (
    CrudOperation,
    MigrationObservation,
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


def _payload_digest(value: object) -> str:
    try:
        rendered = json.dumps(value, sort_keys=True, separators=(",", ":"), default=repr)
    except Exception:
        rendered = repr(value)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _request_fingerprint(request: ExecutionRequest) -> str:
    parts = (
        request.action_id,
        request.action_name,
        request.target,
        request.parameter_hash,
        request.side_effect_class.upper(),
        request.target_authority or "",
        request.required_capability_id or "",
        _payload_digest(request.payload),
    )
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


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


class ActionCoordinator:
    """Policy boundary around executor adapters, ownership and safe fallback.

    Mutation semantics are capability-owned. Requests may assert persistence/CRUD/asset
    metadata, but those assertions never become authority: the selected registered
    capability derives the mutation contract and canonical target, while a trusted
    PersistentAssetCatalog supplies lifecycle/owner/role metadata.
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
    def _is_mutating(request: ExecutionRequest) -> bool:
        return request.side_effect_class.upper() not in {"NONE", "READ"}

    def _admit(
        self,
        request: ExecutionRequest,
        registered: RegisteredCapability,
    ) -> ExecutionAdmissionReceipt:
        self.authority_gate.require(request, active_authority=self.authority_context)
        fingerprint = _request_fingerprint(request)
        if not self._is_mutating(request):
            if request.mutation_persistence is not None:
                raise PersistentAssetViolation(
                    "non-mutating request cannot assert mutation_persistence"
                )
            if request.persistent_operation is not None:
                asserted = _normalize_operation(request.persistent_operation)
                if asserted is not CrudOperation.READ:
                    raise PersistentAssetViolation(
                        "non-mutating request may only assert READ persistent_operation"
                    )
            return ExecutionAdmissionReceipt(
                registered.observation.capability_id,
                fingerprint,
                None,
                None,
                None,
                CrudOperation.READ if request.persistent_operation is not None else None,
            )

        contract = registered.mutation_contracts.get(request.action_name)
        if contract is None:
            raise PersistentAssetViolation(
                "mutating capability action requires trusted MutationContract registration"
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
                raise PersistentAssetViolation(
                    "migration source requires migration_target_ref"
                )
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

    def execute(
        self,
        request: ExecutionRequest,
        *,
        approval: ApprovalGrant | None = None,
        now: datetime | None = None,
    ) -> CoordinatedExecution:
        now = now or datetime.now(UTC)
        # Routing is side-effect free; trusted capability registration then supplies
        # action semantics/canonicalization before any approval or executor side effect.
        registered = self.router.select(self.registry, request)
        admission = self._admit(request, registered)
        self.approval_gate.require(request, approval, now=now)
        outcome = registered.executor.execute(request)
        outcome = self._enforce_migration_closure(admission, outcome)
        self.router.record_outcome(registered.observation.capability_id, outcome.disposition)
        if outcome.disposition not in {
            ExecutionDisposition.CONFIRMED,
            ExecutionDisposition.FAILED,
            ExecutionDisposition.UNKNOWN,
        }:
            raise RuntimeError("executor returned unsupported disposition")
        return CoordinatedExecution(
            registered.observation.capability_id,
            outcome,
            admission,
        )

    def execute_with_fallback(
        self,
        request: ExecutionRequest,
        *,
        approval: ApprovalGrant | None = None,
        now: datetime | None = None,
    ) -> CoordinatedExecution:
        if self._is_mutating(request):
            return self.execute(request, approval=approval, now=now)
        now = now or datetime.now(UTC)
        ranked = self.router.ranked(self.registry, request)
        if not ranked:
            raise CapabilityUnavailable(
                f"no executable capability satisfies action={request.action_name!r}"
            )
        last: CoordinatedExecution | None = None
        for registered in ranked:
            admission = self._admit(request, registered)
            self.approval_gate.require(request, approval, now=now)
            outcome = registered.executor.execute(request)
            self.router.record_outcome(
                registered.observation.capability_id, outcome.disposition
            )
            current = CoordinatedExecution(
                registered.observation.capability_id,
                outcome,
                admission,
            )
            if outcome.disposition is ExecutionDisposition.CONFIRMED:
                return current
            if outcome.disposition is ExecutionDisposition.UNKNOWN:
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
        if unknown.outcome.disposition is not ExecutionDisposition.UNKNOWN:
            raise ValueError("only UNKNOWN execution may be reconciled")
        if _request_fingerprint(request) != unknown.admission.request_fingerprint:
            raise PersistentAssetViolation(
                "reconciliation request must exactly match the originally admitted request"
            )
        registered = self.registry.get(unknown.capability_id)
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
        outcome = reconciler(request, unknown.outcome)
        outcome = self._enforce_migration_closure(admission, outcome)
        self.router.record_outcome(unknown.capability_id, outcome.disposition)
        if outcome.disposition not in {
            ExecutionDisposition.CONFIRMED,
            ExecutionDisposition.FAILED,
            ExecutionDisposition.UNKNOWN,
        }:
            raise RuntimeError("reconciler must return CONFIRMED, FAILED or UNKNOWN")
        return CoordinatedExecution(unknown.capability_id, outcome, admission)
