from contextlib import contextmanager
from types import SimpleNamespace
from uaos.runtime import DBOSRuntime, RuntimeMessage, RuntimeWorkflowStatus, WorkflowSpec


class Handle:
    def __init__(self, workflow_id, status):
        self._workflow_id = workflow_id
        self._status = status

    def get_workflow_id(self):
        return self._workflow_id

    def get_status(self):
        return self._status


class FakeDBOS:
    def __init__(self):
        self.next_id = None
        self.handles = {}
        self.sent = []
        self.cancelled = []
        self.events = {("wf-1", "stage"): "write"}

    def start_workflow(self, workflow, *args, **kwargs):
        del workflow, args, kwargs
        handle = self.handles.setdefault(self.next_id, Handle(self.next_id, "ENQUEUED"))
        return handle

    def retrieve_workflow(self, workflow_id):
        return self.handles[workflow_id]

    def resume_workflow(self, workflow_id):
        self.handles[workflow_id] = Handle(workflow_id, "RUNNING")
        return self.handles[workflow_id]

    def cancel_workflow(self, workflow_id):
        self.cancelled.append(workflow_id)

    def send(self, destination_id, payload, topic=None, *, idempotency_key=None):
        self.sent.append((destination_id, payload, topic, idempotency_key))

    def get_event(self, workflow_id, key, timeout_seconds=0):
        return self.events.get((workflow_id, key))


def runtime():
    fake = FakeDBOS()

    @contextmanager
    def set_workflow_id(workflow_id):
        fake.next_id = workflow_id
        try:
            yield
        finally:
            fake.next_id = None

    return DBOSRuntime(dbos_api=fake, set_workflow_id=set_workflow_id), fake


def test_dbos_adapter_uses_exact_workflow_id_and_maps_status():
    adapter, _ = runtime()
    ref = adapter.start(WorkflowSpec("wf-1", lambda: None))
    assert ref.workflow_id == "wf-1"
    assert ref.status is RuntimeWorkflowStatus.PENDING
    assert adapter.resume("wf-1").status is RuntimeWorkflowStatus.RUNNING


def test_dbos_adapter_forwards_idempotent_message_and_event():
    adapter, fake = runtime()
    adapter.start(WorkflowSpec("wf-1", lambda: None))
    adapter.send(RuntimeMessage("m1", "wf-1", {"x": 1}, "requirement_update", "idem"))
    assert fake.sent == [("wf-1", {"x": 1}, "requirement_update", "idem")]
    assert adapter.get_event("wf-1", "stage") == "write"


def test_dbos_status_mapping_is_conservative():
    assert DBOSRuntime._map_status(SimpleNamespace(status="SOMETHING_NEW")) is RuntimeWorkflowStatus.UNKNOWN
