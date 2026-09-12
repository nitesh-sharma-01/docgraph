"""Parser interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from docgraph.core.document import Document


class DocumentParser(ABC):
    """A parser turns source text into a normalized Document."""

    @abstractmethod
    def parse(self, content: str, source: str) -> Document:
        """Parse raw content from a source path or identifier."""
