from __future__ import annotations
from typing import Any

import chromadb
from chromadb.config import Settings

from app.infrastructure.vector_db.base import (
    VectorStore,
    VectorDocument,
    SearchResult,
    CollectionInfo,
)


class ChromaVectorStore(VectorStore):
    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        host: str | None = None,
        port: int | None = None,
    ):
        if host and port:
            self.client = chromadb.HttpClient(host=host, port=port)
        else:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )

    async def create_collection(
        self,
        name: str,
        dimension: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.client.get_or_create_collection(
            name=name,
            metadata={"dimension": dimension, **(metadata or {})},
        )

    async def delete_collection(self, name: str) -> None:
        try:
            self.client.delete_collection(name=name)
        except Exception:
            pass

    async def list_collections(self) -> list[CollectionInfo]:
        collections = []
        for col in self.client.list_collections():
            collections.append(CollectionInfo(
                name=col.name,
                dimension=col.metadata.get("dimension", 0) if col.metadata else 0,
                count=col.count(),
                metadata=col.metadata or {},
            ))
        return collections

    async def get_collection_info(self, name: str) -> CollectionInfo | None:
        try:
            col = self.client.get_collection(name=name)
            return CollectionInfo(
                name=col.name,
                dimension=col.metadata.get("dimension", 0) if col.metadata else 0,
                count=col.count(),
                metadata=col.metadata or {},
            )
        except Exception:
            return None

    async def upsert(
        self,
        collection: str,
        documents: list[VectorDocument],
    ) -> list[str]:
        col = self.client.get_collection(name=collection)
        
        ids = [doc.id for doc in documents]
        embeddings = [doc.embedding for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        contents = [doc.content for doc in documents]
        
        col.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=contents,
        )
        
        return ids

    async def delete(
        self,
        collection: str,
        ids: list[str],
    ) -> int:
        col = self.client.get_collection(name=collection)
        col.delete(ids=ids)
        return len(ids)

    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
        include_metadata: bool = True,
        include_content: bool = True,
    ) -> list[SearchResult]:
        col = self.client.get_collection(name=collection)
        
        results = col.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=filter,
            include=["metadatas", "documents", "distances"],
        )
        
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if include_metadata else {}
                content = results["documents"][0][i] if include_content else ""
                distance = results["distances"][0][i]
                score = 1.0 - distance
                
                search_results.append(SearchResult(
                    document=VectorDocument(
                        id=doc_id,
                        content=content,
                        embedding=[],
                        metadata=metadata,
                    ),
                    score=score,
                ))
        
        return search_results

    async def search_by_id(
        self,
        collection: str,
        id: str,
    ) -> VectorDocument | None:
        col = self.client.get_collection(name=collection)
        results = col.get(ids=[id], include=["metadatas", "documents", "embeddings"])
        
        if results["ids"]:
            return VectorDocument(
                id=results["ids"][0],
                content=results["documents"][0] if results["documents"] else "",
                embedding=results["embeddings"][0] if results["embeddings"] else [],
                metadata=results["metadatas"][0] if results["metadatas"] else {},
            )
        return None

    async def hybrid_search(
        self,
        collection: str,
        query_text: str,
        query_vector: list[float],
        top_k: int = 10,
        alpha: float = 0.5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        col = self.client.get_collection(name=collection)
        
        results = col.query(
            query_embeddings=[query_vector],
            query_texts=[query_text],
            n_results=top_k,
            where=filter,
            include=["metadatas", "documents", "distances"],
        )
        
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                content = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i]
                score = 1.0 - distance
                
                search_results.append(SearchResult(
                    document=VectorDocument(
                        id=doc_id,
                        content=content,
                        embedding=[],
                        metadata=metadata,
                    ),
                    score=score,
                ))
        
        return search_results