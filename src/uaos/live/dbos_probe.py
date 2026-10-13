from __future__ import annotations

from dataclasses import dataclass
import uuid


@dataclass(frozen=True, slots=True)
class DBOSProbeResult:
    workflow_id: str
    result: str
    duplicate_returned_existing: bool


def run_dbos_probe(system_database_url: str) -> DBOSProbeResult:
    try:
        from dbos import DBOS, DBOSConfig, SetWorkflowID
    except ImportError as exc:
        raise RuntimeError("live DBOS probe requires dbos; install .[live]") from exc

    config: DBOSConfig = {
        "name": "uaos-live-probe",
        "application_version": "live-probe-v1",
        "system_database_url": system_database_url,
    }
    DBOS(config=config)

    @DBOS.workflow(name="uaos_live_probe_workflow")
    def probe(value: str) -> str:
        return f"ok:{value}"

    DBOS.launch()
    workflow_id = f"uaos-live-{uuid.uuid4().hex}"
    try:
        with SetWorkflowID(workflow_id):
            first = DBOS.start_workflow(probe, "one")
        first_result = first.get_result()
        with SetWorkflowID(workflow_id):
            second = DBOS.start_workflow(probe, "different-input-must-not-rerun")
        second_result = second.get_result()
        same_identity = second.get_workflow_id() == workflow_id
        duplicate_existing = same_identity and second_result == first_result
        if first_result != "ok:one" or not duplicate_existing:
            raise RuntimeError("DBOS workflow identity/idempotency probe failed")
        return DBOSProbeResult(workflow_id, first_result, duplicate_existing)
    finally:
        DBOS.destroy()
