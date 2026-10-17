from __future__ import annotations

from typing import Any, Mapping, Sequence


class NativeRuntimeSkillError(ValueError):
    """Raised when canonical authority cannot produce the native runtime Skill projection."""


def _mapping(value: object, *, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise NativeRuntimeSkillError(f"{field} must be a mapping")
    return value


def _value(mapping: Mapping[str, Any], key: str, *, field: str) -> Any:
    if key not in mapping:
        raise NativeRuntimeSkillError(f"missing {field}.{key}")
    return mapping[key]


def _strings(value: object, *, field: str) -> Sequence[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise NativeRuntimeSkillError(f"{field} must be a sequence")
    items = list(value)
    if not all(isinstance(item, str) for item in items):
        raise NativeRuntimeSkillError(f"{field} must contain strings")
    return items


def _bullets(items: Sequence[str]) -> list[str]:
    return [f"- {item}" for item in items]


def build_native_runtime_skill(
    *,
    intent_policy: Mapping[str, Any],
    session_policy: Mapping[str, Any],
    deliberation_policy: Mapping[str, Any],
    evolution_policy: Mapping[str, Any],
    host_profiles: Mapping[str, Any],
) -> str:
    """Compile the installable native ChatGPT dispatcher from canonical policy owners."""

    intent = _mapping(intent_policy, field="intent_policy")
    session = _mapping(session_policy, field="session_policy")
    _mapping(deliberation_policy, field="deliberation_policy")
    evolution = _mapping(evolution_policy, field="evolution_policy")
    profiles = _mapping(_value(host_profiles, "profiles", field="host_profiles"), field="host_profiles.profiles")
    chatgpt = _mapping(_value(profiles, "CHATGPT_GITHUB", field="host_profiles.profiles"), field="host_profiles.profiles.CHATGPT_GITHUB")

    entry = _mapping(_value(session, "mandatory_selected_context_entry", field="session_policy"), field="session_policy.mandatory_selected_context_entry")
    problem = _mapping(_value(session, "always_on_problem_detection_sentinel", field="session_policy"), field="session_policy.always_on_problem_detection_sentinel")
    depth = _mapping(_value(session, "always_on_execution_depth_sentinel", field="session_policy"), field="session_policy.always_on_execution_depth_sentinel")
    closure = _mapping(_value(session, "problem_to_action_closure_gate", field="session_policy"), field="session_policy.problem_to_action_closure_gate")
    systemic = _mapping(_value(closure, "systemic_repair_completeness", field="problem_to_action_closure_gate"), field="session_policy.problem_to_action_closure_gate.systemic_repair_completeness")
    mutation = _mapping(_value(session, "always_on_mutation_sentinel", field="session_policy"), field="session_policy.always_on_mutation_sentinel")
    solution_directive = _mapping(_value(intent, "problem_solution_directive_resolution", field="intent_policy"), field="intent_policy.problem_solution_directive_resolution")
    bounded = _mapping(_value(evolution, "bounded_verification_and_promotion", field="evolution_policy"), field="evolution_policy.bounded_verification_and_promotion")

    lines: list[str] = [
        "---",
        "name: uaos-controller-runtime",
        "description: Runtime dispatcher for selected UAOS or registered persistent-Agent work. Use after context selection and on bootstrap/resume to recover current authority, run the mandatory lightweight entry, and dispatch any needed cognition, comprehensive knowledge acquisition, evolution, mutation, or durable continuation to canonical UAOS owners. Non-authoritative.",
        "---",
        "",
        "# UAOS Controller Runtime",
        "",
        "This is a **generated, non-authoritative runtime dispatcher projection**. It does not own cognition, research, evolution, requirements, business state, or mutation authority. Change canonical policy, not this file.",
        "",
        "## 1. Mandatory selected-context entry",
        "",
        f"Scope: `{_value(entry, 'scope', field='mandatory_selected_context_entry')}`",
        f"Responsibility: {_value(entry, 'responsibility', field='mandatory_selected_context_entry')}",
        f"Anti-circularity: {_value(entry, 'anti_circularity', field='mandatory_selected_context_entry')}",
        f"Autonomous continuation: `{_value(entry, 'autonomous_goal_loop', field='mandatory_selected_context_entry')}`",
        f"Blocker rule: {_value(closure, 'blocker_rule', field='problem_to_action_closure_gate')}",
        "",
        *_bullets(_strings(_value(entry, "checks", field="mandatory_selected_context_entry"), field="mandatory_selected_context_entry.checks")),
        "",
        "Entry is mandatory; escalation is adaptive. A simple/familiar turn should pass through without ceremonial cognition or research.",
        "",
        "## 2. Recover current authority",
        "",
        "For UAOS controller or persistent registered-Agent work, read current `main` starting from `ENTRYPOINT.md` and `CURRENT_SYSTEM.json`, then use `config/NATIVE_SESSION_RUNTIME_PROFILE.json` for the selected-context hot path. Reread exact owner authority when the current action requires it.",
        "Never reconstruct current task identity or authoritative state from chat memory, prior assistant conclusions, historical branches, or retired files.",
        "",
        "## 3. Route adaptively",
        "",
        f"Problem sentinel scope: `{_value(problem, 'scope', field='problem_detection')}`",
        "If a problem signal is detected, dispatch the canonical CognitionCase before selecting a repair/no-change outcome.",
        f"Execution-depth responsibility: {_value(depth, 'responsibility', field='execution_depth')}",
        "When comprehensive knowledge acquisition is required, use the current Deep Task + `src/uaos/kernel/problem_space.py#require_knowledge_acquisition_admission` evidence path. Narrow known lookups remain lightweight.",
        "This Skill routes to canonical owners; it is not a second cognition, research, or evolution state machine.",
        "",
        "## 4. Keep claims and requirements distinct",
        "",
        f"Requirement rule: {_value(solution_directive, 'outcome_constraint_rule', field='problem_solution_directive_resolution')}",
        "Causal explanations, framework choices, solution proposals, and action recommendations from any source remain candidates until current evidence admits them at the required risk/depth level.",
        "A remedy proposed inside a problem statement remains an ActionCandidate until current cognition/evidence selects it; imperative wording does not change that epistemic role.",
        f"Independent-mechanism requirement rule: {_value(solution_directive, 'explicit_mechanism_requirement_rule', field='problem_solution_directive_resolution')}",
        "",
        "## 5. Execute toward the governing objective",
        "",
        f"Problem closure: {_value(closure, 'rule', field='problem_to_action_closure_gate')}",
        f"Systemic selection: `{_value(systemic, 'selection_principle', field='systemic_repair_completeness')}`",
        "Verification and validation must match the admitted objective/intervention; do not stop at a plan when authorized executable work remains and no genuine blocker exists.",
        "",
        "## 6. Evolution and mutation",
        "",
        "Use the current `config/EVOLUTION_POLICY.json` / `EvolutionTransaction`; durable learning does not create another lifecycle.",
        f"Evolution cost rule: `{_value(bounded, 'cost_rule', field='bounded_verification_and_promotion')}`",
        f"Evolution stop condition: `{_value(bounded, 'stop_condition', field='bounded_verification_and_promotion')}`",
        f"Mutation scope: `{_value(mutation, 'scope', field='always_on_mutation_sentinel')}`",
        f"Production mutation: {_value(mutation, 'production_rule', field='always_on_mutation_sentinel')}",
        "",
        "## 7. Host boundary",
        "",
        f"Role: `{_value(chatgpt, 'native_runtime_skill_role', field='CHATGPT_GITHUB')}`",
        f"Activation: `{_value(chatgpt, 'native_runtime_skill_activation', field='CHATGPT_GITHUB')}`",
        f"Semantic-signal assurance: `{_value(chatgpt, 'semantic_signal_assurance', field='CHATGPT_GITHUB')}`",
        f"Final-response enforcement: `{_value(chatgpt, 'final_response_enforcement', field='CHATGPT_GITHUB')}`",
        f"Host cost policy: `{_value(chatgpt, 'cost_policy', field='CHATGPT_GITHUB')}`",
        "",
        "This Skill improves native routing consistency but is not a repository-controlled ChatGPT pre-send/pre-tool hook. Do not claim physical complete mediation of product-internal messages, memory, or Custom Instructions.",
    ]
    return "\n".join(lines).rstrip() + "\n"