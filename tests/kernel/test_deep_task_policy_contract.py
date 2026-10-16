import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_deep_task_profile_is_owned_by_canonical_deliberation_not_a_second_state_machine():
    deliberation = load("config/DELIBERATION_POLICY.json")
    profile = load("config/DEEP_TASK_EXECUTION_PROFILE.json")
    system_map = load("config/SYSTEM_MAP.json")

    deep = deliberation["deep_task_execution_profile"]
    assert profile["owner_policy"] == "config/DELIBERATION_POLICY.json"
    assert deep["profile_ref"] == "config/DEEP_TASK_EXECUTION_PROFILE.json"
    assert deep["relationship_to_cognition_kernel"] == "EVIDENCE_ADMISSION_PROFILE_ONLY__NO_SECOND_ORDERED_COGNITION_STATE_MACHINE"
    assert system_map["controller"]["deep_task_execution_profile"] == "config/DEEP_TASK_EXECUTION_PROFILE.json"
    assert profile["executable_trigger"] == "src/uaos/kernel/deep_task.py#assess_deep_task_requirement"
    assert profile["executable_admission"] == "src/uaos/kernel/deep_task.py#require_deep_task_admission"
    assert profile["controlled_finalization"] == "src/uaos/runtime/finalization.py#admit_final_response"


def test_profile_covers_all_user_requested_depth_dimensions():
    profile = load("config/DEEP_TASK_EXECUTION_PROFILE.json")
    ids = {item["id"] for item in profile["depth_dimensions"]}
    assert ids == {
        "A_GOVERNING_OUTCOME",
        "B_PROFESSIONAL_PRACTICE_GAP",
        "C_PRIMARY_OR_RAW_MATERIAL",
        "D_METHODS_AND_TOOLS",
        "E_UNKNOWN_DISCOVERY",
        "F_COMPETING_ALTERNATIVES_AND_FALSIFICATION",
        "G_STRETCH_WITH_FEASIBILITY",
        "H_INDEPENDENT_JUDGE_AND_VALIDATION",
    }
    activation = " ".join(profile["activation"]["required_when"]).lower()
    assert "explicitly asks for a deeper" in activation
    assert "deeptasksignals" in profile["activation"]["semantic_signal_contract"].lower()
    assert "without language-specific keyword matching" in profile["activation"]["semantic_signal_contract"].lower()
    principles = " ".join(profile["execution_principles"]).lower()
    assert "not by answer length" in principles
    assert "second cognition state machine" in principles


def test_common_capability_inherits_profile_without_bumping_contract_or_copying_algorithm():
    common = load("config/COMMON_CAPABILITIES.json")
    assert common["contract_version"] == "1.7.0"
    capabilities = {item["capability_id"]: item for item in common["capabilities"]}
    adaptive = capabilities["adaptive_deliberation_and_parent_guidance"]
    assert adaptive["policy_ref"] == "config/DELIBERATION_POLICY.json"
    assert adaptive["deep_task_profile_ref"] == "config/DEEP_TASK_EXECUTION_PROFILE.json"
    rules = " ".join(adaptive["rules"]).lower()
    assert "deeper rather than larger" in rules
    assert "second cognition state machine" in rules
