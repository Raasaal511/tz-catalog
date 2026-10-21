"""
Bot entrypoint.

Modes:
  - polling: convenient for local development (single instance)
  - webhook: production / multi-instance (stateless HTTP handlers)
"""

from __future__ import annotations

import asyncio
import logging

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.bot_factory import create_bot, create_dispatcher
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_polling() -> None:
    bot = create_bot()
    dp = create_dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started in polling mode")
    await dp.start_polling(bot)


async def on_startup(bot) -> None:
    settings = get_settings()
    await bot.set_webhook(
        url=settings.webhook_url,
        secret_token=settings.webhook_secret,
        drop_pending_updates=True,
    )
    logger.info("Webhook set to %s", settings.webhook_url)


async def on_shutdown(bot) -> None:
    await bot.session.close()


def run_webhook() -> None:
    settings = get_settings()
    bot = create_bot()
    dp = create_dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()

    async def health(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    app.router.add_get("/health", health)

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret,
    )
    webhook_handler.register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    logger.info(
        "Bot webhook server on %s:%s path=%s",
        settings.bot_listen_host,
        settings.listen_port,
        settings.webhook_path,
    )
    web.run_app(app, host=settings.bot_listen_host, port=settings.listen_port)


def main() -> None:
    settings = get_settings()
    if settings.bot_mode.lower() == "webhook":
        run_webhook()
    else:
        asyncio.run(run_polling())


if __name__ == "__main__":
    main()
