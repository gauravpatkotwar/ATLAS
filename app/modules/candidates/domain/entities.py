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
    UniqueConstraint,
    Integer,
    Boolean,
    JSON,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.base import AggregateRoot, DomainEvent
from app.core.config import settings


class CandidateSource(str, Enum):
    MANUAL = "manual"
    UPLOAD = "upload"
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    REFERRAL = "referral"
    CAREER_SITE = "career_site"
    AGENCY = "agency"
    INTERNAL = "internal"
    IMPORT = "import"


class CandidateStatus(str, Enum):
    NEW = "new"
    SCREENING = "screening"
    PHONE_SCREEN = "phone_screen"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ARCHIVED = "archived"


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    EXECUTIVE = "executive"


class Candidate(AggregateRoot):
    __tablename__ = "candidates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    source: Mapped[CandidateSource] = mapped_column(String(30), default=CandidateSource.MANUAL, nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    headline: Mapped[str | None] = mapped_column(String(300), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    willing_to_relocate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    remote_preference: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    status: Mapped[CandidateStatus] = mapped_column(String(30), default=CandidateStatus.NEW, nullable=False, index=True)
    experience_level: Mapped[ExperienceLevel | None] = mapped_column(String(30), nullable=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    current_company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    current_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    current_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    availability: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notice_period: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    skill_embeddings: Mapped[dict[str, list[float]]] = mapped_column(JSON, default_factory=dict, nullable=False)
    languages: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    resume_file_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    parsed_data: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_strengths: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    ai_weaknesses: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    ai_fit_score: Mapped[float | None] = mapped_column(nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    profile_completeness: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_enriched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    enrichment_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="candidates")
    experiences: Mapped[list["Experience"]] = relationship("Experience", back_populates="candidate", cascade="all, delete-orphan")
    educations: Mapped[list["Education"]] = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="candidate", cascade="all, delete-orphan")
    documents: Mapped[list["CandidateDocument"]] = relationship("CandidateDocument", back_populates="candidate", cascade="all, delete-orphan")
    job_applications: Mapped[list["JobApplication"]] = relationship("JobApplication", back_populates="candidate")
    timeline_events: Mapped[list["CandidateTimelineEvent"]] = relationship("CandidateTimelineEvent", back_populates="candidate", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_candidate_tenant_email"),
        Index("ix_candidate_tenant_status", "tenant_id", "status"),
        Index("ix_candidate_tenant_skills", "tenant_id", "skills"),
    )


class Experience(AggregateRoot):
    __tablename__ = "candidate_experiences"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    candidate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    technologies: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    achievements: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    employment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="experiences")
    tenant: Mapped["Tenant"] = relationship("Tenant")


class Education(AggregateRoot):
    __tablename__ = "candidate_educations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    candidate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    institution: Mapped[str] = mapped_column(String(300), nullable=False)
    degree: Mapped[str] = mapped_column(String(200), nullable=False)
    field_of_study: Mapped[str | None] = mapped_column(String(200), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    activities: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    honors: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="educations")
    tenant: Mapped["Tenant"] = relationship("Tenant")


class Project(AggregateRoot):
    __tablename__ = "candidate_projects"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    candidate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_ongoing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    technologies: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    team_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    highlights: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="projects")
    tenant: Mapped["Tenant"] = relationship("Tenant")


class CandidateDocument(AggregateRoot):
    __tablename__ = "candidate_documents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    candidate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    file_name: Mapped[str] = mapped_column(String(300), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    document_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    
    parsed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsing_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    parsing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="documents")
    tenant: Mapped["Tenant"] = relationship("Tenant")


class CandidateTimelineEvent(AggregateRoot):
    __tablename__ = "candidate_timeline_events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    candidate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="timeline_events")
    tenant: Mapped["Tenant"] = relationship("Tenant")
    user: Mapped["User"] = relationship("User")


class JobApplication(AggregateRoot):
    __tablename__ = "job_applications"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(30), default="applied", nullable=False, index=True)
    source: Mapped[CandidateSource] = mapped_column(String(30), default=CandidateSource.MANUAL, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_file_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    additional_data: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    stage_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("pipeline_stages.id"), nullable=True)
    stage_entered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    score: Mapped[float | None] = mapped_column(nullable=True)
    match_details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    job: Mapped["Job"] = relationship("Job", back_populates="applications")
    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="job_applications")
    tenant: Mapped["Tenant"] = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", name="uq_job_application"),
        Index("ix_application_tenant_status", "tenant_id", "status"),
    )