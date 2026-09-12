# Task Decomposition

## Purpose
Convert a user or client request into bounded executable tasks without allowing specialists to silently redefine scope.

## Inputs
- objective
- affected canonical object IDs
- current approved state
- constraints
- deadlines
- authority level

## Procedure
1. Resolve the request to canonical objects. Never create a duplicate object when an existing ID matches.
2. Separate requested outcome from implementation assumptions.
3. Identify affected disciplines from the dependency graph.
4. Create the minimum independent tasks needed to reach the outcome.
5. Give every task an owner, expected output, acceptance criteria, dependencies, evidence requirement, and approval level.
6. Mark unknowns explicitly. Do not convert unknowns into facts.
7. Route safety-critical or regulated decisions to L3 qualified-professional review.
8. Submit tasks to Context Builder before specialist execution.

## Output contract
Return `TaskSpec[]` with task_id, object_id, objective, inputs, constraints, expected_outputs, dependencies, evidence_required, approval_level, assigned_agent.

## Failure conditions
- duplicate work on the same canonical object
- missing owner or acceptance criteria
- hidden budget/scope change
- safety decision routed to an unauthorized agent

## Source synthesis
Adapted from context-engineering and spec-driven-development patterns reviewed from Muratcan Koylan and NeoLabHQ. This file is TCZ-original synthesis, not copied upstream text.
