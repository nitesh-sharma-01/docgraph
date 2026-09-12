# Contributing to DocGraph

DocGraph is deterministic-first. Contributions should keep the core package
usable without an API key or live model dependency.

## Development Setup

```bash
pip install -e ".[dev]"
pytest
```

## Principles

- Keep modules small and typed.
- Prefer explicit interfaces over provider-specific coupling.
- Validate all extracted data before graph insertion.
- Do not expose NetworkX from extraction, validation, or storage APIs.
- Add focused tests for parser, extraction, validation, graph, storage, and CLI
  behavior.
- Do not add live LLM/API calls to tests.

## Pull Requests

Include a short summary, test coverage notes, and any ontology or output format
changes. Breaking changes should include migration notes.
