import pytest
from uaos.runtime import InMemoryDurableRuntime, RuntimeMessage, RuntimeWorkflowStatus, WorkflowNotFound, WorkflowSpec, WorkflowStateError


def noop():
    return None


def spec(workflow_id="wf-1"):
    return WorkflowSpec(workflow_id=workflow_id, workflow=noop, application_version="v1", attributes={"task_id": "t1"})


def test_workflow_id_is_idempotent():
    runtime = InMemoryDurableRuntime()
    first = runtime.start(spec())
    second = runtime.start(spec())
    assert first == second
    assert first.status is RuntimeWorkflowStatus.PENDING


def test_cancel_and_resume_have_explicit_state():
    runtime = InMemoryDurableRuntime()
    runtime.start(spec())
    runtime.cancel("wf-1")
    assert runtime.retrieve("wf-1").status is RuntimeWorkflowStatus.CANCELLED
    assert runtime.resume("wf-1").status is RuntimeWorkflowStatus.RUNNING


def test_completed_workflow_cannot_be_cancelled_or_resumed():
    runtime = InMemoryDurableRuntime()
    runtime.start(spec())
    runtime.mark_completed("wf-1")
    with pytest.raises(WorkflowStateError):
        runtime.cancel("wf-1")
    with pytest.raises(WorkflowStateError):
        runtime.resume("wf-1")


def test_messages_are_topic_scoped_fifo_and_idempotent():
    runtime = InMemoryDurableRuntime()
    runtime.start(spec())
    msg = RuntimeMessage("m1", "wf-1", {"x": 1}, topic="requirements", idempotency_key="k1")
    runtime.send(msg)
    runtime.send(msg)
    runtime.send(RuntimeMessage("m2", "wf-1", {"x": 2}, topic="approval"))
    assert runtime.recv("wf-1", "approval").message_id == "m2"
    assert runtime.recv("wf-1", "requirements").message_id == "m1"
    assert runtime.recv("wf-1", "requirements") is None


def test_events_update_latest_value():
    runtime = InMemoryDurableRuntime()
    runtime.start(spec())
    runtime.set_event("wf-1", "stage", "research")
    runtime.set_event("wf-1", "stage", "write")
    assert runtime.get_event("wf-1", "stage") == "write"


def test_unknown_workflow_is_never_guessed():
    runtime = InMemoryDurableRuntime()
    with pytest.raises(WorkflowNotFound):
        runtime.retrieve("missing")
