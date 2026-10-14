from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uaos.migration import LegacyRecord, SelectiveLegacyImporter


def main() -> int:
    parser = argparse.ArgumentParser(description="Import the selected legacy semantic bundle into local SQLite")
    parser.add_argument("--bundle", type=Path, default=ROOT / "docs" / "migration" / "LEGACY_CUTOVER_V1.json")
    parser.add_argument("--db", type=Path, default=ROOT / ".uaos" / "uaos.db")
    args = parser.parse_args()

    raw = json.loads(args.bundle.read_text(encoding="utf-8"))
    records = tuple(
        LegacyRecord(item["record_id"], item["record_type"], item["source_ref"], item["payload"])
        for item in raw["records"]
    )
    result = SelectiveLegacyImporter(args.db).import_records(records)
    print(json.dumps({
        "status": "PASS",
        "imported": list(result.imported_ids),
        "already_present": list(result.already_present_ids),
        "ledger_events": list(result.ledger_event_ids),
        "db": str(args.db),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
