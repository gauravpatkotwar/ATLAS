from typing import Generic, TypeVar, Type, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic async repository interface supporting dynamic Tenant data isolation filters."""

    def __init__(
        self, model: Type[ModelType], db: AsyncSession, tenant_id: Optional[int] = None
    ):
        self.model = model
        self.db = db
        self.tenant_id = tenant_id

    async def get(self, id: Any) -> Optional[ModelType]:
        """Fetches a record by ID, filtered by tenant context if specified."""
        query = select(self.model).filter(getattr(self.model, "id") == id)
        if self.tenant_id is not None and hasattr(self.model, "tenant_id"):
            query = query.filter(getattr(self.model, "tenant_id") == self.tenant_id)

        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Lists records, filtered by tenant context if specified."""
        query = select(self.model).offset(skip).limit(limit)
        if self.tenant_id is not None and hasattr(self.model, "tenant_id"):
            query = query.filter(getattr(self.model, "tenant_id") == self.tenant_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: ModelType) -> ModelType:
        """Saves a record, auto-assigning tenant context if specified."""
        if self.tenant_id is not None and hasattr(obj_in, "tenant_id"):
            setattr(obj_in, "tenant_id", self.tenant_id)

        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Modifies a record, raising a PermissionError upon cross-tenant writes."""
        if self.tenant_id is not None and hasattr(db_obj, "tenant_id"):
            if getattr(db_obj, "tenant_id") != self.tenant_id:
                raise PermissionError(
                    "Access Denied: Cross-tenant updates are not allowed."
                )

        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> bool:
        """Deletes a record matching ID and tenant context."""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
