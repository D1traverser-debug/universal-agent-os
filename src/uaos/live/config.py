from __future__ import annotations

from dataclasses import dataclass
import os


class LiveConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class LiveConfig:
    database_url: str | None
    dbos_system_database_url: str | None
    openai_api_key_present: bool
    object_store_url: str | None
    object_store_bucket: str | None
    object_store_region: str
    openai_model: str | None

    @classmethod
    def from_env(cls) -> "LiveConfig":
        return cls(
            database_url=os.getenv("UAOS_DATABASE_URL"),
            dbos_system_database_url=os.getenv("DBOS_SYSTEM_DATABASE_URL"),
            openai_api_key_present=bool(os.getenv("OPENAI_API_KEY")),
            object_store_url=os.getenv("UAOS_OBJECT_STORE_URL"),
            object_store_bucket=os.getenv("UAOS_OBJECT_STORE_BUCKET"),
            object_store_region=os.getenv("UAOS_OBJECT_STORE_REGION", "us-east-1"),
            openai_model=os.getenv("UAOS_OPENAI_PROBE_MODEL"),
        )

    def require_postgres(self) -> str:
        if not self.database_url:
            raise LiveConfigurationError("UAOS_DATABASE_URL is required for live PostgreSQL verification")
        return self.database_url

    def require_dbos(self) -> str:
        if not self.dbos_system_database_url:
            raise LiveConfigurationError("DBOS_SYSTEM_DATABASE_URL is required for live DBOS verification")
        return self.dbos_system_database_url

    def require_object_store(self) -> tuple[str, str, str]:
        if not self.object_store_url:
            raise LiveConfigurationError("UAOS_OBJECT_STORE_URL is required for live object-store verification")
        if not self.object_store_bucket:
            raise LiveConfigurationError("UAOS_OBJECT_STORE_BUCKET is required for live object-store verification")
        return self.object_store_url, self.object_store_bucket, self.object_store_region

    def require_openai(self) -> str:
        if not self.openai_api_key_present:
            raise LiveConfigurationError("OPENAI_API_KEY is required for live OpenAI executor verification")
        if not self.openai_model:
            raise LiveConfigurationError("UAOS_OPENAI_PROBE_MODEL is required; no model is guessed for live verification")
        return self.openai_model
