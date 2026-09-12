"""Small shared helpers."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel


def slugify(value: str) -> str:
    """Create a stable id from a human-readable name."""

    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-") or "unnamed"


def model_to_dict(model: BaseModel) -> dict[str, Any]:
    """Return a dict for Pydantic v2 models."""

    return model.model_dump(mode="json")
