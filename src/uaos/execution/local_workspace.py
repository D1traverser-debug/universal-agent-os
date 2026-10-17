from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
import time
from typing import Mapping

from .models import (
    CapabilityAvailability,
    CapabilityCostClass,
    CapabilityHealth,
    CapabilityObservation,
    ExecutionDisposition,
    ExecutionOutcome,
    ExecutionRequest,
)
from .persistent_assets import CrudOperation, MutationContract, MutationPersistence
from .registry import CapabilityRegistry


class LocalWorkspaceExecutor:
    """Zero-cost file executor confined to one explicit workspace root."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, target: str) -> Path:
        if not target.strip():
            raise ValueError("target is required")
        path = (self.root / target).resolve()
        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise PermissionError("target escapes workspace root") from exc
        return path

    def canonicalize_target(self, target: str) -> str:
        return f"file://{self._resolve(target).as_posix()}"

    @staticmethod
    def _sha256(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _write_text(self, request: ExecutionRequest, path: Path, *, create: bool) -> ExecutionOutcome:
        if not isinstance(request.payload, Mapping) or not isinstance(
            request.payload.get("content"), str
        ):
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error=f"{request.action_name} requires string payload['content']",
            )
        if create and path.exists():
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error="CREATE target already exists",
            )
        if not create and not path.exists():
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error="UPDATE target does not exist",
            )

        current = path.read_bytes() if path.exists() else b""
        expected_current_hash = request.payload.get("expected_current_hash")
        if expected_current_hash is not None and self._sha256(current) != expected_current_hash:
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error="current hash mismatch",
            )

        content = request.payload["content"].encode("utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.uaos-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            if create and path.exists():
                return ExecutionOutcome(
                    ExecutionDisposition.FAILED,
                    error="CREATE target appeared before commit",
                )
            if not create and not path.exists():
                return ExecutionOutcome(
                    ExecutionDisposition.FAILED,
                    error="UPDATE target disappeared before commit",
                )
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

        digest = self._sha256(content)
        return ExecutionOutcome(
            ExecutionDisposition.CONFIRMED,
            output={"path": request.target, "sha256": digest},
            evidence={"sha256": digest},
        )

    def execute(self, request: ExecutionRequest) -> ExecutionOutcome:
        try:
            path = self._resolve(request.target)
        except Exception as exc:
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error=f"{type(exc).__name__}: {exc}",
            )

        if request.action_name == "local.read_bytes":
            if not path.exists():
                return ExecutionOutcome(
                    ExecutionDisposition.FAILED, error="target does not exist"
                )
            content = path.read_bytes()
            return ExecutionOutcome(
                ExecutionDisposition.CONFIRMED,
                output=content,
                evidence={"sha256": self._sha256(content)},
            )
        if request.action_name == "local.create_text":
            return self._write_text(request, path, create=True)
        if request.action_name == "local.update_text":
            return self._write_text(request, path, create=False)
        return ExecutionOutcome(
            ExecutionDisposition.FAILED,
            error=f"unsupported local workspace action: {request.action_name}",
        )


def register_local_workspace_capability(
    registry: CapabilityRegistry,
    root: str | Path,
    *,
    capability_id: str = "local.workspace",
) -> CapabilityObservation:
    executor = LocalWorkspaceExecutor(root)
    observation = CapabilityObservation(
        capability_id=capability_id,
        health=CapabilityHealth.AVAILABLE,
        observed_at_epoch=time.time(),
        supported_actions=("local.read_bytes", "local.create_text", "local.update_text"),
        permissions=("workspace:read", "workspace:write"),
        quality_score=1.0,
        estimated_cost=0.0,
        executor_kind="local_workspace",
        metadata={"root": str(Path(root).resolve())},
        cost_class=CapabilityCostClass.FREE,
        availability=CapabilityAvailability.LOCAL,
    )
    registry.register(
        observation,
        executor,
        read_only_actions={"local.read_bytes"},
        mutation_contracts={
            "local.create_text": MutationContract(
                MutationPersistence.DURABLE_OR_EXTERNAL,
                CrudOperation.CREATE,
            ),
            "local.update_text": MutationContract(
                MutationPersistence.DURABLE_OR_EXTERNAL,
                CrudOperation.UPDATE,
            ),
        },
        canonicalize_target=executor.canonicalize_target,
    )
    return observation
