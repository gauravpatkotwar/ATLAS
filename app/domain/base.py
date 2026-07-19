from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T", bound="Entity")


class Entity(ABC, Generic[T]):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    version: int = 1

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid4())
        self.created_at = kwargs.get("created_at", datetime.utcnow())
        self.updated_at = kwargs.get("updated_at", datetime.utcnow())
        self.deleted_at = kwargs.get("deleted_at")
        self.version = kwargs.get("version", 1)

    def mark_deleted(self) -> None:
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_updated(self) -> None:
        self.updated_at = datetime.utcnow()
        self.version += 1

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class AggregateRoot(Entity[T]):
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def add_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def clear_domain_events(self) -> list[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


class ValueObject(ABC):
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))


class DomainEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    aggregate_id: UUID
    aggregate_type: str
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DomainEventPublisher:
    def __init__(self):
        self._handlers: dict[str, list[callable]] = {}

    def subscribe(self, event_type: str, handler: callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: callable) -> None:
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            await handler(event)

    async def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)


domain_event_publisher = DomainEventPublisher()