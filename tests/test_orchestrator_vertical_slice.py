from pathlib import Path

from brain.contracts.runtime_contracts import RunPhase, SideEffectClass, TaskGraph, TaskNode
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
