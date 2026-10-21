from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def ensure_scheme(url: str, default_scheme: str = "https") -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"{default_scheme}://{url}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str
    admin_telegram_ids: str = ""  # comma-separated Telegram user IDs

    api_base_url: str = "http://localhost:8000"
    internal_api_key: str = "change-me-internal-key"

    # Mini App / catalog URL (Next.js)
    webapp_url: str = "http://localhost:3000"

    # Webhook mode (production / multi-instance)
    bot_mode: str = "polling"  # polling | webhook
    webhook_host: str = "https://example.com"
    webhook_path: str = "/telegram/webhook"
    webhook_secret: str = "change-me-webhook-secret"
    bot_listen_host: str = "0.0.0.0"
    # Render injects PORT; fall back to BOT_LISTEN_PORT / 8080
    port: int | None = None
    bot_listen_port: int = 8080

    @property
    def listen_port(self) -> int:
        return self.port or self.bot_listen_port

    @field_validator("api_base_url", "webapp_url", "webhook_host", mode="before")
    @classmethod
    def _normalize_urls(cls, value: str) -> str:
        raw = str(value).rstrip("/")
        if "localhost" in raw or raw.startswith("http://"):
            return ensure_scheme(raw, "http") if not raw.startswith("http") else raw
        return ensure_scheme(raw)

    @property
    def admin_ids(self) -> set[int]:
        ids: set[int] = set()
        for part in self.admin_telegram_ids.split(","):
            part = part.strip()
            if part.isdigit():
                ids.add(int(part))
        return ids

    @property
    def webhook_url(self) -> str:
        return f"{self.webhook_host.rstrip('/')}{self.webhook_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
