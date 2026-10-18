from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from uaos.contracts.enums import KnowledgeState
from uaos.contracts.models import KnowledgeItem


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
    round_ids = [item.round_id for item in assessment.saturation_rounds]
    if len(round_ids) != len(set(round_ids)):
        raise KnowledgeAcquisitionAdmissionError("saturation round ids must be unique")

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
        if any(not set(item.methods).intersection(_EXPANSION_METHODS) for item in terminal):
            raise KnowledgeAcquisitionAdmissionError(
                "search saturation requires each terminal round to contain expansion work beyond seed/direct lookup"
            )
        terminal_signatures = {
            (
                tuple(sorted(method.value for method in item.methods)),
                tuple(sorted(item.evidence_refs)),
            )
            for item in terminal
        }
        if len(terminal_signatures) < 2:
            raise KnowledgeAcquisitionAdmissionError(
                "search saturation requires two distinct terminal expansion rounds, not repeated evidence/work"
            )
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

# Method transfer belongs to the existing knowledge-acquisition/cognition owner.
# It is an admission check, not a knowledge store, autonomous agent, or policy owner.
class MethodTransferAdmissionError(RuntimeError):
    pass


class MethodTransferDisposition(str, Enum):
    REUSE_CANONICAL_CANDIDATE = "REUSE_CANONICAL_CANDIDATE"
    ADAPT_PROVISIONALLY = "ADAPT_PROVISIONALLY"
    NO_REUSABLE_METHOD = "NO_REUSABLE_METHOD"


@dataclass(frozen=True, slots=True)
class MethodTransferCandidate:
    """One prior method plus *current-case* evidence for fit and misfit."""

    knowledge: KnowledgeItem
    method_family: str
    failure_class: str
    fit_evidence_refs: tuple[str, ...]
    misfit_or_falsification_refs: tuple[str, ...]
    fit_condition: str
    nonfit_condition: str

    def __post_init__(self) -> None:
        if not self.method_family.strip() or not self.failure_class.strip():
            raise ValueError("method family and failure class are required")
        if not self.fit_evidence_refs or not self.misfit_or_falsification_refs:
            raise ValueError("method transfer needs current evidence for both fit and nonfit")
        if not self.fit_condition.strip() or not self.nonfit_condition.strip():
            raise ValueError("method transfer needs explicit fit and nonfit conditions")


@dataclass(frozen=True, slots=True)
class MethodTransferAssessment:
    """Select a method by analogy *and* disanalogy; no prior action is automatically copied."""

    current_problem_ref: str
    target_scope: str
    observed_failure_classes: tuple[str, ...]
    lookup_evidence_refs: tuple[str, ...]
    candidates: tuple[MethodTransferCandidate, ...]
    selected_knowledge_id: str | None
    disposition: MethodTransferDisposition
    novelty_probe_refs: tuple[str, ...]
    selection_rationale: str

    def __post_init__(self) -> None:
        if not self.current_problem_ref.strip() or not self.target_scope.strip():
            raise ValueError("method transfer requires current problem and target scope")
        if not self.observed_failure_classes or not all(x.strip() for x in self.observed_failure_classes):
            raise ValueError("method transfer requires observed failure classes")
        if not self.lookup_evidence_refs or not all(x.strip() for x in self.lookup_evidence_refs):
            raise ValueError("method transfer requires real prior-method lookup evidence")
        if not self.novelty_probe_refs or not all(x.strip() for x in self.novelty_probe_refs):
            raise ValueError("method transfer requires a probe beyond familiar known failures")
        if not self.selection_rationale.strip():
            raise ValueError("method transfer requires a rationale")


@dataclass(frozen=True, slots=True)
class MethodTransferReceipt:
    problem_ref: str
    disposition: MethodTransferDisposition
    selected_knowledge_id: str | None
    inspected_knowledge_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    method_family: str | None


def require_method_transfer_admission(
    assessment: MethodTransferAssessment,
    *,
    verify_current_evidence: Callable[[str], bool] | None,
) -> MethodTransferReceipt:
    """A repeated/systemic case must consciously reuse, adapt, or reject historical methods.

    Reuses the canonical KnowledgeItem lifecycle; refuses a remembered rule with no
    current fit/counterexample evidence. This checks bound evidence identity, not
    semantic truth or live native ChatGPT execution.
    """

    if verify_current_evidence is None:
        raise MethodTransferAdmissionError("method transfer requires current-case evidence verification")
    candidates = assessment.candidates
    ids = [c.knowledge.knowledge_id for c in candidates]
    if len(ids) != len(set(ids)):
        raise MethodTransferAdmissionError("duplicate prior method identities")
    if len(assessment.observed_failure_classes) != len(set(assessment.observed_failure_classes)):
        raise MethodTransferAdmissionError("duplicate observed failure class")

    refs = {
        *assessment.lookup_evidence_refs,
        *assessment.novelty_probe_refs,
        *(ref for candidate in candidates for ref in candidate.fit_evidence_refs),
        *(ref for candidate in candidates for ref in candidate.misfit_or_falsification_refs),
    }
    if not all(verify_current_evidence(ref) for ref in refs):
        raise MethodTransferAdmissionError("method transfer refers to unverified current-case evidence")

    for candidate in candidates:
        if candidate.failure_class not in assessment.observed_failure_classes:
            raise MethodTransferAdmissionError("prior-method analogy references an unobserved failure class")
        if candidate.knowledge.state is KnowledgeState.RETIRED:
            raise MethodTransferAdmissionError("retired knowledge cannot be silently reused")
        if not candidate.knowledge.source_refs:
            raise MethodTransferAdmissionError("prior knowledge lacks source provenance")

    if assessment.disposition is MethodTransferDisposition.NO_REUSABLE_METHOD:
        if assessment.selected_knowledge_id is not None:
            raise MethodTransferAdmissionError("no-reuse disposition cannot select a method")
        return MethodTransferReceipt(
            problem_ref=assessment.current_problem_ref,
            disposition=assessment.disposition,
            selected_knowledge_id=None,
            inspected_knowledge_ids=tuple(ids),
            evidence_refs=tuple(sorted(refs)),
            method_family=None,
        )

    selected = next((item for item in candidates if item.knowledge.knowledge_id == assessment.selected_knowledge_id), None)
    if selected is None:
        raise MethodTransferAdmissionError("reuse/adaptation requires a known selected method")
    if selected.knowledge.applicable_scope not in {"GLOBAL", "UAOS", assessment.target_scope}:
        raise MethodTransferAdmissionError("selected knowledge scope does not match this authority")
    if assessment.disposition is MethodTransferDisposition.REUSE_CANONICAL_CANDIDATE:
        if selected.knowledge.state is not KnowledgeState.CANONICAL or not selected.knowledge.usage_links:
            raise MethodTransferAdmissionError("canonical reuse candidate requires an already promoted method and a prior-use reference; reference reality still needs a trusted host verifier")
    elif assessment.disposition is MethodTransferDisposition.ADAPT_PROVISIONALLY:
        if selected.knowledge.state is KnowledgeState.RAW_EVIDENCE:
            raise MethodTransferAdmissionError("raw unevaluated knowledge may not be transferred as a selected method")
    else:
        raise MethodTransferAdmissionError("unsupported method transfer disposition")

    return MethodTransferReceipt(
        problem_ref=assessment.current_problem_ref,
        disposition=assessment.disposition,
        selected_knowledge_id=selected.knowledge.knowledge_id,
        inspected_knowledge_ids=tuple(ids),
        evidence_refs=tuple(sorted(refs)),
        method_family=selected.method_family,
    )
