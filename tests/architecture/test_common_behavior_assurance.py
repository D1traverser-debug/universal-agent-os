import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def test_financial_parent_guidance_is_resolved_as_common_outcomes_not_financial_shape():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    decisions = policy["parent_decisions"]

    assert decisions["PROACTIVE_RESOLUTION_GAP"].startswith("PROMOTE_COMMON_OUTCOME_SEMANTICS")
    assert decisions["EVOLUTION_HISTORY_INTERFACE"].startswith("REQUIRE_ONE_CANONICAL_CHILD_EVOLUTION_EVIDENCE_ENTRYPOINT")
    assert decisions["VERSION_METADATA_DRIFT"].startswith("RESOLVED_BY_EXISTING_PARENT_RELEASE_SYNC_INVARIANT")
    assert decisions["INHERITANCE_BEHAVIOR_VS_DECLARATION"].startswith("PROMOTE_COMMON_ASSURANCE_RULE")
    assert decisions["DECLARATION_TO_OPERATION_GAP"].startswith("PROMOTE_AS_UMBRELLA_COMMON_FAILURE_CLASS")
    assert "RECOMMENDATION_ONLY" in decisions["PROBLEM_TO_ACTION_CLOSURE_GAP"]
    assert "ROOT_SCOPE" in decisions["PREMATURE_REPAIR_BEFORE_ROOT_SCOPE"]

    assert _version_tuple(policy["contract_version"]) >= (1, 3, 0)
    assert policy["observable_inheritance_assurance"]["no_uniform_probe_implementation"] is True
    assert policy["adoption_and_compatibility"]["no_parent_microscheduler"] is True
    assert "FORCE_FINANCIAL_WRITINGS_EXACT_RECOVERY_ORDER_ON_OTHER_DOMAINS" in policy["recover_before_user_escalation"]["forbidden"]


def test_problem_cognition_transaction_prevents_user_external_or_first_fix_anchoring():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    transaction = policy["problem_cognition_action_transaction"]
    rules = "\n".join(transaction["rules"]).lower()
    assert "user correction" in rules
    assert "external skill" in rules
    assert "first available edit" in rules
    assert "at least two layers" in rules
    assert "architecture/upstream" in rules
    assert "evolution/learning disposition" in rules
    assert transaction["ordered_stages"].index("ROOT_SCOPE_ADMISSION") < transaction["ordered_stages"].index("REPAIR_REDESIGN_OR_NO_CHANGE")


def test_declaration_is_not_operational_proof_and_user_escalation_has_safe_boundary():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    assurance = policy["observable_inheritance_assurance"]
    recovery = policy["recover_before_user_escalation"]

    assert assurance["principle"] == "DECLARED_COMMON_CAPABILITY_IS_NOT_OPERATIONAL_BEHAVIOR_PROOF"
    assert assurance["default_assurance_when_only_declared"] == "DECLARED_ONLY"
    joined = "\n".join(assurance["operational_claim_requires"]).lower()
    assert "invocation path" in joined
    assert "evidence" in joined
    assert "current-enough" in joined

    escalation = "\n".join(recovery["user_escalation_is_required_or_preferred_when"]).lower()
    assert "authorization" in escalation
    assert "materially different outcomes" in escalation
    assert "genuinely unavailable" in escalation


def test_problem_to_action_closure_is_downstream_of_cognitive_admission():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    closure = policy["problem_to_action_closure"]
    assert closure["executable_ref"] == "src/uaos/kernel/problem_closure.py"
    assert closure["terminal_states"] == ["REPAIR_EXECUTED", "BLOCKED_WITH_REASON", "NO_CHANGE_WITH_EVIDENCE"]
    repair_rule = closure["repair_now_rule"].lower()
    assert "root-scope cognition" in repair_rule
    assert "evolution disposition" in repair_rule
    assert "must attempt the repair" in repair_rule
    assert "before finalizing" in repair_rule
    assert "before root-scope admission" in closure["premature_action_rule"].lower()


def test_child_evolution_interface_standardizes_discoverability_not_internal_state_machine():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    interface = policy["canonical_child_evolution_evidence_interface"]

    assert interface["decision"] == "MINIMAL_CANONICAL_ENTRYPOINT_PLUS_OWNER_NATIVE_CAUSAL_HISTORY"
    assert "owner/domain identity" in interface["minimum_logical_fields"]
    assert "open parent-guidance references" in interface["minimum_logical_fields"]
    assert "owner-native representation" in interface["format_rule"]
    assert "child-owned" in interface["ownership_rule"]


def test_causal_problem_history_preserves_root_scope_and_learning_without_forcing_heavy_logs():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    history = policy["causal_problem_history_preservation"]

    assert "EVOLUTION_RELEVANT_OR_MATERIAL_DETECTED_PROBLEM" in history["scope"]
    semantics = "\n".join(history["minimum_semantics_when_applicable"]).lower()
    assert "symptom" in semantics
    assert "micro diagnosis" in semantics
    assert "macro goal/topology" in semantics
    assert "competing hypotheses" in semantics
    assert "root-scope receipt" in semantics
    assert "verification" in semantics
    assert "remaining unknowns" in semantics
    assert "small local defects" in history["compression_rule"].lower()
    assert "must not be silently rewritten out of history" in history["failed_path_rule"].lower()


def test_binding_and_current_system_reference_common_behavior_assurance():
    binding = _json("config/BINDING_POLICY.json")
    current = _json("CURRENT_SYSTEM.json")

    assert binding["common_behavior_assurance_policy"] == "config/COMMON_BEHAVIOR_ASSURANCE.json"
    assert "DECLARATION_OF_COMMON_CAPABILITY_INHERITANCE_IS_NOT_OPERATIONAL_PROOF" in binding["operational_behavior_assurance_rule"]
    assert "PROPORTIONATE_LAWFUL_RECOVERY" in binding["recover_before_user_escalation_rule"]
    assert "ROOT_SCOPE_ADMISSION" in binding["problem_cognition_action_rule"]
    assert "ONLY_AFTER_ROOT_SCOPE_ADMISSION" in binding["problem_action_closure_rule"]
    assert "ONE_CANONICAL_OWNER_NATIVE_EVIDENCE_ENTRYPOINT" in binding["evolution_evidence_interface_rule"]
    assert "EVOLUTION_RELEVANT_OR_MATERIAL_DETECTED_PROBLEM" in binding["causal_problem_history_rule"]
    assert binding["domain_health_escalation_policy"] == "config/DOMAIN_HEALTH_ESCALATION_POLICY.json"

    assert current["common_behavior_assurance"] == "config/COMMON_BEHAVIOR_ASSURANCE.json"
    assert current["domain_health_escalation_policy"] == "config/DOMAIN_HEALTH_ESCALATION_POLICY.json"
    assert current["domain_health_index"] == "state/DOMAIN_HEALTH_INDEX.json"
    assert "COMMON_BEHAVIOR_ASSURANCE_1_3" in current["common_behavior_assurance_contract"]
    assert "CAUSAL_PROBLEM_HISTORY" in current["common_behavior_assurance_contract"]
    assert "ROOT_SCOPE_ADMISSION" in current["problem_action_closure_assurance"]


def test_child_observations_remain_current_evidence_not_parent_authority():
    current = _json("CURRENT_SYSTEM.json")
    health = _json("state/DOMAIN_HEALTH_INDEX.json")
    verification = current["financial_child_production_verification"]

    assert current["financial_binding_assurance"].startswith("CURRENT_CHILD_OBSERVATION_IN_state/DOMAIN_HEALTH_INDEX.json")
    assert verification["observation_role"] == "CURRENT_CHILD_HEAD_OBSERVATION__NOT_IMMUTABLE_RELEASE_CERTIFICATE"
    assert health["domains"]["financial_writing"]["observed_main_commit"] == verification["current_main_commit"]
    assert health["domains"]["financial_writing"]["observed_profile_version"] == verification["profile_version"]
    assert _version_tuple(verification["common_behavior_assurance_min"]) >= (1, 3, 0)
    assert verification["result"] == "PASS"


def test_novel_parent_observation_is_current_and_owner_native():
    current = _json("CURRENT_SYSTEM.json")
    health = _json("state/DOMAIN_HEALTH_INDEX.json")
    verification = current["novel_child_production_verification"]
    assert verification["profile_version"] >= 6
    assert verification["profile_version"] == health["domains"]["novel"]["observed_profile_version"]
    assert _version_tuple(verification["common_behavior_assurance_min"]) >= (1, 3, 0)
    assert verification["active_rulebook_version"] == "2.5-github"
    assert verification["result"] == "PASS"
    assert "NEXT_LINE_3914" in verification["business_cursor_preserved"]


def test_version_metadata_drift_remains_mechanically_guarded():
    current = _json("CURRENT_SYSTEM.json")
    entrypoint = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    assert f"System release: `{current['system_release_version']}`" in entrypoint
