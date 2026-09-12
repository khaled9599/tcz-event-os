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
Task-specific Skills
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

For a concise system overview, see `docs/PROJECT_BRIEF.md`. For researched upstream references and adoption decisions, see `docs/resources/RESOURCE_CATALOG.md`.

## Skills layer

Agents are roles with ownership and authority. Skills are reusable operating procedures loaded only when needed.

- `configs/skills_registry.yaml` defines every skill, source provenance, path, and intended agents.
- `configs/agent_skill_matrix.yaml` maps agents to required and optional skills.
- `skills/` contains the actual task procedures.
- `knowledge_packs` in agent charters remain background reference and are not a substitute for operational skills.

Phase 1 agents now reference their skills directly in their charters. Specialist Phase 2 skills are also registered so runtime work can activate them without redesigning the architecture.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python examples/jotun_kanva/run_vertical_slice.py
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --auto-approve-demo
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --approval-file work/jotun_approvals.json
python -m brain.runtime.cli --resume work/jotun_approvals.json
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --runtime openai-impact --approval-file work/jotun_openai_approvals.json
python -m brain.runtime.cli --resume work/jotun_openai_approvals.json --output full --output-file work/jotun_openai_full_result.json
```

The Jotun vertical slice demonstrates controlled change, impact detection, QA, approval policy, and append-only event history.

See `docs/PROJECT_BRIEF.md`, `docs/resources/RESOURCE_CATALOG.md`, `docs/AGENT_CATALOG.md`, `configs/skills_registry.yaml`, `configs/agent_skill_matrix.yaml`, `docs/sources/SOURCE_REGISTRY.md`, and `docs/ROADMAP.md` for the full system map.
