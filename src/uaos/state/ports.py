from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")


class VersionConflict(RuntimeError):
    pass


class NotFound(KeyError):
    pass


@dataclass(frozen=True, slots=True)
class Versioned(Generic[T]):
    value: T
    version: int


class VersionedRepository(Protocol[T]):
    def get(self, object_id: str) -> Versioned[T]: ...
    def create(self, object_id: str, value: T) -> Versioned[T]: ...
    def compare_and_set(self, object_id: str, expected_version: int, value: T) -> Versioned[T]: ...
