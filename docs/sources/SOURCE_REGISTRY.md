# Source Registry

Decision vocabulary: **adopt** = belongs in target architecture; **adapt** = selective use; **idea-only** = borrow pattern, not runtime/code; **reference** = supporting reference; **reject** = deliberately excluded; **pending** = deeper audit required.

## Agent engineering and protocols

| Source | Decision | Extracted contribution |
|---|---|---|
| muratcankoylan/Agent-Skills-for-Context-Engineering | adopt | progressive disclosure, context degradation/compression, multi-agent patterns, memory, tool design, evaluation, harness engineering, long-horizon prompting, runtime-neutral artifact contracts |
| NeoLabHQ/context-engineering-kit | adopt | granular context, subagent/spec-driven development, reflection, judge/evaluation, prompt testing, memory extraction |
| temporal-community/ai-agents-workshop-python | adapt | durable multi-agent workflows, MCP, human approval patterns |
| temporal-community/temporal-agent-harness | adapt | durable execution, typed contracts, tool approvals, resumability, standardized lifecycle event streams |
| pydantic/pydantic-ai | adapt | typed graph/state-machine patterns separating state, deps, input and output |
| langchain-ai/langgraph | reference | shared state vs runtime context, reducers, checkpointing and graph execution |
| modelcontextprotocol/modelcontextprotocol | adopt | Resources / Tools / Prompts boundary |
| cloudevents/spec | adapt | vendor-neutral internal event envelope |
| asyncapi/spec | reference | machine-readable channels/messages/payload contracts |
| microsoft/autogen | reference | structured handoff patterns; not selected as runtime |
| aliseylaneh/Python-Eventsourcing-CQRS | reference | reconstructable event history and CQRS concepts |

## Blender, visual production and reference engineering

| Source | Decision | Extracted contribution |
|---|---|---|
| XliuXjianX/blender-production-skills | adapt | deep Blender technical production, native modeling, Geometry Nodes, simulation, materials, validation |
| achimala/dream-loop | adapt | target image -> build -> independent critic -> iterate loop |
| kevinbadi/blender-skills | adapt | image-to-3D, camera moves, Poly Haven, polish, export utilities |
| Humanoid-SkillBlender/SkillBlender | reject | robotics RL project, not Blender DCC |
| ajay-vikram/SkillBlenderLC | idea-only | missing-capability detection and feedback refinement only |
| arjun988/blender-skills | adapt | director routing, reference matching, modeling, archviz, lookdev, lighting, camera, rendering, QA |
| ProfRino/Blender-MCP-Assembly-Skill | adopt | connection maps, bounds/overlap verification, assembly audit |
| ig-shadow-walker/BlenderXAlpha-3DGenSkill | adapt | Alpha3D/Tripo/Meshy provider-router architecture and generated-mesh cleanup |
| Liuziyu77/gene-skill | idea-only | capability extraction, provenance, recombination and validation methodology |
| TMHSDigital/Blender-Developer-Tools | adopt | tested bpy/bmesh patterns, headless validation, Blender-version guardrails |
| p4inz-code/3d-ref-skills | adopt | reference brief, hierarchy, audit, authoritative-vs-mood source separation |
| CheshireJCat/create-3d-model-skill | adapt | scene safety, checkpoints, versioning, image acceptance criteria |
| lovecatisgood-sudo/3d-asset-generation-blender-unity-game-development-skills | idea-only | reversible production slice and evidence gates |
| frabcd/codex-ai-game-studio | idea-only | provenance, rollback, tool metadata and quality governance |
| Limbicnation/hermes-asset-pipeline | adapt | staged asset manifests and pipeline state |
| RobLe3/cc-blender-skill | adopt | skill harmonization, source-of-truth, source-locked reconstruction, multiview QA and repair loops |
| LevyBytes/AI-SKILL-blender | reference | Blender Manual/API-oriented reference routing |
| HabrielStark/brilliant-blender-skill | pending | deeper audit required |
| boernmaster/blender_skill | pending | deeper audit required |
| CurioCrafter/BlenderAstraSkills | pending | deeper audit required |
| thanhdongnguyen/Blender-Skill | pending | user-provided source, deeper audit required |
| Mik1703/blender-mcp-quality | pending | user-provided quality source, deeper audit required |

## CAD, BIM, lighting, venue reconstruction and operations

| Source | Decision | Extracted contribution |
|---|---|---|
| pzfreo/build123d-mcp | adopt | incremental measured parametric CAD, validation, STEP/STL/SVG/DXF export |
| Show2Instruct/bonsai-mcp | adopt | Blender+Bonsai/IFC, quantities, psets, screenshots, guarded code execution |
| open-stage/blender-dmx | adopt | event-lighting visualization using GDTF/MVR ecosystem |
| EaseHee/rhino-mcp | adapt | Rhino/NURBS/Grasshopper, drawings, quantities, panelization, IFC, analysis |
| reer-ide/rhino_mcp | reference | alternative Rhino bridge architecture |
| dongwoosuk/rhino-grasshopper-mcp | reference | Grasshopper MCP and computational design experiments |
| SBCV/Blender-Addon-Photogrammetry-Importer | adopt | COLMAP/GLOMAP/Meshroom/point-cloud import and venue reconstruction |
| stuffmatic/fSpy | adopt | still-image perspective/camera calibration |
| stuffmatic/fSpy-Blender | adopt | Blender import of fSpy calibration |
| CWRU-AISM/COLMAP_workflow | reference | video-frame extraction and COLMAP/GLOMAP reconstruction workflow |
| CadQuery/cadquery-contrib | reference | parametric CAD examples alongside build123d |
| yuxiang-gao/PySocialForce | adapt | early pedestrian/crowd flow simulation |
| IfcTruss/IfcTruss | reference | preliminary truss modeling/analysis, never final professional signoff |
| ManuelMRosa/SheetNest | adapt | DXF/STEP nesting and material utilization |
| RU-Airborne/BalsaNest | adapt | grain, kerf, spacing, scrap reuse and utilization |
| jgmedialtd/smartcut-api | adapt | sheet/profile/irregular DXF cut optimization and stock constraints |

## License policy

This project records ideas, patterns, interfaces and tool references with provenance. It does not wholesale copy upstream code or long documentation. Vendored code requires a current license review and preserved notices.