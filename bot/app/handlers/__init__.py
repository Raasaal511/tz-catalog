from aiogram import Router

from app.handlers.admin import router as admin_router
from app.handlers.common import router as common_router


def build_root_router() -> Router:
    root = Router()
    root.include_router(common_router)
    root.include_router(admin_router)
    return root
