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
    assert review["evidence_admission_ref"] == session["controller_inheritance_review"]["evidence_admission_ref"]
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



def test_review_source_inventory_tracks_all_registered_domains_not_fixed_names():
    registry = read_json("config/AGENT_REGISTRY.json")
    actual = read_json("state/observations/uaos-controller-five-repo-review-20261018.json")
    expected = {"universal-agent-os"} | {
        agent["repository"].split("/")[-1] for agent in registry["agents"]
    }
    recorded = {entry["repo"] for entry in actual["source_heads"]}
    assert recorded == expected

    required = set(actual["dimensions"]) if "dimensions" in actual else {
        "authority_architecture", "requirement_continuity", "execution_admission",
        "quality_validation", "observability", "evolution_learning",
    }
    assert len(required) == 6
    for repository in recorded:
        observations = {
            cell["dimension"] for cell in actual["coverage"]
            if cell["repo"] == repository and cell["source"]
        }
        assert observations == required


def test_source_inventory_does_not_claim_unverified_deep_or_native_outcomes():
    actual = read_json("state/observations/uaos-controller-five-repo-review-20261018.json")
    assert actual["status"] == "SOURCE_PROBES_PARTIAL__DEEP_AUDIT_INCOMPLETE"
    assert actual["counts"]["deep_validated_dimensions"] == 0
    assert actual["counts"]["native_cross_session_trigger_verification"] == 0
    assert actual["outcome"].startswith("NOT_GREEN")
    assert all(
        cell["assurance"] == "SOURCE_IDENTIFIED__NOT_RUNTIME_VERIFIED"
        for cell in actual["coverage"]
    )
