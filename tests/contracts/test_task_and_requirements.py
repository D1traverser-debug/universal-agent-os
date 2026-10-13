import pytest
from uaos.contracts.enums import IntentType, RequirementState, ScopeType, TaskStatus
from uaos.contracts.models import RequirementRecord, TaskRecord
from uaos.contracts.requirements import cancel_requirement, supersede_requirement


def test_global_requirement_cannot_have_scope_id():
    with pytest.raises(ValueError, match="GLOBAL"):
        RequirementRecord("r1", "global rule", ScopeType.GLOBAL, scope_id="video")


def test_scoped_requirement_requires_scope_id():
    with pytest.raises(ValueError, match="requires scope_id"):
        RequirementRecord("r1", "video rule", ScopeType.SUBSYSTEM)


def test_supersession_is_explicit_and_same_scope():
    old = RequirementRecord("r-old", "old", ScopeType.SUBSYSTEM, scope_id="video")
    new = RequirementRecord("r-new", "new", ScopeType.SUBSYSTEM, scope_id="video", supersedes=("r-old",))
    old2, new2 = supersede_requirement(old, new)
    assert old2.lifecycle_state is RequirementState.SUPERSEDED
    assert new2.lifecycle_state is RequirementState.ACTIVE


def test_cancellation_marks_old_requirement_inactive():
    req = RequirementRecord("r1", "rule", ScopeType.TASK, scope_id="task-1")
    assert cancel_requirement(req).lifecycle_state is RequirementState.CANCELLED


def test_complete_task_requires_completion_evidence():
    with pytest.raises(ValueError, match="completion_evidence"):
        TaskRecord(task_id="task-1", intent=IntentType.NEW_TASK, owner_domain="financial-writing", goal="write article", done_condition="verified article delivered", requirement_snapshot=("r1",), status=TaskStatus.COMPLETE)


def test_complete_task_with_evidence_is_valid():
    task = TaskRecord(task_id="task-1", intent=IntentType.NEW_TASK, owner_domain="financial-writing", goal="write article", done_condition="verified article delivered", requirement_snapshot=("r1",), status=TaskStatus.COMPLETE, completion_evidence=("delivery:artifact-42",))
    assert task.status is TaskStatus.COMPLETE
