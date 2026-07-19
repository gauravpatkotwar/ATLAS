from __future__ import annotations
import asyncio
import json
import time
from typing import Any, AsyncGenerator
import httpx

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


class OllamaProvider(AIProvider):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None
        self._models_cache: list[ModelInfo] | None = None

    @property
    def provider_type(self) -> AIProviderType:
        return AIProviderType.OLLAMA

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )
        await self._pull_default_models()

    async def _pull_default_models(self) -> None:
        models_to_pull = [
            settings.ai.openai_model,
            settings.ai.embedding_model,
            settings.ai.rerank_model,
        ]
        
        for model in models_to_pull:
            if model:
                try:
                    await self._pull_model(model)
                except Exception as e:
                    logger.warning(f"Failed to pull model {model}", error=str(e))

    async def _pull_model(self, model: str) -> None:
        if not self._client:
            return
        try:
            response = await self._client.post(
                "/api/pull",
                json={"name": model, "stream": False},
                timeout=300.0,
            )
            response.raise_for_status()
            logger.info(f"Pulled model: {model}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise

    async def health_check(self) -> bool:
        if not self._client:
            return False
        try:
            response = await self._client.get("/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[ModelInfo]:
        if not self._client:
            return []
        
        if self._models_cache is not None:
            return self._models_cache

        try:
            response = await self._client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model_data in data.get("models", []):
                name = model_data.get("name", "")
                model_info = ModelInfo(
                    name=name,
                    type=ModelType.CHAT,
                    max_tokens=8192,
                    supports_streaming=True,
                )
                models.append(model_info)
            
            self._models_cache = models
            return models
        except Exception as e:
            logger.error("Failed to list Ollama models", error=str(e))
            return []

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        if not self._client:
            raise RuntimeError("Provider not initialized")
        
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, endpoint, **kwargs)
                response.raise_for_status()
                return response
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
        
        raise last_exception

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
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
            },
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        if functions:
            payload["tools"] = functions
            if function_call:
                payload["tool_choice"] = function_call

        response = await self._request_with_retry("POST", "/api/chat", json=payload)
        data = response.json()
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        message = data.get("message", {})
        content = message.get("content", "")
        
        usage = data.get("usage", {})
        
        return CompletionResponse(
            content=content,
            model=model,
            usage={
                "prompt_tokens": usage.get("prompt_eval_count", 0),
                "completion_tokens": usage.get("eval_count", 0),
                "total_tokens": usage.get("prompt_eval_count", 0) + usage.get("eval_count", 0),
            },
            finish_reason=data.get("done_reason"),
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
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
            },
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        if functions:
            payload["tools"] = functions
            if function_call:
                payload["tool_choice"] = function_call

        async with self._client.stream("POST", "/api/chat", json=payload, timeout=self.timeout) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        message = data.get("message", {})
                        content = message.get("content", "")
                        if content:
                            yield content
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

    async def create_embedding(
        self,
        texts: list[str],
        model: str,
        **kwargs,
    ) -> EmbeddingResponse:
        start_time = time.time()
        
        embeddings = []
        for text in texts:
            response = await self._request_with_retry(
                "POST",
                "/api/embeddings",
                json={"model": model, "prompt": text},
            )
            data = response.json()
            embeddings.append(data.get("embedding", []))
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            usage={"total_tokens": sum(len(e) for e in embeddings)},
        )

    async def rerank(
        self,
        query: str,
        documents: list[str],
        model: str,
        top_k: int = 10,
        **kwargs,
    ) -> RerankResponse:
        response = await self._request_with_retry(
            "POST",
            "/api/rerank",
            json={"model": model, "query": query, "documents": documents, "top_k": top_k},
        )
        data = response.json()
        
        return RerankResponse(
            results=data.get("results", []),
            model=model,
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None