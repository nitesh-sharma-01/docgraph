"""Extraction interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from docgraph.core.document import Document
from docgraph.core.entity import Entity
from docgraph.core.relationship import Relationship


class ExtractionResult(BaseModel):
    """Entities and relationships extracted from a document or corpus."""

    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    ambiguous: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def deduplicated(self) -> "ExtractionResult":
        entities = {entity.id: entity for entity in self.entities}
        relationships = {
            (
                relationship.source,
                relationship.relation,
                relationship.target,
                relationship.source_document,
            ): relationship
            for relationship in self.relationships
        }
        return ExtractionResult(
            entities=sorted(entities.values(), key=lambda item: item.id),
            relationships=sorted(
                relationships.values(),
                key=lambda item: (
                    item.source,
                    item.relation,
                    item.target,
                    item.source_document or "",
                ),
            ),
            ambiguous=sorted(set(self.ambiguous)),
            metadata=self.metadata,
        )


class Extractor(ABC):
    """An extractor creates typed graph candidates from a parsed document."""

    @abstractmethod
    def extract(self, document: Document) -> ExtractionResult:
        """Extract graph candidates from a parsed document."""
