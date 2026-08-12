import json

from google import genai

from app.core.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def analyze_incident(description: str) -> dict:
    prompt = f"""
You are an AI emergency response assistant.

Analyze the following emergency incident.

Return ONLY a valid JSON object.

Required JSON format:

{{
    "predicted_severity": "",
    "predicted_category": "",
    "severity_confidence": 0.0,
    "category_confidence": 0.0,
    "summary": "",
    "recommended_response": []
}}

Rules:
- predicted_severity must be one of: Low, Medium, High, Critical.
- predicted_category should describe the incident category.
- severity_confidence must be a number between 0.0 and 1.0.
- category_confidence must be a number between 0.0 and 1.0.
- summary must briefly explain the incident.
- recommended_response must be a JSON array of emergency response actions.
- Do not use Markdown.
- Do not use code fences.
- Do not include any text outside the JSON object.

Incident:
{description}
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )

    text = response.text.strip()

    return json.loads(text)