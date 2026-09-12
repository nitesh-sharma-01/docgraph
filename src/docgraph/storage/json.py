"""Stable JSON graph export."""

from __future__ import annotations

import json as json_module
from pathlib import Path
from typing import Any

from docgraph import __version__
from docgraph.core.graph import Graph
from docgraph.storage.base import GraphStore
from docgraph.utils import model_to_dict


class JSONGraphStore(GraphStore):
    """Persist graph data as deterministic, readable JSON."""

    def save(self, graph: Graph, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.to_payload(graph)
        output_path.write_text(
            json_module.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return output_path

    @staticmethod
    def to_payload(graph: Graph) -> dict[str, Any]:
        return {
            "entities": [model_to_dict(entity) for entity in graph.entities()],
            "relationships": [
                model_to_dict(relationship)
                for relationship in graph.relationships()
            ],
            "metadata": {"version": __version__},
        }
