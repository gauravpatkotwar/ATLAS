import io
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.services.auth import AuthService
from atlas.vector.store import vector_store


@pytest.mark.asyncio
async def test_candidates_workflow_and_crud(
    client: AsyncClient, db_session: AsyncSession
):
    """Tests resume upload transaction steps and complete candidate profile lifecycle."""
    # Setup recruiter profile
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="recruiter@example.com", password="password123", org_name="Candidate Org"
    )
    token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Reset index files
    vector_store.clear()

    # 1. Upload mock text resume
    file_bytes = b"John Doe\nPython developer. Skills: Python, SQL. Experienced with Django and FastAPI."
    files = {"file": ("resume.txt", io.BytesIO(file_bytes), "text/plain")}

    upload_res = await client.post(
        "/api/v1/candidates/upload", files=files, headers=headers
    )
    assert upload_res.status_code == 201

    cand_data = upload_res.json()
    assert cand_data["name"] == "John Doe"
    assert "Python" in cand_data["skills"]
    candidate_id = cand_data["id"]

    # Verify candidate vector added to FAISS index
    assert vector_store.index.ntotal == 1

    # 2. List all candidates
    list_res = await client.get("/api/v1/candidates", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 3. Read single candidate
    get_res = await client.get(f"/api/v1/candidates/{candidate_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "John Doe"

    # 4. Update candidate details
    update_res = await client.put(
        f"/api/v1/candidates/{candidate_id}",
        json={"name": "John Changed", "skills": ["Python", "FastAPI", "React"]},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "John Changed"
    assert "React" in update_res.json()["skills"]

    # 5. Delete candidate
    del_res = await client.delete(f"/api/v1/candidates/{candidate_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify candidate vector is dynamically deleted from FAISS
    assert vector_store.index.ntotal == 0

    # 6. Read deleted candidate should return 404
    get_del_res = await client.get(
        f"/api/v1/candidates/{candidate_id}", headers=headers
    )
    assert get_del_res.status_code == 404
