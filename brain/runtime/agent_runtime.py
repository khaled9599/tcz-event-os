from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field

from brain.contracts.runtime_contracts import FailureClass, TaskNode


class ContextPackage(BaseModel):
    context_id: str
    task_id: str
    objective: str
    object_id: str | None = None
    authoritative_state: dict[str, Any] = Field(default_factory=dict)
    prior_outputs: dict[str, dict[str, Any]] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    excluded_context_notes: list[str] = Field(default_factory=list)


class AgentExecutionRequest(BaseModel):
    run_id: str
    task: TaskNode
    context: ContextPackage
    skills: list[dict[str, Any]] = Field(default_factory=list)


class AgentResult(BaseModel):
    task_id: str
    agent_id: str | None = None
    status: str = "submitted"
    summary: str
    outputs: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    requires_human_decision: bool = False
    failure_class: FailureClass | None = None
    failure_detail: str | None = None

    @property
    def accepted(self) -> bool:
        return self.status in {"submitted", "passed"} and self.failure_class is None


class AgentRuntime(Protocol):
    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        """Execute one task and return a structured result."""


class DeterministicAgentRuntime:
    """Local runtime used for tests and offline vertical slices.

    It exercises the same orchestration contract as an LLM-backed adapter while
    keeping CI deterministic and side-effect free.
    """

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        task = request.task
        return AgentResult(
            task_id=task.task_id,
            agent_id=task.assigned_agent,
            summary=f"{task.assigned_agent or 'agent'} completed: {task.objective}",
            outputs={
                "objective": task.objective,
                "object_id": task.object_id,
                "skills": [skill["skill_id"] for skill in request.skills],
                "acceptance_criteria": list(task.acceptance_criteria),
                "context_id": request.context.context_id,
            },
            evidence_refs=[request.context.context_id],
            assumptions=["Runtime is deterministic; external tools are not invoked."],
            risks=[],
            requires_human_decision=False,
        )


class DeterministicImpactRuntime:
    """Offline impact analyzer for the first planning phase."""

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        task = request.task
        state = request.context.authoritative_state
        before = state.get("before", {})
        proposed = state.get("proposed", {})
        impacts = list(state.get("impacts", []))
        risks = list(state.get("risks", []))
        before_height = before.get("height_mm")
        proposed_height = proposed.get("height_mm")
        height_delta = proposed_height - before_height if before_height is not None and proposed_height is not None else None

        outputs = {
            "affected_domains": impacts,
            "required_agents": [
                "creative_spatial",
                "production_engineering",
                "rigging",
                "blender_production",
                "independent_judge",
            ],
            "approval_levels": [
                {
                    "task_id": "T-PRODUCTION",
                    "level": "L2",
                    "reason": "Buildability, quantities, cost, schedule, and material state may change.",
                },
                {
                    "task_id": "T-RIGGING",
                    "level": "L3",
                    "reason": "Height change can affect safety-critical temporary-structure assumptions.",
                },
            ],
            "risks": risks,
            "assumptions": [
                f"Baseline height is {before_height}mm and marked {before.get('verification', 'unknown')}.",
                f"Proposed height is {proposed_height}mm and marked {proposed.get('verification', 'unknown')}.",
                "No external tools are invoked in deterministic impact analysis.",
            ],
            "recommended_next_tasks": [
                "Revise entrance geometry and preserve approved clear opening.",
                "Review buildability and update material takeoff.",
                "Review temporary-structure rigging implications.",
                "Update Blender representation and validate render geometry.",
                "Run independent judge on the revised package.",
            ],
            "height_delta_mm": height_delta,
            "context_id": request.context.context_id,
        }
        return AgentResult(
            task_id=task.task_id,
            agent_id=task.assigned_agent,
            summary=f"Impact analysis identified {len(impacts)} affected domains for {task.object_id}.",
            outputs=outputs,
            evidence_refs=[request.context.context_id],
            assumptions=outputs["assumptions"],
            risks=risks,
            requires_human_decision=False,
        )


class DeterministicSpatialRuntime:
    """Offline spatial analyzer for the first geometry-response phase."""

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        task = request.task
        state = request.context.authoritative_state
        before = state.get("before", {})
        proposed = state.get("proposed", {})
        before_height = before.get("height_mm")
        proposed_height = proposed.get("height_mm")
        impact_output = request.context.prior_outputs.get("T-IMPACT", {}).get("outputs", {})
        height_delta = impact_output.get("height_delta_mm")

        outputs = {
            "geometry_change_summary": f"Increase {task.object_id} height from {before_height}mm to {proposed_height}mm.",
            "height_mm": proposed_height,
            "height_delta_mm": height_delta,
            "preserved_constraints": [
                "canonical object ID remains KANVA_ENTRANCE_01",
                "approved clear opening must be retained",
                "design intent remains The Living KANVAS transition moment",
            ],
            "design_intent_assumptions": [
                "The added height increases entrance presence without changing the approved concept.",
                "Width and clear opening are unchanged unless a later specialist flags conflict.",
            ],
            "downstream_production_notes": [
                "Production must verify buildability, quantities, and material takeoff.",
                "Rigging must review temporary-structure and safety-critical implications.",
                "Blender representation and render validation become stale until updated.",
            ],
            "input_impact_domains": impact_output.get("affected_domains", []),
            "context_id": request.context.context_id,
        }
        return AgentResult(
            task_id=task.task_id,
            agent_id=task.assigned_agent,
            summary=f"Spatial response keeps {task.object_id} at {proposed_height}mm with clear-opening constraints preserved.",
            outputs=outputs,
            evidence_refs=[request.context.context_id],
            assumptions=outputs["design_intent_assumptions"],
            risks=[
                "Spatial proposal remains unverified until production and rigging reviews complete."
            ],
            requires_human_decision=False,
        )


class DeterministicProductionRuntime:
    """Offline production engineering review for buildability and takeoff impacts."""

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        task = request.task
        proposed = request.context.authoritative_state.get("proposed", {})
        impact_output = request.context.prior_outputs.get("T-IMPACT", {}).get("outputs", {})
        spatial_output = request.context.prior_outputs.get("T-SPATIAL", {}).get("outputs", {})
        height_mm = spatial_output.get("height_mm", proposed.get("height_mm"))
        height_delta_mm = spatial_output.get("height_delta_mm", impact_output.get("height_delta_mm"))

        outputs = {
            "buildability_review": {
                "status": "requires_detailing",
                "summary": "Entrance height increase is buildable in concept but requires production detailing before release.",
                "checks": [
                    "confirm panel/module proportions after 5500mm height change",
                    "verify base/foundation interface is unchanged or explicitly revised",
                    "separate temporary-structure engineering signoff from production approval",
                ],
            },
            "material_takeoff_impact": {
                "height_mm": height_mm,
                "height_delta_mm": height_delta_mm,
                "quantity_status": "stale_until_remeasured",
                "affected_items": [
                    "entrance cladding or scenic skin",
                    "primary frame members",
                    "secondary support/bracing",
                    "finish area and paint/coating quantities",
                ],
            },
            "cost_schedule_flags": [
                "material quantities require recalculation",
                "fabrication drawings must be revised",
                "installation method statement may need revision",
                "schedule allowance should be reviewed after rigging signoff",
            ],
            "approval_gate": {
                "level": "L2",
                "reason": "Production state, quantities, cost, and schedule may change.",
            },
            "structural_signoff_boundary": "Production review does not replace qualified rigging or structural signoff.",
            "context_id": request.context.context_id,
        }
        return AgentResult(
            task_id=task.task_id,
            agent_id=task.assigned_agent,
            summary="Production review flags stale quantities, buildability detailing, and separate structural signoff.",
            outputs=outputs,
            evidence_refs=[request.context.context_id],
            assumptions=[
                "No fabrication documents are mutated by this deterministic review.",
                "Final quantities require updated geometry or CAD/Blender measurement.",
            ],
            risks=[
                "Quantity, cost, and schedule artifacts remain stale until production updates are completed.",
                "Structural implications must be reviewed by the rigging/qualified engineering path.",
            ],
            requires_human_decision=False,
        )


class DeterministicRiggingRuntime:
    """Offline rigging review for safety-critical temporary-structure implications."""

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        task = request.task
        impact_output = request.context.prior_outputs.get("T-IMPACT", {}).get("outputs", {})
        production_output = request.context.prior_outputs.get("T-PRODUCTION", {}).get("outputs", {})
        height_delta_mm = impact_output.get("height_delta_mm")

        outputs = {
            "rigging_review": {
                "status": "qualified_signoff_required",
                "summary": "Height increase may affect stability, bracing, ballast, wind response, and installation method.",
                "temporary_structure_assumptions": [
                    "Existing support scheme is not considered verified for 5500mm height.",
                    "Loads and restraint assumptions must be recalculated by qualified engineering.",
                    "Production buildability approval does not authorize safety-critical rigging release.",
                ],
            },
            "safety_critical_flags": [
                "temporary-structure engineering review required",
                "wind/load assumptions require verification",
                "anchoring/ballast strategy must be checked",
                "installation and dismantle method statement may need revision",
            ],
            "blocked_until": [
                "qualified rigging or structural signoff is recorded",
                "updated drawings/calculations support the 5500mm height",
                "site constraints and base interface are verified",
            ],
            "approval_gate": {
                "level": "L3",
                "reason": "Safety-critical temporary-structure assumptions may change.",
            },
            "height_delta_mm": height_delta_mm,
            "production_dependency": production_output.get("buildability_review", {}),
            "context_id": request.context.context_id,
        }
        return AgentResult(
            task_id=task.task_id,
            agent_id=task.assigned_agent,
            summary="Rigging review requires qualified L3 signoff before safety-critical release.",
            outputs=outputs,
            evidence_refs=[request.context.context_id],
            assumptions=outputs["rigging_review"]["temporary_structure_assumptions"],
            risks=[
                "Unverified height increase could invalidate temporary-structure stability assumptions.",
                "Rigging approval must come from the qualified review path before release.",
            ],
            requires_human_decision=False,
        )


class DeterministicBlenderRuntime:
    """Offline Blender production package for model/update validation planning."""

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        task = request.task
        state = request.context.authoritative_state
        proposed = state.get("proposed", {})
        spatial_output = request.context.prior_outputs.get("T-SPATIAL", {}).get("outputs", {})
        production_output = request.context.prior_outputs.get("T-PRODUCTION", {}).get("outputs", {})
        rigging_output = request.context.prior_outputs.get("T-RIGGING", {}).get("outputs", {})
        height_mm = spatial_output.get("height_mm", proposed.get("height_mm"))
        object_id = task.object_id or proposed.get("object_id")

        outputs = {
            "blender_package": {
                "status": "ready_for_blender_adapter",
                "object_id": object_id,
                "target_height_mm": height_mm,
                "source_height_delta_mm": spatial_output.get("height_delta_mm"),
                "scene_actions": [
                    "locate canonical entrance object KANVA_ENTRANCE_01",
                    "scale or rebuild vertical entrance geometry to 5500mm",
                    "preserve approved clear opening and design intent markers",
                    "mark prior renders and measurements stale until regenerated",
                ],
            },
            "validation_plan": [
                "measure final model height equals 5500mm",
                "confirm canonical object ID remains KANVA_ENTRANCE_01",
                "confirm visual clear opening is retained",
                "capture render-validation evidence for judge review",
            ],
            "evidence_package": {
                "context_id": request.context.context_id,
                "requires_real_blender_run": True,
                "expected_artifacts": [
                    "updated .blend scene",
                    "dimension validation report",
                    "front elevation render",
                    "judge evidence manifest",
                ],
            },
            "upstream_reviews": {
                "production_status": production_output.get("buildability_review", {}).get("status"),
                "rigging_status": rigging_output.get("rigging_review", {}).get("status"),
                "rigging_blockers": rigging_output.get("blocked_until", []),
            },
            "context_id": request.context.context_id,
        }
        return AgentResult(
            task_id=task.task_id,
            agent_id=task.assigned_agent,
            summary=f"Blender package prepared for {object_id} at {height_mm}mm without mutating scene files.",
            outputs=outputs,
            evidence_refs=[request.context.context_id],
            assumptions=[
                "This deterministic phase does not open or mutate Blender scene files.",
                "Real geometry and render artifacts remain pending until the Blender adapter runs.",
            ],
            risks=[
                "Visual evidence remains provisional until a real Blender measurement/render is produced.",
                "Rigging blockers must stay visible to the judge and downstream release gates.",
            ],
            requires_human_decision=False,
        )


class DelegatingAgentRuntime:
    """Route selected tasks to a specialist runtime and keep the rest deterministic."""

    def __init__(self, task_runtimes: dict[str, AgentRuntime], fallback: AgentRuntime | None = None):
        self.task_runtimes = task_runtimes
        self.fallback = fallback or DeterministicAgentRuntime()

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        runtime = self.task_runtimes.get(request.task.task_id, self.fallback)
        return runtime.execute(request)
