from __future__ import annotations

from pathlib import Path
import pytest

from uaos.live.config import LiveConfig, LiveConfigurationError
from uaos.live.postgres import migration_files, apply_migrations


def test_live_config_fails_closed_without_postgres(monkeypatch):
    monkeypatch.delenv("UAOS_DATABASE_URL", raising=False)
    cfg = LiveConfig.from_env()
    with pytest.raises(LiveConfigurationError, match="UAOS_DATABASE_URL"):
        cfg.require_postgres()


def test_live_config_fails_closed_without_dbos(monkeypatch):
    monkeypatch.delenv("DBOS_SYSTEM_DATABASE_URL", raising=False)
    cfg = LiveConfig.from_env()
    with pytest.raises(LiveConfigurationError, match="DBOS_SYSTEM_DATABASE_URL"):
        cfg.require_dbos()


def test_migration_files_are_sorted(tmp_path: Path):
    (tmp_path / "0002_b.sql").write_text("select 2;", encoding="utf-8")
    (tmp_path / "0001_a.sql").write_text("select 1;", encoding="utf-8")
    assert [p.name for p in migration_files(tmp_path)] == ["0001_a.sql", "0002_b.sql"]


class Cursor:
    def __init__(self, calls): self.calls = calls
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def execute(self, sql, params=None): self.calls.append((sql, params))


class Connection:
    def __init__(self): self.calls=[]; self.commits=0
    def cursor(self): return Cursor(self.calls)
    def commit(self): self.commits += 1


def test_apply_migrations_executes_every_file_once(tmp_path: Path):
    a = tmp_path / "0001.sql"; b = tmp_path / "0002.sql"
    a.write_text("select 1;", encoding="utf-8"); b.write_text("select 2;", encoding="utf-8")
    conn = Connection()
    assert apply_migrations(conn, (a,b)) == ("0001.sql", "0002.sql")
    assert [call[0] for call in conn.calls] == ["select 1;", "select 2;"]
    assert conn.commits == 1


def test_live_openai_requires_key_and_explicit_model(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("UAOS_OPENAI_PROBE_MODEL", raising=False)
    with pytest.raises(LiveConfigurationError, match="OPENAI_API_KEY"):
        LiveConfig.from_env().require_openai()
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with pytest.raises(LiveConfigurationError, match="UAOS_OPENAI_PROBE_MODEL"):
        LiveConfig.from_env().require_openai()
    monkeypatch.setenv("UAOS_OPENAI_PROBE_MODEL", "explicit-model")
    assert LiveConfig.from_env().require_openai() == "explicit-model"
