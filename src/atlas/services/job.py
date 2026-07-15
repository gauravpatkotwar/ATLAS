import logging
from typing import List, Dict, Any, Optional, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from atlas.repositories.job import JobRepository
from atlas.repositories.candidate import CandidateRepository
from atlas.database.models import Job, Tenant
from atlas.vector.store import vector_store
from atlas.ai.factory import AIProviderFactory

logger = logging.getLogger(__name__)


class JobService:
    """Service handling multi-tenant Job CRUD, vector recommenders, and quota verifications."""

    def __init__(self, db: AsyncSession, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = JobRepository(db, tenant_id)
        self.candidate_repo = CandidateRepository(db, tenant_id)

    async def get_job(self, job_id: int) -> Optional[Job]:
        return await self.repo.get(job_id)

    async def get_jobs(self, skip: int = 0, limit: int = 100) -> List[Job]:
        return await self.repo.get_all(skip, limit)

    async def verify_job_quota(self) -> None:
        """Checks if active job count violates the Tenant's billing tier limitations."""
        result = await self.db.execute(
            select(Tenant).filter(Tenant.id == self.tenant_id)
        )
        tenant = result.scalars().first()
        if not tenant:
            raise ValueError("Access Denied: Tenant workspace does not exist.")

        tier = tenant.subscription_tier.lower()
        if tier == "free":
            max_limit = 2
        elif tier == "pro":
            max_limit = 10
        else:
            return  # Enterprise tier has unlimited job creation quotas

        count_result = await self.db.execute(
            select(func.count(Job.id))
            .filter(Job.tenant_id == self.tenant_id)
            .filter(Job.is_active)
        )
        count = count_result.scalar() or 0

        if count >= max_limit:
            raise PermissionError(
                f"SaaS Plan Limit: '{tier}' plan permits a maximum of {max_limit} active job postings. "
                "Please upgrade your workspace tier."
            )

    async def create_job(self, obj_in: dict) -> Job:
        """Publishes a new job specification, verifying billing quotas first."""
        await self.verify_job_quota()

        job = Job(
            tenant_id=self.tenant_id,
            title=obj_in.get("title", "Untitled Job"),
            description=obj_in.get("description", ""),
            required_skills=obj_in.get("required_skills") or [],
            salary=obj_in.get("salary"),
            location=obj_in.get("location"),
            experience_years=obj_in.get("experience_years", 0),
            employment_type=obj_in.get("employment_type"),
            is_active=obj_in.get("is_active", True),
        )
        return await self.repo.create(job)

    async def update_job(self, job_id: int, obj_in: dict) -> Job:
        db_obj = await self.repo.get(job_id)
        if not db_obj:
            raise ValueError(f"Job with ID {job_id} not found.")
        return await self.repo.update(db_obj, obj_in)

    async def delete_job(self, job_id: int) -> bool:
        return await self.repo.delete(job_id)

    async def get_recommendations_for_job(
        self, job_id: int, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Finds candidate recommendations scoped strictly to this tenant's candidates pool."""
        job = await self.repo.get(job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found.")

        skills_str = ", ".join(job.required_skills or [])
        search_text = f"Job Profile. Title: {job.title}. Description: {job.description}. Required Skills: {skills_str}."

        try:
            embed_provider = AIProviderFactory.get_embedding_provider()
            job_embedding = await embed_provider.generate_embedding(search_text)
        except Exception as e:
            logger.error(f"Job embedding generation failed: {e}")
            job_embedding = []

        if not job_embedding:
            # Fallback: display candidate list with zero similarity if Ollama is offline
            candidates = await self.candidate_repo.get_all(limit=50)
            return [
                {
                    "candidate": c,
                    "similarity_score": 0.0,
                    "skills_match_ratio": 0.0,
                    "explanation": "AI embedding service offline. Defaulting candidates list.",
                }
                for c in candidates
            ]

        # Search candidate vectors in FAISS
        match_results = vector_store.search(job_embedding, top_k=top_k)

        recommendations = []
        ai_provider = AIProviderFactory.get_ai_provider()

        for candidate_id, similarity_score in match_results:
            # get() will automatically filter candidate by this tenant's ID!
            # This guarantees absolute multi-tenant vector security isolation!
            candidate = await self.candidate_repo.get(candidate_id)
            if not candidate:
                continue

            job_skills = set(s.lower() for s in (job.required_skills or []))
            candidate_skills = set(s.lower() for s in (candidate.skills or []))

            skills_match_ratio = 0.0
            if job_skills:
                skills_match_ratio = len(
                    job_skills.intersection(candidate_skills)
                ) / len(job_skills)

            candidate_payload = {
                "name": candidate.name,
                "skills": candidate.skills,
                "summary": candidate.summary,
                "experience": candidate.experience,
            }
            job_payload = {
                "title": job.title,
                "description": job.description,
                "required_skills": job.required_skills,
            }

            try:
                explanation = await ai_provider.explain_recommendation(
                    candidate_payload, job_payload
                )
            except Exception as e:
                logger.warning(
                    f"Could not generate AI explanation for candidate {candidate.id}: {e}"
                )
                explanation = "AI matching explanation is temporarily unavailable."

            recommendations.append(
                {
                    "candidate": candidate,
                    "similarity_score": similarity_score,
                    "skills_match_ratio": skills_match_ratio,
                    "explanation": explanation,
                }
            )

        # Sort recommendations by similarity score descending
        recommendations.sort(
            key=lambda x: cast(float, x["similarity_score"]), reverse=True
        )
        return recommendations
