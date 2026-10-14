from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
import uuid


@dataclass(frozen=True, slots=True)
class MaintenanceScheduleProbeResult:
    schedule_created: bool
    queue_global_concurrency: int | None
    trigger_executed: bool
    cleanup_verified: bool


def run_maintenance_schedule_probe(system_database_url: str) -> MaintenanceScheduleProbeResult:
    try:
        from dbos import DBOS, DBOSConfig
    except ImportError as exc:
        raise RuntimeError("live maintenance probe requires dbos; install .[live]") from exc

    config: DBOSConfig = {
        "name": "uaos-live-maintenance-probe",
        "application_version": "maintenance-probe-v1",
        "system_database_url": system_database_url,
    }
    DBOS(config=config)

    @DBOS.workflow(name="uaos_live_maintenance_scheduled_workflow")
    def maintenance_workflow(scheduled_time: datetime, context: Any) -> None:
        DBOS.set_event("uaos-maintenance-probe", {
            "token": context["token"],
            "scheduled_time": scheduled_time.isoformat(),
        })

    DBOS.launch()
    schedule_name = f"uaos-live-maintenance-{uuid.uuid4().hex}"
    token = uuid.uuid4().hex
    queue_name = "uaos-live-maintenance-queue"
    try:
        queue = DBOS.register_queue(
            queue_name,
            global_concurrency=1,
            worker_concurrency=1,
            on_conflict="always_update",
        )
        DBOS.create_schedule(
            schedule_name=schedule_name,
            workflow_fn=maintenance_workflow,
            schedule="0 0 0 1 1 *",
            context={"token": token},
            queue_name=queue_name,
        )
        created = DBOS.get_schedule(schedule_name) is not None
        handle = DBOS.trigger_schedule(schedule_name)
        handle.get_result()
        event = DBOS.get_event(handle.get_workflow_id(), "uaos-maintenance-probe", timeout_seconds=10)
        executed = isinstance(event, dict) and event.get("token") == token
        DBOS.delete_schedule(schedule_name)
        cleanup = DBOS.get_schedule(schedule_name) is None
        if not created or not executed or not cleanup:
            raise RuntimeError("DBOS maintenance schedule probe failed")
        return MaintenanceScheduleProbeResult(created, queue.global_concurrency, executed, cleanup)
    finally:
        DBOS.delete_schedule(schedule_name)
        DBOS.destroy()
