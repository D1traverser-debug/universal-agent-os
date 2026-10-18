"""The bounded gate fix may close while the original deep controller audit stays open."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_bounded_epistemic_repair_and_parent_have_distinct_outcomes():
    child = _load("state/tasks/uaos-epistemic-entry-20261018.json")
    parent = _load("state/tasks/uaos-inheritance-review-20261018.json")
    evo = _load(child["evolution_ref"])
    index = _load("state/TASK_INDEX.json")

    assert child["parent_task_id"] == parent["task_id"]
    assert parent["epistemic_entry_implementation"]["task_ref"] == "state/tasks/uaos-epistemic-entry-20261018.json"
    assert child["status"] == "COMPLETE"
    assert child["production_evidence"]["ci_run"] == 598
    assert evo["production_evidence"]["main_sha"] == child["production_evidence"]["main_sha"]
    assert "NATIVE_CROSS_SESSION" in evo["status"]
    assert parent["status"] == "RUNNING"
    assert parent["epistemic_entry_implementation"]["native_host"] == "UNVERIFIED_PRE_SEND_PRE_TOOL_HOOK"

    eligible = [task for task in index["controller_tasks"] if task["default_resume"]]
    assert len(eligible) == 1
    assert eligible[0]["authority_context"] == "UAOS"
    assert eligible[0]["status"] == "RUNNING"
    inherited = [task for task in index["controller_tasks"] if task["task_id"] == parent["task_id"]]
    assert len(inherited) == 1
    assert inherited[0]["status"] == "RUNNING"
    assert inherited[0]["current_stage"] == parent["current_stage"]
