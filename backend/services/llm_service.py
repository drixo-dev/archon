import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


class LLMService:

    def __init__(self):
        env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(env_path, override=False)

        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set"
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def generate_answer(
        self,
        prompt: str
    ) -> str:

        try:
            response = (
                self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
            )

        except Exception as error:
            raise RuntimeError(
                f"Gemini request failed: {error}"
            ) from error

        answer = getattr(
            response,
            "text",
            None
        )

        if not answer or not answer.strip():
            raise RuntimeError(
                f"{self.model} returned an empty or malformed response."
            )

        return answer



    def extract_json(self, text: str) -> dict | list:
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
            
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        return json.loads(clean_text.strip())


llm_service = LLMService()
