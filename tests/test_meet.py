import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.services.auth import AuthService


@pytest.mark.asyncio
async def test_meeting_room_signaling_flow(
    client: AsyncClient, db_session: AsyncSession
):
    """Tests the Atlas Meet multi-party video conferencing signaling API."""
    # Setup test recruiter
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="recruiter.meet@example.com", password="password123", org_name="Meet Org"
    )
    token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a meeting room
    create_res = await client.post("/api/v1/meet/create", headers=headers)
    assert create_res.status_code == 200
    room_code = create_res.json()["room_code"]
    assert room_code is not None

    # 2. Host joins the room
    join_host_res = await client.post(
        f"/api/v1/meet/join/{room_code}",
        json={"participant_id": "host_user", "name": "Host Recruiter"}
    )
    assert join_host_res.status_code == 200
    assert join_host_res.json()["status"] == "success"
    assert len(join_host_res.json()["other_participants"]) == 0

    # 3. Guest joins the room
    join_guest_res = await client.post(
        f"/api/v1/meet/join/{room_code}",
        json={"participant_id": "guest_user", "name": "Guest Candidate"}
    )
    assert join_guest_res.status_code == 200
    assert join_guest_res.json()["status"] == "success"
    assert len(join_guest_res.json()["other_participants"]) == 1
    assert join_guest_res.json()["other_participants"][0]["id"] == "host_user"

    # 4. Host polls the room, detecting the new guest
    poll_host = await client.get(f"/api/v1/meet/poll/{room_code}/host_user")
    assert poll_host.status_code == 200
    assert len(poll_host.json()["participants"]) == 2
    assert any(p["id"] == "guest_user" for p in poll_host.json()["participants"])

    # 5. Host sends SDP offer to the guest
    signal_res = await client.post(
        f"/api/v1/meet/signal/{room_code}",
        json={
            "sender_id": "host_user",
            "target_id": "guest_user",
            "type": "offer",
            "data": "sdp_mock_data_for_offer"
        }
    )
    assert signal_res.status_code == 200
    assert signal_res.json()["status"] == "success"

    # 6. Guest polls and retrieves the SDP offer
    poll_guest = await client.get(f"/api/v1/meet/poll/{room_code}/guest_user")
    assert poll_guest.status_code == 200
    assert len(poll_guest.json()["signals"]) == 1
    assert poll_guest.json()["signals"][0]["sender_id"] == "host_user"
    assert poll_guest.json()["signals"][0]["type"] == "offer"
    assert poll_guest.json()["signals"][0]["data"] == "sdp_mock_data_for_offer"

    # 7. Guest leaves the room
    leave_res = await client.post(f"/api/v1/meet/leave/{room_code}/guest_user")
    assert leave_res.status_code == 200

    # 8. Host polls and detects guest has left
    poll_host_after = await client.get(f"/api/v1/meet/poll/{room_code}/host_user")
    assert poll_host_after.status_code == 200
    assert len(poll_host_after.json()["participants"]) == 1
    assert poll_host_after.json()["participants"][0]["id"] == "host_user"
