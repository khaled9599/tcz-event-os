from copy import deepcopy
from tcz_event_os.domain.enums import ApprovalLevel, LifecycleStatus, VerificationStatus
from tcz_event_os.domain.models import ChangeRequest, Decision
from tcz_event_os.protocols.events import DomainEvent
from .impact import infer_impact_domains

def propose_change(state,*,object_id,field_path,new_value,requested_by,reason=None,approval_level=ApprovalLevel.L2_HUMAN_APPROVAL):
    obj=state.installations[object_id]; target=obj
    for part in field_path.split('.'): target=getattr(target,part)
    old=getattr(target,'value',target)
    change=ChangeRequest(id=f"CHG-{len(state.changes)+1:03d}",name=f"Change {object_id} {field_path}",project_id=state.project.id,object_id=object_id,field_path=field_path,old_value=old,proposed_value=new_value,reason=reason,requested_by=requested_by,impact_domains=infer_impact_domains(field_path),approval_level=approval_level,status=LifecycleStatus.PROPOSED)
    new_state=deepcopy(state); new_state.changes[change.id]=change
    event=DomainEvent(type="change.proposed",source="tcz-event-os/change-workflow",subject=object_id,actor=requested_by,data={"change_id":change.id,"field_path":field_path,"old_value":old,"proposed_value":new_value,"impact_domains":change.impact_domains})
    return new_state,change,event

def approve_and_apply_change(state,change_id,*,approved_by,reason=None):
    new_state=deepcopy(state); change=new_state.changes[change_id]; obj=new_state.installations[change.object_id]; parts=change.field_path.split('.'); target=obj
    for part in parts[:-1]: target=getattr(target,part)
    existing=getattr(target,parts[-1])
    if hasattr(existing,'value') and isinstance(change.proposed_value,(int,float)):
        existing.value=change.proposed_value; existing.verification=VerificationStatus.UNVERIFIED
    else: setattr(target,parts[-1],change.proposed_value)
    obj.touch(); change.status=LifecycleStatus.APPROVED
    decision=Decision(id=f"DEC-{len(new_state.decisions)+1:03d}",name=f"Approve {change.id}",project_id=new_state.project.id,statement=f"Approved {change.field_path} = {change.proposed_value} for {change.object_id}",reason=reason or change.reason,decided_by=approved_by,affected_object_ids=[change.object_id],locked=True,status=LifecycleStatus.APPROVED)
    new_state.decisions[decision.id]=decision
    return new_state,DomainEvent(type="change.approved_applied",source="tcz-event-os/change-workflow",subject=change.object_id,actor=approved_by,data={"change_id":change.id,"decision_id":decision.id,"impact_domains":change.impact_domains})
