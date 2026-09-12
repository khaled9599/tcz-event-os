# TCZ Event OS Brain Gap Audit v1

## Purpose
Audit the current repository against the minimum architecture required for a real, resumable, governed end-to-end Event OS workflow.

## Existing strengths
- Canonical Event Model and typed domain objects
- Agent charters and explicit authority boundaries
- Skill registry and agent-skill matrix
- Change impact rules and Jotun vertical slice
- Evidence/provenance model
- Human approval levels L0-L3
- Independent judge concept
- MCP/tool direction and source registry

## Critical gaps blocking a real brain runtime

### 1. Orchestrator runtime
Missing a single runtime service that receives a user objective, creates a task graph, routes work, pauses for approvals, resumes, and closes the run.

Required modules:
- orchestrator
- planner
- router
- run coordinator
- task graph

### 2. Dynamic skill loading
The repo now maps agents to skills, but the runtime does not yet resolve the minimum skill set for each task and inject only those procedures.

Required:
- skill loader
- skill dependency resolution
- skill version pinning
- skill activation trace

### 3. Deterministic workflow/state machine
Agent reasoning must not control critical process transitions. Legal transitions need to be enforced in code.

Required:
- workflow states
- transition guards
- gate requirements
- cancellation/resume rules
- idempotency rules

### 4. Plan-before-side-effects boundary
Planning, impact analysis, approvals, and tool execution must be separated.

Required phases:
DISCOVER -> PLAN -> VALIDATE -> APPROVE -> EXECUTE -> VERIFY -> COMMIT

No external side effect should occur before required gates pass.

### 5. Durable/resumable run state
Long-running event workflows must survive process restarts, approval waits, tool failures, and partial completion.

Required:
- run snapshot
- checkpoint references
- retry policy
- resume token/run id
- completed-call ledger to prevent duplicate side effects

### 6. Event bus and domain events
The Event OS needs first-class events to wake dependent capabilities and preserve causality.

Examples:
- change.proposed
- approval.required
- approval.granted
- task.completed
- render.completed
- vendor.quote.received
- object.verification.invalidated

### 7. Conflict and decision resolution
Multiple specialists may disagree. The system needs a deterministic conflict packet, not free-form agent debate.

Required:
- conflicting claims
- evidence refs
- cost/schedule/risk impacts
- authority level
- recommended decision owner

### 8. Run-level observability
Current tracing concepts are not yet formalized into a common run record.

Required:
- run id
- parent/child task ids
- agent and model used
- loaded skills
- context package id
- tool calls
- token/cost metrics
- approvals
- judge results
- latency/errors/retries

### 9. Failure taxonomy and recovery
Retries should differ by failure type.

Required classes:
- transient tool failure
- invalid output/schema
- missing context
- permission violation
- failed quality gate
- conflicting state
- external dependency unavailable
- human rejection

### 10. Idempotency and side-effect ledger
Any operation that can cost money or mutate an external system must be deduplicated.

Examples:
- vendor RFQ sent once
- Blender destructive mutation not replayed accidentally
- purchase request not duplicated
- client email not sent twice

### 11. Budget and resource policy for agents
The brain needs limits for expensive reasoning and tools.

Required:
- max agent turns
- max revision loops
- tool budgets
- model routing policy
- escalation instead of endless retries

### 12. Security and permission enforcement
Charters define authority, but runtime enforcement is required.

Required:
- read/write scopes
- tool permissions
- side-effect classes
- protected canonical fields
- L3 professional-only actions

### 13. Human approval inbox contract
Approval objects need a standard UI/runtime shape so a human can understand exactly what is being approved.

Required fields:
- requested action
- before/after
- evidence
- impacts
- risks
- cost/schedule delta
- recommendation
- approve/reject/request revision

### 14. Retrieval hierarchy
Context Builder needs an explicit authority order.

Recommended hierarchy:
1. verified canonical state
2. approved decisions
3. verified evidence/source files
4. current project artifacts
5. TCZ knowledge base
6. external references
7. assumptions

### 15. Automated repository validation
CI must verify:
- every agent skill reference exists
- every skill has metadata and procedure
- every active agent has at least one allowed skill
- approval levels are valid
- workflow transitions are valid
- schemas load
- Jotun vertical slice passes

## Architecture decision
TCZ owns the orchestration contract. External frameworks are implementation layers, not the architecture itself.

Recommended stack:
- OpenAI Agents SDK: agent execution, tools, handoffs, guardrails, sessions/tracing
- Temporal: durable workflow execution, wait/resume, retries, long-running jobs
- Pydantic: typed contracts/state/result validation
- MCP: tool/resource protocol
- PostgreSQL: canonical project/task/run state
- Object storage: media, Blender/CAD/BIM, renders, documents
- append-only event store: causality and audit history

## V1 acceptance test
Input: `Increase KANVA_ENTRANCE_01 height from 4200 mm to 5500 mm.`

The system must:
1. create one run id
2. read verified canonical state
3. create a change proposal without mutating the entrance
4. calculate impacted domains
5. create a task graph
6. load only required skills per agent
7. gather minimal authoritative context
8. run spatial and production reviews
9. identify L3 structural verification requirement
10. pause at the correct approval gate
11. resume without repeating completed side effects
12. execute approved geometry changes
13. run independent QA
14. write the new version and invalidate superseded evidence where required
15. preserve before/after state and full event history
16. report final outcome, unresolved risks, and affected downstream deliverables

Until this test passes, adding more specialist agents is secondary.