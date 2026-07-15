from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Emergency Response Intelligence Platform",
    version=settings.APP_VERSION,
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
        "version": "0.1.0",
    }