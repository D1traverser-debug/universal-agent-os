#!/usr/bin/env python3
"""Print a deterministic UAOS source filelist from current authority metadata.

This DOES NOT download files, run skills, or attest to native ChatGPT invocation.
Use from a checkout of the current intended repository ref.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from uaos.integrations.retrieval import RetrievalPolicy, build_source_read_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", choices=("financial_writing", "ashare", "novel", "video"))
    parser.add_argument("--cold", action="store_true")
    parser.add_argument("--knowledge", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    system_map = json.loads((root / "config/SYSTEM_MAP.json").read_text(encoding="utf-8"))
    task_index = json.loads((root / "state/TASK_INDEX.json").read_text(encoding="utf-8"))
    policy = RetrievalPolicy.from_path(root / "config/RETRIEVAL_POLICY.json")
    plan = build_source_read_plan(
        system_map=system_map, task_index=task_index, retrieval_policy=policy,
        selected_domain=args.domain, cold_start=args.cold,
        broad_knowledge=args.knowledge,
    )
    print(json.dumps({
        "source_commit": "CHECK_CURRENT_CHECKOUT_AND_HOST_GIT_REF",
        "selected_domain": plan.selected_domain,
        "reads": [
            {"repository": x.repository, "path": x.path, "phase": x.phase, "purpose": x.purpose}
            for x in plan.reads
        ],
        "directory_discovery": [
            {"repository": repo, "root": path} for repo, path in plan.discovery_roots
        ],
        "assurance": plan.assurance,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
