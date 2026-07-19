from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.core.ai.service import AIService
from app.core.config import settings
from app.modules.atlas_brain.domain.entities import (
    Memory,
    MemoryRelation,
    MemoryType,
    EntityType,
    RelationType,
    KnowledgeGraphEntity,
    KnowledgeGraphRelation,
    ConversationMemory,
)
from app.modules.atlas_brain.domain.repositories import (
    MemoryRepository,
    KnowledgeGraphRepository,
    ConversationMemoryRepository,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievalConfig:
    max_memories: int = 10
    max_relations: int = 5
    max_kg_entities: int = 10
    min_similarity: float = 0.7
    min_relation_strength: float = 0.5
    include_conversation_history: bool = True
    conversation_limit: int = 20


@dataclass
class RetrievedContext:
    memories: list[Memory]
    relations: list[MemoryRelation]
    kg_entities: list[KnowledgeGraphEntity]
    kg_relations: list[KnowledgeGraphRelation]
    conversation_history: list[ConversationMemory]
    total_tokens: int


class MemoryRetriever:
    def __init__(
        self,
        memory_repo: MemoryRepository,
        kg_repo: KnowledgeGraphRepository,
        conversation_repo: ConversationMemoryRepository,
        ai_service: AIService,
        config: RetrievalConfig | None = None,
    ):
        self.memory_repo = memory_repo
        self.kg_repo = kg_repo
        self.conversation_repo = conversation_repo
        self.ai_service = ai_service
        self.config = config or RetrievalConfig()

    async def retrieve(
        self,
        tenant_id: UUID,
        query: str,
        entity_type: EntityType | None = None,
        entity_id: UUID | None = None,
        memory_types: list[MemoryType] | None = None,
        user_id: UUID | None = None,
        session_id: str | None = None,
    ) -> RetrievedContext:
        query_embedding = await self.ai_service.create_embedding(query)

        memories = await self.memory_repo.search_by_embedding(
            tenant_id=tenant_id,
            query_embedding=query_embedding,
            entity_type=entity_type,
            entity_id=entity_id,
            memory_types=memory_types,
            limit=self.config.max_memories,
            min_similarity=self.config.min_similarity,
        )

        relations = []
        if memories:
            memory_ids = [m.id for m in memories]
            relations = await self.memory_repo.get_relations(
                tenant_id=tenant_id,
                memory_ids=memory_ids,
                min_strength=self.config.min_relation_strength,
                limit=self.config.max_relations,
            )

        kg_entities = await self.kg_repo.search_entities(
            tenant_id=tenant_id,
            query=query,
            limit=self.config.max_kg_entities,
        )

        kg_relations = []
        if kg_entities:
            entity_ids = [e.id for e in kg_entities]
            kg_relations = await self.kg_repo.get_relations(
                tenant_id=tenant_id,
                entity_ids=entity_ids,
                limit=self.config.max_relations,
            )

        conversation_history = []
        if self.config.include_conversation_history and user_id:
            conversation_history = await self.conversation_repo.get_recent(
                tenant_id=tenant_id,
                user_id=user_id,
                session_id=session_id,
                limit=self.config.conversation_limit,
            )

        total_tokens = sum(m.tokens for m in memories if hasattr(m, 'tokens'))
        total_tokens += sum(c.tokens for c in conversation_history if hasattr(c, 'tokens'))

        return RetrievedContext(
            memories=memories,
            relations=relations,
            kg_entities=kg_entities,
            kg_relations=kg_relations,
            conversation_history=conversation_history,
            total_tokens=total_tokens,
        )

    async def retrieve_for_candidate(
        self,
        tenant_id: UUID,
        candidate_id: UUID,
        query: str,
        user_id: UUID | None = None,
    ) -> RetrievedContext:
        return await self.retrieve(
            tenant_id=tenant_id,
            query=query,
            entity_type=EntityType.CANDIDATE,
            entity_id=candidate_id,
            memory_types=[MemoryType.CANDIDATE, MemoryType.CONVERSATION, MemoryType.DECISION],
            user_id=user_id,
        )

    async def retrieve_for_job(
        self,
        tenant_id: UUID,
        job_id: UUID,
        query: str,
        user_id: UUID | None = None,
    ) -> RetrievedContext:
        return await self.retrieve(
            tenant_id=tenant_id,
            query=query,
            entity_type=EntityType.JOB,
            entity_id=job_id,
            memory_types=[MemoryType.CANDIDATE, MemoryType.DECISION, MemoryType.CONVERSATION, MemoryType.KNOWLEDGE],
            user_id=user_id,
        )

    async def retrieve_for_recruiter(
        self,
        tenant_id: UUID,
        recruiter_id: UUID,
        query: str,
    ) -> RetrievedContext:
        return await self.retrieve(
            tenant_id=tenant_id,
            query=query,
            entity_type=EntityType.RECRUITER,
            entity_id=recruiter_id,
            memory_types=[MemoryType.RECRUITER, MemoryType.CONVERSATION, MemoryType.KNOWLEDGE],
            user_id=recruiter_id,
        )


class RAGService:
    def __init__(
        self,
        retriever: MemoryRetriever,
        ai_service: AIService,
    ):
        self.retriever = retriever
        self.ai_service = ai_service

    async def generate_response(
        self,
        tenant_id: UUID,
        query: str,
        entity_type: EntityType | None = None,
        entity_id: UUID | None = None,
        user_id: UUID | None = None,
        session_id: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.1,
    ) -> str:
        context = await self.retriever.retrieve(
            tenant_id=tenant_id,
            query=query,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            session_id=session_id,
        )

        augmented_prompt = self._build_augmented_prompt(
            query=query,
            context=context,
            system_prompt=system_prompt,
        )

        response = await self.ai_service.chat_completion(
            messages=[{"role": "user", "content": augmented_prompt}],
            temperature=temperature,
            max_tokens=2000,
        )

        return response

    async def generate_structured_response(
        self,
        tenant_id: UUID,
        query: str,
        response_model: type,
        entity_type: EntityType | None = None,
        entity_id: UUID | None = None,
        user_id: UUID | None = None,
        system_prompt: str | None = None,
    ) -> Any:
        context = await self.retriever.retrieve(
            tenant_id=tenant_id,
            query=query,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
        )

        augmented_prompt = self._build_augmented_prompt(
            query=query,
            context=context,
            system_prompt=system_prompt,
        )

        response = await self.ai_service.structured_completion(
            messages=[{"role": "user", "content": augmented_prompt}],
            response_model=response_model,
        )

        return response

    def _build_augmented_prompt(
        self,
        query: str,
        context: RetrievedContext,
        system_prompt: str | None = None,
    ) -> str:
        parts = []
        
        if system_prompt:
            parts.append(f"System: {system_prompt}")
        
        parts.append("=== Relevant Memories ===")
        for memory in context.memories:
            parts.append(f"[{memory.memory_type.value}] {memory.title}: {memory.content[:500]}")
        
        if context.relations:
            parts.append("\n=== Memory Relations ===")
            for rel in context.relations:
                parts.append(f"{rel.relation_type.value} (strength: {rel.strength:.2f})")
        
        if context.kg_entities:
            parts.append("\n=== Knowledge Graph Entities ===")
            for entity in context.kg_entities:
                parts.append(f"[{entity.entity_type.value}] {entity.name}: {entity.description or ''}")
        
        if context.kg_relations:
            parts.append("\n=== Knowledge Graph Relations ===")
            for rel in context.kg_relations:
                parts.append(f"{rel.relation_type.value} (weight: {rel.weight:.2f})")
        
        if context.conversation_history:
            parts.append("\n=== Recent Conversation ===")
            for conv in context.conversation_history[-5:]:
                parts.append(f"{conv.role}: {conv.content[:200]}")
        
        parts.append(f"\n=== Query ===\n{query}")
        parts.append("\nPlease provide a comprehensive answer based on the above context.")
        
        return "\n".join(parts)


class MemoryIngestionService:
    def __init__(
        self,
        memory_repo: MemoryRepository,
        kg_repo: KnowledgeGraphRepository,
        ai_service: AIService,
    ):
        self.memory_repo = memory_repo
        self.kg_repo = kg_repo
        self.ai_service = ai_service

    async def ingest_candidate_memory(
        self,
        tenant_id: UUID,
        candidate_id: UUID,
        content: str,
        title: str,
        memory_type: MemoryType = MemoryType.CANDIDATE,
        source: str = "system",
        source_id: UUID | None = None,
        tags: list[str] | None = None,
        importance: str = "medium",
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        embedding = await self.ai_service.create_embedding(content)
        
        memory = Memory(
            tenant_id=tenant_id,
            memory_type=memory_type,
            entity_type=EntityType.CANDIDATE,
            entity_id=candidate_id,
            title=title,
            content=content,
            importance=importance,
            embedding=embedding,
            source=source,
            source_id=source_id,
            tags=tags or [],
            metadata=metadata or {},
        )
        
        await self.memory_repo.add(memory)
        
        await self._extract_and_store_entities(tenant_id, memory)
        
        return memory

    async def ingest_conversation(
        self,
        tenant_id: UUID,
        user_id: UUID,
        session_id: str,
        role: str,
        content: str,
        conversation_id: UUID | None = None,
        model: str | None = None,
        tokens: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationMemory:
        conv_memory = ConversationMemory(
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            tokens=tokens,
            metadata=metadata or {},
        )
        
        await self.conversation_repo.add(conv_memory)
        return conv_memory

    async def create_kg_entity(
        self,
        tenant_id: UUID,
        entity_type: EntityType,
        name: str,
        external_id: UUID | None = None,
        description: str | None = None,
        aliases: list[str] | None = None,
        properties: dict[str, Any] | None = None,
    ) -> KnowledgeGraphEntity:
        content = f"{name}: {description or ''}"
        embedding = await self.ai_service.create_embedding(content)
        
        entity = KnowledgeGraphEntity(
            tenant_id=tenant_id,
            entity_type=entity_type,
            external_id=external_id,
            name=name,
            description=description,
            aliases=aliases or [],
            properties=properties or {},
            embedding=embedding,
        )
        
        await self.kg_repo.add_entity(entity)
        return entity

    async def create_kg_relation(
        self,
        tenant_id: UUID,
        source_entity_id: UUID,
        target_entity_id: UUID,
        relation_type: RelationType,
        properties: dict[str, Any] | None = None,
        weight: float = 1.0,
    ) -> KnowledgeGraphRelation:
        relation = KnowledgeGraphRelation(
            tenant_id=tenant_id,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relation_type=relation_type,
            properties=properties or {},
            weight=weight,
        )
        
        await self.kg_repo.add_relation(relation)
        return relation

    async def _extract_and_store_entities(
        self,
        tenant_id: UUID,
        memory: Memory,
    ) -> None:
        extraction_prompt = f"""
        Extract entities from the following text. Return a JSON array of entities with:
        - name: entity name
        - type: one of [candidate, job, company, recruiter, hiring_manager, skill, technology, certification, project]
        - description: brief description
        - properties: any relevant properties
        
        Text: {memory.content[:2000]}
        """
        
        response = await self.ai_service.structured_completion(
            messages=[{"role": "user", "content": extraction_prompt}],
            response_model=list[dict[str, Any]],
        )
        
        for entity_data in response:
            entity = await self.create_kg_entity(
                tenant_id=tenant_id,
                entity_type=EntityType(entity_data["type"]),
                name=entity_data["name"],
                description=entity_data.get("description"),
                properties=entity_data.get("properties"),
            )
            
            await self.create_kg_relation(
                tenant_id=tenant_id,
                source_entity_id=entity.id,
                target_entity_id=entity.id,
                relation_type=RelationType.SIMILAR_TO,
            )