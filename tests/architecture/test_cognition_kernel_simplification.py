import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_deliberation_policy_is_the_single_cognition_stage_authority():
    policy = _json("config/DELIBERATION_POLICY.json")
    kernel = policy["cognition_kernel"]
    assert kernel["canonical"] is True
    assert kernel["hot_path"] == [
        "FRAME_AS_HYPOTHESIS",
        "EXPAND_PROBLEM_SPACE_WHEN_NEEDED",
        "FALSIFY_COMPETING_FRAMES",
        "COMMIT_ROOT_SCOPE_AND_LEARNING_DISPOSITION",
        "ACT_AND_VERIFY",
    ]
    assert "second" in kernel["anti_bloat"].lower() or "other policies" in kernel["anti_bloat"].lower()


def test_session_and_common_behavior_reference_kernel_instead_of_copying_stage_machine():
    session = _json("config/SESSION_INTERACTION_POLICY.json")
    common = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")

    session_tx = session["problem_cognition_action_transaction"]
    common_tx = common["problem_cognition_action_transaction"]

    assert session_tx["canonical_cognition_policy_ref"] == "config/DELIBERATION_POLICY.json#cognition_kernel"
    assert common_tx["canonical_cognition_policy_ref"] == "config/DELIBERATION_POLICY.json#cognition_kernel"
    assert "ordered_stages" not in session_tx
    assert "rules" not in session_tx
    assert "ordered_stages" not in common_tx
    assert "rules" not in common_tx
    assert common["contract_version"] == "1.3.0"


def test_bootstrap_hot_path_exposes_only_the_canonical_five_primitives():
    entrypoint = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    stages = (
        "FRAME_AS_HYPOTHESIS",
        "EXPAND_PROBLEM_SPACE_WHEN_NEEDED",
        "FALSIFY_COMPETING_FRAMES",
        "COMMIT_ROOT_SCOPE_AND_LEARNING_DISPOSITION",
        "ACT_AND_VERIFY",
    )
    for stage in stages:
        assert stage in entrypoint
        assert stage in agents
    assert "single cognition-stage authority" in entrypoint.lower()
    assert "only cognition-stage authority" in agents.lower()


def test_outside_in_discovery_is_conditional_not_a_per_turn_ritual():
    policy = _json("config/DELIBERATION_POLICY.json")
    discovery = policy["outside_in_capability_discovery"]
    assert "BROAD_EXTERNAL_CAPABILITY_LEARNING" in discovery["trigger"]
    assert "KNOWN_NEED" in discovery["known_need_exception"]
    assert discovery["executable_ref"] == "src/uaos/kernel/problem_space.py"
    assert "at least two distinct outside-in lenses" in discovery["broad_discovery_floor"]
    assert "not an instruction to create a matching Agent" in discovery["nonliteral_rule"]
