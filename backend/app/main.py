from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Emergency Response Intelligence Platform",
    version=settings.APP_VERSION,
)

app.include_router(
    auth_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    users_router,
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