from __future__ import annotations

try:
    import fcntl
except ImportError:  # pragma: no cover - exercised by fail-closed platform guard
    fcntl = None  # type: ignore[assignment]

import hashlib
import os
from pathlib import Path
import secrets
import stat
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
    """Zero-cost file executor confined to one explicit workspace root.

    Execution uses directory-file-descriptor relative operations. Parent components are
    opened with ``O_NOFOLLOW`` and retained as directory descriptors, so changing a
    pathname to a symlink after admission cannot redirect the write outside the bound
    workspace. CREATE is committed with an atomic hard-link no-replace operation.
    UPDATE holds an advisory exclusive lock on the already-open parent directory across
    hash verification and atomic rename; cooperating UAOS writers therefore cannot race
    an expected-hash compare-and-update sequence.

    The directory lock is deliberately advisory: it coordinates this executor family,
    not arbitrary external programs that ignore POSIX locks. Expected-hash updates also
    re-read immediately before rename to detect non-cooperating changes observed before
    commit. Platforms without the required dir-fd/no-follow/flock primitives fail closed
    rather than silently falling back to path-based mutation.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._require_secure_fs_primitives()

    @staticmethod
    def _require_secure_fs_primitives() -> None:
        required = (os.open, os.mkdir, os.unlink, os.stat, os.link, os.rename)
        if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
            raise RuntimeError("local workspace requires O_NOFOLLOW and O_DIRECTORY")
        if fcntl is None or not hasattr(fcntl, "flock"):
            raise RuntimeError("local workspace requires POSIX flock support")
        supports = getattr(os, "supports_dir_fd", set())
        missing = [func.__name__ for func in required if func not in supports]
        if missing:
            raise RuntimeError(
                "local workspace requires dir_fd filesystem primitives: "
                + ",".join(sorted(missing))
            )

    @staticmethod
    def _sha256(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def _target_parts(target: str) -> tuple[str, ...]:
        if not isinstance(target, str) or not target.strip():
            raise ValueError("target is required")
        if "\x00" in target:
            raise ValueError("target contains NUL")
        if os.path.isabs(target):
            raise PermissionError("absolute workspace targets are forbidden")
        normalized = os.path.normpath(target)
        if normalized in {"", "."}:
            raise ValueError("target must name a file")
        parts = Path(normalized).parts
        if not parts or any(part in {"", ".", ".."} for part in parts):
            raise PermissionError("target escapes workspace root")
        return tuple(parts)

    def canonicalize_target(self, target: str) -> str:
        parts = self._target_parts(target)
        return f"file://{self.root.joinpath(*parts).as_posix()}"

    def _open_parent(self, target: str, *, create_parents: bool) -> tuple[int, str]:
        parts = self._target_parts(target)
        leaf = parts[-1]
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        current_fd = os.open(self.root, flags)
        try:
            for component in parts[:-1]:
                try:
                    child_fd = os.open(component, flags, dir_fd=current_fd)
                except FileNotFoundError:
                    if not create_parents:
                        raise
                    try:
                        os.mkdir(component, 0o755, dir_fd=current_fd)
                    except FileExistsError:
                        pass
                    child_fd = os.open(component, flags, dir_fd=current_fd)
                previous_fd = current_fd
                current_fd = child_fd
                os.close(previous_fd)
            return current_fd, leaf
        except Exception:
            os.close(current_fd)
            raise

    @staticmethod
    def _lock_parent(parent_fd: int) -> None:
        assert fcntl is not None
        fcntl.flock(parent_fd, fcntl.LOCK_EX)

    @staticmethod
    def _unlock_parent(parent_fd: int) -> None:
        if fcntl is None:
            return
        try:
            fcntl.flock(parent_fd, fcntl.LOCK_UN)
        except OSError:
            # Unlock/close does not roll back an already completed filesystem commit.
            # The operation's durability is established by directory fsync before this.
            pass

    @staticmethod
    def _safe_close(fd: int) -> None:
        try:
            os.close(fd)
        except OSError:
            pass

    @staticmethod
    def _read_regular_file(parent_fd: int, leaf: str) -> tuple[bytes, os.stat_result]:
        fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise PermissionError("workspace target must be a regular file")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks), info
        finally:
            os.close(fd)

    @staticmethod
    def _write_temp(parent_fd: int, leaf: str, content: bytes) -> str:
        temporary = f".{leaf}.uaos-{secrets.token_hex(12)}"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        fd = os.open(temporary, flags, 0o600, dir_fd=parent_fd)
        try:
            view = memoryview(content)
            offset = 0
            while offset < len(view):
                offset += os.write(fd, view[offset:])
            os.fsync(fd)
        except Exception:
            os.close(fd)
            try:
                os.unlink(temporary, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
            raise
        else:
            os.close(fd)
        return temporary

    @staticmethod
    def _post_commit_unknown(
        request: ExecutionRequest,
        *,
        digest: str,
        commit_semantics: str,
        exc: Exception,
    ) -> ExecutionOutcome:
        return ExecutionOutcome(
            ExecutionDisposition.UNKNOWN,
            output={"path": request.target, "sha256": digest},
            evidence={
                "sha256": digest,
                "commit_point_reached": True,
                "commit_semantics": commit_semantics,
            },
            error=(
                "filesystem mutation crossed commit point but cleanup/durability "
                f"confirmation failed: {type(exc).__name__}: {exc}"
            ),
        )

    def _create_text(self, request: ExecutionRequest) -> ExecutionOutcome:
        if not isinstance(request.payload, Mapping) or not isinstance(
            request.payload.get("content"), str
        ):
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error="local.create_text requires string payload['content']",
            )
        parent_fd = None
        temporary = None
        committed = False
        digest = ""
        locked = False
        commit_semantics = "ATOMIC_CREATE_NO_REPLACE"
        try:
            parent_fd, leaf = self._open_parent(request.target, create_parents=True)
            self._lock_parent(parent_fd)
            locked = True
            content = request.payload["content"].encode("utf-8")
            digest = self._sha256(content)
            expected_current_hash = request.payload.get("expected_current_hash")
            if expected_current_hash is not None and expected_current_hash != self._sha256(b""):
                return ExecutionOutcome(
                    ExecutionDisposition.FAILED,
                    error="CREATE expected_current_hash must represent an absent/empty target",
                )
            temporary = self._write_temp(parent_fd, leaf, content)
            os.link(
                temporary,
                leaf,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
            committed = True
            os.unlink(temporary, dir_fd=parent_fd)
            temporary = None
            os.fsync(parent_fd)
            return ExecutionOutcome(
                ExecutionDisposition.CONFIRMED,
                output={"path": request.target, "sha256": digest},
                evidence={
                    "sha256": digest,
                    "commit_semantics": commit_semantics,
                    "concurrency_semantics": "ADVISORY_PARENT_DIRECTORY_LOCK",
                },
            )
        except FileExistsError:
            if committed:
                return self._post_commit_unknown(
                    request,
                    digest=digest,
                    commit_semantics=commit_semantics,
                    exc=FileExistsError("post-commit cleanup collision"),
                )
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error="CREATE target already exists",
            )
        except Exception as exc:
            if committed:
                return self._post_commit_unknown(
                    request,
                    digest=digest,
                    commit_semantics=commit_semantics,
                    exc=exc,
                )
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error=f"{type(exc).__name__}: {exc}",
            )
        finally:
            if parent_fd is not None:
                if temporary is not None:
                    try:
                        os.unlink(temporary, dir_fd=parent_fd)
                    except OSError:
                        pass
                if locked:
                    self._unlock_parent(parent_fd)
                self._safe_close(parent_fd)

    def _update_text(self, request: ExecutionRequest) -> ExecutionOutcome:
        if not isinstance(request.payload, Mapping) or not isinstance(
            request.payload.get("content"), str
        ):
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error="local.update_text requires string payload['content']",
            )
        parent_fd = None
        temporary = None
        committed = False
        digest = ""
        locked = False
        commit_semantics = "LOCKED_COMPARE_AND_ATOMIC_RENAME"
        try:
            parent_fd, leaf = self._open_parent(request.target, create_parents=False)
            self._lock_parent(parent_fd)
            locked = True
            current, original_info = self._read_regular_file(parent_fd, leaf)
            expected_current_hash = request.payload.get("expected_current_hash")
            if expected_current_hash is not None and self._sha256(current) != expected_current_hash:
                return ExecutionOutcome(
                    ExecutionDisposition.FAILED,
                    error="current hash mismatch",
                )

            content = request.payload["content"].encode("utf-8")
            digest = self._sha256(content)
            temporary = self._write_temp(parent_fd, leaf, content)
            latest, latest_info = self._read_regular_file(parent_fd, leaf)
            if (latest_info.st_dev, latest_info.st_ino) != (
                original_info.st_dev,
                original_info.st_ino,
            ):
                return ExecutionOutcome(
                    ExecutionDisposition.FAILED,
                    error="UPDATE target identity changed before commit",
                )
            if expected_current_hash is not None and self._sha256(latest) != expected_current_hash:
                return ExecutionOutcome(
                    ExecutionDisposition.FAILED,
                    error="UPDATE target content changed before commit",
                )

            # The hash check and rename occur while cooperating UAOS writers are
            # excluded by the parent-directory flock. The final content re-read above
            # also detects non-cooperating writes that become visible before commit.
            os.rename(
                temporary,
                leaf,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
            )
            committed = True
            temporary = None
            os.fsync(parent_fd)
            return ExecutionOutcome(
                ExecutionDisposition.CONFIRMED,
                output={"path": request.target, "sha256": digest},
                evidence={
                    "sha256": digest,
                    "commit_semantics": commit_semantics,
                    "concurrency_semantics": (
                        "ADVISORY_PARENT_DIRECTORY_LOCK__EXPECTED_HASH_RECHECK__ATOMIC_RENAME"
                    ),
                },
            )
        except FileNotFoundError:
            if committed:
                return self._post_commit_unknown(
                    request,
                    digest=digest,
                    commit_semantics=commit_semantics,
                    exc=FileNotFoundError("post-commit durability confirmation failed"),
                )
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error="UPDATE target does not exist",
            )
        except Exception as exc:
            if committed:
                return self._post_commit_unknown(
                    request,
                    digest=digest,
                    commit_semantics=commit_semantics,
                    exc=exc,
                )
            return ExecutionOutcome(
                ExecutionDisposition.FAILED,
                error=f"{type(exc).__name__}: {exc}",
            )
        finally:
            if parent_fd is not None:
                if temporary is not None:
                    try:
                        os.unlink(temporary, dir_fd=parent_fd)
                    except OSError:
                        pass
                if locked:
                    self._unlock_parent(parent_fd)
                self._safe_close(parent_fd)

    def execute(self, request: ExecutionRequest) -> ExecutionOutcome:
        if request.action_name == "local.create_text":
            return self._create_text(request)
        if request.action_name == "local.update_text":
            return self._update_text(request)
        if request.action_name == "local.read_bytes":
            parent_fd = None
            try:
                parent_fd, leaf = self._open_parent(request.target, create_parents=False)
                content, _ = self._read_regular_file(parent_fd, leaf)
                return ExecutionOutcome(
                    ExecutionDisposition.CONFIRMED,
                    output=content,
                    evidence={"sha256": self._sha256(content)},
                )
            except FileNotFoundError:
                return ExecutionOutcome(
                    ExecutionDisposition.FAILED,
                    error="target does not exist",
                )
            except Exception as exc:
                return ExecutionOutcome(
                    ExecutionDisposition.FAILED,
                    error=f"{type(exc).__name__}: {exc}",
                )
            finally:
                if parent_fd is not None:
                    self._safe_close(parent_fd)
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
