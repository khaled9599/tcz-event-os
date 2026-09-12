from pathlib import Path

from brain.contracts.runtime_contracts import SideEffectClass, TaskGraph, TaskNode
from brain.runtime.orchestrator import BrainOrchestrator


ROOT = Path(__file__).resolve().parents[2]


def build_graph() -> TaskGraph:
    impact = TaskNode(
        task_id="T-IMPACT",
        objective="Assess impact of increasing KANVA_ENTRANCE_01 height to 5500mm",
        object_id="KANVA_ENTRANCE_01",
        assigned_agent="executive_producer",
        required_skills=[
            "orchestration.task_decomposition",
            "orchestration.change_impact",
            "orchestration.approval_routing",
        ],
        acceptance_criteria=["affected domains identified", "approval levels assigned"],
    )
    spatial = TaskNode(
        task_id="T-SPATIAL",
        objective="Revise entrance geometry and preserve approved clear opening",
        object_id="KANVA_ENTRANCE_01",
        assigned_agent="creative_spatial",
        required_skills=[
            "creative.installation_design",
            "visualization.reference_engineering",
        ],
        depends_on=[impact.task_id],
        acceptance_criteria=["height 5500mm", "clear opening retained", "design intent preserved"],
    )
    production = TaskNode(
        task_id="T-PRODUCTION",
        objective="Review buildability and update material takeoff",
        object_id="KANVA_ENTRANCE_01",
        assigned_agent="production_engineering",
        required_skills=[
            "production.buildability_review",
            "production.material_takeoff",
            "visualization.blender_assembly",
        ],
        depends_on=[spatial.task_id],
        required_approval_level="L2",
        side_effect_class=SideEffectClass.REVERSIBLE,
        acceptance_criteria=["buildability reviewed", "quantity impact stated", "structural signoff separated"],
    )
    rigging = TaskNode(
        task_id="T-RIGGING",
        objective="Review temporary-structure rigging implications for revised height",
        object_id="KANVA_ENTRANCE_01",
        assigned_agent="rigging",
        required_skills=["technical.rigging_review"],
        depends_on=[production.task_id],
        required_approval_level="L3",
        side_effect_class=SideEffectClass.SAFETY_CRITICAL,
        acceptance_criteria=["engineering assumptions explicit", "qualified signoff required"],
    )
    blender = TaskNode(
        task_id="T-BLENDER",
        objective="Update approved entrance representation to 5500mm and validate render geometry",
        object_id="KANVA_ENTRANCE_01",
        assigned_agent="blender_production",
        required_skills=[
            "visualization.reference_engineering",
            "visualization.blender_modeling",
            "visualization.blender_assembly",
            "visualization.render_validation",
        ],
        depends_on=[production.task_id, rigging.task_id],
        acceptance_criteria=["model height 5500mm", "canonical object ID preserved", "render validation passes"],
    )
    judge = TaskNode(
        task_id="T-JUDGE",
        objective="Independently judge the revised entrance package",
        object_id="KANVA_ENTRANCE_01",
        assigned_agent="independent_judge",
        required_skills=["quality.independent_judging", "quality.visual_critique"],
        depends_on=[blender.task_id],
        acceptance_criteria=["no blocker findings", "measurable claims backed by evidence"],
    )
    return TaskGraph(objective="Increase Jotun Kanva entrance to 5.5m", nodes=[impact, spatial, production, rigging, blender, judge])


def main() -> None:
    before = {"object_id": "KANVA_ENTRANCE_01", "height_mm": 4200, "verification": "verified"}
    proposed = {"object_id": "KANVA_ENTRANCE_01", "height_mm": 5500, "verification": "unverified"}
    impacts = ["spatial", "production_engineering", "rigging", "quantity", "cost", "schedule", "blender", "visual_qa"]
    risks = ["structural assumptions require qualified review", "previous render and quantity artifacts become stale"]

    brain = BrainOrchestrator(ROOT)
    result = brain.start(
        objective="Increase KANVA_ENTRANCE_01 from 4200mm to 5500mm",
        graph=build_graph(),
        before_state=before,
        proposed_state=proposed,
        impacts=impacts,
        risks=risks,
    )

    print("phase after planning:", result.run.phase.value)
    print("approval levels:", [p.required_level for p in result.approvals])

    # Demo only: these decisions simulate the human / qualified-professional
    # responses that a real UI or workflow system would collect externally.
    decisions = {packet.approval_id: "approved" for packet in result.approvals}
    result = brain.resume(result, decisions, proposed)

    print("final phase:", result.run.phase.value)
    print("agents used:", result.run.agents_used)
    print("skills loaded:", [s.skill_id for s in result.run.skills_loaded])
    print("committed state:", result.committed_state)


if __name__ == "__main__":
    main()
