from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AI Lead Generation System"
    environment: str = "development"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://lead_user:lead_pass@localhost:5432/lead_db"

    # Security
    admin_api_key: str = "change-me-before-production"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # OpenAI (Phase 2)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # n8n webhook (Phase 2)
    n8n_handoff_webhook_url: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str) -> str:
        return v

    def get_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    def get_test_database_url(self) -> str:
        return "sqlite+aiosqlite:///./test.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
