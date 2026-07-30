from abc import ABC, abstractmethod
from typing import Dict, Any, List


class AIProvider(ABC):
    """Abstract interface for AI LLM generation providers."""

    @abstractmethod
    async def extract_candidate_data(self, resume_text: str) -> Dict[str, Any]:
        """Extract candidate metadata (name, email, skills, education, experience, links) from raw resume text."""
        pass

    @abstractmethod
    async def generate_summary(self, resume_text: str) -> str:
        """Generate a concise professional candidate summary from raw resume text."""
        pass

    @abstractmethod
    async def chat_copilot(self, query: str, history: List[Dict[str, str]]) -> str:
        """Process queries on candidates/jobs database and answer as a helpful recruiter assistant."""
        pass

    @abstractmethod
    async def explain_recommendation(
        self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> str:
        """Explain why a candidate is suitable for a specific job and details on fit."""
        pass

    async def generate(self, prompt: str) -> str:
        """Generic single-turn text generation. Defaults to _post_generate if available, else chat_copilot."""
        if hasattr(self, '_post_generate'):
            return await self._post_generate(prompt)  # type: ignore
        return await self.chat_copilot(prompt, [])


class EmbeddingProvider(ABC):
    """Abstract interface for Generating Text Embeddings."""

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate numerical embedding array for the given input text."""
        pass
