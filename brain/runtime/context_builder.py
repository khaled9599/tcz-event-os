from __future__ import annotations

from typing import Any

from brain.contracts.runtime_contracts import TaskNode
from brain.runtime.agent_runtime import ContextPackage


class BrainContextBuilder:
    """Builds the smallest sufficient context package for a task."""

    def build(
        self,
        *,
        run_id: str,
        task: TaskNode,
        before_state: dict[str, Any],
        proposed_state: dict[str, Any],
        impacts: list[str],
        risks: list[str],
        prior_outputs: dict[str, dict[str, Any]],
    ) -> ContextPackage:
        authoritative_state = {
            "before": before_state,
            "proposed": proposed_state,
            "impacts": impacts,
            "risks": risks,
        }
        if task.object_id:
            authoritative_state["target_object_id"] = task.object_id

        return ContextPackage(
            context_id=f"CTX-{run_id}-{task.task_id}",
            task_id=task.task_id,
            objective=task.objective,
            object_id=task.object_id,
            authoritative_state=authoritative_state,
            prior_outputs={
                dep: prior_outputs[dep]
                for dep in task.depends_on
                if dep in prior_outputs
            },
            acceptance_criteria=list(task.acceptance_criteria),
            excluded_context_notes=[
                "Only before/proposed state, impacts, risks, dependency outputs, and task metadata are included."
            ],
        )
