from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.application.base import Query, QueryHandler
from app.modules.companies.domain.entities import (
    Tenant,
    Department,
    Integration,
    Webhook,
    APIKey,
    FeatureFlag,
    AuditLog,
    SubscriptionPlan,
    SubscriptionStatus,
    CompanySize,
    Industry,
)
from app.modules.companies.domain.repositories import (
    TenantRepository,
    DepartmentRepository,
    IntegrationRepository,
    WebhookRepository,
    FeatureFlagRepository,
)
from app.core.exceptions import NotFoundException, AuthorizationException


class GetTenantQuery(Query):
    tenant_id: UUID | None = None


class TenantResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    domain: str | None
    subdomain: str | None
    logo_url: str | None
    primary_color: str
    secondary_color: str
    favicon_url: str | None
    company_size: CompanySize
    industry: Industry
    subscription_plan: SubscriptionPlan
    subscription_status: SubscriptionStatus
    max_users: int
    max_jobs: int
    max_candidates: int
    is_active: bool
    is_trial: bool
    trial_ends_at: datetime | None
    subscription_expires_at: datetime | None
    settings: dict[str, Any]
    features: dict[str, bool]
    created_at: datetime
    updated_at: datetime


class GetTenantHandler(QueryHandler[GetTenantQuery, TenantResult]):
    def __init__(self, tenant_repo: TenantRepository):
        self.tenant_repo = tenant_repo

    async def handle(self, query: GetTenantQuery) -> TenantResult:
        tenant_id = query.tenant_id or UUID(query.__tenant_id__)
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise NotFoundException("Tenant", tenant_id)
        return TenantResult.model_validate(tenant)


class ListTenantsQuery(Query):
    page: int = 1
    page_size: int = 50
    plan: SubscriptionPlan | None = None
    status: SubscriptionStatus | None = None
    is_active: bool | None = None


class ListTenantsResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[TenantResult]
    total: int
    page: int
    page_size: int
    total_pages: int


class ListTenantsHandler(QueryHandler[ListTenantsQuery, ListTenantsResult]):
    def __init__(self, tenant_repo: TenantRepository):
        self.tenant_repo = tenant_repo

    async def handle(self, query: ListTenantsQuery) -> ListTenantsResult:
        tenants = await self.tenant_repo.get_active_tenants(
            limit=query.page_size,
            offset=(query.page - 1) * query.page_size,
            plan=query.plan,
        )
        total = await self.tenant_repo.count_active(query.plan)
        return ListTenantsResult(
            items=[TenantResult.model_validate(t) for t in tenants],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=(total + query.page_size - 1) // query.page_size,
        )


class GetDepartmentQuery(Query):
    department_id: UUID


class DepartmentResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    name: str
    description: str | None
    parent_id: UUID | None
    manager_id: UUID | None
    budget: int | None
    location: str | None
    is_active: bool
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class GetDepartmentHandler(QueryHandler[GetDepartmentQuery, DepartmentResult]):
    def __init__(self, dept_repo: DepartmentRepository):
        self.dept_repo = dept_repo

    async def handle(self, query: GetDepartmentQuery) -> DepartmentResult:
        department = await self.dept_repo.get_by_id(query.department_id)
        if not department:
            raise NotFoundException("Department", query.department_id)
        return DepartmentResult.model_validate(department)


class ListDepartmentsQuery(Query):
    page: int = 1
    page_size: int = 50
    include_inactive: bool = False


class ListDepartmentsResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[DepartmentResult]
    total: int
    page: int
    page_size: int
    total_pages: int


class ListDepartmentsHandler(QueryHandler[ListDepartmentsQuery, ListDepartmentsResult]):
    def __init__(self, dept_repo: DepartmentRepository):
        self.dept_repo = dept_repo

    async def handle(self, query: ListDepartmentsQuery) -> ListDepartmentsResult:
        departments = await self.dept_repo.get_by_tenant(
            UUID(query.__tenant_id__),
            limit=query.page_size,
            offset=(query.page - 1) * query.page_size,
            include_inactive=query.include_inactive,
        )
        total = await self.dept_repo.count_by_tenant(
            UUID(query.__tenant_id__),
            include_inactive=query.include_inactive,
        )
        return ListDepartmentsResult(
            items=[DepartmentResult.model_validate(d) for d in departments],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=(total + query.page_size - 1) // query.page_size,
        )


class GetDepartmentTreeQuery(Query):
    pass


class GetDepartmentTreeHandler(QueryHandler[GetDepartmentTreeQuery, list[DepartmentResult]]):
    def __init__(self, dept_repo: DepartmentRepository):
        self.dept_repo = dept_repo

    async def handle(self, query: GetDepartmentTreeQuery) -> list[DepartmentResult]:
        departments = await self.dept_repo.get_tree(UUID(query.__tenant_id__))
        return [DepartmentResult.model_validate(d) for d in departments]


class ListIntegrationsQuery(Query):
    pass


class IntegrationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    name: str
    type: str
    provider: str
    config: dict[str, Any]
    credentials: dict[str, Any]
    webhook_url: str | None
    events: list[str]
    is_active: bool
    last_sync_at: datetime | None
    sync_status: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ListIntegrationsHandler(QueryHandler[ListIntegrationsQuery, list[IntegrationResult]]):
    def __init__(self, integration_repo: IntegrationRepository):
        self.integration_repo = integration_repo

    async def handle(self, query: ListIntegrationsQuery) -> list[IntegrationResult]:
        integrations = await self.integration_repo.get_active_by_tenant(UUID(query.__tenant_id__))
        return [IntegrationResult.model_validate(i) for i in integrations]


class ListWebhooksQuery(Query):
    page: int = 1
    page_size: int = 50
    event: str | None = None


class WebhookResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    name: str
    url: str
    events: list[str]
    secret: str | None
    is_active: bool
    retry_policy: dict[str, Any]
    headers: dict[str, str]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ListWebhooksHandler(QueryHandler[ListWebhooksQuery, list[WebhookResult]]):
    def __init__(self, webhook_repo: WebhookRepository):
        self.webhook_repo = webhook_repo

    async def handle(self, query: ListWebhooksQuery) -> list[WebhookResult]:
        webhooks = await self.webhook_repo.get_by_tenant(
            UUID(query.__tenant_id__),
            limit=query.page_size,
            offset=(query.page - 1) * query.page_size,
            event=query.event,
        )
        return [WebhookResult.model_validate(w) for w in webhooks]


class ListFeatureFlagsQuery(Query):
    pass


class FeatureFlagResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    key: str
    name: str
    description: str | None
    enabled: bool
    rollout_percentage: int
    target_groups: list[str]
    target_users: list[UUID]
    conditions: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int


class ListFeatureFlagsHandler(QueryHandler[ListFeatureFlagsQuery, list[FeatureFlagResult]]):
    def __init__(self, flag_repo: FeatureFlagRepository):
        self.flag_repo = flag_repo

    async def handle(self, query: ListFeatureFlagsQuery) -> list[FeatureFlagResult]:
        flags = await self.flag_repo.get_all_for_tenant(UUID(query.__tenant_id__))
        return [FeatureFlagResult.model_validate(f) for f in flags]


class EvaluateFeatureFlagQuery(Query):
    key: str
    user_id: UUID | None = None
    groups: list[str] | None = None


class EvaluateFeatureFlagResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    enabled: bool


class EvaluateFeatureFlagHandler(QueryHandler[EvaluateFeatureFlagQuery, EvaluateFeatureFlagResult]):
    def __init__(self, flag_repo: FeatureFlagRepository):
        self.flag_repo = flag_repo

    async def handle(self, query: EvaluateFeatureFlagQuery) -> EvaluateFeatureFlagResult:
        enabled = await self.flag_repo.evaluate(
            UUID(query.__tenant_id__),
            query.key,
            query.user_id,
            query.groups,
        )
        return EvaluateFeatureFlagResult(key=query.key, enabled=enabled)


class ListAPIKeysQuery(Query):
    pass


class APIKeyResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    user_id: UUID | None
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
    updated_at: datetime


class ListAPIKeysHandler(QueryHandler[ListAPIKeysQuery, list[APIKeyResult]]):
    def __init__(self, api_key_repo: Any):
        self.api_key_repo = api_key_repo

    async def handle(self, query: ListAPIKeysQuery) -> list[APIKeyResult]:
        keys = await self.api_key_repo.get_by_tenant(UUID(query.__tenant_id__))
        return [APIKeyResult.model_validate(k) for k in keys]


class GetAuditLogsQuery(Query):
    page: int = 1
    page_size: int = 50
    start_date: datetime | None = None
    end_date: datetime | None = None
    user_id: UUID | None = None
    action: str | None = None
    resource_type: str | None = None
    resource_id: UUID | None = None


class AuditLogResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    user_id: UUID | None
    api_key_id: UUID | None
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
    def __init__(self, audit_log_repo: Any):
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
            resource_id=query.resource_id,
        )
        total = await self.audit_log_repo.count_by_tenant(
            tenant_id=UUID(query.__tenant_id__),
            start_date=query.start_date,
            end_date=query.end_date,
            user_id=query.user_id,
            action=query.action,
            resource_type=query.resource_type,
            resource_id=query.resource_id,
        )
        return AuditLogsResult(
            items=[AuditLogResult.model_validate(item) for item in items],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=(total + query.page_size - 1) // query.page_size,
        )