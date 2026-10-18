"""Read-only controller inheritance review admission over canonical owner evidence.

This is a source/coverage validator, NOT a native ChatGPT pre-send hook or
another research/evolution decision owner.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from uaos.kernel.problem_space import (
    KnowledgeAcquisitionAdmissionError,
    KnowledgeAcquisitionAssessment,
    require_knowledge_acquisition_admission,
)


class ControllerReviewAdmissionError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ControllerReviewReceipt:
    recorded_repositories: tuple[str, ...]
    dimensions: tuple[str, ...]
    mapped_source_count: int
    complete: bool
    open_findings: tuple[str, ...]


def require_controller_review_admission(
    *,
    registry: Mapping[str, Any],
    review_policy: Mapping[str, Any],
    observation: Mapping[str, Any],
    completion_requested: bool = False,
    verify_evidence: Callable[[str], bool] | None = None,
    current_repository_heads: Mapping[str, str] | None = None,
    knowledge_acquisition_assessment: KnowledgeAcquisitionAssessment | None = None,
) -> ControllerReviewReceipt:
    if review_policy.get("required") is not True:
        raise ControllerReviewAdmissionError("controller review is not enabled")
    agents = registry.get("agents", [])
    expected = {"universal-agent-os"} | {
        item["repository"].split("/")[-1] for item in agents
    }
    dimensions = tuple(review_policy.get("required_dimensions", ()))
    if not dimensions or len(set(dimensions)) != len(dimensions):
        raise ControllerReviewAdmissionError("missing or duplicate required dimensions")
    heads = observation.get("source_heads", ())
    recorded = {row.get("repo") for row in heads}
    if recorded != expected or len(heads) != len(expected):
        raise ControllerReviewAdmissionError("review does not cover current registered repositories")
    if any(not row.get("head") or len(row["head"]) != 40 for row in heads):
        raise ControllerReviewAdmissionError("each source revision must be commit-pinned")
    cells = observation.get("coverage", ())
    seen = set()
    open_findings = []
    for cell in cells:
        key = (cell.get("repo"), cell.get("dimension"))
        if key in seen:
            raise ControllerReviewAdmissionError("duplicate review dimension")
        seen.add(key)
        if not cell.get("source"):
            raise ControllerReviewAdmissionError("review cell has no source")
        if cell.get("assurance") != "DEEP_SCENARIO_VERIFIED":
            open_findings.append(f"{key[0]}:{key[1]}:not-deep-verified")
    required = {(repo, dimension) for repo in expected for dimension in dimensions}
    if required != seen:
        raise ControllerReviewAdmissionError("uncovered or unexpected repository review dimensions")
    method_evidence = observation.get("method_evidence_refs", ())
    challenge_evidence = observation.get("challenge_evidence_refs", ())
    outcome_evidence = observation.get("realistic_validation_refs", ())
    independent_judge = observation.get("independent_judge_refs", ())
    deep_complete = not open_findings and all(
        (method_evidence, challenge_evidence, outcome_evidence, independent_judge)
    )
    if completion_requested:
        if not deep_complete:
            raise ControllerReviewAdmissionError("mapped sources or self-report are insufficient for deep review completion")
        if verify_evidence is None:
            raise ControllerReviewAdmissionError("completion requires a separate evidence verifier")
        references = (
            tuple(method_evidence)
            + tuple(challenge_evidence)
            + tuple(outcome_evidence)
            + tuple(independent_judge)
        )
        if not all(verify_evidence(ref) for ref in references):
            raise ControllerReviewAdmissionError("review completion has unverified evidence")
        # Current revisions and comprehensive learning must be independently supplied
        # by the controlled caller. A historic pinned snapshot is not current coverage.
        if current_repository_heads is None:
            raise ControllerReviewAdmissionError(
                "review completion requires freshly verified registered repository heads"
            )
        pinned_heads = {row["repo"]: row["head"] for row in heads}
        if dict(current_repository_heads) != pinned_heads:
            raise ControllerReviewAdmissionError(
                "review completion source heads differ from current registered revisions"
            )
        if knowledge_acquisition_assessment is None:
            raise ControllerReviewAdmissionError(
                "review completion requires canonical comprehensive knowledge acquisition assessment"
            )
        try:
            require_knowledge_acquisition_admission(
                knowledge_acquisition_assessment, comprehensive=True
            )
        except (KnowledgeAcquisitionAdmissionError, ValueError) as exc:
            raise ControllerReviewAdmissionError(
                f"comprehensive controller learning not admitted: {exc}"
            ) from exc
    return ControllerReviewReceipt(
        recorded_repositories=tuple(sorted(expected)),
        dimensions=dimensions,
        mapped_source_count=len(cells),
        complete=bool(completion_requested and deep_complete),
        open_findings=tuple(open_findings),
    )
