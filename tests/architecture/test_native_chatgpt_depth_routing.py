from uaos.kernel.problem_space import MethodTransferAssessment, MethodTransferDisposition
import json
from pathlib import Path

from uaos.kernel import (
    ActionCandidate,
    ArchitectureCandidate,
    ArchitectureConcern,
    ArchitectureExperienceCase,
    ArchitectureScenario,
    CausalFactor,
    CausalFactorDisposition,
    CognitionCase,
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

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _maintenance_evidence():
    return (
        EvidenceItem("goal", EvidenceKind.USER_CLAIM, "The user wants the Agent to decide when deeper/system-level work is needed without waiting for the user to classify the task or ask for a better solution.", "conversation://native-chatgpt-depth-routing-goal"),
        EvidenceItem("session-gap", EvidenceKind.REPOSITORY_FACT, "Production SESSION_INTERACTION_POLICY had an always-on problem detector but no equally explicit every-turn execution-depth routing responsibility for non-problem work.", "repo://main@012feee/config/SESSION_INTERACTION_POLICY.json"),
        EvidenceItem("pointer-gap", EvidenceKind.REPOSITORY_FACT, "Production CHATGPT_CUSTOM_INSTRUCTIONS activated cognition for problem/correction/knowledge-gap cases but did not tell the session to independently assess DeepTask depth for every request.", "repo://main@012feee/docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md"),
        EvidenceItem("kernel-exists", EvidenceKind.REPOSITORY_FACT, "DeepTaskSignals and assess_deep_task_requirement already support semantic explicit and non-explicit escalation, so a second classifier/cognition owner is unnecessary.", "repo://main@012feee/src/uaos/kernel/deep_task.py"),
        EvidenceItem("macro", EvidenceKind.ANALYSIS_RESULT, "The reproduced failure is an invocation-responsibility gap between native-session bootstrap and the existing DeepTask kernel, not a missing A-H evidence profile.", "analysis://host-session-kernel-seam"),
        EvidenceItem("assumption", EvidenceKind.ANALYSIS_RESULT, "Copying the full DeepTask policy into account Custom Instructions would create a second stale behavioral authority rather than fixing invocation ownership.", "analysis://shadow-policy-risk"),
        EvidenceItem("openai-custom-instructions", EvidenceKind.EXTERNAL_SOURCE, "OpenAI documents Custom Instructions as direct guidance applied across chats, supporting their use as a compact bootstrap surface rather than a repository policy copy.", "https://help.openai.com/articles/8096356-chatgpt-custom-instructions", "OpenAI Help Center product-behavior verification"),
        EvidenceItem("openai-memory", EvidenceKind.EXTERNAL_SOURCE, "OpenAI documents Memory as relevance-selected and not an every-detail/every-response retrieval mechanism, so Memory alone is not a deterministic UAOS bootstrap substitute.", "https://help.openai.com/articles/8590148-memory-in-chatgpt", "OpenAI Help Center product-behavior verification"),
        EvidenceItem("github-reread", EvidenceKind.TOOL_RESULT, "Repository reread independently confirmed the production session/pointer gap and the already-existing DeepTask semantic mechanism.", "tool://github-production-reread-20261017", "repository authority gap audit"),
        EvidenceItem("unknown-probe", EvidenceKind.TOOL_RESULT, "Authority-wide scan found the residual user-explicit wording in AGENTS and the missing session sentinel, while the DeepTask kernel itself already supported host-classified escalation.", "tool://authority-wide-trigger-semantics-scan", "repository semantic closure scan"),
        EvidenceItem("trade-no-change", EvidenceKind.ANALYSIS_RESULT, "NO_CHANGE preserves the reproduced gap: the user may still have to notice that an unlabeled non-problem task needs deeper work.", "tradeoff://no-change"),
        EvidenceItem("trade-copy", EvidenceKind.ANALYSIS_RESULT, "Full-policy Custom Instructions improve salience but create policy drift, prompt bloat, and a second stale source of truth.", "tradeoff://full-policy-copy"),
        EvidenceItem("trade-sentinel", EvidenceKind.ANALYSIS_RESULT, "A lightweight session sentinel assigns classification responsibility to the Agent while reusing current DeepTask semantics and keeping simple tasks lightweight.", "tradeoff://session-sentinel"),
        EvidenceItem("dogfood-scenario", EvidenceKind.SCENARIO_RESULT, "CURRENT_AGENT walkthrough: an unlabeled architecture/design request is self-classified, current authority is consulted, and DeepTask is activated only when ordinary structured evidence is insufficient.", "scenario://current-agent-unlabeled-depth-routing", "CURRENT_AGENT cognitive walkthrough"),
        EvidenceItem("recovery-scenario", EvidenceKind.SCENARIO_RESULT, "Failure/recovery replay: if initial depth is light but new evidence reveals material uncertainty or architecture risk, the session re-evaluates depth before material completion rather than waiting for the user to object.", "scenario://depth-reclassification-recovery", "failure-and-recovery replay"),
    )


def _architecture_experience():
    concerns = (
        ArchitectureConcern("classification-ownership", "The acting Agent, not the user, owns routine execution-depth classification.", actor_operability_material=True),
        ArchitectureConcern("dynamic-reclassification", "Depth can be re-evaluated when new evidence changes the task risk/uncertainty profile.", temporal_behavior_material=True),
        ArchitectureConcern("authority-split", "Custom Instructions bootstrap the session while repository policy remains the single semantic authority.", structural_relationships_material=True),
    )
    dogfood = ArchitectureScenario(
        "current-agent-unlabeled-request",
        "CURRENT_AGENT_DOGFOOD",
        "Handle an unlabeled material design request without requiring the user to diagnose its depth.",
        "UAOS selected; user asks for a result without naming DeepTask",
        (
            WalkthroughStep("classify", "CURRENT_AGENT", "derive current execution-depth signals from the request and available evidence", "ordinary-vs-deep route is explicit before material completion", "wait for the user to say 'go deeper'", "consult current session/deep-task authority and derive semantic signals"),
            WalkthroughStep("execute", "CURRENT_AGENT", "use the minimum sufficient current execution depth and collect required evidence", "simple work stays light; material deep work has admitted evidence", "copy the full policy into the account pointer or over-expand every task", "return to the repository-owned DeepTask admission/profile"),
        ),
        frozenset({"classification-ownership", "authority-split"}),
    )
    recovery = ArchitectureScenario(
        "depth-miss-recovery",
        "FAILURE_AND_RECOVERY",
        "Recover when a request initially appears ordinary but execution reveals material uncertainty or architecture risk.",
        "ordinary execution already started",
        (
            WalkthroughStep("observe-new-evidence", "CURRENT_AGENT", "re-evaluate DeepTask semantic signals before material completion", "new evidence can escalate the route without a new user prompt", "freeze the first classification and deliver a shallow answer", "activate current DeepTask admission or remain ordinary with evidence"),
        ),
        frozenset({"classification-ownership", "dynamic-reclassification"}),
    )
    return ArchitectureExperienceCase(
        signals=(
            InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "make depth selection Agent-owned and proactive without bloating simple tasks"),
            InputSignal("user-mechanism", SignalKind.OBSERVATION, "The user challenged user-triggered wording and asked why the system itself cannot know when to go deeper.", promoted_to_requirement=False),
        ),
        concerns=concerns,
        scenarios=(dogfood, recovery),
        representations=(
            Representation("COGNITIVE_WALKTHROUGH", frozenset({"classification-ownership"}), "dogfood-scenario"),
            Representation("SEQUENCE", frozenset({"dynamic-reclassification"}), "recovery-scenario"),
            Representation("AUTHORITY_MAP", frozenset({"authority-split"}), "macro"),
        ),
        candidates=(
            ArchitectureCandidate("no-change", "Keep the existing problem sentinel and user-explicit/host-classified DeepTask wording.", frozenset({"classification-ownership", "dynamic-reclassification", "authority-split"}), ("trade-no-change",), True),
            ArchitectureCandidate("full-custom-instructions-policy-copy", "Copy the detailed DeepTask policy into account Custom Instructions.", frozenset({"classification-ownership", "dynamic-reclassification", "authority-split"}), ("trade-copy",)),
            ArchitectureCandidate("session-execution-depth-sentinel", "Add a lightweight every-turn session sentinel that self-derives current depth and delegates detailed semantics to the existing DeepTask owner.", frozenset({"classification-ownership", "dynamic-reclassification", "authority-split"}), ("trade-sentinel",)),
        ),
    )


def _cognition_case():
    items = _maintenance_evidence()
    factors = (
        CausalFactor("session-invocation-gap", ProblemLayer.CONTROL_PLANE, "The session layer explicitly detects problems every turn but did not equally own every-turn non-problem execution-depth routing.", CausalFactorDisposition.SUPPORTED, ("session-gap", "pointer-gap", "github-reread"), ("kernel-exists",)),
        CausalFactor("bootstrap-pointer-gap", ProblemLayer.HOST, "The native ChatGPT pointer did not clearly assign autonomous depth classification to the acting session.", CausalFactorDisposition.SUPPORTED, ("pointer-gap", "github-reread"), ("openai-custom-instructions",)),
        CausalFactor("missing-deep-task-kernel", ProblemLayer.COMMON_CAPABILITY, "The DeepTask semantic mechanism itself is missing and must be replaced.", CausalFactorDisposition.REJECTED, ("macro",), ("kernel-exists", "unknown-probe")),
    )
    actions = (
        ActionCandidate("no-change", ProblemLayer.CONTROL_PLANE, "Keep current routing semantics.", ("session-gap",), ("trade-no-change",), True),
        ActionCandidate("full-custom-instructions-policy-copy", ProblemLayer.HOST, "Duplicate detailed DeepTask rules into account Custom Instructions.", ("openai-custom-instructions",), ("trade-copy",)),
        ActionCandidate("session-execution-depth-sentinel", ProblemLayer.CONTROL_PLANE, "Add an every-turn lightweight execution-depth sentinel and keep Custom Instructions as a compact bootstrap pointer.", ("session-gap", "pointer-gap", "kernel-exists", "github-reread"), ("trade-sentinel",)),
    )
    return CognitionCase(
        case_id="native-chatgpt-user-dependent-depth-routing",
        signals=DeliberationSignals(user_correction=True, repeated_failure_count=2, knowledge_gap=True, architecture_gap=True, material_problem=True),
        evidence=DeliberationEvidence({
            "MICRO_DIAGNOSIS": ("session-gap", "pointer-gap"),
            "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT": ("macro",),
            "GOVERNING_ASSUMPTION_CHALLENGE": ("assumption",),
            "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH": ("openai-custom-instructions", "openai-memory"),
            "COUNTEREXAMPLE_SEARCH": ("kernel-exists", "trade-no-change", "trade-copy"),
            "INDEPENDENT_VERIFICATION": ("github-reread",),
        }),
        evidence_items=items,
        causal_factors=factors,
        action_candidates=actions,
        selected_action_candidate_id="session-execution-depth-sentinel",
        engineering_trace=EngineeringTrace(
            governing_outcome="The selected Agent proactively chooses the minimum sufficient execution depth without making the user classify the task, while repository authority stays singular and simple tasks remain lightweight.",
            requirement_or_goal_evidence_ids=("goal",),
            mechanism_candidate_id="session-execution-depth-sentinel",
            verification_methods=("native ChatGPT depth-routing contract tests",),
            validation_methods=("CURRENT_AGENT unlabeled-request and depth-miss recovery replays",),
        ),
        architecture_reassessment_evidence_ids=("macro", "dogfood-scenario", "recovery-scenario"),
        architecture_experience=_architecture_experience(),
        method_transfer=MethodTransferAssessment(
            current_problem_ref="native-chatgpt-user-dependent-depth-routing",
            target_scope="UAOS",
            observed_failure_classes=("NATIVE_ROUTING_DEPTH_MISS",),
            lookup_evidence_refs=("session-gap",),
            candidates=(),
            selected_knowledge_id=None,
            disposition=MethodTransferDisposition.NO_REUSABLE_METHOD,
            novelty_probe_refs=("unknown-probe",),
            selection_rationale="The fixture has no certified prior-method analogy; retain that as explicit no-reuse.",
        ),
    )


def test_current_maintenance_problem_and_architecture_are_executable_admitted():
    receipt = require_cognition_case_admission(_cognition_case())
    assert receipt.search_mode is CognitiveSearchMode.STRUCTURED
    assert set(receipt.supported_factor_ids) == {"session-invocation-gap", "bootstrap-pointer-gap"}
    assert receipt.rejected_factor_ids == ("missing-deep-task-kernel",)
    assert receipt.intervention_candidate_id == "session-execution-depth-sentinel"
    assert receipt.architecture_experience_admitted is True
    assert receipt.systemic is True


def test_session_policy_requires_user_independent_execution_depth_routing():
    policy = _json("config/SESSION_INTERACTION_POLICY.json")
    sentinel = policy["always_on_execution_depth_sentinel"]
    assert sentinel["required"] is True
    assert "EVERY_ASSISTANT_TURN" in sentinel["scope"]
    assert "user is not responsible" in sentinel["responsibility"].lower()
    checks = " ".join(sentinel["checks"]).lower()
    assert "not as the only path" in checks
    assert "ordinary structured" in checks
    assert "assess_deep_task_requirement" in sentinel["assessment_ref"]


def test_chatgpt_pointer_is_bootstrap_not_shadow_policy():
    text = (ROOT / "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")
    lower = text.lower()
    assert "for every request, independently assess" in lower
    assert "mandatory escalation signal, not the only trigger" in lower
    assert "user is not the classifier" in lower
    assert "bootstrap-only and non-authoritative" in lower
    recommended = text.split("## Recommended Custom Instructions", 1)[1].split("Do not paste", 1)[0].lower()
    assert "professional-practice gap" not in recommended
    assert "holdout/replay" not in recommended
    assert len(recommended) <= 5000


def test_host_and_projection_preserve_native_chatgpt_boundary():
    hosts = _json("config/HOST_PROFILES.json")["profiles"]["CHATGPT_GITHUB"]
    current = _json("CURRENT_SYSTEM.json")
    assert hosts["custom_instructions_role"] == "BOOTSTRAP_ONLY__NON_AUTHORITATIVE"
    assert "EVERY_SELECTED_CONTEXT_TURN" in hosts["session_execution_depth_routing"]
    assert "NO_VERIFIED_REPOSITORY_CONTROLLED_NON_BYPASSABLE_SIGNAL_INJECTOR" in hosts["semantic_signal_assurance"]
    assert "execution_depth_detection_sentinel" in current["fresh_chat_bootstrap"]
    assert current["physical_complete_mediation_assurance"] == "CONTROLLED_RUNTIME_GATE_VERIFIED__NATIVE_CHATGPT_COMPLETE_MEDIATION_NOT_CLAIMED"
