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


def _hypothetically_complete(observation):
    """Synthetic complete case; never evidence of live native assurance."""
    candidate = copy.deepcopy(observation)
    for item in candidate["coverage"]:
        item["assurance"] = "DEEP_SCENARIO_VERIFIED"
    candidate["method_evidence_refs"] = ["method:reference"]
    candidate["challenge_evidence_refs"] = ["challenge:counterexample"]
    candidate["realistic_validation_refs"] = ["runtime:observed"]
    candidate["independent_judge_refs"] = ["judge:independent"]
    return candidate


def test_completion_cannot_use_old_or_unverified_head_snapshots():
    registry, policy, observation = _inputs()
    candidate = _hypothetically_complete(observation)
    with pytest.raises(ControllerReviewAdmissionError, match="freshly verified"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=candidate,
            completion_requested=True, verify_evidence=lambda _: True,
        )
    heads = {item["repo"]: item["head"] for item in candidate["source_heads"]}
    stale = dict(heads)
    stale["universal-agent-os"] = "a" * 40
    with pytest.raises(ControllerReviewAdmissionError, match="differ from current"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=candidate,
            completion_requested=True, verify_evidence=lambda _: True,
            current_repository_heads=stale,
        )
    with pytest.raises(ControllerReviewAdmissionError, match="comprehensive knowledge acquisition"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=candidate,
            completion_requested=True, verify_evidence=lambda _: True,
            current_repository_heads=heads,
        )


def test_source_and_methods_self_claim_cannot_replace_knowledge_admission():
    from uaos.kernel.problem_space import (
        KnowledgeAcquisitionAssessment, KnowledgeSourceRole,
    )

    registry, policy, observation = _inputs()
    candidate = _hypothetically_complete(observation)
    heads = {item["repo"]: item["head"] for item in candidate["source_heads"]}
    claim = KnowledgeAcquisitionAssessment(
        acquisition_id="claim:shallow",
        objective="Pretend all disciplinary learning is comprehensive.",
        knowledge_modules=("architecture",),
        required_source_roles=(KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY,),
        sources=(), probes=(), method_families=(), contradictions=(),
        saturation_rounds=(),
        stop_reason="I say so",
        holdout_or_validation_plan="none",
    )
    with pytest.raises(ControllerReviewAdmissionError, match="comprehensive controller learning not admitted"):
        require_controller_review_admission(
            registry=registry, review_policy=policy, observation=candidate,
            completion_requested=True, verify_evidence=lambda _: True,
            current_repository_heads=heads, knowledge_acquisition_assessment=claim,
        )


def test_synthetic_full_admission_does_not_count_as_native_assurance():
    from uaos.kernel.problem_space import (
        AcquisitionMethod, AcquisitionProbe, Contradiction,
        ContradictionDisposition, KnowledgeAcquisitionAssessment,
        KnowledgeSource, KnowledgeSourceRole, MethodFamily, SaturationRound,
    )
    registry, policy, observation = _inputs()
    claimed = _hypothetically_complete(observation)
    heads = {item["repo"]: item["head"] for item in claimed["source_heads"]}
    validated_methods = KnowledgeAcquisitionAssessment(
        acquisition_id="test:synthetic-only",
        objective="Distinguish controlled evidence admission from behavioral assertion.",
        knowledge_modules=("multi-causal", "research-reliability"),
        required_source_roles=(
            KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY,
            KnowledgeSourceRole.PROFESSIONAL_METHOD,
            KnowledgeSourceRole.IMPLEMENTATION_EVIDENCE,
        ),
        sources=(
            KnowledgeSource("current", "source://current", KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY, ("e:current",)),
            KnowledgeSource("method", "source://method", KnowledgeSourceRole.PROFESSIONAL_METHOD, ("e:method",)),
            KnowledgeSource("repo", "source://repo", KnowledgeSourceRole.IMPLEMENTATION_EVIDENCE, ("e:repo",)),
        ),
        probes=(
            AcquisitionProbe("p1", AcquisitionMethod.DIRECT_SEARCH, "search", "baseline", ("e:current",)),
            AcquisitionProbe("p2", AcquisitionMethod.QUERY_EXPANSION, "cross-causal", "competing mechanisms", ("e:method",)),
            AcquisitionProbe("p3", AcquisitionMethod.REPOSITORY_TRAVERSAL, "current-owner", "implementation check", ("e:repo",)),
        ),
        method_families=(
            MethodFamily("causal", "Multiple causes", ("e:method",)),
            MethodFamily("trace", "Known-dependency impact", ("e:repo",)),
        ),
        contradictions=(
            Contradiction("c", "Exhaustive browse vs selective deep review", ContradictionDisposition.BOUNDED, ("e:method",), "Inventory all owners, prove scenario depth."),
        ),
        saturation_rounds=(
            SaturationRound("s1", (AcquisitionMethod.QUERY_EXPANSION,), (), (), (), False, ("e:method",)),
            SaturationRound("s2", (AcquisitionMethod.REPOSITORY_TRAVERSAL,), (), (), (), False, ("e:repo",)),
        ),
        stop_reason="Synthetic terminal rounds supplied for gate reachability only",
        holdout_or_validation_plan="Test native traces separately",
    )
    receipt = require_controller_review_admission(
        registry=registry, review_policy=policy, observation=claimed,
        completion_requested=True, verify_evidence=lambda _: True,
        current_repository_heads=heads,
        knowledge_acquisition_assessment=validated_methods,
    )
    assert receipt.complete
    assert not observation.get("independent_judge_refs")
    # The positive result proves a gate is reachable with trusted inputs;
    # it must never be interpreted as the actual UAOS review having finished.
