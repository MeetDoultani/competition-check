from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.schemas.reports import ReportSchema

client = genai.Client(api_key=settings.GEMINI_API_KEY)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_report(matrix_json: str) -> ReportSchema:
    prompt = (
        "You are an expert competitive intelligence analyst. "
        "Analyze the following JSON comparison matrix. "
        "You must generate a structured report based strictly on the provided data. "
        "Do not invent or assume any information. "
        "Ensure all claims are backed by the evidence present in the JSON. "
        f"Data:\n{matrix_json}"
    )
    
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ReportSchema,
            temperature=0.1
        )
    )
    
    return ReportSchema.model_validate_json(response.text)
