"""Deterministic Markdown extraction rules."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from docgraph.core.document import Document, Section
from docgraph.core.entity import Entity
from docgraph.core.relationship import Relationship
from docgraph.extraction.base import ExtractionResult, Extractor
from docgraph.utils import slugify

WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


class RuleExtractor(Extractor):
    """Extract common documentation relationships from Markdown conventions."""

    SECTION_RELATIONS = {
        "depends on": ("DEPENDS_ON", "dependency"),
        "dependencies": ("DEPENDS_ON", "dependency"),
        "publishes": ("PUBLISHES", "event"),
        "published events": ("PUBLISHES", "event"),
        "consumes": ("CONSUMES", "event"),
        "consumed events": ("CONSUMES", "event"),
        "database": ("STORES_IN", "database"),
        "databases": ("STORES_IN", "database"),
        "apis": ("EXPOSES_API", "api"),
        "api": ("EXPOSES_API", "api"),
        "endpoints": ("EXPOSES_API", "api"),
        "owner": ("OWNED_BY", "owner"),
    }

    DATABASE_HINTS = {
        "postgres",
        "postgresql",
        "mysql",
        "mariadb",
        "mongodb",
        "mongo",
        "redis",
        "dynamodb",
        "sqlite",
        "oracle",
        "sql server",
        "cassandra",
    }
    QUEUE_HINTS = {"sqs", "queue", "topic", "kafka", "rabbitmq", "pubsub", "sns"}

    def extract(self, document: Document) -> ExtractionResult:
        source_entity = self._source_entity(document)
        entities: dict[str, Entity] = {source_entity.id: source_entity}
        relationships: dict[tuple[str, str, str, str | None], Relationship] = {}

        owner = document.metadata.get("owner")
        if isinstance(owner, str) and owner.strip():
            self._add_related_entity(
                entities=entities,
                relationships=relationships,
                source_entity=source_entity,
                document=document,
                relation="OWNED_BY",
                target_name=owner,
                target_type="owner",
                metadata={"extracted_from": "frontmatter.owner"},
            )

        for section in document.sections:
            relation_info = self.SECTION_RELATIONS.get(self._canonical_heading(section.heading))
            if relation_info is None:
                continue

            relation, target_kind = relation_info
            for raw_value in self._section_values(section):
                target_name = self._clean_value(raw_value)
                if not target_name:
                    continue
                self._add_related_entity(
                    entities=entities,
                    relationships=relationships,
                    source_entity=source_entity,
                    document=document,
                    relation=relation,
                    target_name=target_name,
                    target_type=self._target_type(target_name, target_kind),
                    metadata={"extracted_from": section.heading},
                )

        return ExtractionResult(
            entities=sorted(entities.values(), key=lambda entity: entity.id),
            relationships=sorted(
                relationships.values(),
                key=lambda item: (
                    item.source,
                    item.relation,
                    item.target,
                    item.source_document or "",
                ),
            ),
        )

    @staticmethod
    def _source_entity(document: Document) -> Entity:
        name = str(
            document.metadata.get("name")
            or document.metadata.get("title")
            or document.title
            or document.source
        )
        entity_type = str(document.metadata.get("type") or "document")
        entity_id = str(document.metadata.get("id") or slugify(name))
        metadata: dict[str, Any] = dict(document.metadata)
        return Entity(
            id=entity_id,
            type=entity_type,
            name=name,
            source=document.source,
            metadata=metadata,
        )

    @classmethod
    def _target_type(cls, value: str, target_kind: str) -> str:
        if target_kind != "dependency":
            return target_kind

        normalized = value.strip().lower()
        if cls._looks_like_database(normalized):
            return "database"
        if cls._looks_like_queue(normalized):
            return "queue"
        return "service"

    @classmethod
    def _looks_like_database(cls, normalized: str) -> bool:
        return any(hint in normalized for hint in cls.DATABASE_HINTS) or normalized.endswith("db")

    @classmethod
    def _looks_like_queue(cls, normalized: str) -> bool:
        return any(hint in normalized for hint in cls.QUEUE_HINTS)

    @staticmethod
    def _entity_id(name: str, entity_type: str) -> str:
        if entity_type == "api":
            return f"api-{slugify(name)}"
        return slugify(name)

    @classmethod
    def _add_related_entity(
        cls,
        *,
        entities: dict[str, Entity],
        relationships: dict[tuple[str, str, str, str | None], Relationship],
        source_entity: Entity,
        document: Document,
        relation: str,
        target_name: str,
        target_type: str,
        metadata: dict[str, Any],
    ) -> None:
        target_id = cls._entity_id(target_name, target_type)
        entities[target_id] = Entity(
            id=target_id,
            type=target_type,
            name=target_name,
            source=document.source,
            metadata=metadata,
        )
        relationship = Relationship(
            source=source_entity.id,
            relation=relation,
            target=target_id,
            source_document=document.source,
            confidence=1.0,
            metadata=metadata,
        )
        relationships[
            (
                relationship.source,
                relationship.relation,
                relationship.target,
                relationship.source_document,
            )
        ] = relationship

    @staticmethod
    def _canonical_heading(heading: str) -> str:
        return re.sub(r"\s+", " ", heading.strip().lower())

    @staticmethod
    def _section_values(section: Section) -> Iterable[str]:
        if section.items:
            return section.items
        return section.paragraphs

    @staticmethod
    def _clean_value(raw_value: str) -> str:
        value = raw_value.strip()
        wiki_match = WIKI_LINK_RE.fullmatch(value)
        if wiki_match is not None:
            return wiki_match.group(1).strip()

        wiki_links = WIKI_LINK_RE.findall(value)
        if len(wiki_links) == 1:
            return wiki_links[0].strip()

        value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", value)
        return value.strip()
