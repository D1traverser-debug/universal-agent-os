from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(ref: str) -> dict:
    return json.loads((ROOT / ref).read_text(encoding="utf-8"))


def current_status() -> dict:
    # No second status owner: index selects, exact task owns lifecycle state.
    index = _json("state/TASK_INDEX.json")
    selected = [
        item for item in index["controller_tasks"]
        if item["resume_eligible"] and item["default_resume"]
    ]
    if len(selected) > 1:
        raise ValueError("multiple active default controller tasks are ambiguous")
    current = None
    if selected:
        item = selected[0]
        state_ref = item["state_ref"]
        if not state_ref.startswith("state/tasks/") or ".." in Path(state_ref).parts:
            raise ValueError("active task must resolve to exact owner task path")
        task = _json(state_ref)
        for key in ("task_id", "status", "current_stage", "authority_context"):
            if item.get(key) != task.get(key):
                raise ValueError(f"task index and exact owner state disagree: {key}")
        current = {
            "task_id": task["task_id"],
            "authority_context": task["authority_context"],
            "status": task["status"],
            "current_stage": task["current_stage"],
            "state_ref": state_ref,
        }

    release = _json("CURRENT_SYSTEM.json")
    historical = _json("docs/assurance/PRODUCTION_READINESS.json")
    return {
        "system_release": release["system_release_version"],
        "current_task": current,
        "readiness_snapshot": {
            "role": "HISTORICAL_ASSURANCE_ONLY__NOT_LIVE_TASK_STATE",
            "status": historical["status"],
        },
    }


if __name__ == "__main__":
    print(json.dumps(current_status(), ensure_ascii=False, indent=2))
