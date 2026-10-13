from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SQL = (ROOT / "migrations" / "0001_core.sql").read_text(encoding="utf-8")


def test_core_schema_contains_authority_and_lane_guards():
    required = ["uaos_task", "uaos_requirement", "uaos_action", "uaos_artifact", "uaos_knowledge", "uaos_ledger_event", "row_version", "PRODUCTION", "CANDIDATE", "EXPLORATION", "idempotency_key"]
    for token in required:
        assert token in SQL
