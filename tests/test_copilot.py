import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.services.auth import AuthService


@pytest.mark.asyncio
async def test_copilot_chat_history_persistence(
    client: AsyncClient, db_session: AsyncSession
):
    """Tests loading, persistence, and wiping of user copilot conversations."""
    # Setup authenticated user session
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="recruiter_chat@example.com",
        password="password123",
        org_name="Copilot Org",
    )
    token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch history (should be empty initially)
    history_res = await client.get("/api/v1/copilot/history", headers=headers)
    assert history_res.status_code == 200
    assert len(history_res.json()) == 0

    # 2. Send query (registers user message and mock assistant reply in DB)
    chat_res = await client.post(
        "/api/v1/copilot/chat",
        json={"query": "Who is best for python?"},
        headers=headers,
    )
    assert chat_res.status_code == 200
    assert "Mock Copilot response" in chat_res.json()["reply"]

    # 3. Retrieve history (should contain 2 messages: user query and assistant reply)
    history_res2 = await client.get("/api/v1/copilot/history", headers=headers)
    assert history_res2.status_code == 200
    logs = history_res2.json()
    assert len(logs) == 2
    assert logs[0]["role"] == "user"
    assert logs[0]["content"] == "Who is best for python?"
    assert logs[1]["role"] == "assistant"
    assert "Mock Copilot response" in logs[1]["content"]

    # 4. Clear chat log database records
    clear_res = await client.delete("/api/v1/copilot/history", headers=headers)
    assert clear_res.status_code == 204

    # 5. Fetch history again (should be wiped clean)
    history_res3 = await client.get("/api/v1/copilot/history", headers=headers)
    assert history_res3.status_code == 200
    assert len(history_res3.json()) == 0
