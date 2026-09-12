"""Configuration models and defaults."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from docgraph.validation.schema import Ontology


class SourceConfig(BaseModel):
    path: str = "./docs"
    format: Literal["markdown"] = "markdown"


class OntologyConfig(BaseModel):
    path: str = "./ontology.yaml"


class ExtractionConfig(BaseModel):
    strategy: Literal["deterministic", "hybrid"] = "deterministic"


class GraphConfig(BaseModel):
    backend: Literal["networkx"] = "networkx"


class OutputConfig(BaseModel):
    format: Literal["json"] = "json"
    path: str = "./output/graph.json"


class ModelConfig(BaseModel):
    provider: str | None = None
    name: str | None = None


class DocGraphConfig(BaseModel):
    source: SourceConfig = Field(default_factory=SourceConfig)
    ontology: OntologyConfig = Field(default_factory=OntologyConfig)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    graph: GraphConfig = Field(default_factory=GraphConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    model: ModelConfig | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> "DocGraphConfig":
        with Path(path).open("r", encoding="utf-8") as file:
            payload = yaml.safe_load(file) or {}
        return cls.model_validate(payload)

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.model_dump(mode="json", exclude_none=True), sort_keys=False)


def resolve_path(base_dir: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base_dir / path


def default_config_yaml() -> str:
    return DocGraphConfig().to_yaml()


def default_ontology_yaml() -> str:
    return Ontology.default().to_yaml()
