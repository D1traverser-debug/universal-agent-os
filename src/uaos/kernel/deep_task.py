from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cognition_case import EvidenceItem, EvidenceKind
from .problem_space import (
    KnowledgeAcquisitionAssessment,
    KnowledgeAcquisitionReceipt,
    require_knowledge_acquisition_admission,
)


class DeepTaskAdmissionError(RuntimeError):
    """Raised when a task claims deep execution without the required evidence trace."""


class DeepTaskAlternativeDisposition(str, Enum):
    PLAUSIBLE = "PLAUSIBLE"
    PREFERRED = "PREFERRED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class DeepTaskSignals:
    """Semantic trigger signals supplied by a compatible host before finalization."""

    explicit_user_depth_request: bool = False
    material_high_uncertainty: bool = False
    unknown_knowledge: bool = False
    architecture_or_control_plane: bool = False
    repeated_systemic: bool = False
    ordinary_structured_evidence_insufficient: bool = False
    comprehensive_knowledge_acquisition_required: bool = False


@dataclass(frozen=True, slots=True)
class DeepTaskRequirement:
    required: bool
    reason_codes: tuple[str, ...]


def assess_deep_task_requirement(signals: DeepTaskSignals) -> DeepTaskRequirement:
    """Derive deep-task activation from semantic signals, not wording heuristics."""

    reasons: list[str] = []
    if signals.explicit_user_depth_request:
        reasons.append("EXPLICIT_USER_DEPTH_REQUEST")
    if signals.material_high_uncertainty:
        reasons.append("MATERIAL_HIGH_UNCERTAINTY")
    if signals.unknown_knowledge:
        reasons.append("UNKNOWN_KNOWLEDGE")
    if signals.architecture_or_control_plane:
        reasons.append("ARCHITECTURE_OR_CONTROL_PLANE")
    if signals.repeated_systemic:
        reasons.append("REPEATED_SYSTEMIC")
    if signals.ordinary_structured_evidence_insufficient:
        reasons.append("ORDINARY_STRUCTURED_EVIDENCE_INSUFFICIENT")
    if signals.comprehensive_knowledge_acquisition_required:
        reasons.append("COMPREHENSIVE_KNOWLEDGE_ACQUISITION_REQUIRED")

    escalated_material = bool(
        signals.ordinary_structured_evidence_insufficient
        and any(
            (
                signals.material_high_uncertainty,
                signals.unknown_knowledge,
                signals.architecture_or_control_plane,
                signals.repeated_systemic,
            )
        )
    )
    return DeepTaskRequirement(
        required=bool(
            signals.explicit_user_depth_request
            or signals.comprehensive_knowledge_acquisition_required
            or escalated_material
        ),
        reason_codes=tuple(reasons),
    )


@dataclass(frozen=True, slots=True)
class DeepTaskAlternative:
    alternative_id: str
    statement: str
    disposition: DeepTaskAlternativeDisposition
    supporting_evidence_ids: tuple[str, ...]
    falsification_condition: str
    falsification_evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.alternative_id.strip() or not self.statement.strip():
            raise ValueError("deep-task alternative identity and statement are required")
        if not self.supporting_evidence_ids:
            raise ValueError("deep-task alternative requires supporting evidence")
        if not self.falsification_condition.strip():
            raise ValueError("deep-task alternative requires an explicit falsification condition")
        if not self.falsification_evidence_ids:
            raise ValueError("deep-task alternative requires falsification/red-team evidence")


@dataclass(frozen=True, slots=True)
class DeepTaskCase:
    """Evidence bundle for an explicitly deeper task, without creating a second cognition state machine."""

    case_id: str
    governing_outcome: str
    evidence_items: tuple[EvidenceItem, ...]
    professional_practice_evidence_ids: tuple[str, ...]
    raw_material_evidence_ids: tuple[str, ...]
    method_tool_evidence_ids: tuple[str, ...]
    unknown_discovery_evidence_ids: tuple[str, ...]
    alternatives: tuple[DeepTaskAlternative, ...]
    independent_judge_evidence_ids: tuple[str, ...]
    holdout_replay_or_production_evidence_ids: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    stretch_target: str | None = None
    stretch_target_feasibility_evidence_ids: tuple[str, ...] = ()
    knowledge_acquisition_assessment: KnowledgeAcquisitionAssessment | None = None

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("deep-task case id is required")
        if not self.governing_outcome.strip():
            raise ValueError("deep-task governing outcome is required")
        if not self.evidence_items:
            raise ValueError("deep-task case requires typed evidence items")
        required_groups = (
            (self.professional_practice_evidence_ids, "professional-practice evidence"),
            (self.raw_material_evidence_ids, "raw-material evidence"),
            (self.method_tool_evidence_ids, "method/tool evidence"),
            (self.unknown_discovery_evidence_ids, "unknown-discovery evidence"),
            (self.independent_judge_evidence_ids, "independent-judge evidence"),
            (self.holdout_replay_or_production_evidence_ids, "holdout/replay/production evidence"),
            (self.acceptance_criteria, "acceptance criteria"),
        )
        for values, label in required_groups:
            if not values or not all(value.strip() for value in values):
                raise ValueError(f"deep-task {label} is required")
        if len(self.alternatives) < 2:
            raise ValueError("deep-task execution requires at least two competing alternatives")
        if self.stretch_target is not None:
            if not self.stretch_target.strip():
                raise ValueError("stretch target cannot be blank")
            if not self.stretch_target_feasibility_evidence_ids:
                raise ValueError("stretch target requires feasibility evidence")


@dataclass(frozen=True, slots=True)
class DeepTaskReceipt:
    case_id: str
    preferred_alternative_id: str
    evidence_ids: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    stretch_target_admitted: bool
    knowledge_acquisition_receipt: KnowledgeAcquisitionReceipt | None = None


_RAW_ALLOWED = {
    EvidenceKind.EXTERNAL_SOURCE,
    EvidenceKind.REPOSITORY_FACT,
    EvidenceKind.TOOL_RESULT,
    EvidenceKind.TEST_RESULT,
    EvidenceKind.RUNTIME_OBSERVATION,
    EvidenceKind.SCENARIO_RESULT,
}
_SUBSTANTIVE_ALLOWED = _RAW_ALLOWED | {EvidenceKind.ANALYSIS_RESULT}
_FALSIFICATION_ALLOWED = {
    EvidenceKind.REPOSITORY_FACT,
    EvidenceKind.TOOL_RESULT,
    EvidenceKind.TEST_RESULT,
    EvidenceKind.RUNTIME_OBSERVATION,
    EvidenceKind.SCENARIO_RESULT,
    EvidenceKind.ANALYSIS_RESULT,
}
_INDEPENDENT_JUDGE_ALLOWED = {
    EvidenceKind.TOOL_RESULT,
    EvidenceKind.TEST_RESULT,
    EvidenceKind.RUNTIME_OBSERVATION,
    EvidenceKind.SCENARIO_RESULT,
}
_HOLDOUT_ALLOWED = {
    EvidenceKind.TOOL_RESULT,
    EvidenceKind.TEST_RESULT,
    EvidenceKind.RUNTIME_OBSERVATION,
    EvidenceKind.SCENARIO_RESULT,
}


def _index(items: tuple[EvidenceItem, ...]) -> dict[str, EvidenceItem]:
    result: dict[str, EvidenceItem] = {}
    for item in items:
        if item.evidence_id in result:
            raise DeepTaskAdmissionError(f"duplicate deep-task evidence id: {item.evidence_id}")
        result[item.evidence_id] = item
    return result


def _require_known(refs: tuple[str, ...], index: dict[str, EvidenceItem], label: str) -> None:
    missing = tuple(ref for ref in refs if ref not in index)
    if missing:
        raise DeepTaskAdmissionError(f"{label} references unknown evidence: {', '.join(missing)}")


def _require_kind(
    refs: tuple[str, ...],
    index: dict[str, EvidenceItem],
    allowed: set[EvidenceKind],
    label: str,
) -> None:
    if not any(index[ref].kind in allowed for ref in refs):
        raise DeepTaskAdmissionError(f"{label} lacks admissible substantive evidence")


def require_deep_task_admission(case: DeepTaskCase) -> DeepTaskReceipt:
    """Fail closed unless a deep task proves depth through evidence rather than verbosity."""

    index = _index(case.evidence_items)

    groups = (
        (case.professional_practice_evidence_ids, "professional-practice"),
        (case.raw_material_evidence_ids, "raw-material"),
        (case.method_tool_evidence_ids, "method/tool"),
        (case.unknown_discovery_evidence_ids, "unknown-discovery"),
        (case.independent_judge_evidence_ids, "independent-judge"),
        (case.holdout_replay_or_production_evidence_ids, "holdout/replay/production"),
    )
    for refs, label in groups:
        _require_known(refs, index, label)

    if not any(index[ref].kind is EvidenceKind.EXTERNAL_SOURCE for ref in case.professional_practice_evidence_ids):
        raise DeepTaskAdmissionError(
            "professional-practice gap analysis requires at least one external source; same-model expertise claims are insufficient"
        )

    _require_kind(case.raw_material_evidence_ids, index, _RAW_ALLOWED, "raw-material evidence")
    if any(index[ref].kind in {EvidenceKind.USER_CLAIM, EvidenceKind.ANALYSIS_RESULT} for ref in case.raw_material_evidence_ids):
        raise DeepTaskAdmissionError(
            "raw-material evidence cannot be only user claims or already-digested analysis"
        )

    _require_kind(case.method_tool_evidence_ids, index, _SUBSTANTIVE_ALLOWED, "method/tool evidence")
    if not any(index[ref].method_ref for ref in case.method_tool_evidence_ids):
        raise DeepTaskAdmissionError(
            "method/tool evidence must name at least one concrete method or tool through method_ref"
        )

    _require_kind(case.unknown_discovery_evidence_ids, index, _SUBSTANTIVE_ALLOWED, "unknown-discovery evidence")

    preferred = tuple(
        item for item in case.alternatives if item.disposition is DeepTaskAlternativeDisposition.PREFERRED
    )
    if len(preferred) != 1:
        raise DeepTaskAdmissionError("deep-task execution requires exactly one current preferred alternative")
    if len({item.alternative_id for item in case.alternatives}) != len(case.alternatives):
        raise DeepTaskAdmissionError("deep-task alternative identifiers must be unique")

    for alternative in case.alternatives:
        _require_known(alternative.supporting_evidence_ids, index, f"alternative {alternative.alternative_id}")
        _require_known(
            alternative.falsification_evidence_ids,
            index,
            f"alternative {alternative.alternative_id} falsification",
        )
        _require_kind(
            alternative.falsification_evidence_ids,
            index,
            _FALSIFICATION_ALLOWED,
            f"alternative {alternative.alternative_id} falsification",
        )

    _require_kind(
        case.independent_judge_evidence_ids,
        index,
        _INDEPENDENT_JUDGE_ALLOWED,
        "independent-judge evidence",
    )

    _require_kind(
        case.holdout_replay_or_production_evidence_ids,
        index,
        _HOLDOUT_ALLOWED,
        "holdout/replay/production evidence",
    )

    stretch_admitted = case.stretch_target is not None
    if stretch_admitted:
        _require_known(
            case.stretch_target_feasibility_evidence_ids,
            index,
            "stretch-target feasibility",
        )
        _require_kind(
            case.stretch_target_feasibility_evidence_ids,
            index,
            _RAW_ALLOWED,
            "stretch-target feasibility",
        )

    knowledge_receipt: KnowledgeAcquisitionReceipt | None = None
    if case.knowledge_acquisition_assessment is not None:
        try:
            knowledge_receipt = require_knowledge_acquisition_admission(
                case.knowledge_acquisition_assessment,
                comprehensive=True,
            )
        except (RuntimeError, ValueError) as exc:
            raise DeepTaskAdmissionError(f"knowledge-acquisition evidence is not admitted: {exc}") from exc
        _require_known(
            knowledge_receipt.evidence_refs,
            index,
            "knowledge-acquisition",
        )

    evidence_ids = tuple(sorted({
        *case.professional_practice_evidence_ids,
        *case.raw_material_evidence_ids,
        *case.method_tool_evidence_ids,
        *case.unknown_discovery_evidence_ids,
        *case.independent_judge_evidence_ids,
        *case.holdout_replay_or_production_evidence_ids,
        *case.stretch_target_feasibility_evidence_ids,
        *(knowledge_receipt.evidence_refs if knowledge_receipt is not None else ()),
        *(ref for item in case.alternatives for ref in item.supporting_evidence_ids),
        *(ref for item in case.alternatives for ref in item.falsification_evidence_ids),
    }))

    return DeepTaskReceipt(
        case_id=case.case_id,
        preferred_alternative_id=preferred[0].alternative_id,
        evidence_ids=evidence_ids,
        acceptance_criteria=case.acceptance_criteria,
        stretch_target_admitted=stretch_admitted,
        knowledge_acquisition_receipt=knowledge_receipt,
    )
