from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uaos.live import LiveConfig, LiveConfigurationError, run_dbos_probe, run_postgres_probe
from uaos.live.object_store_probe import run_object_store_probe
from uaos.live.openai_probe import run_openai_probe


def main() -> int:
    parser = argparse.ArgumentParser(description="UAOS live integration verifier")
    parser.add_argument("target", choices=("postgres", "dbos", "object-store", "openai", "all"))
    args = parser.parse_args()
    cfg = LiveConfig.from_env()
    out: dict[str, object] = {"target": args.target, "status": "PASS", "checks": {}}
    try:
        if args.target in {"postgres", "all"}:
            result = run_postgres_probe(cfg.require_postgres(), ROOT / "migrations")
            out["checks"]["postgres"] = {
                "migrations": list(result.migrations_applied),
                "cas_verified": result.cas_verified,
                "ledger_verified": result.ledger_verified,
            }
        if args.target in {"dbos", "all"}:
            result = run_dbos_probe(cfg.require_dbos())
            out["checks"]["dbos"] = {
                "workflow_id": result.workflow_id,
                "result": result.result,
                "duplicate_returned_existing": result.duplicate_returned_existing,
            }
        if args.target in {"object-store", "all"}:
            endpoint, bucket, region = cfg.require_object_store()
            result = run_object_store_probe(endpoint_url=endpoint, bucket=bucket, region=region)
            out["checks"]["object_store"] = {
                "bucket": result.bucket,
                "content_hash": result.content_hash,
                "roundtrip_verified": result.roundtrip_verified,
                "cleanup_verified": result.cleanup_verified,
            }
        if args.target in {"openai", "all"}:
            result = run_openai_probe(cfg.require_openai())
            out["checks"]["openai"] = {
                "disposition": result.disposition,
                "output": result.output,
                "last_agent": result.last_agent,
            }
    except LiveConfigurationError as exc:
        out["status"] = "BLOCKED"
        out["error"] = f"{type(exc).__name__}: {exc}"
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 2
    except Exception as exc:
        out["status"] = "FAIL"
        out["error"] = f"{type(exc).__name__}: {exc}"
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
