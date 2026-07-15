import io
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.services.auth import AuthService
from atlas.vector.store import vector_store


@pytest.mark.asyncio
async def test_jobs_crud_and_recommendations(
    client: AsyncClient, db_session: AsyncSession
):
    """Tests job management and recommendation matching."""
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="recruiter_jobs@example.com", password="password123", org_name="Jobs Org"
    )
    token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    vector_store.clear()

    # 1. Seed candidate
    file_bytes = (
        b"John Doe\nPython developer. Skills: Python, SQL. Experienced with Django."
    )
    files = {"file": ("resume.txt", io.BytesIO(file_bytes), "text/plain")}
    upload_res = await client.post(
        "/api/v1/candidates/upload", files=files, headers=headers
    )
    assert upload_res.status_code == 201

    # 2. Create Job
    job_payload = {
        "title": "Senior Python Developer",
        "description": "Looking for a seasoned backend engineer with expert Python skills.",
        "required_skills": ["Python", "Django"],
        "salary": "130k",
        "location": "San Francisco",
        "experience_years": 5,
        "employment_type": "Full-time",
    }
    job_res = await client.post("/api/v1/jobs", json=job_payload, headers=headers)
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # 3. List jobs
    list_res = await client.get("/api/v1/jobs", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Get Job by ID
    get_res = await client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Senior Python Developer"

    # 5. Fetch recommendations
    rec_res = await client.get(
        f"/api/v1/jobs/{job_id}/recommendations", headers=headers
    )
    assert rec_res.status_code == 200
    recs = rec_res.json()
    assert len(recs) == 1
    assert recs[0]["candidate"]["name"] == "John Doe"
    assert (
        recs[0]["skills_match_ratio"] == 0.5
    )  # Python matches, Django matches (wait, Django is not in John's explicit mock skills, but python is. 1 out of 2 is 0.5)
    assert recs[0]["explanation"] is not None
