# Concepts

## Document

A parsed source file. Markdown frontmatter becomes document metadata, and
Markdown structure becomes sections, paragraphs, list items, links, and code
blocks.

## Entity

A graph node with an id, type, name, optional source document, and metadata.

## Relationship

A graph edge with a source id, relation name, target id, optional source
document, confidence, and metadata. Deterministic extraction uses confidence
`1.0`.

## Ontology

A schema defining valid entity types and relationship constraints.

## Extractor

A component that proposes entities and relationships from a parsed document.
The initial `RuleExtractor` handles common Markdown conventions.

## Graph

A storage-neutral graph abstraction. Application code should depend on
`Graph`, not on NetworkX directly.
