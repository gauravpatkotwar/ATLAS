from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories import TenantRepositoryPort
from app.modules.companies.domain.entities import (
    Tenant,
    Department,
    Integration,
    Webhook,
    APIKey,
    AuditLog,
    FeatureFlag,
    SubscriptionPlan,
    SubscriptionStatus,
    CompanySize,
    Industry,
)


class TenantRepository(TenantRepositoryPort[Tenant], ABC):
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Tenant | None:
        pass

    @abstractmethod
    async def get_by_domain(self, domain: str) -> Tenant | None:
        pass

    @abstractmethod
    async def get_by_subdomain(self, subdomain: str) -> Tenant | None:
        pass

    @abstractmethod
    async def get_active_tenants(
        self,
        limit: int = 50,
        offset: int = 0,
        plan: SubscriptionPlan | None = None,
    ) -> list[Tenant]:
        pass

    @abstractmethod
    async def count_active(self, plan: SubscriptionPlan | None = None) -> int:
        pass


class DepartmentRepository(ABC):
    @abstractmethod
    async def get_by_tenant(
        self,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        include_inactive: bool = False,
    ) -> list[Department]:
        pass

    @abstractmethod
    async def count_by_tenant(self, tenant_id: UUID, include_inactive: bool = False) -> int:
        pass

    @abstractmethod
    async def get_tree(self, tenant_id: UUID) -> list[Department]:
        pass


class IntegrationRepository(ABC):
    @abstractmethod
    async def get_by_type(
        self,
        tenant_id: UUID,
        type: str,
        provider: str | None = None,
    ) -> Integration | None:
        pass

    @abstractmethod
    async def get_active_by_tenant(self, tenant_id: UUID) -> list[Integration]:
        pass


class WebhookRepository(ABC):
    @abstractmethod
    async def get_by_tenant(
        self,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        event: str | None = None,
    ) -> list[Webhook]:
        pass

    @abstractmethod
    async def get_for_event(self, tenant_id: UUID, event: str) -> list[Webhook]:
        pass


class WebhookDeliveryRepository(ABC):
    @abstractmethod
    async def get_pending_deliveries(self, limit: int = 100) -> list[WebhookDelivery]:
        pass

    @abstractmethod
    async def get_failed_deliveries(self, limit: int = 100) -> list[WebhookDelivery]:
        pass


class FeatureFlagRepository(ABC):
    @abstractmethod
    async def get_by_key(self, tenant_id: UUID, key: str) -> FeatureFlag | None:
        pass

    @abstractmethod
    async def get_all_for_tenant(self, tenant_id: UUID) -> list[FeatureFlag]:
        pass

    @abstractmethod
    async def evaluate(self, tenant_id: UUID, key: str, user_id: UUID | None = None, groups: list[str] | None = None) -> bool:
        pass