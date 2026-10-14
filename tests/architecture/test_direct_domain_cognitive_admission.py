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


def test_readiness_does_not_certify_retired_financial_same_id_binding():
    readiness = _json("docs/assurance/PRODUCTION_READINESS.json")
    serialized = json.dumps(readiness, ensure_ascii=False)

    assert "Financial 0.8.2" not in serialized
    assert "mechanically validated UAOS article-task binding" not in serialized
    assert "exact UAOS article identity" not in serialized
    assert "FINANCIAL_0_8_3" in serialized
    assert "DISTINCT_PARENT_AND_FINANCIAL_IDENTITY_NAMESPACES" in serialized


def test_current_requirements_include_direct_domain_and_cognitive_admission_delta():
    current = _json("CURRENT_SYSTEM.json")
    assert "docs/requirements/FROZEN_REQUIREMENTS_v1.5.md" in current["requirements"]
    requirements = (ROOT / "docs/requirements/FROZEN_REQUIREMENTS_v1.5.md").read_text(encoding="utf-8")
    assert "Registered child Agents are directly activatable work planes" in requirements
    assert "Triggered deliberation is fail-closed admission for material change" in requirements
    assert "Evolution closure is authority-wide, not file-local" in requirements


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


def test_deliberation_policy_requires_authority_wide_closure_scan():
    policy = _json("config/DELIBERATION_POLICY.json")
    admission = policy["material_change_admission"]

    assert admission["fail_closed"] is True
    closure = "\n".join(admission["closure_guard"])
    assert "ENTRYPOINT" in closure
    assert "CURRENT_SYSTEM" in closure
    assert "task/router state" in closure
    assert "affected domain bindings" in closure
