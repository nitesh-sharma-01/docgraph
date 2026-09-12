from pathlib import Path

from docgraph.parser.markdown import MarkdownParser


def test_markdown_parser_reads_frontmatter_sections_links_and_code_blocks() -> None:
    content = Path("tests/fixtures/service.md").read_text(encoding="utf-8")
    document = MarkdownParser().parse(content, "service.md")

    assert document.metadata["id"] == "order-service"
    assert document.metadata["type"] == "service"
    assert document.title == "Order Service"
    assert document.code_blocks[0].language == "python"
    assert 'print("example")' in document.code_blocks[0].content

    depends_on = next(section for section in document.sections if section.heading == "Depends On")
    assert depends_on.items == ["MongoDB", "SQS", "[[IoT Service]]"]
    assert any(link.kind == "wiki" and link.target == "IoT Service" for link in document.links)
