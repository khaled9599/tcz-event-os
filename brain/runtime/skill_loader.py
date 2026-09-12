from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml


class SkillResolutionError(ValueError):
    pass


class SkillLoader:
    def __init__(self, repo_root: str | Path):
        self.repo_root = Path(repo_root)
        registry_path = self.repo_root / "configs" / "skills_registry.yaml"
        matrix_path = self.repo_root / "configs" / "agent_skill_matrix.yaml"
        self.registry = yaml.safe_load(registry_path.read_text()) or {}
        self.matrix = yaml.safe_load(matrix_path.read_text()) or {}

    def _agent_entry(self, agent_id: str) -> dict:
        agents = self.matrix.get("agents", self.matrix)
        entry = agents.get(agent_id, {}) if isinstance(agents, dict) else {}
        if isinstance(entry, list):
            return {"required": entry, "optional": []}
        return entry or {}

    def required_skills(self, agent_id: str) -> list[str]:
        return list(self._agent_entry(agent_id).get("required", []) or [])

    def optional_skills(self, agent_id: str) -> list[str]:
        return list(self._agent_entry(agent_id).get("optional", []) or [])

    def allowed_skills(self, agent_id: str) -> set[str]:
        entry = self._agent_entry(agent_id)
        return set((entry.get("required", []) or []) + (entry.get("optional", []) or []))

    def resolve(self, agent_id: str, required_skills: Iterable[str]) -> list[dict]:
        allowed = self.allowed_skills(agent_id)
        requested = list(dict.fromkeys(required_skills))
        denied = [skill for skill in requested if skill not in allowed]
        if denied:
            raise SkillResolutionError(f"agent {agent_id} is not allowed to load skills: {denied}")

        registry_items = self.registry.get("skills", self.registry)
        resolved: list[dict] = []
        for skill_id in requested:
            item = registry_items.get(skill_id) if isinstance(registry_items, dict) else None
            if item is None and isinstance(registry_items, list):
                item = next((x for x in registry_items if x.get("id") == skill_id or x.get("skill_id") == skill_id), None)
            if item is None:
                raise SkillResolutionError(f"skill {skill_id} missing from registry")
            path = item.get("path") or item.get("source_path")
            if not path:
                raise SkillResolutionError(f"skill {skill_id} has no path")
            skill_path = self.repo_root / path
            if not skill_path.exists():
                raise SkillResolutionError(f"skill {skill_id} points to missing file {path}")
            resolved.append({
                "skill_id": skill_id,
                "path": path,
                "content": skill_path.read_text(),
                "sources": item.get("sources", []),
            })
        return resolved

    def resolve_required(self, agent_id: str) -> list[dict]:
        return self.resolve(agent_id, self.required_skills(agent_id))
