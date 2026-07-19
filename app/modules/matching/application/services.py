from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.core.ai.service import AIService
from app.core.config import settings
from app.modules.matching.domain.entities import Candidate, Job, MatchResult, MatchType
from app.modules.matching.domain.repositories import CandidateRepository, JobRepository, MatchRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class MatchingConfig:
    semantic_weight: float = 0.4
    skill_weight: float = 0.3
    experience_weight: float = 0.15
    education_weight: float = 0.1
    location_weight: float = 0.05
    
    min_semantic_score: float = 0.3
    min_skill_overlap: float = 0.1
    
    max_candidates: int = 100
    max_results: int = 50


class SemanticMatcher:
    def __init__(self, ai_service: AIService, config: MatchingConfig):
        self.ai_service = ai_service
        self.config = config

    async def match(
        self,
        job: Job,
        candidates: list[Candidate],
    ) -> dict[UUID, float]:
        if not job.description_embedding or not candidates:
            return {}

        candidate_embeddings = [
            c.resume_embedding or c.description_embedding
            for c in candidates
        ]
        valid_indices = [i for i, e in enumerate(candidate_embeddings) if e]
        
        if not valid_indices:
            return {}

        valid_candidates = [candidates[i] for i in valid_indices]
        valid_embeddings = [candidate_embeddings[i] for i in valid_indices]

        scores = await self.ai_service.compute_similarity_scores(
            job.description_embedding,
            valid_embeddings,
        )

        results = {}
        for idx, candidate in enumerate(valid_candidates):
            score = scores[idx] if idx < len(scores) else 0.0
            if score >= self.config.min_semantic_score:
                results[candidate.id] = score

        return results


class SkillMatcher:
    def __init__(self, config: MatchingConfig):
        self.config = config

    def match(
        self,
        job: Job,
        candidates: list[Candidate],
    ) -> dict[UUID, float]:
        job_skills = set(s.lower() for s in job.required_skills + job.preferred_skills)
        if not job_skills:
            return {c.id: 0.0 for c in candidates}

        results = {}
        for candidate in candidates:
            candidate_skills = set(s.lower() for s in candidate.skills)
            if not candidate_skills:
                results[candidate.id] = 0.0
                continue

            overlap = len(job_skills & candidate_skills)
            score = overlap / len(job_skills)
            
            if score >= self.config.min_skill_overlap:
                results[candidate.id] = score

        return results


class ExperienceMatcher:
    def __init__(self, config: MatchingConfig):
        self.config = config

    def match(
        self,
        job: Job,
        candidates: list[Candidate],
    ) -> dict[UUID, float]:
        results = {}
        
        for candidate in candidates:
            if candidate.years_experience is None:
                results[candidate.id] = 0.5
                continue

            required_years = job.min_years_experience or 0
            if candidate.years_experience >= required_years:
                if candidate.years_experience <= required_years + 5:
                    score = 1.0
                else:
                    score = max(0.7, 1.0 - (candidate.years_experience - required_years - 5) * 0.05)
            else:
                score = candidate.years_experience / max(required_years, 1) * 0.8
            
            results[candidate.id] = max(0.0, min(1.0, score))

        return results


class EducationMatcher:
    def __init__(self, config: MatchingConfig):
        self.config = config

    def match(
        self,
        job: Job,
        candidates: list[Candidate],
    ) -> dict[UUID, float]:
        results = {}
        job_education = [e.lower() for e in job.required_education] if job.required_education else []
        
        for candidate in candidates:
            if not job_education:
                results[candidate.id] = 0.5
                continue

            candidate_education = [e.degree.lower() for e in candidate.educations] if candidate.educations else []
            if not candidate_education:
                results[candidate.id] = 0.0
                continue

            matches = sum(1 for req in job_education if any(req in cand for cand in candidate_education))
            score = matches / len(job_education) if job_education else 0.5
            results[candidate.id] = score

        return results


class LocationMatcher:
    def __init__(self, config: MatchingConfig):
        self.config = config

    def match(
        self,
        job: Job,
        candidates: list[Candidate],
    ) -> dict[UUID, float]:
        results = {}
        
        job_location = job.location.lower() if job.location else ""
        job_remote = job.remote_type or "onsite"
        
        for candidate in candidates:
            if job_remote == "remote":
                results[candidate.id] = 1.0
                continue
            
            if not candidate.location:
                results[candidate.id] = 0.3
                continue

            candidate_location = candidate.location.lower()
            
            if candidate.willing_to_relocate:
                score = 0.8
            elif job_remote == "hybrid":
                score = 0.7 if candidate.remote_preference in ["hybrid", "remote"] else 0.5
            else:
                if job_location and candidate_location:
                    if job_location in candidate_location or candidate_location in job_location:
                        score = 1.0
                    elif any(city in candidate_location for city in job_location.split()):
                        score = 0.7
                    else:
                        score = 0.3
                else:
                    score = 0.5
            
            results[candidate.id] = score

        return results


class CandidateRanker:
    def __init__(
        self,
        ai_service: AIService,
        config: MatchingConfig,
    ):
        self.ai_service = ai_service
        self.config = config
        
        self.semantic_matcher = SemanticMatcher(ai_service, config)
        self.skill_matcher = SkillMatcher(config)
        self.experience_matcher = ExperienceMatcher(config)
        self.education_matcher = EducationMatcher(config)
        self.location_matcher = LocationMatcher(config)

    async def rank(
        self,
        job: Job,
        candidates: list[Candidate],
    ) -> list[MatchResult]:
        if not candidates:
            return []

        semantic_scores = await self.semantic_matcher.match(job, candidates)
        skill_scores = self.skill_matcher.match(job, candidates)
        experience_scores = self.experience_matcher.match(job, candidates)
        education_scores = self.education_matcher.match(job, candidates)
        location_scores = self.location_matcher.match(job, candidates)

        results = []
        for candidate in candidates:
            cid = candidate.id
            
            semantic = semantic_scores.get(cid, 0.0)
            skills = skill_scores.get(cid, 0.0)
            experience = experience_scores.get(cid, 0.0)
            education = education_scores.get(cid, 0.0)
            location = location_scores.get(cid, 0.0)

            total_score = (
                semantic * self.config.semantic_weight +
                skills * self.config.skill_weight +
                experience * self.config.experience_weight +
                education * self.config.education_weight +
                location * self.config.location_weight
            )

            if total_score < 0.1:
                continue

            reasoning = self._generate_reasoning(
                candidate, job, semantic, skills, experience, education, location
            )

            results.append(MatchResult(
                candidate_id=cid,
                job_id=job.id,
                score=total_score,
                match_type=MatchType.AI_RANKED,
                semantic_score=semantic,
                skill_score=skills,
                experience_score=experience,
                education_score=education,
                location_score=location,
                reasoning=reasoning,
                matched_skills=list(set(job.required_skills + job.preferred_skills) & set(candidate.skills)),
                missing_skills=list(set(job.required_skills) - set(candidate.skills)),
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:self.config.max_results]

    def _generate_reasoning(
        self,
        candidate: Candidate,
        job: Job,
        semantic: float,
        skills: float,
        experience: float,
        education: float,
        location: float,
    ) -> str:
        reasons = []
        
        if semantic > 0.7:
            reasons.append("Strong semantic match with job requirements")
        elif semantic > 0.4:
            reasons.append("Good semantic alignment with job description")
        
        if skills > 0.7:
            reasons.append(f"Excellent skill match ({int(skills*100)}% of required skills)")
        elif skills > 0.4:
            reasons.append(f"Good skill match ({int(skills*100)}% of required skills)")
        
        if experience > 0.8:
            reasons.append("Ideal experience level")
        elif experience > 0.5:
            reasons.append("Relevant experience level")
        
        if education > 0.7:
            reasons.append("Education requirements well met")
        
        if location > 0.8:
            reasons.append("Location preference aligned")
        
        return "; ".join(reasons) if reasons else "Basic profile match"


class MatchingService:
    def __init__(
        self,
        candidate_repo: CandidateRepository,
        job_repo: JobRepository,
        match_repo: MatchRepository,
        ai_service: AIService,
        config: MatchingConfig | None = None,
    ):
        self.candidate_repo = candidate_repo
        self.job_repo = job_repo
        self.match_repo = match_repo
        self.ai_service = ai_service
        self.config = config or MatchingConfig()
        self.ranker = CandidateRanker(ai_service, self.config)

    async def find_matches_for_job(
        self,
        job_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MatchResult]:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        candidates = await self.candidate_repo.search(
            tenant_id=job.tenant_id,
            limit=self.config.max_candidates,
        )

        results = await self.ranker.rank(job, candidates)
        
        for result in results:
            result.tenant_id = job.tenant_id
            await self.match_repo.upsert(result)

        return results[offset:offset + limit]

    async def find_matches_for_candidate(
        self,
        candidate_id: UUID,
        limit: int = 20,
    ) -> list[MatchResult]:
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        jobs = await self.job_repo.search(
            tenant_id=candidate.tenant_id,
            status="published",
            limit=self.config.max_candidates,
        )

        results = []
        for job in jobs:
            ranked = await self.ranker.rank(job, [candidate])
            if ranked:
                result = ranked[0]
                result.tenant_id = candidate.tenant_id
                results.append(result)

        results.sort(key=lambda x: x.score, reverse=True)
        
        for result in results[:limit]:
            await self.match_repo.upsert(result)

        return results[:limit]

    async def get_match(self, match_id: UUID) -> MatchResult | None:
        return await self.match_repo.get_by_id(match_id)

    async def get_job_matches(
        self,
        job_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MatchResult]:
        return await self.match_repo.get_by_job(job_id, limit, offset)

    async def get_candidate_matches(
        self,
        candidate_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MatchResult]:
        return await self.match_repo.get_by_candidate(candidate_id, limit, offset)

    async def refresh_matches(self, job_id: UUID) -> list[MatchResult]:
        return await self.find_matches_for_job(job_id)