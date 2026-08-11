from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.ai.service import AIService
from app.core.rate_limiter import limiter

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class AIRequest(BaseModel):
    description: str


@router.post(
    "/analyze",
    responses={
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("20/minute")
def analyze_incident(
    request: Request,
    ai_request: AIRequest,
):
    return AIService.analyze(ai_request.description)