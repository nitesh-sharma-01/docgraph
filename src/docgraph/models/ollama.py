"""Optional Ollama model adapter."""

from __future__ import annotations

import json
from urllib import request

from docgraph.models.base import Model, ModelError


class OllamaModel(Model):
    """Minimal Ollama adapter using the local HTTP API."""

    def __init__(self, name: str, base_url: str = "http://localhost:11434") -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        payload = json.dumps(
            {"model": self.name, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        url = f"{self.base_url}/api/generate"
        http_request = request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
        except OSError as exc:
            raise ModelError(f"Ollama generation failed: {exc}") from exc

        generated = data.get("response")
        if not isinstance(generated, str):
            raise ModelError("Ollama response did not include a text response.")
        return generated
