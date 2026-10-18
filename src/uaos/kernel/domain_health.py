from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable
from enum import Enum

from .problem_space import CapabilityDiscoveryReceipt
from .scheduling import RunnableWork, ScheduleSelection, select_non_conflicting


class HealthFindingType(str, Enum):
    PARENT_CHILD_REVISION_DRIFT = "PARENT_CHILD_REVISION_DRIFT"
    COMMON_BEHAVIOR_BINDING_MISSING = "COMMON_BEHAVIOR_BINDING_MISSING"
    DECLARED_WITHOUT_OPERATIONAL_EVIDENCE = "DECLARED_WITHOUT_OPERATIONAL_EVIDENCE"
    CANONICAL_EVOLUTION_INTERFACE_MISSING = "CANONICAL_EVOLUTION_INTERFACE_MISSING"
    SCENARIO_OR_RECOVERY_GAP = "SCENARIO_OR_RECOVERY_GAP"
    PRODUCT_OUTCOME_VALIDATION_GAP = "PRODUCT_OUTCOME_VALIDATION_GAP"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


_SEVERITY_PRIORITY = {
    Severity.LOW: 100,
    Severity.MEDIUM: 200,
    Severity.HIGH: 300,
    Severity.CRITICAL: 400,
}


@dataclass(frozen=True, slots=True)
class DomainObservation:
    domain_id: str
    current_revision: str
    parent_observed_revision: str | None = None
    common_behavior_required: bool = False
    common_behavior_binding_present: bool = False
    inherited_behavior_claims: tuple[str, ...] = ()
    operational_evidence_capabilities: tuple[str, ...] = ()
    canonical_evolution_interface_required: bool = False
    canonical_evolution_interface_present: bool = False
    material_change_pending: bool = False
    failure_recovery_scenario_evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.domain_id.strip() or not self.current_revision.strip():
            raise ValueError("domain_id and current_revision are required")
        if any(not ref.strip() for ref in self.failure_recovery_scenario_evidence_refs):
            raise ValueError("failure/recovery scenario evidence refs must be non-empty")


@dataclass(frozen=True, slots=True)
class DomainHealthFinding:
    domain_id: str
    finding_type: HealthFindingType
    severity: Severity
    summary: str
    capability_id: str | None = None


@dataclass(frozen=True, slots=True)
class DomainHealthReceipt:
    domain_id: str
    findings: tuple[DomainHealthFinding, ...]

    @property
    def healthy(self) -> bool:
        return not self.findings


@dataclass(frozen=True, slots=True)
class ProductOutcomeEvidence:
    """Owner-sourced validation record, separate from passing code/CI verification.

    This is an optional *governing outcome* check provided by a trusted parent
    caller after reading the live child source. It is not a universal requirement
    for all registered domains and cannot infer user satisfaction from a test run.
    """
    domain_id: str
    child_revision: str
    objective_ref: str
    required_dimensions: tuple[str, ...]
    dimension_evidence: tuple[tuple[str, str], ...] = ()
    independently_adjudicated_outcome_ref: str | None = None
    open_rejection_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.domain_id.strip() or not self.child_revision.strip() or not self.objective_ref.strip():
            raise ValueError("product outcome must identify domain, revision and objective")
        if not self.required_dimensions or len(set(self.required_dimensions)) != len(self.required_dimensions):
            raise ValueError("product outcome requires unique acceptance dimensions")
        names = [dimension for dimension, _ in self.dimension_evidence]
        if len(names) != len(set(names)) or any(not name.strip() or not ref.strip() for name, ref in self.dimension_evidence):
            raise ValueError("product outcome evidence requires unique dimension names and refs")


def assess_product_outcome(
    observation: DomainObservation,
    product: ProductOutcomeEvidence,
    *,
    verify_evidence: Callable[[str], bool] | None,
) -> DomainHealthReceipt:
    """Fail the *outcome assurance* claim until current independent evidence exists.

    A child repair can be production verified while this outcome remains OPEN.
    The verifier must resolve refs against source/host receipts independently of
    caller-provided PASS strings. Product declarations have no blanket authority.
    """
    if product.domain_id != observation.domain_id:
        raise ValueError("product outcome domain mismatch")
    findings: list[DomainHealthFinding] = []
    reasons: list[str] = []
    if product.child_revision != observation.current_revision:
        reasons.append("outcome proof is not bound to the current child revision")
    observed = dict(product.dimension_evidence)
    expected = set(product.required_dimensions)
    extras = sorted(set(observed) - expected)
    missing = sorted(expected - set(observed))
    if missing:
        reasons.append(f"required outcome dimensions missing: {missing}")
    if extras:
        reasons.append(f"unrecognized outcome dimensions: {extras}")
    if product.open_rejection_refs:
        reasons.append("open user rejection or material failure is not adjudicated")
    if product.independently_adjudicated_outcome_ref is None:
        reasons.append("no independent or real user outcome adjudication")
    refs = (product.objective_ref, *observed.values())
    if product.independently_adjudicated_outcome_ref is not None:
        refs += (product.independently_adjudicated_outcome_ref,)
    if verify_evidence is None:
        reasons.append("trusted evidence verifier absent")
    else:
        for ref in refs:
            try:
                verified = bool(verify_evidence(ref))
            except Exception:
                verified = False
            if not verified:
                reasons.append(f"outcome evidence not independently verified: {ref}")
    if reasons:
        findings.append(DomainHealthFinding(
            observation.domain_id,
            HealthFindingType.PRODUCT_OUTCOME_VALIDATION_GAP,
            Severity.HIGH,
            "; ".join(reasons),
            capability_id="outcome_validation",
        ))
    return DomainHealthReceipt(observation.domain_id, tuple(findings))


def require_product_outcome_completion(
    observation: DomainObservation,
    product: ProductOutcomeEvidence,
    *,
    verify_evidence: Callable[[str], bool] | None,
) -> DomainHealthReceipt:
    """Controlled parent completion admission; never conflate product and CI."""
    receipt = assess_product_outcome(observation, product, verify_evidence=verify_evidence)
    if not receipt.healthy:
        raise ValueError(f"product outcome not validated: {receipt.findings[0].summary}")
    return receipt


def assess_domain_health(observation: DomainObservation) -> DomainHealthReceipt:
    """Assess parent/child control-plane health from current owner evidence.

    A parent observation is deliberately treated as a cache. A mismatch is a
    health finding; it never rewrites or downgrades current child authority.
    Material change readiness is also checked before execution: if the owner
    cannot show a failure/recovery scenario for a pending material change, the
    gap is surfaced before a real incident is needed to reveal it.
    """

    findings: list[DomainHealthFinding] = []

    parent_revision = (observation.parent_observed_revision or "").strip()
    if parent_revision and parent_revision != observation.current_revision:
        findings.append(
            DomainHealthFinding(
                observation.domain_id,
                HealthFindingType.PARENT_CHILD_REVISION_DRIFT,
                Severity.HIGH,
                f"parent observation {parent_revision} differs from current child {observation.current_revision}",
            )
        )

    if observation.common_behavior_required and not observation.common_behavior_binding_present:
        findings.append(
            DomainHealthFinding(
                observation.domain_id,
                HealthFindingType.COMMON_BEHAVIOR_BINDING_MISSING,
                Severity.HIGH,
                "common behavior assurance is required but no current child binding is present",
            )
        )

    evidence = set(observation.operational_evidence_capabilities)
    for capability_id in sorted(set(observation.inherited_behavior_claims)):
        if capability_id not in evidence:
            findings.append(
                DomainHealthFinding(
                    observation.domain_id,
                    HealthFindingType.DECLARED_WITHOUT_OPERATIONAL_EVIDENCE,
                    Severity.MEDIUM,
                    "inherited behavior is declared but lacks current owner-native operational evidence",
                    capability_id=capability_id,
                )
            )

    if observation.canonical_evolution_interface_required and not observation.canonical_evolution_interface_present:
        findings.append(
            DomainHealthFinding(
                observation.domain_id,
                HealthFindingType.CANONICAL_EVOLUTION_INTERFACE_MISSING,
                Severity.MEDIUM,
                "material/open evolution exists but no canonical child evolution evidence entrypoint is exposed",
            )
        )

    if observation.material_change_pending and not observation.failure_recovery_scenario_evidence_refs:
        findings.append(
            DomainHealthFinding(
                observation.domain_id,
                HealthFindingType.SCENARIO_OR_RECOVERY_GAP,
                Severity.HIGH,
                "material change is pending without owner-native pre-change failure/recovery scenario evidence",
            )
        )

    return DomainHealthReceipt(observation.domain_id, tuple(findings))


@dataclass(frozen=True, slots=True)
class ParentUpcall:
    escalation_id: str
    domain_id: str
    domain_revision: str
    problem_ref: str
    severity: Severity
    impact: str
    blocking_scope: str
    suspected_layer: str
    evidence_refs: tuple[str, ...]
    local_recovery_attempts: tuple[str, ...]
    requested_parent_help: str
    can_continue_unaffected_work: bool
    conflict_keys: tuple[str, ...] = ()
    failure_class: str | None = None
    capability_id: str | None = None
    urgency: int = 50
    blast_radius: int = 1

    def __post_init__(self) -> None:
        required = (
            self.escalation_id,
            self.domain_id,
            self.domain_revision,
            self.problem_ref,
            self.impact,
            self.blocking_scope,
            self.suspected_layer,
            self.requested_parent_help,
        )
        if not all(value.strip() for value in required):
            raise ValueError("material parent upcall requires complete identity, impact, scope, layer and help request")
        if not self.evidence_refs:
            raise ValueError("material parent upcall requires evidence_refs")
        if not 0 <= self.urgency <= 100:
            raise ValueError("urgency must be between 0 and 100")
        if self.blast_radius < 1:
            raise ValueError("blast_radius must be >= 1")
        if len(self.conflict_keys) != len(set(self.conflict_keys)):
            raise ValueError("duplicate conflict key")

    def as_runnable_work(self) -> RunnableWork:
        priority = _SEVERITY_PRIORITY[self.severity] + self.urgency + min(self.blast_radius, 50)
        return RunnableWork(
            task_id=f"parent-guidance:{self.domain_id}",
            work_unit_id=self.escalation_id,
            task_priority=priority,
            work_priority=100,
            resource_keys=self.conflict_keys,
            work_class="FOREGROUND",
        )


def triage_parent_upcalls(upcalls: tuple[ParentUpcall, ...], *, max_slots: int) -> ScheduleSelection:
    """Bulkhead parent guidance by selecting every non-conflicting high-value upcall."""

    works = tuple(upcall.as_runnable_work() for upcall in upcalls)
    return select_non_conflicting(works, max_slots=max_slots)


@dataclass(frozen=True, slots=True)
class FailureCluster:
    cluster_key: str
    escalation_ids: tuple[str, ...]
    domain_ids: tuple[str, ...]


def cluster_cross_domain_failures(upcalls: tuple[ParentUpcall, ...], *, minimum_domains: int = 2) -> tuple[FailureCluster, ...]:
    if minimum_domains < 2:
        raise ValueError("minimum_domains must be >= 2")

    grouped: dict[str, list[ParentUpcall]] = defaultdict(list)
    for upcall in upcalls:
        if upcall.failure_class and upcall.failure_class.strip():
            key = f"failure_class:{upcall.failure_class.strip()}"
        elif upcall.capability_id and upcall.capability_id.strip():
            key = f"capability:{upcall.capability_id.strip()}|layer:{upcall.suspected_layer.strip()}"
        else:
            continue
        grouped[key].append(upcall)

    clusters: list[FailureCluster] = []
    for key, members in sorted(grouped.items()):
        domains = tuple(sorted({member.domain_id for member in members}))
        if len(domains) < minimum_domains:
            continue
        clusters.append(
            FailureCluster(
                cluster_key=key,
                escalation_ids=tuple(sorted(member.escalation_id for member in members)),
                domain_ids=domains,
            )
        )
    return tuple(clusters)


@dataclass(frozen=True, slots=True)
class ExternalSkillCandidate:
    skill_id: str
    source_ref: str
    mapped_need_or_failure_class: str
    source_inspected: bool
    companion_files_inspected: bool
    security_and_permissions_reviewed: bool
    existing_overlap_assessed: bool
    evaluation_refs: tuple[str, ...]
    discovered_capability_gap: str | None = None
    discovery_receipt: CapabilityDiscoveryReceipt | None = None


@dataclass(frozen=True, slots=True)
class ExternalSkillAdmission:
    promotable_candidate: bool
    missing_evidence: tuple[str, ...]


def assess_external_skill_candidate(candidate: ExternalSkillCandidate) -> ExternalSkillAdmission:
    """Keep marketplace Skills as evidence-bound candidates, never authority by popularity.

    A candidate may be pulled from an already-known need/failure class or from an
    outside-in discovery receipt that established a previously unnamed capability gap.
    Broad catalog learning therefore does not have to pretend the gap was known first.
    """

    if not candidate.skill_id.strip() or not candidate.source_ref.strip():
        raise ValueError("skill_id and source_ref are required")

    known_need = candidate.mapped_need_or_failure_class.strip()
    discovered_gap = (candidate.discovered_capability_gap or "").strip()
    if not known_need:
        if not discovered_gap or candidate.discovery_receipt is None:
            raise ValueError(
                "candidate requires either a mapped known need/failure class or an outside-in discovered capability gap with receipt"
            )
        if discovered_gap not in candidate.discovery_receipt.latent_gap_candidates:
            raise ValueError("discovered capability gap must be present in the discovery receipt")

    missing: list[str] = []
    checks = {
        "source_inspected": candidate.source_inspected,
        "companion_files_inspected": candidate.companion_files_inspected,
        "security_and_permissions_reviewed": candidate.security_and_permissions_reviewed,
        "existing_overlap_assessed": candidate.existing_overlap_assessed,
        "bounded_evaluation": bool(candidate.evaluation_refs),
    }
    for name, passed in checks.items():
        if not passed:
            missing.append(name)
    return ExternalSkillAdmission(not missing, tuple(missing))
