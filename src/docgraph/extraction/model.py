"""Optional model-backed extractor."""

from __future__ import annotations

import json

from pydantic import ValidationError

from docgraph.core.document import Document
from docgraph.core.entity import Entity
from docgraph.core.relationship import Relationship
from docgraph.extraction.base import ExtractionResult, Extractor
from docgraph.models.base import Model, ModelError


class ModelExtractor(Extractor):
    """Extract entities and relationships from structured model output."""

    def __init__(self, model: Model) -> None:
        self.model = model

    def extract(self, document: Document) -> ExtractionResult:
        prompt = self._prompt(document)
        raw_output = self.model.generate(prompt)

        try:
            payload = json.loads(raw_output)
            entities = [
                Entity.model_validate(entity)
                for entity in payload.get("entities", [])
            ]
            relationships = [
                Relationship.model_validate(relationship)
                for relationship in payload.get("relationships", [])
            ]
        except (json.JSONDecodeError, AttributeError, TypeError, ValidationError) as exc:
            raise ModelError("Model output was not valid DocGraph JSON.") from exc

        return ExtractionResult(
            entities=entities,
            relationships=relationships,
            metadata={"source": "model"},
        ).deduplicated()

    @staticmethod
    def _prompt(document: Document) -> str:
        return "\n".join(
            [
                "Extract documentation knowledge graph candidates.",
                "Return JSON with top-level 'entities' and 'relationships' arrays.",
                "Every entity must match: id, type, name, source, metadata.",
                (
                    "Every relationship must match: source, relation, target, "
                    "source_document, confidence, metadata."
                ),
                "Do not include prose outside JSON.",
                "",
                f"Source: {document.source}",
                document.content,
            ]
        )
