from __future__ import annotations
from functools import lru_cache
from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import db, get_db
from app.core.security import decode_token, TokenPayload
from app.domain.base import Permission
from app.modules.auth.domain.repositories import (
    UserRepository,
    TenantRepository,
    UserSessionRepository,
    APIKeyRepository,
    RoleRepository,
    AuditLogRepository,
)
from app.modules.auth.infrastructure.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyTenantRepository,
    SQLAlchemyUserSessionRepository,
    SQLAlchemyAPIKeyRepository,
    SQLAlchemyRoleRepository,
    SQLAlchemyAuditLogRepository,
)
from app.modules.auth.application.commands import (
    RegisterTenantHandler,
    LoginHandler,
    RefreshTokenHandler,
    LogoutHandler,
    ChangePasswordHandler,
    RequestPasswordResetHandler,
    ResetPasswordHandler,
    VerifyEmailHandler,
    EnableMFAHandler,
    VerifyMFAHandler,
    DisableMFAHandler,
    CreateAPIKeyHandler,
    RevokeAPIKeyHandler,
)
from app.modules.auth.application.queries import (
    GetCurrentUserHandler,
    GetUserHandler,
    ListUsersHandler,
    GetTenantHandler,
    ListSessionsHandler,
    ListAPIKeysHandler,
    ListRolesHandler,
    GetAuditLogsHandler,
)
from app.application.base import CommandBus, QueryBus, MessageBus


async def get_tenant_id_from_header(x_tenant_id: Annotated[str | None, Header()] = None) -> UUID | None:
    if x_tenant_id:
        try:
            return UUID(x_tenant_id)
        except ValueError:
            pass
    return None


async def get_current_token_payload(
    credentials: Annotated[str, Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", ""))],
) -> TokenPayload:
    if not credentials or credentials == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_token(credentials)


async def get_current_user(
    payload: Annotated[TokenPayload, Depends(get_current_token_payload)],
    session: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
) -> dict:
    if tenant_id and str(tenant_id) != payload.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant access denied",
        )
    
    user_repo = SQLAlchemyUserRepository(session, UUID(payload.tenant_id))
    user = await user_repo.get_by_id(UUID(payload.sub))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "user_id": UUID(payload.sub),
        "tenant_id": UUID(payload.tenant_id),
        "email": payload.email,
        "roles": payload.roles,
        "permissions": payload.permissions,
    }


async def get_current_tenant(
    payload: Annotated[TokenPayload, Depends(get_current_token_payload)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    tenant_repo = SQLAlchemyTenantRepository(session)
    tenant = await tenant_repo.get_by_id(UUID(payload.tenant_id))
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    return {
        "tenant_id": tenant.id,
        "name": tenant.name,
        "slug": tenant.slug,
        "is_active": tenant.is_active,
    }


def get_user_id(user: Annotated[dict, Depends(get_current_user)]) -> UUID:
    return user["user_id"]


def get_tenant_id(user: Annotated[dict, Depends(get_current_user)]) -> UUID:
    return user["tenant_id"]


def require_permission(permission: Permission):
    def dependency(user: Annotated[dict, Depends(get_current_user)]) -> None:
        if permission.value not in user["permissions"] and "admin" not in user["roles"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}",
            )
    return dependency


def require_any_permission(*permissions: Permission):
    def dependency(user: Annotated[dict, Depends(get_current_user)]) -> None:
        user_perms = set(user["permissions"])
        required_perms = {p.value for p in permissions}
        if not (user_perms & required_perms) and "admin" not in user["roles"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join(required_perms)}",
            )
    return dependency


def require_role(*roles: str):
    def dependency(user: Annotated[dict, Depends(get_current_user)]) -> None:
        if not any(r in user["roles"] for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {', '.join(roles)}",
            )
    return dependency


class CommandBusImpl(CommandBus):
    def __init__(self):
        self._handlers: dict[type, object] = {}
    
    def register(self, command_type: type, handler: object) -> None:
        self._handlers[command_type] = handler
    
    async def dispatch(self, command: object) -> object:
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for {type(command).__name__}")
        return await handler.handle(command)


class QueryBusImpl(QueryBus):
    def __init__(self):
        self._handlers: dict[type, object] = {}
    
    def register(self, query_type: type, handler: object) -> None:
        self._handlers[query_type] = handler
    
    async def dispatch(self, query: object) -> object:
        handler = self._handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for {type(query).__name__}")
        return await handler.handle(query)


class MessageBusImpl(MessageBus):
    def __init__(self, command_bus: CommandBus, query_bus: QueryBus):
        self._command_bus = command_bus
        self._query_bus = query_bus
    
    async def dispatch_command(self, command: object) -> object:
        return await self._command_bus.dispatch(command)
    
    async def dispatch_query(self, query: object) -> object:
        return await self._query_bus.dispatch(query)


_command_bus = CommandBusImpl()
_query_bus = QueryBusImpl()
_message_bus = MessageBusImpl(_command_bus, _query_bus)


def get_command_bus() -> CommandBus:
    return _command_bus


def get_query_bus() -> QueryBus:
    return _query_bus


def get_message_bus() -> MessageBus:
    return _message_bus


@lru_cache
def get_user_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    tenant_id = UUID("00000000-0000-0000-0000-000000000000")
    return SQLAlchemyUserRepository(session, tenant_id)


@lru_cache
def get_tenant_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> TenantRepository:
    return SQLAlchemyTenantRepository(session)


@lru_cache
def get_user_session_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
) -> UserSessionRepository:
    return SQLAlchemyUserSessionRepository(session, tenant_id)


@lru_cache
def get_api_key_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
) -> APIKeyRepository:
    return SQLAlchemyAPIKeyRepository(session, tenant_id)


@lru_cache
def get_role_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
) -> RoleRepository:
    return SQLAlchemyRoleRepository(session, tenant_id)


@lru_cache
def get_audit_log_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> AuditLogRepository:
    return SQLAlchemyAuditLogRepository(session)


def register_auth_handlers(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    tenant_repo: Annotated[TenantRepository, Depends(get_tenant_repository)],
    session_repo: Annotated[UserSessionRepository, Depends(get_user_session_repository)],
    api_key_repo: Annotated[APIKeyRepository, Depends(get_api_key_repository)],
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
    audit_log_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
    command_bus: Annotated[CommandBus, Depends(get_command_bus)],
    query_bus: Annotated[QueryBus, Depends(get_query_bus)],
) -> None:
    command_bus.register(RegisterTenantCommand, RegisterTenantHandler(tenant_repo, user_repo, role_repo))
    command_bus.register(LoginCommand, LoginHandler(user_repo, tenant_repo, session_repo))
    command_bus.register(RefreshTokenCommand, RefreshTokenHandler(user_repo, session_repo))
    command_bus.register(LogoutCommand, LogoutHandler(session_repo))
    command_bus.register(ChangePasswordCommand, ChangePasswordHandler(user_repo))
    command_bus.register(RequestPasswordResetCommand, RequestPasswordResetHandler(user_repo, tenant_repo))
    command_bus.register(ResetPasswordCommand, ResetPasswordHandler(user_repo))
    command_bus.register(VerifyEmailCommand, VerifyEmailHandler(user_repo))
    command_bus.register(EnableMFACommand, EnableMFAHandler(user_repo))
    command_bus.register(VerifyMFACommand, VerifyMFAHandler(user_repo))
    command_bus.register(DisableMFACommand, DisableMFAHandler(user_repo))
    command_bus.register(CreateAPIKeyCommand, CreateAPIKeyHandler(api_key_repo, user_repo))
    command_bus.register(RevokeAPIKeyCommand, RevokeAPIKeyHandler(api_key_repo))
    
    query_bus.register(GetCurrentUserQuery, GetCurrentUserHandler(user_repo))
    query_bus.register(GetUserQuery, GetUserHandler(user_repo))
    query_bus.register(ListUsersQuery, ListUsersHandler(user_repo))
    query_bus.register(GetTenantQuery, GetTenantHandler(tenant_repo))
    query_bus.register(ListSessionsQuery, ListSessionsHandler(session_repo))
    query_bus.register(ListAPIKeysQuery, ListAPIKeysHandler(api_key_repo))
    query_bus.register(ListRolesQuery, ListRolesHandler(role_repo))
    query_bus.register(GetAuditLogsQuery, GetAuditLogsHandler(audit_log_repo))