import pytest

from uaos.kernel import (
    DeepTaskAlternative,
    DeepTaskAlternativeDisposition,
    DeepTaskCase,
    EvidenceItem,
    EvidenceKind,
)
from uaos.runtime import FinalizationBlocked, FinalizationContext, admit_final_response


def _report() -> str:
    return """Completed.

当前 Agent：UAOS
当前范围或任务：deep-task finalization test
Authority：UAOS
状态：DONE
当前阶段：FINALIZATION
下一动作或阻塞：none
Evolution：NO_EVOLUTION_TRIGGER
Deliberation：NOT_TRIGGERED
版本：UAOS test
进度时间：2026-10-16 22:55:00（北京时间）
"""


def _case() -> DeepTaskCase:
    items = (
        EvidenceItem("practice", EvidenceKind.EXTERNAL_SOURCE, "Independent TEVV is professional practice.", "https://airc.nist.gov/airmf-resources/airmf/5-sec-core/"),
        EvidenceItem("raw", EvidenceKind.REPOSITORY_FACT, "Original runtime code inspected.", "repo://runtime"),
        EvidenceItem("method", EvidenceKind.EXTERNAL_SOURCE, "ATAM scenario analysis used.", "https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/", method_ref="ATAM"),
        EvidenceItem("unknown", EvidenceKind.TOOL_RESULT, "Unknown-gap search completed.", "tool://search", method_ref="gap search"),
        EvidenceItem("a", EvidenceKind.ANALYSIS_RESULT, "Extend existing cognition.", "analysis://a"),
        EvidenceItem("b", EvidenceKind.ANALYSIS_RESULT, "Create new cognition state machine.", "analysis://b"),
        EvidenceItem("fa", EvidenceKind.TEST_RESULT, "Existing cognition can host the profile.", "test://fa", method_ref="contract test"),
        EvidenceItem("fb", EvidenceKind.TEST_RESULT, "New state machine duplicates authority.", "test://fb", method_ref="negative architecture test"),
        EvidenceItem("judge", EvidenceKind.TEST_RESULT, "Admission test passed.", "test://judge", method_ref="pytest"),
        EvidenceItem("holdout", EvidenceKind.SCENARIO_RESULT, "Held-out deep request passed.", "scenario://holdout", method_ref="scenario replay"),
    )
    return DeepTaskCase(
        case_id="deep-runtime",
        governing_outcome="Deepen evidence and validation without enlarging the task unnecessarily.",
        evidence_items=items,
        professional_practice_evidence_ids=("practice",),
        raw_material_evidence_ids=("raw",),
        method_tool_evidence_ids=("method",),
        unknown_discovery_evidence_ids=("unknown",),
        alternatives=(
            DeepTaskAlternative("a", "Extend current cognition.", DeepTaskAlternativeDisposition.PREFERRED, ("a",), "Reject if current cognition cannot host the evidence profile.", ("fa",)),
            DeepTaskAlternative("b", "Create a new state machine.", DeepTaskAlternativeDisposition.REJECTED, ("b",), "Reject if it duplicates current cognition authority.", ("fb",)),
        ),
        independent_judge_evidence_ids=("judge",),
        holdout_replay_or_production_evidence_ids=("holdout",),
        acceptance_criteria=("controlled finalization blocks missing deep evidence",),
    )


def test_explicit_deep_task_cannot_finalize_without_evidence_case():
    with pytest.raises(FinalizationBlocked) as exc:
        admit_final_response(
            _report(),
            FinalizationContext(context_selected=True, deep_task_required=True),
        )
    assert "MISSING_DEEP_TASK_EVIDENCE_CASE" in exc.value.reasons


def test_explicit_deep_task_finalizes_after_evidence_admission():
    receipt = admit_final_response(
        _report(),
        FinalizationContext(
            context_selected=True,
            deep_task_required=True,
            deep_task_case=_case(),
        ),
    )
    assert receipt.deep_task_receipt is not None
    assert receipt.deep_task_receipt.preferred_alternative_id == "a"


def test_deep_task_case_cannot_be_smuggled_into_a_non_deep_turn():
    with pytest.raises(FinalizationBlocked) as exc:
        admit_final_response(
            _report(),
            FinalizationContext(
                context_selected=True,
                deep_task_case=_case(),
            ),
        )
    assert "UNEXPECTED_DEEP_TASK_CASE_WITHOUT_DEEP_TASK_REQUIREMENT" in exc.value.reasons
