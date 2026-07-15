from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.database.models import AuditLog
from atlas.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """AuditLog repository isolating system audit logs per tenant."""

    def __init__(self, db: AsyncSession, tenant_id: int):
        super().__init__(AuditLog, db, tenant_id)

    async def get_by_target(self, target_type: str, target_id: str) -> List[AuditLog]:
        """Loads target logs strictly within tenant boundaries."""
        result = await self.db.execute(
            select(AuditLog)
            .filter(
                AuditLog.target_type == target_type, AuditLog.target_id == target_id
            )
            .filter(AuditLog.tenant_id == self.tenant_id)
            .order_by(AuditLog.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> List[AuditLog]:
        """Loads user logs strictly within tenant boundaries."""
        result = await self.db.execute(
            select(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .filter(AuditLog.tenant_id == self.tenant_id)
            .order_by(AuditLog.timestamp.desc())
        )
        return list(result.scalars().all())
