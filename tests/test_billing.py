import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from atlas.database.models import Tenant


@pytest.mark.asyncio
async def test_billing_checkout_routing(
    client: AsyncClient, db_session: AsyncSession
):
    # 1. Register a test organization recruiter user
    register_payload = {
        "email": "billing.tester@example.com",
        "password": "strongPassword123",
        "role": "recruiter",
        "org_name": "Billing Test Org",
    }
    reg_response = await client.post(
        "/api/v1/auth/register", json=register_payload
    )
    assert reg_response.status_code == 201

    # 2. Login to get authentication token
    login_payload = {
        "username": "billing.tester@example.com",
        "password": "strongPassword123",
    }
    login_response = await client.post(
        "/api/v1/auth/login", data=login_payload
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create checkout session for Razorpay (Domestic INR)
    razor_req = {"provider": "razorpay"}
    razor_res = await client.post(
        "/api/v1/billing/checkout", json=razor_req, headers=headers
    )
    assert razor_res.status_code == 200
    razor_data = razor_res.json()
    assert razor_data["provider"] == "razorpay"
    assert "order_id" in razor_data
    assert razor_data["amount"] == 6500.00
    assert razor_data["currency"] == "inr"

    # 4. Create checkout session for Stripe (Global USD)
    stripe_req = {"provider": "stripe"}
    stripe_res = await client.post(
        "/api/v1/billing/checkout", json=stripe_req, headers=headers
    )
    assert stripe_res.status_code == 200
    stripe_data = stripe_res.json()
    assert stripe_data["provider"] == "stripe"
    assert "session_id" in stripe_data
    assert stripe_data["amount"] == 79.00
    assert stripe_data["currency"] == "usd"

    # 5. Confirm Stripe payment and verify tenant upgrade to PRO
    confirm_req = {
        "provider": "stripe",
        "reference_id": stripe_data["session_id"],
    }
    confirm_res = await client.post(
        "/api/v1/billing/confirm", json=confirm_req, headers=headers
    )
    assert confirm_res.status_code == 200
    assert "success" in confirm_res.json()["status"]

    # 6. Fetch updated user context and verify subscription tier has changed to Pro
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["subscription_tier"] == "pro"

    # 7. Check database tenant row state directly
    tenant_id = me_data["tenant_id"]
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await db_session.execute(stmt)
    tenant = result.scalars().first()
    assert tenant is not None
    assert tenant.subscription_tier == "pro"
    assert tenant.billing_provider == "stripe"
    assert tenant.billing_subscription_id == stripe_data["session_id"]
    assert tenant.billing_customer_id == f"cus_stripe_{tenant.id}"
