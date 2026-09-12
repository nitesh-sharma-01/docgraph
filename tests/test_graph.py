import json

from docgraph.core.entity import Entity
from docgraph.core.graph import NetworkXGraph
from docgraph.core.relationship import Relationship
from docgraph.storage.json import JSONGraphStore


def test_networkx_graph_adds_entities_relationships_and_neighbors() -> None:
    graph = NetworkXGraph()
    graph.add_entity(Entity(id="orders", type="service", name="Orders"))
    graph.add_entity(Entity(id="postgresql", type="database", name="PostgreSQL"))
    graph.add_relationship(
        Relationship(
            source="orders",
            relation="DEPENDS_ON",
            target="postgresql",
            confidence=1.0,
        )
    )

    assert graph.get_entity("orders").name == "Orders"
    assert [entity.id for entity in graph.neighbors("orders")] == ["postgresql"]
    assert [entity.id for entity in graph.neighbors("orders", "DEPENDS_ON")] == [
        "postgresql"
    ]


def test_json_export_is_stable(tmp_path) -> None:
    graph = NetworkXGraph()
    graph.add_entity(Entity(id="b", type="service", name="B"))
    graph.add_entity(Entity(id="a", type="service", name="A"))
    graph.add_relationship(Relationship(source="a", relation="DEPENDS_ON", target="b"))

    output = JSONGraphStore().save(graph, tmp_path / "graph.json")
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert [entity["id"] for entity in payload["entities"]] == ["a", "b"]
    assert payload["relationships"][0]["relation"] == "DEPENDS_ON"
    assert payload["metadata"]["version"] == "0.1.0"
