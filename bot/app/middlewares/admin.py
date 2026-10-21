from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from app.config import get_settings


class AdminContextMiddleware(BaseMiddleware):
    """Injects is_admin into handler data. No mutable shared state."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        admin_ids = get_settings().admin_ids
        data["is_admin"] = bool(user and user.id in admin_ids)
        return await handler(event, data)
