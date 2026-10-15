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


def test_child_evolution_interface_standardizes_discoverability_not_internal_state_machine():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    interface = policy["canonical_child_evolution_evidence_interface"]

    assert interface["decision"] == "MINIMAL_CANONICAL_ENTRYPOINT_ONLY"
    assert "owner/domain identity" in interface["minimum_logical_fields"]
    assert "open parent-guidance references" in interface["minimum_logical_fields"]
    assert "owner-native representation" in interface["format_rule"]
    assert "child-owned" in interface["ownership_rule"]


def test_binding_and_current_system_reference_common_behavior_assurance():
    binding = _json("config/BINDING_POLICY.json")
    current = _json("CURRENT_SYSTEM.json")

    assert binding["common_behavior_assurance_policy"] == "config/COMMON_BEHAVIOR_ASSURANCE.json"
    assert "DECLARATION_OF_COMMON_CAPABILITY_INHERITANCE_IS_NOT_OPERATIONAL_PROOF" in binding["operational_behavior_assurance_rule"]
    assert "PROPORTIONATE_LAWFUL_RECOVERY" in binding["recover_before_user_escalation_rule"]
    assert "ONE_CANONICAL_OWNER_NATIVE_EVIDENCE_ENTRYPOINT" in binding["evolution_evidence_interface_rule"]

    assert current["common_behavior_assurance"] == "config/COMMON_BEHAVIOR_ASSURANCE.json"
    assert "DECLARATION_NOT_OPERATIONAL_PROOF" in current["common_behavior_assurance_contract"]


def test_version_metadata_drift_remains_mechanically_guarded():
    current = _json("CURRENT_SYSTEM.json")
    entrypoint = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")

    assert f"System release: `{current['system_release_version']}`" in entrypoint
