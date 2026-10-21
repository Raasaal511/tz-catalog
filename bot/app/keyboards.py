from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.config import get_settings


def _is_https(url: str) -> bool:
    return url.startswith("https://")


def catalog_open_row() -> list[InlineKeyboardButton]:
    """
    Telegram Mini App (web_app) accepts HTTPS only.
    For local http://localhost we skip the WebApp button — URL goes in the message text.
    """
    settings = get_settings()
    if _is_https(settings.webapp_url):
        return [
            InlineKeyboardButton(
                text="Открыть каталог",
                web_app=WebAppInfo(url=settings.webapp_url),
            )
        ]
    return []


def catalog_keyboard() -> InlineKeyboardMarkup | None:
    row = catalog_open_row()
    if not row:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[row])


def admin_help_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    open_row = catalog_open_row()
    if open_row:
        rows.append(open_row)
    rows.append(
        [
            InlineKeyboardButton(
                text="Как создать товар",
                callback_data="admin:create_help",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def catalog_hint_text() -> str:
    settings = get_settings()
    if _is_https(settings.webapp_url):
        return ""
    return f"\n\nКаталог (браузер): {settings.webapp_url}"
