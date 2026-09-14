from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any, Protocol


class AdvisoryChatRuntime(Protocol):
    provider_name: str

    def respond(
        self,
        *,
        agent: dict[str, Any],
        message: str,
        history: list[dict[str, Any]],
        attachments: list[dict[str, Any]],
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
        attachments: list[dict[str, Any]],
    ) -> str:
        del history
        focus = ", ".join(agent.get("owns", [])[:3]) or agent.get(
            "department", "project work"
        )
        attachment_note = ""
        if attachments:
            names = ", ".join(item["filename"] for item in attachments)
            readable = sum(bool(item.get("extracted_text")) for item in attachments)
            attachment_note = (
                f"\n\nAttached files received: {names}. "
                f"Readable text was extracted from {readable} of {len(attachments)} file(s)."
            )
        received = f'"{message.strip()}"' if message.strip() else "the attached file(s)"
        return (
            f'I am {agent["name"]}. I received: {received}{attachment_note}\n\n'
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
        attachments: list[dict[str, Any]],
    ) -> str:
        client = self.client or self._build_client()
        recent_history = history[-12:]
        input_items = []
        for index, item in enumerate(recent_history):
            if item["role"] not in {"user", "assistant"}:
                continue
            current_attachments = attachments if index == len(recent_history) - 1 else []
            input_items.append(
                {
                    "role": item["role"],
                    "content": self._history_content(item, current_attachments),
                }
            )
        response = client.responses.create(
            model=self.model,
            instructions=self._instructions(agent),
            input=input_items,
            store=False,
        )
        return response.output_text

    def _history_content(
        self, item: dict[str, Any], attachments: list[dict[str, Any]]
    ) -> str | list[dict[str, Any]]:
        if not attachments:
            names = [record["filename"] for record in item.get("attachments", [])]
            suffix = f"\n\n[Attached files: {', '.join(names)}]" if names else ""
            return f"{item['content']}{suffix}"

        blocks: list[dict[str, Any]] = []
        if item["content"]:
            blocks.append({"type": "input_text", "text": item["content"]})
        for attachment in attachments:
            if attachment.get("extracted_text"):
                blocks.append(
                    {
                        "type": "input_text",
                        "text": (
                            f"Attached file {attachment['filename']}:\n"
                            f"{attachment['extracted_text']}"
                        ),
                    }
                )
            else:
                path = Path(attachment["storage_path"])
                encoded = base64.b64encode(path.read_bytes()).decode("ascii")
                data_url = f"data:{attachment['content_type']};base64,{encoded}"
                if attachment["content_type"].startswith("image/"):
                    blocks.append(
                        {
                            "type": "input_image",
                            "image_url": data_url,
                            "detail": "auto",
                        }
                    )
                    continue
                blocks.append(
                    {
                        "type": "input_file",
                        "filename": attachment["filename"],
                        "file_data": data_url,
                    }
                )
        return blocks

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
