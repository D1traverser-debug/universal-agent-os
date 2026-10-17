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
    """Compile the installable native ChatGPT dispatcher from canonical policy owners.

    The Skill is a generated projection, not a policy owner. CI must compare the committed
    SKILL.md byte-for-byte with this function's output so hand-written normative additions
    cannot silently create a second control surface.
    """

    intent = _mapping(intent_policy, field="intent_policy")
    session = _mapping(session_policy, field="session_policy")
    deliberation = _mapping(deliberation_policy, field="deliberation_policy")
    evolution = _mapping(evolution_policy, field="evolution_policy")
    profiles = _mapping(_value(host_profiles, "profiles", field="host_profiles"), field="host_profiles.profiles")
    chatgpt = _mapping(_value(profiles, "CHATGPT_GITHUB", field="host_profiles.profiles"), field="host_profiles.profiles.CHATGPT_GITHUB")

    problem = _mapping(_value(session, "always_on_problem_detection_sentinel", field="session_policy"), field="session_policy.always_on_problem_detection_sentinel")
    closure = _mapping(_value(session, "problem_to_action_closure_gate", field="session_policy"), field="session_policy.problem_to_action_closure_gate")
    systemic = _mapping(_value(closure, "systemic_repair_completeness", field="problem_to_action_closure_gate"), field="session_policy.problem_to_action_closure_gate.systemic_repair_completeness")
    mutation = _mapping(_value(session, "always_on_mutation_sentinel", field="session_policy"), field="session_policy.always_on_mutation_sentinel")
    cognition_tx = _mapping(_value(deliberation, "cognition_case_transaction", field="deliberation_policy"), field="deliberation_policy.cognition_case_transaction")
    solution_directive = _mapping(_value(intent, "problem_solution_directive_resolution", field="intent_policy"), field="intent_policy.problem_solution_directive_resolution")
    bounded = _mapping(_value(evolution, "bounded_verification_and_promotion", field="evolution_policy"), field="evolution_policy.bounded_verification_and_promotion")

    lines: list[str] = [
        "---",
        "name: uaos-controller-runtime",
        "description: Use for UAOS controller or registered persistent Agent work, including continue/inherit/resume, user corrections, failures, repeated failures, contradictory evidence, uncertain progress, knowledge gaps, architecture/control-plane issues, system maintenance, evolution, or any repair that may be only a local patch. Recover current GitHub authority and dispatch the current canonical UAOS cognition/evolution/closure workflow. Do not use this skill as a second policy authority.",
        "---",
        "",
        "# UAOS Controller Runtime",
        "",
        "This file is a **generated, non-authoritative native ChatGPT dispatcher projection**.",
        "It does not own cognition, evolution, business rules, project state, requirements, or mutation authority. Current GitHub canonical authority always wins. Do not hand-edit normative behavior here; change the owning canonical policy and rebuild this projection.",
        "",
        "## 1. Bootstrap current authority",
        "",
        "For UAOS controller or persistent registered-Agent work, read current `main` in this order:",
        "1. `ENTRYPOINT.md`",
        "2. `CURRENT_SYSTEM.json`",
        "3. `config/NATIVE_SESSION_RUNTIME_PROFILE.json`",
        "",
        "Resolve the selected controller/domain/task from current authority. Never reconstruct current task identity from chat memory, an old assistant conclusion, a historical branch, or a retired file.",
        "",
        "## 2. Always run the lightweight problem sentinel",
        "",
        f"Scope: `{_value(problem, 'scope', field='problem_detection')}`",
        "",
        *_bullets(_strings(_value(problem, "checks", field="problem_detection"), field="problem_detection.checks")),
        "",
        "If a problem signal exists, dispatch the current canonical CognitionCase owner; this Skill's prose is not a substitute for `config/DELIBERATION_POLICY.json` or executable admission.",
        "",
        "## 3. Who said it is not causal or intervention authority",
        "",
        f"Canonical user-anchoring rule: {_value(cognition_tx, 'user_anchoring_rule', field='cognition_case_transaction')}",
        f"Problem-solution directive rule: {_value(solution_directive, 'candidate_mechanism_rule', field='problem_solution_directive_resolution')}",
        f"Anti-bypass rule: {_value(solution_directive, 'anti_bypass_rule', field='problem_solution_directive_resolution')}",
        f"Explicit mechanism requirement rule: {_value(solution_directive, 'explicit_mechanism_requirement_rule', field='problem_solution_directive_resolution')}",
        f"Conflict rule: {_value(solution_directive, 'conflict_rule', field='problem_solution_directive_resolution')}",
        "",
        "A user's outcome/constraint may be authoritative at the valid scope. A proposed remedy inside a problem statement is not automatically the selected repair merely because it is phrased as an imperative.",
        "",
        "## 4. Systemic repair completeness",
        "",
        f"Closure rule: {_value(closure, 'rule', field='problem_to_action_closure_gate')}",
        "",
        "Required evidence for systemic/material repair:",
        *_bullets(_strings(_value(systemic, "required_evidence", field="systemic_repair_completeness"), field="systemic_repair_completeness.required_evidence")),
        "",
        f"Local exception: {_value(systemic, 'local_intervention_exception', field='systemic_repair_completeness')}",
        f"Selection principle: `{_value(systemic, 'selection_principle', field='systemic_repair_completeness')}`",
        f"Premature action rule: {_value(closure, 'premature_action_rule', field='problem_to_action_closure_gate')}",
        "",
        "## 5. Evolution and bounded promotion",
        "",
        "Use the current `config/EVOLUTION_POLICY.json` / `EvolutionTransaction`; do not create another lifecycle.",
        f"Cost rule: `{_value(bounded, 'cost_rule', field='bounded_verification_and_promotion')}`",
        f"Stop condition: `{_value(bounded, 'stop_condition', field='bounded_verification_and_promotion')}`",
        "",
        "## 6. Mutation admission",
        "",
        f"Scope: `{_value(mutation, 'scope', field='always_on_mutation_sentinel')}`",
        "",
        *_bullets(_strings(_value(mutation, "checks", field="always_on_mutation_sentinel"), field="always_on_mutation_sentinel.checks")),
        "",
        f"Production rule: {_value(mutation, 'production_rule', field='always_on_mutation_sentinel')}",
        "Never use `next` or another no-op user message as the workflow clock.",
        "",
        "## 7. Native-host and cost boundary",
        "",
        f"Role: `{_value(chatgpt, 'native_runtime_skill_role', field='CHATGPT_GITHUB')}`",
        f"Activation: `{_value(chatgpt, 'native_runtime_skill_activation', field='CHATGPT_GITHUB')}`",
        f"Semantic-signal assurance: `{_value(chatgpt, 'semantic_signal_assurance', field='CHATGPT_GITHUB')}`",
        f"Final-response enforcement: `{_value(chatgpt, 'final_response_enforcement', field='CHATGPT_GITHUB')}`",
        f"Host cost policy: `{_value(chatgpt, 'cost_policy', field='CHATGPT_GITHUB')}`",
        "",
        "This Skill improves native-session activation and consistency but is not a repository-controlled pre-send/pre-tool hook. Do not claim physical complete mediation of ChatGPT product-internal messages, memory, or Custom Instructions.",
    ]
    return "\n".join(lines).rstrip() + "\n"
