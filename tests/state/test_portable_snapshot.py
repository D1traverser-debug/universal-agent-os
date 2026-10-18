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
