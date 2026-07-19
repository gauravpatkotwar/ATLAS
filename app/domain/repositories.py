from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import InstrumentedAttribute

from app.domain.base import Entity

T = TypeVar("T", bound=Entity)


class RepositoryPort(ABC, Generic[T]):
    @abstractmethod
    async def add(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get(self, id: UUID) -> T | None:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass

    @abstractmethod
    async def soft_delete(self, id: UUID) -> bool:
        pass

    @abstractmethod
    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        order_by: list[tuple[str, str]] | None = None,
    ) -> list[T]:
        pass

    @abstractmethod
    async def count(self, filters: dict[str, Any] | None = None) -> int:
        pass

    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        pass


class TenantRepositoryPort(RepositoryPort[T], ABC):
    @abstractmethod
    async def get_by_tenant(
        self,
        tenant_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        order_by: list[tuple[str, str]] | None = None,
    ) -> list[T]:
        pass

    @abstractmethod
    async def count_by_tenant(self, tenant_id: UUID, filters: dict[str, Any] | None = None) -> int:
        pass

    @abstractmethod
    async def exists_in_tenant(self, tenant_id: UUID, id: UUID) -> bool:
        pass


class SQLAlchemyRepository(RepositoryPort[T]):
    def __init__(self, session: AsyncSession, model_class: type[T]):
        self.session = session
        self.model_class = model_class

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get(self, id: UUID) -> T | None:
        return await self.session.get(self.model_class, id)

    async def get_by_id(self, id: UUID) -> T | None:
        return await self.get(id)

    async def update(self, entity: T) -> T:
        entity.mark_updated()
        await self.session.flush()
        return entity

    async def delete(self, id: UUID) -> bool:
        entity = await self.get(id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
            return True
        return False

    async def soft_delete(self, id: UUID) -> bool:
        entity = await self.get(id)
        if entity and not entity.is_deleted:
            entity.mark_deleted()
            await self.session.flush()
            return True
        return False

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        order_by: list[tuple[str, str]] | None = None,
    ) -> list[T]:
        query = select(self.model_class).where(self.model_class.deleted_at.is_(None))

        if filters:
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    attr = getattr(self.model_class, key)
                    if isinstance(value, list):
                        query = query.where(attr.in_(value))
                    else:
                        query = query.where(attr == value)

        if order_by:
            for field, direction in order_by:
                if hasattr(self.model_class, field):
                    attr = getattr(self.model_class, field)
                    query = query.order_by(attr.desc() if direction.lower() == "desc" else attr.asc())

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        query = select(func.count()).select_from(self.model_class).where(self.model_class.deleted_at.is_(None))

        if filters:
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    attr = getattr(self.model_class, key)
                    if isinstance(value, list):
                        query = query.where(attr.in_(value))
                    else:
                        query = query.where(attr == value)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def exists(self, id: UUID) -> bool:
        query = select(func.count()).select_from(self.model_class).where(
            self.model_class.id == id,
            self.model_class.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return (result.scalar() or 0) > 0


class SQLAlchemyTenantRepository(SQLAlchemyRepository[T], TenantRepositoryPort[T]):
    def __init__(self, session: AsyncSession, model_class: type[T], tenant_id: UUID):
        super().__init__(session, model_class)
        self.tenant_id = tenant_id

    def _apply_tenant_filter(self, query):
        return query.where(self.model_class.tenant_id == self.tenant_id)

    async def get(self, id: UUID) -> T | None:
        query = select(self.model_class).where(
            self.model_class.id == id,
            self.model_class.tenant_id == self.tenant_id,
            self.model_class.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, id: UUID) -> T | None:
        return await self.get(id)

    async def update(self, entity: T) -> T:
        if entity.tenant_id != self.tenant_id:
            raise ValueError("Entity does not belong to this tenant")
        return await super().update(entity)

    async def delete(self, id: UUID) -> bool:
        entity = await self.get(id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
            return True
        return False

    async def soft_delete(self, id: UUID) -> bool:
        entity = await self.get(id)
        if entity and not entity.is_deleted:
            entity.mark_deleted()
            await self.session.flush()
            return True
        return False

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        order_by: list[tuple[str, str]] | None = None,
    ) -> list[T]:
        query = select(self.model_class).where(
            self.model_class.tenant_id == self.tenant_id,
            self.model_class.deleted_at.is_(None),
        )

        if filters:
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    attr = getattr(self.model_class, key)
                    if isinstance(value, list):
                        query = query.where(attr.in_(value))
                    else:
                        query = query.where(attr == value)

        if order_by:
            for field, direction in order_by:
                if hasattr(self.model_class, field):
                    attr = getattr(self.model_class, field)
                    query = query.order_by(attr.desc() if direction.lower() == "desc" else attr.asc())

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        query = select(func.count()).select_from(self.model_class).where(
            self.model_class.tenant_id == self.tenant_id,
            self.model_class.deleted_at.is_(None),
        )

        if filters:
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    attr = getattr(self.model_class, key)
                    if isinstance(value, list):
                        query = query.where(attr.in_(value))
                    else:
                        query = query.where(attr == value)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def exists(self, id: UUID) -> bool:
        query = select(func.count()).select_from(self.model_class).where(
            self.model_class.id == id,
            self.model_class.tenant_id == self.tenant_id,
            self.model_class.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return (result.scalar() or 0) > 0

    async def get_by_tenant(
        self,
        tenant_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        order_by: list[tuple[str, str]] | None = None,
    ) -> list[T]:
        if tenant_id != self.tenant_id:
            raise ValueError("Tenant ID mismatch")
        return await self.list(offset=offset, limit=limit, filters=filters, order_by=order_by)

    async def count_by_tenant(self, tenant_id: UUID, filters: dict[str, Any] | None = None) -> int:
        if tenant_id != self.tenant_id:
            raise ValueError("Tenant ID mismatch")
        return await self.count(filters)

    async def exists_in_tenant(self, tenant_id: UUID, id: UUID) -> bool:
        if tenant_id != self.tenant_id:
            raise ValueError("Tenant ID mismatch")
        return await self.exists(id)