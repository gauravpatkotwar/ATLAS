import datetime
import uuid
from typing import Any, List, Dict, Optional
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative Base class for SQLAlchemy models with PEP-561 static typing support."""

    pass


def get_utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def generate_invite_code() -> str:
    """Generates an 8-character unique alphanumeric join code for inviting recruiters."""
    return uuid.uuid4().hex[:8].upper()


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    invite_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        default=generate_invite_code,
        nullable=False,
        index=True,
    )
    subscription_tier: Mapped[str] = mapped_column(
        default="free", nullable=False
    )  # free, pro, enterprise
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )
    billing_customer_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    billing_subscription_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    billing_provider: Mapped[Optional[str]] = mapped_column(nullable=True)

    users: Mapped[List["User"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    candidates: Mapped[List["Candidate"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    jobs: Mapped[List["Job"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    copilot_messages: Mapped[List["CopilotMessage"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(
        default="recruiter", nullable=False
    )  # admin, recruiter
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    video_path: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )

    tenant: Mapped[Tenant] = relationship(back_populates="users")
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    copilot_messages: Mapped[List["CopilotMessage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[Optional[str]] = mapped_column(index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(nullable=True)
    location: Mapped[Optional[str]] = mapped_column(nullable=True)

    skills: Mapped[List[str]] = mapped_column(
        JSON, default=list, nullable=False
    )  # list of strings
    education: Mapped[List[Any]] = mapped_column(
        JSON, default=list, nullable=False
    )  # list of dicts
    experience: Mapped[List[Any]] = mapped_column(
        JSON, default=list, nullable=False
    )  # list of dicts

    summary: Mapped[Optional[str]] = mapped_column(nullable=True)
    linkedin: Mapped[Optional[str]] = mapped_column(nullable=True)
    github: Mapped[Optional[str]] = mapped_column(nullable=True)
    portfolio: Mapped[Optional[str]] = mapped_column(nullable=True)
    resume_path: Mapped[Optional[str]] = mapped_column(nullable=True)
    video_path: Mapped[Optional[str]] = mapped_column(nullable=True)

    ai_score: Mapped[float] = mapped_column(default=0.0, nullable=False)
    recruiter_rating: Mapped[float] = mapped_column(default=0.0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )

    tenant: Mapped[Tenant] = relationship(back_populates="candidates")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    required_skills: Mapped[List[str]] = mapped_column(
        JSON, default=list, nullable=False
    )  # list of strings
    salary: Mapped[Optional[str]] = mapped_column(nullable=True)
    location: Mapped[Optional[str]] = mapped_column(nullable=True)
    experience_years: Mapped[int] = mapped_column(default=0, nullable=False)
    employment_type: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )  # e.g., Full-time
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )

    tenant: Mapped[Tenant] = relationship(back_populates="jobs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(nullable=False)  # e.g., "UPLOAD_RESUME"
    target_type: Mapped[str] = mapped_column(nullable=False)  # e.g., "candidate"
    target_id: Mapped[Optional[str]] = mapped_column(nullable=True)  # target record ID
    timestamp: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )
    details: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )  # additional metadata

    tenant: Mapped[Tenant] = relationship(back_populates="audit_logs")
    user: Mapped[Optional[User]] = relationship(back_populates="audit_logs")


class CopilotMessage(Base):
    __tablename__ = "copilot_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(nullable=False)  # "user" or "assistant"
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )

    tenant: Mapped[Tenant] = relationship(back_populates="copilot_messages")
    user: Mapped[User] = relationship(back_populates="copilot_messages")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    author_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_anonymous: Mapped[bool] = mapped_column(default=True, nullable=False)
    post_type: Mapped[str] = mapped_column(default="discussion", nullable=False)  # "discussion" or "whistleblower"
    votes: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    author_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_anonymous: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )


class MarketplaceProduct(Base):
    __tablename__ = "marketplace_products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)  # "software" or "service"
    download_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    author_email: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )


class MarketplacePurchase(Base):
    __tablename__ = "marketplace_purchases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("marketplace_products.id", ondelete="CASCADE"), nullable=False
    )
    purchased_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )


class SSOConfig(Base):
    __tablename__ = "sso_configurations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    idp_entity_id: Mapped[str] = mapped_column(nullable=False)
    idp_sso_url: Mapped[str] = mapped_column(nullable=False)
    x509_certificate: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    key_prefix: Mapped[str] = mapped_column(nullable=False)
    hashed_key: Mapped[str] = mapped_column(nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(nullable=False)
    secret_token: Mapped[str] = mapped_column(nullable=False)
    events: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )


class WorkflowRule(Base):
    __tablename__ = "workflow_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    trigger_event: Mapped[str] = mapped_column(nullable=False)
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    action_type: Mapped[str] = mapped_column(nullable=False)
    action_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )


class Integration(Base):
    __tablename__ = "integrations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    provider_name: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )


# ============================================================
#  ATLAS ACADEMY — Learning Management System Models
# ============================================================

class AcademyInstructor(Base):
    __tablename__ = "academy_instructors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(nullable=True)
    expertise: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    revenue_share: Mapped[float] = mapped_column(default=0.70, nullable=False)  # 70% to instructor
    total_students: Mapped[int] = mapped_column(default=0, nullable=False)
    total_revenue: Mapped[float] = mapped_column(default=0.0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)

    courses: Mapped[List["AcademyCourse"]] = relationship(back_populates="instructor", cascade="all, delete-orphan")


class AcademyCourse(Base):
    __tablename__ = "academy_courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    instructor_id: Mapped[int] = mapped_column(ForeignKey("academy_instructors.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    short_description: Mapped[Optional[str]] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=False)  # Programming, AI, Cloud, etc.
    level: Mapped[str] = mapped_column(default="beginner", nullable=False)  # beginner, intermediate, advanced
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    skills_taught: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(default=0.0, nullable=False)
    is_free: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(default=False, nullable=False)
    duration_hours: Mapped[float] = mapped_column(default=0.0, nullable=False)
    total_lessons: Mapped[int] = mapped_column(default=0, nullable=False)
    total_enrolled: Mapped[int] = mapped_column(default=0, nullable=False)
    avg_rating: Mapped[float] = mapped_column(default=0.0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)

    instructor: Mapped["AcademyInstructor"] = relationship(back_populates="courses")
    modules: Mapped[List["AcademyModule"]] = relationship(back_populates="course", cascade="all, delete-orphan", order_by="AcademyModule.order_index")
    enrollments: Mapped[List["AcademyEnrollment"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    certificates: Mapped[List["AcademyCertificate"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    reviews: Mapped[List["AcademyReview"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    projects: Mapped[List["AcademyProject"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class AcademyModule(Base):
    __tablename__ = "academy_modules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("academy_courses.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)

    course: Mapped["AcademyCourse"] = relationship(back_populates="modules")
    lessons: Mapped[List["AcademyLesson"]] = relationship(back_populates="module", cascade="all, delete-orphan", order_by="AcademyLesson.order_index")


class AcademyLesson(Base):
    __tablename__ = "academy_lessons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("academy_modules.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[Optional[str]] = mapped_column(nullable=True)  # markdown content
    video_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    duration_mins: Mapped[int] = mapped_column(default=10, nullable=False)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)
    is_preview: Mapped[bool] = mapped_column(default=False, nullable=False)  # free preview lesson
    quiz_data: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)  # inline quiz
    created_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)

    module: Mapped["AcademyModule"] = relationship(back_populates="lessons")


class AcademyEnrollment(Base):
    __tablename__ = "academy_enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("academy_courses.id", ondelete="CASCADE"), nullable=False)
    enrolled_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True)
    completed_lesson_ids: Mapped[List[int]] = mapped_column(JSON, default=list, nullable=False)
    progress_pct: Mapped[float] = mapped_column(default=0.0, nullable=False)
    last_lesson_id: Mapped[Optional[int]] = mapped_column(nullable=True)

    course: Mapped["AcademyCourse"] = relationship(back_populates="enrollments")


class AcademyCertificate(Base):
    __tablename__ = "academy_certificates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("academy_courses.id", ondelete="CASCADE"), nullable=False)
    credential_id: Mapped[str] = mapped_column(default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    issued_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)
    user_name: Mapped[str] = mapped_column(nullable=False)
    course_title: Mapped[str] = mapped_column(nullable=False)
    instructor_name: Mapped[str] = mapped_column(nullable=False)

    course: Mapped["AcademyCourse"] = relationship(back_populates="certificates")


class AcademyReview(Base):
    __tablename__ = "academy_reviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("academy_courses.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)  # 1-5
    body: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)

    course: Mapped["AcademyCourse"] = relationship(back_populates="reviews")


class AcademyProject(Base):
    __tablename__ = "academy_projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("academy_courses.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    submission_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    ai_feedback: Mapped[Optional[str]] = mapped_column(nullable=True)
    score: Mapped[Optional[float]] = mapped_column(nullable=True)
    submitted_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)

    course: Mapped["AcademyCourse"] = relationship(back_populates="projects")


class AcademySkillGap(Base):
    __tablename__ = "academy_skill_gaps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_title: Mapped[str] = mapped_column(nullable=False)
    job_required_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    candidate_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    matching_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    recommended_course_ids: Mapped[List[int]] = mapped_column(JSON, default=list, nullable=False)
    ai_roadmap: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)


class AcademyLearningPath(Base):
    __tablename__ = "academy_learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal: Mapped[str] = mapped_column(nullable=False)
    ai_roadmap: Mapped[Optional[str]] = mapped_column(nullable=True)
    course_ids: Mapped[List[int]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=get_utc_now, nullable=False)
