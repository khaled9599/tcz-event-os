from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from brain.contracts.runtime_contracts import (
    ApprovalPacket,
    RunPhase,
    RunTrace,
    SideEffectClass,
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

    The LLM/agent implementations can be plugged in later. This class owns the
    invariant workflow: plan first, load authorized skills, gate side effects,
    verify outputs, and commit only after all required tasks complete.
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

    def approval_for(self, run: RunTrace, task: TaskNode, before: dict[str, Any], after: dict[str, Any], impacts: list[str], risks: list[str]) -> ApprovalPacket:
        level = approval_required(task.required_approval_level, task.side_effect_class)
        packet = ApprovalPacket(
            run_id=run.run_id,
            task_id=task.task_id,
            requested_action=task.objective,
            required_level=level,
            before=before,
            after=after,
            impacts=impacts,
            risks=risks,
            recommendation="approve if evidence and specialist reviews are complete",
        )
        run.approval_ids.append(packet.approval_id)
        return packet

    def run_vertical_slice(
        self,
        objective: str,
        graph: TaskGraph,
        before_state: dict[str, Any],
        proposed_state: dict[str, Any],
        impacts: list[str],
        risks: list[str],
        auto_approve_levels: set[str] | None = None,
    ) -> OrchestrationResult:
        auto_approve_levels = auto_approve_levels or {"L0", "L1"}
        run = RunTrace(objective=objective)
        result = OrchestrationResult(run=run, graph=graph)

        run.phase = require_transition(run.phase, RunPhase.PLAN)
        run.task_graph_id = graph.graph_id

        for task in graph.nodes:
            self._activate_skills(run, task)

        run.phase = require_transition(run.phase, RunPhase.VALIDATE)
        known_ids = {task.task_id for task in graph.nodes}
        for task in graph.nodes:
            missing = [dep for dep in task.depends_on if dep not in known_ids]
            if missing:
                raise ValueError(f"task {task.task_id} references missing dependencies: {missing}")

        approval_packets: dict[str, ApprovalPacket] = {}
        for task in graph.nodes:
            level = approval_required(task.required_approval_level, task.side_effect_class)
            if level not in {"L0", "L1"}:
                packet = self.approval_for(run, task, before_state, proposed_state, impacts, risks)
                if level in auto_approve_levels:
                    packet.status = "approved"
                else:
                    task.status = "awaiting_approval"
                approval_packets[task.task_id] = packet
                result.approvals.append(packet)

        if result.approvals:
            run.phase = require_transition(run.phase, RunPhase.APPROVE)
            blocked = [p for p in result.approvals if not can_execute(p)]
            if blocked:
                return result
            run.phase = require_transition(run.phase, RunPhase.EXECUTE)
        else:
            run.phase = require_transition(run.phase, RunPhase.EXECUTE)

        completed: set[str] = set()
        while len(completed) < len(graph.nodes):
            progressed = False
            for task in graph.nodes:
                if task.task_id in completed:
                    continue
                if all(dep in completed for dep in task.depends_on):
                    packet = approval_packets.get(task.task_id)
                    if packet and not can_execute(packet):
                        task.status = "awaiting_approval"
                        continue
                    task.status = "running"
                    # Placeholder execution result. Specialist agent/tool adapters
                    # will replace this while preserving the workflow contract.
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
                raise RuntimeError("task graph deadlocked or contains a dependency cycle")

        run.phase = require_transition(run.phase, RunPhase.VERIFY)
        run.judge_results.append({
            "judge": "independent_judge",
            "decision": "PASS",
            "reason": "all task acceptance placeholders passed in vertical slice",
        })

        require_all_completed(task.status for task in graph.nodes)
        run.phase = require_transition(run.phase, RunPhase.COMMIT)
        result.committed_state = proposed_state
        run.phase = require_transition(run.phase, RunPhase.COMPLETED)
        return result
