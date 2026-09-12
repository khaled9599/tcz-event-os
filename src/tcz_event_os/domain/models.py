from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, Field
from .base import BaseEntity, VersionRef, utcnow
from .enums import *

class Measurement(BaseModel):
    value:float; unit:str; verification:VerificationStatus=VerificationStatus.UNVERIFIED; evidence_ids:list[str]=Field(default_factory=list)
class Dimensions(BaseModel):
    width:Measurement|None=None; height:Measurement|None=None; depth:Measurement|None=None; clear_width:Measurement|None=None; clear_height:Measurement|None=None
class Relation(BaseModel):
    subject_id:str; predicate:RelationType; object_id:str; metadata:dict[str,Any]=Field(default_factory=dict)
class Client(BaseEntity): contacts:list[str]=Field(default_factory=list)
class Project(BaseEntity):
    client_id:str|None=None; event_date:datetime|None=None; currency:str="EGP"; current_stage:str="discovery"; brief_version:str|None=None
class Venue(BaseEntity): address_label:str|None=None; capacity:int|None=None; venue_rules:list[str]=Field(default_factory=list)
class Zone(BaseEntity): venue_id:str; capacity:int|None=None; dimensions:Dimensions|None=None
class Experience(BaseEntity): creative_intent:str; zone_ids:list[str]=Field(default_factory=list)
class Material(BaseEntity): specification:str|None=None; finish:str|None=None; supplier_id:str|None=None
class Installation(BaseEntity):
    project_id:str; zone_id:str; creative_intent:str|None=None; dimensions:Dimensions=Field(default_factory=Dimensions); material_ids:list[str]=Field(default_factory=list); asset_ids:list[str]=Field(default_factory=list); design_version:VersionRef|None=None; geometry_version:VersionRef|None=None; visual_version:VersionRef|None=None; production_status:LifecycleStatus=LifecycleStatus.DRAFT; brand_status:LifecycleStatus=LifecycleStatus.DRAFT; open_issue_ids:list[str]=Field(default_factory=list)
class Asset(BaseEntity): asset_type:str; owner_type:str="tcz"; location:str|None=None; condition:str|None=None; reusable:bool=True
class AVSystem(BaseEntity): project_id:str; zone_id:str|None=None; system_type:str; specification:dict[str,Any]=Field(default_factory=dict); connected_load_kw:float|None=None; backup_strategy:str|None=None
class RiggingSystem(BaseEntity): project_id:str; zone_id:str|None=None; suspended_load_kg:float|None=None; trim_height_m:float|None=None; hanging_points:list[dict[str,Any]]=Field(default_factory=list); professional_signoff_required:bool=True
class ElectricalSystem(BaseEntity): project_id:str; connected_load_kw:float|None=None; demand_load_kw:float|None=None; supply_description:str|None=None; circuits:list[dict[str,Any]]=Field(default_factory=list); redundancy:str|None=None
class ShowCue(BaseEntity): project_id:str; sequence:int; trigger:str; actions:list[dict[str,Any]]=Field(default_factory=list); fallback:str|None=None
class HospitalityPlan(BaseEntity): project_id:str; guest_count:int; vip_count:int=0; crew_count:int=0; service_points:list[dict[str,Any]]=Field(default_factory=list); requirements:list[str]=Field(default_factory=list)
class AccessibilityRequirement(BaseEntity): project_id:str; zone_id:str|None=None; requirement_type:str; constraint:str; evidence_ids:list[str]=Field(default_factory=list)
class WarehouseItem(BaseEntity): sku:str; category:str; quantity_total:float=0; quantity_available:float=0; warehouse_location:str|None=None; maintenance_due:bool=False
class Vendor(BaseEntity): categories:list[str]=Field(default_factory=list); capabilities:list[str]=Field(default_factory=list); lead_time_days:float|None=None; quality_score:float|None=Field(default=None,ge=0,le=100); reliability_score:float|None=Field(default=None,ge=0,le=100); notes:list[str]=Field(default_factory=list)
class QuantityItem(BaseEntity): project_id:str; object_id:str; description:str; quantity:Decimal; unit:str; waste_factor:Decimal=Decimal("0")
class CostItem(BaseEntity):
    project_id:str; cost_code:str; description:str; quantity:Decimal=Decimal("1"); unit_cost:Decimal=Decimal("0"); committed_cost:Decimal=Decimal("0"); actual_cost:Decimal=Decimal("0")
    @property
    def forecast(self): return self.quantity*self.unit_cost
class Risk(BaseEntity): project_id:str; probability:float=Field(ge=0,le=1); impact:Severity; owner:str|None=None; mitigation:str|None=None
class Issue(BaseEntity): project_id:str; severity:Severity; object_ids:list[str]=Field(default_factory=list); description:str; owner:str|None=None
class Assumption(BaseEntity): project_id:str; statement:str; verification:VerificationStatus=VerificationStatus.ASSUMED; affected_object_ids:list[str]=Field(default_factory=list)
class Decision(BaseEntity): project_id:str; statement:str; reason:str|None=None; decided_by:str; affected_object_ids:list[str]=Field(default_factory=list); locked:bool=False
class ChangeRequest(BaseEntity): project_id:str; object_id:str; field_path:str; old_value:Any=None; proposed_value:Any; reason:str|None=None; requested_by:str; impact_domains:list[str]=Field(default_factory=list); approval_level:ApprovalLevel=ApprovalLevel.L2_HUMAN_APPROVAL
class Approval(BaseEntity): project_id:str; subject_id:str; approval_level:ApprovalLevel; approved:bool|None=None; approver:str|None=None; notes:str|None=None
class Evidence(BaseEntity): project_id:str; evidence_type:EvidenceType; source_uri:str|None=None; statement:str; verification:VerificationStatus; confidence:float=Field(ge=0,le=1); supports_object_ids:list[str]=Field(default_factory=list)
class FileArtifact(BaseEntity): project_id:str; artifact_type:str; path_or_uri:str; version:str; content_hash:str|None=None; derived_from_ids:list[str]=Field(default_factory=list)
class Task(BaseEntity): project_id:str; assigned_agent:str; object_id:str|None=None; objective:str; task_status:TaskStatus=TaskStatus.QUEUED; inputs:dict[str,Any]=Field(default_factory=dict); constraints:list[str]=Field(default_factory=list); required_outputs:list[str]=Field(default_factory=list); acceptance_criteria:list[str]=Field(default_factory=list); dependency_task_ids:list[str]=Field(default_factory=list)
class CanonicalEventState(BaseModel):
    project:Project; clients:dict[str,Client]=Field(default_factory=dict); venues:dict[str,Venue]=Field(default_factory=dict); zones:dict[str,Zone]=Field(default_factory=dict); experiences:dict[str,Experience]=Field(default_factory=dict); installations:dict[str,Installation]=Field(default_factory=dict); materials:dict[str,Material]=Field(default_factory=dict); assets:dict[str,Asset]=Field(default_factory=dict); av_systems:dict[str,AVSystem]=Field(default_factory=dict); rigging_systems:dict[str,RiggingSystem]=Field(default_factory=dict); electrical_systems:dict[str,ElectricalSystem]=Field(default_factory=dict); show_cues:dict[str,ShowCue]=Field(default_factory=dict); hospitality_plans:dict[str,HospitalityPlan]=Field(default_factory=dict); accessibility_requirements:dict[str,AccessibilityRequirement]=Field(default_factory=dict); warehouse_items:dict[str,WarehouseItem]=Field(default_factory=dict); vendors:dict[str,Vendor]=Field(default_factory=dict); quantities:dict[str,QuantityItem]=Field(default_factory=dict); costs:dict[str,CostItem]=Field(default_factory=dict); risks:dict[str,Risk]=Field(default_factory=dict); issues:dict[str,Issue]=Field(default_factory=dict); assumptions:dict[str,Assumption]=Field(default_factory=dict); decisions:dict[str,Decision]=Field(default_factory=dict); changes:dict[str,ChangeRequest]=Field(default_factory=dict); approvals:dict[str,Approval]=Field(default_factory=dict); evidence:dict[str,Evidence]=Field(default_factory=dict); artifacts:dict[str,FileArtifact]=Field(default_factory=dict); tasks:dict[str,Task]=Field(default_factory=dict); relations:list[Relation]=Field(default_factory=list); updated_at:datetime=Field(default_factory=utcnow)
