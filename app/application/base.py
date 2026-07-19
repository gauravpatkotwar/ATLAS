from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")
R = TypeVar("R")


class Command(BaseModel, Generic[T]):
    model_config = ConfigDict(frozen=True)

    command_id: UUID = field(default_factory=UUID)
    timestamp: float = field(default_factory=lambda: __import__("time").time())
    correlation_id: UUID | None = None
    causation_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Query(BaseModel, Generic[R]):
    model_config = ConfigDict(frozen=True)

    query_id: UUID = field(default_factory=UUID)
    timestamp: float = field(default_factory=lambda: __import__("time").time())
    correlation_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class CommandHandler(ABC, Generic[T, R]):
    @abstractmethod
    async def handle(self, command: T) -> R:
        pass


class QueryHandler(ABC, Generic[T, R]):
    @abstractmethod
    async def handle(self, query: T) -> R:
        pass


class MessageBus:
    def __init__(self):
        self._command_handlers: dict[type, CommandHandler] = {}
        self._query_handlers: dict[type, QueryHandler] = {}

    def register_command_handler(self, command_type: type[T], handler: CommandHandler[T, R]) -> None:
        self._command_handlers[command_type] = handler

    def register_query_handler(self, query_type: type[T], handler: QueryHandler[T, R]) -> None:
        self._query_handlers[query_type] = handler

    async def dispatch_command(self, command: T) -> R:
        handler = self._command_handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for command {type(command).__name__}")
        return await handler.handle(command)

    async def dispatch_query(self, query: T) -> R:
        handler = self._query_handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for query {type(query).__name__}")
        return await handler.handle(query)


message_bus = MessageBus()


@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@dataclass
class SortParams:
    field: str = "created_at"
    direction: str = "desc"

    def __post_init__(self):
        if self.direction.lower() not in ("asc", "desc"):
            raise ValueError("Direction must be 'asc' or 'desc'")


@dataclass
class FilterParams:
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class PaginatedResponse(Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1