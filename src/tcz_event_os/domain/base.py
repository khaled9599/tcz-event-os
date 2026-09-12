from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field
from .enums import LifecycleStatus

def utcnow(): return datetime.now(timezone.utc)
class VersionRef(BaseModel):
    version:str; artifact_id:str|None=None; created_at:datetime=Field(default_factory=utcnow); created_by:str|None=None
class BaseEntity(BaseModel):
    model_config=ConfigDict(extra="forbid",validate_assignment=True)
    id:str=Field(default_factory=lambda:str(uuid4())); name:str; status:LifecycleStatus=LifecycleStatus.DRAFT; schema_version:str="0.1"; tags:set[str]=Field(default_factory=set); metadata:dict[str,Any]=Field(default_factory=dict); created_at:datetime=Field(default_factory=utcnow); updated_at:datetime=Field(default_factory=utcnow)
    def touch(self): self.updated_at=utcnow()
