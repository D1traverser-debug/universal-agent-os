"""Bounded evidence replay for the user's first installed-Skill native canary."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_canary_is_attempted_and_not_falsely_marked_successful():
    account = _json("state/observations/native-account-install-handoff-20261018.json")
    canary = _json(account["canary"]["first_run_observation_ref"])
    assert canary["sample_count"] == 1
    assert canary["user_supplied_inputs"]["prior_skill_update"].startswith("USER_CONFIRMED")
    assert account["required_user_actions"] == []
    assert canary["rubric"]["fresh_chat_initiation"] == "OBSERVED_FROM_USER_TRANSCRIPT"
    assert canary["rubric"]["Skill_auto_invocation"] == "UNVERIFIED"
    assert canary["rubric"]["full_native_conformance"] == "NOT_VERIFIED"
    assert canary["rubric"]["single_canary_overall"].startswith("PARTIAL")


def test_canary_incomplete_action_does_not_close_parent_task():
    account = _json("state/observations/native-account-install-handoff-20261018.json")
    canary = _json(account["canary"]["first_run_observation_ref"])
    task = _json(account["continued_parent_task_ref"])
    assert task["status"] == "RUNNING"
    assert task["native_account_cutover"]["required_user_part"].startswith("NONE")
    assert "NO_DURABLE_FOLLOWTHROUGH" in canary["rubric"]["action_continuation"]
    assert canary["rubric"]["source_write"].startswith("REPORTED_BLOCKED")
    assert "no-followthrough" in " ".join(canary["followup_disposition"]["next_agent_work"])
