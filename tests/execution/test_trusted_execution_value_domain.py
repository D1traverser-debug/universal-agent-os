import pytest

from uaos.execution import (
    ActionCoordinator,
    CapabilityHealth,
    CapabilityObservation,
    CapabilityRegistry,
    ExecutionDisposition,
    ExecutionOutcome,
    ExecutionRequest,
    MutationContract,
    MutationPersistence,
)


class MutableStr(str):
    def __new__(cls, value):
        item = super().__new__(cls, value)
        item.route = {"provider": "original"}
        return item


class StickyMutable:
    def __init__(self):
        self.route = "original"

    def __deepcopy__(self, memo):
        return self


class ReconcilingExecutor:
    def __init__(self):
        self.seen_token = None

    def execute(self, request):
        return ExecutionOutcome(
            ExecutionDisposition.UNKNOWN,
            provider_ref="provider:1",
            evidence={"sent": True},
        )

    def reconcile(self, request, unknown):
        self.seen_token = request.payload["token"]
        return ExecutionOutcome(ExecutionDisposition.CONFIRMED, output="ok")


class NoopExecutor:
    def execute(self, request):
        return ExecutionOutcome(ExecutionDisposition.CONFIRMED)


def observation(capability_id, actions):
    return CapabilityObservation(
        capability_id,
        CapabilityHealth.AVAILABLE,
        1.0,
        tuple(actions),
        quality_score=1.0,
        executor_kind="test",
    )


def test_request_snapshot_normalizes_mutable_scalar_subclasses_before_unknown_reconcile():
    token = MutableStr("stable-token")
    request = ExecutionRequest("a1", "read", "resource", {"token": "initial"})
    object.__setattr__(request, "payload", {"token": token})

    registry = CapabilityRegistry()
    executor = ReconcilingExecutor()
    registry.register(
        observation("reader", ("read",)),
        executor,
        read_only_actions={"read"},
    )
    coordinator = ActionCoordinator(registry)
    unknown = coordinator.execute(request)

    token.route["provider"] = "forged"
    assert type(unknown.original_request.payload["token"]) is str
    assert unknown.original_request.payload["token"] == "stable-token"

    resolved = coordinator.reconcile(unknown.original_request, unknown)
    assert resolved.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert type(executor.seen_token) is str
    assert not hasattr(executor.seen_token, "route")


def test_execution_outcome_rejects_custom_object_even_when_deepcopy_claims_success():
    sticky = StickyMutable()
    with pytest.raises(TypeError, match="trusted immutable value domain"):
        ExecutionOutcome(
            ExecutionDisposition.UNKNOWN,
            output=sticky,
            evidence={"route": sticky},
        )


def test_registered_mutation_contract_mapping_is_immutable_after_registration():
    registry = CapabilityRegistry()
    original = MutationContract(MutationPersistence.EPHEMERAL)
    registry.register(
        observation("mutator", ("mutate",)),
        NoopExecutor(),
        mutation_contracts={"mutate": original},
    )
    registered = registry.get("mutator")
    generation = registered.registration_generation

    with pytest.raises(TypeError):
        registered.mutation_contracts["mutate"] = MutationContract(
            MutationPersistence.DURABLE_OR_EXTERNAL,
            "UPDATE",
        )

    current = registry.get("mutator")
    current_contract = current.mutation_contract_for("mutate")
    assert current.registration_generation == generation
    assert current_contract is not original
    assert current_contract is not None
    assert current_contract.persistence is MutationPersistence.EPHEMERAL
    assert current_contract.operation is None
