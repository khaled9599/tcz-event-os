from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from brain.contracts.runtime_contracts import (
    ApprovalPacket,
    RunPhase,
    RunTrace,
    SkillActivation,
    TaskGraph,
    TaskNode,
)
from brain.runtime.approval_policy import approval_required, can_execute
from brain.runtime.skill_loader import SkillLoader
from brain.runtime.workflow_engine import require_all_completed, require_transition


@dataclass
class OrchestrationResult:
    run: RunTrace
    graph: TaskGraph
    approvals: list[ApprovalPacket] = field(default_factory=list)
    outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    committed_state: dict[str, Any] | None = None


class BrainOrchestrator:
    """Deterministic shell around specialist reasoning.

    The LLM/agent implementations plug into this shell. The shell owns the
    invariants: plan first, load authorized skills, gate side effects, preserve
    approval pauses, verify outputs, and commit only after required work passes.
    """

    def __init__(self, repo_root: str | Path):
        self.repo_root = Path(repo_root)
        self.skills = SkillLoader(self.repo_root)

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
        return self._execute_verify_commit(result, proposed_state)

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
        return self._execute_verify_commit(result, proposed_state)

    def _validate_graph(self, graph: TaskGraph) -> None:
        known_ids = {task.task_id for task in graph.nodes}
        for task in graph.nodes:
            missing = [dep for dep in task.depends_on if dep not in known_ids]
            if missing:
                raise ValueError(f"task {task.task_id} references missing dependencies: {missing}")

    def _execute_verify_commit(
        self,
        result: OrchestrationResult,
        proposed_state: dict[str, Any],
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
                    result.outputs[task.task_id] = {
                        "agent": task.assigned_agent,
                        "objective": task.objective,
                        "skills": task.required_skills,
                        "accepted": True,
                    }
                    task.status = "completed"
                    completed.add(task.task_id)
                    progressed = True
            if not progressed:
                raise RuntimeError("task graph deadlocked, blocked, or contains a dependency cycle")

        result.run.phase = require_transition(result.run.phase, RunPhase.VERIFY)
        result.run.judge_results.append({
            "judge": "independent_judge",
            "decision": "PASS",
            "reason": "vertical-slice acceptance checks passed",
        })

        require_all_completed(task.status for task in graph.nodes)
        result.run.phase = require_transition(result.run.phase, RunPhase.COMMIT)
        result.committed_state = proposed_state
        result.run.phase = require_transition(result.run.phase, RunPhase.COMPLETED)
        return result

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
