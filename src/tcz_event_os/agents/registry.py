from pathlib import Path
import yaml
from .spec import AgentSpec
class AgentRegistry:
    def __init__(self): self._specs={}
    def add(self,spec):
        if spec.id in self._specs: raise ValueError(f"Duplicate agent id: {spec.id}")
        self._specs[spec.id]=spec
    def get(self,agent_id): return self._specs[agent_id]
    def all(self): return list(self._specs.values())
    @classmethod
    def from_directory(cls,path):
        reg=cls()
        for p in sorted(Path(path).glob("*.yaml")): reg.add(AgentSpec.model_validate(yaml.safe_load(p.read_text())))
        return reg
