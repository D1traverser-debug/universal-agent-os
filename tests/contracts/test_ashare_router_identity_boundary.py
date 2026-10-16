import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_parent_has_one_ashare_router_and_no_parent_market_day_business_state():
    index = load("state/TASK_INDEX.json")
    ashare = [row for row in index["tasks"] if row["domain_id"] == "ashare"]
    assert [row["task_id"] for row in ashare] == ["ashare:main"]
    router = ashare[0]
    assert router["task_type"] == "domain_market_day_router"
    assert router["state_ref"] == "state/tasks/ashare-main.json"
    assert "ashare:recommendation" in router["aliases"]
    assert not (ROOT / "state/tasks/ashare-recommendation.json").exists()


def test_ashare_router_does_not_own_trading_day_or_child_business_identity():
    router = load("state/tasks/ashare-main.json")
    assert router["task_id"] == "ashare:main"
    assert router["active_domain_state_ref"] is None
    assert router["domain_business_state_is_controller"] is False
    assert "OPAQUE_CHILD_MARKET_DAY_REFERENCE" in router["domain_reference_semantics"]
    assert "NO_EQUALITY_REQUIREMENT" in router["identity_boundary"]
    assert "CHILD_RESOLVES_CURRENT_CHINA_TRADING_DAY" in router["generic_resolution_rule"]
    assert "OLD_PREMARKET_NEVER_AUTO_BECOMES_CURRENT_DAY" in router["historical_resume_rule"]
    serialized = json.dumps(router, ensure_ascii=False).lower()
    assert "ticker" not in serialized
    assert "limit_up" not in serialized
    assert "level-2" not in serialized
    assert "u0" not in serialized and "u1" not in serialized and "u3" not in serialized


def test_parent_system_map_points_to_child_business_identity_without_copying_business_rules():
    system_map = load("config/SYSTEM_MAP.json")
    ashare = system_map["domains"]["ashare"]
    assert ashare["business_identity"] == "ashare_event_agent/models.py:TaskContract.task_id"
    assert "MarketDayState" in ashare["business_state"]
    assert "DISTINCT" in ashare["identity_semantics"]
    assert "OPAQUE_CHILD_REF" in ashare["identity_semantics"]


def test_current_system_routes_ashare_freshness_to_domain_health_cache_instead_of_copying_child_snapshot():
    current = load("CURRENT_SYSTEM.json")
    health = load("state/DOMAIN_HEALTH_INDEX.json")
    assert tuple(map(int, current["system_release_version"].split("."))) >= (2, 5, 2)
    assert current["status"] == "ACTIVE_PRIMARY_CONTROLLER" or current["status"].startswith("CANDIDATE_")
    assert current["child_observation"]["source"] == "state/DOMAIN_HEALTH_INDEX.json"
    assert "ashare_child_production_verification" not in current
    assert "ashare_binding_assurance" not in current
    observed = health["domains"]["ashare"]
    assert observed["repository"] == "D1traverser-debug/a-share-event-driven-agent"
    assert observed["observed_release"] == "0.3.0"
    assert observed["observed_profile_version"] >= 7
    assert observed["production_ci"]["conclusion"] == "success"
