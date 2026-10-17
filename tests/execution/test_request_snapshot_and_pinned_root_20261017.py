from __future__ import annotations

import os
from pathlib import Path

import pytest

from uaos.execution import (
    ActionCoordinator,
    CapabilityHealth,
    CapabilityObservation,
    CapabilityRegistry,
    ExecutionDisposition,
    ExecutionOutcome,
    ExecutionRequest,
    LocalWorkspaceExecutor,
    PersistentAssetViolation,
)


class UnknownReadExecutor:
    def __init__(self) -> None:
        self.reconcile_calls = 0

    def execute(self, request: ExecutionRequest) -> ExecutionOutcome:
        return ExecutionOutcome(ExecutionDisposition.UNKNOWN, provider_ref="read:1")

    def reconcile(self, request: ExecutionRequest, unknown: ExecutionOutcome) -> ExecutionOutcome:
        self.reconcile_calls += 1
        return ExecutionOutcome(ExecutionDisposition.CONFIRMED, output=request.payload)


def _read_observation() -> CapabilityObservation:
    return CapabilityObservation(
        capability_id="reader",
        health=CapabilityHealth.AVAILABLE,
        observed_at_epoch=1.0,
        supported_actions=("read",),
        permissions=(),
        quality_score=1.0,
        estimated_cost=0.0,
        executor_kind="test",
    )


def test_unknown_record_detaches_mutable_payload_and_preserves_mapping_key_identity():
    registry = CapabilityRegistry()
    executor = UnknownReadExecutor()
    registry.register(_read_observation(), executor, read_only_actions={"read"})
    coordinator = ActionCoordinator(registry)

    payload = {1: {"hidden": 1}, "1": "visible"}
    request = ExecutionRequest("a1", "read", "topic", payload)
    unknown = coordinator.execute(request)
    assert unknown.outcome.disposition is ExecutionDisposition.UNKNOWN

    # This used to mutate the same object retained by the UNKNOWN record. The older
    # fingerprint also collapsed int key 1 and str key "1" to the same JSON key.
    payload[1]["hidden"] = 2
    with pytest.raises(PersistentAssetViolation, match="originally executed request"):
        coordinator.reconcile(request, unknown)
    assert executor.reconcile_calls == 0

    first = coordinator.execute(
        ExecutionRequest("a2", "read", "topic", {1: "left", "1": "same"})
    )
    second = coordinator.execute(
        ExecutionRequest("a3", "read", "topic", {1: "right", "1": "same"})
    )
    assert first.admission.request_fingerprint != second.admission.request_fingerprint


def test_local_create_does_not_create_unadmitted_parent_directories(tmp_path: Path):
    root = tmp_path / "workspace"
    executor = LocalWorkspaceExecutor(root)
    try:
        result = executor.execute(
            ExecutionRequest(
                "a1",
                "local.create_text",
                "missing/child.txt",
                {"content": "x"},
            )
        )
        assert result.disposition is ExecutionDisposition.FAILED
        assert "parent directory does not exist" in (result.error or "")
        assert not (root / "missing").exists()
    finally:
        executor.close()


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink support required")
def test_local_workspace_root_is_pinned_against_ancestor_symlink_swap(tmp_path: Path):
    holder = tmp_path / "holder"
    root = holder / "workspace"
    root.mkdir(parents=True)
    executor = LocalWorkspaceExecutor(root)

    moved_holder = tmp_path / "holder-original"
    outside = tmp_path / "outside"
    outside_workspace = outside / "workspace"
    outside_workspace.mkdir(parents=True)

    try:
        holder.rename(moved_holder)
        try:
            os.symlink(outside, holder, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            pytest.skip(f"symlink creation unavailable: {exc}")

        result = executor.execute(
            ExecutionRequest(
                "a1",
                "local.create_text",
                "bound.txt",
                {"content": "pinned"},
            )
        )
        assert result.disposition is ExecutionDisposition.CONFIRMED
        assert (moved_holder / "workspace" / "bound.txt").read_text(encoding="utf-8") == "pinned"
        assert not (outside_workspace / "bound.txt").exists()
    finally:
        executor.close()
