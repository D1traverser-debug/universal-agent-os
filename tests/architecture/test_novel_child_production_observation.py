from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_novel_current_observation_lives_in_domain_health_cache_not_current_system():
    system = load_json("CURRENT_SYSTEM.json")
    health = load_json("state/DOMAIN_HEALTH_INDEX.json")
    assert tuple(int(part) for part in system["schema_version"].split(".")) >= (2, 31)
    assert system["child_observation"]["source"] == "state/DOMAIN_HEALTH_INDEX.json"
    assert system["child_observation"]["role"] == "PARENT_HEALTH_OBSERVATION_CACHE__NOT_CHILD_BUSINESS_AUTHORITY"
    assert "novel_child_production_verification" not in system
    assert "novel_binding_assurance" not in system
    observed = health["domains"]["novel"]
    assert observed["repository"] == "D1traverser-debug/novel-writing-agent"
    assert observed["observed_profile_version"] >= 6
    assert observed["common_behavior_assurance_min"] == "1.3.0"
    assert observed["canonical_evolution_entrypoint"] == "audits/EVOLUTION_INDEX.json"


def test_parent_observation_does_not_mirror_child_canon_or_learning_payloads():
    system = load_json("CURRENT_SYSTEM.json")
    serialized = json.dumps(system, ensure_ascii=False).lower()
    for forbidden in (
        '"canon"',
        '"characters"',
        '"threads"',
        '"foreshadow"',
        '"masterwork_ledger"',
        '"story_candidates"',
        '"dynamic_outline"',
        '"chapter_contracts"',
    ):
        assert forbidden not in serialized

    task = load_json("state/tasks/FQ001_MINGRI_ORDER.json")
    assert task["project_business_authority"] == "D1traverser-debug/novel-writing-agent@main:projects/FQ001_MINGRI_ORDER/checkpoints/CURRENT_CHECKPOINT.json"
    assert task["project_business_state_is_controller"] is False
    assert task["progress_timestamp_semantics"] == "UAOS_TASK_STATE_NORMALIZED_ONLY__BUSINESS_CHECKPOINT_MUST_BE_REREAD_BEFORE_RESUME"
