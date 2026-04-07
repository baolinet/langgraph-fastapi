from __future__ import annotations

from copy import deepcopy
from typing import Any

from agents.core.llm import create_chat_model, get_llm_config
from agents.core.state import AgentState
from agents.profiles.base import AgentProfile


def load_profile_node(payload: dict[str, Any]) -> dict[str, Any]:
    state: AgentState = deepcopy(payload["state"])
    profile: AgentProfile = payload["profile"]
    state["context"]["profile"] = profile.agent_type
    state["context"]["capabilities"] = profile.capabilities
    return {"state": state, "profile": profile}


def preprocess_input_node(payload: dict[str, Any]) -> dict[str, Any]:
    state: AgentState = deepcopy(payload["state"])
    state["user_input"] = " ".join(state["user_input"].split())
    state["messages"] = state.get("messages", [])[-10:]
    return {**payload, "state": state}


def classify_intent_node(payload: dict[str, Any]) -> dict[str, Any]:
    state: AgentState = deepcopy(payload["state"])
    profile: AgentProfile = payload["profile"]
    lowered = state["user_input"].lower()
    if profile.domain == "moderation":
        intent = "moderation"
    elif profile.domain == "audit":
        intent = "audit"
    elif profile.domain in {"support", "it"}:
        intent = "support"
    elif any(token in lowered for token in ["分析", "report", "指标", "trend"]):
        intent = "analysis"
    elif any(token in lowered for token in ["写", "生成", "copy", "post"]):
        intent = "content_generation"
    else:
        intent = "qa"
    state["intent"] = intent
    return {**payload, "state": state}


def route_tools_node(payload: dict[str, Any]) -> dict[str, Any]:
    state: AgentState = deepcopy(payload["state"])
    profile: AgentProfile = payload["profile"]
    state["tool_calls"] = [
        {"name": tool_name, "arguments": {"conversation_id": state["conversation_id"]}}
        for tool_name in profile.default_tools
    ]
    return {**payload, "state": state}


def execute_task_node(payload: dict[str, Any]) -> dict[str, Any]:
    state: AgentState = deepcopy(payload["state"])
    profile: AgentProfile = payload["profile"]
    prompt = _render_task_prompt(profile, state)
    llm_config = get_llm_config(profile)
    try:
        llm = create_chat_model(profile)
        response = llm.invoke(prompt)
    except Exception as exc:
        raise RuntimeError(
            f"LLM invocation failed for agent '{profile.agent_type}' "
            f"with profile '{llm_config.get('llm_profile', 'default')}': {exc}"
        ) from exc

    answer = getattr(response, "content", str(response))
    state["draft_response"] = answer
    state["structured_output"] = {
        "prompt": prompt,
        "agent_type": profile.agent_type,
        "llm_config": _safe_llm_config(llm_config),
    }
    return {**payload, "state": state}


def specialist_node(payload: dict[str, Any]) -> dict[str, Any]:
    state: AgentState = deepcopy(payload["state"])
    profile: AgentProfile = payload["profile"]
    specialist_notes = profile.build_specialist_notes(state["intent"])
    state["structured_output"]["specialist_notes"] = specialist_notes
    state["draft_response"] += f"\n特色能力: {specialist_notes}"
    return {**payload, "state": state}


def safety_check_node(payload: dict[str, Any]) -> dict[str, Any]:
    state: AgentState = deepcopy(payload["state"])
    profile: AgentProfile = payload["profile"]
    flags = []
    if profile.should_run_safety_check():
        flags.append("requires_review")
    if state["intent"] in {"audit", "moderation"}:
        state["risk_level"] = "medium"
    if state["intent"] == "audit" and profile.should_run_safety_check():
        state["risk_level"] = "high"
        state["needs_human_handoff"] = True
        flags.append("human_review_recommended")
    state["risk_flags"] = flags
    return {**payload, "state": state}


def finalize_node(payload: dict[str, Any]) -> dict[str, Any]:
    state: AgentState = deepcopy(payload["state"])
    profile: AgentProfile = payload["profile"]
    state["final_response"] = state["draft_response"]
    state["next_actions"] = profile.default_next_actions
    return {**payload, "state": state}

def _safe_llm_config(config: dict[str, Any]) -> dict[str, Any]:
    safe_config = dict(config)
    if safe_config.get("api_key"):
        safe_config["api_key"] = "***"
    return safe_config


def _render_task_prompt(profile: AgentProfile, state: AgentState) -> str:
    capabilities = ", ".join(profile.capabilities)
    constraints = "\n".join(f"- {item}" for item in profile.constraints)
    output_fields = "\n".join(f"- {item}" for item in profile.output_sections)
    return (
        f"你是 {profile.display_name}。\n"
        f"岗位目标：{profile.description}\n"
        f"核心能力：{capabilities}\n"
        f"输出结构：\n{output_fields}\n"
        f"执行约束：\n{constraints}\n\n"
        f"用户输入：{state['user_input']}\n"
        f"会话上下文：{state.get('user_context', {})}\n"
        "请基于岗位职责输出结构化、可执行的回答。"
    )
