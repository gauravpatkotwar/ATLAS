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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.base import AggregateRoot


class JobStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PUBLISHED = "published"
    PAUSED = "paused"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    CONTRACT_TO_HIRE = "contract_to_hire"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"
    FREELANCE = "freelance"
    VOLUNTEER = "volunteer"


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    EXECUTIVE = "executive"


class RemoteType(str, Enum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"
    REMOTE_FIRST = "remote_first"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    INR = "INR"
    SGD = "SGD"
    JPY = "JPY"


class PipelineStageType(str, Enum):
    SOURCING = "sourcing"
    SCREENING = "screening"
    PHONE_SCREEN = "phone_screen"
    TECHNICAL_INTERVIEW = "technical_interview"
    ON_SITE_INTERVIEW = "on_site_interview"
    FINAL_INTERVIEW = "final_interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Job(AggregateRoot):
    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    department_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("departments.id"), nullable=True, index=True)
    hiring_manager_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    recruiter_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    benefits: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    job_type: Mapped[JobType] = mapped_column(String(30), default=JobType.FULL_TIME, nullable=False)
    experience_level: Mapped[ExperienceLevel] = mapped_column(String(30), default=ExperienceLevel.MID, nullable=False)
    remote_type: Mapped[RemoteType] = mapped_column(String(30), default=RemoteType.ONSITE, nullable=False)
    
    location: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    location_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    min_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[Currency] = mapped_column(String(3), default=Currency.USD, nullable=False)
    salary_period: Mapped[str] = mapped_column(String(20), default="yearly", nullable=False)
    equity_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    equity_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    bonus_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    visa_sponsorship: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    relocation_assistance: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    required_skills: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    preferred_skills: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    required_education: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    required_experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    required_certifications: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    languages: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    status: Mapped[JobStatus] = mapped_column(String(30), default=JobStatus.DRAFT, nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    openings: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    filled_openings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    pipeline_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("pipelines.id"), nullable=True)
    current_stage_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("pipeline_stages.id"), nullable=True)
    
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    apply_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    search_index_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    created_by_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="jobs")
    department: Mapped["Department | None"] = relationship("Department", back_populates="jobs")
    hiring_manager: Mapped["User | None"] = relationship("User", foreign_keys=[hiring_manager_id])
    recruiter: Mapped["User | None"] = relationship("User", foreign_keys=[recruiter_id])
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    pipeline: Mapped["Pipeline | None"] = relationship("Pipeline", back_populates="jobs")
    current_stage: Mapped["PipelineStage | None"] = relationship("PipelineStage", foreign_keys=[current_stage_id])
    applications: Mapped[list["JobApplication"]] = relationship("JobApplication", back_populates="job")
    team_members: Mapped[list["JobTeamMember"]] = relationship("JobTeamMember", back_populates="job", cascade="all, delete-orphan")
    interview_templates: Mapped[list["InterviewTemplate"]] = relationship("InterviewTemplate", back_populates="job", cascade="all, delete-orphan")
    search_index: Mapped["JobSearchIndex | None"] = relationship("JobSearchIndex", back_populates="job", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "slug", name="uq_job_tenant_slug"),
        Index("ix_job_tenant_status", "tenant_id", "status"),
        Index("ix_job_tenant_dept_status", "tenant_id", "department_id", "status"),
        Index("ix_job_tenant_recruiter", "tenant_id", "recruiter_id"),
    )


class Pipeline(AggregateRoot):
    __tablename__ = "pipelines"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="pipelines")
    stages: Mapped[list["PipelineStage"]] = relationship("PipelineStage", back_populates="pipeline", order_by="PipelineStage.order", cascade="all, delete-orphan")
    jobs: Mapped[list[Job]] = relationship("Job", back_populates="pipeline")

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_pipeline_tenant_name"),
        Index("ix_pipeline_tenant_default", "tenant_id", "is_default"),
    )


class PipelineStage(AggregateRoot):
    __tablename__ = "pipeline_stages"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    pipeline_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("pipelines.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[PipelineStageType] = mapped_column(String(30), default=PipelineStageType.SCREENING, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    color: Mapped[str] = mapped_column(String(7), default="#6366F1", nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_terminal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    sla_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    auto_advance: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_advance_condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    entry_criteria: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    exit_criteria: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    interview_template_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("interview_templates.id"), nullable=True)
    scorecard_template_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("scorecard_templates.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    pipeline: Mapped[Pipeline] = relationship("Pipeline", back_populates="stages")
    jobs: Mapped[list[Job]] = relationship("Job", back_populates="current_stage", foreign_keys=[Job.current_stage_id])
    interview_template: Mapped["InterviewTemplate | None"] = relationship("InterviewTemplate", foreign_keys=[interview_template_id])
    scorecard_template: Mapped["ScorecardTemplate | None"] = relationship("ScorecardTemplate", foreign_keys=[scorecard_template_id])

    __table_args__ = (
        UniqueConstraint("pipeline_id", "order", name="uq_pipeline_stage_order"),
        Index("ix_stage_pipeline_order", "pipeline_id", "order"),
    )


class JobTeamMember(AggregateRoot):
    __tablename__ = "job_team_members"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    role: Mapped[str] = mapped_column(String(50), default="interviewer", nullable=False)
    permissions: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    is_lead: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_interview: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_view_feedback: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_make_decisions: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    job: Mapped[Job] = relationship("Job", back_populates="team_members")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint("job_id", "user_id", name="uq_job_team_member"),
    )


class JobApplication(AggregateRoot):
    __tablename__ = "job_applications"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(30), default="applied", nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(30), default="manual", nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    referred_by_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_file_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    additional_data: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    stage_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("pipeline_stages.id"), nullable=True)
    stage_entered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    previous_stage_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    match_details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    job: Mapped[Job] = relationship("Job", back_populates="applications")
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="job_applications")
    tenant: Mapped["Tenant"] = relationship("Tenant")
    referred_by: Mapped["User | None"] = relationship("User", foreign_keys=[referred_by_id])
    stage: Mapped["PipelineStage | None"] = relationship("PipelineStage", foreign_keys=[stage_id])
    interviews: Mapped[list["Interview"]] = relationship("Interview", back_populates="application")
    feedback: Mapped[list["InterviewFeedback"]] = relationship("InterviewFeedback", back_populates="application")
    offers: Mapped[list["Offer"]] = relationship("Offer", back_populates="application")

    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", name="uq_job_application"),
        Index("ix_application_tenant_status", "tenant_id", "status"),
        Index("ix_application_job_stage", "job_id", "stage_id"),
    )


class InterviewTemplate(AggregateRoot):
    __tablename__ = "interview_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    job_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True, index=True)
    created_by_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), default="technical", nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    
    sections: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default_factory=list, nullable=False)
    questions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default_factory=list, nullable=False)
    scorecard_template_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("scorecard_templates.id"), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    job: Mapped["Job | None"] = relationship("Job", back_populates="interview_templates")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])

    __table_args__ = (
        Index("ix_interview_template_tenant_active", "tenant_id", "is_active"),
    )


class ScorecardTemplate(AggregateRoot):
    __tablename__ = "scorecard_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    criteria: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default_factory=list, nullable=False)
    rating_scale: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    overall_recommendation_options: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])

    __table_args__ = (
        Index("ix_scorecard_template_tenant_active", "tenant_id", "is_active"),
    )