from datetime import datetime
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, Field
from tcz_event_os.domain.base import utcnow
class DomainEvent(BaseModel):
    specversion:str="1.0"; id:str=Field(default_factory=lambda:str(uuid4())); type:str; source:str; subject:str|None=None; time:datetime=Field(default_factory=utcnow); datacontenttype:str="application/json"; dataschema:str="tcz-event-os/0.1"; correlation_id:str|None=None; causation_id:str|None=None; actor:str|None=None; data:dict[str,Any]=Field(default_factory=dict)
