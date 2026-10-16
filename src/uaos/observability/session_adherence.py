from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from uaos.kernel.deliberation import RootScopeReceipt
from uaos.kernel.problem_closure import EvolutionDisposition


POLICY_REQUIRED_PROGRESS_FIELDS: tuple[str, ...] = (
    "current_agent",
    "current_scope_or_task",
    "authority_context",
    "status",
    "current_stage",
    "next_action_or_blocker",
    "evolution_state_when_triggered_or_NO_EVOLUTION_TRIGGER",
    "deliberation_state_when_triggered_or_NOT_TRIGGERED",
    "version_identity",
    "progress_timestamp",
)

POLICY_TO_CANONICAL_FIELD: Mapping[str, str] = {
    "current_agent": "current_agent",
    "current_scope_or_task": "current_scope_or_task",
    "authority_context": "authority_context",
    "status": "status",
    "current_stage": "current_stage",
    "next_action_or_blocker": "next_action_or_blocker",
    "evolution_state_when_triggered_or_NO_EVOLUTION_TRIGGER": "evolution_state",
    "deliberation_state_when_triggered_or_NOT_TRIGGERED": "deliberation_state",
    "version_identity": "version_identity",
    "progress_timestamp": "progress_timestamp",
}

REQUIRED_PROGRESS_FIELDS: tuple[str, ...] = tuple(
    POLICY_TO_CANONICAL_FIELD[field] for field in POLICY_REQUIRED_PROGRESS_FIELDS
)

_FIELD_ALIASES: Mapping[str, tuple[str, ...]] = {
    "current_agent": ("当前 agent", "current agent"),
    "current_scope_or_task": (
        "当前范围", "当前任务", "当前范围或任务", "current scope", "current task", "current scope or task",
    ),
    "authority_context": ("authority", "authority context", "权威", "权限上下文"),
    "status": ("状态", "status"),
    "current_stage": ("当前阶段", "stage", "current stage"),
    "next_action_or_blocker": ("下一动作或阻塞", "下一动作", "下一步", "next action or blocker", "next action", "blocker"),
    "evolution_state": ("evolution", "进化"),
    "deliberation_state": ("deliberation", "认知审议"),
    "version_identity": ("版本", "version", "version identity"),
    "progress_timestamp": ("进度时间", "progress timestamp", "timestamp"),
}

_NO_OP_CONTINUATION_MARKERS: tuple[str, ...] = (
    "下一轮", "下轮", "下一条", "回复 next", "回复next", "发 next", "发next", "send next", "reply next", "next turn", "next message",
)


class SessionAdherenceViolation(str, Enum):
    MISSING_PROGRESS_REPORT = "MISSING_PROGRESS_REPORT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    PROBLEM_SIGNAL_REPORTED_NOT_TRIGGERED = "PROBLEM_SIGNAL_REPORTED_NOT_TRIGGERED"
    PROBLEM_SIGNAL_REPORTED_NO_EVOLUTION_TRIGGER = "PROBLEM_SIGNAL_REPORTED_NO_EVOLUTION_TRIGGER"
    EMPTY_REQUIRED_FIELD = "EMPTY_REQUIRED_FIELD"
    UNNECESSARY_USER_CONTINUATION_HANDOFF = "UNNECESSARY_USER_CONTINUATION_HANDOFF"
    CLAIMED_COGNITION_WITHOUT_ROOT_SCOPE_RECEIPT = "CLAIMED_COGNITION_WITHOUT_ROOT_SCOPE_RECEIPT"
    CLAIMED_EVOLUTION_WITHOUT_VERIFIED_DISPOSITION = "CLAIMED_EVOLUTION_WITHOUT_VERIFIED_DISPOSITION"
    MISSING_DURABLE_PROBLEM_RECORD_EVIDENCE = "MISSING_DURABLE_PROBLEM_RECORD_EVIDENCE"


@dataclass(frozen=True, slots=True)
class SessionProgressExpectation:
    """Observable expectations for one final assistant response.

    Report text is never treated as proof that cognition/evolution actually ran.
    Verified admission artifacts must be supplied separately when required.
    """
    context_selected: bool
    problem_signal_observed: bool = False
    user_input_required: bool = False
    no_op_continuation_disallowed: bool = False
    cognition_admission_required: bool = False
    root_scope_receipt: RootScopeReceipt | None = None
    evolution_disposition: EvolutionDisposition | None = None
    problem_record_ref: str | None = None


@dataclass(frozen=True, slots=True)
class SessionAdherenceResult:
    report_required: bool
    fields: Mapping[str, str]
    violations: tuple[SessionAdherenceViolation, ...]
    missing_fields: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.violations


@dataclass(frozen=True, slots=True)
class SessionAdherenceSummary:
    sample_count: int
    required_report_count: int
    pass_count: int
    fail_count: int
    missing_report_count: int
    problem_state_contradiction_count: int
    unnecessary_continuation_handoff_count: int
    cognition_evidence_gap_count: int
    durable_problem_record_gap_count: int

    @property
    def adherence_rate(self) -> float:
        if self.required_report_count == 0:
            return 1.0
        return self.pass_count / self.required_report_count


def _normalize_key(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").split())


def _contains_no_op_continuation_handoff(value: str) -> bool:
    normalized = value.strip().lower()
    return any(marker in normalized for marker in _NO_OP_CONTINUATION_MARKERS)


def _present(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


def extract_progress_fields(response: str) -> dict[str, str]:
    alias_to_field = {
        _normalize_key(alias): field
        for field, aliases in _FIELD_ALIASES.items()
        for alias in aliases
    }
    fields: dict[str, str] = {}
    for raw_line in response.splitlines():
        line = raw_line.strip().lstrip("-*• ").strip()
        if not line:
            continue
        separator = "：" if "：" in line else ":" if ":" in line else None
        if separator is None:
            continue
        key, value = line.split(separator, 1)
        field = alias_to_field.get(_normalize_key(key))
        if field is not None and field not in fields:
            fields[field] = value.strip()
    return fields


def evaluate_session_progress_response(response: str, expectation: SessionProgressExpectation) -> SessionAdherenceResult:
    fields = extract_progress_fields(response)
    if not expectation.context_selected:
        return SessionAdherenceResult(False, fields, (), ())

    missing = tuple(field for field in REQUIRED_PROGRESS_FIELDS if field not in fields)
    violations: list[SessionAdherenceViolation] = []
    if len(missing) == len(REQUIRED_PROGRESS_FIELDS):
        violations.append(SessionAdherenceViolation.MISSING_PROGRESS_REPORT)
    elif missing:
        violations.append(SessionAdherenceViolation.MISSING_REQUIRED_FIELD)

    if any(field in fields and not fields[field].strip() for field in REQUIRED_PROGRESS_FIELDS):
        violations.append(SessionAdherenceViolation.EMPTY_REQUIRED_FIELD)

    if expectation.problem_signal_observed:
        deliberation = fields.get("deliberation_state", "").upper()
        evolution = fields.get("evolution_state", "").upper()
        if "NOT_TRIGGERED" in deliberation:
            violations.append(SessionAdherenceViolation.PROBLEM_SIGNAL_REPORTED_NOT_TRIGGERED)
        if "NO_EVOLUTION_TRIGGER" in evolution:
            violations.append(SessionAdherenceViolation.PROBLEM_SIGNAL_REPORTED_NO_EVOLUTION_TRIGGER)

    if (
        expectation.no_op_continuation_disallowed
        and not expectation.user_input_required
        and _contains_no_op_continuation_handoff(fields.get("next_action_or_blocker", ""))
    ):
        violations.append(SessionAdherenceViolation.UNNECESSARY_USER_CONTINUATION_HANDOFF)

    if expectation.cognition_admission_required:
        if not isinstance(expectation.root_scope_receipt, RootScopeReceipt):
            violations.append(SessionAdherenceViolation.CLAIMED_COGNITION_WITHOUT_ROOT_SCOPE_RECEIPT)
        if not isinstance(expectation.evolution_disposition, EvolutionDisposition):
            violations.append(SessionAdherenceViolation.CLAIMED_EVOLUTION_WITHOUT_VERIFIED_DISPOSITION)
        if (
            isinstance(expectation.root_scope_receipt, RootScopeReceipt)
            and expectation.root_scope_receipt.durable_problem_record_required
            and not _present(expectation.problem_record_ref)
        ):
            violations.append(SessionAdherenceViolation.MISSING_DURABLE_PROBLEM_RECORD_EVIDENCE)

    return SessionAdherenceResult(True, fields, tuple(dict.fromkeys(violations)), missing)


def summarize_session_adherence(samples: Iterable[tuple[str, SessionProgressExpectation]]) -> SessionAdherenceSummary:
    results = [evaluate_session_progress_response(response, expected) for response, expected in samples]
    required = [result for result in results if result.report_required]
    contradiction_types = {
        SessionAdherenceViolation.PROBLEM_SIGNAL_REPORTED_NOT_TRIGGERED,
        SessionAdherenceViolation.PROBLEM_SIGNAL_REPORTED_NO_EVOLUTION_TRIGGER,
    }
    cognition_gap_types = {
        SessionAdherenceViolation.CLAIMED_COGNITION_WITHOUT_ROOT_SCOPE_RECEIPT,
        SessionAdherenceViolation.CLAIMED_EVOLUTION_WITHOUT_VERIFIED_DISPOSITION,
    }
    return SessionAdherenceSummary(
        sample_count=len(results),
        required_report_count=len(required),
        pass_count=sum(result.passed for result in required),
        fail_count=sum(not result.passed for result in required),
        missing_report_count=sum(SessionAdherenceViolation.MISSING_PROGRESS_REPORT in result.violations for result in required),
        problem_state_contradiction_count=sum(bool(contradiction_types.intersection(result.violations)) for result in required),
        unnecessary_continuation_handoff_count=sum(SessionAdherenceViolation.UNNECESSARY_USER_CONTINUATION_HANDOFF in result.violations for result in required),
        cognition_evidence_gap_count=sum(bool(cognition_gap_types.intersection(result.violations)) for result in required),
        durable_problem_record_gap_count=sum(SessionAdherenceViolation.MISSING_DURABLE_PROBLEM_RECORD_EVIDENCE in result.violations for result in required),
    )
