from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CapabilityDiscoveryAdmissionError(RuntimeError):
    """Raised when broad capability discovery collapses back to known-need search."""


class DiscoveryLens(str, Enum):
    ROLE_OR_OCCUPATION = "ROLE_OR_OCCUPATION"
    TASK_OR_ACTIVITY = "TASK_OR_ACTIVITY"
    WORKFLOW_OR_HANDOFF = "WORKFLOW_OR_HANDOFF"
    CATEGORY_OR_TAXONOMY = "CATEGORY_OR_TAXONOMY"
    CREATOR_OR_PORTFOLIO = "CREATOR_OR_PORTFOLIO"
    REPOSITORY_OR_PORTFOLIO = "REPOSITORY_OR_PORTFOLIO"
    ADJACENT_DOMAIN = "ADJACENT_DOMAIN"


@dataclass(frozen=True, slots=True)
class ExternalSourceModel:
    source_id: str
    source_ref: str
    organization_axes: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.source_ref.strip():
            raise ValueError("source identity and reference are required")
        if not self.organization_axes or not all(axis.strip() for axis in self.organization_axes):
            raise ValueError("source model requires at least one organization axis")
        if not self.evidence_refs or not all(ref.strip() for ref in self.evidence_refs):
            raise ValueError("source model requires evidence references")


@dataclass(frozen=True, slots=True)
class DiscoveryProbe:
    lens: DiscoveryLens
    finding: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.finding.strip():
            raise ValueError("discovery probe finding is required")
        if not self.evidence_refs or not all(ref.strip() for ref in self.evidence_refs):
            raise ValueError("discovery probe requires evidence references")


@dataclass(frozen=True, slots=True)
class CapabilityDiscoveryAssessment:
    objective: str
    source_model: ExternalSourceModel
    probes: tuple[DiscoveryProbe, ...]
    latent_gap_candidates: tuple[str, ...]
    known_need_seeded_only: bool = False

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("capability discovery objective is required")
        if not all(gap.strip() for gap in self.latent_gap_candidates):
            raise ValueError("latent gap candidates cannot contain empty values")


@dataclass(frozen=True, slots=True)
class CapabilityDiscoveryReceipt:
    source_id: str
    source_axes: tuple[str, ...]
    lenses: tuple[DiscoveryLens, ...]
    latent_gap_candidates: tuple[str, ...]
    evidence_refs: tuple[str, ...]


def require_outside_in_capability_discovery(
    assessment: CapabilityDiscoveryAssessment,
    *,
    broad_discovery: bool = True,
) -> CapabilityDiscoveryReceipt:
    """Admit outside-in discovery without turning one example/lens into authority.

    Broad discovery is for questions such as "what capabilities are we missing?" or
    "how should this source be used?". It first models how the source organizes its
    knowledge, then samples multiple independent lenses before naming latent gaps.
    Specific known-need lookups should not be forced through this heavier path.
    """

    axes = tuple(dict.fromkeys(axis.strip() for axis in assessment.source_model.organization_axes))
    lenses = tuple(sorted({probe.lens for probe in assessment.probes}, key=lambda item: item.value))

    if broad_discovery:
        if assessment.known_need_seeded_only:
            raise CapabilityDiscoveryAdmissionError(
                "broad capability discovery cannot be only a known-need/keyword search"
            )
        if len(axes) < 2:
            raise CapabilityDiscoveryAdmissionError(
                "broad capability discovery requires a source-affordance model with at least two organization axes"
            )
        if len(lenses) < 2:
            raise CapabilityDiscoveryAdmissionError(
                "broad capability discovery requires at least two distinct outside-in lenses"
            )
        if not assessment.latent_gap_candidates:
            raise CapabilityDiscoveryAdmissionError(
                "broad capability discovery must produce at least one evidence-grounded latent capability gap candidate"
            )
    elif not assessment.probes:
        raise CapabilityDiscoveryAdmissionError("capability discovery requires at least one evidence probe")

    evidence_refs = tuple(sorted({
        *assessment.source_model.evidence_refs,
        *(ref for probe in assessment.probes for ref in probe.evidence_refs),
    }))
    return CapabilityDiscoveryReceipt(
        source_id=assessment.source_model.source_id,
        source_axes=axes,
        lenses=lenses,
        latent_gap_candidates=tuple(dict.fromkeys(assessment.latent_gap_candidates)),
        evidence_refs=evidence_refs,
    )
