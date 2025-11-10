from typing import Protocol, Dict
from app.models import Task, Result

class Agent(Protocol):
    name: str
    capability: str
    def run(self, task: Task) -> Result: ...

_registry: Dict[str, Agent] = {}

def register(agent: Agent):
    _registry[agent.capability] = agent

def get_agent(capability: str) -> Agent:
    if capability not in _registry:
        raise KeyError(f"No agent for capability: {capability}")
    return _registry[capability]
