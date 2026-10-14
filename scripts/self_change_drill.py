from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uaos.evolution import run_self_change_drill


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the zero-cost governed self-change rollback drill")
    parser.add_argument("--workspace", type=Path, default=ROOT / ".uaos" / "self-change-drill")
    args = parser.parse_args()
    result = run_self_change_drill(args.workspace)
    print(json.dumps({
        "status": "PASS",
        "proposal_id": result.proposal_id,
        "candidate_hash": result.candidate_hash,
        "restored_hash": result.restored_hash,
        "recommendation": result.recommendation,
        "final_state": result.final_state.value,
        "ledger_events": result.ledger_events,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
