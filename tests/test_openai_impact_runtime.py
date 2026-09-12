import json
from pathlib import Path

from brain.contracts.runtime_contracts import RunPhase
from brain.runtime.agent_runtime import DelegatingAgentRuntime
from brain.runtime.cli import run_scenario
from brain.runtime.openai_agents_adapter import OpenAIImpactRuntime

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "examples" / "jotun_kanva" / "change_entrance_height.yaml"


class FakeResponse:
    output_text = json.dumps(
        {
            "affected_domains": ["spatial", "production_engineering", "rigging"],
            "required_agents": ["creative_spatial", "production_engineering", "rigging"],
            "approval_levels": {"T-PRODUCTION": "L2", "T-RIGGING": "L3"},
            "risks": ["structural assumptions require qualified review"],
            "assumptions": ["No external tools were invoked."],
            "recommended_next_tasks": ["Review geometry", "Review rigging implications"],
        }
    )


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse()


class FakeOpenAIClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_openai_impact_runtime_returns_structured_agent_result():
    client = FakeOpenAIClient()
    runtime = DelegatingAgentRuntime({"T-IMPACT": OpenAIImpactRuntime(client=client)})

    result = run_scenario(SCENARIO, auto_approve=True, agent_runtime=runtime)

    impact = result.agent_results["T-IMPACT"]
    assert result.run.phase == RunPhase.COMPLETED
    assert impact.outputs["approval_levels"]["T-RIGGING"] == "L3"
    assert impact.risks == ["structural assumptions require qualified review"]
    assert client.responses.calls[0]["text"]["format"]["type"] == "json_schema"


def test_openai_impact_runtime_rejects_non_impact_task():
    runtime = OpenAIImpactRuntime(client=FakeOpenAIClient())
    result = run_scenario(SCENARIO, auto_approve=True, agent_runtime=runtime)

    assert result.run.phase == RunPhase.FAILED
    assert result.run.failure_detail == "OpenAIImpactRuntime only handles T-IMPACT"
