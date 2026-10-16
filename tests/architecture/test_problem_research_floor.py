import json
from pathlib import Path

from uaos.kernel import CognitiveSearchMode, DeliberationSignals, assess_deliberation

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_oneoff_local_failure_keeps_cognition_but_does_not_force_external_research():
    directive = assess_deliberation(DeliberationSignals(repeated_failure_count=1))
    assert directive.required
    assert directive.micro_diagnosis_required
    assert directive.macro_alignment_required
    assert directive.governing_assumptions_challenge_required
    assert not directive.external_research_required
    assert directive.search_mode is CognitiveSearchMode.LIGHTWEIGHT


def test_user_correction_forces_contrastive_search_not_automatic_web_research():
    directive = assess_deliberation(DeliberationSignals(user_correction=True))
    assert directive.search_mode is CognitiveSearchMode.CONTRASTIVE
    assert directive.min_hypotheses == 2
    assert directive.min_action_candidates == 2
    assert directive.counterexample_search_required
    assert not directive.external_research_required


def test_systemic_unknown_and_knowledge_gap_require_structured_research():
    cases = [
        DeliberationSignals(repeated_failure_count=2),
        DeliberationSignals(conflicting_evidence=True),
        DeliberationSignals(unknown_failure_class=True),
        DeliberationSignals(knowledge_gap=True),
        DeliberationSignals(architecture_gap=True),
        DeliberationSignals(material_problem=True),
    ]
    for signals in cases:
        directive = assess_deliberation(signals)
        assert directive.search_mode is CognitiveSearchMode.STRUCTURED
        assert directive.external_research_required
        assert directive.min_action_candidates == 3
        assert directive.no_change_baseline_required
        assert directive.max_deliberation_rounds == 3


def test_problem_free_normal_work_does_not_force_research_ritual():
    directive = assess_deliberation(DeliberationSignals())
    assert not directive.required
    assert not directive.external_research_required


def test_policy_matches_frozen_compact_small_problem_semantics():
    current = _json("CURRENT_SYSTEM.json")
    assert "docs/requirements/FROZEN_REQUIREMENTS_v2.2.md" in current["requirements"]

    policy = _json("config/DELIBERATION_POLICY.json")
    floor = policy["problem_detection_floor"]
    assert floor["always_required_dimensions"] == [
        "MICRO_DIAGNOSIS",
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT",
        "GOVERNING_ASSUMPTION_CHALLENGE",
    ]
    assert "NO_CEREMONIAL_RESEARCH" in floor["depth_rule"]
    assert policy["cognitive_search_modes"]["LIGHTWEIGHT"]["external_research"] == "NOT_MANDATORY_UNLESS_CURRENT_KNOWLEDGE_IS_INSUFFICIENT"
