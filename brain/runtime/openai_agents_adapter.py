from __future__ import annotations

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
