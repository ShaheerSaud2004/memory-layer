from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[4]
_API_ENV = _REPO_ROOT / "apps" / "api" / ".env"
_ROOT_ENV = _REPO_ROOT / ".env"
_env_file_list: list[str | Path] = []
if _ROOT_ENV.is_file():
    _env_file_list.append(_ROOT_ENV)
if _API_ENV.is_file():
    _env_file_list.append(_API_ENV)
if not _env_file_list:
    _env_file_list.append(".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file_list, env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://memory:memory@localhost:5432/memory"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    api_public_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"
    cors_allow_localhost_any_port: bool = True
    cors_include_vercel_app_host: bool = False
    master_key: str = "dev-master-key-must-be-32-chars!!"

    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None

    rate_limit_per_minute: int = 120

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_pro: str | None = None
    billing_success_url: str = "http://localhost:3000/billing?success=1"
    billing_cancel_url: str = "http://localhost:3000/billing?canceled=1"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
