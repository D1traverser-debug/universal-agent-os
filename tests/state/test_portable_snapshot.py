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
