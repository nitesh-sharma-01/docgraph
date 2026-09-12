"""Markdown parser implementation."""

from __future__ import annotations

import re
from typing import Any

import yaml
from markdown_it import MarkdownIt
from markdown_it.token import Token

from docgraph.core.document import CodeBlock, Document, DocumentLink, Section
from docgraph.parser.base import DocumentParser

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


class MarkdownParser(DocumentParser):
    """Parse Markdown into DocGraph's neutral document model."""

    def __init__(self) -> None:
        self._markdown = MarkdownIt()

    def parse(self, content: str, source: str) -> Document:
        metadata, body = self._split_frontmatter(content)
        tokens = self._markdown.parse(body)

        sections: list[Section] = []
        links: list[DocumentLink] = []
        code_blocks: list[CodeBlock] = []
        current: Section | None = None
        list_depth = 0
        title: str | None = None
        heading_inline_indexes: set[int] = set()

        for index, token in enumerate(tokens):
            if token.type == "heading_open":
                current, title = self._handle_heading(
                    tokens=tokens,
                    index=index,
                    token=token,
                    sections=sections,
                    links=links,
                    heading_inline_indexes=heading_inline_indexes,
                    title=title,
                )
                continue
            if token.type in {"bullet_list_open", "ordered_list_open"}:
                list_depth += 1
                continue
            if token.type in {"bullet_list_close", "ordered_list_close"}:
                list_depth = max(0, list_depth - 1)
                continue
            if token.type == "fence":
                self._handle_fence(token, current, sections, code_blocks)
                continue
            if token.type != "inline" or index in heading_inline_indexes:
                continue
            self._handle_inline(token, current, sections, links, list_depth)

        document_title = str(metadata.get("name") or metadata.get("title") or title or "").strip()
        return Document(
            source=source,
            content=body,
            metadata=metadata,
            title=document_title or None,
            sections=sections,
            links=links,
            code_blocks=code_blocks,
        )

    @staticmethod
    def _split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
        match = FRONTMATTER_RE.match(content)
        if match is None:
            return {}, content

        raw = match.group(1)
        parsed = yaml.safe_load(raw) or {}
        if not isinstance(parsed, dict):
            raise ValueError("Markdown frontmatter must be a YAML mapping.")
        return parsed, content[match.end():]

    def _handle_heading(
        self,
        tokens: list[Token],
        index: int,
        token: Token,
        sections: list[Section],
        links: list[DocumentLink],
        heading_inline_indexes: set[int],
        title: str | None,
    ) -> tuple[Section, str | None]:
        inline = self._next_inline(tokens, index)
        heading = inline.content.strip() if inline is not None else ""
        level = self._heading_level(token)
        current = Section(heading=heading, level=level)
        sections.append(current)
        if level == 1 and title is None:
            title = heading
        if inline is not None:
            heading_inline_indexes.add(index + 1)
            found = self._extract_links(inline.content, inline)
            current.links.extend(found)
            links.extend(found)
        return current, title

    def _handle_fence(
        self,
        token: Token,
        current: Section | None,
        sections: list[Section],
        code_blocks: list[CodeBlock],
    ) -> None:
        block = CodeBlock(language=token.info.strip() or None, content=token.content)
        code_blocks.append(block)
        self._section(current, sections).code_blocks.append(block)

    def _handle_inline(
        self,
        token: Token,
        current: Section | None,
        sections: list[Section],
        links: list[DocumentLink],
        list_depth: int,
    ) -> None:
        text = token.content.strip()
        if not text:
            return
        section = self._section(current, sections)
        found = self._extract_links(text, token)
        links.extend(found)
        section.links.extend(found)
        if list_depth > 0:
            section.items.append(text)
        else:
            section.paragraphs.append(text)

    @staticmethod
    def _next_inline(tokens: list[Token], index: int) -> Token | None:
        if index + 1 >= len(tokens):
            return None
        inline = tokens[index + 1]
        return inline if inline.type == "inline" else None

    @staticmethod
    def _heading_level(token: Token) -> int:
        if token.tag.startswith("h") and token.tag[1:].isdigit():
            return int(token.tag[1:])
        return 1

    @staticmethod
    def _section(current: Section | None, sections: list[Section]) -> Section:
        if current is not None:
            return current
        if sections and sections[0].level == 0:
            return sections[0]
        preamble = Section(heading="", level=0)
        sections.insert(0, preamble)
        return preamble

    @staticmethod
    def _extract_links(text: str, token: Token | None = None) -> list[DocumentLink]:
        links: list[DocumentLink] = []
        for match in WIKI_LINK_RE.finditer(text):
            target = match.group(1).strip()
            links.append(DocumentLink(text=target, target=target, kind="wiki"))

        for match in MARKDOWN_LINK_RE.finditer(text):
            links.append(
                DocumentLink(
                    text=match.group(1).strip(),
                    target=match.group(2).strip(),
                    kind="markdown",
                )
            )

        if token is None or token.children is None:
            return links

        children = token.children
        for index, child in enumerate(children):
            if child.type != "link_open":
                continue
            href = child.attrGet("href") or ""
            label = ""
            if index + 1 < len(children) and children[index + 1].type == "text":
                label = children[index + 1].content
            link = DocumentLink(text=label.strip() or href, target=href, kind="markdown")
            if link not in links:
                links.append(link)

        return links
