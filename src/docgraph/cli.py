"""Command line interface for DocGraph."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from docgraph.config import (
    DocGraphConfig,
    default_config_yaml,
    default_ontology_yaml,
    resolve_path,
)
from docgraph.core.graph import NetworkXGraph
from docgraph.extraction.pipeline import ExtractionPipeline, PipelineResult
from docgraph.extraction.rule import RuleExtractor
from docgraph.parser.markdown import MarkdownParser
from docgraph.storage.json import JSONGraphStore
from docgraph.validation.schema import Ontology
from docgraph.validation.validator import OntologyValidator, ValidationIssue

app = typer.Typer(help="Build knowledge graphs from documentation.")
console = Console()


@dataclass(frozen=True)
class BuildContext:
    result: PipelineResult
    output_path: Path


@app.command()
def init(
    directory: Path = typer.Argument(Path("."), help="Project directory to initialize."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files."),
) -> None:
    """Create a starter DocGraph project."""

    directory.mkdir(parents=True, exist_ok=True)
    docs_dir = directory / "docs"
    docs_dir.mkdir(exist_ok=True)

    files = {
        directory / "docgraph.yaml": default_config_yaml(),
        directory / "ontology.yaml": default_ontology_yaml(),
        docs_dir / "order-service.md": _example_document(),
    }

    for path, content in files.items():
        if path.exists() and not force:
            console.print(f"[yellow]Skipped existing[/yellow] {path}")
            continue
        path.write_text(content, encoding="utf-8")
        console.print(f"[green]Created[/green] {path}")


@app.command()
def build(
    config: Path = typer.Option(
        Path("docgraph.yaml"),
        "--config",
        "-c",
        help="Path to a DocGraph configuration file.",
    ),
) -> None:
    """Build and export a knowledge graph."""

    console.print("Scanning documentation...")
    context = build_project(config, write_output=True)
    result = context.result
    issue_count = len(result.validation_issues)

    console.print(f"[green]OK[/green] {len(result.documents)} documents parsed")
    console.print(f"[green]OK[/green] {len(result.valid.entities)} entities discovered")
    console.print(
        f"[green]OK[/green] {len(result.valid.relationships)} relationships discovered"
    )
    if issue_count:
        console.print(f"[yellow]WARN[/yellow] {issue_count} validation errors")
        _print_issues(result.validation_issues)
    else:
        console.print("[green]OK[/green] 0 validation errors")

    console.print("")
    console.print("Knowledge graph generated.")
    console.print("")
    console.print(f"Nodes: {len(result.graph.entities())}")
    console.print(f"Edges: {len(result.graph.relationships())}")
    console.print("")
    console.print("Output:")
    console.print(str(context.output_path))


@app.command()
def validate(
    config: Path = typer.Option(
        Path("docgraph.yaml"),
        "--config",
        "-c",
        help="Path to a DocGraph configuration file.",
    ),
) -> None:
    """Validate documentation against the ontology."""

    console.print("Validating documentation...")
    result = build_project(config, write_output=False).result
    if result.validation_issues:
        _print_issues(result.validation_issues)
        raise typer.Exit(1)
    console.print("[green]No validation errors found.[/green]")


@app.command()
def stats(
    config: Path = typer.Option(
        Path("docgraph.yaml"),
        "--config",
        "-c",
        help="Path to a DocGraph configuration file.",
    ),
) -> None:
    """Print statistics for the exported graph."""

    config_path = config.resolve()
    docgraph_config = DocGraphConfig.from_yaml(config_path)
    output_path = resolve_path(config_path.parent, docgraph_config.output.path)
    if not output_path.exists():
        raise typer.BadParameter(
            f"Graph output does not exist at {output_path}. Run 'docgraph build' first."
        )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    entities = payload.get("entities", [])
    relationships = payload.get("relationships", [])

    console.print("Knowledge Graph Statistics")
    table = Table()
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Entities", str(len(entities)))
    table.add_row("Relationships", str(len(relationships)))
    console.print(table)

    _print_counter("Entity Types", Counter(entity["type"] for entity in entities))
    _print_counter(
        "Relationships",
        Counter(relationship["relation"] for relationship in relationships),
    )


def build_project(config_path: Path, *, write_output: bool) -> BuildContext:
    config_path = config_path.resolve()
    docgraph_config = DocGraphConfig.from_yaml(config_path)
    base_dir = config_path.parent
    source_path = resolve_path(base_dir, docgraph_config.source.path)
    ontology_path = resolve_path(base_dir, docgraph_config.ontology.path)
    output_path = resolve_path(base_dir, docgraph_config.output.path)

    if docgraph_config.source.format != "markdown":
        raise typer.BadParameter("Only Markdown sources are supported.")
    if docgraph_config.graph.backend != "networkx":
        raise typer.BadParameter("Only the NetworkX graph backend is available.")
    if docgraph_config.output.format != "json":
        raise typer.BadParameter("Only JSON output is available.")

    ontology = Ontology.from_yaml(ontology_path)
    parser = MarkdownParser()
    documents = [
        parser.parse(path.read_text(encoding="utf-8"), _display_source(path, base_dir))
        for path in sorted(source_path.rglob("*.md"))
    ]

    pipeline = ExtractionPipeline(
        extractor=RuleExtractor(),
        validator=OntologyValidator(ontology),
        graph=NetworkXGraph(),
    )
    result = pipeline.run(documents)

    if write_output:
        JSONGraphStore().save(result.graph, output_path)

    return BuildContext(result=result, output_path=output_path)


def _display_source(path: Path, base_dir: Path) -> str:
    try:
        return str(path.relative_to(base_dir))
    except ValueError:
        return str(path)


def _print_issues(issues: list[ValidationIssue]) -> None:
    for issue in issues:
        console.print(f"[red]ERROR[/red] {issue.message}")


def _print_counter(title: str, counter: Counter[str]) -> None:
    if not counter:
        return
    table = Table(title=title)
    table.add_column("Name")
    table.add_column("Count", justify="right")
    for name, count in sorted(counter.items()):
        table.add_row(name, str(count))
    console.print(table)


def _example_document() -> str:
    return """---
type: service
id: order-service
name: Order Service
owner: commerce-platform
---

# Order Service

## Description

Responsible for creating and managing customer orders.

## Depends On

- PostgreSQL
- [[Payment Service]]

## Publishes

- OrderCreatedEvent

## Consumes

- PaymentCompletedEvent

## APIs

- POST /v1/orders
- GET /v1/orders/{orderId}

## Database

- PostgreSQL
"""


if __name__ == "__main__":
    app()
