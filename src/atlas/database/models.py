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
