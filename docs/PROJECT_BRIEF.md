# TCZ Event OS Project Brief

TCZ Event OS is a multi-agent operating system for event design, production, technical review, visualization, procurement, operations, quality control, and approvals.

The project is built around one rule: agents do not keep separate truths. Every role works from the same typed Canonical Event Model, proposes changes through explicit workflow protocols, and leaves auditable evidence, decisions, approvals, and event history behind.

## What the Brain Does

The brain is the deterministic orchestration layer around specialist reasoning. It owns the lifecycle:

```text
request -> plan -> load skills -> build context -> approve -> execute agents -> judge -> commit
```

It is responsible for legal workflow transitions, approval pause/resume, side-effect gating, failure classification, tracing, and committing only verified state.

The specialist agents can use LLMs, SDKs, MCP tools, CAD tools, Blender, Rhino, or external services, but they do not define the workflow rules. The orchestrator does.

## Agents, Skills, Tools, and State

**Agents** are accountable roles. Examples include Executive Producer, Creative Spatial, Production Engineering, Rigging, Blender Production, and Independent Judge. Agents own decisions and outputs within a bounded authority model.

**Skills** are reusable operating procedures loaded only when required. A skill tells an agent how to perform a class of work, such as change impact, rigging review, Blender modeling, render validation, or independent judging.

**Tools** are executable capabilities. They may read files, create geometry, call Blender/Rhino/CAD, send RFQs, update documents, or use MCP servers. Tools are side-effect gated and must be called through policy-aware runtime paths.

**Canonical State** is the project truth. It contains typed event objects, relationships, decisions, assumptions, evidence, quantities, costs, approvals, and status. Agents receive context packages extracted from canonical state and return structured results rather than mutating state directly.

## Current Goal

The current milestone is to replace placeholder task execution with the first real pluggable agent runtime.

The target vertical slice is the Jotun KANVA entrance change:

- Current approved entrance height: `4200mm`
- Proposed entrance height: `5500mm`
- Flow: impact assessment, spatial update, production review, rigging review, Blender production, independent judging, approval preservation, and final state commit

The implementation must remain provider-neutral. The orchestrator depends on typed runtime contracts, while OpenAI Agents SDK support is an adapter, not a hard dependency in the workflow core.

## Guardrails

- Plan before side effects.
- Pause for L2/L3 approvals before execution.
- Preserve approval packets and decisions across resume.
- Build the smallest sufficient context package per task.
- Load only authorized skills.
- Return structured agent results.
- Run independent judge checks before commit.
- Classify failures instead of hiding them.
- Commit only after all tasks complete and verification passes.
