from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import uuid


@dataclass(frozen=True, slots=True)
class PostgresProbeResult:
    migrations_applied: tuple[str, ...]
    cas_verified: bool
    ledger_verified: bool


def migration_files(root: Path) -> tuple[Path, ...]:
    files = tuple(sorted(root.glob("*.sql")))
    if not files:
        raise RuntimeError(f"no SQL migrations found in {root}")
    names = [p.name for p in files]
    if names != sorted(names):
        raise RuntimeError("migration ordering is not deterministic")
    return files


def apply_migrations(connection, files: Iterable[Path]) -> tuple[str, ...]:
    applied: list[str] = []
    with connection.cursor() as cur:
        for path in files:
            cur.execute(path.read_text(encoding="utf-8"))
            applied.append(path.name)
    connection.commit()
    return tuple(applied)


def verify_authority_roundtrip(connection) -> tuple[bool, bool]:
    suffix = uuid.uuid4().hex
    task_id = f"live-probe-{suffix}"
    event_id = f"event-{suffix}"
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO uaos_task (
                task_id, intent, owner_domain, goal, done_condition,
                status, priority, current_stage, plan_version, row_version
            ) VALUES (%s, 'NEW_TASK', 'live-probe', 'verify authority',
                      'probe completes', 'PENDING', 1, 'CREATED', 1, 1)
            """,
            (task_id,),
        )
        cur.execute(
            "UPDATE uaos_task SET current_stage='CAS_OK', row_version=row_version+1 "
            "WHERE task_id=%s AND row_version=1 RETURNING row_version",
            (task_id,),
        )
        first = cur.fetchone()
        cur.execute(
            "UPDATE uaos_task SET current_stage='STALE_WRITE', row_version=row_version+1 "
            "WHERE task_id=%s AND row_version=1 RETURNING row_version",
            (task_id,),
        )
        stale = cur.fetchone()
        cur.execute(
            "INSERT INTO uaos_ledger_event (event_id, aggregate_type, aggregate_id, event_type, payload) "
            "VALUES (%s, 'task', %s, 'LIVE_PROBE', '{}'::jsonb)",
            (event_id, task_id),
        )
        cur.execute("SELECT event_id FROM uaos_ledger_event WHERE event_id=%s", (event_id,))
        ledger = cur.fetchone()
        cur.execute("DELETE FROM uaos_ledger_event WHERE event_id=%s", (event_id,))
        cur.execute("DELETE FROM uaos_task WHERE task_id=%s", (task_id,))
    connection.commit()
    return bool(first and first[0] == 2 and stale is None), bool(ledger and ledger[0] == event_id)


def run_postgres_probe(database_url: str, migrations_root: Path) -> PostgresProbeResult:
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("live PostgreSQL probe requires psycopg; install .[live]") from exc

    with psycopg.connect(database_url) as connection:
        applied = apply_migrations(connection, migration_files(migrations_root))
        cas_ok, ledger_ok = verify_authority_roundtrip(connection)
    if not cas_ok:
        raise RuntimeError("PostgreSQL CAS probe failed")
    if not ledger_ok:
        raise RuntimeError("PostgreSQL ledger probe failed")
    return PostgresProbeResult(applied, cas_ok, ledger_ok)
