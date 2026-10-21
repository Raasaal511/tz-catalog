from fastapi import APIRouter

from app.api.routes_media import router as media_router
from app.api.routes_products import router as products_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(products_router)
api_router.include_router(media_router)
