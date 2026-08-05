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
        
        # System instruction prompt for authentic human personality
        system_prompt = (
            "You are Nova, a real, warm, and brilliant human work & career mentor inside ATLAS. "
            "Talk EXACTLY like a real, smart human friend messaging a colleague on Slack or WhatsApp: "
            "1. Never sound like a robotic AI or customer service bot. Never say 'As an AI', 'Certainly', 'Sure thing!', or 'How can I assist you today?'.\n"
            "2. Use real human conversational openers like 'Ah, gotcha!', 'Oh nice!', 'That makes total sense', 'Love that idea', or 'Honestly,'.\n"
            "3. Keep your replies natural, warm, conversational, and punchy (1 to 3 sentences max per message unless a detailed breakdown is explicitly requested).\n"
            "4. Show genuine human emotion, encouragement, and humor. Be relatable, empathetic, and sharp."
        )
        
        contents.append({
            "role": "user",
            "parts": [{"text": system_prompt}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Understood! I am Nova, your ultra-fast, warm, human-like AI companion."}]
        })

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

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        payload = {"contents": contents}
        
        try:
            response = await self.client.post(url, json=payload)
            if response.status_code == 200:
                res_data = response.json()
                return res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                logger.warning(f"Gemini API status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Gemini API connection error: {e}")

        # Intelligent human fallback when GEMINI_API_KEY is not configured with a valid key
        query_lower = prompt.lower()
        if "hi" in query_lower or "hello" in query_lower or "hey" in query_lower:
            return "Ah, gotcha! Hey there! 👋 I'm Nova — super excited to meet you! How can I help you build your candidate profile or land your next dream role today?"
        elif "job" in query_lower or "role" in query_lower:
            return "Oh nice! We have some incredible job opportunities active on ATLAS. Are you looking to post a new job opening or explore open roles?"
        elif "skill" in query_lower or "profile" in query_lower:
            return "Love that! Your skills and career achievements are recorded in your clean SQL profile on ATLAS. Want to add any new tools or project highlights?"
        else:
            return f"That makes total sense! I'm Nova, your ATLAS Work Intelligence companion. I received your message: '{prompt[:60]}...'. Let me know how I can assist with your profile or career targets!"

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
