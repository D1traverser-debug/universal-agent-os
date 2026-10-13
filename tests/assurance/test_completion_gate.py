from datetime import UTC, datetime
from uaos.assurance import (
    AssuranceGate,
    CheckStatus,
    CoverageEntry,
    DeliveryExpectation,
    DeliveryProof,
    EvidenceLevel,
    RequirementCheck,
    ReviewEvidence,
    coverage_map,
)


def passing_check(requirement_id="r1", level=EvidenceLevel.DETERMINISTIC):
    return RequirementCheck(requirement_id, CheckStatus.PASS, ("e:1",), level)


def test_completion_requires_every_requirement_and_evidence():
    decision = AssuranceGate().assess(required_requirement_ids=("r1", "r2"), checks=(passing_check("r1"),))
    assert not decision.complete
    assert any("missing requirement check: r2" in reason for reason in decision.reasons)


def test_delivery_must_match_actual_visible_version_and_hash():
    expectation = DeliveryExpectation("doc", 2, "hash2")
    bad_proof = DeliveryProof("doc", 2, "wrong", True, datetime.now(UTC), "proof")
    decision = AssuranceGate().assess(
        required_requirement_ids=("r1",),
        checks=(passing_check(),),
        delivery_expectations=(expectation,),
        delivery_proofs=(bad_proof,),
    )
    assert not decision.complete
    assert any("hash mismatch" in reason for reason in decision.reasons)


def test_unresolved_unknown_action_blocks_completion():
    decision = AssuranceGate().assess(
        required_requirement_ids=("r1",),
        checks=(passing_check(),),
        unresolved_unknown_action_ids=("a9",),
    )
    assert not decision.complete
    assert any("UNKNOWN" in reason for reason in decision.reasons)


def test_independent_review_is_evidence_based_not_reviewer_label():
    same = ReviewEvidence("rv", "agent-a", "agent-a", "e", ("prompt",))
    different = ReviewEvidence("rv2", "agent-a", "agent-b", "e2", ("reviewer_identity",))
    gate = AssuranceGate()
    blocked = gate.assess(
        required_requirement_ids=("r1",),
        checks=(passing_check("r1", EvidenceLevel.SEMANTIC),),
        independent_review_required=True,
        reviews=(same,),
    )
    assert not blocked.complete
    passed = gate.assess(
        required_requirement_ids=("r1",),
        checks=(passing_check("r1", EvidenceLevel.SEMANTIC),),
        independent_review_required=True,
        reviews=(different,),
    )
    assert passed.complete


def test_evidence_level_caps_claim():
    low = RequirementCheck("r1", CheckStatus.PASS, ("doc:rule",), EvidenceLevel.DECLARATION)
    decision = AssuranceGate().assess(
        required_requirement_ids=("r1",),
        checks=(low,),
        minimum_evidence=EvidenceLevel.DETERMINISTIC,
    )
    assert not decision.complete
    assert any("below minimum" in reason for reason in decision.reasons)


def test_coverage_is_by_capability_or_failure_class_not_count():
    grouped = coverage_map((
        CoverageEntry("capability", "resume", ("test:s8",), CheckStatus.PASS),
        CoverageEntry("failure_class", "ambiguous_outcome", ("test:s10",), CheckStatus.PASS),
    ))
    assert set(grouped) == {"capability", "failure_class"}
