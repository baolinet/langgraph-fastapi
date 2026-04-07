from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field

from agents.graphs.base_graph import build_agent_graph
from agents.core.registry import AgentRegistry
from agents.core.state import build_initial_state


class AgentRunRequest(BaseModel):
    agent_type: str = Field(..., description="Registered agent type")
    user_input: str = Field(..., min_length=1, description="User task or question")
    conversation_id: str = Field(..., min_length=1)
    user_context: dict[str, Any] = Field(default_factory=dict)
    messages: list[dict[str, str]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    agent_type: str
    conversation_id: str
    answer: str
    summary: str
    structured_data: dict[str, Any] = Field(default_factory=dict)
    citations: list[str] = Field(default_factory=list)
    risk_level: str = "low"
    risk_flags: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    needs_human_handoff: bool = False
    prompt_preview: str = ""


class GraphRunner:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def list_agent_types(self) -> list[str]:
        return self.registry.list_types()

    def run(self, request: AgentRunRequest) -> AgentRunResponse:
        profile = self.registry.get(request.agent_type)
        graph = self._get_graph()
        state = build_initial_state(
            agent_type=request.agent_type,
            user_input=request.user_input,
            conversation_id=request.conversation_id,
            user_context=request.user_context,
            messages=request.messages,
            metadata=request.metadata,
        )
        final_state = graph.invoke({"state": state, "profile": profile})
        resolved_state = final_state["state"]
        return AgentRunResponse(
            agent_type=request.agent_type,
            conversation_id=request.conversation_id,
            answer=resolved_state["final_response"],
            summary=resolved_state["structured_output"].get("summary", ""),
            structured_data=resolved_state["structured_output"],
            citations=resolved_state.get("citations", []),
            risk_level=resolved_state.get("risk_level", "low"),
            risk_flags=resolved_state.get("risk_flags", []),
            next_actions=resolved_state.get("next_actions", []),
            needs_human_handoff=resolved_state.get("needs_human_handoff", False),
            prompt_preview=profile.display_name,
        )

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_graph():
        return build_agent_graph()
