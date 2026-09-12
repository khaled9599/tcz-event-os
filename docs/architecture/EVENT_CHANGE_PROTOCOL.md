# Event and Change Protocol

Changes are objects, not chat messages.

1. Create `ChangeRequest` with old/proposed value, reason and requester.
2. Infer impact domains from field and dependency graph.
3. Create specialist review tasks.
4. Collect technical, production, cost, schedule, brand and visual impacts as required.
5. Apply authority policy.
6. On approval, mutate canonical state.
7. Record a `Decision` where appropriate.
8. Emit domain events and mark derivative artifacts stale.

TCZ uses a CloudEvents-inspired internal envelope: `id`, `type`, `source`, `subject`, `time`, `correlation_id`, `causation_id`, `actor`, `data`.

Example event types: `installation.dimension.changed`, `av.specification.changed`, `rigging.review.required`, `electrical.load.changed`, `vendor.quote.received`, `budget.forecast.changed`, `artifact.superseded`, `client.approval.received`.

Transport is intentionally separate. Future implementations may use Temporal signals, database outbox, NATS, Kafka or webhooks and document messages with AsyncAPI.