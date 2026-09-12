"""Graph abstraction and the initial NetworkX-backed implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

import networkx as nx

from docgraph.core.entity import Entity
from docgraph.core.relationship import Relationship


class Graph(ABC):
    """Storage-neutral graph interface used by extraction and output layers."""

    @abstractmethod
    def add_entity(self, entity: Entity) -> None:
        """Add or update an entity."""

    @abstractmethod
    def add_relationship(self, relationship: Relationship) -> None:
        """Add or update a relationship."""

    @abstractmethod
    def get_entity(self, entity_id: str) -> Entity | None:
        """Return an entity by id."""

    @abstractmethod
    def neighbors(self, entity_id: str, relation: str | None = None) -> list[Entity]:
        """Return outgoing neighbor entities, optionally filtered by relation."""

    @abstractmethod
    def entities(self) -> list[Entity]:
        """Return graph entities in deterministic order."""

    @abstractmethod
    def relationships(self) -> list[Relationship]:
        """Return graph relationships in deterministic order."""

    def add_entities(self, entities: Iterable[Entity]) -> None:
        for entity in entities:
            self.add_entity(entity)

    def add_relationships(self, relationships: Iterable[Relationship]) -> None:
        for relationship in relationships:
            self.add_relationship(relationship)


class NetworkXGraph(Graph):
    """NetworkX implementation hidden behind the DocGraph interface."""

    def __init__(self) -> None:
        self._graph = nx.MultiDiGraph()

    def add_entity(self, entity: Entity) -> None:
        self._graph.add_node(entity.id, entity=entity)

    def add_relationship(self, relationship: Relationship) -> None:
        key = self._relationship_key(relationship)
        self._graph.add_edge(
            relationship.source,
            relationship.target,
            key=key,
            relationship=relationship,
        )

    def get_entity(self, entity_id: str) -> Entity | None:
        if entity_id not in self._graph:
            return None
        data = self._graph.nodes[entity_id]
        entity = data.get("entity")
        return entity if isinstance(entity, Entity) else None

    def neighbors(self, entity_id: str, relation: str | None = None) -> list[Entity]:
        if entity_id not in self._graph:
            return []

        neighbors: list[Entity] = []
        for _, target, edge_data in self._graph.out_edges(entity_id, data=True):
            relationship = edge_data.get("relationship")
            if relation is not None and relationship.relation != relation:
                continue
            entity = self.get_entity(target)
            if entity is not None:
                neighbors.append(entity)

        return sorted(neighbors, key=lambda entity: entity.id)

    def entities(self) -> list[Entity]:
        entities = [
            data["entity"]
            for _, data in self._graph.nodes(data=True)
            if isinstance(data.get("entity"), Entity)
        ]
        return sorted(entities, key=lambda entity: entity.id)

    def relationships(self) -> list[Relationship]:
        relationships = [
            data["relationship"]
            for _, _, data in self._graph.edges(data=True)
            if isinstance(data.get("relationship"), Relationship)
        ]
        return sorted(
            relationships,
            key=lambda item: (
                item.source,
                item.relation,
                item.target,
                item.source_document or "",
            ),
        )

    @staticmethod
    def _relationship_key(relationship: Relationship) -> str:
        return "|".join(
            [
                relationship.source,
                relationship.relation,
                relationship.target,
                relationship.source_document or "",
            ]
        )
