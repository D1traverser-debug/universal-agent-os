"""Portable, integrity-checked snapshots of the existing SQLite/artifact owner.

This module is a storage adapter, not a second task/evolution authority.
Its restore API remains an explicitly called filesystem operation, not proof
that native chat or arbitrary external writes pass through ActionCoordinator.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import tempfile


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
    # Scan the *whole* tree for links before following any manifest-selected
    # path: a symlinked intermediate directory must not be read during hashing.
    actual: set[str] = set()
    for artifact in root.rglob("*"):
        if artifact.is_symlink():
            raise ValueError(f"snapshot contains a symlink: {artifact}")
        if artifact.is_file():
            actual.add(artifact.relative_to(root).as_posix())
        elif not artifact.is_dir():
            raise ValueError(f"unexpected snapshot artifact type: {artifact}")
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
        if _hash_file(artifact) != digest or artifact.stat().st_size != size:
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
        # Examine all file types, including symlinked directories, before copying.
        sources = tuple(sorted(artifact_root.rglob("*"))) if artifact_root.exists() else ()
        for source in sources:
            if source.is_symlink() or not (source.is_file() or source.is_dir()):
                raise ValueError(f"unsupported or symlinked artifact: {source}")

        destination.mkdir(parents=True, exist_ok=True)
        db_out = destination / "authority.sqlite3"
        with sqlite3.connect(sqlite_path) as src, sqlite3.connect(db_out) as dst:
            src.backup(dst)
        root_out = destination / "artifacts"
        root_out.mkdir()
        records: list[tuple[str, str, int]] = []
        for source in sources:
            if source.is_dir():
                continue
            relative = source.relative_to(artifact_root)
            portable_name = relative.as_posix()
            _safe_artifact_name(portable_name)
            target = root_out / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
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
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or raw.get("format_version") != self.FORMAT_VERSION:
            raise ValueError("unsupported snapshot format")
        database_hash = raw.get("database_sha256")
        if not isinstance(database_hash, str) or len(database_hash) != 64 or any(
            char not in "0123456789abcdef" for char in database_hash
        ):
            raise ValueError("invalid snapshot database digest")
        if _hash_file(db_path) != database_hash:
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
            shutil.copy2(snapshot / "authority.sqlite3", staged_db)
            shutil.copytree(snapshot / "artifacts", staged_artifacts, symlinks=True)
            if _hash_file(staged_db) != manifest.database_sha256:
                raise ValueError("staged database integrity mismatch")
            raw = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
            _validated_artifact_tree(staged_artifacts, raw["artifacts"])
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
