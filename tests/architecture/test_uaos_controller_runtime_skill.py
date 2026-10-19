import json
from pathlib import Path

from uaos.runtime.native_runtime_skill import build_native_runtime_skill


ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _recommended_custom_instruction_pointer() -> str:
    text = (ROOT / "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")
    recommended = text.split("## Recommended Custom Instructions", 1)[1].split("Do not paste", 1)[0]
    lines = []
    for line in recommended.splitlines():
        if line == ">":
            lines.append("")
        elif line.startswith("> "):
            lines.append(line[2:])
    return "\n".join(lines).strip()


def test_runtime_skill_is_exact_generated_projection_of_canonical_owners():
    expected = build_native_runtime_skill(
        intent_policy=_json("config/INTENT_RESOLUTION_POLICY.json"),
        session_policy=_json("config/SESSION_INTERACTION_POLICY.json"),
        deliberation_policy=_json("config/DELIBERATION_POLICY.json"),
        evolution_policy=_json("config/EVOLUTION_POLICY.json"),
        host_profiles=_json("config/HOST_PROFILES.json"),
    )
    actual = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    assert actual == expected


def test_runtime_skill_metadata_is_scope_based_not_a_problem_symptom_ontology():
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\nname: uaos-controller-runtime\n")
    metadata = text.split("---", 2)[1]
    description = next(line for line in metadata.splitlines() if line.startswith("description:"))
    assert "selected UAOS or registered persistent-Agent work" in description
    assert "mandatory lightweight entry" in description
    assert "canonical UAOS owners" in description
    assert "repeated failures" not in description
    assert "contradictory evidence" not in description
    assert "local patch" not in description


def test_runtime_skill_is_dispatcher_not_second_cognition_research_or_evolution_machine():
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "generated, non-authoritative" in lowered
    assert "does not own cognition, research, evolution" in lowered
    assert "EvolutionTransaction" in text
    canonical_stage_tokens = (
        "FRAME_OUTCOME_OBSERVATIONS_AND_HYPOTHESES",
        "EXPAND_CAUSAL_SOLUTION_AND_EVIDENCE_SPACE",
        "FALSIFY_TRACE_AND_COMPARE",
        "COMMIT_CAUSAL_MODEL_INTERVENTION_AND_LEARNING",
        "ACT_VERIFY_VALIDATE_AND_OBSERVE",
    )
    assert not any(token in text for token in canonical_stage_tokens)


def test_runtime_skill_frontloads_mandatory_entry_continuation_and_blocker_semantics():
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    entry = text.index("## 1. Mandatory selected-context entry")
    continuation = text.index("Autonomous continuation:")
    blocker = text.index("Blocker rule:")
    authority = text.index("## 2. Recover current authority")
    mutation = text.index("## 6. Evolution and mutation")
    assert entry < continuation < blocker < authority < mutation
    assert "Entry is mandatory; escalation is adaptive." in text
    assert "not prerequisites for entering this sentinel" in text
    assert "unresolved causality disguised as certainty is not a valid repair claim" in text
    assert "adaptively route current observations" in text
    assert "governing rules, architecture and learning method itself" in text
    assert "persist exact continuation without waiting for a user reminder" in text


def test_runtime_skill_preserves_requirement_vs_candidate_semantics_without_incident_phrases():
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    intent = _json("config/INTENT_RESOLUTION_POLICY.json")["problem_solution_directive_resolution"]
    assert intent["outcome_constraint_rule"] in text
    assert "remain candidates until current evidence admits them" in text
    assert "remains an ActionCandidate" in text
    assert "independent of whether it solves the diagnosed problem" in text
    for incident_phrase in ("just do X", "upper layer is the cause", "10 rules", "no-op user message"):
        assert incident_phrase not in text


def test_custom_instruction_pointer_is_mandatory_entry_not_symptom_trigger_and_stays_compact():
    pointer = _recommended_custom_instruction_pointer()
    lower = pointer.lower()
    assert 0 < len(pointer) <= 1500
    assert pointer.startswith("After UAOS or a registered persistent Agent/domain is selected")
    assert "before every substantive response, tool call, or action" in pointer
    assert "entry is unconditional" in lower
    assert "escalation is adaptive" in lower
    assert "the user is not the classifier" in lower
    assert "internal cognition, evidence gathering, admission, comparison, and verification" in lower
    assert "are work to continue, not blockers" in lower
    assert "from any source as candidates until evidence supports them" in lower
    assert "explicit outcomes/constraints" in lower
    assert "choose the next evidence-supported action, execute, verify, reassess, and continue" in lower
    assert "broad unknown-method/framework learning uses coverage-oriented acquisition" in lower
    assert "never use `next` or another no-op user message as the workflow clock" not in lower
    assert "FRAME_OUTCOME_OBSERVATIONS_AND_HYPOTHESES" not in pointer


def test_chatgpt_host_and_compiled_profile_bind_mandatory_entry_skill():
    host = _json("config/HOST_PROFILES.json")["profiles"]["CHATGPT_GITHUB"]
    profile = _json("config/NATIVE_SESSION_RUNTIME_PROFILE.json")
    assert host["native_runtime_skill_source"] == "skills/uaos-controller-runtime/SKILL.md"
    assert "NON_AUTHORITATIVE" in host["native_runtime_skill_role"]
    assert host["custom_instructions_role"] == "BOOTSTRAP_ONLY__NON_AUTHORITATIVE"
    assert "MANDATORY_LIGHTWEIGHT_ENTRY" in host["native_runtime_skill_activation"]
    assert profile["runtime_skill"]["source"] == host["native_runtime_skill_source"]
    assert profile["runtime_skill"]["role"] == host["native_runtime_skill_role"]
    assert profile["runtime_skill"]["activation"] == host["native_runtime_skill_activation"]
    assert profile["turn_contract"]["mandatory_entry"]["scope"] == _json("config/SESSION_INTERACTION_POLICY.json")["mandatory_selected_context_entry"]["scope"]
    assert "INTERNAL ROUTING SIGNALS" in profile["turn_contract"]["mandatory_entry"]["anti_circularity"]


def test_compiled_profile_exposes_complete_systemic_repair_not_smallest_diff_rule():
    session = _json("config/SESSION_INTERACTION_POLICY.json")
    profile = _json("config/NATIVE_SESSION_RUNTIME_PROFILE.json")
    source = session["problem_to_action_closure_gate"]["systemic_repair_completeness"]
    projected = profile["turn_contract"]["problem_closure"]["systemic_repair_completeness"]
    assert projected["required_evidence"] == source["required_evidence"]
    assert projected["local_intervention_exception"] == source["local_intervention_exception"]
    assert "SMALLEST_COMPLETE_INTERVENTION" in projected["selection_principle"]
    assert "SMALLEST_DIFF" in projected["selection_principle"]


def test_native_dispatcher_projects_all_ten_progress_fields_from_canonical_session_authority():
    session = _json("config/SESSION_INTERACTION_POLICY.json")
    progress = session["inherited_session_progress_report"]
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    assert progress["required"] is True
    assert progress["scope"] in text
    assert progress["placement"] in text
    assert "Before releasing each selected-context final reply" in text
    assert "including the assistant's own output" in text
    assert progress["timestamp_display_format"] in text
    assert progress["evolution_rule"] in text
    assert progress["deliberation_rule"] in text
    aliases = (
        "当前 Agent", "当前任务", "Authority", "状态", "当前阶段",
        "下一动作", "Evolution", "Deliberation", "版本", "进度时间",
    )
    for label, field in zip(aliases, progress["fields"], strict=True):
        assert f"- {label}: {field}" in text
    assert len(aliases) == 10


def test_native_dispatcher_refuses_silent_loss_of_mandatory_progress_contract():
    import pytest
    from uaos.runtime.native_runtime_skill import NativeRuntimeSkillError

    policies = dict(
        intent_policy=_json("config/INTENT_RESOLUTION_POLICY.json"),
        session_policy=_json("config/SESSION_INTERACTION_POLICY.json"),
        deliberation_policy=_json("config/DELIBERATION_POLICY.json"),
        evolution_policy=_json("config/EVOLUTION_POLICY.json"),
        host_profiles=_json("config/HOST_PROFILES.json"),
    )
    modified = dict(policies["session_policy"])
    modified.pop("inherited_session_progress_report")
    with pytest.raises(NativeRuntimeSkillError, match="inherited_session_progress_report"):
        build_native_runtime_skill(**(policies | {"session_policy": modified}))
    modified = dict(policies["session_policy"])
    modified["inherited_session_progress_report"] = {
        **modified["inherited_session_progress_report"], "required": False,
    }
    with pytest.raises(NativeRuntimeSkillError, match="must remain mandatory"):
        build_native_runtime_skill(**(policies | {"session_policy": modified}))


def test_current_entry_does_not_contain_literal_escaped_newline_shadow_separator():
    entry = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    marker = "**Context reads are role-specific, not exhaustive**"
    assert entry.count(marker) == 1
    assert entry.split(marker, 1)[0].endswith(chr(10) + chr(10))
    assert chr(92) + "n" + chr(92) + "n" + marker not in entry


def test_self_correction_target_and_outcome_fit_are_projected_before_routing_not_buried_in_procedure():
    intent = _json("config/INTENT_RESOLUTION_POLICY.json")
    rules = intent["problem_solution_directive_resolution"]
    skill = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    pointer = _recommended_custom_instruction_pointer()
    assert "Agent/controller's own interpretation" in rules["correction_target_rule"]
    assert "unrelated work" in rules["correction_target_rule"]
    assert "actual complained-of capability" in rules["intervention_outcome_alignment_rule"]
    first_section = skill.split("## 2. Recover current authority", 1)[0]
    assert rules["correction_target_rule"] in first_section
    assert rules["intervention_outcome_alignment_rule"] in first_section
    assert skill.index("Agent self-correction target:") < skill.index("## 2. Recover current authority")
    assert skill.index("Intervention-to-outcome alignment:") < skill.index("## 2. Recover current authority")
    assert "identify and improve the failing capability" in pointer
    assert "do not substitute stopping unrelated work for self-repair" in pointer


def test_goal_fidelity_repair_retracts_child_work_suspension_in_exact_current_task_and_selector():
    task = _json("state/tasks/uaos-inheritance-review-20261018.json")
    index = _json("state/TASK_INDEX.json")
    record = task["self_assurance_priority_gate_20261019"]
    assert record["status"].startswith("RETRACTED")
    assert record["suspended_scope"] == "NONE__NORMAL_AUTHORIZED_WORK_CONTINUES"
    assert "SUSPENDED" not in task["current_stage"]
    # An ongoing controller stage can advance to autonomous evolution without
    # losing the independently governed goal-fidelity repair or restoring the freeze.
    assert "SUSPENDED" not in task["current_stage"]
    assert task["controller_goal_fidelity_20261019"]["status"] != "COMPLETE"
    assert task["controller_goal_fidelity_20261019"]["erroneous_intervention"] == "SUSPEND_DISCRETIONARY_CHILD_AUDITS"
    current = [entry for entry in index["controller_tasks"] if entry["default_resume"]]
    assert len(current) == 1
    assert current[0]["task_id"] == task["task_id"]
    assert current[0]["current_stage"] == task["current_stage"]


def test_compiled_self_repair_language_is_not_the_same_as_a_proven_native_behavioral_result():
    skill = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    assert "A self-review without a trusted host trace is not independent native enforcement." in skill
    task = _json("state/tasks/uaos-inheritance-review-20261018.json")
    assert "NATIVE_CHATGPT_SELF_GOVERNANCE_UNVERIFIED" in task["controller_goal_fidelity_20261019"]["assurance"]
