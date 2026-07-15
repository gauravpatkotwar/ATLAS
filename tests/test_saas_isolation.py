import io
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.services.auth import AuthService
from atlas.vector.store import vector_store


@pytest.mark.asyncio
async def test_tenant_data_isolation_and_quotas(
    client: AsyncClient, db_session: AsyncSession
):
    """Verifies that recruiters from different organizations have isolated candidate scopes and billing limits."""
    # Setup Tenant A recruiter
    auth_service = AuthService(db_session)
    user_a = await auth_service.register_user(
        email="recruiter_a@company-a.com", password="password123", org_name="Tenant A"
    )
    token_a = auth_service.create_access_token(
        data={"sub": user_a.email, "role": user_a.role}
    )
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup Tenant B recruiter
    user_b = await auth_service.register_user(
        email="recruiter_b@company-b.com", password="password123", org_name="Tenant B"
    )
    token_b = auth_service.create_access_token(
        data={"sub": user_b.email, "role": user_b.role}
    )
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Reset vector store index
    vector_store.clear()

    # 1. Tenant A uploads a candidate
    file_a = b"Candidate Alice. Skills: Python, FastAPI. Senior Backend Developer at Netflix."
    files_a = {"file": ("alice.txt", io.BytesIO(file_a), "text/plain")}
    res_a = await client.post(
        "/api/v1/candidates/upload", files=files_a, headers=headers_a
    )
    assert res_a.status_code == 201
    _alice_id = res_a.json()["id"]

    # 2. Tenant B uploads a candidate
    file_b = (
        b"Candidate Bob. Skills: Rust, WebAssembly. Systems developer at Cloudflare."
    )
    files_b = {"file": ("bob.txt", io.BytesIO(file_b), "text/plain")}
    res_b = await client.post(
        "/api/v1/candidates/upload", files=files_b, headers=headers_b
    )
    assert res_b.status_code == 201
    bob_id = res_b.json()["id"]

    # 3. Verify Tenant A only retrieves Alice
    list_a = await client.get("/api/v1/candidates", headers=headers_a)
    assert list_a.status_code == 200
    candidates_a = list_a.json()
    assert len(candidates_a) == 1
    assert candidates_a[0]["name"] == "John Doe"  # Mock parser default

    # 4. Verify Tenant A cannot retrieve Bob's profile directly (404 isolation)
    get_bob = await client.get(f"/api/v1/candidates/{bob_id}", headers=headers_a)
    assert get_bob.status_code == 404

    # 5. Verify Semantic Search is Tenant-isolated
    # Search Rust skills from Tenant A context
    search_a = await client.post(
        "/api/v1/search",
        json={"query": "Rust WebAssembly Cloudflare Developer", "top_k": 5},
        headers=headers_a,
    )
    assert search_a.status_code == 200
    search_results_a = search_a.json()
    # Even though Bob (Rust developer) is in FAISS, search should not return him to Tenant A!
    assert all(c["id"] != bob_id for c in search_results_a)

    # 6. Verify Free Tier Limit (Max 5 candidate uploads)
    # Tenant A currently has 1 candidate upload. Upload 4 more.
    for i in range(4):
        f = {"file": (f"candidate_{i}.txt", io.BytesIO(file_a), "text/plain")}
        res = await client.post("/api/v1/candidates/upload", files=f, headers=headers_a)
        assert res.status_code == 201

    # The 6th upload attempt for Tenant A must fail (403 Forbidden)
    f_limit = {"file": ("limit.txt", io.BytesIO(file_a), "text/plain")}
    res_limit = await client.post(
        "/api/v1/candidates/upload", files=f_limit, headers=headers_a
    )
    assert res_limit.status_code == 403
    assert "SaaS Plan Limit" in res_limit.json()["detail"]
