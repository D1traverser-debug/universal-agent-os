from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Mapping
from urllib import request

from uaos.kernel.domain_health import DomainHealthReceipt, DomainObservation, assess_domain_health


class LiveDomainHealthAuditError(RuntimeError):
    """Raised when live health evidence cannot be acquired or reconciled safely."""


@dataclass(frozen=True, slots=True)
class LiveDomainRevisionAudit:
    domain_id: str
    repository: str
    cached_revision: str
    current_revision: str
    receipt: DomainHealthReceipt

    @property
    def healthy(self) -> bool:
        return self.receipt.healthy

    def as_dict(self) -> dict[str, object]:
        return {
            "domain_id": self.domain_id,
            "repository": self.repository,
            "cached_revision": self.cached_revision,
            "current_revision": self.current_revision,
            "healthy": self.healthy,
            "findings": [
                {
                    "type": finding.finding_type.value,
                    "severity": finding.severity.value,
                    "summary": finding.summary,
                    "capability_id": finding.capability_id,
                }
                for finding in self.receipt.findings
            ],
        }


def registered_domain_repositories(registry: Mapping[str, object]) -> dict[str, str]:
    agents = registry.get("agents")
    if not isinstance(agents, list) or not agents:
        raise LiveDomainHealthAuditError("AGENT_REGISTRY agents must be a non-empty list")

    repositories: dict[str, str] = {}
    for raw in agents:
        if not isinstance(raw, Mapping):
            raise LiveDomainHealthAuditError("AGENT_REGISTRY entries must be objects")
        domain_id = str(raw.get("domain_id", "")).strip()
        repository = str(raw.get("repository", "")).strip()
        if not domain_id or not repository:
            raise LiveDomainHealthAuditError("registered domains require domain_id and repository")
        if domain_id in repositories:
            raise LiveDomainHealthAuditError(f"duplicate registered domain_id: {domain_id}")
        repositories[domain_id] = repository
    return repositories


def fetch_github_main_revision(
    repository: str,
    *,
    token: str | None = None,
    api_base: str = "https://api.github.com",
    timeout_seconds: float = 10.0,
) -> str:
    url = f"{api_base.rstrip('/')}/repos/{repository}/branches/main"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "uaos-domain-health-audit",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        req = request.Request(url, headers=headers, method="GET")
        with request.urlopen(req, timeout=timeout_seconds) as response:  # noqa: S310 - fixed GitHub API base by default
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # network/provider failure must not masquerade as healthy
        raise LiveDomainHealthAuditError(f"failed to fetch current main for {repository}: {exc}") from exc

    try:
        revision = str(payload["commit"]["sha"]).strip()
    except (KeyError, TypeError) as exc:
        raise LiveDomainHealthAuditError(f"GitHub response for {repository} lacks commit.sha") from exc
    if not revision:
        raise LiveDomainHealthAuditError(f"GitHub response for {repository} returned empty commit.sha")
    return revision


def audit_registered_domain_revisions(
    registry: Mapping[str, object],
    health_index: Mapping[str, object],
    *,
    revision_fetcher: Callable[[str], str],
) -> tuple[LiveDomainRevisionAudit, ...]:
    repositories = registered_domain_repositories(registry)
    raw_domains = health_index.get("domains")
    if not isinstance(raw_domains, Mapping):
        raise LiveDomainHealthAuditError("DOMAIN_HEALTH_INDEX domains must be an object")

    extra = sorted(set(raw_domains) - set(repositories))
    missing = sorted(set(repositories) - set(raw_domains))
    if missing or extra:
        raise LiveDomainHealthAuditError(
            f"registry/health domain set mismatch: missing={missing}, extra={extra}"
        )

    results: list[LiveDomainRevisionAudit] = []
    for domain_id in sorted(repositories):
        repository = repositories[domain_id]
        raw_observation = raw_domains[domain_id]
        if not isinstance(raw_observation, Mapping):
            raise LiveDomainHealthAuditError(f"health observation for {domain_id} must be an object")

        cached_repository = str(raw_observation.get("repository", "")).strip()
        if cached_repository != repository:
            raise LiveDomainHealthAuditError(
                f"repository mismatch for {domain_id}: registry={repository}, health={cached_repository or '<empty>'}"
            )
        cached_revision = str(raw_observation.get("observed_main_commit", "")).strip()
        if not cached_revision:
            raise LiveDomainHealthAuditError(f"health observation for {domain_id} lacks observed_main_commit")

        current_revision = revision_fetcher(repository).strip()
        if not current_revision:
            raise LiveDomainHealthAuditError(f"revision fetcher returned empty revision for {repository}")

        receipt = assess_domain_health(
            DomainObservation(
                domain_id=domain_id,
                current_revision=current_revision,
                parent_observed_revision=cached_revision,
            )
        )
        results.append(
            LiveDomainRevisionAudit(
                domain_id=domain_id,
                repository=repository,
                cached_revision=cached_revision,
                current_revision=current_revision,
                receipt=receipt,
            )
        )
    return tuple(results)
