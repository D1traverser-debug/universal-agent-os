import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_deep_task_profile_points_to_existing_problem_space_acquisition_owner():
    profile = load("config/DEEP_TASK_EXECUTION_PROFILE.json")
    system_map = load("config/SYSTEM_MAP.json")
    assert profile["knowledge_acquisition_admission"] == "src/uaos/kernel/problem_space.py#require_knowledge_acquisition_admission"
    assert system_map["controller"]["knowledge_acquisition_admission"] == profile["knowledge_acquisition_admission"]
    assert "literal claim" in profile["coverage_oriented_knowledge_acquisition"]["non_exhaustiveness_rule"]
    assert "narrow factual lookup" in profile["coverage_oriented_knowledge_acquisition"]["narrow_lookup_rule"]


def test_comprehensive_learning_is_an_internal_escalation_not_a_session_entry_precondition():
    session = load("config/SESSION_INTERACTION_POLICY.json")
    entry = session["mandatory_selected_context_entry"]
    depth = session["always_on_execution_depth_sentinel"]
    assert entry["required"] is True
    assert "INTERNAL ROUTING SIGNALS" in entry["anti_circularity"]
    assert "comprehensive_knowledge_acquisition_required" in " ".join(depth["checks"])
    assert "not prerequisites for entering this sentinel" in entry["anti_circularity"]
