from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import auth, incidents, users
from app.api.ai import router as ai_router
from app.api.analytics import router as analytics_router
from app.api.notifications import router as notifications_router
from app.core.config import settings
from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
)
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.core.rate_limiter import limiter
from app.middleware.logging import LoggingMiddleware

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Emergency Response Intelligence Platform",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:4173",
    "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach Limiter State & Register Middlewares
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(LoggingMiddleware)

# Register Exception Handlers
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
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
app.include_router(
    notifications_router,
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