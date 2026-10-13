from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class SubsystemLifecycle(StrEnum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


@dataclass(frozen=True, slots=True)
class SubsystemDescriptor:
    subsystem_id: str
    owner: str
    root_path: str
    parent_id: str | None = None
    dependencies: tuple[str, ...] = ()
    rule_refs: tuple[str, ...] = ()
    state_refs: tuple[str, ...] = ()
    knowledge_refs: tuple[str, ...] = ()
    workflow_refs: tuple[str, ...] = ()
    validation_refs: tuple[str, ...] = ()
    lifecycle: SubsystemLifecycle = SubsystemLifecycle.ACTIVE

    def __post_init__(self) -> None:
        if not all((self.subsystem_id.strip(), self.owner.strip(), self.root_path.strip())):
            raise ValueError("subsystem identity, owner and root_path are required")
        if self.subsystem_id in self.dependencies or self.parent_id == self.subsystem_id:
            raise ValueError("subsystem cannot depend on itself")


class TopologyRegistry:
    def __init__(self) -> None:
        self._nodes: dict[str, SubsystemDescriptor] = {}
        self._authorities: dict[str, str] = {}

    def register(self, descriptor: SubsystemDescriptor) -> None:
        if descriptor.subsystem_id in self._nodes:
            raise ValueError(f"duplicate subsystem: {descriptor.subsystem_id}")
        refs = set(descriptor.dependencies)
        if descriptor.parent_id:
            refs.add(descriptor.parent_id)
        missing = refs - set(self._nodes)
        if missing:
            raise ValueError(f"unknown topology references: {sorted(missing)}")
        self._nodes[descriptor.subsystem_id] = descriptor

    def get(self, subsystem_id: str) -> SubsystemDescriptor:
        return self._nodes[subsystem_id]

    def bind_authority(self, authority_key: str, subsystem_id: str, *, replace_existing: bool = False) -> None:
        if subsystem_id not in self._nodes or self._nodes[subsystem_id].lifecycle is SubsystemLifecycle.RETIRED:
            raise ValueError("authority owner must be an active/deprecated registered subsystem")
        current = self._authorities.get(authority_key)
        if current is not None and current != subsystem_id and not replace_existing:
            raise ValueError(f"authority already bound: {authority_key} -> {current}")
        self._authorities[authority_key] = subsystem_id

    def authority_owner(self, authority_key: str) -> str:
        return self._authorities[authority_key]

    def impact_closure(self, subsystem_id: str) -> frozenset[str]:
        if subsystem_id not in self._nodes:
            raise KeyError(subsystem_id)
        impacted = {subsystem_id}
        changed = True
        while changed:
            changed = False
            for node in self._nodes.values():
                if node.subsystem_id in impacted:
                    continue
                refs = set(node.dependencies)
                if node.parent_id:
                    refs.add(node.parent_id)
                if refs.intersection(impacted):
                    impacted.add(node.subsystem_id)
                    changed = True
        return frozenset(impacted)

    def deprecate(self, subsystem_id: str) -> SubsystemDescriptor:
        current = self.get(subsystem_id)
        if current.lifecycle is not SubsystemLifecycle.ACTIVE:
            raise ValueError("only ACTIVE subsystem may be deprecated")
        updated = replace(current, lifecycle=SubsystemLifecycle.DEPRECATED)
        self._nodes[subsystem_id] = updated
        return updated

    def retire(self, subsystem_id: str) -> SubsystemDescriptor:
        current = self.get(subsystem_id)
        active_dependents = self.impact_closure(subsystem_id) - {subsystem_id}
        active_dependents = {sid for sid in active_dependents if self._nodes[sid].lifecycle is not SubsystemLifecycle.RETIRED}
        if active_dependents:
            raise ValueError(f"cannot retire subsystem with active dependents: {sorted(active_dependents)}")
        bound = [key for key, owner in self._authorities.items() if owner == subsystem_id]
        if bound:
            raise ValueError(f"cannot retire subsystem while authorities remain bound: {sorted(bound)}")
        updated = replace(current, lifecycle=SubsystemLifecycle.RETIRED)
        self._nodes[subsystem_id] = updated
        return updated
