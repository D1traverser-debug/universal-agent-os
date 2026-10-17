from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event, Lock

import pytest

from uaos.execution import (
    ActionCoordinator,
    AssetLifecycle,
    AssetRole,
    CapabilityHealth,
    CapabilityObservation,
    CapabilityRegistry,
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


class BlockingReconciler:
    def __init__(self) -> None:
        self.calls = 0
        self._lock = Lock()
        self.entered = Event()
        self.release = Event()

    def execute(self, request: ExecutionRequest) -> ExecutionOutcome:
        return ExecutionOutcome(ExecutionDisposition.UNKNOWN, error="ambiguous")

    def reconcile(self, request: ExecutionRequest, unknown: ExecutionOutcome) -> ExecutionOutcome:
        with self._lock:
            self.calls += 1
            self.entered.set()
        assert self.release.wait(timeout=5)
        return ExecutionOutcome(ExecutionDisposition.CONFIRMED, output="resolved")


def _fixture() -> tuple[ActionCoordinator, ExecutionRequest, BlockingReconciler]:
    registry = CapabilityRegistry()
    executor = BlockingReconciler()
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
        asset_id="asset:repo:file",
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
        action_id="write-1",
        action_name="write",
        target="repo:file",
        payload={"value": 1},
        required_permissions=("repo:write",),
        target_authority="UAOS",
    )
    return coordinator, request, executor


def test_unknown_execution_id_is_single_flight_under_concurrent_reconcile():
    coordinator, request, executor = _fixture()
    unknown = coordinator.execute(request)
    assert unknown.outcome.disposition is ExecutionDisposition.UNKNOWN
    assert unknown.execution_id

    start = Barrier(3)

    def attempt():
        start.wait(timeout=5)
        try:
            return coordinator.reconcile(request, unknown)
        except PersistentAssetViolation as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(attempt)
        second = pool.submit(attempt)
        start.wait(timeout=5)
        assert executor.entered.wait(timeout=5)
        # Keep the first reconciler inside its side-effecting repair while the second
        # competes for the same execution id. Only one is allowed to enter reconcile().
        executor.release.set()
        results = (first.result(timeout=5), second.result(timeout=5))

    assert executor.calls == 1
    confirmed = [
        result for result in results
        if not isinstance(result, Exception)
        and result.outcome.disposition is ExecutionDisposition.CONFIRMED
    ]
    rejected = [result for result in results if isinstance(result, PersistentAssetViolation)]
    assert len(confirmed) == 1
    assert len(rejected) == 1


def test_terminal_reconciliation_consumes_execution_id_against_serial_replay():
    coordinator, request, executor = _fixture()
    unknown = coordinator.execute(request)
    executor.release.set()
    resolved = coordinator.reconcile(request, unknown)
    assert resolved.outcome.disposition is ExecutionDisposition.CONFIRMED
    with pytest.raises(PersistentAssetViolation, match="not owned|already|terminal|claim"):
        coordinator.reconcile(request, unknown)
    assert executor.calls == 1


def test_reconciler_exception_releases_claim_and_preserves_retryable_unknown():
    coordinator, request, executor = _fixture()
    unknown = coordinator.execute(request)
    calls = 0

    def flaky_reconcile(request: ExecutionRequest, prior: ExecutionOutcome) -> ExecutionOutcome:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("provider transport failed before reliable disposition")
        return ExecutionOutcome(ExecutionDisposition.CONFIRMED, output="resolved-after-retry")

    executor.reconcile = flaky_reconcile  # type: ignore[method-assign]
    with pytest.raises(RuntimeError, match="provider transport failed"):
        coordinator.reconcile(request, unknown)

    # The first exception must release the single-flight claim without consuming the
    # coordinator-owned UNKNOWN authority record, so a later explicit retry is legal.
    resolved = coordinator.reconcile(request, unknown)
    assert resolved.outcome.disposition is ExecutionDisposition.CONFIRMED
    assert resolved.outcome.output == "resolved-after-retry"
    assert calls == 2
