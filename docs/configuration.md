# Configuration

DocGraph uses `docgraph.yaml`.

```yaml
source:
  path: ./docs
  format: markdown

ontology:
  path: ./ontology.yaml

extraction:
  strategy: deterministic

graph:
  backend: networkx

output:
  format: json
  path: ./output/graph.json
```

Hybrid extraction can be configured for future model-assisted workflows:

```yaml
extraction:
  strategy: hybrid

model:
  provider: openai
  name: gpt-5-mini
```

Model configuration is not required for deterministic extraction.
