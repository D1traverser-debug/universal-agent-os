from uaos.execution import (
    ActionCoordinator,
    AssetLifecycle,
    AssetRole,
    CapabilityHealth,
    CapabilityObservation,
    CapabilityRegistry,
    CoordinatedExecution,
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
import pytest


class ReconcilingExecutor:
    def __init__(self) -> None:
        self.reconcile_calls = []

    def execute(self, request):
        return ExecutionOutcome(
            ExecutionDisposition.UNKNOWN,
            output={"repair": {"token": "output:original"}},
            provider_ref="provider:original",
            evidence={
                "operation_ref": "op:original",
                "nested": {"token": "evidence:original"},
            },
            error="timeout",
        )

    def reconcile(self, request, unknown):
        self.reconcile_calls.append((request, unknown))
        return ExecutionOutcome(
            ExecutionDisposition.CONFIRMED,
            output="resolved",
            provider_ref=unknown.provider_ref,
        )


def _coordinator():
    registry = CapabilityRegistry()
    executor = ReconcilingExecutor()
    registry.register(
        CapabilityObservation(
            capability_id="writer",
            health=CapabilityHealth.AVAILABLE,
            observed_at_epoch=1.0,
            supported_actions=("write",),
            permissions=("repo:write",),
            quality_score=1.0,
            estimated_cost=0.0,
            executor_kind="test",
        ),
        executor,
        mutation_contracts={
            "write": MutationContract(
                MutationPersistence.DURABLE_OR_EXTERNAL,
                CrudOperation.UPDATE,
            )
        },
        canonicalize_target=lambda target: target,
    )
    asset = PersistentAssetDescriptor(
        asset_id="repo:file",
        resource_ref="repo:file",
        surface=PersistentSurface.GITHUB,
        role=AssetRole.AUTHORITY,
        lifecycle=AssetLifecycle.CURRENT,
        owner_authority="UAOS",
        allowed_operations=frozenset({CrudOperation.READ, CrudOperation.UPDATE}),
        canonical_authority_ref="github://D1traverser-debug/universal-agent-os@main",
    )
    coordinator = ActionCoordinator(
        registry,
        authority_context="UAOS",
        persistent_asset_catalog=PersistentAssetCatalog((asset,)),
    )
    request = ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {"content": "x"},
        required_permissions=("repo:write",),
        target_authority="UAOS",
    )
    return coordinator, request, executor


def test_reconcile_ignores_forged_public_unknown_outcome_and_uses_owned_record():
    coordinator, request, executor = _coordinator()
    unknown = coordinator.execute(request)
    assert unknown.execution_id

    forged = CoordinatedExecution(
        capability_id=unknown.capability_id,
        outcome=ExecutionOutcome(
            ExecutionDisposition.UNKNOWN,
            provider_ref="provider:forged",
            evidence={"operation_ref": "op:forged"},
            error="forged",
        ),
        admission=unknown.admission,
        original_request=unknown.original_request,
        execution_id=unknown.execution_id,
    )
    resolved = coordinator.reconcile(request, forged)

    assert resolved.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert resolved.outcome.provider_ref == "provider:original"
    assert len(executor.reconcile_calls) == 1
    passed_unknown = executor.reconcile_calls[0][1]
    assert passed_unknown.provider_ref == "provider:original"
    assert passed_unknown.evidence["operation_ref"] == "op:original"
    assert passed_unknown.error == "timeout"


def test_public_unknown_nested_mutation_cannot_change_coordinator_owned_reconcile_truth():
    coordinator, request, executor = _coordinator()
    unknown = coordinator.execute(request)
    assert unknown.execution_id

    public_evidence = unknown.outcome.evidence
    public_output = unknown.outcome.output
    public_evidence["operation_ref"] = "op:forged"
    public_evidence["nested"]["token"] = "evidence:forged"
    public_output["repair"]["token"] = "output:forged"

    resolved = coordinator.reconcile(request, unknown)
    assert resolved.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert len(executor.reconcile_calls) == 1
    passed_unknown = executor.reconcile_calls[0][1]
    assert passed_unknown.evidence == {
        "operation_ref": "op:original",
        "nested": {"token": "evidence:original"},
    }
    assert passed_unknown.output == {"repair": {"token": "output:original"}}


def test_execution_outcome_snapshots_source_containers_at_construction():
    evidence = {"nested": {"token": "evidence:original"}}
    output = {"nested": ["output:original"]}
    outcome = ExecutionOutcome(
        ExecutionDisposition.UNKNOWN,
        output=output,
        evidence=evidence,
    )
    evidence["nested"]["token"] = "evidence:mutated"
    output["nested"].append("output:mutated")

    assert outcome.evidence == {"nested": {"token": "evidence:original"}}
    assert outcome.output == {"nested": ["output:original"]}


def test_reconcile_rejects_unowned_execution_id_even_with_copied_receipt():
    coordinator, request, executor = _coordinator()
    unknown = coordinator.execute(request)
    forged = CoordinatedExecution(
        capability_id=unknown.capability_id,
        outcome=unknown.outcome,
        admission=unknown.admission,
        original_request=unknown.original_request,
        execution_id="forged-execution-id",
    )
    with pytest.raises(PersistentAssetViolation, match="not owned by this coordinator"):
        coordinator.reconcile(request, forged)
    assert executor.reconcile_calls == []
