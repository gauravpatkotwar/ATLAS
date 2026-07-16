import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.services.auth import AuthService


@pytest.mark.asyncio
async def test_developer_marketplace_flows(
    client: AsyncClient, db_session: AsyncSession
):
    """Tests the Developer Software & Services Marketplace endpoints."""
    # Setup test recruiter
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="developer.meet@example.com", password="password123", org_name="Dev Org"
    )
    token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List products (should be empty initially)
    list_res = await client.get("/api/v1/marketplace/products", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 0

    # 2. Publish a new product
    pub_payload = {
        "name": "ATLAS Slack Integration Hook",
        "description": "Publishes real-time recruiter alerts to your Slack workspaces.",
        "price": 19.99,
        "category": "software",
        "download_url": "https://github.com/atlas-awi/slack-plugin"
    }
    pub_res = await client.post("/api/v1/marketplace/products", json=pub_payload, headers=headers)
    assert pub_res.status_code == 200
    prod_data = pub_res.json()
    assert prod_data["name"] == "ATLAS Slack Integration Hook"
    assert prod_data["price"] == 19.99
    assert prod_data["category"] == "software"
    assert prod_data["author_email"] == "developer.meet@example.com"
    prod_id = prod_data["id"]

    # 3. List products again (should contain the newly published product)
    list_res2 = await client.get("/api/v1/marketplace/products", headers=headers)
    assert list_res2.status_code == 200
    assert len(list_res2.json()) == 1
    assert list_res2.json()[0]["id"] == prod_id

    # 4. Purchase the product
    purchase_res = await client.post(f"/api/v1/marketplace/products/{prod_id}/purchase", headers=headers)
    assert purchase_res.status_code == 200
    assert purchase_res.json()["status"] == "success"

    # 5. List purchases (should show the purchased product in inventory)
    purch_list = await client.get("/api/v1/marketplace/purchases", headers=headers)
    assert purch_list.status_code == 200
    assert len(purch_list.json()) == 1
    assert purch_list.json()[0]["product_id"] == prod_id
    assert purch_list.json()[0]["product"]["name"] == "ATLAS Slack Integration Hook"
