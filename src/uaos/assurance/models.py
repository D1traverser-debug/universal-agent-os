from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Mapping


class EvidenceLevel(IntEnum):
    DECLARATION = 1
    STRUCTURAL = 2
    DETERMINISTIC = 3
    SEMANTIC = 4
    INDEPENDENT = 5
    LIVE_OUTCOME = 6


class CheckStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class RequirementCheck:
    requirement_id: str
    status: CheckStatus
    evidence_refs: tuple[str, ...] = ()
    evidence_level: EvidenceLevel = EvidenceLevel.DECLARATION
    notes: str = ""


@dataclass(frozen=True, slots=True)
class DeliveryExpectation:
    artifact_id: str
    version: int
    content_hash: str


@dataclass(frozen=True, slots=True)
class DeliveryProof:
    artifact_id: str
    version: int
    content_hash: str
    accessible: bool
    checked_at: datetime
    evidence_ref: str


@dataclass(frozen=True, slots=True)
class ReviewEvidence:
    review_id: str
    producer_identity: str
    reviewer_identity: str
    evidence_ref: str
    independence_axes: tuple[str, ...] = ()

    @property
    def is_independent(self) -> bool:
        return bool(self.independence_axes) and self.producer_identity != self.reviewer_identity


@dataclass(frozen=True, slots=True)
class CoverageEntry:
    subject_type: str
    subject_id: str
    evidence_refs: tuple[str, ...]
    status: CheckStatus


@dataclass(frozen=True, slots=True)
class CompletionDecision:
    complete: bool
    status: str
    reasons: tuple[str, ...] = ()
    evidence_summary: Mapping[str, int] = field(default_factory=dict)
