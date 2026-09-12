"""Ontology validation logic."""

from __future__ import annotations

from pydantic import BaseModel

from docgraph.core.entity import Entity
from docgraph.core.relationship import Relationship
from docgraph.extraction.base import ExtractionResult
from docgraph.validation.schema import Ontology


class ValidationIssue(BaseModel):
    """A validation issue found before graph insertion."""

    message: str
    kind: str
    entity_id: str | None = None
    relationship: Relationship | None = None


class OntologyValidator:
    """Validate extracted entities and relationships against an ontology."""

    def __init__(self, ontology: Ontology) -> None:
        self.ontology = ontology

    def validate_entities(self, entities: list[Entity]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for entity in entities:
            if entity.type not in self.ontology.entities:
                issues.append(
                    ValidationIssue(
                        kind="unknown_entity_type",
                        entity_id=entity.id,
                        message=(
                            f"Entity '{entity.id}' uses unknown type "
                            f"'{entity.type}'."
                        ),
                    )
                )
        return issues

    def validate_relationships(
        self,
        relationships: list[Relationship],
        entities: list[Entity],
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        entity_map = {entity.id: entity for entity in entities}

        for relationship in relationships:
            rule = self.ontology.relationships.get(relationship.relation)
            if rule is None:
                issues.append(
                    ValidationIssue(
                        kind="unknown_relationship",
                        relationship=relationship,
                        message=(
                            f"Relationship '{relationship.relation}' is not "
                            "defined in the ontology."
                        ),
                    )
                )
                continue

            source = entity_map.get(relationship.source)
            target = entity_map.get(relationship.target)
            if source is None:
                issues.append(
                    ValidationIssue(
                        kind="missing_source_entity",
                        relationship=relationship,
                        message=(
                            f"Relationship '{relationship.relation}' references "
                            f"missing source entity '{relationship.source}'."
                        ),
                    )
                )
                continue
            if target is None:
                issues.append(
                    ValidationIssue(
                        kind="missing_target_entity",
                        relationship=relationship,
                        message=(
                            f"Relationship '{relationship.relation}' references "
                            f"missing target entity '{relationship.target}'."
                        ),
                    )
                )
                continue

            if source.type not in rule.source_types:
                issues.append(
                    ValidationIssue(
                        kind="invalid_source_type",
                        relationship=relationship,
                        message=(
                            f"Relationship '{relationship.relation}' does not "
                            f"allow source type '{source.type}'."
                        ),
                    )
                )
            if target.type not in rule.target_types:
                issues.append(
                    ValidationIssue(
                        kind="invalid_target_type",
                        relationship=relationship,
                        message=(
                            f"Relationship '{relationship.relation}' does not "
                            f"allow target type '{target.type}'."
                        ),
                    )
                )

        return issues

    def validate(self, result: ExtractionResult) -> list[ValidationIssue]:
        issues = self.validate_entities(result.entities)
        issues.extend(self.validate_relationships(result.relationships, result.entities))
        return issues

    def filter_valid(self, result: ExtractionResult) -> ExtractionResult:
        """Remove invalid relationships and entities with unknown types."""

        valid_entities = [
            entity
            for entity in result.entities
            if entity.type in self.ontology.entities
        ]
        known_valid_ids = {entity.id for entity in valid_entities}
        valid_relationships: list[Relationship] = []

        for relationship in result.relationships:
            candidate = ExtractionResult(
                entities=valid_entities,
                relationships=[relationship],
            )
            if (
                relationship.source in known_valid_ids
                and relationship.target in known_valid_ids
                and not self.validate(candidate)
            ):
                valid_relationships.append(relationship)

        return ExtractionResult(
            entities=valid_entities,
            relationships=valid_relationships,
            ambiguous=result.ambiguous,
            metadata=result.metadata,
        ).deduplicated()
