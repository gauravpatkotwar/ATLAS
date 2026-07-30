import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from atlas.config.settings import settings
from atlas.ai.base import AIProvider, EmbeddingProvider

logger = logging.getLogger(__name__)

ATLAS_SYSTEM_PROMPT = """You are Nova — ATLAS's AI career companion. You are warm, smart, encouraging, and genuinely care about helping people grow.

Your personality:
- You speak like a real person — naturally, conversationally, never robotic
- You use contractions ("you're", "I'd", "let's", "that's") always
- You occasionally say things like "Honestly,", "Here's the thing —", "I love that question", "Great point!", "Okay so..."
- You celebrate wins: "That's amazing!", "Honestly, that's a solid background"
- You're empathetic when someone struggles: "I get it — job searching is tough. Let's figure this out together."
- You're specific — never vague. Give real advice, real numbers, real skill names.
- You keep responses focused and conversational (2-4 paragraphs max unless asked for more)
- You never say "I'm an AI" or "As a language model" — you're Nova, a career coach

Your expertise:
- Resume writing and optimization for ATS systems
- Identifying skill gaps and recommending learning paths
- Salary negotiation and market intelligence
- Interview coaching and behavioral question prep
- Career path planning and job search strategy
- Matching candidates to the right opportunities

Always end with either a question to continue the conversation, or a clear next step the user can take right now."""


class OllamaProvider(AIProvider, EmbeddingProvider):
    """Implementation of AI and Embedding Providers using Ollama HTTP endpoints."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        # Generous timeout for larger phi4-mini model first-token latency
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    async def _post(self, path: str, json_data: dict) -> dict:
        try:
            response = await self.client.post(path, json=json_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ollama API request failed on {path}: {e}")
            raise RuntimeError(f"Ollama provider connection error: {e}")

    # ── Generic single-turn generation ───────────────────────────────────────

    async def generate(self, prompt: str) -> str:
        """Generic single-turn text generation using the chat model."""
        payload = {
            "model": settings.MODEL_RECRUITER_CHAT,
            "messages": [
                {"role": "system", "content": ATLAS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        try:
            res = await self._post("/api/chat", payload)
            return res.get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.error(f"Ollama generate failed: {e}")
            return "Nova AI is warming up — please try again in a moment."

    # ── Resume parsing ────────────────────────────────────────────────────────

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
            f"Resume Text:\n{resume_text}\n\n"
            "Return ONLY valid JSON, no explanation."
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
            "Summarize the following resume in 2-3 professional sentences, "
            "highlighting the candidate's core expertise, key achievements, and years of experience. "
            "Be specific and compelling — this will be shown to recruiters.\n\n"
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

    # ── Copilot chat ──────────────────────────────────────────────────────────

    async def chat_copilot(self, query: str, history: List[Dict[str, str]]) -> str:
        messages = [{"role": "system", "content": ATLAS_SYSTEM_PROMPT}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        payload = {
            "model": settings.MODEL_RECRUITER_CHAT,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            },
        }
        try:
            res = await self._post("/api/chat", payload)
            return res.get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.error(f"Ollama Copilot Chat failed: {e}")
            return "Nova is currently offline. Please check your Ollama service is running."

    # ── Recommendation explanation ────────────────────────────────────────────

    async def explain_recommendation(
        self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> str:
        prompt = (
            "As an expert recruiter, explain in 3-4 clear paragraphs why this candidate "
            "is a good or poor fit for the job. Cover: skills match, experience relevance, "
            "salary alignment, and overall suitability. Be specific and cite actual details.\n\n"
            f"Candidate profile: {json.dumps(candidate_data)}\n"
            f"Job requirement: {json.dumps(job_data)}"
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

    # ── Embeddings ────────────────────────────────────────────────────────────

    async def generate_embedding(self, text: str) -> List[float]:
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
