from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable, Mapping


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
    def __init__(self, *, retired_repositories: frozenset[str], uaos_cold_patterns: tuple[str, ...], repository_rules: dict[str, RepositoryRetrievalRule], historical_requires_explicit_intent: bool = True, knowledge_inventory_routing: Mapping[str, object] | None = None) -> None:
        self.retired_repositories = retired_repositories
        self.uaos_cold_patterns = uaos_cold_patterns
        self.repository_rules = repository_rules
        self.historical_requires_explicit_intent = historical_requires_explicit_intent
        self.knowledge_inventory_routing = dict(knowledge_inventory_routing or {})

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
            knowledge_inventory_routing=data.get("knowledge_inventory_routing", {}),
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

    def admit_broad_knowledge_inventory(
        self,
        *,
        system_map: Mapping[str, object],
        repository_evidence_refs: Mapping[str, str],
        verify_source_ref: Callable[[str], bool] | None,
        prior_work_requested: bool,
        historical_surface_outcomes: Mapping[str, str] | None = None,
    ) -> tuple[str, ...]:
        """Require source-role breadth before claiming a broad knowledge inventory.

        Reuses retrieval policy and the current SYSTEM_MAP; it does not store
        knowledge or certify content exhaustiveness. A controlled host must
        actually perform and attest reads via verify_source_ref. This cannot
        install itself as a native ChatGPT retrieval or pre-send hook.
        """
        controller = system_map.get("controller")
        domains = system_map.get("domains")
        if not isinstance(controller, Mapping) or not isinstance(domains, Mapping):
            raise RetrievalDenied("broad knowledge inventory requires current SYSTEM_MAP")
        parent = controller.get("repository")
        children = tuple(
            domain.get("repository") if isinstance(domain, Mapping) else None
            for domain in domains.values()
        )
        if not isinstance(parent, str) or not parent.strip() or any(
            not isinstance(value, str) or not value.strip() for value in children
        ):
            raise RetrievalDenied("broad knowledge inventory has unresolved current repository owners")
        expected = {parent, *children}
        if len(expected) != len(children) + 1:
            raise RetrievalDenied("duplicate or conflicting knowledge repository owners")
        if verify_source_ref is None:
            raise RetrievalDenied("knowledge source role coverage needs a trusted host verifier")
        if not isinstance(repository_evidence_refs, Mapping) or not expected.issubset(repository_evidence_refs):
            raise RetrievalDenied("broad knowledge inventory omitted registered repositories")
        for repo in expected:
            source_ref = repository_evidence_refs[repo]
            if not isinstance(source_ref, str) or not source_ref.strip() or not verify_source_ref(source_ref):
                raise RetrievalDenied("unverified knowledge repository read: " + repo)

        if prior_work_requested:
            historical = self.knowledge_inventory_routing.get("source_roles", {})
            optional = historical.get("optional_connected_historical_surfaces", ()) if isinstance(historical, Mapping) else ()
            expected_surfaces = {
                row["surface"] for row in optional
                if isinstance(row, Mapping) and isinstance(row.get("surface"), str)
            }
            if not expected_surfaces or not isinstance(historical_surface_outcomes, Mapping):
                raise RetrievalDenied("prior-work inventory requires historical source disposition")
            if not expected_surfaces.issubset(historical_surface_outcomes):
                raise RetrievalDenied("historical knowledge surface left unexamined")
            allowed = {"SEARCHED_WITH_EVIDENCE", "UNAVAILABLE_OR_NOT_CONNECTED"}
            if any(historical_surface_outcomes[surface] not in allowed for surface in expected_surfaces):
                raise RetrievalDenied("historical source result must be searched or explicitly unavailable")
        return tuple(sorted(expected))
