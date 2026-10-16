import json
from pathlib import Path

from uaos.kernel import (
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
        "FRAME_AS_HYPOTHESIS",
        "EXPAND_PROBLEM_SPACE_WHEN_NEEDED",
        "FALSIFY_COMPETING_FRAMES",
        "COMMIT_ROOT_SCOPE_AND_LEARNING_DISPOSITION",
        "ACT_AND_VERIFY",
    ]
    assert "other policies" in kernel["anti_bloat"].lower()


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
    assert "established need/failure class" in discovery["known_need_exception"].lower()
    assert "lightweight" in discovery["known_need_exception"].lower()
    assert discovery["executable_ref"] == "src/uaos/kernel/problem_space.py"
    assert "at least two distinct outside-in lenses" in discovery["broad_discovery_floor"]
    assert "not an instruction to create a matching Agent" in discovery["nonliteral_rule"]


def test_current_agent_dogfood_can_follow_the_five_stage_hot_path_without_a_second_state_machine():
    steps = (
        WalkthroughStep(
            "frame",
            "CURRENT_AGENT",
            "hold the user's proposed cause and the Agent's first cause as hypotheses",
            "at least two candidate frames remain distinguishable",
            "latest wording could become premature authority",
            "reread the canonical cognition kernel and preserve both frames",
        ),
        WalkthroughStep(
            "expand",
            "CURRENT_AGENT",
            "expand across local, handoff, architecture/goal and latent-capability possibilities",
            "the problem space includes plausible nonlocal alternatives when evidence warrants them",
            "search could remain trapped inside a known keyword/need",
            "model the external source and use outside-in lenses when the task is broad discovery",
        ),
        WalkthroughStep(
            "falsify",
            "CURRENT_AGENT",
            "look for evidence that would make the preferred frame wrong",
            "at least one material alternative is rejected or bounded by evidence",
            "same-model confidence could masquerade as verification",
            "use external/owner evidence and keep assurance bounded",
        ),
        WalkthroughStep(
            "commit",
            "CURRENT_AGENT",
            "commit root scope and learning disposition only after evidence",
            "root-scope receipt and evolution disposition exist before action",
            "an easy edit could be mistaken for diagnosis",
            "block action admission until root scope is admitted",
        ),
        WalkthroughStep(
            "act",
            "CURRENT_AGENT",
            "perform the smallest authorized change and verify the governing objective",
            "verification evidence supports repair/no-change/block",
            "green tests could be overstated as live behavior proof",
            "report the assurance ceiling and keep live observation open when needed",
        ),
    )
    receipt = require_architecture_experience_admission(
        signals=(
            InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "reduce repeated cognitive errors without adding another control plane"),
            InputSignal("role-example", SignalKind.EXAMPLE, "use occupations as one discovery lens", promoted_to_requirement=False),
        ),
        concerns=(
            ArchitectureConcern("operability", "current Agent can execute a short cognition hot path", actor_operability_material=True),
            ArchitectureConcern("ordering", "action cannot precede framing/falsification/root-scope", temporal_behavior_material=True),
        ),
        scenarios=(
            ArchitectureScenario(
                "current-agent-cognition-dogfood",
                "CURRENT_AGENT_DOGFOOD",
                "detect and correct a bad framing before it becomes a system mutation",
                "UAOS selected; user correction observed",
                steps,
                frozenset({"operability", "ordering"}),
            ),
        ),
        representations=(
            Representation("COGNITIVE_WALKTHROUGH", frozenset({"operability"}), "test://cognition-hot-path"),
            Representation("SEQUENCE", frozenset({"ordering"}), "test://frame-expand-falsify-commit-act"),
        ),
        material_control_plane_or_agent_experience_change=True,
    )
    assert receipt.dogfood_present is True
    assert "role-example" in receipt.user_examples_kept_nonbinding
