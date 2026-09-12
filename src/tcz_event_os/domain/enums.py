from enum import StrEnum

class LifecycleStatus(StrEnum):
    DRAFT="draft"; PROPOSED="proposed"; IN_REVIEW="in_review"; APPROVED="approved"; IN_PRODUCTION="in_production"; INSTALLED="installed"; VERIFIED="verified"; CLOSED="closed"; REJECTED="rejected"
class VerificationStatus(StrEnum):
    VERIFIED="verified"; MODELLED="modelled"; ASSUMED="assumed"; UNVERIFIED="unverified"; SUPERSEDED="superseded"
class TaskStatus(StrEnum):
    QUEUED="queued"; READY="ready"; IN_PROGRESS="in_progress"; BLOCKED="blocked"; SUBMITTED="submitted"; PASSED="passed"; FAILED="failed"; CANCELLED="cancelled"
class ApprovalLevel(StrEnum):
    L0_AUTONOMOUS="L0_autonomous"; L1_ACT_AND_REPORT="L1_act_and_report"; L2_HUMAN_APPROVAL="L2_human_approval"; L3_QUALIFIED_PROFESSIONAL="L3_qualified_professional"
class Severity(StrEnum):
    LOW="low"; MEDIUM="medium"; HIGH="high"; CRITICAL="critical"
class EvidenceType(StrEnum):
    CLIENT_BRIEF="client_brief"; SITE_MEASUREMENT="site_measurement"; VENUE_DOCUMENT="venue_document"; VENDOR_QUOTE="vendor_quote"; VENDOR_SPEC="vendor_spec"; TECHNICAL_DRAWING="technical_drawing"; PHOTO_VIDEO="photo_video"; MODEL_OUTPUT="model_output"; AGENT_INFERENCE="agent_inference"; HUMAN_DECISION="human_decision"; REGULATION="regulation"; FILE="file"
class RelationType(StrEnum):
    LOCATED_IN="located_in"; CONTAINS="contains"; DEPENDS_ON="depends_on"; POWERED_BY="powered_by"; RIGGED_BY="rigged_by"; CONTROLLED_BY="controlled_by"; SUPPLIED_BY="supplied_by"; FABRICATED_BY="fabricated_by"; APPROVED_BY="approved_by"; COSTS_AGAINST="costs_against"; SCHEDULED_FOR="scheduled_for"; REFERENCES="references"; AFFECTS="affects"
