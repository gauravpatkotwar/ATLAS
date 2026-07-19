from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Float,
    Boolean,
    JSON,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.base import AggregateRoot
from app.modules.candidates.domain.entities import Candidate


class MatchAlgorithm(str, Enum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    AI_RERANK = "ai_rerank"


class MatchStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CandidateMatch(AggregateRoot):
    __tablename__ = "candidate_matches"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    algorithm: Mapped[MatchAlgorithm] = mapped_column(String(30), default=MatchAlgorithm.HYBRID, nullable=False)
    status: Mapped[MatchStatus] = mapped_column(String(30), default=MatchStatus.PENDING, nullable=False)
    
    overall_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    semantic_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    keyword_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    skill_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    education_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    matched_skills: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    missing_skills: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    matching_experience: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default_factory=list, nullable=False)
    matching_education: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default_factory=list, nullable=False)
    
    ai_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_strengths: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    ai_concerns: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    score_breakdown: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    computed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    job: Mapped["Job"] = relationship("Job", back_populates="matches")
    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="matches")
    tenant: Mapped["Tenant"] = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", "algorithm", name="uq_candidate_match"),
        Index("ix_match_job_score", "job_id", "overall_score"),
        Index("ix_match_tenant_status", "tenant_id", "status"),
    )


class JobSearchIndex(AggregateRoot):
    __tablename__ = "job_search_index"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, unique=True, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    title_embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    description_embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    requirements_embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    combined_embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    
    skills_text: Mapped[str] = mapped_column(Text, nullable=True)
    title_text: Mapped[str] = mapped_column(Text, nullable=True)
    description_text: Mapped[str] = mapped_column(Text, nullable=True)
    requirements_text: Mapped[str] = mapped_column(Text, nullable=True)
    location_text: Mapped[str] = mapped_column(Text, nullable=True)
    
    last_indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    indexing_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    indexing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    job: Mapped["Job"] = relationship("Job", back_populates="search_index")
    tenant: Mapped["Tenant"] = relationship("Tenant")


class CandidateSearchIndex(AggregateRoot):
    __tablename__ = "candidate_search_index"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    candidate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, unique=True, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    profile_embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    resume_embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    skills_embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    
    skills_text: Mapped[str] = mapped_column(Text, nullable=True)
    experience_text: Mapped[str] = mapped_column(Text, nullable=True)
    education_text: Mapped[str] = mapped_column(Text, nullable=True)
    projects_text: Mapped[str] = mapped_column(Text, nullable=True)
    full_text: Mapped[str] = mapped_column(Text, nullable=True)
    
    last_indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    indexing_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    indexing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="search_index")
    tenant: Mapped["Tenant"] = relationship("Tenant")


class SearchQuery(AggregateRoot):
    __tablename__ = "search_queries"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(30), nullable=False)
    filters: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    user: Mapped["User"] = relationship("User")


class SavedSearch(AggregateRoot):
    __tablename__ = "saved_searches"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=True)
    filters: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    sort_by: Mapped[str] = mapped_column(String(50), default="relevance", nullable=False)
    sort_order: Mapped[str] = mapped_column(String(10), default="desc", nullable=False)
    
    is_alert: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    alert_frequency: Mapped[str | None] = mapped_column(String(30), nullable=True)
    last_alert_sent: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    user: Mapped["User"] = relationship("User")