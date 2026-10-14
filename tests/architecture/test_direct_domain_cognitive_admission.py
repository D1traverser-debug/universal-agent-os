import json
from pathlib import Path

import pytest

from uaos.kernel import DeliberationEvidence, DeliberationSignals, require_deliberation_admission

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


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


def test_v18_keeps_always_on_sentinel_and_problem_research_floor_without_ruleset_blocker():
    current = _json("CURRENT_SYSTEM.json")
    assert current["system_release_version"] == "2.4.4"
    assert current["status"] in {
        "CANDIDATE_AUTONOMOUS_MAINTENANCE_BASELINE__FINAL_VALIDATION_PENDING",
        "ACTIVE_PRIMARY_CONTROLLER",
    }
    assert "docs/requirements/FROZEN_REQUIREMENTS_v1.7.md" in current["requirements"]
    assert "docs/requirements/FROZEN_REQUIREMENTS_v1.8.md" in current["requirements"]
    assert current["production_host_hardening"].startswith("OPTIONAL_DEFENSE_IN_DEPTH")

    session = _json("config/SESSION_INTERACTION_POLICY.json")
    sentinel = session["always_on_mutation_sentinel"]
    assert sentinel["required"] is True
    assert sentinel["depth_rule"] == "SENTINEL_ALWAYS_ON__DEEP_DELIBERATION_TRIGGERED_ONLY"
    assert "optional defense-in-depth" in sentinel["production_rule"]


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
