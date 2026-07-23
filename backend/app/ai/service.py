from app.ai.providers import analyze_incident
from app.ai.schemas import AIAnalysisResponse


class AIService:

    @staticmethod
    def analyze(description: str) -> AIAnalysisResponse:
        result = analyze_incident(description)
        return AIAnalysisResponse(**result)