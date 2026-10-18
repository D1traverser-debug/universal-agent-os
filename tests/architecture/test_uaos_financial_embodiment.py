"""Explicit UAOS-as-Financial-work-executor routing, without parent child-state cloning.

These are structural/continuity checks. They do not claim that native host actually
ran a writing workflow or that a human accepted any article.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_work_is_parent_owned_as_an_actual_professional_task():
    index = _json("state/TASK_INDEX.json")
    defaults = [t for t in index["controller_tasks"] if t["default_resume"] and t["resume_eligible"]]
    assert len(defaults) == 1
    assert defaults[0]["task_id"] == "uaos:maintenance:inheritance-review-20261018"
    finance = next(t for t in index["controller_tasks"] if t["task_id"] == index["controller_default_handoff"]["return_task_id"])
    assert finance["resume_eligible"] and not finance["default_resume"]
    task = _json(finance["state_ref"])
    assert task["authority_context"] == "UAOS"
    assert task["task_id"] == "uaos:maintenance:financial-system-governed-recovery-20261018"
    assert finance["current_stage"] == task["current_stage"]
    assert task["operational_role"].startswith("UAOS_CONTROLLER__PROFESSIONAL_FINANCE_RESEARCH")
    assert task["execution_mandate"]["material_intake_in_this_chat"] is True
    assert task["descendant_business_owner"] == "DOMAIN:financial_writing"
    assert task["status"] == "RUNNING"
    assert task["execution_mandate"]["role_boundary"].endswith("NO_SECOND_STATE")


def test_explicit_parent_professional_entry_keeps_valid_descendant_authority():
    entry = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    assert "### Explicit controller-as-domain-professional execution" in entry
    assert "personally performs" in entry
    assert "parent-governed descendant mutation" in entry
    assert "Do not fabricate a second parent business aggregate" in entry
    assert "This *explicit, task-scoped controller assignment*" in entry


def test_real_editorial_quality_is_open_despite_positive_repo_ci():
    task = _json("state/tasks/uaos-financial-system-governed-recovery-20261018.json")
    review = (ROOT / task["execution_mandate"]["source_ref"]).read_text(encoding="utf-8")
    assert "writing_kernel.py" in review
    assert "Source/material readiness right now" in review
    assert "174-company" in review
    assert "NOT_READY" in review
    assert "CURRENT" in task["workstreams"][2]["state"]
    assert task["deep_review_current_sources"]["old_word_audit_five_style_pass_vs_later_user_rejection"].startswith(
        "FAILURE_CLASS_RECURRED"
    )
    assert task["deep_review_current_sources"]["coverage_claim"].startswith("WIDE_INVENTORY")
    assert task["last_blocker"]["disposition"].startswith("DO_NOT_REROUTE")
    assert task["deep_review_current_sources"]["general_quality"] == "NOT_READY"


def test_parent_authority_is_not_mistaken_for_financial_article_state():
    index = _json("state/TASK_INDEX.json")
    default = next(x for x in index["controller_tasks"] if x["task_id"] == index["controller_default_handoff"]["return_task_id"])
    child_router = next(x for x in index["tasks"] if x["domain_id"] == "financial_writing")
    assert default["task_id"] != child_router["task_id"]
    assert default["authority_context"] == "UAOS"
    assert child_router["domain_id"] == "financial_writing"
    assert child_router["state_ref"] == "state/tasks/financial-writing-main.json"
