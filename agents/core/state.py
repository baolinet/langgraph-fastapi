from __future__ import annotations

from typing import Any, TypedDict

from agents.core.types import IntentType, RiskLevel, ToolCall, ToolResult


class AgentState(TypedDict, total=False):
    agent_type: str
    conversation_id: str
    user_input: str
    user_context: dict[str, Any]
    messages: list[dict[str, str]]
    intent: IntentType
    context: dict[str, Any]
    tool_calls: list[ToolCall]
    tool_results: list[ToolResult]
    draft_response: str
    final_response: str
    structured_output: dict[str, Any]
    citations: list[str]
    risk_level: RiskLevel
    risk_flags: list[str]
    needs_human_handoff: bool
    next_actions: list[str]
    metadata: dict[str, Any]


def build_initial_state(
    *,
    agent_type: str,
    user_input: str,
    conversation_id: str,
    user_context: dict[str, Any] | None = None,
    messages: list[dict[str, str]] | None = None,
    metadata: dict[str, Any] | None = None,
) -> AgentState:
    return AgentState(
        agent_type=agent_type,
        conversation_id=conversation_id,
        user_input=user_input.strip(),
        user_context=user_context or {},
        messages=messages or [],
        intent="unknown",
        context={},
        tool_calls=[],
        tool_results=[],
        draft_response="",
        final_response="",
        structured_output={},
        citations=[],
        risk_level="low",
        risk_flags=[],
        needs_human_handoff=False,
        next_actions=[],
        metadata=metadata or {},
    )
