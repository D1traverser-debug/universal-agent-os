from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from typing import Mapping


@dataclass(frozen=True, slots=True)
class LedgerEvent:
    sequence: int
    event_id: str
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: Mapping[str, object]
    occurred_at: datetime


class InMemoryAppendOnlyLedger:
    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []
        self._ids: set[str] = set()
        self._lock = RLock()

    def append(self, *, event_id: str, aggregate_type: str, aggregate_id: str, event_type: str, payload: Mapping[str, object], occurred_at: datetime | None = None) -> LedgerEvent:
        with self._lock:
            if event_id in self._ids:
                raise ValueError(f"duplicate event_id: {event_id}")
            event = LedgerEvent(sequence=len(self._events) + 1, event_id=event_id, aggregate_type=aggregate_type, aggregate_id=aggregate_id, event_type=event_type, payload=dict(payload), occurred_at=occurred_at or datetime.now(UTC))
            self._events.append(event)
            self._ids.add(event_id)
            return event

    def events_for(self, aggregate_type: str, aggregate_id: str) -> tuple[LedgerEvent, ...]:
        return tuple(event for event in self._events if event.aggregate_type == aggregate_type and event.aggregate_id == aggregate_id)

    def all(self) -> tuple[LedgerEvent, ...]:
        return tuple(self._events)
