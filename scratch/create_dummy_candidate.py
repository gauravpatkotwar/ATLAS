import asyncio
import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.ext.asyncio import AsyncSession
from atlas.database.session import SessionLocal
from atlas.database.models import Candidate, User
from atlas.services.candidate import CandidateService
from atlas.services.auth import AuthService

async def main():
    async with SessionLocal() as db:
        # 1. Create a dummy recruiter (if not already exists)
        email = "recruiter.test@gmail.com"
        password = "password123"
        org_name = "Test Staging Org"
        
        auth_service = AuthService(db)
        recruiter = await auth_service.repo.get_by_email(email)
        
        if not recruiter:
            try:
                recruiter = await auth_service.register_user(
                    email=email,
                    password=password,
                    role="recruiter",
                    org_name=org_name
                )
                print(f"Created dummy recruiter: {email} (Password: {password}) associated with '{org_name}' (Tenant ID: {recruiter.tenant_id})")
            except Exception as e:
                print(f"Failed to create recruiter: {e}")
                return
        else:
            print(f"Recruiter {email} already exists (Tenant ID: {recruiter.tenant_id})")
        
        # 2. We will create dummy candidates for:
        # - tenant_id = 3 (recruiter.billing@gmail.com)
        # - tenant_id = recruiter.tenant_id (the new dummy recruiter)
        # - tenant_id = 1 (local dev tenant)
        tenants = list(set([1, 3, recruiter.tenant_id]))
        
        for t_id in tenants:
            candidate = Candidate(
                tenant_id=t_id,
                name="Jane Doe",
                email="jane.doe@example.com",
                phone="+1-555-0199",
                location="San Francisco, CA",
                skills=["Python", "React", "TypeScript", "FastAPI", "Docker", "WebRTC"],
                summary="Full Stack Software Engineer with 5+ years of experience building secure SaaS applications, collaborative real-time video/VoIP tools, and generative AI pipelines.",
                experience=[
                    {
                        "company": "Tech Innovators Inc",
                        "role": "Senior Engineer",
                        "duration": "2023 - Present",
                        "description": "Architected WebRTC real-time signaling backend. Built frontend React client."
                    }
                ],
                education=[
                    {
                        "school": "Stanford University",
                        "degree": "B.S. Computer Science",
                        "year": "2020"
                    }
                ],
                linkedin="https://linkedin.com/in/janedoe",
                github="https://github.com/janedoe",
                portfolio="https://janedoe.dev"
            )
            
            db.add(candidate)
            await db.commit()
            await db.refresh(candidate)
            
            # Index candidate in vector store
            service = CandidateService(db, tenant_id=t_id)
            await service.reindex_candidate(candidate)
            print(f"Created candidate: {candidate.name} (ID: {candidate.id}) for tenant_id {t_id}")

if __name__ == "__main__":
    asyncio.run(main())
