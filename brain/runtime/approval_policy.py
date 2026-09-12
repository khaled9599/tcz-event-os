from __future__ import annotations

from brain.contracts.runtime_contracts import ApprovalPacket, SideEffectClass


_APPROVAL_RANK = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}

_SIDE_EFFECT_MIN_LEVEL = {
    SideEffectClass.NONE: "L0",
    SideEffectClass.REVERSIBLE: "L1",
    SideEffectClass.EXTERNAL_COMMUNICATION: "L2",
    SideEffectClass.FINANCIAL: "L2",
    SideEffectClass.DESTRUCTIVE: "L2",
    SideEffectClass.SAFETY_CRITICAL: "L3",
}


def normalize_level(level: str) -> str:
    token = level.split("_", 1)[0]
    if token not in _APPROVAL_RANK:
        raise ValueError(f"unknown approval level: {level}")
    return token


def required_level_for_side_effect(side_effect_class: SideEffectClass) -> str:
    return _SIDE_EFFECT_MIN_LEVEL[side_effect_class]


def max_level(*levels: str) -> str:
    normalized = [normalize_level(level) for level in levels]
    return max(normalized, key=lambda x: _APPROVAL_RANK[x])


def approval_required(task_level: str, side_effect_class: SideEffectClass) -> str:
    return max_level(task_level, required_level_for_side_effect(side_effect_class))


def can_execute(packet: ApprovalPacket) -> bool:
    required = normalize_level(packet.required_level)
    if required in {"L0", "L1"}:
        return packet.status in {"pending", "approved"}
    return packet.status == "approved"
