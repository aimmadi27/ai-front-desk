import sentry_sdk
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core import cache
from app.api.routes import voice, sms, businesses, webhooks, sessions, stats, scheduler, chat

configure_logging(settings.app_env)
logger = get_logger(__name__)

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        traces_sample_rate=0.2,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting", env=settings.app_env)
    yield
    await cache.close()
    logger.info("app_stopped")


app = FastAPI(
    title="AI Front Desk",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else [settings.base_url],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(sms.router)
app.include_router(businesses.router)
app.include_router(webhooks.router)
app.include_router(sessions.router)
app.include_router(stats.router)
app.include_router(scheduler.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}
