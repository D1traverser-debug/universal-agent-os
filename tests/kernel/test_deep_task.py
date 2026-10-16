import pytest

from uaos.kernel import (
    DeepTaskAdmissionError,
    DeepTaskAlternative,
    DeepTaskAlternativeDisposition,
    DeepTaskCase,
    EvidenceItem,
    EvidenceKind,
    require_deep_task_admission,
)


def _items():
    return (
        EvidenceItem("practice", EvidenceKind.EXTERNAL_SOURCE, "Top practitioners use explicit TEVV and independent assessment.", "https://airc.nist.gov/airmf-resources/airmf/5-sec-core/"),
        EvidenceItem("raw", EvidenceKind.REPOSITORY_FACT, "Raw runtime source and finalization path were inspected.", "repo://src/uaos/runtime/finalization.py"),
        EvidenceItem("method", EvidenceKind.EXTERNAL_SOURCE, "ATAM evaluates business drivers, scenarios, risks and tradeoffs.", "https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/", method_ref="SEI ATAM scenario/tradeoff analysis"),
        EvidenceItem("unknown", EvidenceKind.TOOL_RESULT, "Search found a missing deep-task admission path.", "tool://repository-search", method_ref="outside-in gap search"),
        EvidenceItem("alt-a", EvidenceKind.ANALYSIS_RESULT, "Extending existing deliberation avoids a second cognition owner.", "analysis://alt-a"),
        EvidenceItem("alt-b", EvidenceKind.ANALYSIS_RESULT, "A standalone state machine would duplicate cognition authority.", "analysis://alt-b"),
        EvidenceItem("falsify-a", EvidenceKind.TEST_RESULT, "A contract test verifies existing deliberation can host the profile.", "test://falsify-a", method_ref="contract test"),
        EvidenceItem("falsify-b", EvidenceKind.TEST_RESULT, "A regression rejects unbound deep-task completion.", "test://falsify-b", method_ref="negative regression"),
        EvidenceItem("judge", EvidenceKind.TEST_RESULT, "Independent deterministic admission test passed.", "test://judge", method_ref="pytest deep-task admission"),
        EvidenceItem("holdout", EvidenceKind.SCENARIO_RESULT, "A held-out explicit-depth scenario is admitted only with the full evidence bundle.", "scenario://holdout", method_ref="holdout scenario replay"),
        EvidenceItem("feasible", EvidenceKind.TOOL_RESULT, "Benchmark shows the bounded target is technically feasible.", "benchmark://feasibility", method_ref="benchmark"),
    )


def _case(**overrides):
    values = dict(
        case_id="deep-task:test",
        governing_outcome="Produce a deeper answer by improving evidence quality, not by increasing size.",
        evidence_items=_items(),
        professional_practice_evidence_ids=("practice",),
        raw_material_evidence_ids=("raw",),
        method_tool_evidence_ids=("method",),
        unknown_discovery_evidence_ids=("unknown",),
        alternatives=(
            DeepTaskAlternative(
                "extend-existing",
                "Extend the existing deliberation/finalization contract.",
                DeepTaskAlternativeDisposition.PREFERRED,
                ("alt-a",),
                "Reject if the existing cognition owner cannot express the required evidence trace.",
                ("falsify-a",),
            ),
            DeepTaskAlternative(
                "new-state-machine",
                "Create a separate deep-task cognition state machine.",
                DeepTaskAlternativeDisposition.REJECTED,
                ("alt-b",),
                "Reject if it duplicates existing cognition authority without a distinct execution need.",
                ("falsify-b",),
            ),
        ),
        independent_judge_evidence_ids=("judge",),
        holdout_replay_or_production_evidence_ids=("holdout",),
        acceptance_criteria=(
            "explicit deep tasks cannot finalize without the required evidence dimensions",
            "ordinary shallow tasks do not pay the deep-task evidence cost",
        ),
    )
    values.update(overrides)
    return DeepTaskCase(**values)


def test_deep_task_admits_evidence_depth_without_new_cognition_state_machine():
    receipt = require_deep_task_admission(_case())
    assert receipt.preferred_alternative_id == "extend-existing"
    assert "judge" in receipt.evidence_ids
    assert receipt.stretch_target_admitted is False


def test_professional_practice_cannot_be_same_model_claim_only():
    items = tuple(item for item in _items() if item.evidence_id != "practice") + (
        EvidenceItem("practice-analysis", EvidenceKind.ANALYSIS_RESULT, "I think experts would do this.", "analysis://self"),
    )
    with pytest.raises(DeepTaskAdmissionError, match="external source"):
        require_deep_task_admission(
            _case(evidence_items=items, professional_practice_evidence_ids=("practice-analysis",))
        )


def test_raw_material_cannot_be_only_digested_analysis():
    with pytest.raises(DeepTaskAdmissionError, match="raw-material evidence"):
        require_deep_task_admission(_case(raw_material_evidence_ids=("alt-a",)))


def test_method_tool_dimension_requires_named_method_ref():
    items = tuple(item for item in _items() if item.evidence_id != "method") + (
        EvidenceItem("method-unbound", EvidenceKind.EXTERNAL_SOURCE, "A method was mentioned.", "https://example.invalid/method"),
    )
    with pytest.raises(DeepTaskAdmissionError, match="method_ref"):
        require_deep_task_admission(
            _case(evidence_items=items, method_tool_evidence_ids=("method-unbound",))
        )


def test_independent_judge_cannot_be_same_model_analysis():
    with pytest.raises(DeepTaskAdmissionError, match="independent-judge"):
        require_deep_task_admission(_case(independent_judge_evidence_ids=("alt-a",)))


def test_stretch_target_requires_feasibility_evidence():
    with pytest.raises(ValueError, match="feasibility"):
        _case(stretch_target="10x quality at the same latency")
    receipt = require_deep_task_admission(
        _case(
            stretch_target="10x quality at the same latency",
            stretch_target_feasibility_evidence_ids=("feasible",),
        )
    )
    assert receipt.stretch_target_admitted is True


def test_each_competing_alternative_needs_real_falsification_evidence():
    bad = DeepTaskAlternative(
        "bad",
        "An alternative with fake falsification evidence.",
        DeepTaskAlternativeDisposition.PREFERRED,
        ("alt-a",),
        "Reject if contradicted.",
        ("practice",),
    )
    other = DeepTaskAlternative(
        "other",
        "Other alternative.",
        DeepTaskAlternativeDisposition.REJECTED,
        ("alt-b",),
        "Reject if contradicted.",
        ("falsify-b",),
    )
    with pytest.raises(DeepTaskAdmissionError, match="falsification"):
        require_deep_task_admission(_case(alternatives=(bad, other)))
