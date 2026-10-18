import copy
import json
from pathlib import Path

import pytest

from uaos.assurance.controller_review import (
    ControllerReviewAdmissionError,
    require_controller_review_admission,
)

ROOT = Path(__file__).resolve().parents[2]


def _j(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _inputs():
    return (
        _j("config/AGENT_REGISTRY.json"),
        _j("config/SESSION_INTERACTION_POLICY.json")["controller_inheritance_review"],
        _j("state/observations/uaos-controller-five-repo-review-20261018.json"),
    )


def test_real_five_repo_source_inventory_is_admitted_only_as_incomplete():
    registry, policy, observed = _inputs()
    receipt = require_controller_review_admission(
        registry=registry, review_policy=policy, observation=observed
    )
    assert len(receipt.recorded_repositories) == len(registry["agents"]) + 1
    assert receipt.mapped_source_count == len(receipt.recorded_repositories) * 6
    assert receipt.open_findings
    assert not receipt.complete


def test_cannot_promote_source_inventory_as_full_depth_or_runtime_quality():
    registry, policy, observed = _inputs()
    with pytest.raises(ControllerReviewAdmissionError, match="insufficient"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=observed,
            completion_requested=True, verify_evidence=lambda ref: True,
        )


def test_registered_repo_and_missing_dimension_are_both_hard_failures():
    registry, policy, observed = _inputs()
    incomplete = copy.deepcopy(observed)
    incomplete["source_heads"].pop()
    with pytest.raises(ControllerReviewAdmissionError, match="registered repositories"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=incomplete
        )
    incomplete = copy.deepcopy(observed)
    incomplete["coverage"].pop()
    with pytest.raises(ControllerReviewAdmissionError, match="dimensions"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=incomplete
        )


def test_self_reported_deep_cells_require_separate_evidence_and_verifier():
    registry, policy, observed = _inputs()
    claimed = copy.deepcopy(observed)
    for row in claimed["coverage"]:
        row["assurance"] = "DEEP_SCENARIO_VERIFIED"
    with pytest.raises(ControllerReviewAdmissionError, match="insufficient"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=claimed,
            completion_requested=True, verify_evidence=lambda ref: True,
        )
    claimed["method_evidence_refs"] = ["source:method-review"]
    claimed["challenge_evidence_refs"] = ["source:counterexample"]
    claimed["realistic_validation_refs"] = ["source:runtime-trace"]
    claimed["independent_judge_refs"] = ["source:independent-judge"]
    with pytest.raises(ControllerReviewAdmissionError, match="separate evidence verifier"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=claimed,
            completion_requested=True,
        )
    with pytest.raises(ControllerReviewAdmissionError, match="unverified evidence"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=claimed,
            completion_requested=True, verify_evidence=lambda ref: False,
        )
