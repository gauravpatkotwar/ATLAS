from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator
from uuid import UUID

from pydantic import BaseModel, Field


class AIProviderType(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    NVIDIA = "nvidia"


class ModelType(str, Enum):
    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_GENERATION = "audio_generation"
    IMAGE_GENERATION = "image_generation"


@dataclass
class ModelInfo:
    name: str
    type: ModelType
    dimensions: int | None = None
    max_tokens: int | None = None
    supports_streaming: bool = False
    supports_functions: bool = False
    supports_vision: bool = False


class AIProvider(ABC):
    @property
    @abstractmethod
    def provider_type(self) -> AIProviderType:
        pass

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int | None = None,
        stream: bool = False,
        functions: list[dict] | None = None,
        function_call: str | dict | None = None,
        **kwargs,
    ) -> Any:
        pass

    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int | None = None,
        functions: list[dict] | None = None,
        function_call: str | dict | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    async def create_embedding(
        self,
        texts: list[str],
        model: str,
        **kwargs,
    ) -> list[list[float]]:
        pass

    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: list[str],
        model: str,
        top_k: int = 10,
        **kwargs,
    ) -> list[dict[str, Any]]:
        pass


class CompletionResponse(BaseModel):
    model_config = {"extra": "allow"}
    content: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)
    finish_reason: str | None = None
    function_calls: list[dict] | None = None


class EmbeddingResponse(BaseModel):
    model_config = {"extra": "allow"}
    embeddings: list[list[float]]
    model: str
    usage: dict[str, int] = Field(default_factory=dict)


class RerankResponse(BaseModel):
    model_config = {"extra": "allow"}
    results: list[dict[str, Any]]
    model: str


class TranscriptionResponse(BaseModel):
    model_config = {"extra": "allow"}
    text: str
    language: str | None = None
    duration: float | None = None
    segments: list[dict] | None = None


class AIRequestLog(BaseModel):
    model_config = {"extra": "allow"}
    request_id: UUID
    provider: AIProviderType
    model: str
    operation: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: int
    success: bool
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIProviderFactory:
    _providers: dict[AIProviderType, type[AIProvider]] = {}

    @classmethod
    def register(cls, provider_type: AIProviderType, provider_class: type[AIProvider]) -> None:
        cls._providers[provider_type] = provider_class

    @classmethod
    def create(cls, provider_type: AIProviderType, **kwargs) -> AIProvider:
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")
        return provider_class(**kwargs)

    @classmethod
    def get_available_providers(cls) -> list[AIProviderType]:
        return list(cls._providers.keys())