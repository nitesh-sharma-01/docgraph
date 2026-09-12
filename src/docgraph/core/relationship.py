"""Relationship domain model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Relationship(BaseModel):
    """A typed edge between two graph entities."""

    source: str
    relation: str
    target: str
    source_document: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
