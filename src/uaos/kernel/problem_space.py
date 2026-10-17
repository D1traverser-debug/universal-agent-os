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


class KnowledgeAcquisitionAdmissionError(RuntimeError):
    """Raised when broad learning claims coverage without an evidence-complete search trace."""


class KnowledgeSourceRole(str, Enum):
    CURRENT_OR_PRIMARY_AUTHORITY = "CURRENT_OR_PRIMARY_AUTHORITY"
    INDEPENDENT_RESEARCH_OR_BENCHMARK = "INDEPENDENT_RESEARCH_OR_BENCHMARK"
    PROFESSIONAL_METHOD = "PROFESSIONAL_METHOD"
    IMPLEMENTATION_EVIDENCE = "IMPLEMENTATION_EVIDENCE"
    DISCOVERY_INDEX = "DISCOVERY_INDEX"
    COMMUNITY_SIGNAL = "COMMUNITY_SIGNAL"


class AcquisitionMethod(str, Enum):
    DIRECT_SEARCH = "DIRECT_SEARCH"
    SOURCE_NATIVE_BROWSE = "SOURCE_NATIVE_BROWSE"
    QUERY_EXPANSION = "QUERY_EXPANSION"
    BACKWARD_REFERENCE = "BACKWARD_REFERENCE"
    FORWARD_REFERENCE = "FORWARD_REFERENCE"
    REPOSITORY_TRAVERSAL = "REPOSITORY_TRAVERSAL"
    ADJACENT_LENS = "ADJACENT_LENS"
    COMMUNITY_SCAN = "COMMUNITY_SCAN"


class ContradictionDisposition(str, Enum):
    RESOLVED = "RESOLVED"
    BOUNDED = "BOUNDED"


@dataclass(frozen=True, slots=True)
class KnowledgeSource:
    source_id: str
    source_ref: str
    role: KnowledgeSourceRole
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.source_ref.strip():
            raise ValueError("knowledge source identity and reference are required")
        if not self.evidence_refs or not all(ref.strip() for ref in self.evidence_refs):
            raise ValueError("knowledge source requires evidence references")


@dataclass(frozen=True, slots=True)
class AcquisitionProbe:
    probe_id: str
    method: AcquisitionMethod
    query_or_path: str
    finding: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.probe_id.strip() or not self.query_or_path.strip() or not self.finding.strip():
            raise ValueError("acquisition probe identity, query/path and finding are required")
        if not self.evidence_refs or not all(ref.strip() for ref in self.evidence_refs):
            raise ValueError("acquisition probe requires evidence references")


@dataclass(frozen=True, slots=True)
class MethodFamily:
    family_id: str
    statement: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.family_id.strip() or not self.statement.strip():
            raise ValueError("method family identity and statement are required")
        if not self.evidence_refs or not all(ref.strip() for ref in self.evidence_refs):
            raise ValueError("method family requires evidence references")


@dataclass(frozen=True, slots=True)
class Contradiction:
    contradiction_id: str
    statement: str
    disposition: ContradictionDisposition
    evidence_refs: tuple[str, ...]
    resolution: str

    def __post_init__(self) -> None:
        if not self.contradiction_id.strip() or not self.statement.strip() or not self.resolution.strip():
            raise ValueError("contradiction identity, statement and resolution/boundary are required")
        if not self.evidence_refs or not all(ref.strip() for ref in self.evidence_refs):
            raise ValueError("contradiction requires evidence references")


@dataclass(frozen=True, slots=True)
class SaturationRound:
    round_id: str
    methods: tuple[AcquisitionMethod, ...]
    new_method_families: tuple[str, ...]
    new_failure_modes: tuple[str, ...]
    new_constraints: tuple[str, ...]
    material_decision_change: bool
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.round_id.strip() or not self.methods:
            raise ValueError("saturation round identity and methods are required")
        if not self.evidence_refs or not all(ref.strip() for ref in self.evidence_refs):
            raise ValueError("saturation round requires evidence references")
        groups = (self.new_method_families, self.new_failure_modes, self.new_constraints)
        if not all(all(item.strip() for item in group) for group in groups):
            raise ValueError("saturation novelty fields cannot contain blank values")

    @property
    def materially_novel(self) -> bool:
        return bool(
            self.new_method_families
            or self.new_failure_modes
            or self.new_constraints
            or self.material_decision_change
        )


@dataclass(frozen=True, slots=True)
class KnowledgeAcquisitionAssessment:
    acquisition_id: str
    objective: str
    knowledge_modules: tuple[str, ...]
    required_source_roles: tuple[KnowledgeSourceRole, ...]
    sources: tuple[KnowledgeSource, ...]
    probes: tuple[AcquisitionProbe, ...]
    method_families: tuple[MethodFamily, ...]
    contradictions: tuple[Contradiction, ...]
    saturation_rounds: tuple[SaturationRound, ...]
    stop_reason: str
    holdout_or_validation_plan: str

    def __post_init__(self) -> None:
        if not self.acquisition_id.strip() or not self.objective.strip():
            raise ValueError("knowledge acquisition identity and objective are required")
        if not self.knowledge_modules or not all(item.strip() for item in self.knowledge_modules):
            raise ValueError("knowledge acquisition requires non-empty knowledge modules")
        if not self.required_source_roles:
            raise ValueError("knowledge acquisition requires declared source roles")
        if not self.stop_reason.strip() or not self.holdout_or_validation_plan.strip():
            raise ValueError("knowledge acquisition requires stop reason and holdout/validation plan")


@dataclass(frozen=True, slots=True)
class KnowledgeAcquisitionReceipt:
    acquisition_id: str
    source_roles: tuple[KnowledgeSourceRole, ...]
    acquisition_methods: tuple[AcquisitionMethod, ...]
    method_family_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    stop_reason: str


_EXPANSION_METHODS = {
    AcquisitionMethod.QUERY_EXPANSION,
    AcquisitionMethod.BACKWARD_REFERENCE,
    AcquisitionMethod.FORWARD_REFERENCE,
    AcquisitionMethod.REPOSITORY_TRAVERSAL,
    AcquisitionMethod.ADJACENT_LENS,
}
_DISCOVERY_ONLY_ROLES = {
    KnowledgeSourceRole.DISCOVERY_INDEX,
    KnowledgeSourceRole.COMMUNITY_SIGNAL,
}


def require_knowledge_acquisition_admission(
    assessment: KnowledgeAcquisitionAssessment,
    *,
    comprehensive: bool = True,
) -> KnowledgeAcquisitionReceipt:
    """Admit evidence that broad learning covered, expanded, challenged and saturated.

    This is an evidence profile for research/learning quality. It does not choose the
    business conclusion, causal model or intervention, and therefore does not create a
    second cognition state machine. Narrow known-need lookups may use comprehensive=False.
    """

    source_ids = [item.source_id for item in assessment.sources]
    if len(source_ids) != len(set(source_ids)):
        raise KnowledgeAcquisitionAdmissionError("knowledge source ids must be unique")
    probe_ids = [item.probe_id for item in assessment.probes]
    if len(probe_ids) != len(set(probe_ids)):
        raise KnowledgeAcquisitionAdmissionError("acquisition probe ids must be unique")
    family_ids = [item.family_id for item in assessment.method_families]
    if len(family_ids) != len(set(family_ids)):
        raise KnowledgeAcquisitionAdmissionError("method family ids must be unique")

    observed_roles = {item.role for item in assessment.sources}
    missing_roles = tuple(role for role in assessment.required_source_roles if role not in observed_roles)
    if missing_roles:
        raise KnowledgeAcquisitionAdmissionError(
            "required source roles are uncovered: " + ",".join(role.value for role in missing_roles)
        )

    observed_methods = {item.method for item in assessment.probes}
    if not assessment.probes:
        raise KnowledgeAcquisitionAdmissionError("knowledge acquisition requires evidence probes")

    if comprehensive:
        if KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY not in observed_roles:
            raise KnowledgeAcquisitionAdmissionError(
                "comprehensive acquisition requires current/primary authority evidence"
            )
        substantive_roles = observed_roles - _DISCOVERY_ONLY_ROLES - {
            KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY
        }
        if not substantive_roles:
            raise KnowledgeAcquisitionAdmissionError(
                "comprehensive acquisition requires evidence beyond primary authority and discovery/community signals"
            )
        if len(observed_methods) < 2:
            raise KnowledgeAcquisitionAdmissionError(
                "comprehensive acquisition requires at least two acquisition methods"
            )
        if not observed_methods.intersection(_EXPANSION_METHODS):
            raise KnowledgeAcquisitionAdmissionError(
                "comprehensive acquisition requires query/reference/repository/adjacent expansion beyond seed search"
            )
        if len(assessment.method_families) < 2:
            raise KnowledgeAcquisitionAdmissionError(
                "comprehensive method/framework learning requires at least two competing method families"
            )
        if len(assessment.saturation_rounds) < 2:
            raise KnowledgeAcquisitionAdmissionError(
                "comprehensive acquisition requires at least two documented saturation rounds"
            )
        terminal = assessment.saturation_rounds[-2:]
        if any(item.materially_novel for item in terminal):
            raise KnowledgeAcquisitionAdmissionError(
                "search saturation is not established: a terminal expansion round still changed the method/failure/constraint space"
            )

    evidence_refs = tuple(sorted({
        *(ref for item in assessment.sources for ref in item.evidence_refs),
        *(ref for item in assessment.probes for ref in item.evidence_refs),
        *(ref for item in assessment.method_families for ref in item.evidence_refs),
        *(ref for item in assessment.contradictions for ref in item.evidence_refs),
        *(ref for item in assessment.saturation_rounds for ref in item.evidence_refs),
    }))
    if not evidence_refs:
        raise KnowledgeAcquisitionAdmissionError("knowledge acquisition requires evidence references")

    return KnowledgeAcquisitionReceipt(
        acquisition_id=assessment.acquisition_id,
        source_roles=tuple(sorted(observed_roles, key=lambda item: item.value)),
        acquisition_methods=tuple(sorted(observed_methods, key=lambda item: item.value)),
        method_family_ids=tuple(family_ids),
        evidence_refs=evidence_refs,
        stop_reason=assessment.stop_reason,
    )
