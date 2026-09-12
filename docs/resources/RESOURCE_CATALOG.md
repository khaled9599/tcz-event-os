# TCZ Event OS Resource Catalog

This catalog consolidates the researched sources currently shaping TCZ Event OS. TCZ extracts patterns, interfaces, and operating ideas from these resources. It does not vendor upstream code unless a separate license review approves it.

Adoption status vocabulary: **adopt** = core pattern or protocol; **adapt** = selective use; **reference** = useful comparison; **idea-only** = conceptual inspiration; **pending** = needs deeper audit; **reject** = not applicable.

## Brain, Orchestration, Context, State, and Protocol

| Resource | Status | TCZ extracts |
|---|---:|---|
| `openai/openai-agents-python` | adapt | Provider adapter pattern, agents as tools, handoffs, guardrails, tracing, human approval boundaries, MCP integration. |
| `temporal-community/temporal-agent-harness` | adapt | Durable run lifecycle, replayable workflow/activity split, retries, recovery, approval wait/resume, lifecycle event streams. |
| `temporal-community/ai-agents-workshop-python` | adapt | Human-in-the-loop multi-agent workflow examples, MCP wiring, durable execution examples. |
| `pydantic/pydantic-ai` | adapt | Typed runtime contracts, structured result validation, dependency/state separation, graph/state-machine references. |
| `langchain-ai/langgraph` | reference | Explicit state schema vs runtime context, reducers, graph execution, checkpointing. |
| `modelcontextprotocol/modelcontextprotocol` | adopt | Tools/resources/prompts boundary, schemas, progress, cancellation, logging, external app integration. |
| `cloudevents/spec` | adapt | Vendor-neutral event envelope shape for future event history. |
| `asyncapi/spec` | reference | Machine-readable event channel and payload documentation. |
| `muratcankoylan/Agent-Skills-for-Context-Engineering` | adopt | Progressive disclosure, context degradation management, context vs memory separation, tool design, evaluation patterns. |
| `NeoLabHQ/context-engineering-kit` | adopt | Granular context building, subagent/spec-driven development, reflection, independent judging, prompt testing. |
| `microsoft/autogen` | reference | Handoff and multi-agent coordination patterns; not selected as the core runtime. |
| `aliseylaneh/Python-Eventsourcing-CQRS` | reference | Reconstructable event history and CQRS concepts. |
| `statelyai/agent` | pending | State-machine driven agent execution and inspectable workflow concepts. |
| `run-llama/workflows-py` | pending | Event-driven async workflow and resumable step boundaries. |
| `tainguyen07/agent-workflow-mcp` | pending | Planner/executor/critic flow, MCP discovery, retry loops, execution traces. |
| `Quantlix/anycode` | pending | DAG scheduling, concurrency, checkpointing, cost controls, verification gates. |

## Blender and 3D Production

| Resource | Status | TCZ extracts |
|---|---:|---|
| `XliuXjianX/blender-production-skills` | adapt | Blender technical production, Geometry Nodes, simulation, materials, validation. |
| `achimala/dream-loop` | adapt | Target image -> build -> independent critic -> iterate production loop. |
| `kevinbadi/blender-skills` | adapt | Image-to-3D, camera moves, Poly Haven use, polish, export utilities. |
| `arjun988/blender-skills` | adapt | Director routing, reference matching, modeling, archviz, lookdev, lighting, camera, rendering, QA. |
| `ProfRino/Blender-MCP-Assembly-Skill` | adopt | Connection maps, bounds checks, overlap verification, assembly audit. |
| `ig-shadow-walker/BlenderXAlpha-3DGenSkill` | adapt | Generated-mesh provider router, Alpha3D/Tripo/Meshy-style cleanup flow. |
| `TMHSDigital/Blender-Developer-Tools` | adopt | Tested `bpy`/`bmesh` patterns, headless validation, Blender version guardrails. |
| `p4inz-code/3d-ref-skills` | adopt | Reference brief, hierarchy, authoritative vs mood source separation, audit trail. |
| `CheshireJCat/create-3d-model-skill` | adapt | Scene safety, checkpoints, versioning, image acceptance criteria. |
| `Limbicnation/hermes-asset-pipeline` | adapt | Staged asset manifests and asset pipeline state. |
| `RobLe3/cc-blender-skill` | adopt | Source-locked reconstruction, multiview QA, repair loops, skill harmonization. |
| `LevyBytes/AI-SKILL-blender` | reference | Blender Manual/API-oriented routing. |
| `HabrielStark/brilliant-blender-skill` | pending | Deeper audit required. |
| `boernmaster/blender_skill` | pending | Deeper audit required. |
| `CurioCrafter/BlenderAstraSkills` | pending | Deeper audit required. |
| `thanhdongnguyen/Blender-Skill` | pending | User-provided source; deeper audit required. |
| `Mik1703/blender-mcp-quality` | pending | User-provided quality source; deeper audit required. |
| `Humanoid-SkillBlender/SkillBlender` | reject | Robotics RL project, not Blender DCC production. |
| `ajay-vikram/SkillBlenderLC` | idea-only | Missing-capability detection and feedback refinement only. |
| `Liuziyu77/gene-skill` | idea-only | Capability extraction, provenance, recombination, validation methodology. |
| `lovecatisgood-sudo/3d-asset-generation-blender-unity-game-development-skills` | idea-only | Reversible production slices and evidence gates. |
| `frabcd/codex-ai-game-studio` | idea-only | Provenance, rollback, tool metadata, quality governance. |

## CAD, BIM, Reconstruction, Lighting, and Fabrication

| Resource | Status | TCZ extracts |
|---|---:|---|
| `pzfreo/build123d-mcp` | adopt | Incremental measured parametric CAD, validation, STEP/STL/SVG/DXF export. |
| `Show2Instruct/bonsai-mcp` | adopt | Blender+Bonsai/IFC, quantities, property sets, screenshots, guarded code execution. |
| `open-stage/blender-dmx` | adopt | Event-lighting visualization through GDTF/MVR ecosystem. |
| `EaseHee/rhino-mcp` | adapt | Rhino/NURBS/Grasshopper, drawings, quantities, panelization, IFC, analysis. |
| `reer-ide/rhino_mcp` | reference | Alternative Rhino bridge architecture. |
| `dongwoosuk/rhino-grasshopper-mcp` | reference | Grasshopper MCP and computational design experiments. |
| `SBCV/Blender-Addon-Photogrammetry-Importer` | adopt | COLMAP/GLOMAP/Meshroom/point-cloud import and venue reconstruction. |
| `stuffmatic/fSpy` | adopt | Still-image perspective and camera calibration. |
| `stuffmatic/fSpy-Blender` | adopt | Blender import of fSpy calibration. |
| `CWRU-AISM/COLMAP_workflow` | reference | Video-frame extraction and COLMAP/GLOMAP reconstruction workflow. |
| `CadQuery/cadquery-contrib` | reference | Parametric CAD examples alongside build123d. |
| `yuxiang-gao/PySocialForce` | adapt | Early pedestrian and crowd-flow simulation. |
| `IfcTruss/IfcTruss` | reference | Preliminary truss modeling and analysis; never final professional signoff. |
| `ManuelMRosa/SheetNest` | adapt | DXF/STEP nesting and material utilization. |
| `RU-Airborne/BalsaNest` | adapt | Grain, kerf, spacing, scrap reuse, utilization. |
| `jgmedialtd/smartcut-api` | adapt | Sheet/profile/irregular DXF optimization and stock constraints. |

## Foundational Specs and TCZ Architecture Docs

| Resource | Status | TCZ extracts |
|---|---:|---|
| `docs/architecture/CANONICAL_EVENT_MODEL.md` | adopt | Single source of truth for typed project state. |
| `docs/architecture/AGENT_PROTOCOL.md` | adopt | Agent authority, inputs, outputs, and escalation semantics. |
| `docs/architecture/EVENT_CHANGE_PROTOCOL.md` | adopt | Controlled state mutation and append-only event history. |
| `docs/architecture/AUTHORITY_APPROVAL_MODEL.md` | adopt | L0-L3 authority, human approval, and safety-critical gates. |
| `docs/architecture/EVIDENCE_PROVENANCE_MODEL.md` | adopt | Evidence, verification, confidence, assumptions, and traceability. |
| `docs/architecture/RUNTIME_ARCHITECTURE.md` | adopt | Runtime shell, task graph, permissions, state transitions, tracing. |
| `docs/architecture/TCZ_BRAIN_GAP_AUDIT.md` | adopt | Gap model for orchestration, approvals, conflicts, failures, and runtime limits. |
| `brain/contracts/runtime_contracts.py` | adopt | Current executable runtime contract boundary. |
| `configs/skills_registry.yaml` | adopt | Registered skill IDs, paths, sources, and provenance. |
| `configs/agent_skill_matrix.yaml` | adopt | Authorized skills per agent. |

## Current Adoption Rule

TCZ should first adopt interfaces and tests, then adapters. External runtimes may execute specialist work, but the TCZ brain remains responsible for context, authority, approval, deterministic phase transitions, failure classification, judging, and canonical state commits.
