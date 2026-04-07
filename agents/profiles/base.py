from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentProfile:
    agent_type: str
    display_name: str
    description: str
    domain: str
    capabilities: tuple[str, ...]
    output_sections: tuple[str, ...]
    constraints: tuple[str, ...]
    default_tools: tuple[str, ...] = ()
    default_next_actions: list[str] = field(default_factory=lambda: ["review", "confirm"])
    llm_profile: str = "default"
    model_config: dict[str, Any] = field(default_factory=dict)
    enable_intent_classification: bool = True
    enable_tool_routing: bool | None = None
    enable_specialist: bool | None = None
    enable_safety_check: bool | None = None

    def build_specialist_notes(self, intent: str) -> str:
        return f"{self.display_name} 针对 {intent} 场景应用岗位专属规则。"

    def should_classify_intent(self) -> bool:
        return self.enable_intent_classification

    def should_route_tools(self) -> bool:
        if self.enable_tool_routing is not None:
            return self.enable_tool_routing
        return bool(self.default_tools)

    def should_use_specialist(self) -> bool:
        if self.enable_specialist is not None:
            return self.enable_specialist
        return False

    def should_run_safety_check(self) -> bool:
        if self.enable_safety_check is not None:
            return self.enable_safety_check
        return False
