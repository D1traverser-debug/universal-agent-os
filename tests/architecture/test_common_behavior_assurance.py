import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_parent_guidance_is_resolved_as_common_outcomes_not_financial_shape():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    decisions = policy["parent_decisions"]

    assert decisions["PROACTIVE_RESOLUTION_GAP"].startswith("PROMOTE_COMMON_OUTCOME_SEMANTICS")
    assert decisions["EVOLUTION_HISTORY_INTERFACE"].startswith("REQUIRE_ONE_CANONICAL_CHILD_EVOLUTION_EVIDENCE_ENTRYPOINT")
    assert decisions["VERSION_METADATA_DRIFT"].startswith("RESOLVED_BY_EXISTING_PARENT_RELEASE_SYNC_INVARIANT")
    assert decisions["INHERITANCE_BEHAVIOR_VS_DECLARATION"].startswith("PROMOTE_COMMON_ASSURANCE_RULE")
    assert decisions["DECLARATION_TO_OPERATION_GAP"].startswith("PROMOTE_AS_UMBRELLA_COMMON_FAILURE_CLASS")
    assert "RECOMMENDATION_ONLY" in decisions["PROBLEM_TO_ACTION_CLOSURE_GAP"]

    assert policy["contract_version"] == "1.2.0"
    assert policy["observable_inheritance_assurance"]["no_uniform_probe_implementation"] is True
    assert policy["adoption_and_compatibility"]["no_parent_microscheduler"] is True
    assert "FORCE_FINANCIAL_WRITINGS_EXACT_RECOVERY_ORDER_ON_OTHER_DOMAINS" in policy["recover_before_user_escalation"]["forbidden"]


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


def test_problem_to_action_closure_forbids_recommendation_only_when_repair_is_available():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    closure = policy["problem_to_action_closure"]
    assert closure["executable_ref"] == "src/uaos/kernel/problem_closure.py"
    assert closure["terminal_states"] == ["REPAIR_EXECUTED", "BLOCKED_WITH_REASON", "NO_CHANGE_WITH_EVIDENCE"]
    assert "must be attempted before finalizing" in closure["repair_now_rule"]
    assert "physical interception" in closure["assurance_boundary"]


def test_child_evolution_interface_standardizes_discoverability_not_internal_state_machine():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    interface = policy["canonical_child_evolution_evidence_interface"]

    assert interface["decision"] == "MINIMAL_CANONICAL_ENTRYPOINT_PLUS_OWNER_NATIVE_CAUSAL_HISTORY"
    assert "owner/domain identity" in interface["minimum_logical_fields"]
    assert "open parent-guidance references" in interface["minimum_logical_fields"]
    assert "owner-native representation" in interface["format_rule"]
    assert "child-owned" in interface["ownership_rule"]


def test_causal_problem_history_preserves_learning_without_forcing_heavyweight_logs():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    history = policy["causal_problem_history_preservation"]

    assert "EVOLUTION_RELEVANT_OR_MATERIAL_DETECTED_PROBLEM" in history["scope"]
    semantics = "\n".join(history["minimum_semantics_when_applicable"]).lower()
    assert "symptom" in semantics
    assert "micro diagnosis" in semantics
    assert "macro goal/topology" in semantics
    assert "rejected paths" in semantics
    assert "verification" in semantics
    assert "remaining unknowns" in semantics
    assert "small local defects" in history["compression_rule"].lower()
    assert "must not be silently rewritten out of history" in history["failed_path_rule"].lower()
    assert "not a universal journal file" in history["format_and_storage_rule"].lower()


def test_binding_and_current_system_reference_common_behavior_assurance():
    binding = _json("config/BINDING_POLICY.json")
    current = _json("CURRENT_SYSTEM.json")

    assert binding["common_behavior_assurance_policy"] == "config/COMMON_BEHAVIOR_ASSURANCE.json"
    assert "DECLARATION_OF_COMMON_CAPABILITY_INHERITANCE_IS_NOT_OPERATIONAL_PROOF" in binding["operational_behavior_assurance_rule"]
    assert "PROPORTIONATE_LAWFUL_RECOVERY" in binding["recover_before_user_escalation_rule"]
    assert "MUST_ATTEMPT_THE_REPAIR_BEFORE_FINALIZING" in binding["problem_action_closure_rule"]
    assert "ONE_CANONICAL_OWNER_NATIVE_EVIDENCE_ENTRYPOINT" in binding["evolution_evidence_interface_rule"]
    assert "EVOLUTION_RELEVANT_OR_MATERIAL_DETECTED_PROBLEM" in binding["causal_problem_history_rule"]

    assert current["common_behavior_assurance"] == "config/COMMON_BEHAVIOR_ASSURANCE.json"
    assert "COMMON_BEHAVIOR_ASSURANCE_1_2" in current["common_behavior_assurance_contract"]
    assert "CAUSAL_PROBLEM_HISTORY" in current["common_behavior_assurance_contract"]
    assert "PROBLEM_TO_ACTION_CLOSURE" in current["common_behavior_assurance_contract"]
    assert "RECOMMENDATION_ONLY_FORBIDDEN" in current["problem_action_closure_assurance"]


def test_financial_parent_observation_is_current_and_evidence_bounded():
    current = _json("CURRENT_SYSTEM.json")
    verification = current["financial_child_production_verification"]

    assert current["financial_binding_assurance"].startswith("FINANCIAL_0_9_1_PRODUCTION_VERIFIED")
    assert verification["release"] == "0.9.1"
    assert verification["profile_version"] == 16
    assert verification["main_commit"] == "3090a50d6be938947b1073310d5e290cd67cafbc"
    assert verification["production_ci_number"] == 1033
    assert verification["result"] == "PASS"


def test_version_metadata_drift_remains_mechanically_guarded():
    current = _json("CURRENT_SYSTEM.json")
    entrypoint = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")

    assert f"System release: `{current['system_release_version']}`" in entrypoint
