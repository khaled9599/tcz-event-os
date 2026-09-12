from pathlib import Path

from brain.contracts.runtime_contracts import RunPhase
from brain.runtime.cli import run_scenario

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "examples" / "jotun_kanva" / "change_entrance_height.yaml"


def test_cli_scenario_pauses_for_approvals():
    result = run_scenario(SCENARIO)

    assert result.run.phase == RunPhase.APPROVE
    assert [packet.required_level for packet in result.approvals] == ["L2", "L3"]
    assert result.committed_state is None


def test_cli_scenario_can_auto_approve_demo_run():
    result = run_scenario(SCENARIO, auto_approve=True)

    assert result.run.phase == RunPhase.COMPLETED
    assert result.committed_state["height_mm"] == 5500
    assert result.run.context_package_ids
    assert all(task.status == "completed" for task in result.graph.nodes)
