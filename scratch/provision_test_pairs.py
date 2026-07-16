import asyncio
import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from atlas.database.session import SessionLocal
from atlas.database.models import Candidate, User
from atlas.services.auth import AuthService

async def main():
    async with SessionLocal() as db:
        auth_service = AuthService(db)
        
        # Define accounts
        pairs = [
            {
                "recruiter_email": "recruiter.billing@gmail.com",
                "candidate_email": "candidate.billing@gmail.com",
                "tenant_id": 3
            },
            {
                "recruiter_email": "recruiter.test@gmail.com",
                "candidate_email": "candidate.test@gmail.com",
                "tenant_id": 4
            }
        ]
        
        for pair in pairs:
            c_email = pair["candidate_email"]
            t_id = pair["tenant_id"]
            
            # 1. Create candidate user account if not exists
            user = await auth_service.repo.get_by_email(c_email)
            if not user:
                hashed_pw = AuthService.hash_password("password123")
                user = User(
                    email=c_email,
                    hashed_password=hashed_pw,
                    role="recruiter", # Roles are selectable on screen anyway
                    tenant_id=t_id
                )
                db.add(user)
                await db.commit()
                print(f"Created Candidate User: {c_email} (Password: password123) for tenant_id {t_id}")
            else:
                print(f"Candidate User {c_email} already exists")
                
            # 2. Find Candidate profile for this tenant and update email to match
            result = await db.execute(
                select(Candidate).filter(Candidate.tenant_id == t_id)
            )
            candidates = result.scalars().all()
            for cand in candidates:
                cand.email = c_email
                cand.name = "Jane Doe (Test Candidate)"
                db.add(cand)
            await db.commit()
            print(f"Updated Jane Doe candidate profile email to '{c_email}' for tenant_id {t_id}")

if __name__ == "__main__":
    asyncio.run(main())
