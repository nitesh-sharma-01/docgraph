from docgraph.core.entity import Entity
from docgraph.core.relationship import Relationship
from docgraph.extraction.base import ExtractionResult
from docgraph.parser.markdown import MarkdownParser
from docgraph.extraction.rule import RuleExtractor
from docgraph.validation.schema import Ontology
from docgraph.validation.validator import OntologyValidator


def test_default_ontology_validates_fixture() -> None:
    content = open("tests/fixtures/service.md", encoding="utf-8").read()
    document = MarkdownParser().parse(content, "service.md")
    result = RuleExtractor().extract(document)

    issues = OntologyValidator(Ontology.default()).validate(result)

    assert issues == []


def test_invalid_relationship_is_reported_and_filtered() -> None:
    result = ExtractionResult(
        entities=[
            Entity(id="orders", type="service", name="Orders"),
            Entity(id="ordercreatedevent", type="event", name="OrderCreatedEvent"),
        ],
        relationships=[
            Relationship(
                source="orders",
                relation="DEPENDS_ON",
                target="ordercreatedevent",
            )
        ],
    )
    validator = OntologyValidator(Ontology.default())

    issues = validator.validate(result)
    filtered = validator.filter_valid(result)

    assert len(issues) == 1
    assert issues[0].kind == "invalid_target_type"
    assert filtered.relationships == []
