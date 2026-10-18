import sqlite3
import pytest
from uaos.state import PortableSnapshotManager

def test_portable_snapshot_roundtrip_and_integrity(tmp_path):
    database=tmp_path/"source.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE example(value TEXT)"); connection.execute("INSERT INTO example VALUES ('hello')"); connection.commit()
    artifacts=tmp_path/"artifacts"; artifacts.mkdir(); (artifacts/"a.txt").write_text("alpha",encoding="utf-8")
    snapshot=tmp_path/"snapshot"; manager=PortableSnapshotManager(); manager.create(sqlite_path=database,artifact_root=artifacts,destination=snapshot,schema_version="1"); manager.verify(snapshot)
    restored_db=tmp_path/"restored.db"; restored_artifacts=tmp_path/"restored-artifacts"; manager.restore(snapshot=snapshot,target_sqlite=restored_db,target_artifact_root=restored_artifacts)
    with sqlite3.connect(restored_db) as connection: assert connection.execute("SELECT value FROM example").fetchone()[0]=="hello"
    assert (restored_artifacts/"a.txt").read_text(encoding="utf-8")=="alpha"
    (snapshot/"artifacts"/"a.txt").write_text("tampered",encoding="utf-8")
    with pytest.raises(ValueError,match="integrity"): manager.verify(snapshot)


def _snapshot_fixture(tmp_path):
    database = tmp_path / "source.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE example(value TEXT)")
        connection.execute("INSERT INTO example VALUES ('new')")
        connection.commit()
    artifacts = tmp_path / "source-artifacts"
    artifacts.mkdir()
    (artifacts / "item.txt").write_text("new-file", encoding="utf-8")
    location = tmp_path / "snapshot"
    manager = PortableSnapshotManager()
    manager.create(
        sqlite_path=database, artifact_root=artifacts,
        destination=location, schema_version="1",
    )
    return manager, location, artifacts


def test_snapshot_rejects_unmanifested_file_and_symlink(tmp_path):
    manager, location, _ = _snapshot_fixture(tmp_path)
    extra = location / "artifacts" / "unlisted.txt"
    extra.write_text("injected", encoding="utf-8")
    with pytest.raises(ValueError, match="unmanifested"):
        manager.verify(location)
    extra.unlink()
    linked = location / "artifacts" / "bad-link"
    linked.symlink_to(tmp_path / "outside")
    with pytest.raises(ValueError, match="symlink"):
        manager.verify(location)


def test_snapshot_rejects_manifest_traversal_and_duplicate_entries(tmp_path):
    import json
    manager, location, _ = _snapshot_fixture(tmp_path)
    path = location / "manifest.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    for name in ("../outside.txt", "/tmp/escape", "x//y.txt", "x/./y.txt", "x/../y.txt"):
        compromised = json.loads(json.dumps(original))
        compromised["artifacts"][0]["path"] = name
        path.write_text(json.dumps(compromised), encoding="utf-8")
        with pytest.raises(ValueError, match="path"):
            manager.verify(location)
    duplicate = json.loads(json.dumps(original))
    duplicate["artifacts"].append(dict(original["artifacts"][0]))
    path.write_text(json.dumps(duplicate), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        manager.verify(location)


def test_restore_overwrite_rolls_back_database_and_artifacts_if_rename_fails(tmp_path, monkeypatch):
    import importlib
    snapshot_module = importlib.import_module("uaos.state.snapshot")
    manager, location, _ = _snapshot_fixture(tmp_path)
    db = tmp_path / "destination.db"
    with sqlite3.connect(db) as connection:
        connection.execute("CREATE TABLE example(value TEXT)")
        connection.execute("INSERT INTO example VALUES ('old')")
        connection.commit()
    artifacts = tmp_path / "destination-artifacts"
    artifacts.mkdir()
    (artifacts / "item.txt").write_text("old-file", encoding="utf-8")
    original_replace = snapshot_module.os.replace

    def fail_install_artifacts(source, destination):
        if destination == artifacts and source.name == "new-artifacts":
            raise OSError("simulated second-resource commit failure")
        return original_replace(source, destination)

    monkeypatch.setattr(snapshot_module.os, "replace", fail_install_artifacts)
    with pytest.raises(OSError, match="second-resource"):
        manager.restore(
            snapshot=location, target_sqlite=db,
            target_artifact_root=artifacts, overwrite=True,
        )
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT value FROM example").fetchone()[0] == "old"
    assert (artifacts / "item.txt").read_text(encoding="utf-8") == "old-file"


def test_snapshot_creation_rejects_symlinked_artifacts(tmp_path):
    manager, location, artifacts = _snapshot_fixture(tmp_path)
    (artifacts / "link.txt").symlink_to(artifacts / "item.txt")
    with pytest.raises(ValueError, match="symlink"):
        manager.create(
            sqlite_path=tmp_path / "source.db", artifact_root=artifacts,
            destination=tmp_path / "unsafe-snapshot", schema_version="1",
        )


def test_restore_rejects_snapshot_and_target_overlap(tmp_path):
    manager, location, _ = _snapshot_fixture(tmp_path)
    with pytest.raises(ValueError, match="disjoint"):
        manager.restore(
            snapshot=location,
            target_sqlite=location / "authority.sqlite3",
            target_artifact_root=tmp_path / "safe-root",
            overwrite=True,
        )


def test_existing_version_one_posix_colon_artifact_is_still_restorable(tmp_path):
    import os
    if os.name == "nt":
        pytest.skip("colon is a Windows drive separator")
    manager, location, artifacts = _snapshot_fixture(tmp_path)
    source = artifacts / "legal:name.txt"
    source.write_text("previously valid v1 POSIX filename", encoding="utf-8")
    backup = tmp_path / "old-version-one-snapshot"
    manager.create(
        sqlite_path=tmp_path / "source.db", artifact_root=artifacts,
        destination=backup, schema_version="1",
    )
    assert any(name == "legal:name.txt" for name, _, _ in manager.verify(backup).artifacts)
    restored_db = tmp_path / "target.db"
    restored_artifacts = tmp_path / "target-artifacts"
    manager.restore(snapshot=backup, target_sqlite=restored_db,
                    target_artifact_root=restored_artifacts)
    assert (restored_artifacts / "legal:name.txt").read_text(encoding="utf-8") == "previously valid v1 POSIX filename"


def test_windows_drive_path_is_not_admitted_on_windows(tmp_path):
    import os, json
    if os.name != "nt":
        pytest.skip("POSIX permits colon path components for v1 compatibility")
    manager, location, _ = _snapshot_fixture(tmp_path)
    manifest = location / "manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["artifacts"][0]["path"] = "C:/escape.txt"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="Windows snapshot artifact path"):
        manager.verify(location)


def test_snapshot_parent_symlink_is_rejected_before_any_external_artifact_read(tmp_path, monkeypatch):
    import importlib
    snapshot_module = importlib.import_module("uaos.state.snapshot")
    manager, _, artifact_source = _snapshot_fixture(tmp_path)
    nested = artifact_source / "nested"
    nested.mkdir()
    (nested / "valid.txt").write_text("reference", encoding="utf-8")
    location = tmp_path / "nested-snapshot"
    manager.create(
        sqlite_path=tmp_path / "source.db", artifact_root=artifact_source,
        destination=location, schema_version="1",
    )
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "valid.txt").write_text("reference", encoding="utf-8")
    (location / "artifacts" / "nested" / "valid.txt").unlink()
    (location / "artifacts" / "nested").rmdir()
    (location / "artifacts" / "nested").symlink_to(outside, target_is_directory=True)

    original_hash = snapshot_module._hash_file

    def guarded_hash(path):
        assert path.resolve().is_relative_to(location.resolve()), "must not open symlinked outside file"
        return original_hash(path)

    monkeypatch.setattr(snapshot_module, "_hash_file", guarded_hash)
    with pytest.raises(ValueError, match="symlink"):
        manager.verify(location)


@pytest.mark.skipif(__import__("os").name != "posix", reason="dirfd no-follow protection is POSIX-specific")
def test_snapshot_verify_rejects_check_to_use_symlink_swap(tmp_path, monkeypatch):
    """A directory substituted after is_file() must not redirect the hash read."""
    import importlib
    from pathlib import Path

    module = importlib.import_module("uaos.state.snapshot")
    manager, _, source = _snapshot_fixture(tmp_path)
    nested_source = source / "nested"
    nested_source.mkdir()
    (nested_source / "payload.txt").write_text("same-bytes", encoding="utf-8")
    location = tmp_path / "second-snapshot"
    manager.create(
        sqlite_path=tmp_path / "source.db", artifact_root=source,
        destination=location, schema_version="1",
    )

    snapshot_nested = location / "artifacts" / "nested"
    victim = snapshot_nested / "payload.txt"
    outside = tmp_path / "external"
    outside.mkdir()
    (outside / "payload.txt").write_text("same-bytes", encoding="utf-8")
    original_is_file = Path.is_file
    swapped = False

    def swap_between_check_and_open(path):
        nonlocal swapped
        is_file = original_is_file(path)
        if path == victim and is_file and not swapped:
            swapped = True
            snapshot_nested.rename(tmp_path / "detached-original")
            snapshot_nested.symlink_to(outside, target_is_directory=True)
        return is_file

    monkeypatch.setattr(Path, "is_file", swap_between_check_and_open)
    with pytest.raises(ValueError, match="unsafe|replaced|symlink"):
        manager.verify(location)
    assert swapped, "exercise the actual stat-to-open race window"
    assert (outside / "payload.txt").read_text(encoding="utf-8") == "same-bytes"


@pytest.mark.skipif(__import__("os").name != "posix", reason="dirfd no-follow protection is POSIX-specific")
def test_snapshot_restore_rejects_symlink_swap_during_staging(tmp_path, monkeypatch):
    """Do not copy outside data if an artifact directory moves after verify."""
    import importlib

    module = importlib.import_module("uaos.state.snapshot")
    manager, _, source = _snapshot_fixture(tmp_path)
    (source / "nested").mkdir()
    (source / "nested" / "payload.txt").write_text("same-bytes", encoding="utf-8")
    location = tmp_path / "restore-snapshot"
    manager.create(
        sqlite_path=tmp_path / "source.db", artifact_root=source,
        destination=location, schema_version="1",
    )
    outside = tmp_path / "external"
    outside.mkdir()
    (outside / "payload.txt").write_text("same-bytes", encoding="utf-8")
    source_nested = location / "artifacts" / "nested"
    original_copy = module._copy_artifact_beneath
    swapped = False

    def swap_before_stage_read(root, relative, destination):
        nonlocal swapped
        if root == location / "artifacts" and relative.as_posix() == "nested/payload.txt":
            swapped = True
            source_nested.rename(tmp_path / "detached-original")
            source_nested.symlink_to(outside, target_is_directory=True)
        return original_copy(root, relative, destination)

    monkeypatch.setattr(module, "_copy_artifact_beneath", swap_before_stage_read)
    db_target = tmp_path / "restored.db"
    artifacts_target = tmp_path / "restored-artifacts"
    with pytest.raises(ValueError, match="unsafe|replaced|symlink"):
        manager.restore(
            snapshot=location, target_sqlite=db_target,
            target_artifact_root=artifacts_target,
        )
    assert swapped
    assert not db_target.exists()
    assert not artifacts_target.exists()


@pytest.mark.skipif(__import__("os").name != "posix", reason="POSIX ancestor dirfd hardening")
def test_restore_rejects_snapshot_root_swap_after_database_stage(tmp_path, monkeypatch):
    """Replacing the snapshot *root* with a symlink must not redirect artifact reads."""
    import importlib
    import shutil

    module = importlib.import_module("uaos.state.snapshot")
    manager, location, _ = _snapshot_fixture(tmp_path)
    outside = tmp_path / "outside-snapshot"
    shutil.copytree(location, outside)
    original_copy = module._copy_artifact_beneath
    swapped = False

    def root_swap_before_artifact_read(root, relative, destination):
        nonlocal swapped
        if root == location / "artifacts" and relative.as_posix() == "item.txt":
            swapped = True
            location.rename(tmp_path / "detached-original-snapshot")
            location.symlink_to(outside, target_is_directory=True)
        return original_copy(root, relative, destination)

    monkeypatch.setattr(module, "_copy_artifact_beneath", root_swap_before_artifact_read)
    target_db = tmp_path / "target.db"
    target_artifacts = tmp_path / "target-artifacts"
    with pytest.raises(ValueError, match="unsafe|replaced|symlink"):
        manager.restore(
            snapshot=location,
            target_sqlite=target_db,
            target_artifact_root=target_artifacts,
        )
    assert swapped
    assert not target_db.exists()
    assert not target_artifacts.exists()


@pytest.mark.skipif(__import__("os").name != "posix", reason="POSIX ancestor dirfd hardening")
def test_snapshot_verify_rejects_symlinked_ancestor_of_snapshot_root(tmp_path):
    """A parent component must be opened with no-follow, not a compound path."""
    manager, location, _ = _snapshot_fixture(tmp_path)
    alias_parent = tmp_path / "alias-parent"
    alias_parent.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="unsafe|replaced|symlink"):
        manager.verify(alias_parent / location.name)
