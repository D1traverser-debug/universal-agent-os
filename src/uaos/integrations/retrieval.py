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
class KnowledgeInventoryCoverageReceipt:
    checked_repositories: tuple[str, ...]
    unavailable_historical_surfaces: tuple[str, ...]
    assurance: str = "SOURCE_ROLES_INSPECTED__CONTENT_EXHAUSTIVENESS_AND_NATIVE_INVOCATION_UNVERIFIED"


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
        historical_surface_evidence_refs: Mapping[str, str] | None = None,
    ) -> KnowledgeInventoryCoverageReceipt:
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

        unavailable: set[str] = set()
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
            for surface in expected_surfaces:
                if historical_surface_outcomes[surface] == "UNAVAILABLE_OR_NOT_CONNECTED":
                    unavailable.add(surface)
                    continue
                ref = (historical_surface_evidence_refs or {}).get(surface)
                if not isinstance(ref, str) or not ref.strip() or not verify_source_ref(ref):
                    raise RetrievalDenied("unverified historical knowledge source read: " + surface)
        return KnowledgeInventoryCoverageReceipt(
            checked_repositories=tuple(sorted(expected)),
            unavailable_historical_surfaces=tuple(sorted(unavailable)),
        )


@dataclass(frozen=True, slots=True)
class PlannedSourceRead:
    repository: str
    path: str
    phase: str
    purpose: str


@dataclass(frozen=True, slots=True)
class SourceReadPlan:
    """Deterministic owner/file discovery, NOT a model invocation or fetched-content proof."""
    selected_domain: str | None
    reads: tuple[PlannedSourceRead, ...]
    discovery_roots: tuple[tuple[str, str], ...] = ()
    assurance: str = "SOURCE_PATHS_RESOLVED_ONLY__NO_FILES_FETCHED_OR_NATIVE_ACTIVATION"


def build_source_read_plan(
    *,
    system_map: Mapping[str, object],
    task_index: Mapping[str, object],
    retrieval_policy: RetrievalPolicy,
    selected_domain: str | None = None,
    cold_start: bool = False,
    broad_knowledge: bool = False,
) -> SourceReadPlan:
    """Resolve the already-owned repository filelist; do not invent a second router.

    Plan only exact files whose owner has been resolved by SYSTEM_MAP/TASK_INDEX.
    Child-specific current business state is deliberately NOT guessed from templates.
    A caller must really fetch each source and prove freshness independently.
    """
    owner = system_map.get("controller")
    domains = system_map.get("domains")
    if not isinstance(owner, Mapping) or not isinstance(domains, Mapping):
        raise RetrievalDenied("current controller or domain map unavailable")
    parent = owner.get("repository")
    if not isinstance(parent, str) or not parent.strip():
        raise RetrievalDenied("controller repository unresolved")
    if selected_domain is not None and selected_domain not in domains:
        raise RetrievalDenied("domain not registered in current SYSTEM_MAP")
    reads: list[PlannedSourceRead] = []
    discovery: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(repo: str, path: str, phase: str, purpose: str) -> None:
        if not isinstance(repo, str) or not repo.strip():
            raise RetrievalDenied("source repository unresolved")
        if not isinstance(path, str) or not path.strip() or path.startswith("/") or (
            any(segment in {".", ".."} for segment in path.split("/"))
        ):
            raise RetrievalDenied("source path missing or unsafe")
        retrieval_policy.authorize(repo, path)
        key = (repo, path)
        if key not in seen:
            reads.append(PlannedSourceRead(repo, path, phase, purpose))
            seen.add(key)

    # Cold-start is a distinct, explicit bootstrap phase; don't reload a giant
    # entrypoint for every turn, but don't pretend a task pointer is its contents.
    if cold_start:
        add(parent, str(owner.get("entrypoint", "")), "BOOTSTRAP", "current entry and contract")
        add(parent, str(owner.get("system_state", "")), "BOOTSTRAP", "system identity and owner pointers")
    add(parent, "config/SYSTEM_MAP.json", "AUTHORITY", "live source owners")
    add(parent, str(owner.get("task_index", "")), "AUTHORITY", "exact task selection")

    if selected_domain is None:
        tasks = task_index.get("controller_tasks")
        if not isinstance(tasks, list):
            raise RetrievalDenied("controller task index missing")
        selected = [t for t in tasks if isinstance(t, Mapping) and t.get("default_resume") is True]
        if len(selected) != 1:
            raise RetrievalDenied("expected exactly one active default controller task")
        task = selected[0]
        if (
            task.get("authority_context") != "UAOS"
            or task.get("task_type") != "controller_maintenance"
            or task.get("resume_eligible") is not True
            or task.get("status") not in {"RUNNING", "HOLD"}
        ):
            raise RetrievalDenied("selected controller task authority, type, eligibility or status invalid")
        task_ref = task.get("state_ref")
        if not isinstance(task_ref, str) or not task_ref.startswith("state/tasks/"):
            raise RetrievalDenied("controller state reference unresolved")
        add(parent, task_ref, "CURRENT_TASK", "current task stage, goal and next action")
    else:
        domain = domains[selected_domain]
        if not isinstance(domain, Mapping):
            raise RetrievalDenied("registered domain mapping malformed")
        children = task_index.get("tasks")
        if not isinstance(children, list):
            raise RetrievalDenied("domain task index missing")
        bound = [row for row in children if isinstance(row, Mapping) and row.get("domain_id") == selected_domain]
        if len(bound) != 1:
            raise RetrievalDenied("domain owner task missing or ambiguous")
        parent_ref = bound[0].get("state_ref")
        if not isinstance(parent_ref, str) or not parent_ref.startswith("state/tasks/"):
            raise RetrievalDenied("parent domain router state reference unresolved")
        add(parent, parent_ref, "CURRENT_TASK", "parent router pointer, not child business state")
        child_repo = domain.get("repository")
        child_entry = domain.get("entrypoint")
        if not isinstance(child_repo, str) or not isinstance(child_entry, str):
            raise RetrievalDenied("registered child repository/entry unresolved")
        add(child_repo, child_entry, "CHILD_AUTHORITY", "child owns current business instructions")
        for item in (".uaos/MANIFEST.json", ".uaos/ADAPTER.json", ".uaos/CAPABILITIES.json"):
            add(child_repo, item, "CHILD_BINDING", "current capability and parent binding")
        # Child business task IDs, project files and checkpoints can depend on the
        # requested project/day. Do not guess those files from a generic router.
        for root in domain.get("rule_roots", ()):
            if not isinstance(root, str) or not root.strip():
                raise RetrievalDenied("malformed child evidence root")
            discovery.append((child_repo, root.rstrip("/") + "/"))

    if broad_knowledge:
        all_sources: list[tuple[str, Mapping[str, object]]] = [(parent, owner)]
        for name, domain in domains.items():
            if not isinstance(domain, Mapping):
                raise RetrievalDenied("malformed domain in broad inventory")
            repo = domain.get("repository")
            entry = domain.get("entrypoint")
            if not isinstance(repo, str) or not isinstance(entry, str):
                raise RetrievalDenied("unresolved domain in broad inventory")
            all_sources.append((repo, domain))
            add(repo, entry, "KNOWLEDGE_OWNER", "source owner first; study content is not automatically canonical")
        roots = retrieval_policy.knowledge_inventory_routing.get("source_roles", {})
        child = roots.get("registered_child_git", {}) if isinstance(roots, Mapping) else {}
        hints = child.get("root_hints_by_domain", {}) if isinstance(child, Mapping) else {}
        if not isinstance(hints, Mapping) or set(hints) != set(domains):
            raise RetrievalDenied("broad knowledge root hints do not match current registered domains")
        ctrl = roots.get("controller_git", {}) if isinstance(roots, Mapping) else {}
        for root in ctrl.get("knowledge_roots", ()):
            discovery.append((parent, str(root).rstrip("/") + "/"))
        for name, domain in domains.items():
            for root in hints.get(name, ()):
                discovery.append((str(domain["repository"]), str(root).rstrip("/") + "/"))
    return SourceReadPlan(selected_domain, tuple(reads), tuple(dict.fromkeys(discovery)))
