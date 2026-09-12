from brain.contracts.runtime_contracts import ApprovalPacket, RunPhase, SideEffectClass
from brain.runtime.approval_policy import approval_required, can_execute
from brain.runtime.side_effect_guard import DuplicateSideEffect, InMemorySideEffectLedger
from brain.runtime.workflow_engine import IllegalTransition, require_transition


def test_workflow_blocks_illegal_transition():
    try:
        require_transition(RunPhase.DISCOVER, RunPhase.EXECUTE)
        assert False, "expected IllegalTransition"
    except IllegalTransition:
        pass


def test_workflow_allows_plan_after_discover():
    assert require_transition(RunPhase.DISCOVER, RunPhase.PLAN) == RunPhase.PLAN


def test_side_effect_approval_escalates():
    assert approval_required("L0", SideEffectClass.FINANCIAL) == "L2"
    assert approval_required("L1_act_and_report", SideEffectClass.SAFETY_CRITICAL) == "L3"


def test_l3_requires_explicit_approval():
    packet = ApprovalPacket(
        run_id="RUN-1",
        task_id="T-1",
        requested_action="approve structural load",
        required_level="L3",
    )
    assert can_execute(packet) is False
    packet.status = "approved"
    assert can_execute(packet) is True


def test_side_effect_ledger_blocks_duplicate_execution():
    ledger = InMemorySideEffectLedger()
    kwargs = dict(
        run_id="RUN-1",
        task_id="T-2",
        tool_name="vendor_email",
        operation="send_rfq",
        payload={"vendor": "V-1", "rfq": "RFQ-1"},
        side_effect_class=SideEffectClass.EXTERNAL_COMMUNICATION,
    )
    ledger.reserve(**kwargs)
    try:
        ledger.reserve(**kwargs)
        assert False, "expected DuplicateSideEffect"
    except DuplicateSideEffect:
        pass
