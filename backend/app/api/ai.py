from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.service import AIService

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class AIRequest(BaseModel):
    description: str


@router.post("/analyze")
def analyze_incident(request: AIRequest):
    return AIService.analyze(request.description)