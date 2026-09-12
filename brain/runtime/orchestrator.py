from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from brain.contracts.runtime_contracts import (
    ApprovalPacket,
    FailureClass,
    RunPhase,
    RunTrace,
    SkillActivation,
    TaskGraph,
    TaskNode,
)
from brain.runtime.agent_runtime import (
    AgentExecutionRequest,
    AgentResult,
    AgentRuntime,
    DeterministicAgentRuntime,
)
from brain.runtime.approval_policy import approval_required, can_execute
from brain.runtime.context_builder import BrainContextBuilder
from brain.runtime.judge import IndependentJudge
from brain.runtime.skill_loader import SkillLoader
from brain.runtime.workflow_engine import require_all_completed, require_transition


@dataclass
class OrchestrationResult:
    run: RunTrace
    graph: TaskGraph
    approvals: list[ApprovalPacket] = field(default_factory=list)
    outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    agent_results: dict[str, AgentResult] = field(default_factory=dict)
    committed_state: dict[str, Any] | None = None


class BrainOrchestrator:
    """Deterministic shell around specialist reasoning.

    The LLM/agent implementations plug into this shell. The shell owns the
    invariants: plan first, load authorized skills, gate side effects, preserve
    approval pauses, verify outputs, and commit only after required work passes.
    """

    def __init__(
        self,
        repo_root: str | Path,
        agent_runtime: AgentRuntime | None = None,
        context_builder: BrainContextBuilder | None = None,
        judge: IndependentJudge | None = None,
    ):
        self.repo_root = Path(repo_root)
        self.skills = SkillLoader(self.repo_root)
        self.agent_runtime = agent_runtime or DeterministicAgentRuntime()
        self.context_builder = context_builder or BrainContextBuilder()
        self.judge = judge or IndependentJudge()

    def _activate_skills(self, run: RunTrace, task: TaskNode) -> None:
        if not task.assigned_agent:
            return
        resolved = self.skills.resolve(task.assigned_agent, task.required_skills)
        if task.assigned_agent not in run.agents_used:
            run.agents_used.append(task.assigned_agent)
        for item in resolved:
            if not any(x.skill_id == item["skill_id"] for x in run.skills_loaded):
                run.skills_loaded.append(
                    SkillActivation(
                        skill_id=item["skill_id"],
                        reason=f"Required by task {task.task_id}",
                        source_path=item["path"],
                    )
                )

    def approval_for(
        self,
        run: RunTrace,
        task: TaskNode,
        before: dict[str, Any],
        after: dict[str, Any],
        impacts: list[str],
        risks: list[str],
    ) -> ApprovalPacket:
        packet = ApprovalPacket(
            run_id=run.run_id,
            task_id=task.task_id,
            requested_action=task.objective,
            required_level=approval_required(task.required_approval_level, task.side_effect_class),
            before=before,
            after=after,
            impacts=impacts,
            risks=risks,
            recommendation="approve only when evidence and required specialist reviews are complete",
        )
        run.approval_ids.append(packet.approval_id)
        return packet

    def start(
        self,
        objective: str,
        graph: TaskGraph,
        before_state: dict[str, Any],
        proposed_state: dict[str, Any],
        impacts: list[str],
        risks: list[str],
    ) -> OrchestrationResult:
        run = RunTrace(objective=objective)
        result = OrchestrationResult(run=run, graph=graph)

        run.phase = require_transition(run.phase, RunPhase.PLAN)
        run.task_graph_id = graph.graph_id
        for task in graph.nodes:
            self._activate_skills(run, task)

        run.phase = require_transition(run.phase, RunPhase.VALIDATE)
        self._validate_graph(graph)

        for task in graph.nodes:
            level = approval_required(task.required_approval_level, task.side_effect_class)
            if level in {"L2", "L3"}:
                packet = self.approval_for(run, task, before_state, proposed_state, impacts, risks)
                task.status = "awaiting_approval"
                result.approvals.append(packet)

        if result.approvals:
            run.phase = require_transition(run.phase, RunPhase.APPROVE)
            return result

        run.phase = require_transition(run.phase, RunPhase.EXECUTE)
        return self._execute_verify_commit(result, before_state, proposed_state, impacts, risks)

    def resume(
        self,
        result: OrchestrationResult,
        approval_decisions: dict[str, str],
        proposed_state: dict[str, Any],
    ) -> OrchestrationResult:
        if result.run.phase != RunPhase.APPROVE:
            raise ValueError(f"run {result.run.run_id} is not awaiting approval")

        for packet in result.approvals:
            decision = approval_decisions.get(packet.approval_id)
            if decision is not None:
                if decision not in {"pending", "approved", "rejected", "revision_requested"}:
                    raise ValueError(f"invalid approval status: {decision}")
                packet.status = decision

        rejected = [p for p in result.approvals if p.status in {"rejected", "revision_requested"}]
        if rejected:
            result.run.phase = require_transition(result.run.phase, RunPhase.PLAN)
            for packet in rejected:
                task = next(t for t in result.graph.nodes if t.task_id == packet.task_id)
                task.status = "blocked"
            return result

        blocked = [p for p in result.approvals if not can_execute(p)]
        if blocked:
            return result

        for packet in result.approvals:
            task = next(t for t in result.graph.nodes if t.task_id == packet.task_id)
            task.status = "pending"

        result.run.phase = require_transition(result.run.phase, RunPhase.EXECUTE)
        approval_impacts = result.approvals[0].impacts if result.approvals else []
        approval_risks = result.approvals[0].risks if result.approvals else []
        before_state = result.approvals[0].before if result.approvals else {}
        return self._execute_verify_commit(result, before_state, proposed_state, approval_impacts, approval_risks)

    def _validate_graph(self, graph: TaskGraph) -> None:
        known_ids = {task.task_id for task in graph.nodes}
        for task in graph.nodes:
            missing = [dep for dep in task.depends_on if dep not in known_ids]
            if missing:
                raise ValueError(f"task {task.task_id} references missing dependencies: {missing}")

    def _execute_verify_commit(
        self,
        result: OrchestrationResult,
        before_state: dict[str, Any],
        proposed_state: dict[str, Any],
        impacts: list[str],
        risks: list[str],
    ) -> OrchestrationResult:
        graph = result.graph
        completed = {task.task_id for task in graph.nodes if task.status == "completed"}
        while len(completed) < len(graph.nodes):
            progressed = False
            for task in graph.nodes:
                if task.task_id in completed:
                    continue
                if task.status in {"blocked", "awaiting_approval", "cancelled", "failed"}:
                    continue
                if all(dep in completed for dep in task.depends_on):
                    task.status = "running"
                    try:
                        skills = self.skills.resolve(task.assigned_agent, task.required_skills) if task.assigned_agent else []
                        context = self.context_builder.build(
                            run_id=result.run.run_id,
                            task=task,
                            before_state=before_state,
                            proposed_state=proposed_state,
                            impacts=impacts,
                            risks=risks,
                            prior_outputs=result.outputs,
                        )
                        if context.context_id not in result.run.context_package_ids:
                            result.run.context_package_ids.append(context.context_id)
                        agent_result = self.agent_runtime.execute(
                            AgentExecutionRequest(
                                run_id=result.run.run_id,
                                task=task,
                                context=context,
                                skills=skills,
                            )
                        )
                        if not agent_result.accepted:
                            task.status = "failed"
                            result.run.failure_class = agent_result.failure_class or FailureClass.INVALID_OUTPUT
                            result.run.failure_detail = agent_result.failure_detail or "agent result was not accepted"
                            result.run.phase = require_transition(result.run.phase, RunPhase.FAILED)
                            return result
                        result.agent_results[task.task_id] = agent_result
                        result.outputs[task.task_id] = agent_result.model_dump(mode="json")
                        task.status = "completed"
                        completed.add(task.task_id)
                        progressed = True
                    except Exception as exc:  # noqa: BLE001 - classify adapter failures at the workflow boundary.
                        task.status = "failed"
                        result.run.failure_class = self._classify_failure(exc)
                        result.run.failure_detail = str(exc)
                        result.run.phase = require_transition(result.run.phase, RunPhase.FAILED)
                        return result
            if not progressed:
                raise RuntimeError("task graph deadlocked, blocked, or contains a dependency cycle")

        result.run.phase = require_transition(result.run.phase, RunPhase.VERIFY)
        for task in graph.nodes:
            review = self.judge.review(task, result.agent_results[task.task_id])
            result.run.judge_results.append(review)
            if review["decision"] != "PASS":
                result.run.failure_class = FailureClass.QUALITY_GATE
                result.run.failure_detail = f"judge failed task {task.task_id}"
                result.run.phase = require_transition(result.run.phase, RunPhase.FAILED)
                return result

        require_all_completed(task.status for task in graph.nodes)
        result.run.phase = require_transition(result.run.phase, RunPhase.COMMIT)
        result.committed_state = proposed_state
        result.run.phase = require_transition(result.run.phase, RunPhase.COMPLETED)
        return result

    def _classify_failure(self, exc: Exception) -> FailureClass:
        if isinstance(exc, ValueError):
            return FailureClass.INVALID_OUTPUT
        if isinstance(exc, PermissionError):
            return FailureClass.PERMISSION
        if isinstance(exc, RuntimeError):
            return FailureClass.EXTERNAL_DEPENDENCY
        return FailureClass.TRANSIENT_TOOL

    def run_vertical_slice(
        self,
        objective: str,
        graph: TaskGraph,
        before_state: dict[str, Any],
        proposed_state: dict[str, Any],
        impacts: list[str],
        risks: list[str],
        approve_all_for_demo: bool = False,
    ) -> OrchestrationResult:
        result = self.start(objective, graph, before_state, proposed_state, impacts, risks)
        if result.run.phase == RunPhase.APPROVE and approve_all_for_demo:
            decisions = {packet.approval_id: "approved" for packet in result.approvals}
            return self.resume(result, decisions, proposed_state)
        return result
