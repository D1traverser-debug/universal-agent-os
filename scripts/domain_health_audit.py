#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from uaos.integrations.domain_health_live import (
    LiveDomainHealthAuditError,
    audit_registered_domain_revisions,
    fetch_github_main_revision,
)

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only live audit of registered child main revisions against DOMAIN_HEALTH_INDEX."
    )
    parser.add_argument("--registry", default=str(ROOT / "config" / "AGENT_REGISTRY.json"))
    parser.add_argument("--health-index", default=str(ROOT / "state" / "DOMAIN_HEALTH_INDEX.json"))
    parser.add_argument("--api-base", default=os.getenv("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    args = parser.parse_args()

    registry = _load_json(Path(args.registry))
    health_index = _load_json(Path(args.health_index))
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    try:
        audits = audit_registered_domain_revisions(
            registry,
            health_index,
            revision_fetcher=lambda repository: fetch_github_main_revision(
                repository,
                token=token,
                api_base=args.api_base,
            ),
        )
    except LiveDomainHealthAuditError as exc:
        payload = {
            "status": "AUDIT_ERROR",
            "checked_at": datetime.now(UTC).isoformat(),
            "error": str(exc),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=None if args.json else 2))
        return 3

    domain_payload = [audit.as_dict() for audit in audits]
    healthy = all(audit.healthy for audit in audits)
    payload = {
        "status": "PASS" if healthy else "DRIFT_DETECTED",
        "checked_at": datetime.now(UTC).isoformat(),
        "health_index_updated_at": health_index.get("updated_at"),
        "domains": domain_payload,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=None if args.json else 2))
    return 0 if healthy else 2


if __name__ == "__main__":
    raise SystemExit(main())
