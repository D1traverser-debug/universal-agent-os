import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_video_domain_has_exactly_one_parent_router():
    index = _load("state/TASK_INDEX.json")
    video_tasks = [item for item in index["tasks"] if item.get("domain_id") == "video"]

    assert len(video_tasks) == 1
    router = video_tasks[0]
    assert router["task_id"] == "video:main"
    assert router["task_type"] == "domain_project_router"
    assert router["state_model"] == "UAOS_NATIVE"
    assert router["state_ref"] == "state/tasks/video-main.json"
    assert router["default_resume_within_domain"] is True


def test_video_router_does_not_mirror_child_business_state():
    router = _load("state/tasks/video-main.json")

    assert router["domain_id"] == "video"
    assert router["active_domain_state_ref"] is None
    assert router["domain_business_state_is_controller"] is False
    assert "NO_EQUALITY_REQUIREMENT" in router["identity_boundary"]
    assert "CHILD_PROJECT" in router["historical_resume_rule"]

    serialized = json.dumps(router, ensure_ascii=False)
    for child_business_marker in (
        "H1_SCULPTURAL_MASSING",
        "VISUAL_PREVIEW_PROCESS_REENTRY",
        "pilot-002",
        "sample_v2",
        "A2_positive_morph",
    ):
        assert child_business_marker not in serialized


def test_retired_parent_video_business_mirrors_stay_absent():
    assert not (ROOT / "state/tasks/video-ai-self-media-commercialization.json").exists()
    assert not (ROOT / "state/tasks/video-growth-main.json").exists()


def test_legacy_video_aliases_route_to_router_without_identity_adoption():
    index = _load("state/TASK_INDEX.json")
    router = next(item for item in index["tasks"] if item.get("domain_id") == "video")
    aliases = set(router["aliases"])

    assert {
        "video:ai-self-media-commercialization",
        "video-growth:main",
        "Pilot 002",
        "AI自媒体视频商业化与原创数字IP",
        "原创数字IP设计",
    } <= aliases
    assert "child project" in router["semantic_summary"].lower()
    assert "opaque child reference" in router["semantic_summary"].lower()
