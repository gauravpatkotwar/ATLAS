from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.application.base import Command, Query, CommandHandler, QueryHandler
from app.core.security import create_token_pair, verify_password, get_password_hash
from app.modules.auth.domain.entities import User, Tenant, UserSession, APIKey, Role, UserStatus, UserRole, Permission
from app.modules.auth.domain.repositories import (
    UserRepository,
    TenantRepository,
    UserSessionRepository,
    APIKeyRepository,
    RoleRepository,
)
from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    ValidationException,
    BusinessRuleException,
    TenantNotFoundException,
    UserNotFoundException,
)


class RegisterTenantCommand(Command):
    name: str
    slug: str
    domain: str | None = None
    admin_email: EmailStr
    admin_password: str
    admin_first_name: str
    admin_last_name: str
    subscription_plan: str = "free"


class RegisterTenantResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tenant_id: UUID
    user_id: UUID
    access_token: str
    refresh_token: str


class RegisterTenantHandler(CommandHandler[RegisterTenantCommand, RegisterTenantResult]):
    def __init__(
        self,
        tenant_repo: TenantRepository,
        user_repo: UserRepository,
        role_repo: RoleRepository,
    ):
        self.tenant_repo = tenant_repo
        self.user_repo = user_repo
        self.role_repo = role_repo

    async def handle(self, command: RegisterTenantCommand) -> RegisterTenantResult:
        existing_tenant = await self.tenant_repo.get_by_slug(command.slug)
        if existing_tenant:
            raise ConflictException(f"Tenant with slug '{command.slug}' already exists")

        if command.domain:
            existing_domain = await self.tenant_repo.get_by_domain(command.domain)
            if existing_domain:
                raise ConflictException(f"Tenant with domain '{command.domain}' already exists")

        admin_user = await self.user_repo.get_by_email_global(command.admin_email)
        if admin_user:
            raise ConflictException(f"User with email '{command.admin_email}' already exists")

        tenant = Tenant(
            name=command.name,
            slug=command.slug,
            domain=command.domain,
            subscription_plan=command.subscription_plan,
        )
        await self.tenant_repo.add(tenant)

        admin_role = await self.role_repo.get_by_name(tenant.id, "admin")
        if not admin_role:
            admin_role = Role(
                tenant_id=tenant.id,
                name="admin",
                display_name="Administrator",
                description="Full access to all features",
                permissions=[p for p in Permission],
                is_system=True,
                is_default=False,
            )
            await self.role_repo.add(admin_role)

        user = User(
            tenant_id=tenant.id,
            email=command.admin_email,
            password_hash=get_password_hash(command.admin_password),
            first_name=command.admin_first_name,
            last_name=command.admin_last_name,
            status=UserStatus.ACTIVE,
            email_verified=True,
            roles=[UserRole.ADMIN],
        )
        await self.user_repo.add(user)

        token_pair = create_token_pair(
            subject=str(user.id),
            tenant_id=str(tenant.id),
            email=user.email,
            roles=[role.value for role in user.roles],
            permissions=[perm.value for role in user.roles for perm in role.get_permissions()],
        )

        return RegisterTenantResult(
            tenant_id=tenant.id,
            user_id=user.id,
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
        )


class LoginCommand(Command):
    email: EmailStr
    password: str
    tenant_slug: str | None = None
    mfa_code: str | None = None
    remember_me: bool = False
    device_info: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None


class LoginResult(BaseModel):
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


class LoginHandler(CommandHandler[LoginCommand, LoginResult]):
    def __init__(
        self,
        user_repo: UserRepository,
        tenant_repo: TenantRepository,
        session_repo: UserSessionRepository,
    ):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo
        self.session_repo = session_repo

    async def handle(self, command: LoginCommand) -> LoginResult:
        if command.tenant_slug:
            tenant = await self.tenant_repo.get_by_slug(command.tenant_slug)
            if not tenant:
                raise TenantNotFoundException(command.tenant_slug)
            if not tenant.is_active:
                raise BusinessRuleException(f"Tenant '{command.tenant_slug}' is inactive")
            user = await self.user_repo.get_by_email(tenant.id, command.email)
        else:
            user = await self.user_repo.get_by_email_global(command.email)

        if not user:
            raise AuthenticationException("Invalid credentials")

        if not user.tenant.is_active:
            raise BusinessRuleException("Tenant is inactive")

        if not verify_password(command.password, user.password_hash):
            user.record_failed_login()
            await self.user_repo.update(user)
            raise AuthenticationException("Invalid credentials")

        if user.is_locked:
            raise AuthenticationException("Account temporarily locked due to failed attempts")

        if user.status != UserStatus.ACTIVE:
            raise AuthenticationException("Account is not active")

        if user.mfa_enabled and not command.mfa_code:
            return LoginResult(
                user_id=user.id,
                tenant_id=user.tenant_id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                roles=[r.value for r in user.roles],
                permissions=[p.value for r in user.roles for p in r.get_permissions()],
                access_token="",
                refresh_token="",
                expires_in=0,
                mfa_required=True,
            )

        if user.mfa_enabled and command.mfa_code:
            if not user.verify_mfa_code(command.mfa_code):
                user.record_failed_login()
                await self.user_repo.update(user)
                raise AuthenticationException("Invalid MFA code")

        user.record_login(command.ip_address)
        await self.user_repo.update(user)

        token_pair = create_token_pair(
            subject=str(user.id),
            tenant_id=str(user.tenant_id),
            email=user.email,
            roles=[r.value for r in user.roles],
            permissions=[p.value for r in user.roles for p in r.get_permissions()],
        )

        session = UserSession(
            user_id=user.id,
            tenant_id=user.tenant_id,
            access_token_jti=token_pair.access_token.split(".")[0],
            refresh_token_jti=token_pair.refresh_token.split(".")[0],
            device_info=command.device_info,
            user_agent=command.user_agent,
            ip_address=command.ip_address,
            expires_at=datetime.utcnow() + timedelta(
                days=settings.auth.refresh_token_expire_days_remember if command.remember_me else settings.auth.refresh_token_expire_days
            ),
        )
        await self.session_repo.add(session)

        return LoginResult(
            user_id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=[r.value for r in user.roles],
            permissions=[p.value for r in user.roles for p in r.get_permissions()],
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            expires_in=token_pair.expires_in,
        )


class RefreshTokenCommand(Command):
    refresh_token: str
    device_info: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None


class RefreshTokenResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    refresh_token: str
    expires_in: int


class RefreshTokenHandler(CommandHandler[RefreshTokenCommand, RefreshTokenResult]):
    def __init__(
        self,
        user_repo: UserRepository,
        session_repo: UserSessionRepository,
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo

    async def handle(self, command: RefreshTokenCommand) -> RefreshTokenResult:
        from app.core.security import decode_token
        
        payload = decode_token(command.refresh_token)
        if payload.type != "refresh":
            raise AuthenticationException("Invalid token type")

        session = await self.session_repo.get_by_refresh_token_jti(payload.jti)
        if not session or not session.is_active:
            raise AuthenticationException("Invalid or expired refresh token")

        user = await self.user_repo.get_by_id(payload.sub)
        if not user or user.status != UserStatus.ACTIVE:
            raise AuthenticationException("User not found or inactive")

        session.last_activity_at = datetime.utcnow()
        session.ip_address = command.ip_address
        session.user_agent = command.user_agent
        await self.session_repo.update(session)

        token_pair = create_token_pair(
            subject=str(user.id),
            tenant_id=str(user.tenant_id),
            email=user.email,
            roles=[r.value for r in user.roles],
            permissions=[p.value for r in user.roles for p in r.get_permissions()],
        )

        session.access_token_jti = token_pair.access_token.split(".")[0]
        session.refresh_token_jti = token_pair.refresh_token.split(".")[0]
        await self.session_repo.update(session)

        return RefreshTokenResult(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            expires_in=token_pair.expires_in,
        )


class LogoutCommand(Command):
    access_token_jti: str
    revoke_all_sessions: bool = False


class LogoutHandler(CommandHandler[LogoutCommand, None]):
    def __init__(self, session_repo: UserSessionRepository):
        self.session_repo = session_repo

    async def handle(self, command: LogoutCommand) -> None:
        session = await self.session_repo.get_by_access_token_jti(command.access_token_jti)
        if session:
            session.revoke("logout")
            await self.session_repo.update(session)

        if command.revoke_all_sessions:
            await self.session_repo.revoke_all_user_sessions(session.user_id, "logout_all")


class ChangePasswordCommand(Command):
    current_password: str
    new_password: str


class ChangePasswordHandler(CommandHandler[ChangePasswordCommand, None]):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def handle(self, command: ChangePasswordCommand) -> None:
        user = await self.user_repo.get_by_id(command.__user_id__)
        if not user:
            raise UserNotFoundException(command.__user_id__)

        if not verify_password(command.current_password, user.password_hash):
            raise AuthenticationException("Current password is incorrect")

        user.change_password(get_password_hash(command.new_password))
        await self.user_repo.update(user)


class RequestPasswordResetCommand(Command):
    email: EmailStr
    tenant_slug: str | None = None


class RequestPasswordResetHandler(CommandHandler[RequestPasswordResetCommand, None]):
    def __init__(
        self,
        user_repo: UserRepository,
        tenant_repo: TenantRepository,
        email_service: Any,
    ):
        self.user_repo = user_repo
        self.tenant_repo = tenant_repo
        self.email_service = email_service

    async def handle(self, command: RequestPasswordResetCommand) -> None:
        if command.tenant_slug:
            tenant = await self.tenant_repo.get_by_slug(command.tenant_slug)
            if not tenant:
                raise TenantNotFoundException(command.tenant_slug)
            user = await self.user_repo.get_by_email(tenant.id, command.email)
        else:
            user = await self.user_repo.get_by_email_global(command.email)

        if user and user.status == UserStatus.ACTIVE:
            token = generate_password_reset_token()
            user.password_reset_token = token
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
            await self.user_repo.update(user)
            
            await self.email_service.send_password_reset(user.email, token, user.tenant_id)


class ResetPasswordCommand(Command):
    token: str
    new_password: str


class ResetPasswordHandler(CommandHandler[ResetPasswordCommand, None]):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def handle(self, command: ResetPasswordCommand) -> None:
        user = await self.user_repo.get_by_password_reset_token(command.token)
        if not user:
            raise ValidationException("Invalid or expired reset token")

        if user.password_reset_expires < datetime.utcnow():
            raise ValidationException("Reset token has expired")

        user.change_password(get_password_hash(command.new_password))
        user.password_reset_token = None
        user.password_reset_expires = None
        await self.user_repo.update(user)


class VerifyEmailCommand(Command):
    token: str


class VerifyEmailHandler(CommandHandler[VerifyEmailCommand, None]):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def handle(self, command: VerifyEmailCommand) -> None:
        user = await self.user_repo.get_by_verification_token(command.token)
        if not user:
            raise ValidationException("Invalid or expired verification token")

        user.verify_email()
        await self.user_repo.update(user)


class EnableMFACommand(Command):
    pass


class EnableMFAResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    secret: str
    qr_code: str
    backup_codes: list[str]


class EnableMFAHandler(CommandHandler[EnableMFACommand, EnableMFAResult]):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def handle(self, command: EnableMFACommand) -> EnableMFAResult:
        user = await self.user_repo.get_by_id(command.__user_id__)
        if not user:
            raise UserNotFoundException(command.__user_id__)

        import pyotp
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        qr_code = totp.provisioning_uri(user.email, issuer_name=settings.auth.mfa_issuer)
        backup_codes = [secrets.token_hex(8) for _ in range(10)]

        user.enable_mfa(secret)
        user.generate_backup_codes(backup_codes)
        await self.user_repo.update(user)

        return EnableMFAResult(secret=secret, qr_code=qr_code, backup_codes=backup_codes)


class VerifyMFACommand(Command):
    code: str


class VerifyMFAHandler(CommandHandler[VerifyMFACommand, None]):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def handle(self, command: VerifyMFACommand) -> None:
        user = await self.user_repo.get_by_id(command.__user_id__)
        if not user:
            raise UserNotFoundException(command.__user_id__)

        if not user.mfa_enabled:
            raise BusinessRuleException("MFA is not enabled")

        if not user.verify_mfa_code(command.code):
            raise AuthenticationException("Invalid MFA code")


class DisableMFACommand(Command):
    password: str


class DisableMFAHandler(CommandHandler[DisableMFACommand, None]):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def handle(self, command: DisableMFACommand) -> None:
        user = await self.user_repo.get_by_id(command.__user_id__)
        if not user:
            raise UserNotFoundException(command.__user_id__)

        if not verify_password(command.password, user.password_hash):
            raise AuthenticationException("Invalid password")

        user.disable_mfa()
        await self.user_repo.update(user)


class CreateAPIKeyCommand(Command):
    name: str
    permissions: list[Permission]
    rate_limit: int = 1000
    expires_in_days: int | None = None


class CreateAPIKeyResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    key: str
    key_prefix: str
    permissions: list[Permission]
    expires_at: datetime | None


class CreateAPIKeyHandler(CommandHandler[CreateAPIKeyCommand, CreateAPIKeyResult]):
    def __init__(
        self,
        api_key_repo: APIKeyRepository,
        user_repo: UserRepository,
    ):
        self.api_key_repo = api_key_repo
        self.user_repo = user_repo

    async def handle(self, command: CreateAPIKeyCommand) -> CreateAPIKeyResult:
        user = await self.user_repo.get_by_id(command.__user_id__)
        if not user:
            raise UserNotFoundException(command.__user_id__)

        from app.core.security import generate_api_key, hash_api_key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        key_prefix = api_key[:20]

        expires_at = None
        if command.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=command.expires_in_days)

        api_key_obj = APIKey(
            user_id=user.id,
            tenant_id=user.tenant_id,
            name=command.name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            permissions=command.permissions,
            rate_limit=command.rate_limit,
            expires_at=expires_at,
        )
        await self.api_key_repo.add(api_key_obj)

        return CreateAPIKeyResult(
            id=api_key_obj.id,
            name=api_key_obj.name,
            key=api_key,
            key_prefix=key_prefix,
            permissions=api_key_obj.permissions,
            expires_at=api_key_obj.expires_at,
        )


class RevokeAPIKeyCommand(Command):
    api_key_id: UUID
    reason: str = "revoked"


class RevokeAPIKeyHandler(CommandHandler[RevokeAPIKeyCommand, None]):
    def __init__(self, api_key_repo: APIKeyRepository):
        self.api_key_repo = api_key_repo

    async def handle(self, command: RevokeAPIKeyCommand) -> None:
        api_key = await self.api_key_repo.get_by_id(command.api_key_id)
        if not api_key:
            raise NotFoundException("APIKey", command.api_key_id)

        if str(api_key.user_id) != command.__user_id__:
            raise AuthorizationException("Cannot revoke another user's API key")

        api_key.revoke(command.reason)
        await self.api_key_repo.update(api_key)