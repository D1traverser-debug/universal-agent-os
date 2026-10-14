from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from uaos.contracts.enums import TaskStatus
from uaos.kernel.control import TaskCandidate


@dataclass(frozen=True, slots=True)
class AgentLink:
    agent_id: str
    domain_id: str
    owner_aliases: tuple[str, ...]
    repository: str
    skill_ref: str
    agent_manifest_ref: str
    capability_ref: str
    uaos_adapter_ref: str
    new_task_mode: str
    business_repository_role: str

    def matches(self, value: str) -> bool:
        normalized = value.strip().lower()
        return normalized in {
            self.agent_id.lower(),
            self.domain_id.lower(),
            *(alias.lower() for alias in self.owner_aliases),
        }


@dataclass(frozen=True, slots=True)
class CurrentTaskRecord:
    task_id: str
    domain_id: str
    task_type: str
    display_name_zh: str
    status: TaskStatus
    resume_eligible: bool
    default_resume_within_domain: bool
    aliases: tuple[str, ...]
    current_stage: str
    state_ref: str

    def matches(self, value: str) -> bool:
        normalized = value.strip().lower()
        return normalized == self.task_id.lower() or normalized in {alias.lower() for alias in self.aliases}

    def as_candidate(self) -> TaskCandidate:
        # Current task ordering is resolved by explicit identity/defaults and durable state,
        # never by fabricated recency from a registry file.
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
    def __init__(self, agents: tuple[AgentLink, ...], tasks: tuple[CurrentTaskRecord, ...]) -> None:
        if len({agent.agent_id for agent in agents}) != len(agents):
            raise ValueError("duplicate agent_id")
        if len({agent.domain_id for agent in agents}) != len(agents):
            raise ValueError("duplicate domain_id")
        known_domains = {agent.domain_id for agent in agents}
        unknown = {task.domain_id for task in tasks} - known_domains
        if unknown:
            raise ValueError(f"tasks reference unknown domains: {sorted(unknown)}")
        for agent in agents:
            refs = (agent.skill_ref, agent.agent_manifest_ref, agent.capability_ref, agent.uaos_adapter_ref)
            if any("continuity/" in ref for ref in refs):
                raise ValueError(f"active agent {agent.agent_id} references retired continuity namespace")
            if agent.new_task_mode != "UAOS_NATIVE":
                raise ValueError(f"active agent {agent.agent_id} is not UAOS_NATIVE")
        defaults: dict[str, int] = {}
        for task in tasks:
            if not task.state_ref.startswith("state/tasks/"):
                raise ValueError(f"active task state must live under state/tasks/: {task.task_id}")
            if task.default_resume_within_domain and task.resume_eligible:
                defaults[task.domain_id] = defaults.get(task.domain_id, 0) + 1
        ambiguous = sorted(domain for domain, count in defaults.items() if count > 1)
        if ambiguous:
            raise ValueError(f"multiple default-resume tasks in domains: {ambiguous}")
        self.agents = agents
        self.tasks = tasks

    @classmethod
    def from_paths(cls, agent_registry: str | Path, task_index: str | Path) -> "AgentLinkRegistry":
        agent_data = json.loads(Path(agent_registry).read_text(encoding="utf-8"))
        task_data = json.loads(Path(task_index).read_text(encoding="utf-8"))
        agents = tuple(
            AgentLink(
                agent_id=item["agent_id"],
                domain_id=item["domain_id"],
                owner_aliases=tuple(item.get("owner_aliases", [])),
                repository=item["repository"],
                skill_ref=item["skill_ref"],
                agent_manifest_ref=item["agent_manifest_ref"],
                capability_ref=item["capability_ref"],
                uaos_adapter_ref=item["uaos_adapter_ref"],
                new_task_mode=item["new_task_mode"],
                business_repository_role=item["business_repository_role"],
            )
            for item in agent_data["agents"]
        )
        tasks = tuple(
            CurrentTaskRecord(
                task_id=item["task_id"],
                domain_id=item["domain_id"],
                task_type=item["task_type"],
                display_name_zh=item["display_name_zh"],
                status=TaskStatus(item["status"]),
                resume_eligible=bool(item["resume_eligible"]),
                default_resume_within_domain=bool(item["default_resume_within_domain"]),
                aliases=tuple(item.get("aliases", [])),
                current_stage=item["current_stage"],
                state_ref=item["state_ref"],
            )
            for item in task_data["tasks"]
        )
        return cls(agents, tasks)

    def resolve_agent(self, hint: str) -> AgentLink:
        matches = [agent for agent in self.agents if agent.matches(hint)]
        if len(matches) != 1:
            raise LookupError(f"agent hint is not uniquely resolvable: {hint}")
        return matches[0]

    def resolve_task(self, hint: str) -> CurrentTaskRecord:
        matches = [task for task in self.tasks if task.matches(hint)]
        if len(matches) != 1:
            raise LookupError(f"task hint is not uniquely resolvable: {hint}")
        return matches[0]

    def domain_candidates(self, domain_id: str) -> tuple[TaskCandidate, ...]:
        return tuple(task.as_candidate() for task in self.tasks if task.domain_id == domain_id)
