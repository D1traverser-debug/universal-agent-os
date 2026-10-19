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
    progress = _mapping(_value(session, "inherited_session_progress_report", field="session_policy"), field="session_policy.inherited_session_progress_report")
    progress_fields = _strings(_value(progress, "fields", field="inherited_session_progress_report"), field="inherited_session_progress_report.fields")
    solution_directive = _mapping(_value(intent, "problem_solution_directive_resolution", field="intent_policy"), field="intent_policy.problem_solution_directive_resolution")
    bounded = _mapping(_value(evolution, "bounded_verification_and_promotion", field="evolution_policy"), field="evolution_policy.bounded_verification_and_promotion")

    expected_progress_labels = {
        "current_agent": "当前 Agent",
        "current_scope_or_task": "当前任务",
        "authority_context": "Authority",
        "status": "状态",
        "current_stage": "当前阶段",
        "next_action_or_blocker": "下一动作",
        "evolution_state_when_triggered_or_NO_EVOLUTION_TRIGGER": "Evolution",
        "deliberation_state_when_triggered_or_NOT_TRIGGERED": "Deliberation",
        "version_identity": "版本",
        "progress_timestamp": "进度时间",
    }
    if tuple(progress_fields) != tuple(expected_progress_labels):
        raise NativeRuntimeSkillError("inherited session Progress field contract drift")
    if _value(progress, "required", field="inherited_session_progress_report") is not True:
        raise NativeRuntimeSkillError("selected-context Progress must remain mandatory")

    lines: list[str] = [
        "---",
        "name: uaos-controller-runtime",
        "description: Runtime dispatcher for selected UAOS or registered persistent-Agent work: mandatory lightweight entry and evidence-based routing to canonical UAOS owners. Non-authoritative.",
        "---",
        "",
        "# UAOS Controller Runtime",
        "",
        "Generated, non-authoritative runtime dispatcher; it does not own cognition, research, evolution, requirements, business state or mutations. Canonical policies, task state and evolution records own the details.",
        "",
        "## 1. Mandatory selected-context entry",
        "",
        f"Scope: `{_value(entry, 'scope', field='mandatory_selected_context_entry')}`",
        f"Agent self-correction target: {_value(solution_directive, 'correction_target_rule', field='problem_solution_directive_resolution')}",
        f"Intervention-to-outcome alignment: {_value(solution_directive, 'intervention_outcome_alignment_rule', field='problem_solution_directive_resolution')}",
        "Entry is mandatory; escalation is adaptive. Complexity, unknown knowledge, architecture/systemic status and uncertainty are not prerequisites for entering this sentinel; they are decisions made after entry.",
        "Identify the real governing outcome, independently notice errors in your own current claims, test competing causes and target the capability actually failing, not unrelated work.",
        "Autonomous continuation: while admitted work remains and no genuine blocker exists, choose the next evidenced action, execute, verify, reassess, continue.",
        f"Blocker rule: {_value(closure, 'blocker_rule', field='problem_to_action_closure_gate')}",
        "- adaptively route current observations to canonical CognitionCase, Deep Task, knowledge acquisition or EvolutionTransaction when evidence requires; do not duplicate any of them.",
        "- actively challenge causal claims AND the governing rules, architecture and learning method itself; do not accept user or model explanations as fact without evidence.",
        "- persist exact continuation without waiting for a user reminder; recheck authority and actual tool outcomes.",
        "",
        "## 2. Recover current authority",
        "",
        "Cold start / inheritance: reread `ENTRYPOINT.md`, `CURRENT_SYSTEM.json` and `state/TASK_INDEX.json` from current GitHub main. Continuing an already selected task: reread its exact `state/tasks/*` owner first; only expand to affected policies, history and child owners as required. Do not reload every long policy every turn.",
        "Current main is authority, not prior assistant answers, memory, a cached Skill or historical research. The four latest studies are not the whole knowledge inventory. For broad learning use relevant source-owner catalogs and record missing coverage.",
        "",
        "## 3. Route adaptively",
        "",
        "Every selected turn derives its own depth. For suspected errors, use `src/uaos/kernel/cognition_case.py` plus independent falsification; for unfamiliar broad research use `src/uaos/kernel/problem_space.py` with source coverage; for systemic/multi-step work use `src/uaos/kernel/deep_task.py`. Execute under the original owner; outcome, not policy wording, determines success.",
        "Only current tool/host evidence proves an action happened. Keep user requirements distinct from proposed fixes and never replace an actual problem with a convenient proxy.",
        "",
        "## 4. Keep claims and requirements distinct",
        "",
        f"Requirement rule: {_value(solution_directive, 'outcome_constraint_rule', field='problem_solution_directive_resolution')}",
        "Causal explanations, framework choices, solution proposals and action recommendations from any source remain candidates until current evidence admits them.",
        "A remedy proposed inside a problem statement remains an ActionCandidate regardless of imperative wording.",
        f"Independent-mechanism requirement rule: {_value(solution_directive, 'explicit_mechanism_requirement_rule', field='problem_solution_directive_resolution')}",
        "",
        "## 5. Execute toward the governing objective",
        "",
        f"Problem closure: {_value(closure, 'rule', field='problem_to_action_closure_gate')}",
        "Repair completion requires observed action and goal-fit validation, not just a passing PR or local CI. If one cause persists after a fix, reopen diagnosis; keep normal domain work active.",
        "",
        "## 6. Evolution and mutation",
        "",
        "Use canonical `config/EVOLUTION_POLICY.json` and `EvolutionTransaction`, not another knowledge/governance lifecycle. For material GitHub changes use candidate branch → PR → owner tests → merge → production reread. Respect `config/AUTHORITY_WRITE_POLICY.json` and the selected authority. No separately paid tools without approval.",
        "",
        "## 7. Mandatory final Progress and self-observation",
        "",
        f"Scope: `{_value(progress, 'scope', field='inherited_session_progress_report')}`",
        f"Placement: `{_value(progress, 'placement', field='inherited_session_progress_report')}`",
        "Before releasing each selected-context final reply, inspect the actual proposed response (including the assistant's own output) for unsupported closure, unresolved current issues, missing fields or stale authority. Correct before emit; cite real task state.",
        "Append all ten fields at the end of the final response, one labeled line each, with actual values:",
        f"- {expected_progress_labels['current_agent']}: current_agent",
        f"- {expected_progress_labels['current_scope_or_task']}: current_scope_or_task",
        f"- {expected_progress_labels['authority_context']}: authority_context",
        f"- {expected_progress_labels['status']}: status",
        f"- {expected_progress_labels['current_stage']}: current_stage",
        f"- {expected_progress_labels['next_action_or_blocker']}: next_action_or_blocker",
        f"- {expected_progress_labels['evolution_state_when_triggered_or_NO_EVOLUTION_TRIGGER']}: evolution_state_when_triggered_or_NO_EVOLUTION_TRIGGER",
        f"- {expected_progress_labels['deliberation_state_when_triggered_or_NOT_TRIGGERED']}: deliberation_state_when_triggered_or_NOT_TRIGGERED",
        f"- {expected_progress_labels['version_identity']}: version_identity",
        f"- {expected_progress_labels['progress_timestamp']}: progress_timestamp",
        f"Timestamp rule: {_value(progress, 'timestamp_rule', field='inherited_session_progress_report')}",
        f"Timezone/display: {_value(progress, 'timestamp_display_format', field='inherited_session_progress_report')}",
        f"Evolution rule: {_value(progress, 'evolution_rule', field='inherited_session_progress_report')}",
        f"Deliberation rule: {_value(progress, 'deliberation_rule', field='inherited_session_progress_report')}",
        "A self-review without a trusted host trace is not independent native enforcement. Missing Progress is a behavioral failure, even if CI passes.",
        "",
        "## 8. Host boundary",
        "",
        "Native ChatGPT + raw GitHub connector calls are not intercepted by this repository's Python finalization code. SDK-controlled user-visible output can be gated only when that adapter is actually invoked. Do not claim account Skill installation or native behavior from GitHub changes alone.",
    ]
    return "\n".join(lines).rstrip() + "\n"