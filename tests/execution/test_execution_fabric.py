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
        read_only_actions={"research"},
    )
    registry.register(
        observation("best", permissions=("web",), quality=0.95, cost=2),
        Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED)),
        read_only_actions={"research"},
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
        read_only_actions={"research"},
    )
    request = ExecutionRequest("a1", "research", "topic", {}, quality_floor=0.9)
    with pytest.raises(CapabilityUnavailable):
        ActionCoordinator(registry).execute(request)


def test_every_registered_action_requires_trusted_mutability_classification():
    registry = CapabilityRegistry()
    executor = Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED))
    with pytest.raises(ValueError, match="trusted read/mutation classification"):
        registry.register(
            observation("writer", actions=("write",), permissions=("repo:write",)),
            executor,
        )
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
        side_effect_class="READ",
        target_authority="UAOS",
        mutation_persistence=MutationPersistence.EPHEMERAL,
    )
    result = ActionCoordinator(registry, authority_context="UAOS").execute(request)
    assert result.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert result.admission.mutation_persistence is MutationPersistence.EPHEMERAL


def test_trusted_mutation_contract_cannot_be_downgraded_by_read_side_effect_assertion():
    registry = CapabilityRegistry()
    executor = Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED))
    register_writer(registry, executor)
    request = ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {},
        required_permissions=("repo:write",),
        side_effect_class="READ",
        target_authority="UAOS",
    )
    with pytest.raises(PersistentAssetViolation, match="PersistentAssetCatalog"):
        ActionCoordinator(registry, authority_context="UAOS").execute(request)
    assert executor.calls == []


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


def test_unknown_outcome_reconcile_is_bound_to_original_request_and_reruns_gates():
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
    with pytest.raises(PersistentAssetViolation, match="originally executed"):
        coordinator.reconcile(tampered, unknown)
    resolved = coordinator.reconcile(request, unknown)
    assert resolved.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert len(executor.reconcile_calls) == 1


def test_reconcile_cannot_remove_original_approval_requirement():
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
        parameter_hash="p1",
        approval_required=True,
        target_authority="UAOS",
    )
    now = datetime.now(UTC)
    grant = ApprovalGrant("g", "a1", "repo:file", "p1", now + timedelta(minutes=5))
    unknown = coordinator.execute(request, approval=grant, now=now)
    weakened = ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {"x": 1},
        required_permissions=("repo:write",),
        parameter_hash="p1",
        approval_required=False,
        target_authority="UAOS",
    )
    with pytest.raises(PersistentAssetViolation, match="originally executed"):
        coordinator.reconcile(weakened, unknown, now=now)
    assert executor.reconcile_calls == []


def test_reconcile_cannot_cross_capability_reregistration_generation():
    registry = CapabilityRegistry()
    original = ReconcilingExecutor(
        ExecutionOutcome(ExecutionDisposition.UNKNOWN, error="timeout")
    )
    register_writer(registry, original)
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
        {},
        required_permissions=("repo:write",),
        target_authority="UAOS",
    )
    unknown = coordinator.execute(request)
    replacement = ReconcilingExecutor(
        ExecutionOutcome(ExecutionDisposition.CONFIRMED, output="replacement")
    )
    register_writer(registry, replacement)
    with pytest.raises(PersistentAssetViolation, match="registration generation changed"):
        coordinator.reconcile(request, unknown)
    assert replacement.reconcile_calls == []
