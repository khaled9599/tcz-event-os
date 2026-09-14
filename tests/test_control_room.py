from pathlib import Path

from fastapi.testclient import TestClient

from brain.control_room.app import create_app

ROOT = Path(__file__).resolve().parents[1]


def build_client(tmp_path: Path) -> TestClient:
    app = create_app(repo_root=ROOT, db_path=tmp_path / "control_room.db")
    return TestClient(app)


def test_control_room_lists_agents_and_health(tmp_path):
    with build_client(tmp_path) as client:
        health = client.get("/api/health")
        agents = client.get("/api/agents")

    assert health.status_code == 200
    assert health.json()["status"] == "ready"
    assert agents.status_code == 200
    assert len(agents.json()) >= 6
    executive = next(
        item for item in agents.json() if item["id"] == "executive_producer"
    )
    assert executive["name"] == "Executive Producer"
    assert "orchestration.task_decomposition" in executive["skills"]


def test_control_room_persists_advisory_agent_conversation(tmp_path):
    with build_client(tmp_path) as client:
        response = client.post(
            "/api/agents/creative_spatial/messages",
            json={"message": "Review the 5.5m entrance", "provider": "deterministic"},
        )
        messages = client.get("/api/agents/creative_spatial/messages")

    assert response.status_code == 200
    assert response.json()["provider"] == "deterministic"
    assert "No project state" in response.json()["content"]
    assert [item["role"] for item in messages.json()] == ["user", "assistant"]


def test_control_room_runs_jotun_workflow_through_approvals(tmp_path):
    with build_client(tmp_path) as client:
        started = client.post(
            "/api/runs",
            json={"runtime_name": "deterministic", "until_task": "T-BLENDER"},
        )

        assert started.status_code == 200
        run = started.json()
        assert run["summary"]["phase"] == "approve"
        assert [item["required_level"] for item in run["approvals"]] == ["L2", "L3"]

        for packet in run["approvals"]:
            decision = client.post(
                f"/api/runs/{run['summary']['run_id']}/approvals/{packet['approval_id']}",
                json={"decision": "approved"},
            )
            assert decision.status_code == 200
            run = decision.json()

        canonical = client.get("/api/state")

    assert run["summary"]["phase"] == "completed"
    assert run["summary"]["task_statuses"]["T-BLENDER"] == "completed"
    assert run["committed_state"]["height_mm"] == 5500
    assert canonical.json()["state"]["object_id"] == "KANVA_ENTRANCE_01"
    assert any(event["event_type"] == "run.completed" for event in run["events"])


def test_control_room_rejects_scenarios_outside_repo(tmp_path):
    with build_client(tmp_path) as client:
        response = client.post(
            "/api/runs",
            json={"scenario": "../outside.yaml", "runtime_name": "deterministic"},
        )

    assert response.status_code == 400
