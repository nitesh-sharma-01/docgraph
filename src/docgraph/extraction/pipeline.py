"""Extraction pipeline orchestration."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from docgraph.core.document import Document
from docgraph.core.graph import Graph, NetworkXGraph
from docgraph.extraction.base import ExtractionResult, Extractor
from docgraph.validation.validator import OntologyValidator, ValidationIssue


@dataclass(frozen=True)
class PipelineResult:
    """Result of running extraction, validation, and graph construction."""

    documents: list[Document]
    extracted: ExtractionResult
    valid: ExtractionResult
    validation_issues: list[ValidationIssue]
    graph: Graph


class ExtractionPipeline:
    """Run extractors, validate candidates, and build a graph."""

    def __init__(
        self,
        extractor: Extractor,
        validator: OntologyValidator,
        graph: Graph | None = None,
    ) -> None:
        self.extractor = extractor
        self.validator = validator
        self.graph = graph or NetworkXGraph()

    def run(self, documents: Iterable[Document]) -> PipelineResult:
        document_list = list(documents)
        aggregate = ExtractionResult()

        for document in document_list:
            extracted = self.extractor.extract(document)
            aggregate.entities.extend(extracted.entities)
            aggregate.relationships.extend(extracted.relationships)
            aggregate.ambiguous.extend(extracted.ambiguous)

        aggregate = aggregate.deduplicated()
        issues = self.validator.validate(aggregate)
        valid = self.validator.filter_valid(aggregate)

        self.graph.add_entities(valid.entities)
        self.graph.add_relationships(valid.relationships)

        return PipelineResult(
            documents=document_list,
            extracted=aggregate,
            valid=valid,
            validation_issues=issues,
            graph=self.graph,
        )
