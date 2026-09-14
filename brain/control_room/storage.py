from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ControlRoomStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode = WAL;

                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS messages_agent_time
                ON messages(agent_id, created_at);

                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    scenario_path TEXT NOT NULL,
                    runtime_name TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    required_level TEXT NOT NULL,
                    status TEXT NOT NULL,
                    packet_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS events_run_id
                ON events(run_id, event_id);
                """
            )

    def add_message(
        self,
        *,
        agent_id: str,
        role: str,
        content: str,
        provider: str,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        record = {
            "message_id": f"MSG-{uuid4().hex[:12]}",
            "conversation_id": conversation_id or f"AGENT-{agent_id}",
            "agent_id": agent_id,
            "role": role,
            "content": content,
            "provider": provider,
            "created_at": utc_now(),
        }
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO messages (
                    message_id, conversation_id, agent_id, role, content, provider, created_at
                ) VALUES (
                    :message_id, :conversation_id, :agent_id, :role, :content, :provider, :created_at
                )
                """,
                record,
            )
        return record

    def list_messages(self, agent_id: str, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM messages
                WHERE agent_id = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (agent_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_run(
        self,
        *,
        run_id: str,
        scenario_path: str,
        runtime_name: str,
        objective: str,
        phase: str,
        checkpoint: dict[str, Any],
        approvals: list[dict[str, Any]],
    ) -> None:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs (
                    run_id, scenario_path, runtime_name, objective, phase,
                    checkpoint_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    runtime_name = excluded.runtime_name,
                    phase = excluded.phase,
                    checkpoint_json = excluded.checkpoint_json,
                    updated_at = excluded.updated_at
                """,
                (
                    run_id,
                    scenario_path,
                    runtime_name,
                    objective,
                    phase,
                    json.dumps(checkpoint, sort_keys=True),
                    now,
                    now,
                ),
            )
            for packet in approvals:
                connection.execute(
                    """
                    INSERT INTO approvals (
                        approval_id, run_id, task_id, required_level,
                        status, packet_json, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(approval_id) DO UPDATE SET
                        status = excluded.status,
                        packet_json = excluded.packet_json,
                        updated_at = excluded.updated_at
                    """,
                    (
                        packet["approval_id"],
                        run_id,
                        packet["task_id"],
                        packet["required_level"],
                        packet["status"],
                        json.dumps(packet, sort_keys=True),
                        now,
                    ),
                )

    def load_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        record = dict(row)
        record["checkpoint"] = json.loads(record.pop("checkpoint_json"))
        return record

    def list_runs(self, limit: int = 30) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT run_id, scenario_path, runtime_name, objective, phase, created_at, updated_at
                FROM runs
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def latest_completed_state(self) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT checkpoint_json FROM runs
                WHERE phase = 'completed'
                ORDER BY updated_at DESC
                LIMIT 1
                """
            ).fetchone()
        if row is None:
            return None
        checkpoint = json.loads(row["checkpoint_json"])
        return checkpoint["result"].get("committed_state")

    def add_event(
        self, run_id: str, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        created_at = utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO events (run_id, event_type, payload_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (run_id, event_type, json.dumps(payload, sort_keys=True), created_at),
            )
            event_id = cursor.lastrowid
        return {
            "event_id": event_id,
            "run_id": run_id,
            "event_type": event_type,
            "payload": payload,
            "created_at": created_at,
        }

    def list_events(self, run_id: str, after: int = 0) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM events
                WHERE run_id = ? AND event_id > ?
                ORDER BY event_id ASC
                """,
                (run_id, after),
            ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "run_id": row["run_id"],
                "event_type": row["event_type"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
