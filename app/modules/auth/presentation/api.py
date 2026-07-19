from __future__ import annotations
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.api.dependencies import (
    get_current_user,
    get_current_tenant,
    get_user_id,
    get_tenant_id,
    require_permission,
)
from app.application.base import message_bus
from app.modules.auth.application.commands import (
    LoginCommand,
    RegisterTenantCommand,
    RefreshTokenCommand,
    LogoutCommand,
    ChangePasswordCommand,
    RequestPasswordResetCommand,
    ResetPasswordCommand,
    VerifyEmailCommand,
    EnableMFACommand,
    VerifyMFACommand,
    DisableMFACommand,
    CreateAPIKeyCommand,
    RevokeAPIKeyCommand,
)
from app.modules.auth.application.queries import (
    GetCurrentUserQuery,
    GetUserQuery,
    ListUsersQuery,
    GetTenantQuery,
    ListSessionsQuery,
    ListAPIKeysQuery,
    ListRolesQuery,
    GetAuditLogsQuery,
)
from app.domain.base import Permission


router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterTenantRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$")
    domain: str | None = Field(None, pattern=r"^[a-z0-9.-]+$")
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=12)
    admin_first_name: str = Field(..., min_length=1, max_length=100)
    admin_last_name: str = Field(..., min_length=1, max_length=100)
    subscription_plan: str = "free"


class LoginRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    password: str
    tenant_slug: str | None = None
    mfa_code: str | None = None
    remember_me: bool = False
    device_info: str | None = None


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    refresh_token: str
    device_info: str | None = None


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    current_password: str
    new_password: str = Field(..., min_length=12)


class RequestPasswordResetRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    tenant_slug: str | None = None


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token: str
    new_password: str = Field(..., min_length=12)


class VerifyEmailRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token: str


class CreateAPIKeyRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., min_length=1, max_length=100)
    permissions: list[str] = Field(default_factory=list)
    rate_limit: int = Field(default=1000, ge=1, le=10000)
    expires_in_days: int | None = Field(None, ge=1, le=365)


class RevokeAPIKeyRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    api_key_id: UUID
    reason: str = "revoked"


class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    tenant_id: UUID
    email: str
    first_name: str
    last_name: str
    roles: list[str]
    permissions: list[str]
    access_token: str
    refresh_token: str
    expires_in: int
    mfa_required: bool = False


class EnableMFAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    secret: str
    qr_code: str
    backup_codes: list[str]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    email: str
    first_name: str
    last_name: str
    display_name: str | None
    avatar_url: str | None
    phone: str | None
    status: str
    roles: list[str]
    permissions: list[str]
    mfa_enabled: bool
    email_verified: bool
    phone_verified: bool
    last_login_at: str | None
    last_login_ip: str | None
    timezone: str
    locale: str
    created_at: str


class TenantResponse(BaseModel):
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
    trial_ends_at: str | None
    settings: dict
    features: dict
    created_at: str


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    device_info: str | None
    user_agent: str | None
    ip_address: str | None
    location: str | None
    expires_at: str
    last_activity_at: str
    revoked_at: str | None
    revoked_reason: str | None
    created_at: str


class APIKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    key_prefix: str
    permissions: list[str]
    rate_limit: int
    last_used_at: str | None
    last_used_ip: str | None
    expires_at: str | None
    revoked_at: str | None
    revoked_reason: str | None
    created_at: str


class CreateAPIKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    key: str
    key_prefix: str
    permissions: list[str]
    expires_at: str | None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    display_name: str
    description: str | None
    permissions: list[str]
    is_system: bool
    is_default: bool
    created_at: str


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID | None
    action: str
    resource_type: str
    resource_id: UUID | None
    old_values: dict | None
    new_values: dict | None
    changed_fields: list[str]
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    metadata: dict
    created_at: str


class PaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register_tenant(request: RegisterTenantRequest):
    command = RegisterTenantCommand(
        name=request.name,
        slug=request.slug,
        domain=request.domain,
        admin_email=request.admin_email,
        admin_password=request.admin_password,
        admin_first_name=request.admin_first_name,
        admin_last_name=request.admin_last_name,
        subscription_plan=request.subscription_plan,
    )
    result = await message_bus.dispatch_command(command)
    return LoginResponse(
        user_id=result.user_id,
        tenant_id=result.tenant_id,
        email=request.admin_email,
        first_name=request.admin_first_name,
        last_name=request.admin_last_name,
        roles=["admin"],
        permissions=[p.value for p in Permission],
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: Request, credentials: LoginRequest):
    command = LoginCommand(
        email=credentials.email,
        password=credentials.password,
        tenant_slug=credentials.tenant_slug,
        mfa_code=credentials.mfa_code,
        remember_me=credentials.remember_me,
        device_info=credentials.device_info,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    result = await message_bus.dispatch_command(command)
    
    if result.mfa_required:
        return LoginResponse(
            user_id=result.user_id,
            tenant_id=result.tenant_id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            roles=result.roles,
            permissions=result.permissions,
            access_token="",
            refresh_token="",
            expires_in=0,
            mfa_required=True,
        )
    
    return result


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: Request, credentials: RefreshTokenRequest):
    command = RefreshTokenCommand(
        refresh_token=credentials.refresh_token,
        device_info=credentials.device_info,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    result = await message_bus.dispatch_command(command)
    return result


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, revoke_all: bool = False):
    from app.core.security import decode_token
    from jose import jwt
    
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    
    command = LogoutCommand(
        access_token_jti=payload.jti,
        revoke_all_sessions=revoke_all,
    )
    await message_bus.dispatch_command(command)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user_id: Annotated[UUID, Depends(get_user_id)],
    request: ChangePasswordRequest,
):
    command = ChangePasswordCommand(
        current_password=request.current_password,
        new_password=request.new_password,
    )
    command.__user_id__ = user_id
    await message_bus.dispatch_command(command)


@router.post("/password/reset/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(request: RequestPasswordResetRequest):
    command = RequestPasswordResetCommand(
        email=request.email,
        tenant_slug=request.tenant_slug,
    )
    await message_bus.dispatch_command(command)


@router.post("/password/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(request: ResetPasswordRequest):
    command = ResetPasswordCommand(
        token=request.token,
        new_password=request.new_password,
    )
    await message_bus.dispatch_command(command)


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(request: VerifyEmailRequest):
    command = VerifyEmailCommand(token=request.token)
    await message_bus.dispatch_command(command)


@router.post("/mfa/enable", response_model=EnableMFAResponse)
async def enable_mfa(user_id: Annotated[UUID, Depends(get_user_id)]):
    command = EnableMFACommand()
    command.__user_id__ = user_id
    result = await message_bus.dispatch_command(command)
    return result


@router.post("/mfa/verify", status_code=status.HTTP_204_NO_CONTENT)
async def verify_mfa(
    user_id: Annotated[UUID, Depends(get_user_id)],
    code: str,
):
    command = VerifyMFACommand(code=code)
    command.__user_id__ = user_id
    await message_bus.dispatch_command(command)


@router.post("/mfa/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_mfa(
    user_id: Annotated[UUID, Depends(get_user_id)],
    password: str,
):
    command = DisableMFACommand(password=password)
    command.__user_id__ = user_id
    await message_bus.dispatch_command(command)


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: Annotated[UUID, Depends(get_user_id)]):
    query = GetCurrentUserQuery()
    query.__user_id__ = user_id
    result = await message_bus.dispatch_query(query)
    return result


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    _: Annotated[None, Depends(require_permission(Permission.USERS_READ))],
):
    query = GetUserQuery(user_id=user_id)
    query.__tenant_id__ = str(tenant_id)
    result = await message_bus.dispatch_query(query)
    return result


@router.get("/users", response_model=PaginatedResponse)
async def list_users(
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    status: str | None = None,
    roles: list[str] | None = None,
    _: Annotated[None, Depends(require_permission(Permission.USERS_READ))],
):
    query = ListUsersQuery(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        roles=roles,
    )
    query.__tenant_id__ = str(tenant_id)
    result = await message_bus.dispatch_query(query)
    return result


@router.get("/tenant", response_model=TenantResponse)
async def get_tenant(tenant_id: Annotated[UUID, Depends(get_tenant_id)]):
    query = GetTenantQuery()
    query.__tenant_id__ = str(tenant_id)
    result = await message_bus.dispatch_query(query)
    return result


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(user_id: Annotated[UUID, Depends(get_user_id)]):
    query = ListSessionsQuery()
    query.__user_id__ = user_id
    result = await message_bus.dispatch_query(query)
    return result


@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(user_id: Annotated[UUID, Depends(get_user_id)]):
    query = ListAPIKeysQuery()
    query.__user_id__ = user_id
    result = await message_bus.dispatch_query(query)
    return result


@router.post("/api-keys", response_model=CreateAPIKeyResponse)
async def create_api_key(
    user_id: Annotated[UUID, Depends(get_user_id)],
    request: CreateAPIKeyRequest,
    _: Annotated[None, Depends(require_permission(Permission.API_ACCESS))],
):
    command = CreateAPIKeyCommand(
        name=request.name,
        permissions=[Permission(p) for p in request.permissions],
        rate_limit=request.rate_limit,
        expires_in_days=request.expires_in_days,
    )
    command.__user_id__ = user_id
    result = await message_bus.dispatch_command(command)
    return result


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    api_key_id: UUID,
    user_id: Annotated[UUID, Depends(get_user_id)],
    request: RevokeAPIKeyRequest | None = None,
    _: Annotated[None, Depends(require_permission(Permission.API_ACCESS))],
):
    reason = request.reason if request else "revoked"
    command = RevokeAPIKeyCommand(api_key_id=api_key_id, reason=reason)
    command.__user_id__ = user_id
    await message_bus.dispatch_command(command)


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    _: Annotated[None, Depends(require_permission(Permission.USERS_MANAGE_ROLES))],
):
    query = ListRolesQuery()
    query.__tenant_id__ = str(tenant_id)
    result = await message_bus.dispatch_query(query)
    return result


@router.get("/audit-logs", response_model=PaginatedResponse)
async def get_audit_logs(
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    page: int = 1,
    page_size: int = 50,
    start_date: str | None = None,
    end_date: str | None = None,
    user_id: UUID | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    _: Annotated[None, Depends(require_permission(Permission.ADMIN_AUDIT_LOGS))],
):
    query = GetAuditLogsQuery(
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
    )
    query.__tenant_id__ = str(tenant_id)
    result = await message_bus.dispatch_query(query)
    return result