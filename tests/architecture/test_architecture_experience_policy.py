import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def test_system_map_registers_architecture_experience_policy():
    system_map = load_json("config/SYSTEM_MAP.json")
    assert _version_tuple(system_map["schema_version"]) >= (1, 9)
    assert system_map["controller"]["architecture_experience_policy"] == "config/ARCHITECTURE_EXPERIENCE_POLICY.json"
    assert system_map["controller"]["domain_health_escalation_policy"] == "config/DOMAIN_HEALTH_ESCALATION_POLICY.json"


def test_policy_rejects_literalizing_user_examples_and_requires_dogfood():
    policy = load_json("config/ARCHITECTURE_EXPERIENCE_POLICY.json")
    assert _version_tuple(policy["policy_version"]) >= (1, 1, 0)
    assert "USER_EXAMPLES_ARE_EVIDENCE_OR_CANDIDATE_HINTS_UNLESS_EXPLICITLY_STATED_AS_REQUIREMENTS" in policy["principles"]
    assert "CURRENT_AGENT_DOGFOODING_IS_REQUIRED_FOR_MATERIAL_CONTROL_PLANE_OR_AGENT_EXPERIENCE_CHANGES" in policy["principles"]
    assert "MATERIAL_CONTROL_PLANE_OR_AGENT_EXPERIENCE_CHANGES_REQUIRE_BOUNDED_COMPETING_ARCHITECTURE_CANDIDATES_AND_AN_EXPLICIT_NO_CHANGE_BASELINE" in policy["principles"]
    assert policy["executable_ref"] == "src/uaos/kernel/architecture_experience.py"
    assert "Do not require every representation family" in policy["view_selection_rule"]
    assert policy["candidate_comparison"]["minimum_candidates"] == 2
    assert policy["candidate_comparison"]["no_change_baseline_required"] is True


def test_deliberation_policy_makes_experience_evaluation_part_of_material_architecture_admission():
    deliberation = load_json("config/DELIBERATION_POLICY.json")
    assert tuple(map(int, deliberation["policy_version"].split("."))) >= (2, 0, 0)
    admission = deliberation["architecture_experience_admission"]
    assert admission["policy_ref"] == "config/ARCHITECTURE_EXPERIENCE_POLICY.json"
    assert admission["executable_ref"] == "src/uaos/kernel/architecture_experience.py"
    assert "CURRENT_AGENT_DOGFOOD_REQUIRED" in admission["dogfood_rule"]
    before = "\n".join(deliberation["material_change_admission"]["before_mutation"])
    assert "config/ARCHITECTURE_EXPERIENCE_POLICY.json" in before
    assert "current-agent dogfood" in before.lower()
    assert "causal/intervention admission" in before.lower()
    assert "bounded search requirements" in before.lower()


def test_repo_instructions_require_concern_driven_walkthrough_before_architecture_promotion():
    instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "## Architecture experience evaluation" in instructions
    assert "A user example, analogy, observation or hypothesis is evidence/candidate input" in instructions
    assert "CURRENT_AGENT dogfood walkthrough" in instructions
    assert "Choose representations by concern" in instructions
    assert "green unit test cannot by itself prove the architecture is suitable in use" in instructions


def test_method_complements_structure_instead_of_replacing_it_with_sequence():
    method = (ROOT / "docs/architecture/ARCHITECTURE_EXPERIENCE_EVALUATION.md").read_text(encoding="utf-8")
    assert "complements, rather than replaces, the structural blueprint" in method
    assert "These are concerns, not mandatory diagram types" in method
    assert "Do not force all views on all changes" in method
    assert "Do not claim a static view proves a temporal property or that a sequence proves ownership boundaries" in method
