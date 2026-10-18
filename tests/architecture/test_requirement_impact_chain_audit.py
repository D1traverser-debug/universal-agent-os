"""Source-bound negative controls for requirement impact and evolution matching.

These tests record a gap; they do not certify any native behavior or a complete
requirement-to-action effect graph.
"""
import json
from pathlib import Path

from uaos.contracts.enums import ScopeType
from uaos.contracts.models import RequirementRecord
from uaos.contracts.planning import transitive_dependents
from uaos.contracts.models import Plan, WorkUnit

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "state/observations/uaos-requirement-impact-chain-20261018.json"


def test_legacy_scenario_coverage_is_not_all_current_requirements():
    inventory = sorted((ROOT / "docs/requirements").glob("FROZEN_REQUIREMENTS_v*.md"))
    coverage = json.loads((ROOT / "docs/assurance/FROZEN_SCENARIO_COVERAGE.json").read_text())
    audit = json.loads(AUDIT.read_text())
    assert len(inventory) == 13
    assert coverage["requirements_version"] == "v1.0"
    assert len(coverage["scenarios"]) == 20
    assert all(item["live_e2e"].startswith("OPEN") for item in coverage["scenarios"])
    assert audit["analysis_status"] == "CONFIRMED_PARTIAL_CHAIN__END_TO_END_AND_UNIVERSAL_EVOLUTION_NOT_VERIFIED"


def test_planning_dependency_closure_needs_explicit_work_root_provenance():
    req = RequirementRecord("r-output", "Improve output readability", ScopeType.TASK, scope_id="task-1")
    plan = Plan("p", "task-1", 1, (
        WorkUnit("research", "task-1", "research"),
        WorkUnit("outline", "task-1", "outline", dependencies=("research",)),
        WorkUnit("draft", "task-1", "draft", dependencies=("outline",)),
        WorkUnit("review", "task-1", "review", dependencies=("draft",)),
    ))
    # For the same RequirementRecord, different guessed roots yield different impacts.
    # Current contracts carry no evidence connecting this requirement to either root.
    outline_impact = transitive_dependents(plan, {"outline"})
    draft_impact = transitive_dependents(plan, {"draft"})
    assert outline_impact == frozenset({"outline", "draft", "review"})
    assert draft_impact == frozenset({"draft", "review"})
    assert outline_impact != draft_impact
    assert req.requirement_id == "r-output"
    audit = json.loads(AUDIT.read_text())
    assert audit["disposition"] == "ROOT_GAP_CONFIRMED__NEW_SYSTEM_WIDE_INTERVENTION_NOT_YET_ADMITTED"


def test_audit_explicitly_rejects_user_and_assistant_as_root_cause_authority():
    audit = json.loads(AUDIT.read_text())
    assert any("user or assistant" in item.lower() for item in audit["required_validation_scenarios"])
    assert {item["id"] for item in audit["competing_interventions"]} >= {
        "A_FORCE_ALL_REQUIREMENTS_INTO_EVOLUTION",
        "B_REWRITE_ALL_REQUIREMENT_AND_ACTION_SYSTEMS",
        "C_BIND_CURRENT_REQUIREMENT_AUTHORITY_TO_EXISTING_PLANNING_TOPOLOGY_ASSURANCE_AND_EVOLUTION_WITH_TRACEABLE_CAUSAL_IMPACT",
        "D_NO_CHANGE",
    }
    assert audit["limits"]
