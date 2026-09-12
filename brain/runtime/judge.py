from __future__ import annotations

from brain.contracts.runtime_contracts import FailureClass, TaskNode
from brain.runtime.agent_runtime import AgentResult


class IndependentJudge:
    id = "independent_judge"

    def review(self, task: TaskNode, result: AgentResult) -> dict:
        findings: list[dict] = []
        if not result.accepted:
            findings.append({
                "code": "agent_result_not_accepted",
                "severity": "high",
                "message": result.failure_detail or "Agent result was not accepted.",
            })
        if task.acceptance_criteria and not result.outputs:
            findings.append({
                "code": "missing_outputs",
                "severity": "high",
                "message": "Task has acceptance criteria but returned no outputs.",
            })
        if result.requires_human_decision:
            findings.append({
                "code": "human_decision_required",
                "severity": "medium",
                "message": "Agent result requires a human decision before commit.",
            })

        passed = not any(item["severity"] == "high" for item in findings)
        return {
            "judge": self.id,
            "task_id": task.task_id,
            "decision": "PASS" if passed else "FAIL",
            "findings": findings,
            "failure_class": None if passed else FailureClass.QUALITY_GATE.value,
        }
