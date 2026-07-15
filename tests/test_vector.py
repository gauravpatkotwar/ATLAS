import os
from atlas.vector.store import FAISSVectorStore


def test_faiss_vector_store_operations():
    """Validates vector persistence, L2 normalization, cosine similarity lookup, and rollback index-rebuilding."""
    temp_path = "test_vector_store.faiss"

    # Pre-test cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)
    if os.path.exists(temp_path + ".map"):
        os.remove(temp_path + ".map")

    try:
        # Create small 4-dimension index for unit testing
        store = FAISSVectorStore(index_path=temp_path, dimension=4)

        v1 = [1.0, 0.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0, 0.0]

        store.add_vector(db_id=101, vector=v1)
        store.add_vector(db_id=202, vector=v2)

        assert store.index.ntotal == 2
        assert store.id_map[0] == 101
        assert store.id_map[1] == 202

        # Test file persistence
        store.save()
        assert os.path.exists(temp_path)
        assert os.path.exists(temp_path + ".map")

        # Test reloading index from disk files
        loaded_store = FAISSVectorStore(index_path=temp_path, dimension=4)
        assert loaded_store.index.ntotal == 2
        assert loaded_store.id_map[0] == 101

        # Test cosine similarity query search
        query = [0.8, 0.2, 0.0, 0.0]
        results = loaded_store.search(query, top_k=2)
        assert len(results) == 2
        # Candidate 101 should match first (highest similarity)
        assert results[0][0] == 101
        assert results[0][1] > results[1][1]

        # Test deletion rebuilding
        loaded_store.remove_vector(101)
        assert loaded_store.index.ntotal == 1
        assert loaded_store.id_map[0] == 202
        assert loaded_store.db_id_map.get(101) is None

    finally:
        # Post-test teardown cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_path + ".map"):
            os.remove(temp_path + ".map")
