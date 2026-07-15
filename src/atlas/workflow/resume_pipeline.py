import os
import uuid
import logging
from typing import Dict, Any

from atlas.workflow.engine import WorkflowStep
from atlas.parser.extractor import ResumeExtractor
from atlas.ai.factory import AIProviderFactory
from atlas.vector.store import FAISSVectorStore
from atlas.repositories.candidate import CandidateRepository
from atlas.repositories.audit import AuditLogRepository
from atlas.database.models import Candidate, AuditLog
from atlas.config.settings import settings

logger = logging.getLogger(__name__)


class ValidateFileStep(WorkflowStep):
    """Step 1: Validates file type and size limitations."""

    def __init__(self):
        super().__init__("ValidateFile")

    async def execute(self, context: Dict[str, Any]) -> None:
        filename: str = context.get("filename", "")
        file_size: int = context.get("file_size", 0)

        # Limit size to 10MB
        if file_size > 10 * 1024 * 1024:
            raise ValueError("File exceeds maximum allowed size of 10MB.")

        _, ext = os.path.splitext(filename.lower())
        if ext not in (".pdf", ".docx", ".txt", ".md"):
            raise ValueError(
                f"Unsupported file extension: {ext}. Only PDF, DOCX, TXT, MD are supported."
            )

    async def rollback(self, context: Dict[str, Any]) -> None:
        pass  # Validation step doesn't persist anything to rollback


class SaveFileStep(WorkflowStep):
    """Step 2: Saves the raw uploaded file content safely to the uploads folder."""

    def __init__(self):
        super().__init__("SaveFile")

    async def execute(self, context: Dict[str, Any]) -> None:
        filename: str = context.get("filename", "")
        file_content: bytes = context.get("file_content", b"")

        # Ensure uploads folder exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        # Create unique filename to prevent collissions
        unique_name = f"{uuid.uuid4().hex}_{os.path.basename(filename)}"
        saved_path = os.path.join(settings.UPLOAD_DIR, unique_name)

        # Write binary file to disk
        with open(saved_path, "wb") as f:
            f.write(file_content)

        context["saved_path"] = saved_path
        logger.info(f"Saved resume file to: {saved_path}")

    async def rollback(self, context: Dict[str, Any]) -> None:
        saved_path = context.get("saved_path")
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)
            logger.info(f"Rolled back file save: deleted {saved_path}")


class ParseResumeStep(WorkflowStep):
    """Step 3: Extracts plain text using specific parser plugins."""

    def __init__(self):
        super().__init__("ParseResume")

    async def execute(self, context: Dict[str, Any]) -> None:
        saved_path = context.get("saved_path")
        if not saved_path:
            raise ValueError("No saved resume path found in context.")

        raw_text = ResumeExtractor.extract_text(saved_path)
        if not raw_text.strip():
            raise ValueError("Resume parser extracted empty text from the file.")

        context["raw_text"] = raw_text

    async def rollback(self, context: Dict[str, Any]) -> None:
        pass  # In-memory parsing does not require rollback


class AIExtractCandidateStep(WorkflowStep):
    """Step 4: Uses LLMs to structure candidate fields and generate summaries."""

    def __init__(self):
        super().__init__("AIExtractCandidate")

    async def execute(self, context: Dict[str, Any]) -> None:
        raw_text = context.get("raw_text", "")

        ai_provider = AIProviderFactory.get_ai_provider()

        # Extract structured data
        candidate_data = await ai_provider.extract_candidate_data(raw_text)
        # Generate summary
        summary = await ai_provider.generate_summary(raw_text)

        candidate_data["summary"] = summary
        context["extracted_data"] = candidate_data
        logger.info(f"AI extracted details for candidate: {candidate_data.get('name')}")

    async def rollback(self, context: Dict[str, Any]) -> None:
        pass


class CreateCandidateRepoStep(WorkflowStep):
    """Step 5: Persists the structured Candidate to the database."""

    def __init__(self):
        super().__init__("CreateCandidateRepo")

    async def execute(self, context: Dict[str, Any]) -> None:
        db = context.get("db_session")
        extracted_data: Dict[str, Any] = context.get("extracted_data", {})
        saved_path: str = context.get("saved_path", "")

        if not db:
            raise ValueError("Database session missing from workflow context.")

        candidate = Candidate(
            name=extracted_data.get("name") or "Unknown",
            email=extracted_data.get("email"),
            phone=extracted_data.get("phone"),
            location=extracted_data.get("location"),
            skills=extracted_data.get("skills") or [],
            education=extracted_data.get("education") or [],
            experience=extracted_data.get("experience") or [],
            summary=extracted_data.get("summary"),
            linkedin=extracted_data.get("linkedin"),
            github=extracted_data.get("github"),
            portfolio=extracted_data.get("portfolio"),
            resume_path=saved_path,
            ai_score=0.0,
            recruiter_rating=0.0,
        )

        tenant_id = int(context.get("tenant_id", 0))
        repo = CandidateRepository(db, tenant_id=tenant_id)
        created_candidate = await repo.create(candidate)

        context["candidate_id"] = created_candidate.id
        context["candidate_obj"] = created_candidate
        logger.info(f"Created candidate DB record with ID: {created_candidate.id}")

    async def rollback(self, context: Dict[str, Any]) -> None:
        db = context.get("db_session")
        candidate_id = context.get("candidate_id")

        tenant_id = int(context.get("tenant_id", 0))
        if db and candidate_id:
            repo = CandidateRepository(db, tenant_id=tenant_id)
            await repo.delete(candidate_id)
            logger.info(
                f"Rolled back candidate creation: deleted candidate ID {candidate_id}"
            )


class GenerateCandidateEmbeddingStep(WorkflowStep):
    """Step 6: Computes semantic vector embeddings using nomic-embed-text."""

    def __init__(self):
        super().__init__("GenerateCandidateEmbedding")

    async def execute(self, context: Dict[str, Any]) -> None:
        extracted_data = context.get("extracted_data", {})

        # Build search text from summary, skills, and roles to capture overall profile semantics
        skills_str = ", ".join(extracted_data.get("skills", []))
        summary_str = extracted_data.get("summary", "")

        exp_list = []
        for exp in extracted_data.get("experience", []):
            if isinstance(exp, dict):
                exp_list.append(
                    f"{exp.get('role', '')} at {exp.get('company', '')}: {exp.get('description', '')}"
                )
            else:
                exp_list.append(str(exp))
        experience_str = " | ".join(exp_list)

        search_text = f"Candidate Profile. Summary: {summary_str}. Skills: {skills_str}. Experience: {experience_str}."

        embed_provider = AIProviderFactory.get_embedding_provider()
        embedding = await embed_provider.generate_embedding(search_text)

        if not embedding:
            # Fallback mock dimension if provider failure (avoids breaking pipeline in local dev environments)
            logger.warning(
                "Embedding provider returned empty vector. Generating zero vector fallback."
            )
            embedding = [0.0] * 768

        context["embedding"] = embedding

    async def rollback(self, context: Dict[str, Any]) -> None:
        pass


class IndexCandidateVectorStep(WorkflowStep):
    """Step 7: Inserts vector embeddings into the FAISS store index."""

    def __init__(self, vector_store: FAISSVectorStore):
        super().__init__("IndexCandidateVector")
        self.vector_store = vector_store

    async def execute(self, context: Dict[str, Any]) -> None:
        candidate_id = context.get("candidate_id")
        embedding = context.get("embedding")

        if not candidate_id or not embedding:
            raise ValueError("Missing candidate ID or embedding vector for indexing.")

        self.vector_store.add_vector(candidate_id, embedding)
        logger.info(f"Successfully indexed vector for candidate ID: {candidate_id}")

    async def rollback(self, context: Dict[str, Any]) -> None:
        candidate_id = context.get("candidate_id")
        if candidate_id:
            self.vector_store.remove_vector(candidate_id)
            logger.info(f"Rolled back vector index for candidate ID: {candidate_id}")


class AuditLogStep(WorkflowStep):
    """Step 8: Writes actions to audit logs."""

    def __init__(self):
        super().__init__("AuditLog")

    async def execute(self, context: Dict[str, Any]) -> None:
        db = context.get("db_session")
        candidate_id = context.get("candidate_id")
        user_id = context.get(
            "current_user_id"
        )  # nullable if uploaded before logging in/anon

        if not db:
            raise ValueError("Database session missing.")

        audit = AuditLog(
            user_id=user_id,
            action="UPLOAD_RESUME",
            target_type="candidate",
            target_id=str(candidate_id) if candidate_id else None,
            details={"filename": context.get("filename")},
        )

        tenant_id = int(context.get("tenant_id", 0))
        repo = AuditLogRepository(db, tenant_id=tenant_id)
        created_log = await repo.create(audit)
        context["audit_log_id"] = created_log.id
        logger.info(f"Recorded audit log for resume upload (ID: {created_log.id})")

    async def rollback(self, context: Dict[str, Any]) -> None:
        db = context.get("db_session")
        audit_log_id = context.get("audit_log_id")

        tenant_id = int(context.get("tenant_id", 0))
        if db and audit_log_id:
            repo = AuditLogRepository(db, tenant_id=tenant_id)
            await repo.delete(audit_log_id)
            logger.info(f"Rolled back audit log entry: ID {audit_log_id}")
