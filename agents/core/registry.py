from __future__ import annotations

from dataclasses import dataclass, field

from agents.profiles.base import AgentProfile


@dataclass
class AgentRegistry:
    _profiles: dict[str, AgentProfile] = field(default_factory=dict)

    def register(self, profile: AgentProfile) -> None:
        self._profiles[profile.agent_type] = profile

    def get(self, agent_type: str) -> AgentProfile:
        try:
            return self._profiles[agent_type]
        except KeyError as exc:
            available = ", ".join(sorted(self._profiles))
            raise ValueError(
                f"Unknown agent type: {agent_type}. Available types: {available}"
            ) from exc

    def list_types(self) -> list[str]:
        return sorted(self._profiles)
