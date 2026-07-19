from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.application.base import Command, CommandHandler, Query, QueryHandler
from app.modules.companies.domain.entities import (
    Tenant,
    Department,
    Integration,
    Webhook,
    APIKey,
    FeatureFlag,
    SubscriptionPlan,
    SubscriptionStatus,
    CompanySize,
    Industry,
    WebhookDelivery,
)
from app.modules.companies.domain.repositories import (
    TenantRepository,
    DepartmentRepository,
    IntegrationRepository,
    WebhookRepository,
    FeatureFlagRepository,
)
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
    BusinessRuleException,
    TenantNotFoundException,
)


class CreateTenantCommand(Command):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    domain: str | None = Field(None, pattern=r"^[a-z0-9.-]+$")
    subdomain: str | None = Field(None, min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$")
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=12)
    admin_first_name: str = Field(..., min_length=1, max_length=100)
    admin_last_name: str = Field(..., min_length=1, max_length=100)
    company_size: CompanySize = CompanySize.SMALL
    industry: Industry = Industry.TECHNOLOGY
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE


class CreateTenantResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tenant_id: UUID
    user_id: UUID
    access_token: str
    refresh_token: str


class CreateTenantHandler(CommandHandler[CreateTenantCommand, CreateTenantResult]):
    def __init__(
        self,
        tenant_repo: TenantRepository,
        user_repo: Any,
        role_repo: Any,
    ):
        self.tenant_repo = tenant_repo
        self.user_repo = user_repo
        self.role_repo = role_repo

    async def handle(self, command: CreateTenantCommand) -> CreateTenantResult:
        existing_tenant = await self.tenant_repo.get_by_slug(command.slug)
        if existing_tenant:
            raise ConflictException(f"Tenant with slug '{command.slug}' already exists")

        if command.domain:
            existing_domain = await self.tenant_repo.get_by_domain(command.domain)
            if existing_domain:
                raise ConflictException(f"Tenant with domain '{command.domain}' already exists")

        if command.subdomain:
            existing_subdomain = await self.tenant_repo.get_by_subdomain(command.subdomain)
            if existing_subdomain:
                raise ConflictException(f"Tenant with subdomain '{command.subdomain}' already exists")

        tenant = Tenant(
            name=command.name,
            slug=command.slug,
            domain=command.domain,
            subdomain=command.subdomain,
            company_size=command.company_size,
            industry=command.industry,
            subscription_plan=command.subscription_plan,
            subscription_status=SubscriptionStatus.ACTIVE,
            settings={},
            features={},
        )
        await self.tenant_repo.add(tenant)

        return CreateTenantResult(
            tenant_id=tenant.id,
            user_id=UUID("00000000-0000-0000-0000-000000000000"),
            access_token="",
            refresh_token="",
        )


class UpdateTenantCommand(Command):
    tenant_id: UUID
    name: str | None = None
    domain: str | None = None
    subdomain: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    favicon_url: str | None = None
    settings: dict[str, Any] | None = None
    features: dict[str, bool] | None = None


class UpdateTenantHandler(CommandHandler[UpdateTenantCommand, Tenant]):
    def __init__(self, tenant_repo: TenantRepository):
        self.tenant_repo = tenant_repo

    async def handle(self, command: UpdateTenantCommand) -> Tenant:
        tenant = await self.tenant_repo.get_by_id(command.tenant_id)
        if not tenant:
            raise TenantNotFoundException(command.tenant_id)

        if command.name is not None:
            tenant.name = command.name
        if command.domain is not None:
            existing = await self.tenant_repo.get_by_domain(command.domain)
            if existing and existing.id != command.tenant_id:
                raise ConflictException(f"Domain '{command.domain}' already in use")
            tenant.domain = command.domain
        if command.subdomain is not None:
            existing = await self.tenant_repo.get_by_subdomain(command.subdomain)
            if existing and existing.id != command.tenant_id:
                raise ConflictException(f"Subdomain '{command.subdomain}' already in use")
            tenant.subdomain = command.subdomain
        if command.logo_url is not None:
            tenant.logo_url = command.logo_url
        if command.primary_color is not None:
            tenant.primary_color = command.primary_color
        if command.secondary_color is not None:
            tenant.secondary_color = command.secondary_color
        if command.favicon_url is not None:
            tenant.favicon_url = command.favicon_url
        if command.settings is not None:
            tenant.settings = {**tenant.settings, **command.settings}
        if command.features is not None:
            tenant.features = {**tenant.features, **command.features}

        tenant.updated_at = datetime.utcnow()
        await self.tenant_repo.update(tenant)
        return tenant


class DeleteTenantCommand(Command):
    tenant_id: UUID
    force: bool = False


class DeleteTenantHandler(CommandHandler[DeleteTenantCommand, None]):
    def __init__(self, tenant_repo: TenantRepository):
        self.tenant_repo = tenant_repo

    async def handle(self, command: DeleteTenantCommand) -> None:
        tenant = await self.tenant_repo.get_by_id(command.tenant_id)
        if not tenant:
            raise TenantNotFoundException(command.tenant_id)

        if command.force:
            await self.tenant_repo.delete(command.tenant_id)
        else:
            tenant.is_active = False
            tenant.updated_at = datetime.utcnow()
            await self.tenant_repo.update(tenant)


class UpdateSubscriptionCommand(Command):
    tenant_id: UUID
    plan: SubscriptionPlan
    status: SubscriptionStatus | None = None
    max_users: int | None = None
    max_jobs: int | None = None
    max_candidates: int | None = None
    expires_at: datetime | None = None


class UpdateSubscriptionHandler(CommandHandler[UpdateSubscriptionCommand, Tenant]):
    def __init__(self, tenant_repo: TenantRepository):
        self.tenant_repo = tenant_repo

    async def handle(self, command: UpdateSubscriptionCommand) -> Tenant:
        tenant = await self.tenant_repo.get_by_id(command.tenant_id)
        if not tenant:
            raise TenantNotFoundException(command.tenant_id)

        tenant.subscription_plan = command.plan
        if command.status:
            tenant.subscription_status = command.status
        if command.max_users:
            tenant.max_users = command.max_users
        if command.max_jobs:
            tenant.max_jobs = command.max_jobs
        if command.max_candidates:
            tenant.max_candidates = command.max_candidates
        if command.expires_at:
            tenant.subscription_expires_at = command.expires_at

        tenant.updated_at = datetime.utcnow()
        await self.tenant_repo.update(tenant)
        return tenant


class CreateDepartmentCommand(Command):
    tenant_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    parent_id: UUID | None = None
    manager_id: UUID | None = None
    budget: int | None = None
    location: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateDepartmentHandler(CommandHandler[CreateDepartmentCommand, Department]):
    def __init__(self, dept_repo: DepartmentRepository):
        self.dept_repo = dept_repo

    async def handle(self, command: CreateDepartmentCommand) -> Department:
        if command.parent_id:
            parent = await self.dept_repo.get_by_id(command.parent_id)
            if not parent:
                raise NotFoundException("Department", command.parent_id)
            if parent.tenant_id != command.tenant_id:
                raise BusinessRuleException("Parent department belongs to different tenant")

        department = Department(
            tenant_id=command.tenant_id,
            name=command.name,
            description=command.description,
            parent_id=command.parent_id,
            manager_id=command.manager_id,
            budget=command.budget,
            location=command.location,
            metadata=command.metadata,
        )
        await self.dept_repo.add(department)
        return department


class UpdateDepartmentCommand(Command):
    department_id: UUID
    name: str | None = None
    description: str | None = None
    parent_id: UUID | None = None
    manager_id: UUID | None = None
    budget: int | None = None
    location: str | None = None
    is_active: bool | None = None
    metadata: dict[str, Any] | None = None


class UpdateDepartmentHandler(CommandHandler[UpdateDepartmentCommand, Department]):
    def __init__(self, dept_repo: DepartmentRepository):
        self.dept_repo = dept_repo

    async def handle(self, command: UpdateDepartmentCommand) -> Department:
        department = await self.dept_repo.get_by_id(command.department_id)
        if not department:
            raise NotFoundException("Department", command.department_id)

        if command.name is not None:
            department.name = command.name
        if command.description is not None:
            department.description = command.description
        if command.parent_id is not None:
            if command.parent_id:
                parent = await self.dept_repo.get_by_id(command.parent_id)
                if not parent:
                    raise NotFoundException("Department", command.parent_id)
                if parent.id == command.department_id:
                    raise ValidationException("Department cannot be its own parent")
            department.parent_id = command.parent_id
        if command.manager_id is not None:
            department.manager_id = command.manager_id
        if command.budget is not None:
            department.budget = command.budget
        if command.location is not None:
            department.location = command.location
        if command.is_active is not None:
            department.is_active = command.is_active
        if command.metadata is not None:
            department.metadata = {**department.metadata, **command.metadata}

        department.updated_at = datetime.utcnow()
        await self.dept_repo.update(department)
        return department


class CreateIntegrationCommand(Command):
    tenant_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    type: str = Field(..., min_length=1, max_length=50)
    provider: str = Field(..., min_length=1, max_length=100)
    config: dict[str, Any] = Field(default_factory=dict)
    credentials: dict[str, Any] = Field(default_factory=dict)
    webhook_url: str | None = None
    events: list[str] = Field(default_factory=list)
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateIntegrationHandler(CommandHandler[CreateIntegrationCommand, Integration]):
    def __init__(self, integration_repo: IntegrationRepository):
        self.integration_repo = integration_repo

    async def handle(self, command: CreateIntegrationCommand) -> Integration:
        existing = await self.integration_repo.get_by_type(command.tenant_id, command.type, command.provider)
        if existing:
            raise ConflictException(f"Integration of type '{command.type}' with provider '{command.provider}' already exists")

        integration = Integration(
            tenant_id=command.tenant_id,
            name=command.name,
            type=command.type,
            provider=command.provider,
            config=command.config,
            credentials=command.credentials,
            webhook_url=command.webhook_url,
            events=command.events,
            is_active=command.is_active,
            metadata=command.metadata,
        )
        await self.integration_repo.add(integration)
        return integration


class UpdateIntegrationCommand(Command):
    integration_id: UUID
    name: str | None = None
    config: dict[str, Any] | None = None
    credentials: dict[str, Any] | None = None
    webhook_url: str | None = None
    events: list[str] | None = None
    is_active: bool | None = None
    metadata: dict[str, Any] | None = None


class UpdateIntegrationHandler(CommandHandler[UpdateIntegrationCommand, Integration]):
    def __init__(self, integration_repo: IntegrationRepository):
        self.integration_repo = integration_repo

    async def handle(self, command: UpdateIntegrationCommand) -> Integration:
        integration = await self.integration_repo.get_by_id(command.integration_id)
        if not integration:
            raise NotFoundException("Integration", command.integration_id)

        if command.name is not None:
            integration.name = command.name
        if command.config is not None:
            integration.config = {**integration.config, **command.config}
        if command.credentials is not None:
            integration.credentials = {**integration.credentials, **command.credentials}
        if command.webhook_url is not None:
            integration.webhook_url = command.webhook_url
        if command.events is not None:
            integration.events = command.events
        if command.is_active is not None:
            integration.is_active = command.is_active
        if command.metadata is not None:
            integration.metadata = {**integration.metadata, **command.metadata}

        integration.updated_at = datetime.utcnow()
        await self.integration_repo.update(integration)
        return integration


class CreateWebhookCommand(Command):
    tenant_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1)
    events: list[str] = Field(..., min_length=1)
    secret: str | None = None
    is_active: bool = True
    retry_policy: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateWebhookHandler(CommandHandler[CreateWebhookCommand, Webhook]):
    def __init__(self, webhook_repo: WebhookRepository):
        self.webhook_repo = webhook_repo

    async def handle(self, command: CreateWebhookCommand) -> Webhook:
        webhook = Webhook(
            tenant_id=command.tenant_id,
            name=command.name,
            url=command.url,
            events=command.events,
            secret=command.secret,
            is_active=command.is_active,
            retry_policy=command.retry_policy,
            headers=command.headers,
            metadata=command.metadata,
        )
        await self.webhook_repo.add(webhook)
        return webhook


class UpdateFeatureFlagCommand(Command):
    tenant_id: UUID
    key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    enabled: bool = False
    rollout_percentage: int = Field(default=100, ge=0, le=100)
    target_groups: list[str] = Field(default_factory=list)
    target_users: list[UUID] = Field(default_factory=list)
    conditions: dict[str, Any] = Field(default_factory=dict)


class UpdateFeatureFlagHandler(CommandHandler[UpdateFeatureFlagCommand, FeatureFlag]):
    def __init__(self, flag_repo: FeatureFlagRepository):
        self.flag_repo = flag_repo

    async def handle(self, command: UpdateFeatureFlagCommand) -> FeatureFlag:
        flag = await self.flag_repo.get_by_key(command.tenant_id, command.key)
        if not flag:
            flag = FeatureFlag(
                tenant_id=command.tenant_id,
                key=command.key,
                name=command.name,
            )
            await self.flag_repo.add(flag)

        flag.name = command.name
        flag.description = command.description
        flag.enabled = command.enabled
        flag.rollout_percentage = command.rollout_percentage
        flag.target_groups = command.target_groups
        flag.target_users = command.target_users
        flag.conditions = command.conditions
        flag.updated_at = datetime.utcnow()
        flag.version += 1

        await self.flag_repo.update(flag)
        return flag


class CreateAPIKeyCommand(Command):
    tenant_id: UUID
    user_id: UUID | None = None
    name: str = Field(..., min_length=1, max_length=100)
    permissions: list[str] = Field(default_factory=list)
    rate_limit: int = Field(default=1000, ge=1)
    expires_in_days: int | None = Field(None, ge=1)


class CreateAPIKeyResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    key: str
    key_prefix: str
    permissions: list[str]
    expires_at: datetime | None


class CreateAPIKeyHandler(CommandHandler[CreateAPIKeyCommand, CreateAPIKeyResult]):
    def __init__(self, api_key_repo: Any):
        self.api_key_repo = api_key_repo

    async def handle(self, command: CreateAPIKeyCommand) -> CreateAPIKeyResult:
        import secrets
        from app.core.security import hash_api_key

        api_key = f"atlas_{secrets.token_urlsafe(32)}"
        key_hash = hash_api_key(api_key)
        key_prefix = api_key[:20]

        expires_at = None
        if command.expires_in_days:
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(days=command.expires_in_days)

        key_obj = APIKey(
            tenant_id=command.tenant_id,
            user_id=command.user_id,
            name=command.name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            permissions=command.permissions,
            rate_limit=command.rate_limit,
            expires_at=expires_at,
        )
        await self.api_key_repo.add(key_obj)

        return CreateAPIKeyResult(
            id=key_obj.id,
            name=key_obj.name,
            key=api_key,
            key_prefix=key_prefix,
            permissions=key_obj.permissions,
            expires_at=key_obj.expires_at,
        )