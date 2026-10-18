"""Bounded controlled-runtime gate can close, parent/native autonomy cannot."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _j(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_blocked_operation_production_state_preserves_native_boundary():
    sub = _j("state/tasks/uaos-blocked-operation-continuation-20261018.json")
    evo = _j(sub["evolution_ref"])
    parent = _j("state/tasks/uaos-inheritance-review-20261018.json")
    index = _j("state/TASK_INDEX.json")
    assert sub["status"] == "COMPLETE"
    assert sub["production_evidence"]["ci_run"] == 622
    assert evo["production_evidence"]["main_sha"] == sub["production_evidence"]["sha"]
    assert parent["status"] == "RUNNING"
    assert "NATIVE_AUTONOMY_OPEN" in parent["blocked_operation_continuation"]["status"]
    assert "UNVERIFIED_DIRECT_TRACE" in evo["post_promotion_observation"]["native_skill_autoload"]
    default = [t for t in index["controller_tasks"] if t["default_resume"]]
    assert len(default) == 1 and default[0]["authority_context"] == "UAOS"
    inherited = [t for t in index["controller_tasks"] if t["task_id"] == parent["task_id"]]
    assert len(inherited) == 1
    assert inherited[0]["status"] == parent["status"]
    assert inherited[0]["current_stage"] == parent["current_stage"]


def test_bootstrap_describes_operation_local_safety_and_independent_work():
    entry = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    assert "## Operation-local blockers" in entry
    assert "do not retry the same prohibited mutation through another provider" in entry
    assert "independently check which authorized read-only research" in entry
    assert "FinalizationContext.blocked_tool_operation_observed" in entry
    assert "does not establish native host mediation" in entry
