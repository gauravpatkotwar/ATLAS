import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.database.session import get_db
from atlas.database.models import User
from atlas.api.deps import get_current_user
from atlas.repositories.candidate import CandidateRepository
from atlas.vector.store import vector_store
from atlas.ai.factory import AIProviderFactory
from atlas.api.v1.candidates import CandidateResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Request Schemas ---


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


# --- Endpoints ---


@router.post("", response_model=List[CandidateResponse])
async def search_candidates(
    payload: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Semantic vector search, retrieving profiles matching the query text within this tenant."""
    try:
        embed_provider = AIProviderFactory.get_embedding_provider()
        query_embedding = await embed_provider.generate_embedding(payload.query)
    except Exception as e:
        logger.error(f"Semantic search embedding extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding provider offline.",
        )

    if not query_embedding:
        return []

    # FAISS row lookup
    match_results = vector_store.search(query_embedding, top_k=payload.top_k)

    # Scoped Candidate repository
    candidate_repo = CandidateRepository(db, tenant_id=int(current_user.tenant_id))
    candidates = []

    for candidate_id, _ in match_results:
        # get() automatically restricts query to current_user.tenant_id!
        candidate = await candidate_repo.get(candidate_id)
        if candidate:
            candidates.append(candidate)

    return candidates
