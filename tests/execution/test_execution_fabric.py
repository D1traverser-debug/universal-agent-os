from datetime import UTC, datetime, timedelta
import posixpath

import pytest

from uaos.execution import (
    ActionCoordinator,
    ApprovalGrant,
    ApprovalRequired,
    AssetLifecycle,
    AssetRole,
    CapabilityHealth,
    CapabilityObservation,
    CapabilityRegistry,
    CapabilityUnavailable,
    CrudOperation,
    ExecutionDisposition,
    ExecutionOutcome,
    ExecutionRequest,
    MutationContract,
    MutationPersistence,
    PersistentAssetCatalog,
    PersistentAssetDescriptor,
    PersistentAssetViolation,
    PersistentSurface,
)


class Executor:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []

    def execute(self, request):
        self.calls.append(request)
        return self.outcome


class ReconcilingExecutor(Executor):
    def __init__(self, outcome, reconciled=None):
        super().__init__(outcome)
        self.reconciled = reconciled or ExecutionOutcome(
            ExecutionDisposition.CONFIRMED, output="found", provider_ref="r1"
        )
        self.reconcile_calls = []

    def reconcile(self, request, unknown):
        self.reconcile_calls.append((request, unknown))
        return self.reconciled


def observation(
    capability_id,
    *,
    actions=("research",),
    permissions=(),
    quality=0.8,
    cost=1.0,
    health=CapabilityHealth.AVAILABLE,
):
    return CapabilityObservation(
        capability_id,
        health,
        1.0,
        actions,
        permissions,
        quality,
        cost,
        "agent",
    )


def canonical_repo_target(target: str) -> str:
    return f"repo:{posixpath.normpath(target.removeprefix('repo:'))}"


def repo_asset(
    *,
    resource_ref="repo:file",
    lifecycle=AssetLifecycle.CURRENT,
    role=AssetRole.AUTHORITY,
    ops=None,
    owner="UAOS",
):
    return PersistentAssetDescriptor(
        asset_id=f"asset:{resource_ref}",
        resource_ref=resource_ref,
        surface=PersistentSurface.GITHUB,
        role=role,
        lifecycle=lifecycle,
        owner_authority=owner,
        allowed_operations=ops
        or frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
        canonical_authority_ref=(
            "github://D1traverser-debug/universal-agent-os@main"
            if role is AssetRole.AUTHORITY
            else None
        ),
    )


def register_writer(
    registry,
    executor,
    *,
    operation=CrudOperation.UPDATE,
    persistence=MutationPersistence.DURABLE_OR_EXTERNAL,
):
    registry.register(
        observation("writer", actions=("write",), permissions=("repo:write",)),
        executor,
        mutation_contracts={"write": MutationContract(persistence, operation)},
        canonicalize_target=(
            canonical_repo_target
            if persistence is MutationPersistence.DURABLE_OR_EXTERNAL
            else None
        ),
    )


def test_router_filters_mandatory_permissions_quality_and_cost():
    registry = CapabilityRegistry()
    registry.register(
        observation("cheap", permissions=("web",), quality=0.8, cost=1),
        Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED)),
    )
    registry.register(
        observation("best", permissions=("web",), quality=0.95, cost=2),
        Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED)),
    )
    request = ExecutionRequest(
        "a1",
        "research",
        "topic",
        {},
        required_permissions=("web",),
        quality_floor=0.9,
        cost_ceiling=3,
    )
    result = ActionCoordinator(registry).execute(request)
    assert result.capability_id == "best"


def test_router_never_silently_downgrades_mandatory_floor():
    registry = CapabilityRegistry()
    registry.register(
        observation("weak", quality=0.4),
        Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED)),
    )
    request = ExecutionRequest("a1", "research", "topic", {}, quality_floor=0.9)
    with pytest.raises(CapabilityUnavailable):
        ActionCoordinator(registry).execute(request)


def test_mutation_without_trusted_capability_contract_fails_before_executor():
    registry = CapabilityRegistry()
    executor = Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED))
    registry.register(
        observation("writer", actions=("write",), permissions=("repo:write",)), executor
    )
    request = ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {},
        required_permissions=("repo:write",),
        side_effect_class="WRITE",
        target_authority="UAOS",
    )
    with pytest.raises(PersistentAssetViolation, match="trusted MutationContract"):
        ActionCoordinator(registry, authority_context="UAOS").execute(request)
    assert executor.calls == []


def test_ephemeral_mutation_is_explicit_but_does_not_fabricate_persistent_asset():
    registry = CapabilityRegistry()
    executor = Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED))
    register_writer(
        registry,
        executor,
        persistence=MutationPersistence.EPHEMERAL,
        operation=None,
    )
    request = ExecutionRequest(
        "a1",
        "write",
        "cache:key",
        {},
        required_permissions=("repo:write",),
        side_effect_class="WRITE",
        target_authority="UAOS",
        mutation_persistence=MutationPersistence.EPHEMERAL,
    )
    result = ActionCoordinator(registry, authority_context="UAOS").execute(request)
    assert result.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert result.admission.mutation_persistence is MutationPersistence.EPHEMERAL


def test_durable_mutation_requires_trusted_catalog_before_approval_or_executor():
    registry = CapabilityRegistry()
    executor = Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED))
    register_writer(registry, executor)
    request = ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {},
        required_permissions=("repo:write",),
        side_effect_class="WRITE",
        approval_required=True,
        target_authority="UAOS",
    )
    with pytest.raises(PersistentAssetViolation, match="PersistentAssetCatalog"):
        ActionCoordinator(registry, authority_context="UAOS").execute(request)
    assert executor.calls == []


def test_request_cannot_spoof_read_or_delete_against_trusted_update_contract():
    registry = CapabilityRegistry()
    executor = Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED))
    register_writer(registry, executor, operation=CrudOperation.UPDATE)
    current = repo_asset()
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((current,)),
    )
    for asserted in (CrudOperation.READ, "READ", CrudOperation.DELETE, "DELETE"):
        request = ExecutionRequest(
            "a1",
            "write",
            "repo:file",
            {},
            required_permissions=("repo:write",),
            side_effect_class="WRITE",
            target_authority="UAOS",
            persistent_operation=asserted,
        )
        with pytest.raises(PersistentAssetViolation, match="trusted capability CRUD"):
            coordinator.execute(request)
    assert executor.calls == []


def test_caller_cannot_relabel_catalog_asset_owner_or_lifecycle():
    registry = CapabilityRegistry()
    executor = Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED))
    register_writer(registry, executor)
    trusted = repo_asset()
    forged = repo_asset(
        lifecycle=AssetLifecycle.ACTIVE_NON_AUTHORITY,
        role=AssetRole.REFERENCE,
        owner="DOMAIN:other",
    )
    request = ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {},
        required_permissions=("repo:write",),
        side_effect_class="WRITE",
        target_authority="UAOS",
        persistent_asset=forged,
    )
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((trusted,)),
    )
    with pytest.raises(PersistentAssetViolation, match="trusted catalog descriptor"):
        coordinator.execute(request)
    assert executor.calls == []


def test_target_alias_is_canonicalized_before_catalog_lookup():
    registry = CapabilityRegistry()
    executor = Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED))
    register_writer(registry, executor)
    trusted = repo_asset(resource_ref="repo:same.txt")
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((trusted,)),
    )
    request = ExecutionRequest(
        "a1",
        "write",
        "repo:sub/../same.txt",
        {},
        required_permissions=("repo:write",),
        side_effect_class="WRITE",
        target_authority="UAOS",
    )
    result = coordinator.execute(request)
    assert result.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert result.admission.canonical_target == "repo:same.txt"


def test_side_effect_requires_exact_action_approval_after_trusted_asset_admission():
    registry = CapabilityRegistry()
    executor = Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED))
    register_writer(registry, executor)
    current = repo_asset()
    request = ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {},
        required_permissions=("repo:write",),
        parameter_hash="p1",
        side_effect_class="WRITE",
        approval_required=True,
        target_authority="UAOS",
    )
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((current,)),
    )
    with pytest.raises(ApprovalRequired):
        coordinator.execute(request)
    now = datetime.now(UTC)
    wrong = ApprovalGrant(
        "g", "a1", "repo:other", "p1", now + timedelta(minutes=5)
    )
    with pytest.raises(ApprovalRequired):
        coordinator.execute(request, approval=wrong, now=now)
    right = ApprovalGrant(
        "g", "a1", "repo:file", "p1", now + timedelta(minutes=5)
    )
    assert (
        coordinator.execute(request, approval=right, now=now).outcome.disposition
        is ExecutionDisposition.CONFIRMED
    )


def test_unknown_outcome_reconcile_is_bound_to_original_admission_and_reruns_gates():
    registry = CapabilityRegistry()
    executor = ReconcilingExecutor(
        ExecutionOutcome(ExecutionDisposition.UNKNOWN, error="timeout")
    )
    register_writer(registry, executor)
    current = repo_asset()
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((current,)),
    )
    request = ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {"x": 1},
        required_permissions=("repo:write",),
        side_effect_class="WRITE",
        target_authority="UAOS",
    )
    unknown = coordinator.execute(request)
    assert unknown.outcome.disposition is ExecutionDisposition.UNKNOWN
    tampered = ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {"x": 2},
        required_permissions=("repo:write",),
        side_effect_class="WRITE",
        target_authority="UAOS",
    )
    with pytest.raises(PersistentAssetViolation, match="originally admitted"):
        coordinator.reconcile(tampered, unknown)
    resolved = coordinator.reconcile(request, unknown)
    assert resolved.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert len(executor.reconcile_calls) == 1
