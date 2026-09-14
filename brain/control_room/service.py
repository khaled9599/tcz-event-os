from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from brain.contracts.runtime_contracts import RunPhase
from brain.control_room.attachments import (
    MAX_ATTACHMENTS_PER_MESSAGE,
    extract_text,
    normalized_content_type,
    public_attachment,
    safe_filename,
    validate_attachment,
)
from brain.control_room.chat_runtime import (
    AdvisoryChatRuntime,
    DeterministicAdvisoryRuntime,
    OpenAIAdvisoryRuntime,
)
from brain.control_room.storage import ControlRoomStore
from brain.runtime.cli import (
    _build_runtime,
    _deserialize_result,
    _load_scenario,
    _serialize_result,
    _summarize,
    run_scenario,
)
from brain.runtime.orchestrator import BrainOrchestrator, OrchestrationResult


class AgentNotFound(KeyError):
    pass


class RunNotFound(KeyError):
    pass


class LiveRuntimeUnavailable(RuntimeError):
    pass


class ControlRoomService:
    def __init__(
        self,
        repo_root: str | Path,
        db_path: str | Path,
        *,
        deterministic_chat: AdvisoryChatRuntime | None = None,
        openai_chat: AdvisoryChatRuntime | None = None,
    ):
        self.repo_root = Path(repo_root).resolve()
        self.store = ControlRoomStore(db_path)
        self.upload_dir = self.store.path.parent / "control_room_uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.deterministic_chat = deterministic_chat or DeterministicAdvisoryRuntime()
        self.openai_chat = openai_chat or OpenAIAdvisoryRuntime()
        self._agents = self._load_agents()

    def _load_agents(self) -> dict[str, dict[str, Any]]:
        agents: dict[str, dict[str, Any]] = {}
        for path in sorted((self.repo_root / "configs" / "agents").glob("*.yaml")):
            payload = yaml.safe_load(path.read_text()) or {}
            if not isinstance(payload, dict) or "id" not in payload:
                continue
            payload["source_path"] = str(path.relative_to(self.repo_root))
            payload["status"] = self._display_status(
                payload.get("runtime_status", "dormant")
            )
            agents[payload["id"]] = payload
        return agents

    @staticmethod
    def _display_status(runtime_status: str) -> str:
        return {
            "active_mvp": "ready",
            "chartered": "chartered",
            "dormant": "offline",
        }.get(runtime_status, runtime_status)

    def health(self) -> dict[str, Any]:
        return {
            "status": "ready",
            "mode": "local",
            "openai_available": bool(os.getenv("OPENAI_API_KEY")),
            "openai_model": os.getenv("TCZ_OPENAI_MODEL", "gpt-5"),
            "database": str(self.store.path),
        }

    def list_agents(self) -> list[dict[str, Any]]:
        return sorted(
            self._agents.values(),
            key=lambda agent: (
                0 if agent["id"] == "executive_producer" else 1,
                agent.get("activation_phase", 99),
                agent["name"],
            ),
        )

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise AgentNotFound(agent_id) from exc

    def messages(self, agent_id: str) -> list[dict[str, Any]]:
        self.get_agent(agent_id)
        return self.store.list_messages(agent_id)

    def upload_attachment(
        self,
        agent_id: str,
        *,
        filename: str,
        content_type: str | None,
        data: bytes,
    ) -> dict[str, Any]:
        self.get_agent(agent_id)
        clean_name = safe_filename(filename)
        validate_attachment(clean_name, data)
        resolved_type = normalized_content_type(clean_name, content_type)
        record = self.store.add_attachment(
            agent_id=agent_id,
            filename=clean_name,
            content_type=resolved_type,
            size_bytes=len(data),
            storage_path="pending",
            extracted_text=extract_text(clean_name, data),
        )
        destination = self.upload_dir / f"{record['attachment_id']}{Path(clean_name).suffix.lower()}"
        destination.write_bytes(data)
        self.store.set_attachment_path(record["attachment_id"], str(destination))
        record["storage_path"] = str(destination)
        return public_attachment(record)

    def chat(
        self,
        agent_id: str,
        message: str,
        provider: str = "deterministic",
        attachment_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        agent = self.get_agent(agent_id)
        clean_message = message.strip()
        ids = list(dict.fromkeys(attachment_ids or []))
        if len(ids) > MAX_ATTACHMENTS_PER_MESSAGE:
            raise ValueError("a message can include at most 5 attachments")
        attachments = self.store.get_attachments(agent_id, ids)
        if not clean_message and not attachments:
            raise ValueError("message or attachment is required")

        runtime = self._resolve_chat_runtime(provider)
        public_attachments = [public_attachment(item) for item in attachments]
        user_message = self.store.add_message(
            agent_id=agent_id,
            role="user",
            content=clean_message,
            provider=runtime.provider_name,
            attachments=public_attachments,
        )
        history = self.store.list_messages(agent_id)
        try:
            content = runtime.respond(
                agent=agent,
                message=clean_message,
                history=history,
                attachments=attachments,
            )
        except Exception as exc:
            if runtime.provider_name == "openai":
                raise LiveRuntimeUnavailable(str(exc)) from exc
            raise
        assistant_message = self.store.add_message(
            agent_id=agent_id,
            role="assistant",
            content=content,
            provider=runtime.provider_name,
            conversation_id=user_message["conversation_id"],
        )
        return assistant_message

    def _resolve_chat_runtime(self, provider: str) -> AdvisoryChatRuntime:
        if provider == "auto":
            provider = "openai" if os.getenv("OPENAI_API_KEY") else "deterministic"
        if provider == "deterministic":
            return self.deterministic_chat
        if provider == "openai":
            if not os.getenv("OPENAI_API_KEY") and isinstance(
                self.openai_chat, OpenAIAdvisoryRuntime
            ):
                raise LiveRuntimeUnavailable(
                    "OPENAI_API_KEY is not configured in this terminal session."
                )
            return self.openai_chat
        raise ValueError(f"unknown chat provider: {provider}")

    def start_run(
        self,
        *,
        scenario: str = "examples/jotun_kanva/change_entrance_height.yaml",
        runtime_name: str = "deterministic",
        until_task: str | None = None,
    ) -> dict[str, Any]:
        scenario_path = self._scenario_path(scenario)
        scenario_data = _load_scenario(scenario_path)
        result = run_scenario(
            scenario_path,
            runtime_name=runtime_name,
            until_task=until_task,
        )
        self._save_result(
            result,
            scenario_path=scenario_path,
            runtime_name=runtime_name,
            proposed_state=scenario_data.get("proposed_state", {}),
        )
        self.store.add_event(
            result.run.run_id,
            "run.created",
            {"objective": result.run.objective, "phase": result.run.phase.value},
        )
        self._emit_result_events(None, result)
        return self.get_run(result.run.run_id)

    def _scenario_path(self, scenario: str) -> Path:
        candidate = (self.repo_root / scenario).resolve()
        if self.repo_root not in candidate.parents or candidate.suffix not in {
            ".yaml",
            ".yml",
        }:
            raise ValueError("scenario must be a YAML file inside the TCZ repository")
        if not candidate.exists():
            raise FileNotFoundError(candidate)
        return candidate

    def list_runs(self) -> list[dict[str, Any]]:
        return self.store.list_runs()

    def get_run(self, run_id: str) -> dict[str, Any]:
        record = self.store.load_run(run_id)
        if record is None:
            raise RunNotFound(run_id)
        result = _deserialize_result(record["checkpoint"]["result"])
        payload = self._public_result(result)
        payload["scenario_path"] = record["scenario_path"]
        payload["runtime_name"] = record["runtime_name"]
        payload["created_at"] = record["created_at"]
        payload["updated_at"] = record["updated_at"]
        payload["events"] = self.store.list_events(run_id)
        return payload

    def decide_approval(
        self, run_id: str, approval_id: str, decision: str
    ) -> dict[str, Any]:
        if decision not in {"approved", "rejected", "revision_requested"}:
            raise ValueError(f"invalid approval decision: {decision}")
        record = self.store.load_run(run_id)
        if record is None:
            raise RunNotFound(run_id)
        result = _deserialize_result(record["checkpoint"]["result"])
        if result.run.phase != RunPhase.APPROVE:
            raise ValueError("run is not awaiting approval")
        packet = next(
            (item for item in result.approvals if item.approval_id == approval_id), None
        )
        if packet is None:
            raise ValueError(f"approval {approval_id} does not belong to run {run_id}")

        before = _deserialize_result(record["checkpoint"]["result"])
        packet.status = decision
        decisions = {item.approval_id: item.status for item in result.approvals}
        proposed_state = record["checkpoint"].get("proposed_state", {})
        brain = BrainOrchestrator(
            self.repo_root,
            agent_runtime=_build_runtime(record["runtime_name"]),
        )
        result = brain.resume(result, decisions, proposed_state)
        self._save_result(
            result,
            scenario_path=Path(record["scenario_path"]),
            runtime_name=record["runtime_name"],
            proposed_state=proposed_state,
        )
        self._emit_result_events(before, result)
        return self.get_run(run_id)

    def canonical_state(self) -> dict[str, Any]:
        return {
            "state": self.store.latest_completed_state(),
            "source": "latest_completed_run",
        }

    def _save_result(
        self,
        result: OrchestrationResult,
        *,
        scenario_path: Path,
        runtime_name: str,
        proposed_state: dict[str, Any],
    ) -> None:
        resolved_scenario = (
            scenario_path.resolve()
            if scenario_path.is_absolute()
            else (self.repo_root / scenario_path).resolve()
        )
        checkpoint = {
            "result": _serialize_result(result, proposed_state),
            "proposed_state": proposed_state,
        }
        self.store.save_run(
            run_id=result.run.run_id,
            scenario_path=str(resolved_scenario.relative_to(self.repo_root)),
            runtime_name=runtime_name,
            objective=result.run.objective,
            phase=result.run.phase.value,
            checkpoint=checkpoint,
            approvals=[packet.model_dump(mode="json") for packet in result.approvals],
        )

    def _public_result(self, result: OrchestrationResult) -> dict[str, Any]:
        return {
            "summary": _summarize(result),
            "graph": result.graph.model_dump(mode="json"),
            "approvals": [
                packet.model_dump(mode="json") for packet in result.approvals
            ],
            "agent_results": {
                task_id: item.model_dump(mode="json")
                for task_id, item in result.agent_results.items()
            },
            "committed_state": result.committed_state,
        }

    def _emit_result_events(
        self,
        before: OrchestrationResult | None,
        after: OrchestrationResult,
    ) -> None:
        run_id = after.run.run_id
        before_phase = before.run.phase.value if before else None
        if before_phase != after.run.phase.value:
            self.store.add_event(
                run_id,
                "phase.changed",
                {"from": before_phase, "to": after.run.phase.value},
            )

        previous_approvals = {
            packet.approval_id: packet.status
            for packet in (before.approvals if before else [])
        }
        for packet in after.approvals:
            previous = previous_approvals.get(packet.approval_id)
            if previous != packet.status:
                event_type = (
                    "approval.requested"
                    if packet.status == "pending"
                    else "approval.decided"
                )
                self.store.add_event(
                    run_id,
                    event_type,
                    {
                        "approval_id": packet.approval_id,
                        "task_id": packet.task_id,
                        "level": packet.required_level,
                        "status": packet.status,
                    },
                )

        previous_results = set(before.agent_results) if before else set()
        for task_id, result in after.agent_results.items():
            if task_id not in previous_results:
                self.store.add_event(
                    run_id,
                    "task.completed",
                    {
                        "task_id": task_id,
                        "agent_id": result.agent_id,
                        "summary": result.summary,
                    },
                )

        if (
            after.run.phase == RunPhase.COMPLETED
            and before_phase != RunPhase.COMPLETED.value
        ):
            self.store.add_event(
                run_id, "run.completed", {"state": after.committed_state}
            )
        if after.run.phase == RunPhase.FAILED and before_phase != RunPhase.FAILED.value:
            self.store.add_event(
                run_id,
                "run.failed",
                {
                    "failure_class": after.run.failure_class.value
                    if after.run.failure_class
                    else None,
                    "detail": after.run.failure_detail,
                },
            )
