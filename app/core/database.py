from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData, event
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(self) -> str:
        attrs = []
        for col in self.__table__.columns:
            if col.primary_key:
                attrs.append(f"{col.name}={getattr(self, col.name)}")
        return f"<{self.__class__.__name__}({', '.join(attrs)})>"


class AsyncDatabase:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(
                settings.database.async_url,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                pool_timeout=settings.database.pool_timeout,
                pool_recycle=settings.database.pool_recycle,
                pool_pre_ping=True,
                echo=settings.database.echo,
                poolclass=NullPool if settings.environment == "testing" else None,
            )
            self._setup_event_listeners()
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
        return self._session_factory

    def _setup_event_listeners(self) -> None:
        @event.listens_for(self.engine.sync_engine, "connect")
        def set_postgres_search_path(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute(f"SET search_path TO {settings.database.name}, public")
            cursor.close()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_all(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


db = AsyncDatabase()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db.session() as session:
        yield session


async def init_db() -> None:
    logger.info("Initializing database connection")
    await db.create_all()
    logger.info("Database initialized")


async def close_db() -> None:
    logger.info("Closing database connection")
    await db.close()
    logger.info("Database connection closed")


class TenantMixin:
    @declared_attr.directive
    def tenant_id(cls):
        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import Mapped, mapped_column
        from sqlalchemy.dialects.postgresql import UUID
        import uuid

        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )

    @declared_attr.directive
    def tenant(cls):
        from sqlalchemy.orm import relationship
        return relationship("Tenant", lazy="raise")


class TimestampMixin:
    @declared_attr.directive
    def created_at(cls):
        from sqlalchemy import DateTime, func
        from sqlalchemy.orm import Mapped, mapped_column

        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr.directive
    def updated_at(cls):
        from sqlalchemy import DateTime, func
        from sqlalchemy.orm import Mapped, mapped_column

        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )


class SoftDeleteMixin:
    @declared_attr.directive
    def deleted_at(cls):
        from sqlalchemy import DateTime
        from sqlalchemy.orm import Mapped, mapped_column

        return mapped_column(DateTime(timezone=True), nullable=True, default=None, index=True)

    @declared_attr.directive
    def is_deleted(cls):
        from sqlalchemy import Boolean
        from sqlalchemy.orm import Mapped, mapped_column

        return mapped_column(Boolean, default=False, nullable=False, index=True)


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    __abstract__ = True

    @declared_attr.directive
    def id(cls):
        from sqlalchemy import String
        from sqlalchemy.orm import Mapped, mapped_column
        import uuid

        return mapped_column(
            String(36),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
        )


class TenantBaseModel(BaseModel, TenantMixin):
    __abstract__ = True