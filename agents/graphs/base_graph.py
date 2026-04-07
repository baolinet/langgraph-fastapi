from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.graphs.nodes import (
    classify_intent_node,
    execute_task_node,
    finalize_node,
    load_profile_node,
    preprocess_input_node,
    route_tools_node,
    safety_check_node,
    specialist_node,
)


def build_agent_graph():
    graph = StateGraph(dict)
    graph.add_node("load_profile", load_profile_node)
    graph.add_node("preprocess_input", preprocess_input_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("route_tools", route_tools_node)
    graph.add_node("execute_task", execute_task_node)
    graph.add_node("specialist", specialist_node)
    graph.add_node("safety_check", safety_check_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "load_profile")
    graph.add_edge("load_profile", "preprocess_input")
    graph.add_conditional_edges(
        "preprocess_input",
        lambda payload: "classify_intent"
        if payload["profile"].should_classify_intent()
        else "route_tools"
        if payload["profile"].should_route_tools()
        else "execute_task",
        {
            "classify_intent": "classify_intent",
            "route_tools": "route_tools",
            "execute_task": "execute_task",
        },
    )
    graph.add_conditional_edges(
        "classify_intent",
        lambda payload: "route_tools"
        if payload["profile"].should_route_tools()
        else "execute_task",
        {
            "route_tools": "route_tools",
            "execute_task": "execute_task",
        },
    )
    graph.add_edge("route_tools", "execute_task")
    graph.add_conditional_edges(
        "execute_task",
        lambda payload: "specialist"
        if payload["profile"].should_use_specialist()
        else "safety_check"
        if payload["profile"].should_run_safety_check()
        else "finalize",
        {
            "specialist": "specialist",
            "safety_check": "safety_check",
            "finalize": "finalize",
        },
    )
    graph.add_conditional_edges(
        "specialist",
        lambda payload: "safety_check"
        if payload["profile"].should_run_safety_check()
        else "finalize",
        {
            "safety_check": "safety_check",
            "finalize": "finalize",
        },
    )
    graph.add_edge("safety_check", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()
