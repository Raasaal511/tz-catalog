from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.config import get_settings


def catalog_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть каталог",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ]
        ]
    )


def admin_help_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть каталог",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Как создать товар",
                    callback_data="admin:create_help",
                )
            ],
        ]
    )
