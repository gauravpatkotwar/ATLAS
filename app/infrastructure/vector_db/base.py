from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID
from dataclasses import dataclass


@dataclass
class VectorDocument:
    id: str
    content: str
    embedding: list[float]
    metadata: dict[str, Any]
    score: float | None = None


@dataclass
class SearchResult:
    document: VectorDocument
    score: float


@dataclass
class CollectionInfo:
    name: str
    dimension: int
    count: int
    metadata: dict[str, Any]


class VectorStore(ABC):
    @abstractmethod
    async def create_collection(
        self,
        name: str,
        dimension: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        pass

    @abstractmethod
    async def delete_collection(self, name: str) -> None:
        pass

    @abstractmethod
    async def list_collections(self) -> list[CollectionInfo]:
        pass

    @abstractmethod
    async def get_collection_info(self, name: str) -> CollectionInfo | None:
        pass

    @abstractmethod
    async def upsert(
        self,
        collection: str,
        documents: list[VectorDocument],
    ) -> list[str]:
        pass

    @abstractmethod
    async def delete(
        self,
        collection: str,
        ids: list[str],
    ) -> int:
        pass

    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
        include_metadata: bool = True,
        include_content: bool = True,
    ) -> list[SearchResult]:
        pass

    @abstractmethod
    async def search_by_id(
        self,
        collection: str,
        id: str,
    ) -> VectorDocument | None:
        pass

    @abstractmethod
    async def hybrid_search(
        self,
        collection: str,
        query_text: str,
        query_vector: list[float],
        top_k: int = 10,
        alpha: float = 0.5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        pass


class VectorStoreFactory:
    _stores: dict[str, type[VectorStore]] = {}

    @classmethod
    def register(cls, name: str, store_class: type[VectorStore]) -> None:
        cls._stores[name] = store_class

    @classmethod
    def create(cls, name: str, **kwargs) -> VectorStore:
        store_class = cls._stores.get(name)
        if not store_class:
            raise ValueError(f"Unknown vector store: {name}")
        return store_class(**kwargs)

    @classmethod
    def get_available_stores(cls) -> list[str]:
        return list(cls._stores.keys())