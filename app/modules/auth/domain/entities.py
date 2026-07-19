from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    Boolean,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.base import AggregateRoot, DomainEvent
from app.core.config import settings


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    LOCKED = "locked"


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    HR = "hr"
    INTERVIEWER = "interviewer"
    VIEWER = "viewer"


class Permission(str, Enum):
    # User management
    USERS_CREATE = "users:create"
    USERS_READ = "users:read"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    USERS_MANAGE_ROLES = "users:manage_roles"
    
    # Company/Tenant management
    COMPANY_CREATE = "company:create"
    COMPANY_READ = "company:read"
    COMPANY_UPDATE = "company:update"
    COMPANY_DELETE = "company:delete"
    COMPANY_MANAGE_SETTINGS = "company:manage_settings"
    COMPANY_MANAGE_BRANDING = "company:manage_branding"
    
    # Candidate management
    CANDIDATES_CREATE = "candidates:create"
    CANDIDATES_READ = "candidates:read"
    CANDIDATES_UPDATE = "candidates:update"
    CANDIDATES_DELETE = "candidates:delete"
    CANDIDATES_IMPORT = "candidates:import"
    CANDIDATES_EXPORT = "candidates:export"
    CANDIDATES_MANAGE_DOCUMENTS = "candidates:manage_documents"
    
    # Job management
    JOBS_CREATE = "jobs:create"
    JOBS_READ = "jobs:read"
    JOBS_UPDATE = "jobs:update"
    JOBS_DELETE = "jobs:delete"
    JOBS_PUBLISH = "jobs:publish"
    JOBS_MANAGE_PIPELINE = "jobs:manage_pipeline"
    JOBS_MANAGE_TEAM = "jobs:manage_team"
    
    # Matching & AI
    MATCHING_SEARCH = "matching:search"
    MATCHING_RECOMMEND = "matching:recommend"
    MATCHING_RANK = "matching:rank"
    AI_RECRUITER_CHAT = "ai:recruiter_chat"
    AI_GENERATE_JD = "ai:generate_jd"
    AI_GENERATE_QUESTIONS = "ai:generate_questions"
    AI_GENERATE_EMAILS = "ai:generate_emails"
    AI_GENERATE_OFFERS = "ai:generate_offers"
    AI_SUMMARIZE = "ai:summarize"
    
    # Communication
    COMMUNICATION_EMAIL = "communication:email"
    COMMUNICATION_SMS = "communication:sms"
    COMMUNICATION_SCHEDULE = "communication:schedule"
    COMMUNICATION_TEMPLATES = "communication:templates"
    
    # Interviews
    INTERVIEWS_SCHEDULE = "interviews:schedule"
    INTERVIEWS_CONDUCT = "interviews:conduct"
    INTERVIEWS_RECORD = "interviews:record"
    INTERVIEWS_SCORE = "interviews:score"
    INTERVIEWS_NOTES = "interviews:notes"
    
    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_DASHBOARDS = "analytics:dashboards"
    
    # Workflows
    WORKFLOWS_CREATE = "workflows:create"
    WORKFLOWS_READ = "workflows:read"
    WORKFLOWS_UPDATE = "workflows:update"
    WORKFLOWS_DELETE = "workflows:delete"
    WORKFLOWS_EXECUTE = "workflows:execute"
    
    # Admin
    ADMIN_TENANTS = "admin:tenants"
    ADMIN_USERS = "admin:users"
    ADMIN_AUDIT_LOGS = "admin:audit_logs"
    ADMIN_FEATURE_FLAGS = "admin:feature_flags"
    ADMIN_BILLING = "admin:billing"
    ADMIN_SYSTEM = "admin:system"
    
    # API
    API_ACCESS = "api:access"
    API_WEBHOOKS = "api:webhooks"
    API_OAUTH = "api:oauth"


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.SUPER_ADMIN: set(Permission),
    UserRole.TENANT_ADMIN: {
        Permission.USERS_CREATE,
        Permission.USERS_READ,
        Permission.USERS_UPDATE,
        Permission.USERS_DELETE,
        Permission.USERS_MANAGE_ROLES,
        Permission.COMPANY_READ,
        Permission.COMPANY_UPDATE,
        Permission.COMPANY_MANAGE_SETTINGS,
        Permission.COMPANY_MANAGE_BRANDING,
        Permission.CANDIDATES_CREATE,
        Permission.CANDIDATES_READ,
        Permission.CANDIDATES_UPDATE,
        Permission.CANDIDATES_DELETE,
        Permission.CANDIDATES_IMPORT,
        Permission.CANDIDATES_EXPORT,
        Permission.CANDIDATES_MANAGE_DOCUMENTS,
        Permission.JOBS_CREATE,
        Permission.JOBS_READ,
        Permission.JOBS_UPDATE,
        Permission.JOBS_DELETE,
        Permission.JOBS_PUBLISH,
        Permission.JOBS_MANAGE_PIPELINE,
        Permission.JOBS_MANAGE_TEAM,
        Permission.MATCHING_SEARCH,
        Permission.MATCHING_RECOMMEND,
        Permission.MATCHING_RANK,
        Permission.AI_RECRUITER_CHAT,
        Permission.AI_GENERATE_JD,
        Permission.AI_GENERATE_QUESTIONS,
        Permission.AI_GENERATE_EMAILS,
        Permission.AI_GENERATE_OFFERS,
        Permission.AI_SUMMARIZE,
        Permission.COMMUNICATION_EMAIL,
        Permission.COMMUNICATION_SMS,
        Permission.COMMUNICATION_SCHEDULE,
        Permission.COMMUNICATION_TEMPLATES,
        Permission.INTERVIEWS_SCHEDULE,
        Permission.INTERVIEWS_CONDUCT,
        Permission.INTERVIEWS_RECORD,
        Permission.INTERVIEWS_SCORE,
        Permission.INTERVIEWS_NOTES,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
        Permission.ANALYTICS_DASHBOARDS,
        Permission.WORKFLOWS_CREATE,
        Permission.WORKFLOWS_READ,
        Permission.WORKFLOWS_UPDATE,
        Permission.WORKFLOWS_DELETE,
        Permission.WORKFLOWS_EXECUTE,
        Permission.ADMIN_USERS,
        Permission.ADMIN_AUDIT_LOGS,
        Permission.ADMIN_FEATURE_FLAGS,
        Permission.API_ACCESS,
        Permission.API_WEBHOOKS,
    },
    UserRole.RECRUITER: {
        Permission.USERS_READ,
        Permission.CANDIDATES_CREATE,
        Permission.CANDIDATES_READ,
        Permission.CANDIDATES_UPDATE,
        Permission.CANDIDATES_IMPORT,
        Permission.CANDIDATES_EXPORT,
        Permission.CANDIDATES_MANAGE_DOCUMENTS,
        Permission.JOBS_CREATE,
        Permission.JOBS_READ,
        Permission.JOBS_UPDATE,
        Permission.JOBS_PUBLISH,
        Permission.JOBS_MANAGE_PIPELINE,
        Permission.JOBS_MANAGE_TEAM,
        Permission.MATCHING_SEARCH,
        Permission.MATCHING_RECOMMEND,
        Permission.MATCHING_RANK,
        Permission.AI_RECRUITER_CHAT,
        Permission.AI_GENERATE_JD,
        Permission.AI_GENERATE_QUESTIONS,
        Permission.AI_GENERATE_EMAILS,
        Permission.AI_SUMMARIZE,
        Permission.COMMUNICATION_EMAIL,
        Permission.COMMUNICATION_SCHEDULE,
        Permission.COMMUNICATION_TEMPLATES,
        Permission.INTERVIEWS_SCHEDULE,
        Permission.INTERVIEWS_CONDUCT,
        Permission.INTERVIEWS_NOTES,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_DASHBOARDS,
        Permission.WORKFLOWS_READ,
        Permission.WORKFLOWS_EXECUTE,
        Permission.API_ACCESS,
    },
    UserRole.HIRING_MANAGER: {
        Permission.USERS_READ,
        Permission.CANDIDATES_READ,
        Permission.CANDIDATES_UPDATE,
        Permission.JOBS_READ,
        Permission.JOBS_UPDATE,
        Permission.JOBS_MANAGE_PIPELINE,
        Permission.JOBS_MANAGE_TEAM,
        Permission.MATCHING_SEARCH,
        Permission.MATCHING_RECOMMEND,
        Permission.AI_RECRUITER_CHAT,
        Permission.AI_GENERATE_QUESTIONS,
        Permission.COMMUNICATION_EMAIL,
        Permission.COMMUNICATION_SCHEDULE,
        Permission.INTERVIEWS_SCHEDULE,
        Permission.INTERVIEWS_CONDUCT,
        Permission.INTERVIEWS_SCORE,
        Permission.INTERVIEWS_NOTES,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_DASHBOARDS,
        Permission.WORKFLOWS_READ,
        Permission.WORKFLOWS_EXECUTE,
        Permission.API_ACCESS,
    },
    UserRole.HR: {
        Permission.USERS_READ,
        Permission.USERS_UPDATE,
        Permission.CANDIDATES_CREATE,
        Permission.CANDIDATES_READ,
        Permission.CANDIDATES_UPDATE,
        Permission.CANDIDATES_IMPORT,
        Permission.CANDIDATES_EXPORT,
        Permission.CANDIDATES_MANAGE_DOCUMENTS,
        Permission.JOBS_CREATE,
        Permission.JOBS_READ,
        Permission.JOBS_UPDATE,
        Permission.JOBS_PUBLISH,
        Permission.JOBS_MANAGE_PIPELINE,
        Permission.JOBS_MANAGE_TEAM,
        Permission.MATCHING_SEARCH,
        Permission.MATCHING_RECOMMEND,
        Permission.MATCHING_RANK,
        Permission.AI_RECRUITER_CHAT,
        Permission.AI_GENERATE_JD,
        Permission.AI_GENERATE_QUESTIONS,
        Permission.AI_GENERATE_EMAILS,
        Permission.AI_GENERATE_OFFERS,
        Permission.AI_SUMMARIZE,
        Permission.COMMUNICATION_EMAIL,
        Permission.COMMUNICATION_SMS,
        Permission.COMMUNICATION_SCHEDULE,
        Permission.COMMUNICATION_TEMPLATES,
        Permission.INTERVIEWS_SCHEDULE,
        Permission.INTERVIEWS_CONDUCT,
        Permission.INTERVIEWS_RECORD,
        Permission.INTERVIEWS_SCORE,
        Permission.INTERVIEWS_NOTES,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
        Permission.ANALYTICS_DASHBOARDS,
        Permission.WORKFLOWS_READ,
        Permission.WORKFLOWS_EXECUTE,
        Permission.API_ACCESS,
    },
    UserRole.INTERVIEWER: {
        Permission.CANDIDATES_READ,
        Permission.JOBS_READ,
        Permission.AI_GENERATE_QUESTIONS,
        Permission.COMMUNICATION_EMAIL,
        Permission.INTERVIEWS_CONDUCT,
        Permission.INTERVIEWS_SCORE,
        Permission.INTERVIEWS_NOTES,
        Permission.WORKFLOWS_EXECUTE,
        Permission.API_ACCESS,
    },
    UserRole.VIEWER: {
        Permission.USERS_READ,
        Permission.CANDIDATES_READ,
        Permission.JOBS_READ,
        Permission.MATCHING_SEARCH,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_DASHBOARDS,
        Permission.API_ACCESS,
    },
}


def get_permissions_for_role(role: UserRole) -> set[Permission]:
    return ROLE_PERMISSIONS.get(role, set())


def get_permissions_for_roles(roles: list[UserRole]) -> set[Permission]:
    permissions = set()
    for role in roles:
        permissions.update(get_permissions_for_role(role))
    return permissions


class User(AggregateRoot):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    password_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    status: Mapped[UserStatus] = mapped_column(
        String(30), default=UserStatus.PENDING_VERIFICATION, nullable=False
    )
    roles: Mapped[list[UserRole]] = mapped_column(
        "roles", 
        default_factory=list, 
        nullable=False
    )
    permissions: Mapped[list[Permission]] = mapped_column(
        "permissions",
        default_factory=list,
        nullable=False
    )
    
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mfa_backup_codes: Mapped[list[str]] = mapped_column(default_factory=list, nullable=False)
    
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
    sessions: Mapped[list["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),
        Index("ix_user_tenant_status", "tenant_id", "status"),
        Index("ix_user_tenant_roles", "tenant_id", "roles"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    @property
    def is_locked(self) -> bool:
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions or permission in get_permissions_for_roles(self.roles)

    def has_role(self, role: UserRole) -> bool:
        return role in self.roles

    def has_any_role(self, roles: list[UserRole]) -> bool:
        return any(role in self.roles for role in roles)

    def add_role(self, role: UserRole) -> None:
        if role not in self.roles:
            self.roles.append(role)
            self.mark_updated()

    def remove_role(self, role: UserRole) -> None:
        if role in self.roles:
            self.roles.remove(role)
            self.mark_updated()

    def add_permission(self, permission: Permission) -> None:
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.mark_updated()

    def remove_permission(self, permission: Permission) -> None:
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.mark_updated()

    def record_login(self, ip: str) -> None:
        self.last_login_at = datetime.utcnow()
        self.last_login_ip = ip
        self.failed_login_attempts = 0
        self.locked_until = None
        self.mark_updated()

    def record_failed_login(self) -> None:
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= settings.auth.lockout_threshold:
            self.locked_until = datetime.utcnow() + timedelta(minutes=settings.auth.lockout_duration_minutes)
        self.mark_updated()

    def verify_email(self) -> None:
        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
        self.mark_updated()

    def change_password(self, new_hash: str) -> None:
        self.password_hash = new_hash
        self.password_changed_at = datetime.utcnow()
        self.mark_updated()

    def enable_mfa(self, secret: str) -> None:
        self.mfa_enabled = True
        self.mfa_secret = secret
        self.mark_updated()

    def disable_mfa(self) -> None:
        self.mfa_enabled = False
        self.mfa_secret = None
        self.mfa_backup_codes = []
        self.mark_updated()

    def generate_backup_codes(self, codes: list[str]) -> None:
        self.mfa_backup_codes = codes
        self.mark_updated()

    def use_backup_code(self, code: str) -> bool:
        if code in self.mfa_backup_codes:
            self.mfa_backup_codes.remove(code)
            self.mark_updated()
            return True
        return False


class Tenant(AggregateRoot):
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(7), default="#0066CC", nullable=False)
    secondary_color: Mapped[str] = mapped_column(String(7), default="#004499", nullable=False)
    favicon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    settings: Mapped[dict[str, Any]] = mapped_column(default_factory=dict, nullable=False)
    features: Mapped[dict[str, bool]] = mapped_column(default_factory=dict, nullable=False)
    
    subscription_plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    subscription_status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    subscription_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    max_users: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_jobs: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_candidates: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    users: Mapped[list[User]] = relationship("User", back_populates="tenant")
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="tenant")
    candidates: Mapped[list["Candidate"]] = relationship("Candidate", back_populates="tenant")
    departments: Mapped[list["Department"]] = relationship("Department", back_populates="tenant")

    __table_args__ = (
        Index("ix_tenant_active", "is_active"),
    )


class UserSession(AggregateRoot):
    __tablename__ = "user_sessions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    access_token_jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    refresh_token_jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    
    device_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    user: Mapped[User] = relationship("User", back_populates="sessions")
    tenant: Mapped[Tenant] = relationship("Tenant")

    __table_args__ = (
        Index("ix_session_user_active", "user_id", "revoked_at"),
        Index("ix_session_tenant_expires", "tenant_id", "expires_at"),
    )

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and self.expires_at > datetime.utcnow()

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= datetime.utcnow()

    def revoke(self, reason: str = "revoked") -> None:
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason
        self.mark_updated()


class APIKey(AggregateRoot):
    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)
    
    permissions: Mapped[list[Permission]] = mapped_column(default_factory=list, nullable=False)
    rate_limit: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user: Mapped[User] = relationship("User", back_populates="api_keys")
    tenant: Mapped[Tenant] = relationship("Tenant")

    __table_args__ = (
        Index("ix_api_key_user_active", "user_id", "revoked_at"),
    )

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and (self.expires_at is None or self.expires_at > datetime.utcnow())

    def revoke(self, reason: str = "revoked") -> None:
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason
        self.mark_updated()


class AuditLog(AggregateRoot):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    old_values: Mapped[dict[str, Any] | None] = mapped_column(default=None, nullable=True)
    new_values: Mapped[dict[str, Any] | None] = mapped_column(default=None, nullable=True)
    changed_fields: Mapped[list[str]] = mapped_column(default_factory=list, nullable=False)
    
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    
    metadata: Mapped[dict[str, Any]] = mapped_column(default_factory=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    tenant: Mapped[Tenant] = relationship("Tenant")
    user: Mapped[User | None] = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_tenant_created", "tenant_id", "created_at"),
        Index("ix_audit_user_created", "user_id", "created_at"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
    )


class Role(AggregateRoot):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    permissions: Mapped[list[Permission]] = mapped_column(default_factory=list, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped[Tenant] = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_role_tenant_name"),
        Index("ix_role_tenant_active", "tenant_id", "deleted_at"),
    )