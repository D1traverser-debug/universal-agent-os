import os
from pathlib import Path
import threading

import pytest

from uaos.execution import (
    ExecutionDisposition,
    ExecutionRequest,
    LocalWorkspaceExecutor,
)
import uaos.execution.local_workspace as local_workspace


def _update_request(content: str, expected_hash: str | None = None) -> ExecutionRequest:
    payload = {"content": content}
    if expected_hash is not None:
        payload["expected_current_hash"] = expected_hash
    return ExecutionRequest(
        "update",
        "local.update_text",
        "policy.txt",
        payload,
    )


def test_update_expected_hash_holds_parent_directory_lock_through_commit(tmp_path: Path):
    executor = LocalWorkspaceExecutor(tmp_path)
    target = tmp_path / "policy.txt"
    target.write_text("v1", encoding="utf-8")
    expected = executor._sha256(b"v1")

    parent_fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    local_workspace.fcntl.flock(parent_fd, local_workspace.fcntl.LOCK_EX)
    completed = threading.Event()
    outcomes = []

    def run_update():
        outcomes.append(executor.execute(_update_request("v2", expected)))
        completed.set()

    thread = threading.Thread(target=run_update, daemon=True)
    thread.start()
    try:
        assert not completed.wait(0.15)
    finally:
        local_workspace.fcntl.flock(parent_fd, local_workspace.fcntl.LOCK_UN)
        os.close(parent_fd)

    assert completed.wait(2.0)
    thread.join(timeout=2.0)
    assert outcomes[0].disposition is ExecutionDisposition.CONFIRMED
    assert target.read_text(encoding="utf-8") == "v2"
    assert "ADVISORY_PARENT_DIRECTORY_LOCK" in outcomes[0].evidence["concurrency_semantics"]


def test_create_reports_unknown_if_directory_fsync_fails_after_link_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    executor = LocalWorkspaceExecutor(tmp_path)
    real_fsync = os.fsync
    calls = 0

    def fail_second_fsync(fd):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic directory fsync failure")
        return real_fsync(fd)

    monkeypatch.setattr(local_workspace.os, "fsync", fail_second_fsync)
    outcome = executor.execute(
        ExecutionRequest(
            "create",
            "local.create_text",
            "created.txt",
            {"content": "committed"},
        )
    )

    assert outcome.disposition is ExecutionDisposition.UNKNOWN
    assert outcome.evidence["commit_point_reached"] is True
    assert (tmp_path / "created.txt").read_text(encoding="utf-8") == "committed"


def test_update_reports_unknown_if_directory_fsync_fails_after_rename_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    executor = LocalWorkspaceExecutor(tmp_path)
    target = tmp_path / "policy.txt"
    target.write_text("v1", encoding="utf-8")
    expected = executor._sha256(b"v1")
    real_fsync = os.fsync
    calls = 0

    def fail_second_fsync(fd):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic directory fsync failure")
        return real_fsync(fd)

    monkeypatch.setattr(local_workspace.os, "fsync", fail_second_fsync)
    outcome = executor.execute(_update_request("v2", expected))

    assert outcome.disposition is ExecutionDisposition.UNKNOWN
    assert outcome.evidence["commit_point_reached"] is True
    assert target.read_text(encoding="utf-8") == "v2"
