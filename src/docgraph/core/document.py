"""Parsed document models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DocumentLink(BaseModel):
    """A link discovered while parsing a document."""

    text: str
    target: str
    kind: str


class CodeBlock(BaseModel):
    """A fenced code block from a parsed document."""

    language: str | None = None
    content: str


class Section(BaseModel):
    """A Markdown section with extracted block-level content."""

    heading: str
    level: int
    paragraphs: list[str] = Field(default_factory=list)
    items: list[str] = Field(default_factory=list)
    links: list[DocumentLink] = Field(default_factory=list)
    code_blocks: list[CodeBlock] = Field(default_factory=list)


class Document(BaseModel):
    """A parsed source document."""

    source: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    title: str | None = None
    sections: list[Section] = Field(default_factory=list)
    links: list[DocumentLink] = Field(default_factory=list)
    code_blocks: list[CodeBlock] = Field(default_factory=list)
