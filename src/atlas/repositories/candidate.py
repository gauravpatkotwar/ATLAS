from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.database.models import Candidate
from atlas.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    """Candidate repository scoped strictly to the organization's tenant context."""

    def __init__(self, db: AsyncSession, tenant_id: int):
        super().__init__(Candidate, db, tenant_id)

    async def get_by_email(self, email: str) -> Optional[Candidate]:
        """Looks up candidate strictly inside the tenant boundaries by email."""
        result = await self.db.execute(
            select(Candidate)
            .filter(Candidate.email == email)
            .filter(Candidate.tenant_id == self.tenant_id)
        )
        return result.scalars().first()
