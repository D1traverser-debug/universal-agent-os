"""Keep verified UAOS controller ownership distinct from unfinished child results."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def _j(p):
    return json.loads((ROOT/p).read_text(encoding="utf-8"))


def test_financial_governance_parent_remains_running_and_exactly_default():
    i=_j("state/TASK_INDEX.json")
    selected=[t for t in i["controller_tasks"] if t["default_resume"]]
    assert len(selected)==1
    t=selected[0]
    task=_j(t["state_ref"])
    assert task["task_id"]==t["task_id"]=="uaos:maintenance:financial-system-governed-recovery-20261018"
    assert t["current_stage"]==task["current_stage"]
    assert task["status"]==t["status"]=="RUNNING"
    assert task["controlled_finalization_extension"]["production"]["ci"]==631
    assert task["assurance"].endswith("FINANCIAL_CURRENT_ARTICLE_READER_AND_DELIVERY_OUTCOME_OPEN")
    assert task["descendant_business_owner"]=="DOMAIN:financial_writing"
    assert task["required_user_action_now"]=="NONE"


def test_code_assurance_is_not_current_product_acceptance():
    health=_j("state/DOMAIN_HEALTH_INDEX.json")
    financial=health["domains"]["financial_writing"]
    assert len(financial["findings"])==1
    assert financial["findings"][0]["type"]=="PRODUCT_OUTCOME_VALIDATION_GAP"
    evidence=_j(financial["findings"][0]["evidence_ref"])
    assert evidence["open_product"]["current_task_stage"]=="RESEARCH"
    assert evidence["open_product"]["delivered_artifacts"]==0
    assert evidence["open_product"]["general_quality_status"].startswith("NOT_READY")
    evo=_j("state/evolution/EVO-20261018-FINANCIAL-PRODUCT-OUTCOME-ASSURANCE.json")
    assert evo["production_20261018_finalization_evidence"]["ci_run"]==631
    assert "LIVE_CHILD_USER_OUTCOME_OPEN" in evo["status"]
