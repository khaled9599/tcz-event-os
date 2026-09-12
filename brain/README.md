# TCZ Event OS Brain

The brain is the orchestration layer that turns a human objective into governed, traceable, resumable work across specialist agents and tools.

It is not one giant agent.

## Components

- Executive Producer: interprets objectives and owns decomposition
- Planner: builds the task graph and dependency order
- Router: selects the agent allowed to perform each task
- Context Builder: assembles the minimum authoritative context package
- Skill Loader: resolves only the skills required for the task
- Workflow Engine: enforces legal process transitions and approval gates
- Permission Engine: enforces agent/tool/state authority
- Event Bus: emits domain events and wakes dependent workflows
- Run Coordinator: owns run lifecycle, checkpoints, retry/recovery, and resume
- Judge Layer: independently evaluates outputs against acceptance criteria
- Canonical State: authoritative project truth
- Event Store: append-only history of what happened and why

## Runtime rule

No model may directly mutate canonical state or trigger an external side effect merely because it reasoned that doing so is useful.

All work follows:

`DISCOVER -> PLAN -> VALIDATE -> APPROVE -> EXECUTE -> VERIFY -> COMMIT`

## Framework boundary

TCZ owns the contracts and process semantics. Frameworks can be replaced.

Current implementation direction:
- OpenAI Agents SDK for agent execution and tool/handoff primitives
- Temporal for durable orchestration and human wait/resume
- Pydantic for typed contracts
- MCP for external tool/resource integration
- PostgreSQL for canonical operational state
- append-only event history for auditability

See `docs/architecture/TCZ_BRAIN_GAP_AUDIT.md` for the current implementation gaps and V1 acceptance test.