import json
from pathlib import Path

import pytest

from uaos.integrations.domain_health_live import (
    LiveDomainHealthAuditError,
    audit_registered_domain_revisions,
    registered_domain_repositories,
)
from uaos.kernel.domain_health import HealthFindingType

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _registry():
    return {
        "agents": [
            {"domain_id": "alpha", "repository": "example/alpha"},
            {"domain_id": "beta", "repository": "example/beta"},
        ]
    }


def _health():
    return {
        "domains": {
            "alpha": {"repository": "example/alpha", "observed_main_commit": "aaa"},
            "beta": {"repository": "example/beta", "observed_main_commit": "bbb"},
        }
    }


def test_registered_domain_repositories_is_registry_driven_and_rejects_duplicates():
    assert registered_domain_repositories(_registry()) == {
        "alpha": "example/alpha",
        "beta": "example/beta",
    }
    duplicate = {"agents": _registry()["agents"] + [{"domain_id": "alpha", "repository": "other/alpha"}]}
    with pytest.raises(LiveDomainHealthAuditError, match="duplicate registered domain_id"):
        registered_domain_repositories(duplicate)


def test_live_revision_audit_passes_when_cache_matches_current_child():
    revisions = {"example/alpha": "aaa", "example/beta": "bbb"}
    audits = audit_registered_domain_revisions(
        _registry(),
        _health(),
        revision_fetcher=revisions.__getitem__,
    )
    assert all(audit.healthy for audit in audits)
    assert [audit.domain_id for audit in audits] == ["alpha", "beta"]


def test_live_revision_audit_surfaces_parent_child_revision_drift():
    revisions = {"example/alpha": "new-alpha", "example/beta": "bbb"}
    audits = audit_registered_domain_revisions(
        _registry(),
        _health(),
        revision_fetcher=revisions.__getitem__,
    )
    alpha = next(audit for audit in audits if audit.domain_id == "alpha")
    beta = next(audit for audit in audits if audit.domain_id == "beta")
    assert not alpha.healthy
    assert alpha.current_revision == "new-alpha"
    assert [finding.finding_type for finding in alpha.receipt.findings] == [
        HealthFindingType.PARENT_CHILD_REVISION_DRIFT
    ]
    assert beta.healthy


def test_live_revision_audit_fails_closed_on_registry_health_topology_drift():
    missing = _health()
    missing["domains"].pop("beta")
    with pytest.raises(LiveDomainHealthAuditError, match="domain set mismatch"):
        audit_registered_domain_revisions(
            _registry(),
            missing,
            revision_fetcher=lambda _: "irrelevant",
        )

    mismatched = _health()
    mismatched["domains"]["alpha"]["repository"] = "wrong/repository"
    with pytest.raises(LiveDomainHealthAuditError, match="repository mismatch"):
        audit_registered_domain_revisions(
            _registry(),
            mismatched,
            revision_fetcher=lambda _: "irrelevant",
        )


def test_current_registry_and_health_index_cover_the_same_domains():
    registry = _json("config/AGENT_REGISTRY.json")
    health = _json("state/DOMAIN_HEALTH_INDEX.json")
    assert set(registered_domain_repositories(registry)) == set(health["domains"])


def test_live_audit_workflow_is_read_only_and_recurring():
    workflow = (ROOT / ".github" / "workflows" / "domain-health-live-audit.yml").read_text(encoding="utf-8")
    assert "schedule:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "python scripts/domain_health_audit.py --json" in workflow
    assert "contents: write" not in workflow
