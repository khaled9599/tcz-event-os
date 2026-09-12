import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
from sample_state import build_sample_state
from tcz_event_os.workflows import propose_change,approve_and_apply_change
state=build_sample_state(); proposed,change,event=propose_change(state,object_id="KANVA-ENT-001",field_path="dimensions.height",new_value=5500,requested_by="creative_lead",reason="Increase entrance presence while preserving approved concept.")
approved,event2=approve_and_apply_change(proposed,change.id,approved_by="authorized_tcz_reviewer")
print(json.dumps({"change_id":change.id,"impact_domains":change.impact_domains,"new_height_mm":approved.installations['KANVA-ENT-001'].dimensions.height.value,"verification":approved.installations['KANVA-ENT-001'].dimensions.height.verification,"decisions":list(approved.decisions)},indent=2,default=str))
