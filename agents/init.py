"""Public entrypoints for the agents package."""

from agents.core.registry import AgentRegistry
from agents.core.runner import GraphRunner
from agents.profiles import register_profiles


def build_agent_runner() -> GraphRunner:
    registry = AgentRegistry()
    register_profiles(registry)
    return GraphRunner(registry=registry)


def get_available_agent_types() -> list[str]:
    runner = build_agent_runner()
    return runner.list_agent_types()
