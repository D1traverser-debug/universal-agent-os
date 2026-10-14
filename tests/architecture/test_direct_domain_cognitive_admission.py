import json
from pathlib import Path

import pytest

from uaos.kernel import DeliberationEvidence, DeliberationSignals, require_deliberation_admission

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def test_direct_domain_session_and_financial_identity_boundary():
    session = _json("config/SESSION_INTERACTION_POLICY.json")
    assert session["domain_session_activation"]["model"] == "DIRECT_DOMAIN_WORK_PLANE_WITH_PARENT_CONTROL_PLANE"
    entry = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    assert "normal child business turns do not traverse a live UAOS proxy" in entry
    assert "must not create a prerequisite parent article identity" in entry


def test_material_change_still_requires_deliberation_evidence():
    signals = DeliberationSignals(user_correction=True, architecture_gap=True, change_proposal=True)
    with pytest.raises(RuntimeError, match="deliberation admission blocked"):
        require_deliberation_admission(signals)
    evidence = DeliberationEvidence({
        "MICRO_DIAGNOSIS": ("incident",),
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT": ("topology",),
        "GOVERNING_ASSUMPTION_CHALLENGE": ("assumption",),
        "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH": ("external",),
        "COUNTEREXAMPLE_SEARCH": ("counterexample",),
    })
    assert require_deliberation_admission(signals, evidence).required


def test_v19_keeps_problem_research_floor_and_adds_child_product_governance():
    current = _json("CURRENT_SYSTEM.json")
    assert _version_tuple(current["system_release_version"]) >= (2, 4, 5)
    assert current["status"] == "ACTIVE_PRIMARY_CONTROLLER" or current["status"].startswith("CANDIDATE_")
    for requirement in (
        "docs/requirements/FROZEN_REQUIREMENTS_v1.7.md",
        "docs/requirements/FROZEN_REQUIREMENTS_v1.8.md",
        "docs/requirements/FROZEN_REQUIREMENTS_v1.9.md",
    ):
        assert requirement in current["requirements"]
    assert current["production_host_hardening"].startswith("OPTIONAL_DEFENSE_IN_DEPTH")
    assert "REGISTERED_CHILDREN_REFERENCE_CURRENT_UAOS_COMMON_CAPABILITIES" in current["child_inheritance_assurance"]
    assert "DOMAIN_PRODUCT_REQUIREMENTS" in current["product_governance_assurance"]
    assert "ARCHITECTURE" in current["product_governance_assurance"]

    common = _json("config/COMMON_CAPABILITIES.json")
    assert _version_tuple(common["contract_version"]) >= (1, 5, 0)
    by_id = {item["capability_id"]: item for item in common["capabilities"]}
    assert "product_requirements_and_architecture_governance" in by_id
    cognition = by_id["adaptive_deliberation_and_parent_guidance"]
    assert cognition["problem_response_floor"] == [
        "MICRO_DIAGNOSIS",
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT",
        "GOVERNING_ASSUMPTION_CHALLENGE",
        "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH",
    ]
    cognition_rules = "\n".join(cognition["rules"]).lower()
    assert "familiarity is not a waiver" in cognition_rules
    assert "problem size changes" in cognition_rules
    assert "research must affect or validate" in cognition_rules


def test_material_production_workflow_uses_candidate_validation_without_requiring_remote_ruleset():
    host = _json("config/HOST_PROFILES.json")["profiles"]["CHATGPT_GITHUB"]
    assert host["production_mutation_protocol"] == "CANDIDATE_BRANCH__PULL_REQUEST__OWNER_APPROPRIATE_CHECKS__CONTROLLED_MERGE_OR_UPDATE__REREAD"
    assert host["uaos_promotion_check"] == "promotion-gate"
    assert host["production_ref_enforcement"].startswith("OPTIONAL_DEFENSE_IN_DEPTH")

    authority = _json("config/AUTHORITY_WRITE_POLICY.json")
    assert authority["optional_host_hardening"]["classification"] == "DEFENSE_IN_DEPTH"
    assert authority["physical_complete_mediation_assurance"]["claim_is_optional"] is True
    assert "CANDIDATE_BRANCH" in authority["autonomous_maintenance_baseline"]["normal_material_github_path"]

    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "name: promotion-gate" in workflow


def test_ruleset_absence_is_not_parent_core_blocker_but_physical_claim_remains_bounded():
    readiness = _json("docs/assurance/PRODUCTION_READINESS.json")
    assert readiness["parent_core_open_work"] == []
    assert readiness["optional_host_hardening"][0]["status"] == "OPTIONAL_NOT_CONFIGURED"
    assert readiness["verification"]["observed_host_state"]["interpretation"] == "OPTIONAL_DEFENSE_IN_DEPTH_GAP__NOT_BASELINE_RELEASE_BLOCKER"

    followup = _json("state/evolution/EVO-20261014-COMPLETE-MEDIATION-HOST-ENFORCEMENT.json")
    assert followup["status"] == "RETIRED__OVERCONSTRAINED_ASSURANCE_GOAL"
    previous = _json("state/evolution/EVO-20261014-COGNITIVE-ADMISSION-DIRECT-DOMAIN.json")
    assert previous["status"] == "RESOLVED"


def test_physical_non_bypassability_still_requires_evidence_if_claimed():
    authority = _json("config/AUTHORITY_WRITE_POLICY.json")
    physical = authority["physical_complete_mediation_assurance"]
    assert physical["when_claimed"] == "REMOTE_NON_BYPASSABLE_ENFORCEMENT_EVIDENCE_IS_MANDATORY"
    assert physical["without_evidence"] == "DO_NOT_CLAIM_PHYSICAL_COMPLETE_MEDIATION"
