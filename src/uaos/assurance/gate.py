from __future__ import annotations

from collections import Counter
from typing import Iterable

from .models import (
    CheckStatus,
    CompletionDecision,
    DeliveryExpectation,
    DeliveryProof,
    EvidenceLevel,
    RequirementCheck,
    ReviewEvidence,
)


class AssuranceGate:
    def assess(
        self,
        *,
        required_requirement_ids: Iterable[str],
        checks: Iterable[RequirementCheck],
        delivery_expectations: Iterable[DeliveryExpectation] = (),
        delivery_proofs: Iterable[DeliveryProof] = (),
        unresolved_unknown_action_ids: Iterable[str] = (),
        minimum_evidence: EvidenceLevel = EvidenceLevel.DETERMINISTIC,
        independent_review_required: bool = False,
        reviews: Iterable[ReviewEvidence] = (),
    ) -> CompletionDecision:
        reasons: list[str] = []
        by_requirement = {check.requirement_id: check for check in checks}

        for requirement_id in required_requirement_ids:
            check = by_requirement.get(requirement_id)
            if check is None:
                reasons.append(f"missing requirement check: {requirement_id}")
                continue
            if check.status is not CheckStatus.PASS:
                reasons.append(f"requirement {requirement_id} is {check.status}")
            if not check.evidence_refs:
                reasons.append(f"requirement {requirement_id} has no evidence")
            if check.evidence_level < minimum_evidence:
                reasons.append(
                    f"requirement {requirement_id} evidence below minimum: "
                    f"{check.evidence_level.name} < {minimum_evidence.name}"
                )

        expected = {(item.artifact_id, item.version): item for item in delivery_expectations}
        proofs = {(item.artifact_id, item.version): item for item in delivery_proofs}
        for key, expectation in expected.items():
            proof = proofs.get(key)
            if proof is None:
                reasons.append(f"missing delivery proof: {expectation.artifact_id}@{expectation.version}")
                continue
            if not proof.accessible:
                reasons.append(f"deliverable inaccessible: {expectation.artifact_id}@{expectation.version}")
            if proof.content_hash != expectation.content_hash:
                reasons.append(f"deliverable hash mismatch: {expectation.artifact_id}@{expectation.version}")

        unknown_actions = tuple(unresolved_unknown_action_ids)
        if unknown_actions:
            reasons.append(f"unresolved UNKNOWN actions: {','.join(sorted(unknown_actions))}")

        if independent_review_required and not any(review.is_independent for review in reviews):
            reasons.append("independent review required but not proven")

        levels = Counter(check.evidence_level.name for check in by_requirement.values())
        complete = not reasons
        return CompletionDecision(
            complete=complete,
            status="COMPLETE" if complete else "BLOCKED",
            reasons=tuple(reasons),
            evidence_summary=dict(sorted(levels.items())),
        )
