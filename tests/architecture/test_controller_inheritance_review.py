import json
from pathlib import Path

from uaos.runtime.native_session_profile import build_native_session_runtime_profile

ROOT = Path(__file__).resolve().parents[2]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_controller_inheritance_review_is_unconditional_after_explicit_selection():
    session = read_json("config/SESSION_INTERACTION_POLICY.json")
    review = session["controller_inheritance_review"]
    assert review["required"] is True
    assert review["trigger"] == "ON_EVERY_EXPLICIT_UAOS_CONTROLLER_SELECTION__INCLUDING_AFTER_RESUME"
    assert review["scope"].startswith("UAOS_CONTROLLER_ONLY")
    assert "ALL_REGISTERED_REPOSITORIES" in review["coverage_rule"]
    assert "UNREAD_UNVERIFIED_OR_UNMEASURED" in review["coverage_rule"]
    assert "REALISTIC_VALIDATION_OR_EXPLICIT_UNVERIFIED" in review["completion_rule"]


def test_controller_review_is_projected_into_native_hot_path():
    session = read_json("config/SESSION_INTERACTION_POLICY.json")
    profile = read_json("config/NATIVE_SESSION_RUNTIME_PROFILE.json")
    compiled = build_native_session_runtime_profile(
        session_policy=session,
        deliberation_policy=read_json("config/DELIBERATION_POLICY.json"),
        host_profiles=read_json("config/HOST_PROFILES.json"),
    )
    assert compiled == profile
    review = profile["turn_contract"]["controller_inheritance_review"]
    assert review["required"]
    assert review["trigger"] == session["controller_inheritance_review"]["trigger"]
    assert review["coverage_rule"] == session["controller_inheritance_review"]["coverage_rule"]
    assert len((ROOT / "config/NATIVE_SESSION_RUNTIME_PROFILE.json").read_text(encoding="utf-8")) <= 12000
    assert "cannot physically force" in session["controller_inheritance_review"]["host_boundary"]


def test_review_reuses_exactly_one_existing_controller_task_authority():
    index = read_json("state/TASK_INDEX.json")
    controller = [task for task in index["controller_tasks"] if task["default_resume"]]
    assert len(controller) == 1
    task = controller[0]
    assert task["task_id"] == "uaos:maintenance:inheritance-review-20261018"
    assert task["resume_eligible"] and task["status"] == "RUNNING"
    assert (ROOT / task["state_ref"]).exists()


def test_domain_work_plane_remains_direct_and_unproxied():
    session = read_json("config/SESSION_INTERACTION_POLICY.json")
    selection = session["bare_inheritance_selector"]["controller_option"]
    assert selection["authority_context"] == "UAOS"
    rules = session["domain_session_activation"]["rules"]
    assert any("directly" in rule for rule in rules)
    review = session["controller_inheritance_review"]
    assert "DO_NOT_PROXY_ORDINARY_CHILD_WORK" in review["scope"]
