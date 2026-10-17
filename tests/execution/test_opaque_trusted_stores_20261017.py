import pytest

from uaos.execution import (
    AssetLifecycle,
    AssetRole,
    CapabilityHealth,
    CapabilityObservation,
    CapabilityRegistry,
    CrudOperation,
    MutationContract,
    MutationPersistence,
    PersistentAssetCatalog,
    PersistentAssetDescriptor,
    PersistentSurface,
)
from uaos.runtime import (
    REF_CONDITIONAL_POLICY_STATUS,
    PolicyActivationViolation,
    ProductionRefIdentity,
    resolve_ref_conditioned_policy_activation,
)


class NoopExecutor:
    def execute(self, request):  # pragma: no cover - registry semantics only
        raise AssertionError("executor must not run in this test")


class LyingStr(str):
    def __new__(cls, actual, lie):
        item = super().__new__(cls, actual)
        item._lie = lie
        return item

    def strip(self, *args, **kwargs):
        return self._lie


def _observation():
    return CapabilityObservation(
        capability_id="writer",
        health=CapabilityHealth.AVAILABLE,
        observed_at_epoch=1.0,
        supported_actions=("write",),
        permissions=("repo:write",),
        quality_score=1.0,
        estimated_cost=0.0,
        executor_kind="test",
    )


def test_registry_detaches_original_and_public_mutation_contract_objects():
    registry = CapabilityRegistry()
    original = MutationContract(
        MutationPersistence.DURABLE_OR_EXTERNAL,
        CrudOperation.UPDATE,
    )
    registry.register(
        _observation(),
        NoopExecutor(),
        mutation_contracts={"write": original},
        canonicalize_target=lambda target: target,
    )
    generation = registry.get("writer").registration_generation

    # Retaining the original contract object must not let a caller rewrite trusted truth.
    object.__setattr__(original, "persistence", MutationPersistence.EPHEMERAL)
    object.__setattr__(original, "operation", None)
    after_original_attack = registry.get("writer")
    trusted = after_original_attack.mutation_contract_for("write")
    assert trusted is not None
    assert trusted.persistence is MutationPersistence.DURABLE_OR_EXTERNAL
    assert trusted.operation is CrudOperation.UPDATE

    # A public detached view is also disposable. Even object.__setattr__ on its frozen
    # wrapper or nested contract cannot modify the private registry record.
    public_contract = after_original_attack.mutation_contracts["write"]
    object.__setattr__(public_contract, "persistence", MutationPersistence.EPHEMERAL)
    object.__setattr__(public_contract, "operation", None)
    object.__setattr__(after_original_attack, "mutation_contracts", {"write": public_contract})

    fresh = registry.get("writer")
    trusted_again = fresh.mutation_contract_for("write")
    assert fresh.registration_generation == generation
    assert trusted_again is not None
    assert trusted_again.persistence is MutationPersistence.DURABLE_OR_EXTERNAL
    assert trusted_again.operation is CrudOperation.UPDATE


def test_catalog_detaches_original_resolve_and_all_descriptor_views():
    original = PersistentAssetDescriptor(
        asset_id="history",
        resource_ref="drive:history",
        surface=PersistentSurface.GOOGLE_DRIVE,
        role=AssetRole.MIGRATED_HISTORY,
        lifecycle=AssetLifecycle.DECOMMISSIONED,
        owner_authority="DOMAIN:financial_writing",
        allowed_operations=frozenset({CrudOperation.READ}),
    )
    catalog = PersistentAssetCatalog((original,))

    object.__setattr__(
        original,
        "allowed_operations",
        frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
    )
    resolved = catalog.resolve("drive:history")
    assert resolved.allowed_operations == frozenset({CrudOperation.READ})

    object.__setattr__(
        resolved,
        "allowed_operations",
        frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
    )
    from_all = catalog.all()[0]
    object.__setattr__(from_all, "lifecycle", AssetLifecycle.CURRENT)
    object.__setattr__(from_all, "role", AssetRole.AUTHORITY)

    fresh = catalog.resolve("drive:history")
    assert fresh.allowed_operations == frozenset({CrudOperation.READ})
    assert fresh.lifecycle is AssetLifecycle.DECOMMISSIONED
    assert fresh.role is AssetRole.MIGRATED_HISTORY


def test_policy_activation_rejects_str_subclasses_before_their_normalization_runs():
    production = ProductionRefIdentity(
        repository="D1traverser-debug/universal-agent-os",
        ref="refs/heads/main",
    )
    lying_repo = LyingStr("evil/repo", "D1traverser-debug/universal-agent-os")
    lying_ref = LyingStr("refs/tags/main", "refs/heads/main")

    with pytest.raises(PolicyActivationViolation, match="exact builtin string"):
        resolve_ref_conditioned_policy_activation(
            declared_status=REF_CONDITIONAL_POLICY_STATUS,
            current_repository=lying_repo,
            current_ref="refs/heads/main",
            production_identity=production,
        )
    with pytest.raises(PolicyActivationViolation, match="exact builtin string"):
        resolve_ref_conditioned_policy_activation(
            declared_status=REF_CONDITIONAL_POLICY_STATUS,
            current_repository="D1traverser-debug/universal-agent-os",
            current_ref=lying_ref,
            production_identity=production,
        )
    with pytest.raises(PolicyActivationViolation, match="exact builtin string"):
        ProductionRefIdentity(repository=lying_repo, ref=lying_ref)


def test_policy_activation_revalidates_tampered_production_identity_as_exact_strings():
    production = ProductionRefIdentity(
        repository="D1traverser-debug/universal-agent-os",
        ref="refs/heads/main",
    )
    object.__setattr__(
        production,
        "repository",
        LyingStr("evil/repo", "D1traverser-debug/universal-agent-os"),
    )
    object.__setattr__(
        production,
        "ref",
        LyingStr("refs/tags/main", "refs/heads/main"),
    )
    with pytest.raises(PolicyActivationViolation, match="exact builtin string"):
        resolve_ref_conditioned_policy_activation(
            declared_status=REF_CONDITIONAL_POLICY_STATUS,
            current_repository="D1traverser-debug/universal-agent-os",
            current_ref="refs/heads/main",
            production_identity=production,
        )
