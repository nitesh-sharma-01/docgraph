"""NetworkX-backed visualization helpers."""

from __future__ import annotations

from typing import Any

import networkx as nx

from docgraph.core.graph import Graph


def spring_layout_payload(graph: Graph) -> dict[str, Any]:
    """Create a deterministic, serializable layout payload for visualization."""

    networkx_graph = nx.MultiDiGraph()
    for entity in graph.entities():
        networkx_graph.add_node(entity.id, label=entity.name, type=entity.type)
    for relationship in graph.relationships():
        networkx_graph.add_edge(
            relationship.source,
            relationship.target,
            relation=relationship.relation,
            confidence=relationship.confidence,
        )

    positions = nx.spring_layout(networkx_graph, seed=42)
    return {
        "nodes": [
            {
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "x": float(positions.get(entity.id, [0.0, 0.0])[0]),
                "y": float(positions.get(entity.id, [0.0, 0.0])[1]),
            }
            for entity in graph.entities()
        ],
        "edges": [
            {
                "source": relationship.source,
                "target": relationship.target,
                "relation": relationship.relation,
                "confidence": relationship.confidence,
            }
            for relationship in graph.relationships()
        ],
    }
