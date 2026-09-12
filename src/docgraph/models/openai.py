"""Optional OpenAI model adapter."""

from __future__ import annotations

from typing import Any

from docgraph.models.base import Model


class OpenAIModel(Model):
    """OpenAI adapter loaded only when the optional dependency is installed."""

    def __init__(self, name: str, client: Any | None = None) -> None:
        self.name = name
        if client is not None:
            self.client = client
            return

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "OpenAI support requires installing docgraph[openai]."
            ) from exc

        self.client = OpenAI()

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(model=self.name, input=prompt)
        return response.output_text
