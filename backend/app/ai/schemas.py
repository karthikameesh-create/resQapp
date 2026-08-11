from pydantic import BaseModel, Field


class AIAnalysisResponse(BaseModel):
    predicted_severity: str
    predicted_category: str
    severity_confidence: float = Field(ge=0.0, le=1.0)
    category_confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    recommended_response: list[str]