from __future__ import annotations
import json
import os
import pickle
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.infrastructure.vector_db.base import (
    VectorStore,
    VectorDocument,
    SearchResult,
    CollectionInfo,
)


class FAISSVectorStore(VectorStore):
    def __init__(self, persist_directory: str = "./data/vector_store"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self._indexes: dict[str, faiss.Index] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._documents: dict[str, dict[str, VectorDocument]] = {}

    def _get_index_path(self, collection: str) -> Path:
        return self.persist_directory / f"{collection}.index"

    def _get_metadata_path(self, collection: str) -> Path:
        return self.persist_directory / f"{collection}_meta.json"

    def _get_documents_path(self, collection: str) -> Path:
        return self.persist_directory / f"{collection}_docs.pkl"

    async def create_collection(
        self,
        name: str,
        dimension: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if name in self._indexes:
            return
        
        index = faiss.IndexFlatIP(dimension)
        self._indexes[name] = index
        self._metadata[name] = metadata or {}
        self._documents[name] = {}
        
        index_path = self._get_index_path(name)
        if index_path.exists():
            await self._load_collection(name)

    async def delete_collection(self, name: str) -> None:
        if name in self._indexes:
            del self._indexes[name]
        if name in self._metadata:
            del self._metadata[name]
        if name in self._documents:
            del self._documents[name]
        
        for path in [
            self._get_index_path(name),
            self._get_metadata_path(name),
            self._get_documents_path(name),
        ]:
            if path.exists():
                path.unlink()

    async def list_collections(self) -> list[CollectionInfo]:
        collections = []
        for name, index in self._indexes.items():
            collections.append(CollectionInfo(
                name=name,
                dimension=index.d,
                count=index.ntotal,
                metadata=self._metadata.get(name, {}),
            ))
        return collections

    async def get_collection_info(self, name: str) -> CollectionInfo | None:
        if name not in self._indexes:
            return None
        index = self._indexes[name]
        return CollectionInfo(
            name=name,
            dimension=index.d,
            count=index.ntotal,
            metadata=self._metadata.get(name, {}),
        )

    async def upsert(
        self,
        collection: str,
        documents: list[VectorDocument],
    ) -> list[str]:
        if collection not in self._indexes:
            raise ValueError(f"Collection '{collection}' does not exist")
        
        index = self._indexes[collection]
        docs_dict = self._documents[collection]
        
        vectors = []
        ids = []
        
        for doc in documents:
            vector = np.array(doc.embedding, dtype=np.float32).reshape(1, -1)
            faiss.normalize_L2(vector)
            vectors.append(vector[0])
            ids.append(doc.id)
            docs_dict[doc.id] = doc
        
        if vectors:
            vectors_array = np.array(vectors, dtype=np.float32)
            index.add(vectors_array)
        
        await self._persist_collection(collection)
        return ids

    async def delete(
        self,
        collection: str,
        ids: list[str],
    ) -> int:
        if collection not in self._indexes:
            return 0
        
        docs_dict = self._documents.get(collection, {})
        deleted = 0
        for doc_id in ids:
            if doc_id in docs_dict:
                del docs_dict[doc_id]
                deleted += 1
        
        if deleted > 0:
            await self._rebuild_index(collection)
        
        return deleted

    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
        include_metadata: bool = True,
        include_content: bool = True,
    ) -> list[SearchResult]:
        if collection not in self._indexes:
            return []
        
        index = self._indexes[collection]
        docs_dict = self._documents[collection]
        
        query = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(query)
        
        scores, indices = index.search(query, min(top_k, index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            
            doc_ids = list(docs_dict.keys())
            if idx < len(doc_ids):
                doc_id = doc_ids[idx]
                doc = docs_dict[doc_id]
                
                if filter and not self._matches_filter(doc.metadata, filter):
                    continue
                
                if not include_metadata:
                    doc.metadata = {}
                if not include_content:
                    doc.content = ""
                
                results.append(SearchResult(document=doc, score=float(score)))
        
        return results

    async def search_by_id(
        self,
        collection: str,
        id: str,
    ) -> VectorDocument | None:
        if collection not in self._documents:
            return None
        return self._documents[collection].get(id)

    async def hybrid_search(
        self,
        collection: str,
        query_text: str,
        query_vector: list[float],
        top_k: int = 10,
        alpha: float = 0.5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        return await self.search(collection, query_vector, top_k, filter)

    def _matches_filter(self, metadata: dict[str, Any], filter: dict[str, Any]) -> bool:
        for key, value in filter.items():
            if key not in metadata:
                return False
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            elif metadata[key] != value:
                return False
        return True

    async def _persist_collection(self, collection: str) -> None:
        index = self._indexes[collection]
        faiss.write_index(index, str(self._get_index_path(collection)))
        
        with open(self._get_metadata_path(collection), 'w') as f:
            json.dump(self._metadata[collection], f)
        
        with open(self._get_documents_path(collection), 'wb') as f:
            pickle.dump(self._documents[collection], f)

    async def _load_collection(self, collection: str) -> None:
        index_path = self._get_index_path(collection)
        if index_path.exists():
            self._indexes[collection] = faiss.read_index(str(index_path))
        
        meta_path = self._get_metadata_path(collection)
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                self._metadata[collection] = json.load(f)
        
        docs_path = self._get_documents_path(collection)
        if docs_path.exists():
            with open(docs_path, 'rb') as f:
                self._documents[collection] = pickle.load(f)

    async def _rebuild_index(self, collection: str) -> None:
        docs_dict = self._documents[collection]
        dimension = self._indexes[collection].d
        
        new_index = faiss.IndexFlatIP(dimension)
        vectors = []
        
        for doc in docs_dict.values():
            vector = np.array(doc.embedding, dtype=np.float32).reshape(1, -1)
            faiss.normalize_L2(vector)
            vectors.append(vector[0])
        
        if vectors:
            vectors_array = np.array(vectors, dtype=np.float32)
            new_index.add(vectors_array)
        
        self._indexes[collection] = new_index
        await self._persist_collection(collection)