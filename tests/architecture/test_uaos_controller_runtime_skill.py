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


def test_runtime_skill_has_discoverable_metadata_and_current_authority_bootstrap():
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\nname: uaos-controller-runtime\n")
    assert "description:" in text.split("---", 2)[1]
    metadata = text.split("---", 2)[1].lower()
    for trigger in ("corrections", "failures", "repeated failures", "architecture", "local patch"):
        assert trigger in metadata
    assert "ENTRYPOINT.md" in text
    assert "CURRENT_SYSTEM.json" in text
    assert "config/NATIVE_SESSION_RUNTIME_PROFILE.json" in text


def test_runtime_skill_is_dispatcher_not_second_cognition_or_evolution_state_machine():
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    assert "generated, non-authoritative" in text.lower()
    assert "does not own cognition" in text.lower()
    assert "EvolutionTransaction" in text
    assert "Do not hand-edit normative behavior here" in text
    canonical_stage_tokens = (
        "FRAME_OUTCOME_OBSERVATIONS_AND_HYPOTHESES",
        "EXPAND_CAUSAL_SOLUTION_AND_EVIDENCE_SPACE",
        "FALSIFY_TRACE_AND_COMPARE",
        "COMMIT_CAUSAL_MODEL_INTERVENTION_AND_LEARNING",
        "ACT_VERIFY_VALIDATE_AND_OBSERVE",
    )
    assert not any(token in text for token in canonical_stage_tokens)


def test_runtime_skill_frontloads_problem_remedy_self_falsification_before_bootstrap():
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    critical = text.index("## 1. CRITICAL pre-action problem gate")
    bootstrap = text.index("## 2. Bootstrap current authority")
    mutation = text.index("## 6. Mutation admission")
    assert critical < bootstrap < mutation
    assert "Do not act first and add a causal disclaimer afterward." in text
    assert "remains an ActionCandidate" in text
    assert "do not convert a remedy candidate into admitted intervention authority" in text


def test_runtime_skill_projects_problem_solution_directive_semantics():
    intent = _json("config/INTENT_RESOLUTION_POLICY.json")["problem_solution_directive_resolution"]
    text = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    assert intent["candidate_mechanism_rule"] in text
    assert intent["anti_bypass_rule"] in text
    assert intent["explicit_mechanism_requirement_rule"] in text
    assert intent["conflict_rule"] in text
    assert "remains an ActionCandidate" in text


def test_custom_instruction_pointer_starts_with_critical_problem_gate_and_stays_compact():
    pointer = _recommended_custom_instruction_pointer()
    assert 0 < len(pointer) <= 1500
    assert pointer.startswith("CRITICAL UAOS PROBLEM GATE:")
    assert "do not execute a proposed cause or fix first" in pointer
    assert "Treat diagnosis and remedy as hypotheses/ActionCandidates" in pointer
    assert "Only when I explicitly require a mechanism independently" in pointer
    assert "uaos-controller-runtime" in pointer
    assert "Repeated/systemic repairs must cover the failure class" in pointer
    assert "never use `next` as the workflow clock" in pointer
    assert "FRAME_OUTCOME_OBSERVATIONS_AND_HYPOTHESES" not in pointer


def test_chatgpt_host_and_compiled_profile_bind_the_same_non_authoritative_skill():
    host = _json("config/HOST_PROFILES.json")["profiles"]["CHATGPT_GITHUB"]
    profile = _json("config/NATIVE_SESSION_RUNTIME_PROFILE.json")
    assert host["native_runtime_skill_source"] == "skills/uaos-controller-runtime/SKILL.md"
    assert "NON_AUTHORITATIVE" in host["native_runtime_skill_role"]
    assert host["custom_instructions_role"] == "BOOTSTRAP_ONLY__NON_AUTHORITATIVE"
    assert profile["runtime_skill"]["source"] == host["native_runtime_skill_source"]
    assert profile["runtime_skill"]["role"] == host["native_runtime_skill_role"]
    assert "SKILL_METADATA_RELEVANCE_IS_SECONDARY" in profile["runtime_skill"]["activation"]


def test_compiled_profile_exposes_complete_systemic_repair_not_smallest_diff_rule():
    session = _json("config/SESSION_INTERACTION_POLICY.json")
    profile = _json("config/NATIVE_SESSION_RUNTIME_PROFILE.json")
    source = session["problem_to_action_closure_gate"]["systemic_repair_completeness"]
    projected = profile["turn_contract"]["problem_closure"]["systemic_repair_completeness"]
    assert projected["required_evidence"] == source["required_evidence"]
    assert projected["local_intervention_exception"] == source["local_intervention_exception"]
    assert "SMALLEST_COMPLETE_INTERVENTION" in projected["selection_principle"]
    assert "SMALLEST_DIFF" in projected["selection_principle"]
