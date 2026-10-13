from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Mapping


def utcnow() -> datetime:
    return datetime.now(UTC)


class ProposalState(StrEnum):
    DRAFT = "DRAFT"
    EVALUATED = "EVALUATED"
    APPROVED = "APPROVED"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"
    RETIRED = "RETIRED"


class MaintenanceRisk(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True, slots=True)
class Incident:
    incident_id: str
    summary: str
    fingerprint: str
    evidence_refs: tuple[str, ...]
    severity: str = "MEDIUM"
    task_id: str | None = None
    domain_id: str | None = None
    occurred_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if not all((self.incident_id.strip(), self.summary.strip(), self.fingerprint.strip())):
            raise ValueError("incident identity, summary and fingerprint are required")
        if not self.evidence_refs:
            raise ValueError("incident requires evidence")


@dataclass(frozen=True, slots=True)
class FailureClass:
    failure_class_id: str
    name: str
    root_layer: str
    incident_ids: tuple[str, ...]
    hypothesis: str

    def __post_init__(self) -> None:
        if not all((self.failure_class_id.strip(), self.name.strip(), self.root_layer.strip(), self.hypothesis.strip())):
            raise ValueError("failure class identity, name, root layer and hypothesis are required")
        if not self.incident_ids:
            raise ValueError("failure class requires incident evidence")
        if len(self.incident_ids) != len(set(self.incident_ids)):
            raise ValueError("duplicate incident in failure class")


@dataclass(frozen=True, slots=True)
class ComplexityDelta:
    added_components: int = 0
    removed_components: int = 0
    added_state_surfaces: int = 0
    removed_state_surfaces: int = 0
    maintenance_cost_delta: int = 0

    def __post_init__(self) -> None:
        if min(self.added_components, self.removed_components, self.added_state_surfaces, self.removed_state_surfaces) < 0:
            raise ValueError("complexity counts cannot be negative")

    @property
    def net_components(self) -> int:
        return self.added_components - self.removed_components

    @property
    def net_state_surfaces(self) -> int:
        return self.added_state_surfaces - self.removed_state_surfaces


@dataclass(frozen=True, slots=True)
class ChangeProposal:
    proposal_id: str
    title: str
    failure_class_ids: tuple[str, ...]
    hypothesis: str
    target_scope: str
    added_mechanisms: tuple[str, ...]
    replaced_mechanisms: tuple[str, ...]
    retired_mechanisms: tuple[str, ...]
    why_not_reuse: str
    retirement_rationale: str
    rollback_plan: str
    expected_benefit: str
    new_failure_modes: tuple[str, ...]
    required_scenarios: tuple[str, ...]
    complexity_delta: ComplexityDelta
    evidence_refs: tuple[str, ...]
    state: ProposalState = ProposalState.DRAFT

    def __post_init__(self) -> None:
        required = (self.proposal_id, self.title, self.hypothesis, self.target_scope, self.rollback_plan, self.expected_benefit)
        if not all(value.strip() for value in required):
            raise ValueError("proposal identity, hypothesis, scope, rollback and expected benefit are required")
        if not self.failure_class_ids:
            raise ValueError("proposal must address at least one failure class")
        if not self.evidence_refs:
            raise ValueError("proposal requires evidence")
        if not self.required_scenarios:
            raise ValueError("proposal requires explicit evaluation scenarios")
        if len(self.failure_class_ids) != len(set(self.failure_class_ids)):
            raise ValueError("duplicate failure class in proposal")
        if self.added_mechanisms and not self.why_not_reuse.strip():
            raise ValueError("new mechanisms require why-not-reuse analysis")
        if self.added_mechanisms and not self.retirement_rationale.strip():
            raise ValueError("new mechanisms require explicit retirement/overlap rationale")


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    evaluation_id: str
    proposal_id: str
    scenario_refs: tuple[str, ...]
    metrics_before: Mapping[str, float]
    metrics_after: Mapping[str, float]
    acceptance_checks: Mapping[str, bool]
    regression_failures: tuple[str, ...] = ()
    passed: bool = False
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.evaluation_id.strip() or not self.proposal_id.strip():
            raise ValueError("evaluation identity is required")
        if not self.scenario_refs:
            raise ValueError("evaluation requires reproducible scenarios")
        if not self.evidence_refs:
            raise ValueError("evaluation requires evidence")
        if not self.acceptance_checks:
            raise ValueError("evaluation requires explicit acceptance checks")
        if self.passed and not all(self.acceptance_checks.values()):
            raise ValueError("passing evaluation cannot contain failed acceptance checks")


@dataclass(frozen=True, slots=True)
class ComplexityBudget:
    max_net_components: int = 2
    max_net_state_surfaces: int = 1
    max_maintenance_cost_delta: int = 2


@dataclass(frozen=True, slots=True)
class PromotionAuthorization:
    proposal_id: str
    approved: bool
    reasons: tuple[str, ...]
    required_action_route: str = "execution.action_authority"


@dataclass(frozen=True, slots=True)
class PostPromotionObservation:
    observation_id: str
    proposal_id: str
    healthy: bool
    metrics: Mapping[str, float]
    evidence_refs: tuple[str, ...]
    regression_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.observation_id.strip() or not self.proposal_id.strip():
            raise ValueError("observation identity is required")
        if not self.evidence_refs:
            raise ValueError("post-promotion observation requires evidence")


@dataclass(frozen=True, slots=True)
class MaintenanceRequest:
    maintenance_id: str
    scope: str
    trigger: str
    risk: MaintenanceRisk
    background_capability_available: bool
    foreground_priority_active: bool
    production_mutation_requested: bool = False
    explicit_approval_id: str | None = None


@dataclass(frozen=True, slots=True)
class MaintenanceDecision:
    allowed: bool
    mode: str
    reasons: tuple[str, ...]
