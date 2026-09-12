import json
from pathlib import Path

from docgraph.extraction.model import ModelExtractor
from docgraph.extraction.rule import RuleExtractor
from docgraph.models.base import Model
from docgraph.parser.markdown import MarkdownParser


def _fixture_document():
    content = Path("tests/fixtures/service.md").read_text(encoding="utf-8")
    return MarkdownParser().parse(content, "service.md")


def test_rule_extractor_extracts_entities_and_relationships() -> None:
    result = RuleExtractor().extract(_fixture_document())

    entities = {entity.id: entity for entity in result.entities}
    assert entities["order-service"].type == "service"
    assert entities["mongodb"].type == "database"
    assert entities["sqs"].type == "queue"
    assert entities["iot-service"].type == "service"
    assert entities["orderupdatedevent"].type == "event"
    assert entities["api-post-v1-orders"].type == "api"
    assert entities["order-management"].type == "owner"

    relationships = {
        (relationship.relation, relationship.target)
        for relationship in result.relationships
    }
    assert ("DEPENDS_ON", "mongodb") in relationships
    assert ("DEPENDS_ON", "sqs") in relationships
    assert ("DEPENDS_ON", "iot-service") in relationships
    assert ("PUBLISHES", "orderupdatedevent") in relationships
    assert ("CONSUMES", "orderupdatedevent") in relationships
    assert ("STORES_IN", "mongodb") in relationships
    assert ("EXPOSES_API", "api-post-v1-orders") in relationships
    assert ("OWNED_BY", "order-management") in relationships

    assert all(relationship.confidence == 1.0 for relationship in result.relationships)


def test_model_extractor_accepts_structured_model_output() -> None:
    class FakeModel(Model):
        def generate(self, prompt: str) -> str:
            return json.dumps(
                {
                    "entities": [
                        {
                            "id": "orders",
                            "type": "service",
                            "name": "Orders",
                            "source": "model.md",
                            "metadata": {},
                        }
                    ],
                    "relationships": [],
                }
            )

    result = ModelExtractor(FakeModel()).extract(_fixture_document())

    assert len(result.entities) == 1
    assert result.entities[0].id == "orders"
    assert result.metadata["source"] == "model"
