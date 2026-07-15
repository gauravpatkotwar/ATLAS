from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.database.models import User
from atlas.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository supporting optional tenant context mapping."""

    def __init__(self, db: AsyncSession, tenant_id: Optional[int] = None):
        super().__init__(User, db, tenant_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Looks up a user globally by email."""
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
