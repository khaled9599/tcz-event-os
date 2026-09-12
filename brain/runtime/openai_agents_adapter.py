from __future__ import annotations

import json
from typing import Any

from brain.runtime.agent_runtime import AgentExecutionRequest, AgentResult


class OpenAIAgentsRuntime:
    """Provider adapter for OpenAI Agents SDK.

    The orchestrator only depends on the AgentRuntime contract. This adapter is
    intentionally thin so SDK-specific details do not leak into workflow policy.
    """

    def __init__(self, model: str = "gpt-5"):
        self.model = model

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        try:
            from agents import Agent, Runner
        except ImportError as exc:
            raise RuntimeError("Install the optional agents dependency with `pip install -e '.[agents]'`.") from exc

        instructions = (
            f"You are {request.task.assigned_agent} in TCZ Event OS. "
            "Use the provided canonical context and skill procedures only. "
            "Return concise structured work notes and do not perform side effects."
        )
        agent = Agent(name=request.task.assigned_agent or "TCZ Agent", model=self.model, instructions=instructions)
        prompt = {
            "task": request.task.model_dump(mode="json"),
            "context": request.context.model_dump(mode="json"),
            "skills": [
                {"skill_id": item.get("skill_id"), "content": item.get("content", "")}
                for item in request.skills
            ],
        }
        output = Runner.run_sync(agent, str(prompt)).final_output
        return AgentResult(
            task_id=request.task.task_id,
            agent_id=request.task.assigned_agent,
            summary=str(output),
            outputs={"raw_output": str(output)},
            evidence_refs=[request.context.context_id],
        )


IMPACT_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "affected_domains": {"type": "array", "items": {"type": "string"}},
        "required_agents": {"type": "array", "items": {"type": "string"}},
        "approval_levels": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "task_id": {"type": "string"},
                    "level": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["task_id", "level", "reason"],
            },
        },
        "risks": {"type": "array", "items": {"type": "string"}},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "recommended_next_tasks": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "affected_domains",
        "required_agents",
        "approval_levels",
        "risks",
        "assumptions",
        "recommended_next_tasks",
    ],
}


class OpenAIImpactRuntime:
    """LLM-backed runtime for the safe impact-analysis task only."""

    def __init__(self, model: str = "gpt-5", client: Any | None = None):
        self.model = model
        self.client = client

    def execute(self, request: AgentExecutionRequest) -> AgentResult:
        if request.task.task_id != "T-IMPACT":
            raise ValueError("OpenAIImpactRuntime only handles T-IMPACT")

        client = self.client or self._build_client()
        response = client.responses.create(
            model=self.model,
            input=self._prompt(request),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "tcz_impact_analysis",
                    "schema": IMPACT_OUTPUT_SCHEMA,
                    "strict": True,
                }
            },
        )
        outputs = json.loads(response.output_text)
        return AgentResult(
            task_id=request.task.task_id,
            agent_id=request.task.assigned_agent,
            summary="OpenAI impact analysis completed.",
            outputs=outputs,
            evidence_refs=[request.context.context_id],
            assumptions=outputs["assumptions"],
            risks=outputs["risks"],
            requires_human_decision=False,
        )

    def _build_client(self) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the optional OpenAI SDK with `pip install openai`.") from exc
        return OpenAI()

    def _prompt(self, request: AgentExecutionRequest) -> str:
        skill_summaries = [
            {"skill_id": item.get("skill_id"), "content": item.get("content", "")[:4000]}
            for item in request.skills
        ]
        payload = {
            "role": "executive_producer",
            "task": request.task.model_dump(mode="json"),
            "context": request.context.model_dump(mode="json"),
            "skills": skill_summaries,
            "rules": [
                "Do not call tools or perform side effects.",
                "Use only the provided canonical context and skill procedures.",
                "Return only the required structured JSON fields.",
                "Return approval_levels as an array of task_id, level, and reason objects.",
                "Mark safety-critical rigging implications as L3.",
                "Mark production/buildability mutations as at least L2.",
            ],
        }
        return json.dumps(payload, sort_keys=True)
