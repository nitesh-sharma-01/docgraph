---
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
