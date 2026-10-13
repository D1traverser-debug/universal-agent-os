from __future__ import annotations

import argparse
import os
import time

WORKFLOW_ID = os.getenv("UAOS_DBOS_CRASH_WORKFLOW_ID", "uaos-live-crash-recovery-v1")


def configure():
    try:
        from dbos import DBOS, DBOSConfig, SetWorkflowID
    except ImportError as exc:
        raise RuntimeError("install .[live] before running DBOS crash probe") from exc
    url = os.getenv("DBOS_SYSTEM_DATABASE_URL")
    if not url:
        raise RuntimeError("DBOS_SYSTEM_DATABASE_URL is required")
    config: DBOSConfig = {
        "name": "uaos-live-crash-probe",
        "application_version": "crash-probe-v1",
        "system_database_url": url,
    }
    DBOS(config=config)

    @DBOS.workflow(name="uaos_crash_recovery_workflow")
    def crash_recovery_workflow() -> str:
        DBOS.sleep(4)
        return "RECOVERED_AFTER_PROCESS_CRASH"

    return DBOS, SetWorkflowID, crash_recovery_workflow


def start_and_crash() -> int:
    DBOS, SetWorkflowID, workflow = configure()
    DBOS.launch()
    with SetWorkflowID(WORKFLOW_ID):
        handle = DBOS.start_workflow(workflow)
    if handle.get_workflow_id() != WORKFLOW_ID:
        raise RuntimeError("unexpected DBOS workflow id")
    time.sleep(0.25)
    os._exit(91)


def recover() -> int:
    DBOS, _, _ = configure()
    DBOS.launch()
    try:
        handle = DBOS.retrieve_workflow(WORKFLOW_ID)
        result = handle.get_result(polling_interval_sec=0.2)
        if result != "RECOVERED_AFTER_PROCESS_CRASH":
            raise RuntimeError(f"unexpected recovered result: {result!r}")
        print(result)
        return 0
    finally:
        DBOS.destroy()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("start", "recover"))
    args = parser.parse_args()
    return start_and_crash() if args.mode == "start" else recover()


if __name__ == "__main__":
    raise SystemExit(main())
