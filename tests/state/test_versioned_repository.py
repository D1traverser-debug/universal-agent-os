import pytest
from uaos.contracts.enums import IntentType
from uaos.contracts.models import TaskRecord
from uaos.state import InMemoryVersionedRepository, VersionConflict


def task(goal="g"):
    return TaskRecord("t1", IntentType.NEW_TASK, "core", goal, "done", ())


def test_compare_and_set_rejects_stale_writer():
    repo = InMemoryVersionedRepository[TaskRecord]()
    created = repo.create("t1", task())
    assert created.version == 1
    updated = repo.compare_and_set("t1", 1, task("new"))
    assert updated.version == 2
    with pytest.raises(VersionConflict, match="stale version"):
        repo.compare_and_set("t1", 1, task("stale"))
    assert repo.get("t1").value.goal == "new"


def test_create_rejects_duplicate_identity():
    repo = InMemoryVersionedRepository[TaskRecord]()
    repo.create("t1", task())
    with pytest.raises(VersionConflict, match="already exists"):
        repo.create("t1", task("duplicate"))
