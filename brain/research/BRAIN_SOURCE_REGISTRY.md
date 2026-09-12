# TCZ Brain Research Source Registry

This registry tracks architecture sources for the orchestration brain. TCZ extracts patterns and interfaces, not wholesale upstream code.

## Core adoption sources

### openai/openai-agents-python
Use for:
- agent runtime patterns
- manager/worker and agents-as-tools
- handoffs
- tool guardrails
- human approval pause/resume
- sessions and tracing
- MCP integration patterns

TCZ rule: SDK primitives implement TCZ contracts. They do not define the Canonical Event Model or TCZ workflow semantics.

### temporal-community/temporal-agent-harness
Use for:
- durable long-running workflows
- retries and recovery
- human wait/resume
- replayable lifecycle events
- tool approval policy patterns
- workflow/activity separation

TCZ rule: Temporal provides durability. It does not decide creative/production workflow policy.

### pydantic/pydantic-ai
Use for:
- typed dependencies/state/results
- graph/state modeling references
- schema validation
- structured agent I/O

TCZ rule: Pydantic is the contract boundary for runtime objects.

## Supporting architecture references

### langchain-ai/langgraph
Use for:
- explicit state schema/context schema separation
- reducers
- checkpointing references
- graph execution concepts

Status: reference, not required runtime dependency.

### modelcontextprotocol/modelcontextprotocol
Use for:
- tools vs resources separation
- tool schemas
- progress/cancellation/logging
- external application integration

Status: protocol layer.

### cloudevents/spec
Use for:
- event envelope conventions
- event id/source/type/subject/time/data

Status: adapt event semantics.

### asyncapi/spec
Use for:
- machine-readable event channels/messages/payloads
- event-driven service contracts

Status: future event API documentation.

### statelyai/agent
Investigate for:
- state-machine-driven agent execution
- legal transition enforcement
- inspectable/replayable workflows

Status: reference candidate, deep audit required before adoption.

### run-llama/workflows-py
Investigate for:
- event-driven async workflow patterns
- resumability and step/event boundaries

Status: reference candidate, deep audit required before adoption.

### tainguyen07/agent-workflow-mcp
Investigate for:
- planner/executor/critic flow
- MCP tool discovery
- bounded retry loops
- execution traces

Status: reference candidate, deep audit required before adoption.

### Quantlix/anycode
Investigate for:
- DAG scheduling
- concurrency
- checkpointing
- cost controls
- verification gates

Status: reference candidate, deep audit required before adoption.

## Context and evaluation sources

### muratcankoylan/Agent-Skills-for-Context-Engineering
Use for:
- progressive disclosure
- smallest sufficient context
- context degradation management
- long-horizon context patterns
- memory/context separation

### NeoLabHQ/context-engineering-kit
Use for:
- subagent-driven work
- reflection
- independent evaluation
- judge/debate patterns
- prompt/agent testing

## Extraction policy
For every source, record:
1. problem solved
2. pattern to adopt
3. pattern to reject
4. TCZ adaptation
5. dependency/licensing implication
6. test that proves the adaptation works

Do not vendor upstream source unless explicitly approved after license review.