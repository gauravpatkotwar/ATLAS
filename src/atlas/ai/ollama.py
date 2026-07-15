import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from atlas.config.settings import settings
from atlas.ai.base import AIProvider, EmbeddingProvider

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider, EmbeddingProvider):
    """Implementation of AI and Embedding Providers using Ollama HTTP endpoints."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        # Singleton client is configured; timeout accommodates larger model processing times
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)

    async def _post(self, path: str, json_data: dict) -> dict:
        try:
            response = await self.client.post(path, json=json_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ollama API request failed on {path}: {e}")
            raise RuntimeError(f"Ollama provider connection error: {e}")

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
        payload = {
            "model": settings.MODEL_RESUME_EXTRACTION,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        try:
            res = await self._post("/api/generate", payload)
            response_text = res.get("response", "{}")
            return json.loads(response_text)
        except Exception as e:
            logger.warning(
                f"Ollama failed to extract candidate data: {e}. Returning fallback skeleton."
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
        payload = {
            "model": settings.MODEL_RESUME_SUMMARY,
            "prompt": prompt,
            "stream": False,
        }
        try:
            res = await self._post("/api/generate", payload)
            return res.get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama summary generation failed: {e}")
            return "Resume text extraction completed. Summary unavailable."

    async def chat_copilot(self, query: str, history: List[Dict[str, str]]) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are ATLAS Recruiter Copilot, a helpful enterprise recruiting AI assistant. You help recruiters search candidates, compare them, and analyze roles. Be professional, direct, and detailed in your answers.",
            }
        ]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        payload = {
            "model": settings.MODEL_RECRUITER_CHAT,
            "messages": messages,
            "stream": False,
        }
        try:
            res = await self._post("/api/chat", payload)
            return res.get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.error(f"Ollama Copilot Chat failed: {e}")
            return "ATLAS Recruiter Copilot is currently offline. Please check your Ollama service."

    async def explain_recommendation(
        self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> str:
        prompt = (
            "Explain why the candidate fits or does not fit the job description.\n"
            f"Candidate profile: {json.dumps(candidate_data)}\n"
            f"Job requirement: {json.dumps(job_data)}\n"
            "Focus on experience, salary, skills overlap, and general suitability."
        )
        payload = {
            "model": settings.MODEL_RECOMMENDATION_EXPLANATION,
            "prompt": prompt,
            "stream": False,
        }
        try:
            res = await self._post("/api/generate", payload)
            return res.get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama recommendation explanation failed: {e}")
            return "Unable to generate matching explanation at this time."

    async def generate_embedding(self, text: str) -> List[float]:
        # standard Ollama embeddings format
        payload = {"model": settings.MODEL_EMBEDDINGS, "prompt": text}
        try:
            res = await self._post("/api/embeddings", payload)
            return res.get("embedding", [])
        except Exception as e:
            # Fallback to newer /api/embed API
            logger.info(
                f"Retrying embedding via alternate /api/embed endpoint due to: {e}"
            )
            payload_embed = {"model": settings.MODEL_EMBEDDINGS, "input": text}
            try:
                res = await self._post("/api/embed", payload_embed)
                embeddings = res.get("embeddings", [])
                if embeddings:
                    return embeddings[0]
            except Exception as e2:
                logger.error(f"All Ollama embedding attempts failed: {e2}")
            return []

    async def close(self) -> None:
        """Close connection pools."""
        await self.client.aclose()
