from fastapi import FastAPI

from app.api import auth, incidents, users
from app.api.ai import router as ai_router
from app.api.analytics import router as analytics_router
from app.core.config import settings
from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
)
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.middleware.logging import LoggingMiddleware

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Emergency Response Intelligence Platform",
    version=settings.APP_VERSION,
)

# Register Middleware
app.add_middleware(LoggingMiddleware)

# Register Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register Routers
app.include_router(
    auth.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    users.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    incidents.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    ai_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    analytics_router,
    prefix=settings.API_PREFIX,
)


@app.get("/")
def root():
    return {
        "message": "Welcome to ResQAI 🚑",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/version")
def version():
    return {
        "version": settings.APP_VERSION,
    }