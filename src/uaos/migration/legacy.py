from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from uaos.state import SQLiteAppendOnlyLedger, SQLiteVersionedRepository, VersionConflict

_ALLOWED = {
    "REQUIREMENT": "requirement",
    "TASK": "task",
    "KNOWLEDGE": "knowledge",
    "EVIDENCE": "evidence",
}


class LegacyControlRejected(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class LegacyRecord:
    record_id: str
    record_type: str
    source_ref: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.record_id.strip() or not self.source_ref.strip():
            raise ValueError("record identity and source_ref are required")


@dataclass(frozen=True, slots=True)
class MigrationResult:
    imported_ids: tuple[str, ...]
    already_present_ids: tuple[str, ...]
    ledger_event_ids: tuple[str, ...]


class SelectiveLegacyImporter:
    """Import only durable business semantics, never legacy control machinery.

    The migration is idempotent when the same record and provenance are replayed.
    A conflicting record with the same ID fails closed instead of overwriting the
    already imported value.
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ledger = SQLiteAppendOnlyLedger(self.db_path)

    def import_records(self, records: tuple[LegacyRecord, ...]) -> MigrationResult:
        imported: list[str] = []
        already_present: list[str] = []
        event_ids: list[str] = []

        for record in records:
            kind = record.record_type.upper()
            namespace = _ALLOWED.get(kind)
            if namespace is None:
                raise LegacyControlRejected(
                    f"legacy record type is not migratable: {record.record_type}"
                )

            value = {
                "source_ref": record.source_ref,
                "payload": dict(record.payload),
                "migration_policy": "SELECTIVE_SEMANTIC_IMPORT",
            }
            repository = SQLiteVersionedRepository(
                self.db_path, f"migrated:{namespace}"
            )
            try:
                repository.create(record.record_id, value)
                imported.append(record.record_id)
            except VersionConflict:
                existing = repository.get(record.record_id)
                if existing.value != value:
                    raise VersionConflict(
                        f"legacy migration collision for {record.record_id}"
                    )
                already_present.append(record.record_id)

            event_id = f"migration:{namespace}:{record.record_id}"
            try:
                self.ledger.append(
                    event_id=event_id,
                    aggregate_type="legacy_migration",
                    aggregate_id=record.record_id,
                    event_type="IMPORTED",
                    payload={"record_type": kind, "source_ref": record.source_ref},
                )
            except ValueError:
                existing_events = self.ledger.events_for(
                    "legacy_migration", record.record_id
                )
                if not any(event.event_id == event_id for event in existing_events):
                    raise
            event_ids.append(event_id)

        return MigrationResult(
            tuple(imported), tuple(already_present), tuple(event_ids)
        )
