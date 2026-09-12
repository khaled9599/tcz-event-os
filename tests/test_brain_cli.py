import json
from pathlib import Path

from brain.contracts.runtime_contracts import RunPhase
from brain.runtime.cli import (
    _render_result,
    resume_approval_file,
    run_scenario,
    write_approval_file,
    write_output_file,
)

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


def test_cli_scenario_resumes_from_approval_file(tmp_path):
    approval_file = tmp_path / "approvals.json"
    result = run_scenario(SCENARIO, approval_file=approval_file)
    write_approval_file(
        result,
        {"object_id": "KANVA_ENTRANCE_01", "height_mm": 5500, "verification": "unverified"},
        approval_file,
    )

    data = json.loads(approval_file.read_text())
    data["decisions"] = {
        approval_id: "approved"
        for approval_id in data["decisions"]
    }
    approval_file.write_text(json.dumps(data))

    resumed = resume_approval_file(approval_file)

    assert resumed.run.run_id == result.run.run_id
    assert resumed.run.phase == RunPhase.COMPLETED
    assert resumed.committed_state["height_mm"] == 5500
    assert all(packet.status == "approved" for packet in resumed.approvals)
    assert json.loads(approval_file.read_text())["runtime"] == "deterministic"


def test_cli_can_write_full_output_file(tmp_path):
    output_file = tmp_path / "full_result.json"
    result = run_scenario(SCENARIO, auto_approve=True)
    payload = _render_result(result, "full")

    write_output_file(payload, output_file)
    saved = json.loads(output_file.read_text())

    assert saved["summary"]["phase"] == "completed"
    assert saved["checkpoint"]["agent_results"]["T-IMPACT"]["outputs"]


def test_cli_can_run_only_impact_task():
    result = run_scenario(SCENARIO, only_task="T-IMPACT")

    assert result.run.phase == RunPhase.COMPLETED
    assert list(result.agent_results) == ["T-IMPACT"]
    assert result.committed_state["height_mm"] == 5500
    assert {task.task_id for task in result.graph.nodes} == {"T-IMPACT"}
