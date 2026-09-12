from pathlib import Path
import sys
EXAMPLES=Path(__file__).resolve().parents[1]/"examples"/"jotun_kanva"; sys.path.insert(0,str(EXAMPLES))
from sample_state import build_sample_state
from tcz_event_os.workflows import propose_change,approve_and_apply_change,infer_impact_domains
from tcz_event_os.domain.enums import VerificationStatus
def test_impact():
    d=infer_impact_domains("dimensions.height"); assert "rigging" in d and "cost" in d and "blender" in d
def test_propose_before_mutate():
    s=build_sample_state(); p,c,_=propose_change(s,object_id="KANVA-ENT-001",field_path="dimensions.height",new_value=5500,requested_by="test"); assert s.installations["KANVA-ENT-001"].dimensions.height.value==4200 and p.installations["KANVA-ENT-001"].dimensions.height.value==4200
def test_approval_invalidates_measurement_verification():
    s=build_sample_state(); p,c,_=propose_change(s,object_id="KANVA-ENT-001",field_path="dimensions.height",new_value=5500,requested_by="test"); a,_=approve_and_apply_change(p,c.id,approved_by="reviewer"); assert a.installations["KANVA-ENT-001"].dimensions.height.value==5500 and a.installations["KANVA-ENT-001"].dimensions.height.verification==VerificationStatus.UNVERIFIED
