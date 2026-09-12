# TCZ Event OS

TCZ Event OS is a framework-agnostic multi-agent operating system for event design, visualization, production, technical systems, operations, vendors, inventory, costing, quality control, and approvals.

It is built around one principle: agents do not own separate truths. They operate on one typed Canonical Event Model, mutate it through explicit protocols, and leave an auditable event history.

## Core architecture

```text
User / TCZ
   |
Executive Producer
   |
Context Builder + Workflow Engine
   |
Specialist Agents
   |
Tools and MCP Servers
   |
Self-check -> Judge -> Approval Gate
   |
Canonical Event Model
   |
Append-only Event History
```

## Foundation specifications

1. `docs/architecture/CANONICAL_EVENT_MODEL.md`
2. `docs/architecture/AGENT_PROTOCOL.md`
3. `docs/architecture/EVENT_CHANGE_PROTOCOL.md`
4. `docs/architecture/AUTHORITY_APPROVAL_MODEL.md`
5. `docs/architecture/EVIDENCE_PROVENANCE_MODEL.md`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python examples/jotun_kanva/run_vertical_slice.py
```

The Jotun vertical slice demonstrates controlled change, impact detection, QA, approval policy, and append-only event history.

See `docs/AGENT_CATALOG.md`, `docs/sources/SOURCE_REGISTRY.md`, and `docs/ROADMAP.md` for the full system map.