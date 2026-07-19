from __future__ import annotations
import time
from typing import Any, AsyncGenerator
import openai
from openai import AsyncOpenAI

from app.infrastructure.ai.providers.base import (
    AIProvider,
    AIProviderType,
    ModelInfo,
    ModelType,
    CompletionResponse,
    EmbeddingResponse,
    RerankResponse,
)
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider(AIProvider):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        organization: str | None = None,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        self.api_key = api_key or settings.ai.openai_api_key
        self.base_url = base_url or settings.ai.openai_base_url
        self.organization = organization or settings.ai.openai_organization
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: AsyncOpenAI | None = None
        self._models_cache: list[ModelInfo] | None = None

    @property
    def provider_type(self) -> AIProviderType:
        return AIProviderType.OPENAI

    async def initialize(self) -> None:
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            organization=self.organization,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    async def health_check(self) -> bool:
        if not self._client:
            return False
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False

    async def list_models(self) -> list[ModelInfo]:
        if not self._client:
            return []
        
        if self._models_cache is not None:
            return self._models_cache

        try:
            models = await self._client.models.list()
            model_infos = []
            for model in models.data:
                model_type = ModelType.CHAT
                if "embedding" in model.id:
                    model_type = ModelType.EMBEDDING
                elif "rerank" in model.id:
                    model_type = ModelType.RERANK
                
                model_infos.append(ModelInfo(
                    name=model.id,
                    type=model_type,
                    supports_streaming=True,
                    supports_functions="gpt-4" in model.id or "gpt-3.5" in model.id,
                ))
            
            self._models_cache = model_infos
            return model_infos
        except Exception as e:
            logger.error("Failed to list OpenAI models", error=str(e))
            return []

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
    ) -> CompletionResponse:
        start_time = time.time()
        
        if not self._client:
            raise RuntimeError("Provider not initialized")

        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        if functions:
            params["tools"] = functions
            if function_call:
                params["tool_choice"] = function_call

        response = await self._client.chat.completions.create(**params)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        choice = response.choices[0]
        content = choice.message.content or ""
        
        function_calls = None
        if choice.message.tool_calls:
            function_calls = [
                {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
                for tc in choice.message.tool_calls
            ]

        return CompletionResponse(
            content=content,
            model=model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            finish_reason=choice.finish_reason,
            function_calls=function_calls,
        )

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
        if not self._client:
            raise RuntimeError("Provider not initialized")

        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        if functions:
            params["tools"] = functions
            if function_call:
                params["tool_choice"] = function_call

        stream = await self._client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def create_embedding(
        self,
        texts: list[str],
        model: str,
        **kwargs,
    ) -> EmbeddingResponse:
        start_time = time.time()
        
        if not self._client:
            raise RuntimeError("Provider not initialized")

        response = await self._client.embeddings.create(
            model=model,
            input=texts,
            **kwargs,
        )
        
        embeddings = [data.embedding for data in response.data]
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        )

    async def rerank(
        self,
        query: str,
        documents: list[str],
        model: str,
        top_k: int = 10,
        **kwargs,
    ) -> RerankResponse:
        return RerankResponse(
            results=[],
            model=model,
        )