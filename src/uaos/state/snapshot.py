"""Portable, integrity-checked snapshots of the existing SQLite/artifact owner.

This module is a storage adapter, not a second task/evolution authority.
Its restore API remains an explicitly called filesystem operation, not proof
that native chat or arbitrary external writes pass through ActionCoordinator.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
import json
import os
import stat
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import tempfile
from typing import BinaryIO, Iterator


@dataclass(frozen=True, slots=True)
class SnapshotManifest:
    format_version: int
    created_at: str
    schema_version: str
    database_sha256: str
    artifacts: tuple[tuple[str, str, int], ...]


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()



@contextmanager
def _open_regular_beneath(root: Path, relative: PurePosixPath) -> Iterator[BinaryIO]:
    """Open a regular file under a directory without following POSIX symlinks.

    For platforms lacking POSIX dir_fd/O_NOFOLLOW, retain a conservative
    path-based compatibility fallback, *not* a cross-platform race guarantee.
    """
    if os.name != "posix":
        current = root
        for component in relative.parts:
            if current.is_symlink():
                raise ValueError("symlinked artifact path")
            current = current / component
        if current.is_symlink() or not current.is_file():
            raise ValueError("unsafe artifact path")
        with current.open("rb") as stream:
            yield stream
        return

    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
    directory_fd: int | None = None
    file_fd: int | None = None
    try:
        directory_fd = os.open(root, flags)
        for part in relative.parts[:-1]:
            next_fd = os.open(part, flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        file_fd = os.open(
            relative.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
            dir_fd=directory_fd,
        )
        if not stat.S_ISREG(os.fstat(file_fd).st_mode):
            raise ValueError("snapshot artifact is not a regular file")
        stream = os.fdopen(file_fd, "rb")
        file_fd = None
        with stream:
            yield stream
    except OSError as exc:
        raise ValueError(f"unsafe or replaced snapshot path: {relative}") from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if directory_fd is not None:
            os.close(directory_fd)


def _stable_file_stat(stream: BinaryIO) -> tuple[int, int, int]:
    info = os.fstat(stream.fileno())
    return info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _hash_artifact_beneath(root: Path, relative: PurePosixPath) -> tuple[str, int]:
    digest = sha256()
    size = 0
    with _open_regular_beneath(root, relative) as stream:
        before = _stable_file_stat(stream)
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
        after = _stable_file_stat(stream)
        if before != after or size != after[0]:
            raise ValueError(f"artifact changed while reading: {relative}")
    return digest.hexdigest(), size


def _copy_artifact_beneath(root: Path, relative: PurePosixPath, target: Path) -> None:
    """Copy by a symlink-resistant file descriptor; validate after staging."""
    with _open_regular_beneath(root, relative) as source:
        before = _stable_file_stat(source)
        with target.open("xb") as output:
            shutil.copyfileobj(source, output)
        after = _stable_file_stat(source)
        if before != after or target.stat().st_size != after[0]:
            raise ValueError(f"artifact changed during copy: {relative}")


def _artifact_names_beneath(root: Path) -> set[str]:
    """Enumerate files with no-follow directory handles on POSIX."""
    if os.name != "posix":
        result: set[str] = set()
        for entry in root.rglob("*"):
            if entry.is_symlink():
                raise ValueError(f"snapshot contains a symlink: {entry}")
            if entry.is_file():
                result.add(entry.relative_to(root).as_posix())
            elif not entry.is_dir():
                raise ValueError(f"unexpected snapshot artifact type: {entry}")
        return result

    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
    def walk(directory_fd: int, prefix: str, found: set[str]) -> None:
        with os.scandir(directory_fd) as entries:
            for entry in entries:
                name = f"{prefix}/{entry.name}" if prefix else entry.name
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISREG(info.st_mode):
                    found.add(name)
                elif stat.S_ISDIR(info.st_mode):
                    child_fd = os.open(entry.name, flags, dir_fd=directory_fd)
                    try:
                        walk(child_fd, name, found)
                    finally:
                        os.close(child_fd)
                else:
                    raise ValueError(f"unexpected or symlinked snapshot entry: {name}")
    try:
        root_fd = os.open(root, flags)
        try:
            result: set[str] = set()
            walk(root_fd, "", result)
            return result
        finally:
            os.close(root_fd)
    except OSError as exc:
        raise ValueError("snapshot artifact tree changed or contains a symlink") from exc


def _safe_artifact_name(name: object) -> PurePosixPath:
    """Treat names as portable relative identifiers, never host paths."""
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("invalid snapshot artifact path")
    parts = name.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("invalid snapshot artifact path")
    # Version-1 POSIX snapshots historically allow colons in filenames. Reject
    # drive-like segments only on Windows where Path interprets them as drives.
    if os.name == "nt" and any(":" in part for part in parts):
        raise ValueError("invalid Windows snapshot artifact path")
    relative = PurePosixPath(name)
    if relative.is_absolute() or relative.as_posix() != name:
        raise ValueError("noncanonical snapshot artifact path")
    return relative


def _validated_artifact_tree(
    root: Path, items: object,
) -> tuple[tuple[str, str, int], ...]:
    if root.is_symlink() or not root.is_dir() or not isinstance(items, list):
        raise ValueError("missing snapshot artifact root or malformed manifest")
    # Never descend into a directory symlink, including during a concurrent
    # swap after the initial stat/manifest inspection.
    actual = _artifact_names_beneath(root)
    declared: set[str] = set()
    records: list[tuple[str, str, int]] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("invalid snapshot artifact entry")
        name = item.get("path")
        relative = _safe_artifact_name(name)
        size = item.get("size")
        digest = item.get("sha256")
        if name in declared:
            raise ValueError("duplicate snapshot artifact identity")
        if type(size) is not int or size < 0:
            raise ValueError("invalid snapshot artifact size")
        if not isinstance(digest, str) or len(digest) != 64 or any(
            char not in "0123456789abcdef" for char in digest
        ):
            raise ValueError("invalid snapshot artifact digest")
        declared.add(name)
        artifact = root.joinpath(*relative.parts)
        if artifact.is_symlink() or not artifact.is_file():
            raise ValueError(f"artifact missing or symlink: {name}")
        observed_digest, observed_size = _hash_artifact_beneath(root, relative)
        if observed_digest != digest or observed_size != size:
            raise ValueError(f"artifact integrity mismatch: {name}")
        records.append((name, digest, size))
    if actual != declared:
        raise ValueError(f"snapshot contains unmanifested or missing artifacts: {sorted(actual ^ declared)}")
    return tuple(records)


class PortableSnapshotManager:
    FORMAT_VERSION = 1

    def create(
        self, *, sqlite_path: str | Path, artifact_root: str | Path,
        destination: str | Path, schema_version: str,
    ) -> SnapshotManifest:
        sqlite_path, artifact_root, destination = (
            Path(sqlite_path), Path(artifact_root), Path(destination)
        )
        if sqlite_path.is_symlink() or artifact_root.is_symlink() or destination.is_symlink():
            raise ValueError("snapshot paths must not be symlinks")
        if not sqlite_path.is_file():
            raise FileNotFoundError(sqlite_path)
        if destination.exists() and any(destination.iterdir()):
            raise FileExistsError("snapshot destination must be empty")
        # Enumeration and file opens never follow intermediate symlinks on POSIX.
        sources = sorted(_artifact_names_beneath(artifact_root)) if artifact_root.exists() else []

        destination.mkdir(parents=True, exist_ok=True)
        db_out = destination / "authority.sqlite3"
        with sqlite3.connect(sqlite_path) as src, sqlite3.connect(db_out) as dst:
            src.backup(dst)
        root_out = destination / "artifacts"
        root_out.mkdir()
        records: list[tuple[str, str, int]] = []
        for portable_name in sources:
            relative = _safe_artifact_name(portable_name)
            target = root_out.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            _copy_artifact_beneath(artifact_root, relative, target)
            records.append((portable_name, _hash_file(target), target.stat().st_size))
        manifest = SnapshotManifest(
            self.FORMAT_VERSION, datetime.now(UTC).isoformat(),
            schema_version, _hash_file(db_out), tuple(records),
        )
        (destination / "manifest.json").write_text(json.dumps({
            "format_version": manifest.format_version,
            "created_at": manifest.created_at,
            "schema_version": manifest.schema_version,
            "database_sha256": manifest.database_sha256,
            "artifacts": [
                {"path": name, "sha256": digest, "size": size}
                for name, digest, size in manifest.artifacts
            ],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        # A snapshot is not ready until it passes its own restore-time checks.
        self.verify(destination)
        return manifest

    def verify(self, snapshot: str | Path) -> SnapshotManifest:
        snapshot = Path(snapshot)
        manifest_path = snapshot / "manifest.json"
        db_path = snapshot / "authority.sqlite3"
        if any(path.is_symlink() for path in (snapshot, manifest_path, db_path)):
            raise ValueError("snapshot paths must not be symlinks")
        with _open_regular_beneath(snapshot, PurePosixPath("manifest.json")) as stream:
            raw = json.load(stream)
        if not isinstance(raw, dict) or raw.get("format_version") != self.FORMAT_VERSION:
            raise ValueError("unsupported snapshot format")
        database_hash = raw.get("database_sha256")
        if not isinstance(database_hash, str) or len(database_hash) != 64 or any(
            char not in "0123456789abcdef" for char in database_hash
        ):
            raise ValueError("invalid snapshot database digest")
        verified_db_hash, _ = _hash_artifact_beneath(
            snapshot, PurePosixPath("authority.sqlite3")
        )
        if verified_db_hash != database_hash:
            raise ValueError("database snapshot hash mismatch")
        records = _validated_artifact_tree(snapshot / "artifacts", raw.get("artifacts"))
        return SnapshotManifest(
            raw["format_version"], raw["created_at"], raw["schema_version"],
            database_hash, records,
        )

    def restore(
        self, *, snapshot: str | Path, target_sqlite: str | Path,
        target_artifact_root: str | Path, overwrite: bool = False,
    ) -> SnapshotManifest:
        snapshot, db, artifacts = (
            Path(snapshot), Path(target_sqlite), Path(target_artifact_root)
        )
        manifest = self.verify(snapshot)
        if any(path.is_symlink() for path in (db, artifacts)):
            raise ValueError("restore targets must not be symlinks")
        snapshot_abs, db_abs, artifacts_abs = (
            snapshot.resolve(), db.resolve(), artifacts.resolve()
        )
        if (
            db_abs.is_relative_to(snapshot_abs)
            or artifacts_abs.is_relative_to(snapshot_abs)
            or snapshot_abs.is_relative_to(artifacts_abs)
            or db_abs.is_relative_to(artifacts_abs)
        ):
            raise ValueError("snapshot and target paths must be disjoint")
        if (db.exists() and not db.is_file()) or (artifacts.exists() and not artifacts.is_dir()):
            raise ValueError("restore destination type mismatch")
        if not overwrite and (db.exists() or artifacts.exists()):
            raise FileExistsError("restore targets already exist")
        db.parent.mkdir(parents=True, exist_ok=True)
        artifacts.parent.mkdir(parents=True, exist_ok=True)
        # Stage each resource on its destination filesystem, then re-verify copied
        # bytes. Roll back ordinary rename/copy failures; cross-device two-resource
        # atomicity and power-loss recovery still require an external transaction.
        with tempfile.TemporaryDirectory(dir=db.parent) as db_dir, tempfile.TemporaryDirectory(
            dir=artifacts.parent
        ) as artifacts_dir:
            db_stage_root, art_stage_root = Path(db_dir), Path(artifacts_dir)
            staged_db = db_stage_root / "new.db"
            staged_artifacts = art_stage_root / "new-artifacts"
            _copy_artifact_beneath(
                snapshot, PurePosixPath("authority.sqlite3"), staged_db
            )
            staged_artifacts.mkdir()
            for name, _, _ in manifest.artifacts:
                relative = _safe_artifact_name(name)
                staged_target = staged_artifacts.joinpath(*relative.parts)
                staged_target.parent.mkdir(parents=True, exist_ok=True)
                _copy_artifact_beneath(snapshot / "artifacts", relative, staged_target)
            if _hash_file(staged_db) != manifest.database_sha256:
                raise ValueError("staged database integrity mismatch")
            _validated_artifact_tree(staged_artifacts, [
                {"path": name, "sha256": digest, "size": size}
                for name, digest, size in manifest.artifacts
            ])
            old_db, old_artifacts = db_stage_root / "old.db", art_stage_root / "old-artifacts"
            backed_db = backed_artifacts = installed_db = installed_artifacts = False
            try:
                if overwrite and db.exists():
                    os.replace(db, old_db)
                    backed_db = True
                if overwrite and artifacts.exists():
                    os.replace(artifacts, old_artifacts)
                    backed_artifacts = True
                os.replace(staged_db, db)
                installed_db = True
                os.replace(staged_artifacts, artifacts)
                installed_artifacts = True
            except Exception:
                if installed_artifacts:
                    shutil.rmtree(artifacts)
                if installed_db:
                    db.unlink()
                if backed_db:
                    os.replace(old_db, db)
                if backed_artifacts:
                    os.replace(old_artifacts, artifacts)
                raise
        return manifest
