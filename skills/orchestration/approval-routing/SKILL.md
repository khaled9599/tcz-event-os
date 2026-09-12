# Approval Routing

Route decisions according to authority level and risk.

## Levels
- L0: automatic, reversible, low impact.
- L1: execute and report.
- L2: TCZ/client human approval before state mutation.
- L3: qualified external professional approval.

## Procedure
1. Identify affected object and proposed action.
2. Evaluate budget, client-facing, safety, structural, electrical and contractual impact.
3. Select highest applicable level.
4. Prevent self-approval when producer and approver must be independent.
5. Record approver, decision, timestamp, evidence and resulting state transition.
6. Expired or superseded approvals must not be reused.

## Output
approval_level, approver_role, gate, blocking_status, evidence_required.

Informed by durable human-in-the-loop approval patterns reviewed from Temporal Agent Harness.
