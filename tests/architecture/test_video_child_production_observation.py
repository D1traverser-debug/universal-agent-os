import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_parent_observes_video_0_7_without_regressing_to_0_6():
    current = load("CURRENT_SYSTEM.json")

    assert current["system_release_version"] == "2.5.2"
    assert "VIDEO_0_7_0_PRODUCTION_VERIFIED" in current["video_binding_assurance"]
    assert "VIDEO_0_6_0" not in current["video_binding_assurance"]
    assert "VIDEO_0_7_0" in current["domain_internal_orchestration_assurance"]
    assert "VIDEO_0_6_0" not in current["domain_internal_orchestration_assurance"]
    assert "VIDEO_0_7_0_MEDIA_BUSINESS_OS_PRODUCTION_VERIFIED" in current["parent_core_assurance"]

    observed = current["video_child_production_verification"]
    assert observed["release"] == "0.7.0"
    assert observed["profile_version"] == 8
    assert observed["common_capabilities_contract_min"] == "1.6.0"
    assert observed["common_behavior_assurance_min"] == "1.2.0"
    assert observed["release_main_commit"] == "ad51bb76188eb0184cf8434384109c5c1257a60c"
    assert observed["release_production_ci_run"] == 38690550495
    assert observed["final_main_commit"] == "55f605e641671a513637ffb03b532c66335a2ad9"
    assert observed["final_main_production_ci_run"] == 38691615525
    assert observed["result"] == "PASS"
    assert "LIVE_EPISODE_GROWTH_IP_COMMERCIAL_OUTCOME_OBSERVATION_OPEN" in observed["assurance"]
    assert "H1_SCULPTURAL_MASSING_V2" in observed["business_cursor_preserved"]
    assert "A2_POSITIVE_MORPH_NEXT" in observed["business_cursor_preserved"]
    assert "PILOT_002_REJECTION_AND_PROCESS_INVALID_EVIDENCE_PRESERVED" in observed["business_cursor_preserved"]


def test_parent_keeps_one_video_router_and_does_not_mirror_child_business_state():
    index = load("state/TASK_INDEX.json")
    task = load("state/tasks/video-main.json")

    video_tasks = [item for item in index["tasks"] if item.get("domain_id") == "video"]
    assert len(video_tasks) == 1
    assert video_tasks[0]["task_id"] == "video:main"
    assert video_tasks[0]["task_type"] == "domain_project_router"
    assert video_tasks[0]["state_ref"] == "state/tasks/video-main.json"
    assert "Video domain router only" in video_tasks[0]["semantic_summary"]

    assert task["task_id"] == "video:main"
    assert task["active_domain_state_ref"] is None
    assert task["domain_business_state_is_controller"] is False
    assert task["domain_reference_semantics"].startswith("OPAQUE_REFERENCE")
    assert "NO_EQUALITY_REQUIREMENT" in task["identity_boundary"]
    assert "NO_PARENT_BUSINESS_PROJECT_SELECTION" in task["generic_resolution_rule"]
    assert "REREAD_CURRENT_VIDEO_DOMAIN_BINDING_BEFORE_DELEGATION" in task["freshness_rule"]

    serialized = json.dumps(task, ensure_ascii=False)
    assert "H1_SCULPTURAL_MASSING_V2" not in serialized
    assert "pilot-002" not in serialized.lower()
    assert "0.7.0" not in serialized
