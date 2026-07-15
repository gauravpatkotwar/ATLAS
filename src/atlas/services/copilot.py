import re
import logging
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.repositories.candidate import CandidateRepository
from atlas.repositories.job import JobRepository
from atlas.repositories.copilot import CopilotMessageRepository
from atlas.database.models import Candidate, Job, CopilotMessage
from atlas.vector.store import vector_store
from atlas.ai.factory import AIProviderFactory

logger = logging.getLogger(__name__)


class CopilotService:
    """Service handling stateful Recruiting Copilot chat transactions, scoped by tenant isolation."""

    def __init__(self, db: AsyncSession, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.candidate_repo = CandidateRepository(db, tenant_id)
        self.job_repo = JobRepository(db, tenant_id)
        self.msg_repo = CopilotMessageRepository(db, tenant_id)

    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """Loads chat history for a specific user within the tenant workspace."""
        messages = await self.msg_repo.get_by_user(user_id)
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    async def clear_history(self, user_id: int) -> None:
        """Wipes the conversation logs for the specified user within the tenant workspace."""
        await self.msg_repo.clear_by_user(user_id)

    async def answer_query(self, query: str, user_id: int) -> str:
        """Loads stateful user memory, builds context block from tenant records, and queries chat assistant."""
        # Detect job posting request
        is_job_post_query = any(
            kw in query.lower()
            for kw in ["create job", "post job", "publish job", "add job", "new job spec"]
        )
        if is_job_post_query:
            logger.info("Detecting job post query. Extracting job details...")
            try:
                ai_provider = AIProviderFactory.get_ai_provider()
                extractor_prompt = (
                    "You are a job specification extraction system.\n"
                    "Analyze the user request to create/post a job and extract the details in strict JSON format.\n"
                    "The JSON must have the following keys:\n"
                    "- title (string, required)\n"
                    "- description (string, required)\n"
                    "- required_skills (list of strings, required)\n"
                    "- salary (string, or null)\n"
                    "- location (string, or null)\n"
                    "- experience_years (integer, default 0)\n"
                    "- employment_type (string, default 'Full-time')\n"
                    "\n"
                    f"User Request: {query}\n"
                    "JSON Output:"
                )
                
                res_text = await ai_provider.chat_copilot(extractor_prompt, [])
                
                # Parse JSON
                import json
                clean_json = res_text.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                
                job_data = json.loads(clean_json)
                
                from atlas.services.job import JobService
                job_service = JobService(self.db, tenant_id=self.tenant_id)
                new_job = await job_service.create_job(job_data)
                
                skills_str = ", ".join(new_job.required_skills or [])
                response_msg = (
                    f"🎉 **Job Opening Successfully Published via Chat Prompt!**\n\n"
                    f"**Job Title:** {new_job.title}\n"
                    f"**Location:** {new_job.location or 'Remote'}\n"
                    f"**Salary:** {new_job.salary or 'N/A'}\n"
                    f"**Experience:** {new_job.experience_years} years\n"
                    f"**Required Skills:** {skills_str}\n\n"
                    f"**Description:** {new_job.description}\n\n"
                    f"The job listing is live and public to all candidates looking to get hired here:\n"
                    f"🔗 [Public Job Page](http://localhost/?publicJobId={new_job.id})"
                )
                
                user_msg = CopilotMessage(
                    tenant_id=self.tenant_id, user_id=user_id, role="user", content=query
                )
                assistant_msg = CopilotMessage(
                    tenant_id=self.tenant_id, user_id=user_id, role="assistant", content=response_msg
                )
                await self.msg_repo.create(user_msg)
                await self.msg_repo.create(assistant_msg)
                
                return response_msg
                
            except Exception as e:
                logger.error(f"Failed to extract and publish job via Copilot: {e}")

        # 1. Fetch chat log context from database
        history = await self.get_history(user_id)

        relevant_candidates: List[Candidate] = []
        relevant_jobs: List[Job] = []

        # 2. Parse query to detect explicit references to jobs, e.g., "Job #3"
        job_match = re.search(r"(?:job|Job)\s*#?\s*(\d+)", query)
        if job_match:
            job_id = int(job_match.group(1))
            # get() will automatically verify the job belongs to this tenant!
            job = await self.job_repo.get(job_id)
            if job:
                relevant_jobs.append(job)
                logger.info(f"Copilot detected reference to Job ID: {job_id}")

        # Fetch candidate profiles (automatically isolated by repo)
        candidates = await self.candidate_repo.get_all(limit=50)

        # 3. Parse query to detect candidate name matches
        for c in candidates:
            name_parts = c.name.lower().split()
            if c.name.lower() in query.lower() or any(
                part in query.lower() for part in name_parts if len(part) > 2
            ):
                relevant_candidates.append(c)

        # 4. Generate an Ideal Candidate Profile / Resume Summary first if this is a matching query
        generated_ideal_profile = None
        is_matching_query = any(
            kw in query.lower()
            for kw in [
                "find",
                "search",
                "match",
                "hire",
                "look for",
                "who has",
                "developer",
                "engineer",
                "candidate",
                "resume",
            ]
        )

        if is_matching_query and not relevant_candidates and not relevant_jobs:
            logger.info("Detecting search query. Generating ideal candidate profile first...")
            try:
                ai_provider = AIProviderFactory.get_ai_provider()
                generator_prompt = (
                    f"The recruiter is searching for a candidate. Based on their query below, write a professional, high-quality, 2-3 sentence Ideal Candidate Resume Summary that describes the perfect candidate profile they want. Do not mention names, keep it general but highly descriptive with target skills and experience.\n"
                    f"Recruiter Query: {query}\n"
                    f"Generated Ideal Resume Summary:"
                )
                generated_ideal_profile = await ai_provider.chat_copilot(
                    generator_prompt, []
                )
                logger.info(f"Generated Ideal Profile: {generated_ideal_profile}")
            except Exception as e:
                logger.error(f"Failed to generate ideal profile: {e}")

        # 5. Run semantic similarity query via FAISS using the ideal target summary
        if not relevant_candidates and not relevant_jobs:
            try:
                # Use the generated ideal profile if available, otherwise fallback to original query
                search_text = (
                    generated_ideal_profile
                    if generated_ideal_profile
                    else query
                )
                embed_provider = AIProviderFactory.get_embedding_provider()
                query_embedding = await embed_provider.generate_embedding(
                    search_text
                )
                if query_embedding:
                    match_results = vector_store.search(query_embedding, top_k=5)
                    for candidate_id, _ in match_results:
                        # get() ensures candidate matches self.tenant_id!
                        candidate = await self.candidate_repo.get(candidate_id)
                        if candidate and candidate not in relevant_candidates:
                            relevant_candidates.append(candidate)
            except Exception as e:
                logger.error(f"Semantic search in Copilot failed: {e}")

        # Fallback to display the top candidates if still empty
        if not relevant_candidates:
            relevant_candidates = candidates[:5]

        # 6. Construct context block
        context_str = "=== CONTEXT ===\n"
        if relevant_jobs:
            context_str += "Referenced Jobs:\n"
            for j in relevant_jobs:
                context_str += f"- Job #{j.id}: {j.title}. Location: {j.location}. Required Skills: {j.required_skills}. Description: {j.description}\n"

        context_str += "\nReferenced/Top Candidates:\n"
        for c in relevant_candidates:
            exp_text = []
            for exp in c.experience or []:
                if isinstance(exp, dict):
                    exp_text.append(
                        f"{exp.get('role', '')} at {exp.get('company', '')}"
                    )
                else:
                    exp_text.append(str(exp))
            context_str += (
                f"- Candidate ID: {c.id}, Name: {c.name}, Email: {c.email or 'N/A'}, Location: {c.location or 'N/A'}\n"
                f"  Skills: {c.skills}\n"
                f"  Summary: {c.summary or 'N/A'}\n"
                f"  Experience: {', '.join(exp_text)}\n"
            )
        context_str += "===============\n"

        # 7. Construct final prompt including the target profile description
        ideal_profile_section = ""
        if generated_ideal_profile:
            ideal_profile_section = (
                f"🎯 **Generated Ideal Candidate Profile:**\n"
                f"\"{generated_ideal_profile}\"\n\n"
            )

        prompt_payload = (
            f"You are the ATLAS AWi Recruiter Copilot assistant. Answer the User Question using the provided CONTEXT block.\n"
            f"If an 'Generated Ideal Candidate Profile' is provided below, make sure to display it at the very top of your response using markdown syntax (e.g., in a styled blockquote or card format), and then display the top matching candidate matches from the database with explanations of how they match.\n\n"
            f"{ideal_profile_section}"
            f"{context_str}\n"
            f"User Question: {query}"
        )

        try:
            ai_provider = AIProviderFactory.get_ai_provider()
            response = await ai_provider.chat_copilot(prompt_payload, history)
        except Exception as e:
            logger.error(f"Copilot LLM response failed: {e}")
            response = "Recruiter Copilot could not complete your request. Please ensure Ollama is running."

        # 8. Persist chat exchange in the database memory scoped to the tenant
        try:
            user_msg = CopilotMessage(
                tenant_id=self.tenant_id, user_id=user_id, role="user", content=query
            )
            assistant_msg = CopilotMessage(
                tenant_id=self.tenant_id,
                user_id=user_id,
                role="assistant",
                content=response,
            )
            await self.msg_repo.create(user_msg)
            await self.msg_repo.create(assistant_msg)
        except Exception as e:
            logger.error(f"Persisting chat message to database memory failed: {e}")

        return response
