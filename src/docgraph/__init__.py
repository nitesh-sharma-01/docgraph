"""DocGraph public package interface."""

from docgraph.core.document import Document
from docgraph.core.entity import Entity
from docgraph.core.graph import Graph, NetworkXGraph
from docgraph.core.relationship import Relationship
from docgraph.extraction.base import ExtractionResult
from docgraph.extraction.pipeline import ExtractionPipeline, PipelineResult
from docgraph.extraction.rule import RuleExtractor
from docgraph.parser.markdown import MarkdownParser
from docgraph.validation.schema import Ontology
from docgraph.validation.validator import OntologyValidator, ValidationIssue

__all__ = [
    "Document",
    "Entity",
    "ExtractionPipeline",
    "ExtractionResult",
    "Graph",
    "MarkdownParser",
    "NetworkXGraph",
    "Ontology",
    "OntologyValidator",
    "PipelineResult",
    "Relationship",
    "RuleExtractor",
    "ValidationIssue",
]

__version__ = "0.1.0"
