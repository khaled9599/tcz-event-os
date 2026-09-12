# TCZ Event OS Agent Catalog

Agent charters are phased. Presence in the catalog does not mean autonomous activation.

## Phase 1 core

| Agent | Department | Primary ownership |
|---|---|---|
| Executive Producer | orchestration | project routing, tasks, dependencies, changes |
| Context Builder | orchestration | minimum authoritative task context |
| Supervisor | quality | process compliance, loops, evidence gaps |
| Independent Judge | quality | independent acceptance-criteria review |
| Creative Spatial Designer | creative/design | zones, experiences, installations |
| Blender Production | visualization | Blender scene, geometry and evidence renders |
| Production Engineering | production | buildability, assembly, materials, transport |
| Change Impact | orchestration | dependency and stale-artifact impact tracing |

## Phase 2 specialists

Reference & Venue Intelligence; Creative Director; Experience Designer; Computational Designer; Design Systems; Brand Guardian; Lookdev & Materials; Lighting Design; Cinematography & Render; Visual Critic; Technical QA; CAD & Fabrication; Production Planner; Site Logistics; BIM & Quantity; Cost Controller; Procurement; AV Systems; Rigging; Electrical & Power; Show Control; Hospitality; Accessibility; Warehouse & Inventory; Vendor Management; Risk Manager.

## Phase 3 optimization and learning

Variant Generator; Fabrication Optimization; Value Engineering; Compliance & Permits; Guest Operations & Crowd; Presentation Director; Knowledge Librarian; Content & Screens.

## Charter contract

Every implemented agent must define: `id`, `name`, `department`, `mission`, `owns`, `can_read`, `can_propose`, `can_mutate`, `can_approve`, `prohibited_actions`, `tools`, `knowledge_packs`, `default_approval_level`, `escalation_rules`, `evaluation_rubric`, `activation_phase`, `runtime_status`.

## Safety boundaries

Rigging, electrical, structural and life-safety agents may plan, calculate, compare and flag issues but cannot replace required qualified-professional approval. Producing agents cannot self-approve critical work.