from __future__ import annotations
from typing import Any
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.domain.repositories import SQLAlchemyTenantRepository
from app.modules.auth.domain.entities import User, Tenant, UserSession, APIKey, Role, UserStatus, UserRole
from app.modules.auth.domain.repositories import (
    UserRepository,
    TenantRepository,
    UserSessionRepository,
    APIKeyRepository,
    RoleRepository,
    AuditLogRepository,
)
from app.modules.auth.domain.events import UserRegistered, UserLoggedIn


class SQLAlchemyUserRepository(SQLAlchemyTenantRepository[User], UserRepository):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(session, User, tenant_id)

    async def get_by_email(self, tenant_id: UUID, email: str) -> User | None:
        query = select(User).where(
            User.tenant_id == tenant_id,
            User.email == email.lower(),
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_global(self, email: str) -> User | None:
        query = select(User).where(
            User.email == email.lower(),
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_tenant(
        self,
        tenant_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        return await self.list(limit=limit, offset=offset)

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        return await self.count()

    async def search(
        self,
        tenant_id: UUID,
        query: str | None = None,
        status: UserStatus | None = None,
        roles: list[UserRole] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        filters = {}
        if status:
            filters["status"] = status.value
        if roles:
            filters["roles"] = [r.value for r in roles]
        
        stmt = select(User).where(
            User.tenant_id == tenant_id,
            User.deleted_at.is_(None),
        )
        
        if query:
            search_term = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.display_name.ilike(search_term),
                )
            )
        
        if status:
            stmt = stmt.where(User.status == status.value)
        
        if roles:
            stmt = stmt.where(User.roles.overlap([r.value for r in roles]))
        
        stmt = stmt.offset(offset).limit(limit).order_by(User.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        tenant_id: UUID,
        query: str | None = None,
        status: UserStatus | None = None,
        roles: list[UserRole] | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(User).where(
            User.tenant_id == tenant_id,
            User.deleted_at.is_(None),
        )
        
        if query:
            search_term = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.display_name.ilike(search_term),
                )
            )
        
        if status:
            stmt = stmt.where(User.status == status.value)
        
        if roles:
            stmt = stmt.where(User.roles.overlap([r.value for r in roles]))
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_by_verification_token(self, token: str) -> User | None:
        query = select(User).where(
            User.email_verification_token == token,
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_password_reset_token(self, token: str) -> User | None:
        query = select(User).where(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.utcnow(),
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class SQLAlchemyTenantRepository(SQLAlchemyTenantRepository[Tenant], TenantRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Tenant, UUID("00000000-0000-0000-0000-000000000000"))

    async def get_by_slug(self, slug: str) -> Tenant | None:
        query = select(Tenant).where(
            Tenant.slug == slug,
            Tenant.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_domain(self, domain: str) -> Tenant | None:
        query = select(Tenant).where(
            Tenant.domain == domain,
            Tenant.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_active_tenants(self, limit: int = 50, offset: int = 0) -> list[Tenant]:
        query = select(Tenant).where(
            Tenant.is_active.is_(True),
            Tenant.deleted_at.is_(None),
        ).offset(offset).limit(limit).order_by(Tenant.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_active(self) -> int:
        query = select(func.count()).select_from(Tenant).where(
            Tenant.is_active.is_(True),
            Tenant.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar() or 0


class SQLAlchemyUserSessionRepository(SQLAlchemyTenantRepository[UserSession], UserSessionRepository):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(session, UserSession, tenant_id)

    async def get_by_access_token_jti(self, jti: str) -> UserSession | None:
        query = select(UserSession).where(
            UserSession.access_token_jti == jti,
            UserSession.revoked_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_refresh_token_jti(self, jti: str) -> UserSession | None:
        query = select(UserSession).where(
            UserSession.refresh_token_jti == jti,
            UserSession.revoked_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_active_sessions(self, user_id: UUID) -> list[UserSession]:
        query = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > datetime.utcnow(),
        ).order_by(UserSession.last_activity_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def revoke_all_user_sessions(self, user_id: UUID, reason: str = "revoked") -> int:
        query = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None),
        )
        result = await self.session.execute(query)
        sessions = result.scalars().all()
        count = 0
        for session in sessions:
            session.revoke(reason)
            count += 1
        await self.session.flush()
        return count

    async def revoke_all_tenant_sessions(self, tenant_id: UUID, reason: str = "revoked") -> int:
        query = select(UserSession).where(
            UserSession.tenant_id == tenant_id,
            UserSession.revoked_at.is_(None),
        )
        result = await self.session.execute(query)
        sessions = result.scalars().all()
        count = 0
        for session in sessions:
            session.revoke(reason)
            count += 1
        await self.session.flush()
        return count

    async def cleanup_expired(self) -> int:
        query = select(UserSession).where(
            UserSession.revoked_at.is_(None),
            UserSession.expires_at <= datetime.utcnow(),
        )
        result = await self.session.execute(query)
        sessions = result.scalars().all()
        count = 0
        for session in sessions:
            session.revoke("expired")
            count += 1
        await self.session.flush()
        return count


class SQLAlchemyAPIKeyRepository(SQLAlchemyTenantRepository[APIKey], APIKeyRepository):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(session, APIKey, tenant_id)

    async def get_by_key_hash(self, key_hash: str) -> APIKey | None:
        query = select(APIKey).where(
            APIKey.key_hash == key_hash,
            APIKey.revoked_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: UUID) -> list[APIKey]:
        query = select(APIKey).where(
            APIKey.user_id == user_id,
        ).order_by(APIKey.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_by_user(self, user_id: UUID) -> list[APIKey]:
        query = select(APIKey).where(
            APIKey.user_id == user_id,
            APIKey.revoked_at.is_(None),
            or_(
                APIKey.expires_at.is_(None),
                APIKey.expires_at > datetime.utcnow(),
            ),
        ).order_by(APIKey.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())


class SQLAlchemyRoleRepository(SQLAlchemyTenantRepository[Role], RoleRepository):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(session, Role, tenant_id)

    async def get_by_name(self, tenant_id: UUID, name: str) -> Role | None:
        query = select(Role).where(
            Role.tenant_id == tenant_id,
            Role.name == name,
            Role.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_tenant(self, tenant_id: UUID, include_system: bool = True) -> list[Role]:
        query = select(Role).where(
            Role.tenant_id == tenant_id,
            Role.deleted_at.is_(None),
        )
        if not include_system:
            query = query.where(Role.is_system.is_(False))
        query = query.order_by(Role.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_default_roles(self, tenant_id: UUID) -> list[Role]:
        query = select(Role).where(
            Role.tenant_id == tenant_id,
            Role.is_default.is_(True),
            Role.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class SQLAlchemyAuditLogRepository(AuditLogRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, audit_log: Any) -> None:
        self.session.add(audit_log)
        await self.session.flush()

    async def get_by_tenant(
        self,
        tenant_id: UUID,
        limit: int = 100,
        offset: int = 0,
        start_date: str | None = None,
        end_date: str | None = None,
        user_id: UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> list[Any]:
        from app.modules.auth.domain.entities import AuditLog
        
        query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
        
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        
        query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_tenant(
        self,
        tenant_id: UUID,
        start_date: str | None = None,
        end_date: str | None = None,
        user_id: UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> int:
        from app.modules.auth.domain.entities import AuditLog
        
        query = select(func.count()).select_from(AuditLog).where(AuditLog.tenant_id == tenant_id)
        
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        
        result = await self.session.execute(query)
        return result.scalar() or 0