import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_sso_endpoints(client: AsyncClient):
    """Verifies SSO/SAML configuration CRUD endpoints and mock authentication flow."""
    # 1. Register and login to get auth token
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "hr@acme.com",
            "password": "acmepassword",
            "role": "recruiter",
            "org_name": "Acme Corp",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "hr@acme.com", "password": "acmepassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get initial SSO Config (should be empty/null or return status with null properties)
    get_res = await client.get("/api/v1/sso/config", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json() is None or get_res.json().get("idp_entity_id") is None

    # 3. Update/Save SAML SSO configuration
    update_res = await client.post(
        "/api/v1/sso/config",
        headers=headers,
        json={
            "idp_entity_id": "https://okta.acme.com/atlas-entity",
            "idp_sso_url": "https://okta.acme.com/atlas-sso",
            "x509_certificate": "PEM_CERT_CONTENT_STUB",
        },
    )
    assert update_res.status_code == 200
    assert update_res.json()["idp_entity_id"] == "https://okta.acme.com/atlas-entity"
    assert update_res.json()["idp_sso_url"] == "https://okta.acme.com/atlas-sso"
    assert update_res.json()["x509_certificate"] == "PEM_CERT_CONTENT_STUB"

    # 4. Get active configuration to verify persistence
    get_res = await client.get("/api/v1/sso/config", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["idp_entity_id"] == "https://okta.acme.com/atlas-entity"

    # 5. Mock SSO Login callback endpoint using organization and corporate email
    sso_login_res = await client.post(
        "/api/v1/sso/login-mock",
        json={"email": "employee@acme.com", "org_name": "Acme Corp"},
    )
    assert sso_login_res.status_code == 200
    assert "access_token" in sso_login_res.json()
    assert sso_login_res.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_developer_endpoints(client: AsyncClient):
    """Verifies developer tools for creating API keys and webhooks."""
    # 1. Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dev@acme.com",
            "password": "devpassword",
            "role": "recruiter",
            "org_name": "Acme Corp",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "dev@acme.com", "password": "devpassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create API key
    key_res = await client.post(
        "/api/v1/developer/keys",
        headers=headers,
        json={"name": "ATS Partner Key"},
    )
    assert key_res.status_code in (200, 201)
    key_data = key_res.json()
    assert key_data["name"] == "ATS Partner Key"
    assert "raw_key" in key_data
    assert key_data["key_prefix"].startswith("at_")

    # 3. List active API keys
    list_keys_res = await client.get("/api/v1/developer/keys", headers=headers)
    assert list_keys_res.status_code == 200
    assert len(list_keys_res.json()) == 1
    assert list_keys_res.json()[0]["name"] == "ATS Partner Key"

    # 4. Revoke/Delete API Key
    key_id = key_data["id"]
    del_key_res = await client.delete(f"/api/v1/developer/keys/{key_id}", headers=headers)
    assert del_key_res.status_code in (200, 204)

    # 5. List keys again to confirm revoked
    list_keys_res = await client.get("/api/v1/developer/keys", headers=headers)
    assert len(list_keys_res.json()) == 0

    # 6. Create Webhook endpoint
    webhook_res = await client.post(
        "/api/v1/developer/webhooks",
        headers=headers,
        json={
            "url": "https://callback.acme.com/hooks/candidate",
            "secret_token": "whsec_supersecret_token",
            "events": ["candidate.created", "candidate.hired"],
        },
    )
    assert webhook_res.status_code in (200, 201)
    webhook_data = webhook_res.json()
    assert webhook_data["url"] == "https://callback.acme.com/hooks/candidate"
    assert webhook_data["events"] == ["candidate.created", "candidate.hired"]

    # 7. List webhooks
    list_wh_res = await client.get("/api/v1/developer/webhooks", headers=headers)
    assert len(list_wh_res.json()) == 1

    # 8. Delete Webhook
    wh_id = webhook_data["id"]
    del_wh_res = await client.delete(f"/api/v1/developer/webhooks/{wh_id}", headers=headers)
    assert del_wh_res.status_code in (200, 204)


@pytest.mark.asyncio
async def test_automations_endpoints(client: AsyncClient):
    """Verifies CRUD rules and toggle states for automated recruiter workflows."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "auto@acme.com",
            "password": "autopassword",
            "role": "recruiter",
            "org_name": "Acme Corp",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "auto@acme.com", "password": "autopassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Workflow Rule
    wf_res = await client.post(
        "/api/v1/automations/workflows",
        headers=headers,
        json={
            "name": "Send rejection email",
            "trigger_event": "candidate_status_changed",
            "conditions": {"status": "rejected"},
            "action_type": "send_email",
            "action_payload": {"email": "recruiter@acme.com"},
        },
    )
    assert wf_res.status_code in (200, 201)
    wf_data = wf_res.json()
    assert wf_data["name"] == "Send rejection email"
    assert wf_data["is_active"] is True

    # 2. List Workflows
    list_wf = await client.get("/api/v1/automations/workflows", headers=headers)
    assert len(list_wf.json()) == 1

    # 3. Toggle Workflow active state
    wf_id = wf_data["id"]
    toggle_res = await client.post(f"/api/v1/automations/workflows/{wf_id}/toggle", headers=headers)
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_active"] is False

    # 4. Delete Workflow Rule
    del_wf = await client.delete(f"/api/v1/automations/workflows/{wf_id}", headers=headers)
    assert del_wf.status_code in (200, 204)


@pytest.mark.asyncio
async def test_integrations_endpoints(client: AsyncClient):
    """Verifies connection toggle integrations endpoints."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "int@acme.com",
            "password": "intpassword",
            "role": "recruiter",
            "org_name": "Acme Corp",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "int@acme.com", "password": "intpassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List Integrations (empty initially, or auto-created defaults depending on seed)
    list_int = await client.get("/api/v1/integrations", headers=headers)
    assert list_int.status_code == 200

    # 2. Toggle integration (connect slack)
    toggle_res = await client.post(
        "/api/v1/integrations/toggle",
        headers=headers,
        json={"provider_name": "slack"},
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["provider_name"] == "slack"
    assert toggle_res.json()["is_active"] is True

    # 3. List integrations again to verify state
    list_int = await client.get("/api/v1/integrations", headers=headers)
    slack_int = next(i for i in list_int.json() if i["provider_name"] == "slack")
    assert slack_int["is_active"] is True

    # 4. Toggle slack integration off
    toggle_off = await client.post(
        "/api/v1/integrations/toggle",
        headers=headers,
        json={"provider_name": "slack"},
    )
    assert toggle_off.json()["is_active"] is False


@pytest.mark.asyncio
async def test_analytics_endpoints(client: AsyncClient):
    """Verifies analytics funnel status retrieval and mock time to hire metrics."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@acme.com",
            "password": "analystpassword",
            "role": "recruiter",
            "org_name": "Acme Corp",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "analyst@acme.com", "password": "analystpassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get recruitment throughput funnel candidate counts
    funnel_res = await client.get("/api/v1/analytics/throughput", headers=headers)
    assert funnel_res.status_code == 200
    assert "applied" in funnel_res.json()
    assert "offered" in funnel_res.json()

    # 2. Get average time to hire statistics
    tth_res = await client.get("/api/v1/analytics/time-to-hire", headers=headers)
    assert tth_res.status_code == 200
    assert "total_days" in tth_res.json()
    assert "screening_days" in tth_res.json()


@pytest.mark.asyncio
async def test_gemini_provider():
    """Validates the GeminiProvider REST requests, parsing logic, and fallback structures."""
    from atlas.ai.gemini import GeminiProvider
    from unittest.mock import AsyncMock, MagicMock

    provider = GeminiProvider(api_key="test_stub_key")

    # Use MagicMock (sync) for response objects — httpx responses are NOT awaitable
    mock_response_generate = MagicMock()
    mock_response_generate.status_code = 200
    mock_response_generate.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "```json\n{\n  \"name\": \"Alice Doe\",\n  \"email\": \"alice@example.com\"\n}\n```"
                        }
                    ]
                }
            }
        ]
    }

    mock_response_embed = MagicMock()
    mock_response_embed.status_code = 200
    mock_response_embed.json.return_value = {"embedding": {"values": [0.125, -0.5, 0.9, 0.0]}}

    async def side_effect(url, **kwargs):
        if "embedContent" in url:
            return mock_response_embed
        return mock_response_generate

    provider.client.post = AsyncMock(side_effect=side_effect)

    # 1. Test resume parsing data extraction
    parsed_data = await provider.extract_candidate_data("Resume Text: Alice Doe")
    assert parsed_data["name"] == "Alice Doe"
    assert parsed_data["email"] == "alice@example.com"

    # 2. Test text embedding generation
    embedding = await provider.generate_embedding("Embed this text")
    assert embedding == [0.125, -0.5, 0.9, 0.0]

    await provider.close()

