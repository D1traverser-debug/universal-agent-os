from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
status = json.loads((ROOT / "docs" / "assurance" / "PRODUCTION_READINESS.json").read_text(encoding="utf-8"))
print(json.dumps({
    "status": status["status"],
    "mandatory_external_services": status["mandatory_external_services"],
    "core_open_work": status["core_open_work"],
    "known_limitations": status.get("known_limitations", []),
}, ensure_ascii=False, indent=2))
