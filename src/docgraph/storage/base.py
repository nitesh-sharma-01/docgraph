"""Storage interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from docgraph.core.graph import Graph


class GraphStore(ABC):
    """Persist a graph to an external representation."""

    @abstractmethod
    def save(self, graph: Graph, path: str | Path) -> Path:
        """Save a graph and return the output path."""
