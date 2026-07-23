from pydantic import BaseModel


class AIAnalysisResponse(BaseModel):
    predicted_severity: str
    predicted_category: str
    summary: str
    recommended_response: list[str]