from pathlib import Path
import tempfile

import pytest

from uaos.runtime import RuntimeMessage, RuntimeWorkflowStatus, SQLiteCheckpointRuntime, WorkflowSpec
from uaos.state import SQLiteAppendOnlyLedger, SQLiteVersionedRepository, VersionConflict


def noop() -> None:
    pass


def test_sqlite_cas_survives_reopen() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "uaos.db"
        repository = SQLiteVersionedRepository(path, "task")
        assert repository.create("t1", {"x": 1}).version == 1
        assert repository.compare_and_set("t1", 1, {"x": 2}).version == 2
        reopened = SQLiteVersionedRepository(path, "task")
        assert reopened.get("t1").value == {"x": 2}
        with pytest.raises(VersionConflict):
            reopened.compare_and_set("t1", 1, {"x": 3})


def test_sqlite_ledger_is_append_only_across_reopen() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "uaos.db"
        ledger = SQLiteAppendOnlyLedger(path)
        ledger.append(
            event_id="e1",
            aggregate_type="task",
            aggregate_id="t1",
            event_type="created",
            payload={"x": 1},
        )
        reopened = SQLiteAppendOnlyLedger(path)
        assert reopened.events_for("task", "t1")[0].event_id == "e1"
        with pytest.raises(ValueError, match="duplicate event_id"):
            reopened.append(
                event_id="e1",
                aggregate_type="task",
                aggregate_id="t1",
                event_type="duplicate",
                payload={},
            )


def test_sqlite_checkpoint_runtime_survives_reopen_and_dedupes_messages() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "uaos.db"
        runtime = SQLiteCheckpointRuntime(path)
        runtime.start(WorkflowSpec("w1", noop, application_version="1"))
        runtime.resume("w1")
        runtime.send(RuntimeMessage("m1", "w1", {"a": 1}, "control", "k1"))
        runtime.send(RuntimeMessage("m2", "w1", {"a": 2}, "control", "k1"))
        runtime.set_event("w1", "checkpoint", {"stage": "research"})

        reopened = SQLiteCheckpointRuntime(path)
        assert reopened.retrieve("w1").status is RuntimeWorkflowStatus.RUNNING
        assert reopened.get_event("w1", "checkpoint") == {"stage": "research"}
        assert reopened.recv("w1", "control").payload == {"a": 1}
        assert reopened.recv("w1", "control") is None
