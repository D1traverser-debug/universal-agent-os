import pytest

from uaos.kernel.architecture_experience import (
    ArchitectureCandidate,
    ArchitectureConcern,
    ArchitectureExperienceAdmissionError,
    ArchitectureScenario,
    InputSignal,
    Representation,
    SignalKind,
    WalkthroughStep,
    require_architecture_experience_admission,
)


def step(step_id: str, actor: str = "CURRENT_AGENT") -> WalkthroughStep:
    return WalkthroughStep(
        step_id=step_id,
        actor=actor,
        action="resolve current authority and choose the next valid operation",
        expected_progress_signal="authority and next action are evidenced",
        failure_or_confusion_risk="cached state or an illustrative mechanism could anchor the Agent incorrectly",
        recovery_or_next_evidence="reread current authority and recover from the last verified state",
    )


def candidates(*concern_ids: str):
    covered = frozenset(concern_ids)
    return (
        ArchitectureCandidate("keep", "preserve current topology", covered, ("tradeoff://keep",), True),
        ArchitectureCandidate("change", "change only the narrowest justified mechanism", covered, ("tradeoff://change",)),
    )


def test_user_example_is_not_directly_promoted_to_architecture_requirement():
    signals = (
        InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "make the architecture understandable and usable by the current Agent"),
        InputSignal("example", SignalKind.EXAMPLE, "a sequence representation may preserve detail", promoted_to_requirement=True),
    )
    with pytest.raises(ArchitectureExperienceAdmissionError, match="promoted directly"):
        require_architecture_experience_admission(
            signals=signals,
            concerns=(ArchitectureConcern("operability", "Agent can understand and use the system", actor_operability_material=True),),
            scenarios=(ArchitectureScenario("dogfood", "CURRENT_AGENT_DOGFOOD", "complete work without losing the governing goal", "UAOS", (step("s1"),), frozenset({"operability"})),),
            representations=(Representation("COGNITIVE_WALKTHROUGH", frozenset({"operability"}), "walkthrough://dogfood"),),
            candidates=candidates("operability"),
            material_control_plane_or_agent_experience_change=True,
        )


def test_view_selection_is_concern_driven_not_one_diagram_for_everything():
    concerns = (
        ArchitectureConcern("ownership", "who owns authority and state", structural_relationships_material=True),
        ArchitectureConcern("recovery", "ordering and recovery across interruption", temporal_behavior_material=True),
        ArchitectureConcern("use", "current Agent can discover the right next step", actor_operability_material=True),
    )
    scenarios = (
        ArchitectureScenario("resume", "RESUME_AFTER_INTERRUPTION", "resume the correct task", "checkpoint", (step("s1"),), frozenset({"ownership", "recovery", "use"})),
    )
    representations = (
        Representation("AUTHORITY_MAP", frozenset({"ownership"}), "arch://authority"),
        Representation("EVENT_TRACE", frozenset({"recovery"}), "arch://resume-trace"),
        Representation("COGNITIVE_WALKTHROUGH", frozenset({"use"}), "arch://agent-walkthrough"),
    )
    receipt = require_architecture_experience_admission(
        signals=(InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "reliable resume"),),
        concerns=concerns,
        scenarios=scenarios,
        representations=representations,
        candidates=candidates("ownership", "recovery", "use"),
        material_control_plane_or_agent_experience_change=True,
    )
    assert receipt.dogfood_present is True
    assert set(receipt.representation_kinds) == {"AUTHORITY_MAP", "EVENT_TRACE", "COGNITIVE_WALKTHROUGH"}
    assert receipt.candidate_ids == ("keep", "change")


def test_temporal_concern_cannot_be_proven_only_by_static_structure():
    with pytest.raises(ArchitectureExperienceAdmissionError, match="temporal/behavioral"):
        require_architecture_experience_admission(
            signals=(InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "correct mutation order"),),
            concerns=(ArchitectureConcern("order", "branch then write then PR", temporal_behavior_material=True),),
            scenarios=(ArchitectureScenario("mutation", "FAILURE_AND_RECOVERY", "mutate safely", "main", (step("s1"),), frozenset({"order"})),),
            representations=(Representation("COMPONENT_VIEW", frozenset({"order"}), "arch://components"),),
            candidates=candidates("order"),
            material_control_plane_or_agent_experience_change=True,
        )


def test_material_agent_experience_change_requires_current_agent_dogfood():
    with pytest.raises(ArchitectureExperienceAdmissionError, match="CURRENT_AGENT dogfooding"):
        require_architecture_experience_admission(
            signals=(InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "usable control plane"),),
            concerns=(ArchitectureConcern("use", "operator usability", actor_operability_material=True),),
            scenarios=(ArchitectureScenario("third-party", "PRIMARY_SUCCESS_PATH", "complete task", "UAOS", (step("s1", actor="OTHER_ACTOR"),), frozenset({"use"})),),
            representations=(Representation("TASK_JOURNEY", frozenset({"use"}), "arch://journey"),),
            candidates=candidates("use"),
            material_control_plane_or_agent_experience_change=True,
        )


def test_material_change_requires_competing_candidates_and_no_change_baseline():
    kwargs = dict(
        signals=(InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "usable control plane"),),
        concerns=(ArchitectureConcern("use", "operator usability", actor_operability_material=True),),
        scenarios=(ArchitectureScenario("dogfood", "CURRENT_AGENT_DOGFOOD", "complete task", "UAOS", (step("s1"),), frozenset({"use"})),),
        representations=(Representation("TASK_JOURNEY", frozenset({"use"}), "arch://journey"),),
        material_control_plane_or_agent_experience_change=True,
    )
    with pytest.raises(ArchitectureExperienceAdmissionError, match="at least two architecture candidates"):
        require_architecture_experience_admission(**kwargs)
    with pytest.raises(ArchitectureExperienceAdmissionError, match="NO_CHANGE baseline"):
        require_architecture_experience_admission(
            **kwargs,
            candidates=(
                ArchitectureCandidate("a", "option a", frozenset({"use"}), ("tradeoff://a",)),
                ArchitectureCandidate("b", "option b", frozenset({"use"}), ("tradeoff://b",)),
            ),
        )


def test_every_walkthrough_step_must_expose_progress_risk_and_recovery():
    bad = WalkthroughStep(
        step_id="s1",
        actor="CURRENT_AGENT",
        action="do something",
        expected_progress_signal="",
        failure_or_confusion_risk="unknown authority",
        recovery_or_next_evidence="reread authority",
    )
    with pytest.raises(ArchitectureExperienceAdmissionError, match="lacks progress/risk/recovery"):
        require_architecture_experience_admission(
            signals=(InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "understand system"),),
            concerns=(ArchitectureConcern("use", "operator usability", actor_operability_material=True),),
            scenarios=(ArchitectureScenario("dogfood", "CURRENT_AGENT_DOGFOOD", "complete task", "UAOS", (bad,), frozenset({"use"})),),
            representations=(Representation("COGNITIVE_WALKTHROUGH", frozenset({"use"}), "arch://walkthrough"),),
            candidates=candidates("use"),
            material_control_plane_or_agent_experience_change=True,
        )
