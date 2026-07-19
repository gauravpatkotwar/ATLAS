from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.application.base import Query, QueryHandler
from app.modules.auth.domain.entities import User, Tenant, UserSession, APIKey, Role, UserStatus, UserRole
from app.modules.auth.domain.repositories import (
    UserRepository,
    TenantRepository,
    UserSessionRepository,
    APIKeyRepository,
    RoleRepository,
    AuditLogRepository,
)
from app.core.exceptions import NotFoundException, AuthorizationException


class GetCurrentUserQuery(Query):
    pass


class CurrentUserResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    email: str
    first_name: str
    last_name: str
    display_name: str | None
    avatar_url: str | None
    phone: str | None
    status: UserStatus
    roles: list[UserRole]
    permissions: list[str]
    mfa_enabled: bool
    last_login_at: datetime | None
    timezone: str
    locale: str
    created_at: datetime


class GetCurrentUserHandler(QueryHandler[GetCurrentUserQuery, CurrentUserResult]):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def handle(self, query: GetCurrentUserQuery) -> CurrentUserResult:
        user = await self.user_repo.get_by_id(query.__user_id__)
        if not user:
            raise NotFoundException("User", query.__user_id__)

        return CurrentUserResult(
            id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            phone=user.phone,
            status=user.status,
            roles=user.roles,
            permissions=[p.value for p in user.get_all_permissions()],
            mfa_enabled=user.mfa_enabled,
            last_login_at=user.last_login_at,
            timezone=user.timezone,
            locale=user.locale,
            created_at=user.created_at,
        )


class GetUserQuery(Query):
    user_id: UUID


class UserResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    email: str
    first_name: str
    last_name: str
    display_name: str | None
    avatar_url: str | None
    phone: str | None
    status: UserStatus
    roles: list[UserRole]
    permissions: list[str]
    mfa_enabled: bool
    email_verified: bool
    phone_verified: bool
    last_login_at: datetime | None
    last_login_ip: str | None
    timezone: str
    locale: str
    created_at: datetime
    updated_at: datetime


class GetUserHandler(QueryHandler[GetUserQuery, UserResult]):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def handle(self, query: GetUserQuery) -> UserResult:
        user = await self.user_repo.get_by_id(query.user_id)
        if not user:
            raise NotFoundException("User", query.user_id)

        if str(user.tenant_id) != query.__tenant_id__:
            raise AuthorizationException("Cannot access user from different tenant")

        return UserResult(
            id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            phone=user.phone,
            status=user.status,
            roles=user.roles,
            permissions=[p.value for p in user.get_all_permissions()],
            mfa_enabled=user.mfa_enabled,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified,
            last_login_at=user.last_login_at,
            last_login_ip=user.last_login_ip,
            timezone=user.timezone,
            locale=user.locale,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class ListUsersQuery(Query):
    page: int = 1
    page_size: int = 50
    search: str | None = None
    status: UserStatus | None = None
    roles: list[UserRole] | None = None


class ListUsersResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[UserResult]
    total: int
    page: int
    page_size: int
    total_pages: int


class ListUsersHandler(QueryHandler[ListUsersQuery, ListUsersResult]):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def handle(self, query: ListUsersQuery) -> ListUsersResult:
        users = await self.user_repo.search(
            tenant_id=UUID(query.__tenant_id__),
            query=query.search,
            status=query.status,
            roles=query.roles,
            limit=query.page_size,
            offset=(query.page - 1) * query.page_size,
        )
        total = await self.user_repo.count_search(
            tenant_id=UUID(query.__tenant_id__),
            query=query.search,
            status=query.status,
            roles=query.roles,
        )

        return ListUsersResult(
            items=[
                UserResult(
                    id=u.id,
                    tenant_id=u.tenant_id,
                    email=u.email,
                    first_name=u.first_name,
                    last_name=u.last_name,
                    display_name=u.display_name,
                    avatar_url=u.avatar_url,
                    phone=u.phone,
                    status=u.status,
                    roles=u.roles,
                    permissions=[p.value for p in u.get_all_permissions()],
                    mfa_enabled=u.mfa_enabled,
                    email_verified=u.email_verified,
                    phone_verified=u.phone_verified,
                    last_login_at=u.last_login_at,
                    last_login_ip=u.last_login_ip,
                    timezone=u.timezone,
                    locale=u.locale,
                    created_at=u.created_at,
                    updated_at=u.updated_at,
                )
                for u in users
            ],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=(total + query.page_size - 1) // query.page_size,
        )


class GetTenantQuery(Query):
    tenant_id: UUID | None = None


class TenantResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    domain: str | None
    logo_url: str | None
    primary_color: str
    secondary_color: str
    favicon_url: str | None
    subscription_plan: str
    subscription_status: str
    max_users: int
    max_jobs: int
    max_candidates: int
    is_active: bool
    is_trial: bool
    trial_ends_at: datetime | None
    settings: dict[str, Any]
    features: dict[str, bool]
    created_at: datetime


class GetTenantHandler(QueryHandler[GetTenantQuery, TenantResult]):
    def __init__(self, tenant_repo: TenantRepository):
        self.tenant_repo = tenant_repo

    async def handle(self, query: GetTenantQuery) -> TenantResult:
        tenant_id = query.tenant_id or UUID(query.__tenant_id__)
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise NotFoundException("Tenant", tenant_id)

        return TenantResult(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            domain=tenant.domain,
            logo_url=tenant.logo_url,
            primary_color=tenant.primary_color,
            secondary_color=tenant.secondary_color,
            favicon_url=tenant.favicon_url,
            subscription_plan=tenant.subscription_plan,
            subscription_status=tenant.subscription_status,
            max_users=tenant.max_users,
            max_jobs=tenant.max_jobs,
            max_candidates=tenant.max_candidates,
            is_active=tenant.is_active,
            is_trial=tenant.is_trial,
            trial_ends_at=tenant.trial_ends_at,
            settings=tenant.settings,
            features=tenant.features,
            created_at=tenant.created_at,
        )


class ListSessionsQuery(Query):
    pass


class SessionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    device_info: str | None
    user_agent: str | None
    ip_address: str | None
    location: str | None
    expires_at: datetime
    last_activity_at: datetime
    revoked_at: datetime | None
    revoked_reason: str | None
    created_at: datetime


class ListSessionsHandler(QueryHandler[ListSessionsQuery, list[SessionResult]]):
    def __init__(self, session_repo: UserSessionRepository):
        self.session_repo = session_repo

    async def handle(self, query: ListSessionsQuery) -> list[SessionResult]:
        sessions = await self.session_repo.get_active_sessions(UUID(query.__user_id__))
        return [
            SessionResult(
                id=s.id,
                device_info=s.device_info,
                user_agent=s.user_agent,
                ip_address=s.ip_address,
                location=s.location,
                expires_at=s.expires_at,
                last_activity_at=s.last_activity_at,
                revoked_at=s.revoked_at,
                revoked_reason=s.revoked_reason,
                created_at=s.created_at,
            )
            for s in sessions
        ]


class ListAPIKeysQuery(Query):
    pass


class APIKeyResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    key_prefix: str
    permissions: list[str]
    rate_limit: int
    last_used_at: datetime | None
    last_used_ip: str | None
    expires_at: datetime | None
    revoked_at: datetime | None
    revoked_reason: str | None
    created_at: datetime


class ListAPIKeysHandler(QueryHandler[ListAPIKeysQuery, list[APIKeyResult]]):
    def __init__(self, api_key_repo: APIKeyRepository):
        self.api_key_repo = api_key_repo

    async def handle(self, query: ListAPIKeysQuery) -> list[APIKeyResult]:
        keys = await self.api_key_repo.get_active_by_user(UUID(query.__user_id__))
        return [
            APIKeyResult(
                id=k.id,
                name=k.name,
                key_prefix=k.key_prefix,
                permissions=[p.value for p in k.permissions],
                rate_limit=k.rate_limit,
                last_used_at=k.last_used_at,
                last_used_ip=k.last_used_ip,
                expires_at=k.expires_at,
                revoked_at=k.revoked_at,
                revoked_reason=k.revoked_reason,
                created_at=k.created_at,
            )
            for k in keys
        ]


class ListRolesQuery(Query):
    pass


class RoleResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    display_name: str
    description: str | None
    permissions: list[str]
    is_system: bool
    is_default: bool
    created_at: datetime


class ListRolesHandler(QueryHandler[ListRolesQuery, list[RoleResult]]):
    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo

    async def handle(self, query: ListRolesQuery) -> list[RoleResult]:
        roles = await self.role_repo.get_by_tenant(UUID(query.__tenant_id__))
        return [
            RoleResult(
                id=r.id,
                name=r.name,
                display_name=r.display_name,
                description=r.description,
                permissions=[p.value for p in r.permissions],
                is_system=r.is_system,
                is_default=r.is_default,
                created_at=r.created_at,
            )
            for r in roles
        ]


class GetAuditLogsQuery(Query):
    page: int = 1
    page_size: int = 50
    start_date: str | None = None
    end_date: str | None = None
    user_id: UUID | None = None
    action: str | None = None
    resource_type: str | None = None


class AuditLogResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID | None
    action: str
    resource_type: str
    resource_id: UUID | None
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    changed_fields: list[str]
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    metadata: dict[str, Any]
    created_at: datetime


class AuditLogsResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[AuditLogResult]
    total: int
    page: int
    page_size: int
    total_pages: int


class GetAuditLogsHandler(QueryHandler[GetAuditLogsQuery, AuditLogsResult]):
    def __init__(self, audit_log_repo: AuditLogRepository):
        self.audit_log_repo = audit_log_repo

    async def handle(self, query: GetAuditLogsQuery) -> AuditLogsResult:
        items = await self.audit_log_repo.get_by_tenant(
            tenant_id=UUID(query.__tenant_id__),
            limit=query.page_size,
            offset=(query.page - 1) * query.page_size,
            start_date=query.start_date,
            end_date=query.end_date,
            user_id=query.user_id,
            action=query.action,
            resource_type=query.resource_type,
        )
        total = await self.audit_log_repo.count_by_tenant(
            tenant_id=UUID(query.__tenant_id__),
            start_date=query.start_date,
            end_date=query.end_date,
            user_id=query.user_id,
            action=query.action,
            resource_type=query.resource_type,
        )

        return AuditLogsResult(
            items=[
                AuditLogResult(
                    id=item.id,
                    user_id=item.user_id,
                    action=item.action,
                    resource_type=item.resource_type,
                    resource_id=item.resource_id,
                    old_values=item.old_values,
                    new_values=item.new_values,
                    changed_fields=item.changed_fields,
                    ip_address=item.ip_address,
                    user_agent=item.user_agent,
                    request_id=item.request_id,
                    metadata=item.metadata,
                    created_at=item.created_at,
                )
                for item in items
            ],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=(total + query.page_size - 1) // query.page_size,
        )