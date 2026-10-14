from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from uaos.contracts.enums import TaskStatus
from uaos.kernel.control import TaskCandidate


class MigrationDisposition(StrEnum):
    ROUTING_ENTRY_ONLY = "ROUTING_ENTRY_ONLY"
    LAZY_IMPORT_ON_CONTINUE = "LAZY_IMPORT_ON_CONTINUE"
    HISTORICAL_STALE_REQUIRES_RECONCILIATION = "HISTORICAL_STALE_REQUIRES_RECONCILIATION"
    UAOS_NATIVE = "UAOS_NATIVE"


@dataclass(frozen=True, slots=True)
class AgentLink:
    agent_id: str
    domain_id: str
    owner_aliases: tuple[str, ...]
    repository: str
    skill_ref: str
    agent_manifest_ref: str
    capability_ref: str
    task_index_ref: str
    uaos_adapter_ref: str
    legacy_protocol_ref: str
    new_task_mode: str
    legacy_resume_mode: str
    business_repository_role: str

    def matches(self, value: str) -> bool:
        normalized = value.strip().lower()
        return normalized in {self.agent_id.lower(), self.domain_id.lower(), *(x.lower() for x in self.owner_aliases)}


@dataclass(frozen=True, slots=True)
class LegacyTaskSeed:
    task_id: str
    domain_id: str
    task_type: str
    display_name_zh: str
    status: TaskStatus
    resume_eligible: bool
    default_resume_within_domain: bool
    aliases: tuple[str, ...]
    migration_disposition: MigrationDisposition
    current_stage: str
    next_action: str
    legacy_source_refs: tuple[str, ...]

    def matches(self, value: str) -> bool:
        normalized = value.strip().lower()
        return normalized == self.task_id.lower() or normalized in {x.lower() for x in self.aliases}

    def as_candidate(self) -> TaskCandidate:
        # Cutover seeds intentionally omit a synthetic updated_at ordering signal.
        # Resolution must use exact identity/domain defaults rather than guessing by recency.
        from datetime import UTC, datetime
        return TaskCandidate(
            task_id=self.task_id,
            owner_domain=self.domain_id,
            task_type=self.task_type,
            status=self.status,
            updated_at=datetime(1970, 1, 1, tzinfo=UTC),
            resume_eligible=self.resume_eligible,
            default_resume=self.default_resume_within_domain,
        )


class AgentLinkRegistry:
    def __init__(self, agents: tuple[AgentLink, ...], tasks: tuple[LegacyTaskSeed, ...]) -> None:
        if len({a.agent_id for a in agents}) != len(agents):
            raise ValueError("duplicate agent_id")
        if len({a.domain_id for a in agents}) != len(agents):
            raise ValueError("duplicate domain_id")
        known_domains = {a.domain_id for a in agents}
        unknown = {task.domain_id for task in tasks} - known_domains
        if unknown:
            raise ValueError(f"legacy tasks reference unknown domains: {sorted(unknown)}")
        self.agents = agents
        self.tasks = tasks

    @classmethod
    def from_paths(cls, agent_registry: str | Path, task_index: str | Path) -> "AgentLinkRegistry":
        agent_data = json.loads(Path(agent_registry).read_text(encoding="utf-8"))
        task_data = json.loads(Path(task_index).read_text(encoding="utf-8"))
        agents = tuple(AgentLink(
            agent_id=item["agent_id"],
            domain_id=item["domain_id"],
            owner_aliases=tuple(item.get("owner_aliases", [])),
            repository=item["repository"],
            skill_ref=item["skill_ref"],
            agent_manifest_ref=item["agent_manifest_ref"],
            capability_ref=item["capability_ref"],
            task_index_ref=item["task_index_ref"],
            uaos_adapter_ref=item["uaos_adapter_ref"],
            legacy_protocol_ref=item["legacy_protocol_ref"],
            new_task_mode=item["new_task_mode"],
            legacy_resume_mode=item["legacy_resume_mode"],
            business_repository_role=item["business_repository_role"],
        ) for item in agent_data["agents"])
        tasks = tuple(LegacyTaskSeed(
            task_id=item["task_id"],
            domain_id=item["domain_id"],
            task_type=item["task_type"],
            display_name_zh=item["display_name_zh"],
            status=TaskStatus(item["status"]),
            resume_eligible=bool(item["resume_eligible"]),
            default_resume_within_domain=bool(item["default_resume_within_domain"]),
            aliases=tuple(item.get("aliases", [])),
            migration_disposition=MigrationDisposition(item["migration_disposition"]),
            current_stage=item["current_stage"],
            next_action=item["next_action"],
            legacy_source_refs=tuple(item.get("legacy_source_refs", [])),
        ) for item in task_data["tasks"])
        return cls(agents, tasks)

    def resolve_agent(self, hint: str) -> AgentLink:
        matches = [agent for agent in self.agents if agent.matches(hint)]
        if len(matches) != 1:
            raise LookupError(f"agent hint is not uniquely resolvable: {hint}")
        return matches[0]

    def resolve_task(self, hint: str) -> LegacyTaskSeed:
        matches = [task for task in self.tasks if task.matches(hint)]
        if len(matches) != 1:
            raise LookupError(f"task hint is not uniquely resolvable: {hint}")
        return matches[0]

    def domain_candidates(self, domain_id: str) -> tuple[TaskCandidate, ...]:
        return tuple(task.as_candidate() for task in self.tasks if task.domain_id == domain_id)

    def migration_action(self, task_id: str, *, already_imported: bool) -> str:
        if already_imported:
            return "RESUME_UAOS"
        task = self.resolve_task(task_id)
        if task.migration_disposition is MigrationDisposition.ROUTING_ENTRY_ONLY:
            return "ROUTE_OR_CREATE_UAOS_TASK"
        if task.migration_disposition is MigrationDisposition.HISTORICAL_STALE_REQUIRES_RECONCILIATION:
            return "RECONCILE_BEFORE_IMPORT"
        if task.migration_disposition is MigrationDisposition.LAZY_IMPORT_ON_CONTINUE:
            return "READ_LEGACY_SOURCE_ONCE__IMPORT__THEN_UAOS_WRITE_ONLY"
        return "RESUME_UAOS"
