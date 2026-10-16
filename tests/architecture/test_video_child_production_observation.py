import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_parent_video_observation_is_cache_only_and_current_system_has_no_child_snapshot_copy():
    current = load("CURRENT_SYSTEM.json")
    health = load("state/DOMAIN_HEALTH_INDEX.json")

    assert current["child_observation"]["source"] == "state/DOMAIN_HEALTH_INDEX.json"
    assert current["child_observation"]["freshness_rule"].startswith("CURRENT_CHILD_AUTHORITY_ALWAYS_WINS")
    assert "video_binding_assurance" not in current
    assert "video_child_production_verification" not in current

    observed = health["domains"]["video"]
    assert observed["repository"] == "D1traverser-debug/video-growth-agent"
    assert observed["observed_release"] == "0.8.0"
    assert observed["observed_profile_version"] >= 10
    assert observed["common_behavior_assurance_min"] == "1.3.0"
    assert observed["canonical_evolution_entrypoint"] == "audits/EVOLUTION_INDEX.json"


def test_parent_keeps_one_video_router_and_does_not_mirror_child_business_state():
    index = load("state/TASK_INDEX.json")
    task = load("state/tasks/video-main.json")
    current = load("CURRENT_SYSTEM.json")

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

    serialized_task = json.dumps(task, ensure_ascii=False)
    serialized_current = json.dumps(current, ensure_ascii=False)
    for text in (serialized_task, serialized_current):
        assert "H1_SCULPTURAL_MASSING_V2" not in text
        assert "pilot-002" not in text.lower()
