from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC,datetime
from hashlib import sha256
import json,os,shutil,sqlite3,tempfile
from pathlib import Path

@dataclass(frozen=True,slots=True)
class SnapshotManifest:
    format_version:int
    created_at:str
    schema_version:str
    database_sha256:str
    artifacts:tuple[tuple[str,str,int],...]

def _hash_file(path:Path)->str:
    h=sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

class PortableSnapshotManager:
    FORMAT_VERSION=1
    def create(self,*,sqlite_path:str|Path,artifact_root:str|Path,destination:str|Path,schema_version:str)->SnapshotManifest:
        sqlite_path=Path(sqlite_path); artifact_root=Path(artifact_root); destination=Path(destination)
        if not sqlite_path.exists(): raise FileNotFoundError(sqlite_path)
        if destination.exists() and any(destination.iterdir()): raise FileExistsError("snapshot destination must be empty")
        destination.mkdir(parents=True,exist_ok=True); db_out=destination/"authority.sqlite3"
        with sqlite3.connect(sqlite_path) as src, sqlite3.connect(db_out) as dst: src.backup(dst)
        artifacts_dir=destination/"artifacts"; artifacts_dir.mkdir(); records=[]
        if artifact_root.exists():
            for source in sorted(p for p in artifact_root.rglob("*") if p.is_file()):
                if source.is_symlink(): raise ValueError(f"symlink artifact not allowed: {source}")
                rel=source.relative_to(artifact_root); target=artifacts_dir/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
                records.append((rel.as_posix(),_hash_file(target),target.stat().st_size))
        manifest=SnapshotManifest(self.FORMAT_VERSION,datetime.now(UTC).isoformat(),schema_version,_hash_file(db_out),tuple(records))
        (destination/"manifest.json").write_text(json.dumps({"format_version":manifest.format_version,"created_at":manifest.created_at,"schema_version":manifest.schema_version,"database_sha256":manifest.database_sha256,"artifacts":[{"path":p,"sha256":h,"size":s} for p,h,s in manifest.artifacts]},ensure_ascii=False,indent=2),encoding="utf-8")
        return manifest
    def verify(self,snapshot:str|Path)->SnapshotManifest:
        snapshot=Path(snapshot); raw=json.loads((snapshot/"manifest.json").read_text(encoding="utf-8"))
        if raw["format_version"]!=self.FORMAT_VERSION: raise ValueError("unsupported snapshot format")
        db=snapshot/"authority.sqlite3"
        if _hash_file(db)!=raw["database_sha256"]: raise ValueError("database snapshot hash mismatch")
        records=[]
        for item in raw.get("artifacts",[]):
            p=snapshot/"artifacts"/item["path"]
            if not p.is_file(): raise ValueError(f"artifact missing: {item['path']}")
            if _hash_file(p)!=item["sha256"] or p.stat().st_size!=item["size"]: raise ValueError(f"artifact integrity mismatch: {item['path']}")
            records.append((item["path"],item["sha256"],item["size"]))
        return SnapshotManifest(raw["format_version"],raw["created_at"],raw["schema_version"],raw["database_sha256"],tuple(records))
    def restore(self,*,snapshot:str|Path,target_sqlite:str|Path,target_artifact_root:str|Path,overwrite:bool=False)->SnapshotManifest:
        snapshot=Path(snapshot); target_sqlite=Path(target_sqlite); target_artifact_root=Path(target_artifact_root); manifest=self.verify(snapshot)
        if not overwrite and (target_sqlite.exists() or target_artifact_root.exists()): raise FileExistsError("restore targets already exist")
        target_sqlite.parent.mkdir(parents=True,exist_ok=True); target_artifact_root.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=target_sqlite.parent) as tmp_name:
            tmp=Path(tmp_name); db_tmp=tmp/"authority.sqlite3"; shutil.copy2(snapshot/"authority.sqlite3",db_tmp); artifacts_tmp=tmp/"artifacts"; shutil.copytree(snapshot/"artifacts",artifacts_tmp)
            if overwrite:
                if target_sqlite.exists(): target_sqlite.unlink()
                if target_artifact_root.exists(): shutil.rmtree(target_artifact_root)
            os.replace(db_tmp,target_sqlite); shutil.move(str(artifacts_tmp),str(target_artifact_root))
        return manifest
