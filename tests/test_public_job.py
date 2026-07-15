import io
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.services.auth import AuthService
from atlas.database.models import Candidate
from sqlalchemy import select


@pytest.mark.asyncio
async def test_public_job_details_and_apply(
    client: AsyncClient, db_session: AsyncSession
):
    """Tests viewing a job listing publicly and applying without headers."""
    auth_service = AuthService(db_session)
    user = await auth_service.register_user(
        email="recruiter_public_test@example.com", password="password123", org_name="Public Test Org"
    )
    token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a Job using the recruiter session
    job_payload = {
        "title": "Public Frontend Engineer",
        "description": "Looking for a seasoned CSS/HTML dev.",
        "required_skills": ["CSS", "HTML"],
        "salary": "110k",
        "location": "Remote",
        "experience_years": 3,
        "employment_type": "Full-time",
    }
    job_res = await client.post("/api/v1/jobs", json=job_payload, headers=headers)
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]
    tenant_id = job_res.json()["tenant_id"]

    # 2. Get Public Job Spec (No Auth Headers)
    public_res = await client.get(f"/api/v1/jobs/{job_id}/public")
    assert public_res.status_code == 200
    public_data = public_res.json()
    assert public_data["title"] == "Public Frontend Engineer"
    assert public_data["salary"] == "110k"

    # 3. Apply to Public Job (No Auth Headers)
    file_bytes = b"Jane Candidate\nExperienced with CSS and HTML layouts."
    apply_payload = {
        "email": "jane.candidate@gmail.com",
        "name": "Jane Candidate",
        "phone": "+1234567890",
    }
    files = {"file": ("resume.txt", io.BytesIO(file_bytes), "text/plain")}
    apply_res = await client.post(
        f"/api/v1/jobs/{job_id}/apply",
        data=apply_payload,
        files=files,
    )
    assert apply_res.status_code == 201
    assert apply_res.json()["message"] == "Application submitted successfully!"

    # 4. Verify candidate got created under correct Tenant ID
    candidate_id = apply_res.json()["candidate_id"]
    stmt = select(Candidate).where(Candidate.id == candidate_id)
    result = await db_session.execute(stmt)
    candidate = result.scalars().first()
    assert candidate is not None
    assert candidate.name == "Jane Candidate"
    assert candidate.email == "jane.candidate@gmail.com"
    assert candidate.tenant_id == tenant_id
