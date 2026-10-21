import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.services.s3 import s3_storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    logger.info("Starting %s (%s)", settings.app_name, settings.environment)

    # Create tables on startup — safe for multi-instance (IF NOT EXISTS).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        await s3_storage.ensure_bucket()
        logger.info("S3 bucket ready: %s", settings.s3_bucket)
    except Exception:
        logger.exception("Failed to ensure S3 bucket — uploads may fail until MinIO is up")

    yield
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
