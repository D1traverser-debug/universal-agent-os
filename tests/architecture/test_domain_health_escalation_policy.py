import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def test_system_map_registers_domain_health_control_surface():
    system_map = _json("config/SYSTEM_MAP.json")
    assert _version_tuple(system_map["schema_version"]) >= (1, 9)
    assert system_map["controller"]["domain_health_escalation_policy"] == "config/DOMAIN_HEALTH_ESCALATION_POLICY.json"
    assert system_map["controller"]["domain_health_index"] == "state/DOMAIN_HEALTH_INDEX.json"


def test_binding_treats_parent_snapshots_as_cache_and_forbids_global_fifo_blocking():
    binding = _json("config/BINDING_POLICY.json")
    assert tuple(map(int, binding["schema_version"].split("."))) >= (2, 1)
    assert binding["domain_health_escalation_policy"] == "config/DOMAIN_HEALTH_ESCALATION_POLICY.json"
    assert "PARENT_RELEASE_OR_PROFILE_OBSERVATIONS_ARE_CACHE_EVIDENCE_NOT_CHILD_AUTHORITY" in binding["proactive_domain_health_rule"]
    assert "MUST_NOT_CREATE_A_GLOBAL_FIFO_BLOCKER" in binding["multi_upcall_rule"]
    assert "CANONICAL_CAUSAL_INTERVENTION_ADMISSION" in binding["problem_cognition_action_rule"]


def test_policy_requires_active_discovery_bulkheading_and_two_skill_discovery_modes():
    policy = _json("config/DOMAIN_HEALTH_ESCALATION_POLICY.json")
    assert _version_tuple(policy["policy_version"]) >= (1, 1, 0)
    checks = set(policy["proactive_discovery"]["checks"])
    assert "PARENT_CHILD_AUTHORITY_FRESHNESS" in checks
    assert "INHERITED_BEHAVIOR_OPERATIONAL_EVIDENCE" in checks
    assert "REPEATED_OR_CROSS_DOMAIN_FAILURE_CLASS_CLUSTERING" in checks
    assert "global FIFO" in policy["triage_and_bulkheading"]["serialization_rule"]

    intake = policy["external_skill_intake"]
    assert set(intake["discovery_modes"]) == {"KNOWN_NEED_MATCH", "OUTSIDE_IN_LATENT_CAPABILITY_DISCOVERY"}
    assert intake["outside_in_executable_ref"] == "src/uaos/kernel/problem_space.py"
    forbidden = set(intake["forbidden"])
    assert "REQUIRE_EVERY_BROAD_SURVEY_TO_PRETEND_THE_USEFUL_NEED_WAS_ALREADY_KNOWN" in forbidden
    assert "TREAT_ONE_ROLE_OCCUPATION_CATEGORY_OR_CREATOR_AS_THE_ARCHITECTURE" in forbidden
    assert "BLIND_COPY_OR_INSTALL_AS_AUTHORITY" in forbidden
    assert "PROMOTE_WITHOUT_EVALUATION_EVIDENCE" in forbidden


def test_health_index_is_non_authoritative_cache_and_current_system_does_not_duplicate_it():
    health = _json("state/DOMAIN_HEALTH_INDEX.json")
    current = _json("CURRENT_SYSTEM.json")
    assert health["role"] == "PARENT_HEALTH_OBSERVATION_CACHE__NOT_CHILD_BUSINESS_AUTHORITY"
    assert current["child_observation"]["source"] == "state/DOMAIN_HEALTH_INDEX.json"
    assert current["child_observation"]["role"] == health["role"]

    expected_profile_floors = {
        "financial_writing": 19,
        "ashare": 7,
        "novel": 6,
        "video": 10,
    }
    for domain_id, profile_floor in expected_profile_floors.items():
        observed = health["domains"][domain_id]
        assert observed["observed_profile_version"] >= profile_floor
        assert _version_tuple(observed["common_behavior_assurance_min"]) >= (1, 3, 0)
        assert observed["production_ci"]["conclusion"] == "success"
        assert "OWNER_NATIVE" in observed["common_behavior_assurance"]
        if domain_id == "financial_writing":
            finding_types = {item["type"] for item in observed["findings"]}
            assert finding_types == {"PRODUCT_OUTCOME_VALIDATION_GAP"}
            assert observed["product_outcome_assurance"]["status"].startswith("OPEN")
            assert observed["product_outcome_assurance"]["source_revision"] == observed["observed_main_commit"]
        else:
            assert observed["findings"] == []

    release_floors = {
        "financial_writing": (1, 0, 1),
        "ashare": (0, 3, 0),
        "video": (0, 8, 0),
    }
    for domain_id, release_floor in release_floors.items():
        assert _version_tuple(health["domains"][domain_id]["observed_release"]) >= release_floor

    assert health["domains"]["financial_writing"]["canonical_evolution_entrypoint"] == "evals/EVOLUTION_INDEX.json"
    assert health["domains"]["ashare"]["canonical_evolution_entrypoint"] == "audits/EVOLUTION_INDEX.json"
    assert health["domains"]["novel"]["canonical_evolution_entrypoint"] == "audits/EVOLUTION_INDEX.json"
    assert health["domains"]["video"]["canonical_evolution_entrypoint"] == "audits/EVOLUTION_INDEX.json"

    for old_snapshot_key in (
        "financial_child_production_verification",
        "ashare_child_production_verification",
        "novel_child_production_verification",
        "video_child_production_verification",
    ):
        assert old_snapshot_key not in current

    learning = {row["failure_class"]: row for row in health["cross_domain_learnings"]}
    freeze = learning["FC-EVOLVING-CAPABILITY-MINIMUM-ENCODED-AS-EXACT-CURRENT-VERSION-005"]
    assert "compatibility-floor" in freeze["selected_rule"].lower()
    live_binding = learning["FC-LIVE-CROSS-REPO-BINDING-DRIFT-HIDDEN-BY-SYNTHETIC-FIXTURE-014"]
    assert "synthetic" in live_binding["selected_rule"].lower()
    assert "current child authority" in live_binding["selected_rule"].lower()

    open_common = set(health["open_common_findings"])
    assert "FC-PARENT-CHILD-FRESHNESS-SNAPSHOT-MASQUERADING-AS-CURRENT-001" not in open_common
    assert "FC-INHERITED-BEHAVIOR-DECLARATION-WITHOUT-UNIFORM-OPERATIONAL-PROOF-002" not in open_common
    assert "FC-PARENT-GUIDANCE-SINGLE-QUEUE-BLOCKING-RISK-003" in open_common
    assert "FC-PROACTIVE-UNKNOWN-FAILURE-DISCOVERY-GAP-004" in open_common


def test_requirements_define_operational_inheritance_active_discovery_and_skill_candidate_semantics():
    text = (ROOT / "docs/requirements/FROZEN_REQUIREMENTS_v2.1.md").read_text(encoding="utf-8")
    assert "Inheritance is operational, not declarative" in text
    assert "Proactive health discovery is required" in text
    assert "Parent guidance is bulkheaded, not one global blocking queue" in text
    assert "External Skills are candidate methods, not authority" in text
