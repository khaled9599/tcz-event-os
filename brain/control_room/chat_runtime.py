from __future__ import annotations

import os
from typing import Any, Protocol


class AdvisoryChatRuntime(Protocol):
    provider_name: str

    def respond(
        self,
        *,
        agent: dict[str, Any],
        message: str,
        history: list[dict[str, Any]],
    ) -> str:
        """Return an advisory response without mutating canonical state."""


class DeterministicAdvisoryRuntime:
    provider_name = "deterministic"

    def respond(
        self,
        *,
        agent: dict[str, Any],
        message: str,
        history: list[dict[str, Any]],
    ) -> str:
        del history
        focus = ", ".join(agent.get("owns", [])[:3]) or agent.get(
            "department", "project work"
        )
        return (
            f'I am {agent["name"]}. I received: "{message.strip()}"\n\n'
            f"My review boundary is {focus}. {agent['mission']}\n\n"
            "This is an advisory response. No project state or external tool was changed. "
            "Submit the Jotun workflow when you want this request routed through context, "
            "specialist review, approval, judging, and canonical-state commit."
        )


class OpenAIAdvisoryRuntime:
    provider_name = "openai"

    def __init__(self, model: str | None = None, client: Any | None = None):
        self.model = model or os.getenv("TCZ_OPENAI_MODEL", "gpt-5")
        self.client = client

    def respond(
        self,
        *,
        agent: dict[str, Any],
        message: str,
        history: list[dict[str, Any]],
    ) -> str:
        client = self.client or self._build_client()
        response = client.responses.create(
            model=self.model,
            instructions=self._instructions(agent),
            input=[
                {"role": item["role"], "content": item["content"]}
                for item in history[-12:]
                if item["role"] in {"user", "assistant"}
            ],
            store=False,
        )
        return response.output_text

    def _build_client(self) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "Install TCZ with the openai optional dependency."
            ) from exc
        return OpenAI()

    def _instructions(self, agent: dict[str, Any]) -> str:
        skills = ", ".join(agent.get("skills", [])) or "none assigned"
        restrictions = "; ".join(agent.get("prohibited_actions", [])) or "none listed"
        return (
            f"You are {agent['name']} in TCZ Event OS. Mission: {agent['mission']} "
            f"Your assigned skills are: {skills}. Prohibited actions: {restrictions}. "
            "This conversation is advisory only. Do not claim that you changed canonical state, "
            "called tools, approved work, or performed side effects. Identify assumptions and risks. "
            "When execution is requested, recommend routing it through the controlled workflow."
        )
