from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
import time

class CircuitState(StrEnum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

@dataclass(slots=True)
class _Entry:
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    opened_at: float | None = None

class CapabilityCircuitBreaker:
    """Provider-neutral circuit breaker for flaky host/plugin/API capabilities."""
    def __init__(self, *, failure_threshold: int = 3, cooldown_seconds: float = 30.0) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if cooldown_seconds <= 0:
            raise ValueError("cooldown_seconds must be positive")
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._entries: dict[str, _Entry] = {}

    def state(self, capability_id: str, *, now: float | None = None) -> CircuitState:
        now = time.time() if now is None else now
        entry = self._entries.setdefault(capability_id, _Entry())
        if entry.state is CircuitState.OPEN and entry.opened_at is not None:
            if now - entry.opened_at >= self.cooldown_seconds:
                entry.state = CircuitState.HALF_OPEN
        return entry.state

    def allows(self, capability_id: str, *, now: float | None = None) -> bool:
        return self.state(capability_id, now=now) is not CircuitState.OPEN

    def record(self, capability_id: str, disposition: object, *, now: float | None = None) -> None:
        now = time.time() if now is None else now
        entry = self._entries.setdefault(capability_id, _Entry())
        value = getattr(disposition, "value", str(disposition))
        if value == "CONFIRMED":
            entry.state = CircuitState.CLOSED
            entry.failures = 0
            entry.opened_at = None
            return
        if value not in {"FAILED", "UNKNOWN"}:
            return
        entry.failures += 1
        if entry.state is CircuitState.HALF_OPEN or entry.failures >= self.failure_threshold:
            entry.state = CircuitState.OPEN
            entry.opened_at = now
