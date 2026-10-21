from fastapi import Request

from app.core.config import Settings, get_settings


def get_request_base_url(request: Request) -> str:
    """
    Resolve a browser-reachable API base URL for media links.

    Priority:
      1. PUBLIC_BASE_URL (explicit, needed for SSR via internal Docker DNS)
      2. X-Forwarded-* headers (Render / reverse proxy)
      3. Request base URL
    """
    settings = get_settings()
    if settings.public_base_url:
        return settings.public_base_url.rstrip("/")

    forwarded_proto = request.headers.get("x-forwarded-proto")
    forwarded_host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if forwarded_proto and forwarded_host:
        return f"{forwarded_proto}://{forwarded_host}"
    return str(request.base_url).rstrip("/")


def settings_dep() -> Settings:
    return get_settings()
