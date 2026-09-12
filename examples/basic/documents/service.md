---
type: service
id: order-service
name: Order Service
owner: order-management
---

# Order Service

## Description

Processes incoming order and product events.

```python
print("example")
```

## Depends On

- MongoDB
- SQS
- [[IoT Service]]

## Publishes

- OrderUpdatedEvent
- ProductUpdatedEvent

## Consumes

- OrderUpdatedEvent

## APIs

- POST /v1/orders
- GET /v1/orders/{orderId}

## Database

- MongoDB