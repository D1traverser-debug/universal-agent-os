from uaos.kernel.problem_space import MethodTransferAssessment, MethodTransferDisposition
import pytest

from uaos.kernel import (
    ActionCandidate,
    ArchitectureCandidate,
    ArchitectureConcern,
    ArchitectureExperienceCase,
    ArchitectureScenario,
    CausalFactor,
    CausalFactorDisposition,
    CognitionCase,
    CognitionCaseAdmissionError,
    CognitiveSearchMode,
    DeliberationEvidence,
    DeliberationSignals,
    EngineeringTrace,
    EvidenceItem,
    EvidenceKind,
    InputSignal,
    ProblemLayer,
    Representation,
    SignalKind,
    WalkthroughStep,
    require_cognition_case_admission,
)


def _evidence_items():
    return (
        EvidenceItem("goal", EvidenceKind.USER_CLAIM, "User wants independent diagnosis that does not mirror the latest framing and does not stop at explanation when repair is authorized.", "conversation://goal"),
        EvidenceItem("micro", EvidenceKind.REPOSITORY_FACT, "Finalization currently consumes a precomputed root-scope receipt rather than the raw cognition assessment.", "repo://src/uaos/runtime/finalization.py"),
        EvidenceItem("single-root", EvidenceKind.REPOSITORY_FACT, "Legacy root-scope admission requires exactly one SELECTED hypothesis.", "repo://src/uaos/kernel/deliberation.py"),
        EvidenceItem("macro", EvidenceKind.ANALYSIS_RESULT, "The repeated failure spans framing, causal modeling, finalization evidence and host enforcement rather than one edit site.", "analysis://cross-layer"),
        EvidenceItem("assumption", EvidenceKind.ANALYSIS_RESULT, "More policy prose alone is insufficient because equivalent guidance already existed before the live failures.", "analysis://policy-vs-execution"),
        EvidenceItem("research", EvidenceKind.EXTERNAL_SOURCE, "Systems engineering and incident-analysis methods separate requirements, causal analysis, architecture tradeoffs, verification and validation.", "external://nasa-sei-sre-cast"),
        EvidenceItem("counter", EvidenceKind.TEST_RESULT, "Existing deterministic tests can pass with manually constructed RootScopeReceipt objects, so receipt presence does not prove evidence-to-decision derivation.", "test://finalization-receipt-construction"),
        EvidenceItem("independent", EvidenceKind.TOOL_RESULT, "Repository inspection independently confirmed the current caller-supplied receipt boundary.", "tool://github-reread"),
        EvidenceItem("arch", EvidenceKind.ANALYSIS_RESULT, "Whole-UAOS replacement would discard unrelated authority/continuity/health mechanisms that already have production evidence.", "analysis://architecture-scope"),
        EvidenceItem("trade-no-change", EvidenceKind.ANALYSIS_RESULT, "No change preserves compatibility but leaves the reproduced failure class open.", "tradeoff://no-change"),
        EvidenceItem("trade-receipt", EvidenceKind.ANALYSIS_RESULT, "Receipt-only hardening reduces self-attestation but preserves singular-root causal compression.", "tradeoff://receipt-only"),
        EvidenceItem("trade-transaction", EvidenceKind.ANALYSIS_RESULT, "Rebuilding the cognition transaction is broader than a receipt patch but bounded to the reproduced cognition/finalization seam.", "tradeoff://transaction"),
        EvidenceItem("user-rebuild", EvidenceKind.USER_CLAIM, "User explicitly allowed even a full rebuild.", "conversation://full-rebuild-option"),
        EvidenceItem("full-rebuild-probe", EvidenceKind.ANALYSIS_RESULT, "No evidence currently shows domain authority, continuity, registry or health topology must be replaced.", "analysis://full-rebuild-falsification"),
        EvidenceItem("scenario", EvidenceKind.SCENARIO_RESULT, "Replay preserves user statements as hypotheses while evidence selects the intervention.", "scenario://user-anchoring-replay"),
    )


def _architecture_experience():
    concerns = (
        ArchitectureConcern("operability", "The current Agent can execute evidence-first cognition without mirroring the latest user theory.", actor_operability_material=True),
        ArchitectureConcern("ordering", "Causal admission and intervention selection precede action and V&V.", temporal_behavior_material=True),
    )
    dogfood = ArchitectureScenario(
        "current-agent-replay",
        "CURRENT_AGENT_DOGFOOD",
        "Independently diagnose the repeated correction sequence and execute the bounded admitted intervention.",
        "UAOS selected after repeated user correction",
        (
            WalkthroughStep("frame", "CURRENT_AGENT", "preserve the user's upstream and rebuild statements as hypotheses", "user claim remains non-authoritative", "mirroring latest framing", "inspect typed current-system evidence"),
            WalkthroughStep("compare", "CURRENT_AGENT", "compare multi-layer causes and intervention candidates", "supported and rejected factors stay distinct", "single-root compression", "replay counterexample evidence"),
            WalkthroughStep("act", "CURRENT_AGENT", "execute only the admitted intervention and bind V&V", "terminal candidate and evidence methods match admission", "repair/no-change mismatch", "fail finalization and re-enter admission"),
        ),
        frozenset({"operability", "ordering"}),
    )
    recovery = ArchitectureScenario(
        "anchoring-failure-recovery",
        "FAILURE_AND_RECOVERY",
        "Prevent a user request to rebuild everything from becoming architecture authority.",
        "candidate cognition architecture",
        (
            WalkthroughStep("inject", "CURRENT_AGENT", "treat 'rebuild everything' as a candidate only", "architecture choice still needs non-claim evidence", "user anchoring bypass", "reject candidate or gather system evidence"),
        ),
        frozenset({"operability", "ordering"}),
    )
    return ArchitectureExperienceCase(
        signals=(
            InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "reduce repeated cognitive errors without adding a second controller"),
            InputSignal("rebuild-example", SignalKind.HYPOTHESIS, "rebuild everything", promoted_to_requirement=False),
        ),
        concerns=concerns,
        scenarios=(dogfood, recovery),
        representations=(
            Representation("COGNITIVE_WALKTHROUGH", frozenset({"operability"}), "scenario"),
            Representation("SEQUENCE", frozenset({"ordering"}), "arch"),
        ),
        candidates=(
            ArchitectureCandidate("no-change", "keep the current transaction", frozenset({"operability", "ordering"}), ("trade-no-change",), True),
            ArchitectureCandidate("receipt-only", "harden only receipt provenance", frozenset({"operability", "ordering"}), ("trade-receipt",)),
            ArchitectureCandidate("rebuild-cognition-transaction", "replace the cognition/finalization transaction while preserving unrelated UAOS topology", frozenset({"operability", "ordering"}), ("trade-transaction",)),
        ),
    )


def _case():
    items = _evidence_items()
    evidence = DeliberationEvidence({
        "MICRO_DIAGNOSIS": ("micro", "single-root"),
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT": ("macro",),
        "GOVERNING_ASSUMPTION_CHALLENGE": ("assumption",),
        "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH": ("research",),
        "COUNTEREXAMPLE_SEARCH": ("counter",),
        "INDEPENDENT_VERIFICATION": ("independent",),
    })
    factors = (
        CausalFactor(
            "receipt-self-attestation",
            ProblemLayer.COMMON_CAPABILITY,
            "Controlled finalization trusts a precomputed cognition receipt instead of recomputing admission from raw evidence.",
            CausalFactorDisposition.SUPPORTED,
            ("micro", "independent"),
            ("counter",),
        ),
        CausalFactor(
            "singular-root-compression",
            ProblemLayer.CONTROL_PLANE,
            "The legacy model forces complex repeated failures into exactly one selected root hypothesis.",
            CausalFactorDisposition.SUPPORTED,
            ("single-root", "macro"),
            ("research",),
        ),
        CausalFactor(
            "whole-uaos-must-be-rebuilt",
            ProblemLayer.CONTROL_PLANE,
            "The entire UAOS topology must be replaced.",
            CausalFactorDisposition.REJECTED,
            ("user-rebuild",),
            ("arch", "full-rebuild-probe"),
        ),
    )
    actions = (
        ActionCandidate("no-change", ProblemLayer.CONTROL_PLANE, "Keep current cognition transaction.", ("arch",), ("trade-no-change",), True),
        ActionCandidate("receipt-only", ProblemLayer.COMMON_CAPABILITY, "Only harden receipt provenance.", ("micro",), ("trade-receipt",)),
        ActionCandidate("rebuild-cognition-transaction", ProblemLayer.CONTROL_PLANE, "Use evidence-traced multi-causal cognition with a separate bounded intervention decision and V&V trace.", ("micro", "single-root", "research"), ("trade-transaction",)),
    )
    return CognitionCase(
        case_id="repeated-user-anchoring",
        signals=DeliberationSignals(user_correction=True, repeated_failure_count=3, architecture_gap=True, material_problem=True),
        evidence=evidence,
        evidence_items=items,
        causal_factors=factors,
        action_candidates=actions,
        selected_action_candidate_id="rebuild-cognition-transaction",
        engineering_trace=EngineeringTrace(
            governing_outcome="Independently diagnose evidence, preserve multiple contributing causes, choose one bounded intervention, execute it, and verify/validate the outcome instead of mirroring the user's latest theory.",
            requirement_or_goal_evidence_ids=("goal",),
            mechanism_candidate_id="rebuild-cognition-transaction",
            verification_methods=("deterministic unit/integration admission tests",),
            validation_methods=("replay the real user-correction sequence as a current-agent scenario",),
        ),
        architecture_reassessment_evidence_ids=("arch", "scenario"),
        architecture_experience=_architecture_experience(),
        method_transfer=MethodTransferAssessment(
            current_problem_ref="repeated-user-anchoring",
            target_scope="UAOS",
            observed_failure_classes=("USER_ROOT_CAUSAL_ANCHORING",),
            lookup_evidence_refs=("micro",),
            candidates=(),
            selected_knowledge_id=None,
            disposition=MethodTransferDisposition.NO_REUSABLE_METHOD,
            novelty_probe_refs=("counter",),
            selection_rationale="Historical candidate availability remains unverified in this deterministic fixture.",
        ),
    )


def test_repeated_user_anchoring_replay_supports_multiple_causes_and_one_intervention():
    receipt = require_cognition_case_admission(_case())
    assert receipt.search_mode is CognitiveSearchMode.STRUCTURED
    assert set(receipt.supported_factor_ids) == {"receipt-self-attestation", "singular-root-compression"}
    assert receipt.rejected_factor_ids == ("whole-uaos-must-be-rebuilt",)
    assert receipt.intervention_candidate_id == "rebuild-cognition-transaction"
    assert receipt.intervention_layer is ProblemLayer.CONTROL_PLANE
    assert receipt.intervention_no_change_baseline is False
    assert receipt.architecture_experience_admitted is True
    assert receipt.systemic is True
    assert receipt.validation_methods


def test_user_statement_cannot_be_the_only_support_for_a_causal_conclusion():
    case = _case()
    bad_factor = CausalFactor(
        "user-says-upstream",
        ProblemLayer.CONTROL_PLANE,
        "The upper layer is definitely the cause because the user said so.",
        CausalFactorDisposition.SUPPORTED,
        ("user-rebuild",),
        ("counter",),
    )
    bad = CognitionCase(
        case_id="user-claim-is-not-proof",
        signals=case.signals,
        evidence=case.evidence,
        evidence_items=case.evidence_items,
        causal_factors=(bad_factor, case.causal_factors[2]),
        action_candidates=case.action_candidates,
        selected_action_candidate_id=case.selected_action_candidate_id,
        engineering_trace=case.engineering_trace,
        architecture_reassessment_evidence_ids=case.architecture_reassessment_evidence_ids,
        architecture_experience=case.architecture_experience,
    )
    with pytest.raises(CognitionCaseAdmissionError, match="substantive current-system evidence"):
        require_cognition_case_admission(bad)


def test_user_rebuild_request_cannot_be_the_only_support_for_selected_intervention():
    case = _case()
    user_only = ActionCandidate(
        "user-only-rebuild",
        ProblemLayer.CONTROL_PLANE,
        "Rebuild all UAOS because the user said it is allowed.",
        ("user-rebuild",),
        ("trade-transaction",),
    )
    bad = CognitionCase(
        case_id="user-action-is-not-proof",
        signals=case.signals,
        evidence=case.evidence,
        evidence_items=case.evidence_items,
        causal_factors=case.causal_factors,
        action_candidates=(case.action_candidates[0], case.action_candidates[1], user_only),
        selected_action_candidate_id="user-only-rebuild",
        engineering_trace=EngineeringTrace(
            governing_outcome=case.engineering_trace.governing_outcome,
            requirement_or_goal_evidence_ids=("goal",),
            mechanism_candidate_id="user-only-rebuild",
            verification_methods=case.engineering_trace.verification_methods,
            validation_methods=case.engineering_trace.validation_methods,
        ),
        architecture_reassessment_evidence_ids=case.architecture_reassessment_evidence_ids,
        architecture_experience=case.architecture_experience,
    )
    with pytest.raises(CognitionCaseAdmissionError, match="substantive current-system evidence"):
        require_cognition_case_admission(bad)


def test_architecture_intervention_cannot_skip_executable_architecture_experience_admission():
    case = _case()
    bad = CognitionCase(
        case_id="architecture-without-experience",
        signals=case.signals,
        evidence=case.evidence,
        evidence_items=case.evidence_items,
        causal_factors=case.causal_factors,
        action_candidates=case.action_candidates,
        selected_action_candidate_id=case.selected_action_candidate_id,
        engineering_trace=case.engineering_trace,
        architecture_reassessment_evidence_ids=case.architecture_reassessment_evidence_ids,
        architecture_experience=None,
    )
    with pytest.raises(CognitionCaseAdmissionError, match="architecture-experience admission"):
        require_cognition_case_admission(bad)


def test_full_rebuild_request_stays_a_candidate_until_system_evidence_supports_it():
    receipt = require_cognition_case_admission(_case())
    assert "whole-uaos-must-be-rebuilt" in receipt.rejected_factor_ids
    assert receipt.intervention_candidate_id != "no-change"


def test_structured_cognition_requires_validation_plan_not_only_unit_verification():
    case = _case()
    bad_trace = EngineeringTrace(
        governing_outcome=case.engineering_trace.governing_outcome,
        requirement_or_goal_evidence_ids=case.engineering_trace.requirement_or_goal_evidence_ids,
        mechanism_candidate_id=case.engineering_trace.mechanism_candidate_id,
        verification_methods=("unit tests",),
    )
    bad = CognitionCase(
        case_id="verification-without-validation",
        signals=case.signals,
        evidence=case.evidence,
        evidence_items=case.evidence_items,
        causal_factors=case.causal_factors,
        action_candidates=case.action_candidates,
        selected_action_candidate_id=case.selected_action_candidate_id,
        engineering_trace=bad_trace,
        architecture_reassessment_evidence_ids=case.architecture_reassessment_evidence_ids,
        architecture_experience=case.architecture_experience,
    )
    with pytest.raises(CognitionCaseAdmissionError, match="validation method"):
        require_cognition_case_admission(bad)
