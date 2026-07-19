from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.modules.auth.domain.entities import User, Tenant, UserSession, APIKey, Role, UserStatus, UserRole, Permission
from app.domain.base import Repository


class UserRepository(Repository[User], ABC):
    @abstractmethod
    async def get_by_email(self, tenant_id: UUID, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_email_global(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_tenant(self, tenant_id: UUID, limit: int = 50, offset: int = 0) -> list[User]:
        pass

    @abstractmethod
    async def count_by_tenant(self, tenant_id: UUID) -> int:
        pass

    @abstractmethod
    async def search(
        self,
        tenant_id: UUID,
        query: str | None = None,
        status: UserStatus | None = None,
        roles: list[UserRole] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        pass

    @abstractmethod
    async def count_search(
        self,
        tenant_id: UUID,
        query: str | None = None,
        status: UserStatus | None = None,
        roles: list[UserRole] | None = None,
    ) -> int:
        pass


class TenantRepository(Repository[Tenant], ABC):
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Tenant | None:
        pass

    @abstractmethod
    async def get_by_domain(self, domain: str) -> Tenant | None:
        pass

    @abstractmethod
    async def get_active_tenants(self, limit: int = 50, offset: int = 0) -> list[Tenant]:
        pass

    @abstractmethod
    async def count_active(self) -> int:
        pass


class UserSessionRepository(Repository[UserSession], ABC):
    @abstractmethod
    async def get_by_access_token_jti(self, jti: str) -> UserSession | None:
        pass

    @abstractmethod
    async def get_by_refresh_token_jti(self, jti: str) -> UserSession | None:
        pass

    @abstractmethod
    async def get_active_sessions(self, user_id: UUID) -> list[UserSession]:
        pass

    @abstractmethod
    async def revoke_all_user_sessions(self, user_id: UUID, reason: str = "revoked") -> int:
        pass

    @abstractmethod
    async def revoke_all_tenant_sessions(self, tenant_id: UUID, reason: str = "revoked") -> int:
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        pass


class APIKeyRepository(Repository[APIKey], ABC):
    @abstractmethod
    async def get_by_key_hash(self, key_hash: str) -> APIKey | None:
        pass

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[APIKey]:
        pass

    @abstractmethod
    async def get_active_by_user(self, user_id: UUID) -> list[APIKey]:
        pass


class RoleRepository(Repository[Role], ABC):
    @abstractmethod
    async def get_by_name(self, tenant_id: UUID, name: str) -> Role | None:
        pass

    @abstractmethod
    async def get_by_tenant(self, tenant_id: UUID, include_system: bool = True) -> list[Role]:
        pass

    @abstractmethod
    async def get_default_roles(self, tenant_id: UUID) -> list[Role]:
        pass


class AuditLogRepository(ABC):
    @abstractmethod
    async def add(self, audit_log: Any) -> None:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def count_by_tenant(
        self,
        tenant_id: UUID,
        start_date: str | None = None,
        end_date: str | None = None,
        user_id: UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> int:
        pass