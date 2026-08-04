"""Data models for the memory store."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    """Represents a single memory record to be stored.

    Attributes:
        id: A unique identifier for the memory.
        content: The textual content of the memory.
        embedding: The vector embedding of the content.
        metadata: A dictionary of additional metadata.
    """

    id: str
    content: str
    embedding: List[float]
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Represents a single result from a similarity search.

    Attributes:
        id: The unique identifier of the found memory.
        content: The content of the found memory.
        score: The similarity score.
        metadata: The metadata of the found memory.
    """

    id: str
    content: str
    score: float
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)