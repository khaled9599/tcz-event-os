from datetime import datetime
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, Field
from tcz_event_os.domain.base import utcnow
from tcz_event_os.domain.enums import ApprovalLevel, Severity, TaskStatus

class ContextPackage(BaseModel):
    task_id:str; project_id:str; target_object_ids:list[str]=Field(default_factory=list); authoritative_state:dict[str,Any]=Field(default_factory=dict); dependencies:list[dict[str,Any]]=Field(default_factory=list); relevant_evidence:list[dict[str,Any]]=Field(default_factory=list); relevant_decisions:list[dict[str,Any]]=Field(default_factory=list); relevant_assumptions:list[dict[str,Any]]=Field(default_factory=list); constraints:list[str]=Field(default_factory=list); excluded_context_notes:list[str]=Field(default_factory=list)
class TaskEnvelope(BaseModel):
    id:str=Field(default_factory=lambda:f"TASK-{uuid4().hex[:8]}"); project_id:str; assigned_agent:str; objective:str; object_ids:list[str]=Field(default_factory=list); inputs:dict[str,Any]=Field(default_factory=dict); constraints:list[str]=Field(default_factory=list); required_outputs:list[str]=Field(default_factory=list); acceptance_criteria:list[str]=Field(default_factory=list); approval_level:ApprovalLevel=ApprovalLevel.L1_ACT_AND_REPORT; dependency_task_ids:list[str]=Field(default_factory=list); status:TaskStatus=TaskStatus.QUEUED; created_at:datetime=Field(default_factory=utcnow)
class EvidenceClaim(BaseModel): statement:str; evidence_ids:list[str]=Field(default_factory=list); confidence:float=Field(ge=0,le=1)
class AgentResult(BaseModel):
    task_id:str; agent_id:str; status:TaskStatus; summary:str; outputs:dict[str,Any]=Field(default_factory=dict); proposed_mutations:list[dict[str,Any]]=Field(default_factory=list); created_artifacts:list[str]=Field(default_factory=list); claims:list[EvidenceClaim]=Field(default_factory=list); assumptions_created:list[dict[str,Any]]=Field(default_factory=list); risks_found:list[dict[str,Any]]=Field(default_factory=list); issues_found:list[dict[str,Any]]=Field(default_factory=list); recommended_next_agents:list[str]=Field(default_factory=list); requires_human_decision:bool=False; notes:list[str]=Field(default_factory=list)
class HandoffEnvelope(BaseModel):
    id:str=Field(default_factory=lambda:f"HANDOFF-{uuid4().hex[:8]}"); task_id:str; from_agent:str; to_agent:str; object_ids:list[str]; objective:str; required_inputs:list[str]=Field(default_factory=list); supplied_inputs:dict[str,Any]=Field(default_factory=dict); constraints:list[str]=Field(default_factory=list); required_outputs:list[str]=Field(default_factory=list); acceptance_criteria:list[str]=Field(default_factory=list); accepted:bool|None=None; rejection_reason:str|None=None
class ReviewFinding(BaseModel): code:str; severity:Severity; message:str; object_ids:list[str]=Field(default_factory=list); remediation:str|None=None
class JudgeResult(BaseModel): task_id:str; reviewer_id:str; passed:bool; score:float=Field(ge=0,le=10); findings:list[ReviewFinding]=Field(default_factory=list); required_rework:list[str]=Field(default_factory=list)
