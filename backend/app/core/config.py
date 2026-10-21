from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def to_asyncpg_url(url: str) -> str:
    """Normalize Render/Heroku-style postgres URLs for SQLAlchemy async."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # asyncpg expects `ssl=true`, libpq-style sslmode breaks the DSN parser
    url = url.replace("sslmode=require", "ssl=require")
    url = url.replace("sslmode=prefer", "ssl=prefer")
    url = url.replace("sslmode=disable", "ssl=disable")
    return url


def ensure_scheme(url: str, default_scheme: str = "https") -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"{default_scheme}://{url}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "tz-catalog-api"
    environment: str = "development"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://catalog:catalog@localhost:5432/catalog"

    # Internal auth for bot / trusted clients
    internal_api_key: str = "change-me-internal-key"

    # CORS / frontend
    cors_origins: str = "http://localhost:3000"

    # Public API base URL used in media links (required behind internal Docker DNS)
    # Example: https://api.example.com or http://localhost:8000
    public_base_url: str | None = None

    # MinIO / S3
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "products"
    s3_region: str = "us-east-1"
    s3_public_endpoint_url: str | None = None  # e.g. https://minio.example.com

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_db(cls, value: str) -> str:
        return to_asyncpg_url(str(value))

    @field_validator("public_base_url", mode="before")
    @classmethod
    def _normalize_public(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        return ensure_scheme(str(value)).rstrip("/")

    @field_validator("s3_endpoint_url", mode="before")
    @classmethod
    def _normalize_s3(cls, value: str) -> str:
        # Local MinIO uses http; Render hostnames get https
        raw = str(value)
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw
        if raw.startswith("minio") or "localhost" in raw or "127.0.0.1" in raw:
            return f"http://{raw}"
        return ensure_scheme(raw)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
