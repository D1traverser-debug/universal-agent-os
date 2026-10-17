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


def test_runtime_skill_frontloads_mandatory_entry_before_bootstrap_and_mutation():
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    entry = text.index("## 1. Mandatory selected-context entry")
    authority = text.index("## 2. Recover current authority")
    mutation = text.index("## 6. Evolution and mutation")
    assert entry < authority < mutation
    assert "Entry is mandatory; escalation is adaptive." in text
    assert "not prerequisites for entering this sentinel" in text
    assert "route broad unknown-method/framework/capability learning" in text


def test_runtime_skill_preserves_requirement_vs_candidate_semantics_without_incident_phrases():
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    assert "requirements at their valid scope" in text
    assert "remain candidates until current evidence admits them" in text
    assert "remains an ActionCandidate" in text
    assert "independent of whether it solves the diagnosed problem" in text
    for incident_phrase in ("just do X", "upper layer is the cause", "10 rules", "no-op user message"):
        assert incident_phrase not in text


def test_custom_instruction_pointer_is_mandatory_entry_not_symptom_trigger_and_stays_compact():
    pointer = _recommended_custom_instruction_pointer()
    assert 0 < len(pointer) <= 1500
    assert pointer.startswith("After UAOS or a registered persistent Agent/domain is selected")
    assert "before every substantive response, tool call, or action" in pointer
    assert "Entry is unconditional; heavy cognition/research/evolution is adaptive." in pointer
    assert "Neither I nor your pre-entry interpretation must label a task" in pointer
    assert "from any source remain candidates until evidence supports them" in pointer
    assert "explicit outcomes/constraints" in pointer
    assert "choose the next evidence-supported action, execute, verify, reassess, and continue" in pointer
    assert "Broad unknown-method/framework learning uses coverage-oriented acquisition" in pointer
    assert "never use `next` or another no-op user message as the workflow clock" not in pointer
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
