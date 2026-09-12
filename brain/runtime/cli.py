from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from brain.contracts.runtime_contracts import (
    ApprovalPacket,
    RunTrace,
    SideEffectClass,
    TaskGraph,
    TaskNode,
)
from brain.runtime.agent_runtime import AgentResult, DelegatingAgentRuntime
from brain.runtime.openai_agents_adapter import OpenAIImpactRuntime
from brain.runtime.orchestrator import BrainOrchestrator, OrchestrationResult


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_scenario(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise TypeError(f"scenario must be a YAML mapping: {path}")
    return data


def _build_graph(data: dict[str, Any]) -> TaskGraph:
    graph_data = data.get("graph", {})
    nodes = []
    for item in graph_data.get("nodes", []):
        side_effect = item.get("side_effect_class", SideEffectClass.NONE.value)
        nodes.append(
            TaskNode(
                task_id=item["task_id"],
                objective=item["objective"],
                object_id=item.get("object_id"),
                assigned_agent=item.get("assigned_agent"),
                required_skills=item.get("required_skills", []),
                depends_on=item.get("depends_on", []),
                acceptance_criteria=item.get("acceptance_criteria", []),
                side_effect_class=SideEffectClass(side_effect),
                required_approval_level=item.get("required_approval_level", "L0"),
            )
        )
    return TaskGraph(objective=graph_data["objective"], nodes=nodes)


def _summarize(result: OrchestrationResult) -> dict[str, Any]:
    return {
        "run_id": result.run.run_id,
        "phase": result.run.phase.value,
        "approval_levels": [packet.required_level for packet in result.approvals],
        "approvals": [
            {
                "approval_id": packet.approval_id,
                "task_id": packet.task_id,
                "required_level": packet.required_level,
                "status": packet.status,
            }
            for packet in result.approvals
        ],
        "agents_used": result.run.agents_used,
        "skills_loaded": [skill.skill_id for skill in result.run.skills_loaded],
        "context_package_ids": result.run.context_package_ids,
        "task_statuses": {task.task_id: task.status for task in result.graph.nodes},
        "judge_decisions": [
            {"task_id": item["task_id"], "decision": item["decision"]}
            for item in result.run.judge_results
        ],
        "committed_state": result.committed_state,
        "failure_class": result.run.failure_class.value if result.run.failure_class else None,
        "failure_detail": result.run.failure_detail,
    }


def _serialize_result(result: OrchestrationResult, proposed_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "run": result.run.model_dump(mode="json"),
        "graph": result.graph.model_dump(mode="json"),
        "approvals": [packet.model_dump(mode="json") for packet in result.approvals],
        "outputs": result.outputs,
        "agent_results": {
            task_id: agent_result.model_dump(mode="json")
            for task_id, agent_result in result.agent_results.items()
        },
        "committed_state": result.committed_state,
        "proposed_state": proposed_state,
    }


def _deserialize_result(data: dict[str, Any]) -> OrchestrationResult:
    return OrchestrationResult(
        run=RunTrace.model_validate(data["run"]),
        graph=TaskGraph.model_validate(data["graph"]),
        approvals=[
            ApprovalPacket.model_validate(packet)
            for packet in data.get("approvals", [])
        ],
        outputs=data.get("outputs", {}),
        agent_results={
            task_id: AgentResult.model_validate(agent_result)
            for task_id, agent_result in data.get("agent_results", {}).items()
        },
        committed_state=data.get("committed_state"),
    )


def _approval_checkpoint(result: OrchestrationResult, proposed_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "instructions": "Set each decision to approved, rejected, revision_requested, or pending. Then resume with --resume this_file.json.",
        "decisions": {
            packet.approval_id: packet.status
            for packet in result.approvals
        },
        "checkpoint": _serialize_result(result, proposed_state),
    }


def write_approval_file(result: OrchestrationResult, proposed_state: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_approval_checkpoint(result, proposed_state), indent=2, sort_keys=True))


def _build_runtime(runtime_name: str):
    if runtime_name == "deterministic":
        return None
    if runtime_name == "openai-impact":
        return DelegatingAgentRuntime({"T-IMPACT": OpenAIImpactRuntime()})
    raise ValueError(f"unknown runtime: {runtime_name}")


def resume_approval_file(path: Path, *, runtime_name: str = "deterministic") -> OrchestrationResult:
    data = json.loads(path.read_text())
    brain = BrainOrchestrator(_repo_root(), agent_runtime=_build_runtime(runtime_name))
    result = _deserialize_result(data["checkpoint"])
    proposed_state = data["checkpoint"].get("proposed_state", {})
    return brain.resume(result, data.get("decisions", {}), proposed_state)


def run_scenario(
    path: Path,
    *,
    auto_approve: bool = False,
    approval_file: Path | None = None,
    runtime_name: str = "deterministic",
    agent_runtime=None,
) -> OrchestrationResult:
    data = _load_scenario(path)
    brain = BrainOrchestrator(_repo_root(), agent_runtime=agent_runtime or _build_runtime(runtime_name))
    proposed_state = data.get("proposed_state", {})
    result = brain.start(
        objective=data["objective"],
        graph=_build_graph(data),
        before_state=data.get("before_state", {}),
        proposed_state=proposed_state,
        impacts=data.get("impacts", []),
        risks=data.get("risks", []),
    )
    if approval_file and result.approvals:
        write_approval_file(result, proposed_state, approval_file)
    if auto_approve and result.approvals:
        decisions = {packet.approval_id: "approved" for packet in result.approvals}
        result = brain.resume(result, decisions, proposed_state)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a TCZ brain scenario.")
    parser.add_argument("scenario", nargs="?", type=Path, help="Path to a YAML brain scenario.")
    parser.add_argument(
        "--auto-approve-demo",
        action="store_true",
        help="Approve all generated approval packets for deterministic demo runs.",
    )
    parser.add_argument(
        "--approval-file",
        type=Path,
        help="Write an editable approval checkpoint when the run pauses.",
    )
    parser.add_argument(
        "--resume",
        type=Path,
        help="Resume a paused run from an edited approval checkpoint JSON file.",
    )
    parser.add_argument(
        "--runtime",
        choices=["deterministic", "openai-impact"],
        default="deterministic",
        help="Agent runtime to use. openai-impact only replaces T-IMPACT with an OpenAI-backed agent.",
    )
    args = parser.parse_args()

    if args.resume:
        result = resume_approval_file(args.resume, runtime_name=args.runtime)
    else:
        if args.scenario is None:
            parser.error("scenario is required unless --resume is provided")
        result = run_scenario(
            args.scenario,
            auto_approve=args.auto_approve_demo,
            approval_file=args.approval_file,
            runtime_name=args.runtime,
        )
    print(json.dumps(_summarize(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
