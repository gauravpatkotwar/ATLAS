import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.services.auth import AuthService


@pytest.mark.asyncio
async def test_calling_signaling_endpoints(
    client: AsyncClient, db_session: AsyncSession
):
    """Tests the in-memory WebRTC call signaling endpoints."""
    # Setup recruiter
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="recruiter.caller@example.com", password="password123", org_name="Call Org"
    )
    token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    candidate_id = 999  # Mock candidate ID

    # 1. Check initial call status is idle
    status_res = await client.get(f"/api/v1/candidates/call/status/{candidate_id}")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "idle"

    # 2. Recruiter initiates call
    init_res = await client.post(
        "/api/v1/candidates/call/initiate",
        json={"candidate_id": candidate_id, "sdp_offer": "mock-sdp-offer-data"},
        headers=headers
    )
    assert init_res.status_code == 200
    assert init_res.json()["status"] == "success"
    assert init_res.json()["call"]["status"] == "ringing"
    assert init_res.json()["call"]["sdp_offer"] == "mock-sdp-offer-data"

    # 3. Check status is now ringing
    status_res = await client.get(f"/api/v1/candidates/call/status/{candidate_id}")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "ringing"
    assert status_res.json()["sdp_offer"] == "mock-sdp-offer-data"

    # 4. Candidate accepts the call
    resp_res = await client.post(
        f"/api/v1/candidates/call/respond/{candidate_id}",
        json={"status": "accepted", "sdp_answer": "mock-sdp-answer-data"}
    )
    assert resp_res.status_code == 200
    assert resp_res.json()["call"]["status"] == "accepted"
    assert resp_res.json()["call"]["sdp_answer"] == "mock-sdp-answer-data"

    # 5. End call
    end_res = await client.post(
        f"/api/v1/candidates/call/respond/{candidate_id}",
        json={"status": "ended"}
    )
    assert end_res.status_code == 200
    assert end_res.json()["call"]["status"] == "ended"
