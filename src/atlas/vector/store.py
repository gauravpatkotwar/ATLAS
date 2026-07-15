import os
import pickle
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import faiss
from atlas.config.settings import settings


class FAISSVectorStore:
    """FAISS-based vector database supporting L2-normalized cosine similarity search."""

    def __init__(self, index_path: Optional[str] = None, dimension: int = 768):
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.dimension = dimension
        self.index: Any = None
        self.id_map: Dict[int, int] = (
            {}
        )  # Maps FAISS row index -> Database candidate ID
        self.db_id_map: Dict[int, int] = (
            {}
        )  # Maps Database candidate ID -> FAISS row index
        self._load_or_create()

    def _load_or_create(self) -> None:
        if os.path.exists(self.index_path) and os.path.exists(self.index_path + ".map"):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.index_path + ".map", "rb") as f:
                    self.id_map, self.db_id_map = pickle.load(f)
                return
            except Exception:
                # Reset if corrupt or incompatible version
                pass

        # Inner Product Flat index maps exactly to Cosine Similarity when vectors are L2-normalized
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = {}
        self.db_id_map = {}

    def save(self) -> None:
        """Persist current index and ID mappings to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.index_path + ".map", "wb") as f:
            pickle.dump((self.id_map, self.db_id_map), f)

    def add_vector(self, db_id: int, vector: List[float]) -> None:
        """Add candidate embedding vector to FAISS, replacing existing if db_id matches."""
        if not vector or len(vector) != self.dimension:
            raise ValueError(f"Vector dimension must be exactly {self.dimension}")

        vec_np = np.array(vector, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(vec_np)

        if db_id in self.db_id_map:
            self.remove_vector(db_id)

        next_row = self.index.ntotal
        self.index.add(vec_np)
        self.id_map[next_row] = db_id
        self.db_id_map[db_id] = next_row
        self.save()

    def remove_vector(self, db_id: int) -> None:
        """Remove candidate embedding vector by database ID (rebuilds the index)."""
        if db_id not in self.db_id_map:
            return

        all_vectors = []
        all_ids = []
        for row in range(self.index.ntotal):
            mapped_db_id = self.id_map[row]
            if mapped_db_id == db_id:
                continue
            all_vectors.append(self.index.reconstruct(row))
            all_ids.append(mapped_db_id)

        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = {}
        self.db_id_map = {}

        if all_vectors:
            vectors_np = np.array(all_vectors, dtype=np.float32)
            self.index.add(vectors_np)
            for i, mapped_db_id in enumerate(all_ids):
                self.id_map[i] = mapped_db_id
                self.db_id_map[mapped_db_id] = i
        self.save()

    def search(
        self, query_vector: List[float], top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """Search similar embeddings. Returns list of (db_id, similarity_score)."""
        if not query_vector or len(query_vector) != self.dimension:
            return []
        if self.index.ntotal == 0:
            return []

        q_vec = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(q_vec)

        actual_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q_vec, actual_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            db_id = self.id_map.get(int(idx))
            if db_id is not None:
                results.append((db_id, float(score)))
        return results

    def clear(self) -> None:
        """Clear index and wipe index files."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = {}
        self.db_id_map = {}
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.index_path + ".map"):
            os.remove(self.index_path + ".map")


# Shared singleton index instance
vector_store = FAISSVectorStore()
