"""A green descendant CI cannot certify a user's financial publication outcome."""
import json
from pathlib import Path

import pytest

from uaos.kernel.domain_health import (
    DomainObservation, HealthFindingType, ProductOutcomeEvidence,
    assess_product_outcome, require_product_outcome_completion,
)

ROOT = Path(__file__).resolve().parents[2]
REV = "e580cd4dfda8db47674803451c9adfff9e3cf975"


def _obs():
    return DomainObservation(domain_id="financial_writing", current_revision=REV, parent_observed_revision=REV)


def _product(**override):
    values = dict(
        domain_id="financial_writing", child_revision=REV,
        objective_ref="verified:governing_user_value",
        required_dimensions=("requirements_consumed", "factual_research",
                             "reader_quality", "visible_word_delivery"),
        dimension_evidence=(("requirements_consumed", "verified:task-contract"),),
        independently_adjudicated_outcome_ref=None,
        open_rejection_refs=("verified:prior-rejection-unresolved",),
    )
    values.update(override)
    return ProductOutcomeEvidence(**values)


def test_real_world_financial_ci_is_not_product_quality_evidence():
    receipt = assess_product_outcome(_obs(), _product(), verify_evidence=lambda ref: ref.startswith("verified:"))
    assert not receipt.healthy
    finding = receipt.findings[0]
    assert finding.finding_type == HealthFindingType.PRODUCT_OUTCOME_VALIDATION_GAP
    assert "reader_quality" in finding.summary
    assert "no independent or real user outcome adjudication" in finding.summary
    with pytest.raises(ValueError, match="product outcome not validated"):
        require_product_outcome_completion(_obs(), _product(), verify_evidence=lambda _: True)


def test_even_all_dimension_strings_and_pass_labels_cannot_self_certify_without_verifier():
    evidence = tuple((d, f"self-report:{d}") for d in _product().required_dimensions)
    claimed = _product(
        dimension_evidence=evidence,
        independently_adjudicated_outcome_ref="self-report:judge"
    )
    assert not assess_product_outcome(_obs(), claimed, verify_evidence=None).healthy
    assert not assess_product_outcome(_obs(), claimed, verify_evidence=lambda ref: False).healthy


def test_old_article_or_old_head_cannot_qualify_new_current_outcome():
    product = _product(child_revision="f261367eb480c884880890513752afc77d1ef916")
    assert "current child revision" in assess_product_outcome(
        _obs(), product, verify_evidence=lambda _: True
    ).findings[0].summary


def test_synthetic_complete_requirements_plus_distinct_receipts_can_be_admitted_by_trusted_host():
    required = _product().required_dimensions
    approved = _product(
        dimension_evidence=tuple((name, "receipt:" + name) for name in required),
        independently_adjudicated_outcome_ref="reviewer:distinct",
        open_rejection_refs=(),
    )
    outcome = require_product_outcome_completion(
        _obs(), approved, verify_evidence=lambda ref: ref.startswith(("receipt:", "reviewer:", "verified:"))
    )
    assert outcome.healthy  # synthetic contract test, NOT a live financial publishing acceptance


def test_outcome_scope_opt_in_does_not_turn_every_domain_into_financial_writer():
    assert DomainObservation(domain_id="novel", current_revision="novel-sha").domain_id == "novel"
    with pytest.raises(ValueError, match="domain mismatch"):
        assess_product_outcome(
            DomainObservation(domain_id="novel", current_revision="novel-sha"),
            _product(), verify_evidence=lambda _: True,
        )


def test_parent_index_keeps_exactly_one_default_and_financial_outcome_open():
    index = json.loads((ROOT / "state/TASK_INDEX.json").read_text(encoding="utf-8"))
    defaults = [x for x in index["controller_tasks"] if x["resume_eligible"] and x["default_resume"]]
    assert [d["task_id"] for d in defaults] == [
        "uaos:maintenance:financial-system-governed-recovery-20261018"
    ]
    task = json.loads((ROOT / defaults[0]["state_ref"]).read_text(encoding="utf-8"))
    assert task["authority_context"] == "UAOS"
    assert task["status"] == "RUNNING"
    assert "UAOS->registered DOMAIN:financial_writing" in task["ancestry_and_mutation_boundary"]
    assert task["acceptance_contract"]["positive_closure_requires"]
