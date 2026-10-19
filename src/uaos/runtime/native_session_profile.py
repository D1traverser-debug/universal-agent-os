from __future__ import annotations

from typing import Any, Mapping


class NativeSessionProfileError(ValueError):
    """Raised when canonical policy inputs cannot produce the native runtime projection."""


def _mapping(value: object, *, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise NativeSessionProfileError(f"{field} must be a mapping")
    return value


def _value(mapping: Mapping[str, Any], key: str, *, field: str) -> Any:
    if key not in mapping:
        raise NativeSessionProfileError(f"missing {field}.{key}")
    return mapping[key]


def build_native_session_runtime_profile(
    *,
    session_policy: Mapping[str, Any],
    deliberation_policy: Mapping[str, Any],
    host_profiles: Mapping[str, Any],
) -> dict[str, Any]:
    """Compile the small effective behavior projection used by native ChatGPT sessions.

    This object is deliberately *not* a new policy authority. It is a generated read model
    over the canonical session, deliberation and host policies so a native ChatGPT turn does
    not have to reconstruct the effective hot path from several large documents. Any drift
    is detected by comparing the committed projection with a fresh build in CI.
    """

    session = _mapping(session_policy, field="session_policy")
    deliberation = _mapping(deliberation_policy, field="deliberation_policy")
    profiles = _mapping(_value(host_profiles, "profiles", field="host_profiles"), field="host_profiles.profiles")
    chatgpt = _mapping(_value(profiles, "CHATGPT_GITHUB", field="host_profiles.profiles"), field="host_profiles.profiles.CHATGPT_GITHUB")

    entry = _mapping(_value(session, "mandatory_selected_context_entry", field="session_policy"), field="session_policy.mandatory_selected_context_entry")
    problem = _mapping(_value(session, "always_on_problem_detection_sentinel", field="session_policy"), field="session_policy.always_on_problem_detection_sentinel")
    depth = _mapping(_value(session, "always_on_execution_depth_sentinel", field="session_policy"), field="session_policy.always_on_execution_depth_sentinel")
    cognition = _mapping(_value(deliberation, "cognition_kernel", field="deliberation_policy"), field="deliberation_policy.cognition_kernel")
    modes = _mapping(_value(deliberation, "cognitive_search_modes", field="deliberation_policy"), field="deliberation_policy.cognitive_search_modes")
    closure = _mapping(_value(session, "problem_to_action_closure_gate", field="session_policy"), field="session_policy.problem_to_action_closure_gate")
    systemic_closure = _mapping(_value(closure, "systemic_repair_completeness", field="problem_to_action_closure_gate"), field="session_policy.problem_to_action_closure_gate.systemic_repair_completeness")
    mutation = _mapping(_value(session, "always_on_mutation_sentinel", field="session_policy"), field="session_policy.always_on_mutation_sentinel")
    progress = _mapping(_value(session, "inherited_session_progress_report", field="session_policy"), field="session_policy.inherited_session_progress_report")
    review = _mapping(_value(session, "controller_inheritance_review", field="session_policy"), field="session_policy.controller_inheritance_review")
    full_study = _mapping(_value(session, "full_dimension_deep_study", field="session_policy"), field="session_policy.full_dimension_deep_study")

    compiled_modes: dict[str, Any] = {}
    for mode in ("LIGHTWEIGHT", "CONTRASTIVE", "STRUCTURED"):
        item = _mapping(_value(modes, mode, field="deliberation_policy.cognitive_search_modes"), field=f"deliberation_policy.cognitive_search_modes.{mode}")
        compiled_modes[mode] = {
            "use_when": _value(item, "use_when", field=f"mode.{mode}"),
            "minimum": _value(item, "minimum", field=f"mode.{mode}"),
            "boundedness": _value(item, "boundedness", field=f"mode.{mode}"),
        }

    return {
        "schema_version": "1.2",
        "projection_role": "COMPILED_EFFECTIVE_RUNTIME_PROJECTION__NON_AUTHORITATIVE",
        "host": "CHATGPT_GITHUB",
        "source_authorities": {
            "session": "config/SESSION_INTERACTION_POLICY.json",
            "deliberation": "config/DELIBERATION_POLICY.json",
            "host": "config/HOST_PROFILES.json#profiles.CHATGPT_GITHUB",
        },
        "source_versions": {
            "session": _value(session, "policy_version", field="session_policy"),
            "deliberation": _value(deliberation, "policy_version", field="deliberation_policy"),
            "host_schema": _value(host_profiles, "schema_version", field="host_profiles"),
        },
        "assurance": {
            "semantic_signals": _value(chatgpt, "semantic_signal_assurance", field="CHATGPT_GITHUB"),
            "final_response": _value(chatgpt, "final_response_enforcement", field="CHATGPT_GITHUB"),
            "cost": _value(chatgpt, "cost_policy", field="CHATGPT_GITHUB"),
        },
        "runtime_skill": {
            "source": _value(chatgpt, "native_runtime_skill_source", field="CHATGPT_GITHUB"),
            "role": _value(chatgpt, "native_runtime_skill_role", field="CHATGPT_GITHUB"),
            "activation": _value(chatgpt, "native_runtime_skill_activation", field="CHATGPT_GITHUB"),
            "installation": _value(chatgpt, "native_runtime_skill_installation", field="CHATGPT_GITHUB"),
        },
        "turn_contract": {
            "full_dimension_deep_study": {
                "required": _value(full_study, "required", field="full_dimension_deep_study"),
                "scope": _value(full_study, "scope", field="full_dimension_deep_study"),
                "source_ref": "config/SESSION_INTERACTION_POLICY.json#full_dimension_deep_study",
                "controlled_admission_ref": _value(full_study, "controlled_admission_ref", field="full_dimension_deep_study"),
            },
            "controller_inheritance_review": {
                "required": _value(review, "required", field="controller_inheritance_review"),
                "trigger": _value(review, "trigger", field="controller_inheritance_review"),
                "coverage_rule": _value(review, "coverage_rule", field="controller_inheritance_review"),
                "evidence_admission_ref": _value(review, "evidence_admission_ref", field="controller_inheritance_review"),
            },
            "mandatory_entry": {
                "scope": _value(entry, "scope", field="mandatory_selected_context_entry"),
                "role": _value(entry, "role", field="mandatory_selected_context_entry"),
                "responsibility": _value(entry, "responsibility", field="mandatory_selected_context_entry"),
                "checks": _value(entry, "checks", field="mandatory_selected_context_entry"),
                "anti_circularity": _value(entry, "anti_circularity", field="mandatory_selected_context_entry"),
                "clear_path": _value(entry, "clear_path", field="mandatory_selected_context_entry"),
                "autonomous_goal_loop": _value(entry, "autonomous_goal_loop", field="mandatory_selected_context_entry"),
            },
            "problem_detection": {
                "scope": _value(problem, "scope", field="problem_detection"),
                "checks": _value(problem, "checks", field="problem_detection"),
            },
            "execution_depth": {
                "scope": _value(depth, "scope", field="execution_depth"),
                "responsibility": _value(depth, "responsibility", field="execution_depth"),
                "checks": _value(depth, "checks", field="execution_depth"),
                "clear_path": _value(depth, "clear_path", field="execution_depth"),
                "triggered_path": _value(depth, "triggered_path", field="execution_depth"),
            },
            "cognition": {
                "canonical_ref": "config/DELIBERATION_POLICY.json#cognition_kernel",
                "hot_path": _value(cognition, "hot_path", field="cognition_kernel"),
                "claim_rule": _value(_mapping(_value(deliberation, "cognition_case_transaction", field="deliberation_policy"), field="deliberation_policy.cognition_case_transaction"), "user_anchoring_rule", field="cognition_case_transaction"),
                "search_modes": compiled_modes,
            },
            "problem_closure": {
                "terminal_states": _value(closure, "terminal_states", field="problem_to_action_closure_gate"),
                "rule": _value(closure, "rule", field="problem_to_action_closure_gate"),
                "systemic_repair_completeness": {
                    "activation": _value(systemic_closure, "activation", field="systemic_repair_completeness"),
                    "required_evidence": _value(systemic_closure, "required_evidence", field="systemic_repair_completeness"),
                    "local_intervention_exception": _value(systemic_closure, "local_intervention_exception", field="systemic_repair_completeness"),
                    "selection_principle": _value(systemic_closure, "selection_principle", field="systemic_repair_completeness"),
                },
                "premature_action_rule": _value(closure, "premature_action_rule", field="problem_to_action_closure_gate"),
            },
            "mutation": {
                "scope": _value(mutation, "scope", field="always_on_mutation_sentinel"),
                "checks": _value(mutation, "checks", field="always_on_mutation_sentinel"),
                "production_rule": _value(mutation, "production_rule", field="always_on_mutation_sentinel"),
            },
            "final_progress": {
                "scope": _value(progress, "scope", field="inherited_session_progress_report"),
                "fields": _value(progress, "fields", field="inherited_session_progress_report"),
                "consistency_rule": _value(progress, "consistency_rule", field="inherited_session_progress_report"),
            },
        },
    }
