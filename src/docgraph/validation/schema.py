"""Ontology schema models."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class EntityType(BaseModel):
    """An allowed entity type."""

    description: str | None = None


class RelationshipRule(BaseModel):
    """Allowed source and target entity types for a relationship."""

    source: str | list[str]
    target: str | list[str]

    @property
    def source_types(self) -> set[str]:
        return {self.source} if isinstance(self.source, str) else set(self.source)

    @property
    def target_types(self) -> set[str]:
        return {self.target} if isinstance(self.target, str) else set(self.target)


class Ontology(BaseModel):
    """Allowed entity and relationship types for a graph."""

    entities: dict[str, EntityType] = Field(default_factory=dict)
    relationships: dict[str, RelationshipRule] = Field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Ontology":
        with Path(path).open("r", encoding="utf-8") as file:
            payload = yaml.safe_load(file) or {}
        return cls.model_validate(payload)

    @classmethod
    def default(cls) -> "Ontology":
        return cls.model_validate(
            {
                "entities": {
                    "document": {"description": "Generic documentation artifact"},
                    "service": {"description": "Software service or microservice"},
                    "database": {"description": "Persistent data store"},
                    "event": {"description": "Domain or integration event"},
                    "api": {"description": "API endpoint"},
                    "queue": {"description": "Queue, topic, or message broker"},
                    "owner": {"description": "Team or person that owns an entity"},
                },
                "relationships": {
                    "DEPENDS_ON": {
                        "source": ["service", "document"],
                        "target": ["service", "database", "queue"],
                    },
                    "PUBLISHES": {
                        "source": ["service", "document"],
                        "target": "event",
                    },
                    "CONSUMES": {
                        "source": ["service", "document"],
                        "target": "event",
                    },
                    "STORES_IN": {
                        "source": ["service", "document"],
                        "target": "database",
                    },
                    "EXPOSES_API": {
                        "source": ["service", "document"],
                        "target": "api",
                    },
                    "OWNED_BY": {
                        "source": ["service", "document"],
                        "target": "owner",
                    },
                },
            }
        )

    def to_yaml(self) -> str:
        payload = self.model_dump(mode="json")
        return yaml.safe_dump(payload, sort_keys=False)
