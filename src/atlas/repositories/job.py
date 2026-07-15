from sqlalchemy.ext.asyncio import AsyncSession
from atlas.database.models import Job
from atlas.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Job repository scoped to tenant context."""

    def __init__(self, db: AsyncSession, tenant_id: int):
        super().__init__(Job, db, tenant_id)
