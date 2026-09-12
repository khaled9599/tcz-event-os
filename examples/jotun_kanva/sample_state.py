from datetime import datetime
from tcz_event_os.domain.enums import *
from tcz_event_os.domain.models import *
def build_sample_state():
    p=Project(id="JOTUN-KANVA-2026",name="Jotun Kanva Launch",client_id="JOTUN",event_date=datetime(2026,10,25),currency="EGP",current_stage="design_development",brief_version="v04",status=LifecycleStatus.IN_REVIEW)
    c=Client(id="JOTUN",name="Jotun"); v=Venue(id="VENUE-MAP",name="Mohammed Ali Palace",capacity=500,status=LifecycleStatus.APPROVED); z=Zone(id="ZONE-GARDEN-ENTRANCE",name="Garden Entrance",venue_id=v.id,status=LifecycleStatus.APPROVED)
    e=Evidence(id="EVD-HEIGHT-001",name="Entrance baseline height",project_id=p.id,evidence_type=EvidenceType.HUMAN_DECISION,statement="Current approved design baseline uses 4200 mm entrance height.",verification=VerificationStatus.VERIFIED,confidence=1.0,supports_object_ids=["KANVA-ENT-001"],status=LifecycleStatus.APPROVED)
    i=Installation(id="KANVA-ENT-001",name="Main Entrance",project_id=p.id,zone_id=z.id,creative_intent="Transition guests into The Living KANVAS.",dimensions=Dimensions(width=Measurement(value=6000,unit="mm",verification=VerificationStatus.VERIFIED),height=Measurement(value=4200,unit="mm",verification=VerificationStatus.VERIFIED,evidence_ids=[e.id]),clear_width=Measurement(value=4000,unit="mm",verification=VerificationStatus.VERIFIED)),status=LifecycleStatus.IN_REVIEW,production_status=LifecycleStatus.IN_REVIEW,brand_status=LifecycleStatus.APPROVED)
    return CanonicalEventState(project=p,clients={c.id:c},venues={v.id:v},zones={z.id:z},installations={i.id:i},evidence={e.id:e},relations=[Relation(subject_id=i.id,predicate=RelationType.LOCATED_IN,object_id=z.id),Relation(subject_id=z.id,predicate=RelationType.LOCATED_IN,object_id=v.id)])
