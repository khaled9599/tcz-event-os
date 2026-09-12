from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from brain.contracts.runtime_contracts import RunPhase


_ALLOWED_TRANSITIONS: dict[RunPhase, set[RunPhase]] = {
    RunPhase.DISCOVER: {RunPhase.PLAN, RunPhase.FAILED, RunPhase.CANCELLED},
    RunPhase.PLAN: {RunPhase.VALIDATE, RunPhase.FAILED, RunPhase.CANCELLED},
    RunPhase.VALIDATE: {RunPhase.APPROVE, RunPhase.EXECUTE, RunPhase.FAILED, RunPhase.CANCELLED},
    RunPhase.APPROVE: {RunPhase.EXECUTE, RunPhase.PLAN, RunPhase.CANCELLED, RunPhase.FAILED},
    RunPhase.EXECUTE: {RunPhase.VERIFY, RunPhase.FAILED, RunPhase.CANCELLED},
    RunPhase.VERIFY: {RunPhase.COMMIT, RunPhase.PLAN, RunPhase.FAILED, RunPhase.CANCELLED},
    RunPhase.COMMIT: {RunPhase.COMPLETED, RunPhase.FAILED},
    RunPhase.COMPLETED: set(),
    RunPhase.FAILED: {RunPhase.PLAN, RunPhase.EXECUTE, RunPhase.CANCELLED},
    RunPhase.CANCELLED: set(),
}


class IllegalTransition(ValueError):
    pass


@dataclass(frozen=True)
class TransitionDecision:
    current: RunPhase
    requested: RunPhase
    allowed: bool
    reason: str


def allowed_next(phase: RunPhase) -> set[RunPhase]:
    return set(_ALLOWED_TRANSITIONS[phase])


def validate_transition(current: RunPhase, requested: RunPhase) -> TransitionDecision:
    allowed = requested in _ALLOWED_TRANSITIONS[current]
    reason = "allowed" if allowed else f"{current.value} cannot transition to {requested.value}"
    return TransitionDecision(current=current, requested=requested, allowed=allowed, reason=reason)


def require_transition(current: RunPhase, requested: RunPhase) -> RunPhase:
    decision = validate_transition(current, requested)
    if not decision.allowed:
        raise IllegalTransition(decision.reason)
    return requested


def require_all_completed(statuses: Iterable[str]) -> None:
    incomplete = [status for status in statuses if status != "completed"]
    if incomplete:
        raise IllegalTransition(f"cannot commit with incomplete tasks: {incomplete}")
