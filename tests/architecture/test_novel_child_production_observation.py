from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_parent_observes_novel_profile5_learning_to_planning_production():
    system = load_json("CURRENT_SYSTEM.json")
    assert tuple(map(int, system["schema_version"].split("."))) >= (2, 26)
    assert system["system_release_version"] == "2.5.2"
    assert "NOVEL_PROFILE_5_PRODUCTION_VERIFIED" in system["novel_binding_assurance"]
    assert "ACTIVE_RULEBOOK_2_5" in system["novel_binding_assurance"]
    assert "MASTERWORK_PROTOCOL_2_1" in system["novel_binding_assurance"]
    assert "CLAIM_CONDITIONED_MULTIDIMENSIONAL_LEARNING" in system["novel_binding_assurance"]
    assert "ZERO_BASED_STORY_RESELECTION" in system["novel_binding_assurance"]
    assert "DYNAMIC_HIERARCHICAL_OUTLINE" in system["novel_binding_assurance"]
    assert "CALIBRATED_UNCERTAINTY_AWARE_VECTOR_EVALUATION" in system["novel_binding_assurance"]
    assert "LIVE_POST_RESELECTION_LITERARY_OUTCOME_OPEN" in system["novel_binding_assurance"]
    assert "NOVEL_PROFILE_4_PRODUCTION_VERIFIED" not in system["novel_binding_assurance"]


def test_parent_novel_receipt_binds_verified_child_events_without_claiming_live_outcome():
    system = load_json("CURRENT_SYSTEM.json")
    receipt = system["novel_child_production_verification"]
    assert receipt["profile_version"] == 5
    assert receipt["active_rulebook_version"] == "2.5-github"
    assert receipt["masterwork_protocol_version"] == "2.1"
    assert receipt["product_architecture_version"] == "1.0"
    assert receipt["common_behavior_assurance_min"] == "1.2.0"
    assert receipt["architecture_main_commit"] == "e0ec355f476830f77033ada08912d6c58f0bafe4"
    assert receipt["architecture_production_ci_run"] == 38706383327
    assert receipt["architecture_production_ci_number"] == 306
    assert receipt["final_main_commit"] == "77bcd48580be186588de2823dd2727a45dcf4251"
    assert receipt["final_main_production_ci_run"] == 38707051516
    assert receipt["final_main_production_ci_number"] == 309
    assert receipt["result"] == "PASS"
    assurance = receipt["assurance"]
    assert assurance.startswith("EXECUTABLE_LEARNING_TO_PLANNING_ARCHITECTURE_AND_TRAJECTORY_VERIFIED")
    assert "COMMON_BEHAVIOR_1_3_ROOT_SCOPE_ADOPTION_NOT_YET_OWNER_NATIVE_VERIFIED" in assurance
    assert assurance.endswith("LIVE_POST_RESELECTION_LITERARY_OUTCOME_OPEN")
    assert "NEXT_LINE_3914" in receipt["business_cursor_preserved"]
    assert "HISTORICAL_FQ001_NO_INCUMBENT_PRIVILEGE" in receipt["business_cursor_preserved"]


def test_parent_observation_does_not_mirror_child_canon_or_learning_payloads():
    system = load_json("CURRENT_SYSTEM.json")
    receipt = system["novel_child_production_verification"]
    forbidden = {
        "canon",
        "characters",
        "threads",
        "foreshadow",
        "timeline",
        "masterwork_ledger",
        "mechanism_registry",
        "story_candidates",
        "dynamic_outline",
        "chapter_contracts",
    }
    assert forbidden.isdisjoint(receipt)

    task = load_json("state/tasks/FQ001_MINGRI_ORDER.json")
    assert task["project_business_authority"] == "D1traverser-debug/novel-writing-agent@main:projects/FQ001_MINGRI_ORDER/checkpoints/CURRENT_CHECKPOINT.json"
    assert task["project_business_state_is_controller"] is False
    assert task["progress_timestamp_semantics"] == "UAOS_TASK_STATE_NORMALIZED_ONLY__BUSINESS_CHECKPOINT_MUST_BE_REREAD_BEFORE_RESUME"
