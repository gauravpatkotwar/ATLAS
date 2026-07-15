import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from atlas.database.models import Tenant

logger = logging.getLogger(__name__)


class BillingService:
    """Service coordinates payment gateways (Stripe & Razorpay) integration and upgrades."""

    def __init__(self, db: AsyncSession, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id

    async def get_tenant(self) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.id == self.tenant_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_checkout_session(self, provider: str) -> Dict[str, Any]:
        """Creates checkout parameters for Stripe or Razorpay.

        In dev mode, we generate mock checkout tokens to initiate simulated payment.
        """
        tenant = await self.get_tenant()
        if not tenant:
            raise ValueError("Tenant not found")

        # Mock Stripe or Razorpay checkout params
        if provider == "stripe":
            mock_session_id = f"cs_test_stripe_{tenant.id}_abc123"
            checkout_url = f"/checkout/stripe?session_id={mock_session_id}"
            return {
                "provider": "stripe",
                "checkout_url": checkout_url,
                "session_id": mock_session_id,
                "amount": 79.00,
                "currency": "usd",
            }
        elif provider == "razorpay":
            mock_order_id = f"order_test_razorpay_{tenant.id}_xyz789"
            checkout_url = f"/checkout/razorpay?order_id={mock_order_id}"
            return {
                "provider": "razorpay",
                "checkout_url": checkout_url,
                "order_id": mock_order_id,
                "amount": 6500.00,
                "currency": "inr",
            }
        else:
            raise ValueError(f"Unsupported billing provider: {provider}")

    async def confirm_payment(self, provider: str, reference_id: str) -> bool:
        """Confirms successful checkout and upgrades the tenant workspace to Pro."""
        tenant = await self.get_tenant()
        if not tenant:
            logger.error(
                f"Cannot confirm payment: Tenant #{self.tenant_id} not found"
            )
            return False

        tenant.subscription_tier = "pro"
        tenant.billing_provider = provider
        if provider == "stripe":
            tenant.billing_subscription_id = reference_id
            tenant.billing_customer_id = f"cus_stripe_{tenant.id}"
        elif provider == "razorpay":
            tenant.billing_subscription_id = reference_id
            tenant.billing_customer_id = f"cus_razorpay_{tenant.id}"

        await self.db.commit()
        await self.db.refresh(tenant)
        logger.info(
            f"Tenant #{tenant.id} successfully upgraded to PRO tier via {provider.upper()}"
        )
        return True
