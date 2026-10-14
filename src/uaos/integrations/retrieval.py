from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class RetrievalPurpose(StrEnum):
    ACTIVE_EXECUTION = "ACTIVE_EXECUTION"
    SYSTEM_MAINTENANCE = "SYSTEM_MAINTENANCE"
    HISTORICAL_QUERY = "HISTORICAL_QUERY"


class RetrievalDenied(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class RepositoryRetrievalRule:
    allow_exact: frozenset[str]
    deny_patterns: tuple[str, ...]
    allow_prefixes: tuple[str, ...]


class RetrievalPolicy:
    def __init__(self, *, retired_repositories: frozenset[str], uaos_cold_patterns: tuple[str, ...], repository_rules: dict[str, RepositoryRetrievalRule], historical_requires_explicit_intent: bool = True) -> None:
        self.retired_repositories = retired_repositories
        self.uaos_cold_patterns = uaos_cold_patterns
        self.repository_rules = repository_rules
        self.historical_requires_explicit_intent = historical_requires_explicit_intent

    @classmethod
    def from_path(cls, path: str | Path) -> "RetrievalPolicy":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rules = {
            repo: RepositoryRetrievalRule(
                allow_exact=frozenset(rule.get("allow_exact", [])),
                deny_patterns=tuple(rule.get("deny_patterns", [])),
                allow_prefixes=tuple(rule.get("allow_prefixes", [])),
            )
            for repo, rule in data.get("repositories", {}).items()
        }
        return cls(
            retired_repositories=frozenset(data.get("retired_repositories", [])),
            uaos_cold_patterns=tuple(data.get("uaos_cold_patterns", [])),
            repository_rules=rules,
            historical_requires_explicit_intent=bool(data.get("historical_requires_explicit_intent", True)),
        )

    def authorize(self, repository: str, path: str, *, purpose: RetrievalPurpose = RetrievalPurpose.ACTIVE_EXECUTION, explicit_historical: bool = False) -> None:
        normalized = path.lstrip("/")
        historical = purpose is RetrievalPurpose.HISTORICAL_QUERY
        if historical and self.historical_requires_explicit_intent and not explicit_historical:
            raise RetrievalDenied("historical retrieval requires explicit historical intent")
        if repository in self.retired_repositories:
            if historical and explicit_historical:
                return
            raise RetrievalDenied(f"retired repository is not active retrieval authority: {repository}")
        if repository == "D1traverser-debug/universal-agent-os" and any(fnmatch.fnmatch(normalized, pattern) for pattern in self.uaos_cold_patterns):
            if historical and explicit_historical:
                return
            raise RetrievalDenied(f"UAOS cold-path evidence is not active retrieval input: {normalized}")
        rule = self.repository_rules.get(repository)
        if rule is None:
            return
        if normalized in rule.allow_exact:
            return
        if any(fnmatch.fnmatch(normalized, pattern) for pattern in rule.deny_patterns):
            if historical and explicit_historical:
                return
            raise RetrievalDenied(f"path denied by active retrieval policy: {repository}:{normalized}")
        if any(normalized.startswith(prefix) for prefix in rule.allow_prefixes):
            return
        # Domain files not explicitly denied remain available as domain evidence;
        # authority still comes from the registry/task/Skill chain, never search rank.
        return

    def is_allowed(self, repository: str, path: str, *, purpose: RetrievalPurpose = RetrievalPurpose.ACTIVE_EXECUTION, explicit_historical: bool = False) -> bool:
        try:
            self.authorize(repository, path, purpose=purpose, explicit_historical=explicit_historical)
            return True
        except RetrievalDenied:
            return False
