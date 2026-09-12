from pathlib import Path

from brain.contracts.runtime_contracts import (
    FailureClass,
    RunPhase,
    SideEffectClass,
    TaskGraph,
    TaskNode,
)
from brain.runtime.agent_runtime import AgentResult
from brain.runtime.orchestrator import BrainOrchestrator
from brain.runtime.skill_loader import SkillLoader

ROOT = Path(__file__).resolve().parents[1]


def test_skill_loader_matches_matrix_schema():
    loader = SkillLoader(ROOT)
    assert "orchestration.task_decomposition" in loader.required_skills("executive_producer")
    assert "quality.visual_critique" in loader.optional_skills("independent_judge")
    resolved = loader.resolve("rigging", ["technical.rigging_review"])
    assert resolved[0]["skill_id"] == "technical.rigging_review"


def test_brain_pauses_then_resumes_after_approval():
    t1 = TaskNode(
        task_id="T1",
        objective="Assess change",
        assigned_agent="executive_producer",
        required_skills=["orchestration.change_impact"],
    )
    t2 = TaskNode(
        task_id="T2",
        objective="Review rigging implication",
        assigned_agent="rigging",
        required_skills=["technical.rigging_review"],
        depends_on=["T1"],
        required_approval_level="L3",
        side_effect_class=SideEffectClass.SAFETY_CRITICAL,
    )
    graph = TaskGraph(objective="Revise entrance height", nodes=[t1, t2])
    before = {"height_mm": 4200}
    proposed = {"height_mm": 5500}

    brain = BrainOrchestrator(ROOT)
    result = brain.start(
        objective="Increase entrance height",
        graph=graph,
        before_state=before,
        proposed_state=proposed,
        impacts=["rigging", "production"],
        risks=["qualified structural review required"],
    )

    assert result.run.phase == RunPhase.APPROVE
    assert result.approvals[0].required_level == "L3"
    assert result.committed_state is None

    decisions = {result.approvals[0].approval_id: "approved"}
    result = brain.resume(result, decisions, proposed)

    assert result.run.phase == RunPhase.COMPLETED
    assert result.committed_state == proposed
    assert all(task.status == "completed" for task in graph.nodes)


def test_rejection_returns_run_to_plan():
    task = TaskNode(
        task_id="T1",
        objective="Safety critical review",
        assigned_agent="rigging",
        required_skills=["technical.rigging_review"],
        required_approval_level="L3",
        side_effect_class=SideEffectClass.SAFETY_CRITICAL,
    )
    graph = TaskGraph(objective="Safety review", nodes=[task])
    brain = BrainOrchestrator(ROOT)
    result = brain.start("Safety review", graph, {}, {"height_mm": 5500}, ["rigging"], ["risk"])
    result = brain.resume(result, {result.approvals[0].approval_id: "rejected"}, {"height_mm": 5500})

    assert result.run.phase == RunPhase.PLAN
    assert task.status == "blocked"
    assert result.committed_state is None


class RecordingRuntime:
    def __init__(self):
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return AgentResult(
            task_id=request.task.task_id,
            agent_id=request.task.assigned_agent,
            summary="recorded",
            outputs={"context": request.context.model_dump(mode="json")},
            evidence_refs=[request.context.context_id],
        )


def test_pluggable_runtime_receives_context_and_skills():
    runtime = RecordingRuntime()
    task = TaskNode(
        task_id="T1",
        objective="Assess change",
        object_id="KANVA_ENTRANCE_01",
        assigned_agent="executive_producer",
        required_skills=["orchestration.change_impact"],
        acceptance_criteria=["impact identified"],
    )
    graph = TaskGraph(objective="Assess entrance change", nodes=[task])
    brain = BrainOrchestrator(ROOT, agent_runtime=runtime)

    result = brain.start(
        objective="Increase entrance height",
        graph=graph,
        before_state={"height_mm": 4200},
        proposed_state={"height_mm": 5500},
        impacts=["production"],
        risks=["quantity changes"],
    )

    assert result.run.phase == RunPhase.COMPLETED
    assert runtime.requests[0].context.authoritative_state["before"]["height_mm"] == 4200
    assert runtime.requests[0].context.authoritative_state["proposed"]["height_mm"] == 5500
    assert runtime.requests[0].skills[0]["skill_id"] == "orchestration.change_impact"
    assert result.run.context_package_ids == [runtime.requests[0].context.context_id]


class FailingRuntime:
    def execute(self, request):
        return AgentResult(
            task_id=request.task.task_id,
            agent_id=request.task.assigned_agent,
            status="failed",
            summary="invalid output",
            failure_class=FailureClass.INVALID_OUTPUT,
            failure_detail="missing required structured output",
        )


def test_agent_failure_is_classified_and_not_committed():
    task = TaskNode(
        task_id="T1",
        objective="Assess change",
        assigned_agent="executive_producer",
        required_skills=["orchestration.change_impact"],
    )
    graph = TaskGraph(objective="Assess entrance change", nodes=[task])
    brain = BrainOrchestrator(ROOT, agent_runtime=FailingRuntime())

    result = brain.start(
        objective="Increase entrance height",
        graph=graph,
        before_state={"height_mm": 4200},
        proposed_state={"height_mm": 5500},
        impacts=[],
        risks=[],
    )

    assert result.run.phase == RunPhase.FAILED
    assert result.run.failure_class == FailureClass.INVALID_OUTPUT
    assert result.committed_state is None
