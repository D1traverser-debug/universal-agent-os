import json
from pathlib import Path

from uaos.kernel import DeliberationSignals, assess_deliberation

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _assert_problem_floor(signals: DeliberationSignals):
    directive = assess_deliberation(signals)
    assert directive.required
    assert directive.micro_diagnosis_required
    assert directive.macro_alignment_required
    assert directive.governing_assumptions_challenge_required
    assert directive.external_research_required


def test_every_detected_problem_requires_research_and_reflection_floor():
    cases = [
        DeliberationSignals(user_correction=True),
        DeliberationSignals(repeated_failure_count=1),
        DeliberationSignals(goal_progress_uncertain=True),
        DeliberationSignals(complexity_increasing=True),
        DeliberationSignals(conflicting_evidence=True),
        DeliberationSignals(unknown_failure_class=True),
        DeliberationSignals(knowledge_gap=True),
        DeliberationSignals(architecture_gap=True),
    ]
    for signals in cases:
        _assert_problem_floor(signals)


def test_problem_free_normal_work_does_not_force_research_ritual():
    directive = assess_deliberation(DeliberationSignals())
    assert not directive.required
    assert not directive.external_research_required


def test_v17_is_current_requirement_and_policy_disallows_familiarity_waiver():
    current = _json("CURRENT_SYSTEM.json")
    assert "docs/requirements/FROZEN_REQUIREMENTS_v1.7.md" in current["requirements"]

    policy = _json("config/DELIBERATION_POLICY.json")
    floor = policy["problem_detection_floor"]
    assert floor["always_required_dimensions"] == [
        "MICRO_DIAGNOSIS",
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT",
        "GOVERNING_ASSUMPTION_CHALLENGE",
        "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH",
    ]
    assert "NO_RESEARCH_OR_REFLECTION_WAIVER_FOR_FAMILIARITY" in floor["depth_rule"]
