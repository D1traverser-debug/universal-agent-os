from __future__ import annotations

from threading import RLock
from typing import Generic, TypeVar

from .ports import NotFound, VersionConflict, Versioned

T = TypeVar("T")


class InMemoryVersionedRepository(Generic[T]):
    """Reference semantics for optimistic authoritative writes.

    Production storage is PostgreSQL. This implementation exists to make the
    version/CAS contract executable before a database service is available.
    """

    def __init__(self) -> None:
        self._items: dict[str, Versioned[T]] = {}
        self._lock = RLock()

    def get(self, object_id: str) -> Versioned[T]:
        with self._lock:
            try:
                return self._items[object_id]
            except KeyError as exc:
                raise NotFound(object_id) from exc

    def create(self, object_id: str, value: T) -> Versioned[T]:
        with self._lock:
            if object_id in self._items:
                raise VersionConflict(f"{object_id} already exists")
            versioned = Versioned(value=value, version=1)
            self._items[object_id] = versioned
            return versioned

    def compare_and_set(self, object_id: str, expected_version: int, value: T) -> Versioned[T]:
        with self._lock:
            current = self.get(object_id)
            if current.version != expected_version:
                raise VersionConflict(
                    f"stale version for {object_id}: expected {expected_version}, current {current.version}"
                )
            updated = Versioned(value=value, version=current.version + 1)
            self._items[object_id] = updated
            return updated
