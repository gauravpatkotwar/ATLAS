from __future__ import annotations
from dataclasses import dataclass, field
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


class MemoryType(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    COMPANY = "company"
    DECISION = "decision"
    CONVERSATION = "conversation"
    INTERVIEW = "interview"
    KNOWLEDGE = "knowledge"
    SKILL = "skill"
    MARKET = "market"


class MemoryImportance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EntityType(str, Enum):
    CANDIDATE = "candidate"
    JOB = "job"
    COMPANY = "company"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    INTERVIEW = "interview"
    OFFER = "offer"
    SKILL = "skill"
    TECHNOLOGY = "technology"
    CERTIFICATION = "certification"
    PROJECT = "project"


class RelationType(str, Enum):
    WORKED_AT = "worked_at"
    APPLIED_TO = "applied_to"
    INTERVIEWED_FOR = "interviewed_for"
    RECOMMENDED_FOR = "recommended_for"
    REJECTED_FROM = "rejected_from"
    HIRED_FOR = "hired_for"
    MANAGES = "manages"
    REPORTS_TO = "reports_to"
    MENTORED = "mentored"
    COLLABORATED_WITH = "collaborated_with"
    KNOWS_SKILL = "knows_skill"
    REQUIRES_SKILL = "requires_skill"
    SIMILAR_TO = "similar_to"
    PREREQUISITE_FOR = "prerequisite_for"
    ALTERNATIVE_TO = "alternative_to"


class Memory(AggregateRoot):
    __tablename__ = "memories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    memory_type: Mapped[MemoryType] = mapped_column(String(30), nullable=False, index=True)
    entity_type: Mapped[EntityType] = mapped_column(String(30), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    importance: Mapped[MemoryImportance] = mapped_column(String(20), default=MemoryImportance.MEDIUM, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    outgoing_relations: Mapped[list["MemoryRelation"]] = relationship(
        "MemoryRelation",
        foreign_keys="MemoryRelation.source_memory_id",
        back_populates="source_memory",
        cascade="all, delete-orphan"
    )
    incoming_relations: Mapped[list["MemoryRelation"]] = relationship(
        "MemoryRelation",
        foreign_keys="MemoryRelation.target_memory_id",
        back_populates="target_memory",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_memory_tenant_type_entity", "tenant_id", "memory_type", "entity_type", "entity_id"),
        Index("ix_memory_tenant_importance", "tenant_id", "importance"),
        Index("ix_memory_tenant_created", "tenant_id", "created_at"),
        Index("ix_memory_embedding", "embedding", postgresql_using="ivfflat", postgresql_with={"lists": 100}),
    )


class MemoryRelation(AggregateRoot):
    __tablename__ = "memory_relations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    source_memory_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("memories.id"), nullable=False, index=True)
    target_memory_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("memories.id"), nullable=False, index=True)
    
    relation_type: Mapped[RelationType] = mapped_column(String(30), nullable=False, index=True)
    strength: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    properties: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    evidence: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    source_memory: Mapped[Memory] = relationship("Memory", foreign_keys=[source_memory_id], back_populates="outgoing_relations")
    target_memory: Mapped[Memory] = relationship("Memory", foreign_keys=[target_memory_id], back_populates="incoming_relations")
    tenant: Mapped["Tenant"] = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("source_memory_id", "target_memory_id", "relation_type", name="uq_memory_relation"),
        Index("ix_relation_tenant_type", "tenant_id", "relation_type"),
    )


class KnowledgeGraphEntity(AggregateRoot):
    __tablename__ = "knowledge_graph_entities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    entity_type: Mapped[EntityType] = mapped_column(String(30), nullable=False, index=True)
    external_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    properties: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    
    popularity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    authority_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    canonical_entity_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("knowledge_graph_entities.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    canonical_entity: Mapped["KnowledgeGraphEntity"] = relationship("KnowledgeGraphEntity", remote_side=[id])
    outgoing_relations: Mapped[list["KnowledgeGraphRelation"]] = relationship(
        "KnowledgeGraphRelation",
        foreign_keys="KnowledgeGraphRelation.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan"
    )
    incoming_relations: Mapped[list["KnowledgeGraphRelation"]] = relationship(
        "KnowledgeGraphRelation",
        foreign_keys="KnowledgeGraphRelation.target_entity_id",
        back_populates="target_entity",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "entity_type", "external_id", name="uq_kg_entity"),
        Index("ix_kg_entity_tenant_type_name", "tenant_id", "entity_type", "name"),
        Index("ix_kg_entity_embedding", "embedding", postgresql_using="ivfflat", postgresql_with={"lists": 100}),
    )


class KnowledgeGraphRelation(AggregateRoot):
    __tablename__ = "knowledge_graph_relations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    source_entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("knowledge_graph_entities.id"), nullable=False, index=True)
    target_entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("knowledge_graph_entities.id"), nullable=False, index=True)
    
    relation_type: Mapped[RelationType] = mapped_column(String(30), nullable=False, index=True)
    properties: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    source_entity: Mapped[KnowledgeGraphEntity] = relationship("KnowledgeGraphEntity", foreign_keys=[source_entity_id], back_populates="outgoing_relations")
    target_entity: Mapped[KnowledgeGraphEntity] = relationship("KnowledgeGraphEntity", foreign_keys=[target_entity_id], back_populates="incoming_relations")
    tenant: Mapped["Tenant"] = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("source_entity_id", "target_entity_id", "relation_type", name="uq_kg_relation"),
        Index("ix_kg_relation_tenant_type", "tenant_id", "relation_type"),
    )


class ConversationMemory(AggregateRoot):
    __tablename__ = "conversation_memories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    conversation_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("ix_conv_memory_tenant_session", "tenant_id", "session_id"),
        Index("ix_conv_memory_tenant_user_created", "tenant_id", "user_id", "created_at"),
    )


class RecruiterMemory(AggregateRoot):
    __tablename__ = "recruiter_memories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    recruiter_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    related_entities: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default_factory=list, nullable=False)
    
    importance: Mapped[MemoryImportance] = mapped_column(String(20), default=MemoryImportance.MEDIUM, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    
    is_preference: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preference_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    recruiter: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("ix_recruiter_memory_tenant_recruiter", "tenant_id", "recruiter_id"),
        Index("ix_recruiter_memory_tenant_type", "tenant_id", "memory_type"),
    )


class DecisionMemory(AggregateRoot):
    __tablename__ = "decision_memories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    decision_maker_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    alternatives_considered: Mapped[list[str]] = mapped_column(ARRAY(String), default_factory=list, nullable=False)
    criteria_used: Mapped[dict[str, Any]] = mapped_column(JSON, default_factory=dict, nullable=False)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    related_entities: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default_factory=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    decision_maker: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("ix_decision_memory_tenant_type", "tenant_id", "decision_type"),
        Index("ix_decision_memory_tenant_maker", "tenant_id", "decision_maker_id"),
    )