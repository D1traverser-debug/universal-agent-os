import json
from pathlib import Path

from uaos.kernel import (
    ArchitectureCandidate,
    ArchitectureConcern,
    ArchitectureScenario,
    InputSignal,
    Representation,
    SignalKind,
    WalkthroughStep,
    require_architecture_experience_admission,
)

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_deliberation_policy_is_the_single_cognition_stage_authority():
    policy = _json("config/DELIBERATION_POLICY.json")
    kernel = policy["cognition_kernel"]
    assert kernel["canonical"] is True
    assert kernel["hot_path"] == [
        "FRAME_OUTCOME_OBSERVATIONS_AND_HYPOTHESES",
        "EXPAND_CAUSAL_SOLUTION_AND_EVIDENCE_SPACE",
        "FALSIFY_TRACE_AND_COMPARE",
        "COMMIT_CAUSAL_MODEL_INTERVENTION_AND_LEARNING",
        "ACT_VERIFY_VALIDATE_AND_OBSERVE",
    ]
    assert "other policies" in kernel["anti_bloat"].lower()
    assert policy["cognitive_search_modes"]["STRUCTURED"]["boundedness"]
    assert policy["cognition_case_transaction"]["canonical_for_problem_finalization"] is True
    assert policy["root_scope_admission"]["status"].startswith("LEGACY_COMPATIBILITY")


def test_session_common_and_current_system_reference_kernel_instead_of_copying_stage_machine():
    session = _json("config/SESSION_INTERACTION_POLICY.json")
    common = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    current = _json("CURRENT_SYSTEM.json")

    session_tx = session["problem_cognition_action_transaction"]
    common_tx = common["problem_cognition_action_transaction"]
    bootstrap_tx = current["fresh_chat_bootstrap"]["problem_cognition_action_transaction"]

    assert session_tx["canonical_cognition_policy_ref"] == "config/DELIBERATION_POLICY.json#cognition_kernel"
    assert common_tx["canonical_cognition_policy_ref"] == "config/DELIBERATION_POLICY.json#cognition_kernel"
    assert "ordered_stages" not in session_tx
    assert "rules" not in session_tx
    assert "ordered_stages" not in common_tx
    assert "rules" not in common_tx
    assert "CANONICAL_COGNITION" in bootstrap_tx
    assert "DETECT__DELIBERATE" not in bootstrap_tx
    assert "SOURCE_FIRST_MULTI_LENS_OUTSIDE_IN_DISCOVERY" in current["capability_discovery_assurance"]
    assert common["contract_version"] == "1.4.0"


def test_bootstrap_hot_path_exposes_only_the_canonical_five_primitives():
    entrypoint = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    stages = (
        "FRAME_OUTCOME_OBSERVATIONS_AND_HYPOTHESES",
        "EXPAND_CAUSAL_SOLUTION_AND_EVIDENCE_SPACE",
        "FALSIFY_TRACE_AND_COMPARE",
        "COMMIT_CAUSAL_MODEL_INTERVENTION_AND_LEARNING",
        "ACT_VERIFY_VALIDATE_AND_OBSERVE",
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
    assert "established need/failure class" in discovery["known_need_exception"].lower()
    assert "lightweight" in discovery["known_need_exception"].lower()
    assert discovery["executable_ref"] == "src/uaos/kernel/problem_space.py"
    assert "at least two distinct outside-in lenses" in discovery["broad_discovery_floor"]
    assert "not an instruction to create a matching Agent" in discovery["nonliteral_rule"]


def test_current_agent_dogfood_can_follow_the_five_stage_hot_path_without_a_second_state_machine():
    steps = (
        WalkthroughStep("frame", "CURRENT_AGENT", "recover outcome and hold first causes as hypotheses", "candidate frames remain distinguishable", "premature authority", "preserve observations and alternatives"),
        WalkthroughStep("expand", "CURRENT_AGENT", "expand plausible causal factors and intervention candidates", "risk-appropriate alternatives exist", "search too narrow", "use adaptive search mode"),
        WalkthroughStep("falsify", "CURRENT_AGENT", "attack preferred causes and trace evidence provenance", "material alternatives are rejected or bounded", "same-model confidence", "use repository/tool/test/external evidence"),
        WalkthroughStep("commit", "CURRENT_AGENT", "commit a possibly multi-causal model and one bounded intervention", "causal/intervention receipt exists", "easy edit or user theory mistaken for diagnosis", "block premature action"),
        WalkthroughStep("act", "CURRENT_AGENT", "perform selected authorized change and verify/validate it", "V&V evidence supports the governing outcome", "green unit tests overstated", "require realistic scenario/runtime validation when material"),
    )
    premortem = ArchitectureScenario(
        "cognition-pre-failure",
        "FAILURE_AND_RECOVERY",
        "prevent the cognition refactor from creating a new failure before release",
        "candidate cognition architecture",
        (
            WalkthroughStep(
                "premortem",
                "CURRENT_AGENT",
                "simulate user anchoring, singular-root compression, receipt self-attestation or ceremonial over-deliberation",
                "a missing invariant or recovery path is exposed before promotion",
                "happy-path component tests may miss an expensive or bypassable failure mode",
                "strengthen the executable admission/test and replay before promotion",
            ),
        ),
        frozenset({"operability", "ordering"}),
    )
    receipt = require_architecture_experience_admission(
        signals=(
            InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "reduce repeated cognitive errors without adding another control plane"),
            InputSignal("role-example", SignalKind.EXAMPLE, "use occupations as one discovery lens", promoted_to_requirement=False),
        ),
        concerns=(
            ArchitectureConcern("operability", "current Agent can execute a short cognition hot path", actor_operability_material=True),
            ArchitectureConcern("ordering", "action cannot precede evidence-traced causal/intervention admission", temporal_behavior_material=True),
        ),
        scenarios=(
            ArchitectureScenario("current-agent-cognition-dogfood", "CURRENT_AGENT_DOGFOOD", "detect and correct bad framing", "UAOS selected", steps, frozenset({"operability", "ordering"})),
            premortem,
        ),
        representations=(
            Representation("COGNITIVE_WALKTHROUGH", frozenset({"operability"}), "test://cognition-hot-path"),
            Representation("SEQUENCE", frozenset({"ordering"}), "test://frame-expand-falsify-commit-act"),
        ),
        candidates=(
            ArchitectureCandidate("no-change", "keep current singular-root receipt semantics", frozenset({"operability", "ordering"}), ("tradeoff://no-change",), True),
            ArchitectureCandidate("case-transaction", "use evidence-traced multi-causal cognition with bounded intervention and V&V", frozenset({"operability", "ordering"}), ("tradeoff://case-transaction",)),
        ),
        material_control_plane_or_agent_experience_change=True,
    )
    assert receipt.dogfood_present is True
    assert "role-example" in receipt.user_examples_kept_nonbinding
    assert receipt.candidate_ids == ("no-change", "case-transaction")
    assert receipt.failure_recovery_scenario_ids == ("cognition-pre-failure",)
