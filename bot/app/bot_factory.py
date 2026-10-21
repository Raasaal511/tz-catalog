from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import get_settings
from app.handlers import build_root_router
from app.middlewares import AdminContextMiddleware


def create_bot() -> Bot:
    settings = get_settings()
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.update.middleware(AdminContextMiddleware())
    dp.include_router(build_root_router())
    return dp
