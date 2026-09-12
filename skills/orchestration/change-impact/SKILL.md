# Change Impact

Trace a proposed change through the canonical dependency graph before mutation.

## Procedure
1. Record old value, proposed value, object ID and reason.
2. Traverse direct and transitive relations.
3. Classify impacts: geometry, structure, materials, AV, lighting, power, quantities, cost, schedule, logistics, vendor, drawings, renders, approvals.
4. Mark affected artifacts stale rather than overwriting them.
5. Create follow-up tasks only for materially affected disciplines.
6. Require new evidence when a verified value changes.

## Output
impact_set, stale_artifacts, required_tasks, approval_level, risks, unresolved_dependencies.

Inspired by event-sourcing/state-graph and CloudEvents patterns, adapted to TCZ event production.
