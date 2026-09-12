"""Future SQLite storage placeholder."""

from __future__ import annotations

from pathlib import Path

from docgraph.core.graph import Graph
from docgraph.storage.base import GraphStore


class SQLiteGraphStore(GraphStore):
    """Reserved adapter for a future SQLite graph backend."""

    def save(self, graph: Graph, path: str | Path) -> Path:
        raise NotImplementedError("SQLite storage is planned but not implemented yet.")
