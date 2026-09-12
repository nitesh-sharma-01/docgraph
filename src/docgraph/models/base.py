"""Model provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ModelError(RuntimeError):
    """Raised when a model provider cannot generate output."""


class Model(ABC):
    """A text generation provider used by optional extraction steps."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text for a prompt."""
