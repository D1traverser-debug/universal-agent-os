import json
from pathlib import Path

import pytest

from uaos.kernel import (
    DeliberationEvidence,
    DeliberationSignals,
    require_deliberation_admission,
)

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_registered_child_session_is_direct_work_plane_not_parent_business_gateway():
    policy = _json("config/SESSION_INTERACTION_POLICY.json")
    activation = policy["domain_session_activation"]

    assert activation["model"] == "DIRECT_DOMAIN_WORK_PLANE_WITH_PARENT_CONTROL_PLANE"
    rules = "\n".join(activation["rules"])
    forbidden = set(activation["forbidden"])

    assert "current Agent" in rules
    assert "not a mandatory per-turn business proxy" in rules
    assert "REQUIRE_USER_TO_START_IN_UAOS_CONTROLLER_CHAT_BEFORE_USING_A_REGISTERED_CHILD" in forbidden
    assert "PROXY_EVERY_CHILD_BUSINESS_TURN_THROUGH_UAOS" in forbidden
    assert "EQUATE_PARENT_CONTROLLER_TASK_ID_WITH_CHILD_BUSINESS_IDENTITY" in forbidden


def test_entrypoint_has_no_stale_financial_same_identity_or_gateway_contract():
    entry = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")

    assert "new UAOS `task_type=article` identity" not in entry
    assert "Financial `STATE.json` with the same task id" not in entry
    assert "must not create a prerequisite parent article identity" in entry
    assert "normal child business turns do not traverse a live UAOS proxy" in entry
    assert "selecting Financial Writing activates `DOMAIN:financial_writing` directly" in entry


def test_bootstrap_pointer_does_not_reintroduce_parent_gateway_or_domain_policy_ownership():
    pointer = (ROOT / "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")

    assert "Resolve the current task through UAOS" not in pointer
    assert "All task, routing, retrieval, approval, recovery and domain policy remains in UAOS" not in pointer
    assert "activate that child directly as the current Agent" in pointer
    assert "do not proxy normal child business turns through UAOS" in pointer
    assert "Before any external or durable mutation" in pointer
    assert "Custom Instructions can make the bootstrap/sentinel persist across chats" in pointer
    assert "cannot make a GitHub write path physically non-bypassable" in pointer


def test_readiness_does_not_certify_retired_financial_same_id_binding():
    readiness = _json("docs/assurance/PRODUCTION_READINESS.json")
    serialized = json.dumps(readiness, ensure_ascii=False)

    assert readiness["verification"]["phase0_18_prior_baseline"] == "PASS_RETAINED"
    assert "Financial 0.8.2" not in serialized
    assert "mechanically validated UAOS article-task binding" not in serialized
    assert "exact UAOS article identity" not in serialized
    assert "FINANCIAL_0_8_3" in serialized
    assert "DISTINCT_PARENT_AND_FINANCIAL_IDENTITY_NAMESPACES" in serialized


def test_current_requirements_include_direct_domain_cognitive_and_complete_mediation_deltas():
    current = _json("CURRENT_SYSTEM.json")
    assert current["system_release_version"] == "2.4.4"
    assert current["status"] == "CANDIDATE_COMPLETE_MEDIATION__HOST_RULESET_PENDING"
    assert "docs/requirements/FROZEN_REQUIREMENTS_v1.5.md" in current["requirements"]
    assert "docs/requirements/FROZEN_REQUIREMENTS_v1.6.md" in current["requirements"]

    v15 = (ROOT / "docs/requirements/FROZEN_REQUIREMENTS_v1.5.md").read_text(encoding="utf-8")
    assert "Registered child Agents are directly activatable work planes" in v15
    assert "Triggered deliberation is fail-closed admission for material change" in v15
    assert "Evolution closure is authority-wide, not file-local" in v15

    v16 = (ROOT / "docs/requirements/FROZEN_REQUIREMENTS_v1.6.md").read_text(encoding="utf-8")
    assert "Production mutation requires complete mediation" in v16
    assert "Always-on sentinel, adaptive-depth cognition" in v16
    assert "Known bypass blocks `RESOLVED`" in v16


def test_material_architecture_change_is_fail_closed_without_deliberation_evidence():
    signals = DeliberationSignals(
        user_correction=True,
        architecture_gap=True,
        change_proposal=True,
    )

    with pytest.raises(RuntimeError, match="deliberation admission blocked"):
        require_deliberation_admission(signals)

    evidence = DeliberationEvidence(
        {
            "MICRO_DIAGNOSIS": ("incident:stale-entrypoint",),
            "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT": ("topology:direct-domain-work-plane",),
            "GOVERNING_ASSUMPTION_CHALLENGE": ("assumption:parent-not-gateway",),
            "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH": (
                "external:kubernetes-control-plane",
                "external:erlang-supervisor",
            ),
            "COUNTEREXAMPLE_SEARCH": ("counterexample:mandatory-parent-proxy",),
        }
    )
    directive = require_deliberation_admission(signals, evidence)
    assert directive.required
    assert directive.external_research_required
    assert not directive.independent_verification_required


def test_high_risk_deliberation_cannot_fake_independent_verification():
    signals = DeliberationSignals(high_risk=True, change_proposal=True)
    evidence = DeliberationEvidence(
        {
            "MICRO_DIAGNOSIS": ("e1",),
            "COUNTEREXAMPLE_SEARCH": ("e2",),
        }
    )
    with pytest.raises(RuntimeError, match="INDEPENDENT_VERIFICATION"):
        require_deliberation_admission(signals, evidence)


def test_deliberation_policy_requires_authority_and_host_control_surface_scan():
    policy = _json("config/DELIBERATION_POLICY.json")
    admission = policy["material_change_admission"]

    assert admission["fail_closed"] is True
    closure = "\n".join(admission["closure_guard"])
    assert "ENTRYPOINT" in closure
    assert "CURRENT_SYSTEM" in closure
    assert "task/router state" in closure
    assert "affected domain bindings" in closure
    assert "connector permissions" in closure
    assert "remote repository protection" in closure
    assert "known active production write path" in closure


def test_always_on_sentinel_is_small_and_distinct_from_deep_deliberation():
    session = _json("config/SESSION_INTERACTION_POLICY.json")
    sentinel = session["always_on_mutation_sentinel"]
    assert sentinel["required"] is True
    assert sentinel["depth_rule"] == "SENTINEL_ALWAYS_ON__DEEP_DELIBERATION_TRIGGERED_ONLY"
    assert "candidate branch -> pull request -> required promotion check -> protected merge" in sentinel["production_rule"]

    deliberation = _json("config/DELIBERATION_POLICY.json")
    contract = deliberation["mutation_sentinel_contract"]
    assert contract["always_on"] is True
    assert "not evidence" in contract["not_a_deliberation_dimension"]


def test_git_host_profile_retires_direct_main_cas_as_normal_production_path():
    host = _json("config/HOST_PROFILES.json")["profiles"]["CHATGPT_GITHUB"]
    assert host["production_mutation_protocol"] == "CANDIDATE_BRANCH__PULL_REQUEST__PROMOTION_GATE__PROTECTED_MERGE__REREAD"
    assert host["required_promotion_check"] == "promotion-gate"
    assert host["production_ref_enforcement"] == "ACTIVE_GITHUB_RULESET_REQUIRED"
    assert host["direct_main_raw_connector_write"] == "NOT_A_NORMAL_PRODUCTION_PATH"

    authority = _json("config/AUTHORITY_WRITE_POLICY.json")
    promotion = authority["promotion_concurrency"]
    assert "DIRECT_CAS_UPDATE_RETIRED" in promotion["production_main"]
    assert "not an authorization" in promotion["cas_semantics"]


def test_entrypoint_and_agents_require_protected_pr_promotion_not_direct_main_cas():
    entry = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "candidate branch -> pull request -> required `promotion-gate` -> protected merge" in entry
    assert "Do not use raw direct-main connector writes as the normal promotion path" in entry
    assert "candidate branch -> pull request -> required promotion-gate -> GitHub protected main" in agents
    assert "observed-HEAD CAS direct-main procedure is retired" in agents


def test_ci_exposes_stable_promotion_gate_context():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "name: promotion-gate" in workflow
    assert "run: pytest" in workflow


def test_known_physical_bypass_blocks_resolved_status():
    readiness = _json("docs/assurance/PRODUCTION_READINESS.json")
    assert readiness["parent_core_open_work"]
    assert readiness["parent_core_open_work"][0]["status"] == "BLOCKED_HOST_CONFIGURATION"
    assert readiness["verification"]["observed_host_state"]["github_main_protected"] is False
    assert readiness["verification"]["observed_host_state"]["github_rulesets"] == []

    previous = _json("state/evolution/EVO-20261014-COGNITIVE-ADMISSION-DIRECT-DOMAIN.json")
    assert previous["status"] == "REOPENED__PHYSICAL_ENFORCEMENT_FOLLOWUP"
    assert previous["acceptance"]["physical_complete_mediation"] == "OPEN_IN_FOLLOWUP"

    followup = _json("state/evolution/EVO-20261014-COMPLETE-MEDIATION-HOST-ENFORCEMENT.json")
    assert followup["status"] == "BLOCKED_HOST_ENFORCEMENT"
    assert followup["current_host_evidence"]["physical_complete_mediation"] == "FAIL"
