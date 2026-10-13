from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class CompatibilityMode(StrEnum):
    DIRECT = "DIRECT"
    MIGRATE = "MIGRATE"
    BLOCK = "BLOCK"


@dataclass(frozen=True, slots=True)
class CompatibilityDecision:
    mode: CompatibilityMode
    from_version: str
    to_version: str
    migration_id: str | None = None
    reason: str = ""


@dataclass(frozen=True, slots=True)
class VersionCompatibilityPolicy:
    current_version: str
    directly_supported: frozenset[str] = frozenset()
    migrations: Mapping[str, str] = None

    def __post_init__(self) -> None:
        if not self.current_version.strip():
            raise ValueError("current_version is required")
        if self.migrations is None:
            object.__setattr__(self, "migrations", {})

    def decide(self, from_version: str) -> CompatibilityDecision:
        if from_version == self.current_version or from_version in self.directly_supported:
            return CompatibilityDecision(CompatibilityMode.DIRECT, from_version, self.current_version, reason="compatible runtime semantics")
        migration = self.migrations.get(from_version)
        if migration:
            return CompatibilityDecision(CompatibilityMode.MIGRATE, from_version, self.current_version, migration, "explicit migration required")
        return CompatibilityDecision(CompatibilityMode.BLOCK, from_version, self.current_version, reason="no compatible interpretation or migration is registered")
