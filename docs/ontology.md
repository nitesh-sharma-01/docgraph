# Ontology

The ontology defines the valid vocabulary for a DocGraph project.

```yaml
entities:
  service:
    description: Software service or microservice
  database:
    description: Persistent data store
  event:
    description: Domain or integration event
  api:
    description: API endpoint
  queue:
    description: Queue, topic, or message broker
  owner:
    description: Team or person that owns an entity

relationships:
  DEPENDS_ON:
    source: service
    target:
      - service
      - database
      - queue
  PUBLISHES:
    source: service
    target: event
  CONSUMES:
    source: service
    target: event
  STORES_IN:
    source: service
    target: database
  EXPOSES_API:
    source: service
    target: api
  OWNED_BY:
    source: service
    target: owner
```

During validation DocGraph checks:

- Every entity type exists in the ontology.
- Every relationship type exists in the ontology.
- Relationship source and target ids reference known entities.
- Source and target entity types match the relationship rule.

Invalid relationships are reported and excluded from graph output.
