"""Entity domain model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """A typed node in a documentation knowledge graph."""

    id: str
    type: str
    name: str
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
