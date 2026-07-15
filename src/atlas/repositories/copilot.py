from typing import List
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.database.models import CopilotMessage
from atlas.repositories.base import BaseRepository


class CopilotMessageRepository(BaseRepository[CopilotMessage]):
    """Repository handling Copilot conversation history logs, scoped by tenant context."""

    def __init__(self, db: AsyncSession, tenant_id: int):
        super().__init__(CopilotMessage, db, tenant_id)

    async def get_by_user(self, user_id: int) -> List[CopilotMessage]:
        """Loads all chat messages for a user sorted by chronological order within this tenant."""
        result = await self.db.execute(
            select(CopilotMessage)
            .filter(CopilotMessage.user_id == user_id)
            .filter(CopilotMessage.tenant_id == self.tenant_id)
            .order_by(CopilotMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def clear_by_user(self, user_id: int) -> None:
        """Deletes all message records for a specific user within this tenant."""
        await self.db.execute(
            delete(CopilotMessage)
            .filter(CopilotMessage.user_id == user_id)
            .filter(CopilotMessage.tenant_id == self.tenant_id)
        )
        await self.db.commit()
