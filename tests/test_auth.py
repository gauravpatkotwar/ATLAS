import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.services.auth import AuthService


@pytest.mark.asyncio
async def test_auth_service_methods(db_session: AsyncSession):
    """Tests password hashing, verification, token encoding/decoding, and user lookup."""
    auth_service = AuthService(db_session)

    # Create user
    user = await auth_service.register_user(
        email="test@example.com",
        password="password123",
        role="recruiter",
        org_name="Test Org",
    )
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == "recruiter"
    assert user.is_active is True

    # Try duplicate registration
    with pytest.raises(ValueError):
        await auth_service.register_user(
            email="test@example.com", password="newpassword", org_name="Other Org"
        )

    # Authenticate success
    authenticated = await auth_service.authenticate_user(
        email="test@example.com", password="password123"
    )
    assert authenticated is not None
    assert authenticated.id == user.id

    # Authenticate failure
    wrong_pw = await auth_service.authenticate_user(
        email="test@example.com", password="wrongpassword"
    )
    assert wrong_pw is None

    # Access token verification
    token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    decoded = auth_service.decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "test@example.com"
    assert decoded["role"] == "recruiter"


@pytest.mark.asyncio
async def test_auth_endpoints(client: AsyncClient):
    """Verifies register, login, and authorization routes lifecycle."""
    # 1. Register candidate account
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "mypassword",
            "role": "recruiter",
            "org_name": "Acme Inc",
        },
    )
    assert reg_res.status_code == 201
    assert reg_res.json()["email"] == "user@example.com"
    assert reg_res.json()["role"] == "recruiter"

    # 2. Login OAuth2
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "mypassword"},
    )
    assert login_res.status_code == 200
    res_data = login_res.json()
    token = res_data["access_token"]
    assert res_data["token_type"] == "bearer"

    # 3. Read profile
    me_res = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "user@example.com"
