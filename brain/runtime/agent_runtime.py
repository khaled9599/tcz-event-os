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


class DelegatingAgentRuntime:
    """Route selected tasks to a specialist runtime and keep the rest deterministic."""

    def __init__(self, task_runtimes: dict[str, AgentRuntime], fallback: AgentRuntime | None = None):
        self.task_runtimes = task_runtimes
        self.fallback = fallback or DeterministicAgentRuntime()

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        runtime = self.task_runtimes.get(request.task.task_id, self.fallback)
        return runtime.execute(request)
