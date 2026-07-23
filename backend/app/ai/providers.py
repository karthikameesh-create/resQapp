import json

from google import genai

from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def analyze_incident(description: str) -> dict:
    prompt = f"""
You are an AI emergency response assistant.

Analyze the following emergency incident.

Return ONLY valid JSON.

Required JSON format:

{{
    "predicted_severity": "",
    "predicted_category": "",
    "summary": "",
    "recommended_response": []
}}

Incident:
{description}
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    text = response.text.strip()

    # Remove markdown code fences if Gemini returns them
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    return json.loads(text)