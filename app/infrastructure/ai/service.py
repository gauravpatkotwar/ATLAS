from __future__ import annotations
import time
import uuid
from typing import Any
from functools import lru_cache

from app.infrastructure.ai.providers.base import (
    AIProvider,
    AIProviderType,
    AIProviderFactory,
    CompletionResponse,
    EmbeddingResponse,
    RerankResponse,
    ModelInfo,
    ModelType,
    AIRequestLog,
)
from app.infrastructure.ai.providers.ollama import OllamaProvider
from app.infrastructure.ai.providers.openai import OpenAIProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIProviderManager:
    def __init__(self):
        self._providers: dict[AIProviderType, AIProvider] = {}
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        ollama = OllamaProvider(
            base_url=settings.ai.ollama_base_url,
            timeout=settings.ai.ollama_timeout,
            max_retries=settings.ai.max_retries,
        )
        await ollama.initialize()
        self._providers[AIProviderType.OLLAMA] = ollama
        AIProviderFactory.register(AIProviderType.OLLAMA, OllamaProvider)

        if settings.ai.openai_api_key:
            openai = OpenAIProvider(
                api_key=settings.ai.openai_api_key,
                base_url=settings.ai.openai_base_url,
                organization=settings.ai.openai_organization,
                timeout=settings.ai.openai_timeout,
                max_retries=settings.ai.max_retries,
            )
            await openai.initialize()
            self._providers[AIProviderType.OPENAI] = openai
            AIProviderFactory.register(AIProviderType.OPENAI, OpenAIProvider)

        self._initialized = True
        logger.info("AI providers initialized", providers=list(self._providers.keys()))

    def get_provider(self, provider_type: AIProviderType | None = None) -> AIProvider:
        if provider_type is None:
            provider_type = AIProviderType(settings.ai.default_provider)
        
        provider = self._providers.get(provider_type)
        if not provider:
            raise ValueError(f"Provider {provider_type} not available")
        return provider

    async def health_check_all(self) -> dict[AIProviderType, bool]:
        results = {}
        for ptype, provider in self._providers.items():
            results[ptype] = await provider.health_check()
        return results

    async def close_all(self) -> None:
        for provider in self._providers.values():
            await provider.close()
        self._providers.clear()
        self._initialized = False


_provider_manager: AIProviderManager | None = None


def get_provider_manager() -> AIProviderManager:
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = AIProviderManager()
    return _provider_manager


async def init_ai_providers() -> None:
    manager = get_provider_manager()
    await manager.initialize()


async def close_ai_providers() -> None:
    global _provider_manager
    if _provider_manager:
        await _provider_manager.close_all()
        _provider_manager = None


class AIService:
    def __init__(self, provider_manager: AIProviderManager | None = None):
        self.provider_manager = provider_manager or get_provider_manager()

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
        functions: list[dict] | None = None,
        function_call: str | dict | None = None,
        provider: AIProviderType | None = None,
        **kwargs,
    ) -> CompletionResponse:
        provider_type = provider or AIProviderType(settings.ai.default_provider)
        ai_provider = self.provider_manager.get_provider(provider_type)
        
        model = model or settings.ai.openai_model
        temperature = temperature if temperature is not None else settings.ai.temperature
        max_tokens = max_tokens or settings.ai.max_tokens

        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            if stream:
                raise ValueError("Use chat_completion_stream for streaming")
            
            response = await ai_provider.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                functions=functions,
                function_call=function_call,
                **kwargs,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            await self._log_request(AIRequestLog(
                request_id=request_id,
                provider=provider_type.value,
                model=model,
                operation="chat_completion",
                prompt_tokens=response.usage.get("prompt_tokens"),
                completion_tokens=response.usage.get("completion_tokens"),
                total_tokens=response.usage.get("total_tokens"),
                latency_ms=latency_ms,
                success=True,
            ))
            
            return response
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_request(AIRequestLog(
                request_id=request_id,
                provider=provider_type.value,
                model=model,
                operation="chat_completion",
                latency_ms=latency_ms,
                success=False,
                error=str(e),
            ))
            raise

    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        functions: list[dict] | None = None,
        function_call: str | dict | None = None,
        provider: AIProviderType | None = None,
        **kwargs,
    ):
        provider_type = provider or AIProviderType(settings.ai.default_provider)
        ai_provider = self.provider_manager.get_provider(provider_type)
        
        model = model or settings.ai.openai_model
        temperature = temperature if temperature is not None else settings.ai.temperature
        max_tokens = max_tokens or settings.ai.max_tokens

        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            async for chunk in ai_provider.chat_completion_stream(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                functions=functions,
                function_call=function_call,
                **kwargs,
            ):
                yield chunk
            
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_request(AIRequestLog(
                request_id=request_id,
                provider=provider_type.value,
                model=model,
                operation="chat_completion_stream",
                latency_ms=latency_ms,
                success=True,
            ))
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_request(AIRequestLog(
                request_id=request_id,
                provider=provider_type.value,
                model=model,
                operation="chat_completion_stream",
                latency_ms=latency_ms,
                success=False,
                error=str(e),
            ))
            raise

    async def create_embedding(
        self,
        texts: list[str],
        model: str | None = None,
        provider: AIProviderType | None = None,
        **kwargs,
    ) -> EmbeddingResponse:
        provider_type = provider or AIProviderType(settings.ai.embedding_provider)
        ai_provider = self.provider_manager.get_provider(provider_type)
        
        model = model or settings.ai.embedding_model

        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            response = await ai_provider.create_embedding(
                texts=texts,
                model=model,
                **kwargs,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            await self._log_request(AIRequestLog(
                request_id=request_id,
                provider=provider_type.value,
                model=model,
                operation="embedding",
                prompt_tokens=len(texts),
                total_tokens=response.usage.get("total_tokens"),
                latency_ms=latency_ms,
                success=True,
            ))
            
            return response
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_request(AIRequestLog(
                request_id=request_id,
                provider=provider_type.value,
                model=model,
                operation="embedding",
                latency_ms=latency_ms,
                success=False,
                error=str(e),
            ))
            raise

    async def rerank(
        self,
        query: str,
        documents: list[str],
        model: str | None = None,
        top_k: int = 10,
        provider: AIProviderType | None = None,
        **kwargs,
    ) -> RerankResponse:
        provider_type = provider or AIProviderType(settings.ai.rerank_provider)
        ai_provider = self.provider_manager.get_provider(provider_type)
        
        model = model or settings.ai.rerank_model

        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            response = await ai_provider.rerank(
                query=query,
                documents=documents,
                model=model,
                top_k=top_k,
                **kwargs,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            await self._log_request(AIRequestLog(
                request_id=request_id,
                provider=provider_type.value,
                model=model,
                operation="rerank",
                latency_ms=latency_ms,
                success=True,
            ))
            
            return response
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_request(AIRequestLog(
                request_id=request_id,
                provider=provider_type.value,
                model=model,
                operation="rerank",
                latency_ms=latency_ms,
                success=False,
                error=str(e),
            ))
            raise

    async def _log_request(self, log: AIRequestLog) -> None:
        logger.info(
            "AI request logged",
            request_id=log.request_id,
            provider=log.provider,
            model=log.model,
            operation=log.operation,
            latency_ms=log.latency_ms,
            success=log.success,
            tokens=log.total_tokens,
        )