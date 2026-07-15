from typing import Dict
from atlas.config.settings import settings
from atlas.ai.base import AIProvider, EmbeddingProvider
from atlas.ai.ollama import OllamaProvider


class AIProviderFactory:
    """Factory to resolve AI and Embedding provider implementations based on settings."""

    _ai_cache: Dict[str, AIProvider] = {}
    _embed_cache: Dict[str, EmbeddingProvider] = {}

    @classmethod
    def get_ai_provider(cls) -> AIProvider:
        provider_type = settings.AI_PROVIDER.lower()
        if provider_type not in cls._ai_cache:
            if provider_type == "ollama":
                cls._ai_cache[provider_type] = OllamaProvider()
            else:
                raise ValueError(f"Unsupported AI provider type: {provider_type}")
        return cls._ai_cache[provider_type]

    @classmethod
    def get_embedding_provider(cls) -> EmbeddingProvider:
        provider_type = settings.AI_PROVIDER.lower()
        if provider_type not in cls._embed_cache:
            if provider_type == "ollama":
                cls._embed_cache[provider_type] = OllamaProvider()
            else:
                raise ValueError(
                    f"Unsupported Embedding provider type: {provider_type}"
                )
        return cls._embed_cache[provider_type]
