from __future__ import annotations

from typing import Any, Literal, TypedDict


RiskLevel = Literal["low", "medium", "high"]
IntentType = Literal[
    "qa",
    "content_generation",
    "analysis",
    "moderation",
    "support",
    "audit",
    "unknown",
]


class ToolCall(TypedDict, total=False):
    name: str
    arguments: dict[str, Any]


class ToolResult(TypedDict, total=False):
    name: str
    success: bool
    payload: dict[str, Any]
    error: str
