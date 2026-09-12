from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class RunPhase(str, Enum):
    DISCOVER = "discover"
    PLAN = "plan"
    VALIDATE = "validate"
    APPROVE = "approve"
    EXECUTE = "execute"
    VERIFY = "verify"
    COMMIT = "commit"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FailureClass(str, Enum):
    TRANSIENT_TOOL = "transient_tool_failure"
    INVALID_OUTPUT = "invalid_output"
    MISSING_CONTEXT = "missing_context"
    PERMISSION = "permission_violation"
    QUALITY_GATE = "failed_quality_gate"
    CONFLICTING_STATE = "conflicting_state"
    EXTERNAL_DEPENDENCY = "external_dependency_unavailable"
    HUMAN_REJECTION = "human_rejection"


class SideEffectClass(str, Enum):
    NONE = "none"
    REVERSIBLE = "reversible"
    EXTERNAL_COMMUNICATION = "external_communication"
    FINANCIAL = "financial"
    DESTRUCTIVE = "destructive"
    SAFETY_CRITICAL = "safety_critical"


class TaskNode(BaseModel):
    task_id: str = Field(default_factory=lambda: f"T-{uuid4().hex[:10]}")
    objective: str
    object_id: str | None = None
    assigned_agent: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    side_effect_class: SideEffectClass = SideEffectClass.NONE
    required_approval_level: str = "L0"
    status: Literal[
        "pending", "ready", "running", "blocked", "awaiting_approval",
        "completed", "failed", "cancelled"
    ] = "pending"


class TaskGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: f"TG-{uuid4().hex[:10]}")
    objective: str
    nodes: list[TaskNode]


class SkillActivation(BaseModel):
    skill_id: str
    version: str | None = None
    reason: str
    source_path: str


class ApprovalPacket(BaseModel):
    approval_id: str = Field(default_factory=lambda: f"APR-{uuid4().hex[:10]}")
    run_id: str
    task_id: str
    requested_action: str
    required_level: str
    before: dict[str, Any] = Field(default_factory=dict)
    after: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    impacts: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    cost_delta: float | None = None
    schedule_delta_hours: float | None = None
    recommendation: str | None = None
    status: Literal["pending", "approved", "rejected", "revision_requested"] = "pending"


class SideEffectRecord(BaseModel):
    idempotency_key: str
    run_id: str
    task_id: str
    tool_name: str
    operation: str
    side_effect_class: SideEffectClass
    request_hash: str
    status: Literal["reserved", "executed", "failed", "reversed"] = "reserved"
    external_reference: str | None = None


class ConflictPacket(BaseModel):
    conflict_id: str = Field(default_factory=lambda: f"CF-{uuid4().hex[:10]}")
    run_id: str
    object_id: str | None = None
    claims: list[dict[str, Any]]
    evidence_refs: list[str] = Field(default_factory=list)
    affected_domains: list[str] = Field(default_factory=list)
    cost_impact: float | None = None
    schedule_impact_hours: float | None = None
    risk_summary: list[str] = Field(default_factory=list)
    required_decision_level: str
    decision_owner: str


class RunTrace(BaseModel):
    run_id: str = Field(default_factory=lambda: f"RUN-{uuid4().hex[:12]}")
    objective: str
    phase: RunPhase = RunPhase.DISCOVER
    task_graph_id: str | None = None
    context_package_ids: list[str] = Field(default_factory=list)
    agents_used: list[str] = Field(default_factory=list)
    skills_loaded: list[SkillActivation] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    approval_ids: list[str] = Field(default_factory=list)
    judge_results: list[dict[str, Any]] = Field(default_factory=list)
    checkpoint_ref: str | None = None
    retry_count: int = 0
    failure_class: FailureClass | None = None
    failure_detail: str | None = None
