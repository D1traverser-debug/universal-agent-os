from uaos.kernel import (
    AcquisitionMethod,
    AcquisitionProbe,
    DeepTaskAlternative,
    DeepTaskAlternativeDisposition,
    DeepTaskCase,
    DeepTaskSignals,
    EvidenceItem,
    EvidenceKind,
    KnowledgeAcquisitionAssessment,
    KnowledgeSource,
    KnowledgeSourceRole,
    MethodFamily,
    SaturationRound,
    assess_deep_task_requirement,
    require_deep_task_admission,
)


def _assessment() -> KnowledgeAcquisitionAssessment:
    return KnowledgeAcquisitionAssessment(
        acquisition_id="knowledge:deep",
        objective="Learn competing instruction-design methods comprehensively before selecting one.",
        knowledge_modules=("skill-metadata", "instruction-language"),
        required_source_roles=(
            KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY,
            KnowledgeSourceRole.INDEPENDENT_RESEARCH_OR_BENCHMARK,
        ),
        sources=(
            KnowledgeSource("primary", "authority://official", KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY, ("raw",)),
            KnowledgeSource("research", "research://benchmark", KnowledgeSourceRole.INDEPENDENT_RESEARCH_OR_BENCHMARK, ("practice",)),
        ),
        probes=(
            AcquisitionProbe("seed", AcquisitionMethod.DIRECT_SEARCH, "skill guidance", "Found the primary guidance.", ("raw",)),
            AcquisitionProbe("expand", AcquisitionMethod.QUERY_EXPANSION, "instruction salience benchmark", "Found independent counterevidence.", ("practice",)),
        ),
        method_families=(
            MethodFamily("principles", "Principle-first contextual guidance.", ("practice",)),
            MethodFamily("gates", "Hard deterministic gates for fragile operations.", ("raw",)),
        ),
        contradictions=(),
        saturation_rounds=(
            SaturationRound("sat-1", (AcquisitionMethod.BACKWARD_REFERENCE,), (), (), (), False, ("practice",)),
            SaturationRound("sat-2", (AcquisitionMethod.QUERY_EXPANSION,), (), (), (), False, ("raw",)),
        ),
        stop_reason="Required source roles were covered and two terminal expansion rounds found no material new family.",
        holdout_or_validation_plan="Test on unseen trigger/non-trigger and research-depth prompts.",
    )


def _case() -> DeepTaskCase:
    items = (
        EvidenceItem("practice", EvidenceKind.EXTERNAL_SOURCE, "Independent benchmark and professional evidence.", "research://benchmark"),
        EvidenceItem("raw", EvidenceKind.REPOSITORY_FACT, "Current authority and implementation were inspected.", "repo://current"),
        EvidenceItem("method", EvidenceKind.EXTERNAL_SOURCE, "Systematic search method used.", "method://search", method_ref="coverage-oriented search"),
        EvidenceItem("unknown", EvidenceKind.TOOL_RESULT, "Unknown-method expansion completed.", "tool://search", method_ref="query expansion"),
        EvidenceItem("a", EvidenceKind.ANALYSIS_RESULT, "Extend current Deep Task.", "analysis://a"),
        EvidenceItem("b", EvidenceKind.ANALYSIS_RESULT, "Create a separate research OS.", "analysis://b"),
        EvidenceItem("fa", EvidenceKind.TEST_RESULT, "Existing owner can host acquisition evidence.", "test://fa", method_ref="contract test"),
        EvidenceItem("fb", EvidenceKind.TEST_RESULT, "Parallel research OS duplicates authority.", "test://fb", method_ref="architecture negative"),
        EvidenceItem("judge", EvidenceKind.TEST_RESULT, "Admission regression passes.", "test://judge", method_ref="pytest"),
        EvidenceItem("holdout", EvidenceKind.SCENARIO_RESULT, "Held-out comprehensive research task uses acquisition evidence.", "scenario://holdout", method_ref="holdout"),
    )
    return DeepTaskCase(
        case_id="deep:knowledge",
        governing_outcome="Learn enough of the external method space to choose a fitted UAOS intervention.",
        evidence_items=items,
        professional_practice_evidence_ids=("practice",),
        raw_material_evidence_ids=("raw",),
        method_tool_evidence_ids=("method",),
        unknown_discovery_evidence_ids=("unknown",),
        alternatives=(
            DeepTaskAlternative("extend", "Extend the existing evidence profile.", DeepTaskAlternativeDisposition.PREFERRED, ("a",), "Reject if current owners cannot host the trace.", ("fa",)),
            DeepTaskAlternative("parallel", "Create a separate research OS.", DeepTaskAlternativeDisposition.REJECTED, ("b",), "Reject if it duplicates current authority.", ("fb",)),
        ),
        independent_judge_evidence_ids=("judge",),
        holdout_replay_or_production_evidence_ids=("holdout",),
        acceptance_criteria=("comprehensive learning is coverage- and saturation-evidence backed",),
        knowledge_acquisition_assessment=_assessment(),
    )


def test_comprehensive_acquisition_signal_requires_deep_execution():
    requirement = assess_deep_task_requirement(
        DeepTaskSignals(comprehensive_knowledge_acquisition_required=True)
    )
    assert requirement.required
    assert "COMPREHENSIVE_KNOWLEDGE_ACQUISITION_REQUIRED" in requirement.reason_codes


def test_deep_task_receipt_carries_knowledge_acquisition_receipt():
    receipt = require_deep_task_admission(_case())
    assert receipt.knowledge_acquisition_receipt is not None
    assert receipt.knowledge_acquisition_receipt.acquisition_id == "knowledge:deep"
    assert "practice" in receipt.evidence_ids
