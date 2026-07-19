from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Boolean,
    JSON,
    ARRAY,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.base import AggregateRoot


class SubscriptionPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class CompanySize(str, Enum):
    STARTUP = "startup"  # 1-10
    SMALL = "small"  # 11-50
    MEDIUM = "medium"  # 51-200
    LARGE = "large"  # 201-1000
    ENTERPRISE = "enterprise"  # 1000+


class Industry(str, Enum):
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing
    REAL_ESTATE = "real_estate
    CONSULTING = "consulting
    MEDIA = "media
    NON_PROFIT = "non_profit
    GOVERNMENT = "government
    OTHER = "other


class Tenant(AggregateRoot):
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    subdomain: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    favicon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(7), default="#0066CC", nullable=False)
    secondary_color: Mapped[str] = mapped_column(String(7), default="#004499", nullable=False)
    font_family: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    company_size: Mapped[CompanySize | None] = mapped_column(String(30), nullable=True)
    industry: Mapped[Industry | None] = mapped_column(String(50), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    features: Mapped[dict[str, bool]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(String(30), default=SubscriptionPlan.FREE, nullable=False)
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(String(30), default=SubscriptionStatus.TRIAL, nullable=False)
    subscription_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    max_users: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_jobs: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_candidates: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    max_storage_gb: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    billing_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    billing_address: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    users: Mapped[list["User"]] = relationship("User", back_populates="tenant")
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="tenant")
    candidates: Mapped[list["Candidate"]] = relationship("Candidate", back_populates="tenant")
    departments: Mapped[list["Department"]] = relationship("Department", back_populates="tenant")
    pipelines: Mapped[list["Pipeline"]] = relationship("Pipeline", back_populates="tenant")
    workflows: Mapped[list["Workflow"]] = relationship("Workflow", back_populates="tenant")
    integrations: Mapped[list["Integration"]] = relationship("Integration", back_populates="tenant")
    webhooks: Mapped[list["Webhook"]] = relationship("Webhook", back_populates="tenant")
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="tenant")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="tenant")

    __table_args__ = (
        Index("ix_tenant_active", "is_active"),
        Index("ix_tenant_subscription", "subscription_plan", "subscription_status"),
    )


class Department(AggregateRoot):
    __tablename__ = "departments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    parent_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("departments.id"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    manager_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_center: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="departments")
    parent: Mapped["Department | None"] = relationship("Department", remote_side=[id], back_populates="children")
    children: Mapped[list["Department"]] = relationship("Department", back_populates="parent")
    manager: Mapped["User | None"] = relationship("User", foreign_keys=[manager_id])
    members: Mapped[list["User"]] = relationship("User", foreign_keys="User.department_id")
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="department")

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_department_tenant_code"),
        Index("ix_department_tenant_active", "tenant_id", "is_active"),
    )


class Integration(AggregateRoot):
    __tablename__ = "integrations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    credentials: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    webhook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    webhook_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="integrations")

    __table_args__ = (
        UniqueConstraint("tenant_id", "type", "provider", name="uq_integration_tenant_type_provider"),
        Index("ix_integration_tenant_active", "tenant_id", "is_active"),
    )


class Webhook(AggregateRoot):
    __tablename__ = "webhooks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    
    events: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    retry_policy: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="webhooks")
    deliveries: Mapped[list["WebhookDelivery"]] = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_webhook_tenant_active", "tenant_id", "is_active"),
    )


class WebhookDelivery(AggregateRoot):
    __tablename__ = "webhook_deliveries"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    webhook_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    event: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_headers: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    attempt: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    webhook: Mapped[Webhook] = relationship("Webhook", back_populates="deliveries")
    tenant: Mapped[Tenant] = relationship("Tenant")

    __table_args__ = (
        Index("ix_webhook_delivery_status_retry", "status", "next_retry_at"),
    )


class APIKey(AggregateRoot):
    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)
    
    permissions: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    rate_limit: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="api_keys")
    user: Mapped["User | None"] = relationship("User", back_populates="api_keys")

    __table_args__ = (
        Index("ix_api_key_tenant_active", "tenant_id", "revoked_at"),
    )


class AuditLog(AggregateRoot):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    api_key_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=True)
    
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    old_values: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    changed_fields: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="audit_logs")
    user: Mapped["User | None"] = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_tenant_created", "tenant_id", "created_at"),
        Index("ix_audit_user_created", "user_id", "created_at"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
    )


class FeatureFlag(AggregateRoot):
    __tablename__ = "feature_flags"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rollout_percentage: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    target_groups: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    target_users: Mapped[list[UUID]] = mapped_column(ARRAY(PGUUID(as_uuid=True)), default_factory=list, nullable=False)
    
    conditions: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped[Tenant] = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uq_feature_flag_tenant_key"),
        Index("ix_feature_flag_tenant_enabled", "tenant_id", "enabled"),
    )