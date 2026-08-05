import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from atlas.repositories.candidate import CandidateRepository
from atlas.database.models import Candidate, Tenant
from atlas.vector.store import vector_store
from atlas.workflow.engine import WorkflowEngine, WorkflowContext
from atlas.workflow.resume_pipeline import (
    ValidateFileStep,
    SaveFileStep,
    ParseResumeStep,
    AIExtractCandidateStep,
    CreateCandidateRepoStep,
    GenerateCandidateEmbeddingStep,
    IndexCandidateVectorStep,
    AuditLogStep,
)
from atlas.ai.factory import AIProviderFactory

logger = logging.getLogger(__name__)


class CandidateService:
    """Service encapsulating Candidate CRUD, FAISS vector synchronization, and multi-tenant parsing pipelines."""

    def __init__(self, db: AsyncSession, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = CandidateRepository(db, tenant_id)

    async def get_candidate(self, candidate_id: int) -> Optional[Candidate]:
        return await self.repo.get(candidate_id)

    async def get_candidates(self, skip: int = 0, limit: int = 100) -> List[Candidate]:
        return await self.repo.get_all(skip, limit)

    async def update_candidate(self, candidate_id: int, obj_in: dict) -> Candidate:
        db_obj = await self.repo.get(candidate_id)
        if not db_obj:
            raise ValueError(f"Candidate with ID {candidate_id} not found.")

        updated_obj = await self.repo.update(db_obj, obj_in)

        # If key search fields change, update FAISS embedding index
        trigger_reindex = any(
            k in obj_in for k in ["skills", "summary", "experience", "name"]
        )
        if trigger_reindex:
            await self.reindex_candidate(updated_obj)

        return updated_obj

    async def delete_candidate(self, candidate_id: int) -> bool:
        # Clear vector index
        vector_store.remove_vector(candidate_id)
        return await self.repo.delete(candidate_id)

    async def reindex_candidate(self, candidate: Candidate) -> None:
        """Regenerate candidate vector embeddings and insert/update in the FAISS index."""
        skills_str = ", ".join(candidate.skills or [])
        summary_str = candidate.summary or ""

        exp_list = []
        for exp in candidate.experience or []:
            if isinstance(exp, dict):
                exp_list.append(
                    f"{exp.get('role', '')} at {exp.get('company', '')}: {exp.get('description', '')}"
                )
            else:
                exp_list.append(str(exp))
        experience_str = " | ".join(exp_list)

        search_text = f"Candidate Profile. Summary: {summary_str}. Skills: {skills_str}. Experience: {experience_str}."

        try:
            embed_provider = AIProviderFactory.get_embedding_provider()
            embedding = await embed_provider.generate_embedding(search_text)
            if embedding:
                vector_store.add_vector(candidate.id, embedding)
                logger.info(f"Re-indexed candidate vector for ID {candidate.id}")
            else:
                logger.warning(
                    f"Re-index failed for candidate ID {candidate.id}: Empty embedding vector."
                )
        except Exception as e:
            logger.error(f"Re-indexing candidate ID {candidate.id} failed: {e}")

    async def verify_upload_quota(self) -> None:
        """Checks if current candidate count violates the Tenant's billing tier limitations."""
        result = await self.db.execute(
            select(Tenant).filter(Tenant.id == self.tenant_id)
        )
        tenant = result.scalars().first()
        if not tenant:
            raise ValueError("Access Denied: Tenant workspace does not exist.")

        tier = tenant.subscription_tier.lower()
        if tier == "free":
            max_limit = 5
        elif tier == "pro":
            max_limit = 100
        else:
            return  # Enterprise tier has unlimited usage quotas

        count_result = await self.db.execute(
            select(func.count(Candidate.id)).filter(
                Candidate.tenant_id == self.tenant_id
            )
        )
        count = count_result.scalar() or 0

        if count >= max_limit:
            raise PermissionError(
                f"SaaS Plan Limit: '{tier}' plan permits a maximum of {max_limit} candidate profiles. "
                "Please upgrade your workspace tier."
            )

    async def create_structured_candidate(
        self,
        name: str,
        email: str,
        phone: Optional[str] = None,
        location: Optional[str] = None,
        skills: Optional[List[str]] = None,
        education: Optional[List[dict]] = None,
        experience: Optional[List[dict]] = None,
        summary: Optional[str] = None,
    ) -> Candidate:
        """Creates a candidate record directly in PostgreSQL without raw file storage."""
        await self.verify_upload_quota()

        candidate = await self.repo.create({
            "name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "skills": skills or [],
            "education": education or [],
            "experience": experience or [],
            "summary": summary or "",
            "resume_path": None,  # No PDF/DOCX file saved!
            "ai_score": 8.5,
        })

        # Generate FAISS vector search embedding from SQL text
        await self.reindex_candidate(candidate)
        return candidate

    async def upload_and_parse_resume(
        self, filename: str, file_content: bytes, current_user_id: Optional[int] = None
    ) -> WorkflowContext:
        """Kicks off the transactional workflow resume upload parsing pipeline, verifying quotas first."""
        await self.verify_upload_quota()

        context = WorkflowContext(
            {
                "filename": filename,
                "file_size": len(file_content),
                "file_content": file_content,
                "db_session": self.db,
                "tenant_id": self.tenant_id,
                "current_user_id": current_user_id,
            }
        )

        pipeline = [
            ValidateFileStep(),
            SaveFileStep(),
            ParseResumeStep(),
            AIExtractCandidateStep(),
            CreateCandidateRepoStep(),
            GenerateCandidateEmbeddingStep(),
            IndexCandidateVectorStep(vector_store),
            AuditLogStep(),
        ]

        engine = WorkflowEngine(pipeline)
        success = await engine.execute(context)
        context.data["success"] = success
        return context
