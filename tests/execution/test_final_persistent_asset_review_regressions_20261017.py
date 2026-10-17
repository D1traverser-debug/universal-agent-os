import os
from enum import StrEnum
from pathlib import Path

import pytest

from uaos.execution import (
    CapabilityHealth,
    CapabilityObservation,
    CapabilityRegistry,
    ExecutionDisposition,
    ExecutionRequest,
    LocalWorkspaceExecutor,
    MutationContract,
    MutationPersistence,
)
import uaos.execution.local_workspace as local_workspace


class NoopExecutor:
    def execute(self, request):
        raise AssertionError("not called")


class SpoofedUaosEnum(StrEnum):
    VALUE = "VALUE"


SpoofedUaosEnum.__module__ = "uaos.fake"


def _observation():
    return CapabilityObservation(
        capability_id="writer",
        health=CapabilityHealth.AVAILABLE,
        observed_at_epoch=1.0,
        supported_actions=("mutate",),
        quality_score=1.0,
        executor_kind="test",
    )


def test_registry_public_views_never_expose_executor_or_canonicalizer():
    registry = CapabilityRegistry()
    registry.register(
        _observation(),
        NoopExecutor(),
        mutation_contracts={"mutate": MutationContract(MutationPersistence.EPHEMERAL)},
    )
    public = registry.get("writer")
    assert not hasattr(public, "executor")
    assert not hasattr(public, "canonicalize_target")
    assert all(not hasattr(item, "executor") for item in registry.all())


def test_execution_value_domain_rejects_module_spoofed_enum_and_detaches_known_enum():
    with pytest.raises(TypeError, match="unsupported enum"):
        ExecutionRequest("a1", "read", "topic", {"mode": SpoofedUaosEnum.VALUE})

    member = ExecutionDisposition.UNKNOWN
    request = ExecutionRequest("a2", "read", "topic", {"mode": member})
    frozen_mode = request.payload["mode"]
    assert isinstance(frozen_mode, tuple)
    assert frozen_mode[0] == "__uaos_enum__"
    object.__setattr__(member, "mutable_aux", {"provider": "forged"})
    try:
        assert request.payload["mode"] == frozen_mode
        assert not isinstance(request.payload["mode"], ExecutionDisposition)
    finally:
        try:
            delattr(member, "mutable_aux")
        except AttributeError:
            pass


def _post_commit_unknown(executor: LocalWorkspaceExecutor, tmp_path: Path, monkeypatch):
    request = ExecutionRequest(
        "create",
        "local.create_text",
        "created.txt",
        {"content": "committed"},
    )
    real_fsync = os.fsync
    calls = 0

    def fail_directory_fsync(fd):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic directory fsync failure")
        return real_fsync(fd)

    monkeypatch.setattr(local_workspace.os, "fsync", fail_directory_fsync)
    unknown = executor.execute(request)
    assert unknown.disposition is ExecutionDisposition.UNKNOWN
    monkeypatch.setattr(local_workspace.os, "fsync", real_fsync)
    assert (tmp_path / "created.txt").read_text(encoding="utf-8") == "committed"
    return request, unknown


def test_local_post_commit_unknown_reconciles_to_confirmed_when_digest_and_fsync_verify(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    executor = LocalWorkspaceExecutor(tmp_path)
    try:
        request, unknown = _post_commit_unknown(executor, tmp_path, monkeypatch)
        resolved = executor.reconcile(request, unknown)
        assert resolved.disposition is ExecutionDisposition.CONFIRMED
        assert resolved.evidence["reconciled_from_post_commit_unknown"] is True
        assert resolved.evidence["sha256"] == unknown.evidence["sha256"]
    finally:
        executor.close()


def test_local_post_commit_unknown_reconcile_fails_if_committed_target_no_longer_matches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    executor = LocalWorkspaceExecutor(tmp_path)
    try:
        request, unknown = _post_commit_unknown(executor, tmp_path, monkeypatch)
        (tmp_path / "created.txt").write_text("different", encoding="utf-8")
        resolved = executor.reconcile(request, unknown)
        assert resolved.disposition is ExecutionDisposition.FAILED
        assert "digest mismatch" in (resolved.error or "")
    finally:
        executor.close()
