from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from brain.control_room.service import (
    AgentNotFound,
    ControlRoomService,
    LiveRuntimeUnavailable,
    RunNotFound,
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    provider: Literal["deterministic", "openai", "auto"] = "deterministic"


class WorkflowRequest(BaseModel):
    scenario: str = "examples/jotun_kanva/change_entrance_height.yaml"
    runtime_name: Literal["deterministic", "openai-impact"] = "deterministic"
    until_task: (
        Literal[
            "T-IMPACT", "T-SPATIAL", "T-PRODUCTION", "T-RIGGING", "T-BLENDER", "T-JUDGE"
        ]
        | None
    ) = None


class ApprovalRequest(BaseModel):
    decision: Literal["approved", "rejected", "revision_requested"]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def create_app(
    *,
    repo_root: str | Path | None = None,
    db_path: str | Path | None = None,
    service: ControlRoomService | None = None,
) -> FastAPI:
    root = Path(repo_root or _repo_root()).resolve()
    control_room = service or ControlRoomService(
        root,
        db_path or root / "work" / "control_room.db",
    )
    static_dir = Path(__file__).resolve().parent / "static"

    app = FastAPI(title="TCZ Agent Control Room", version="0.1.0")
    app.state.control_room = control_room
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/api/health")
    def health() -> dict:
        return control_room.health()

    @app.get("/api/agents")
    def agents() -> list[dict]:
        return control_room.list_agents()

    @app.get("/api/agents/{agent_id}")
    def agent(agent_id: str) -> dict:
        try:
            return control_room.get_agent(agent_id)
        except AgentNotFound as exc:
            raise HTTPException(status_code=404, detail="agent not found") from exc

    @app.get("/api/agents/{agent_id}/messages")
    def messages(agent_id: str) -> list[dict]:
        try:
            return control_room.messages(agent_id)
        except AgentNotFound as exc:
            raise HTTPException(status_code=404, detail="agent not found") from exc

    @app.post("/api/agents/{agent_id}/messages")
    def send_message(agent_id: str, payload: ChatRequest) -> dict:
        try:
            return control_room.chat(agent_id, payload.message, payload.provider)
        except AgentNotFound as exc:
            raise HTTPException(status_code=404, detail="agent not found") from exc
        except LiveRuntimeUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/runs")
    def runs() -> list[dict]:
        return control_room.list_runs()

    @app.post("/api/runs")
    def start_run(payload: WorkflowRequest) -> dict:
        try:
            return control_room.start_run(
                scenario=payload.scenario,
                runtime_name=payload.runtime_name,
                until_task=payload.until_task,
            )
        except (ValueError, FileNotFoundError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/runs/{run_id}")
    def run(run_id: str) -> dict:
        try:
            return control_room.get_run(run_id)
        except RunNotFound as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc

    @app.post("/api/runs/{run_id}/approvals/{approval_id}")
    def decide(run_id: str, approval_id: str, payload: ApprovalRequest) -> dict:
        try:
            return control_room.decide_approval(run_id, approval_id, payload.decision)
        except RunNotFound as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/runs/{run_id}/events")
    async def events(
        run_id: str, request: Request, after: int = 0
    ) -> StreamingResponse:
        try:
            control_room.get_run(run_id)
        except RunNotFound as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc

        async def stream() -> AsyncIterator[str]:
            cursor = after
            while not await request.is_disconnected():
                new_events = control_room.store.list_events(run_id, cursor)
                if new_events:
                    for event in new_events:
                        cursor = event["event_id"]
                        yield (
                            f"id: {cursor}\n"
                            f"event: {event['event_type']}\n"
                            f"data: {json.dumps(event)}\n\n"
                        )
                else:
                    yield ": keep-alive\n\n"
                await asyncio.sleep(1)

        return StreamingResponse(stream(), media_type="text/event-stream")

    @app.get("/api/state")
    def canonical_state() -> dict:
        return control_room.canonical_state()

    return app


load_dotenv(_repo_root() / ".env")
app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(
        "brain.control_room.app:app",
        host=os.getenv("TCZ_CONTROL_ROOM_HOST", "127.0.0.1"),
        port=int(os.getenv("TCZ_CONTROL_ROOM_PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
