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


def test_v16_adds_always_on_sentinel_without_permanent_heavy_deliberation():
    current = _json("CURRENT_SYSTEM.json")
    assert current["system_release_version"] == "2.4.4"
    assert current["status"] == "CANDIDATE_COMPLETE_MEDIATION__REGISTERED_REPOSITORY_RULESETS_PENDING"
    assert "docs/requirements/FROZEN_REQUIREMENTS_v1.6.md" in current["requirements"]
    session = _json("config/SESSION_INTERACTION_POLICY.json")
    sentinel = session["always_on_mutation_sentinel"]
    assert sentinel["required"] is True
    assert sentinel["depth_rule"] == "SENTINEL_ALWAYS_ON__DEEP_DELIBERATION_TRIGGERED_ONLY"


def test_production_promotion_uses_host_mediation_not_direct_main_cas():
    host = _json("config/HOST_PROFILES.json")["profiles"]["CHATGPT_GITHUB"]
    assert host["production_mutation_protocol"] == "CANDIDATE_BRANCH__PULL_REQUEST__PROMOTION_GATE__PROTECTED_MERGE__REREAD"
    assert host["required_promotion_check"] == "promotion-gate"
    authority = _json("config/AUTHORITY_WRITE_POLICY.json")
    assert "DIRECT_CAS_UPDATE_RETIRED" in authority["promotion_concurrency"]["production_branch"]
    assert "EVERY_REGISTERED_PRODUCTION_REPOSITORY" in authority["host_enforcement"]["policy_enforcement_requirement"]
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "name: promotion-gate" in workflow


def test_known_host_gap_prevents_resolved_status():
    readiness = _json("docs/assurance/PRODUCTION_READINESS.json")
    assert readiness["parent_core_open_work"][0]["status"] == "BLOCKED_HOST_CONFIGURATION"
    repos = readiness["verification"]["observed_host_state"]["repositories"]
    assert len(repos) == 5
    assert all(not repo["physically_mediated"] for repo in repos)
    followup = _json("state/evolution/EVO-20261014-COMPLETE-MEDIATION-HOST-ENFORCEMENT.json")
    assert followup["status"] == "BLOCKED_HOST_ENFORCEMENT"
    previous = _json("state/evolution/EVO-20261014-COGNITIVE-ADMISSION-DIRECT-DOMAIN.json")
    assert previous["status"] == "REOPENED__PHYSICAL_ENFORCEMENT_FOLLOWUP"
