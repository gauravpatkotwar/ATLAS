import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from atlas.config.settings import settings
from atlas.ai.base import AIProvider, EmbeddingProvider

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider, EmbeddingProvider):
    """Implementation of AI and Embedding Providers using Google Gemini REST endpoints."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _post_chat(self, prompt: str, history: List[Dict[str, str]]) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        # Convert history format to Gemini format (user -> user, assistant -> model)
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        payload = {"contents": contents}
        
        response = await self.client.post(url, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API error {response.status_code}: {response.text}")
        res_data = response.json()
        try:
            return res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Gemini response: {res_data}. Error: {e}")
            raise RuntimeError("Invalid Gemini API response structure.")

    async def _post_generate(self, prompt: str) -> str:
        return await self._post_chat(prompt, [])

    async def extract_candidate_data(self, resume_text: str) -> Dict[str, Any]:
        prompt = (
            "You are an expert resume parsing system.\n"
            "Analyze the following resume text and extract the candidate details in strict JSON format.\n"
            "The JSON must have the following keys:\n"
            "- name (string, required)\n"
            "- email (string, or null)\n"
            "- phone (string, or null)\n"
            "- location (string, or null)\n"
            "- skills (list of strings)\n"
            "- education (list of dicts, each with keys: institution, degree, year)\n"
            "- experience (list of dicts, each with keys: company, role, duration, description)\n"
            "- linkedin (string, or null)\n"
            "- github (string, or null)\n"
            "- portfolio (string, or null)\n"
            "- summary (string, or null)\n"
            "\n"
            f"Resume Text:\n{resume_text}"
        )
        try:
            res_text = await self._post_generate(prompt)
            clean_json = res_text.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.warning(
                f"Gemini failed to extract candidate data: {e}. Returning fallback skeleton."
            )
            return {
                "name": "Unknown",
                "email": None,
                "phone": None,
                "location": None,
                "skills": [],
                "education": [],
                "experience": [],
                "linkedin": None,
                "github": None,
                "portfolio": None,
                "summary": None,
            }

    async def generate_summary(self, resume_text: str) -> str:
        prompt = (
            "Summarize the following resume text in 2-3 professional sentences focusing on the candidate's core experience and skills.\n"
            f"Resume Text:\n{resume_text}"
        )
        try:
            return await self._post_generate(prompt)
        except Exception as e:
            logger.warning(f"Gemini summary generation failed: {e}")
            return "Resume text extraction completed. Summary unavailable."

    async def chat_copilot(self, query: str, history: List[Dict[str, str]]) -> str:
        system_instruction = (
            "You are ATLAS Recruiter Copilot, a helpful enterprise recruiting AI assistant. "
            "You help recruiters search candidates, compare them, and analyze roles. Be professional, direct, and detailed in your answers."
        )
        try:
            return await self._post_chat(f"{system_instruction}\n\nUser query: {query}", history)
        except Exception as e:
            logger.error(f"Gemini Copilot Chat failed: {e}")
            return "ATLAS Recruiter Copilot is currently offline. Please check your network connection."

    async def explain_recommendation(
        self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> str:
        prompt = (
            "Explain why the candidate fits or does not fit the job description.\n"
            f"Candidate profile: {json.dumps(candidate_data)}\n"
            f"Job requirement: {json.dumps(job_data)}\n"
            "Focus on experience, salary, skills overlap, and general suitability."
        )
        try:
            return await self._post_generate(prompt)
        except Exception as e:
            logger.warning(f"Gemini recommendation explanation failed: {e}")
            return "Unable to generate matching explanation at this time."

    async def generate_embedding(self, text: str) -> List[float]:
        if not self.api_key:
            return []

        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text}]
            }
        }
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            res_data = response.json()
            return res_data["embedding"]["values"]
        except Exception as e:
            logger.error(f"Gemini embedding generation failed: {e}")
            return []

    async def close(self) -> None:
        await self.client.aclose()
