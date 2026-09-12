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


class DelegatingAgentRuntime:
    """Route selected tasks to a specialist runtime and keep the rest deterministic."""

    def __init__(self, task_runtimes: dict[str, AgentRuntime], fallback: AgentRuntime | None = None):
        self.task_runtimes = task_runtimes
        self.fallback = fallback or DeterministicAgentRuntime()

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        runtime = self.task_runtimes.get(request.task.task_id, self.fallback)
        return runtime.execute(request)
