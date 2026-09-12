from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from brain.contracts.runtime_contracts import SideEffectClass, SideEffectRecord


class DuplicateSideEffect(RuntimeError):
    pass


@dataclass
class InMemorySideEffectLedger:
    records: dict[str, SideEffectRecord] = field(default_factory=dict)

    @staticmethod
    def make_key(run_id: str, task_id: str, tool_name: str, operation: str, payload: dict[str, Any]) -> tuple[str, str]:
        normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        request_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        raw = f"{run_id}|{task_id}|{tool_name}|{operation}|{request_hash}"
        key = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return key, request_hash

    def reserve(
        self,
        *,
        run_id: str,
        task_id: str,
        tool_name: str,
        operation: str,
        payload: dict[str, Any],
        side_effect_class: SideEffectClass,
    ) -> SideEffectRecord:
        key, request_hash = self.make_key(run_id, task_id, tool_name, operation, payload)
        existing = self.records.get(key)
        if existing and existing.status in {"reserved", "executed"}:
            raise DuplicateSideEffect(f"side effect already reserved/executed: {key}")
        record = SideEffectRecord(
            idempotency_key=key,
            run_id=run_id,
            task_id=task_id,
            tool_name=tool_name,
            operation=operation,
            side_effect_class=side_effect_class,
            request_hash=request_hash,
        )
        self.records[key] = record
        return record

    def mark_executed(self, key: str, external_reference: str | None = None) -> SideEffectRecord:
        record = self.records[key]
        record.status = "executed"
        record.external_reference = external_reference
        return record

    def mark_failed(self, key: str) -> SideEffectRecord:
        record = self.records[key]
        record.status = "failed"
        return record
