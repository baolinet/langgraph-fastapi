from __future__ import annotations

from agents.profiles.base import AgentProfile


def resolve_agent_steps(profile: AgentProfile) -> list[str]:
    steps = ["load_profile", "preprocess_input"]

    if profile.should_load_customer_profile():
        steps.append("load_customer_profile")
    if profile.should_load_order_context():
        steps.append("load_order_context")
    if profile.should_retrieve_faq():
        steps.append("retrieve_faq")
    if profile.should_classify_intent():
        steps.append("classify_intent")
    if profile.should_route_tools():
        steps.append("route_tools")

    steps.append("execute_task")

    if profile.should_use_specialist():
        steps.append("specialist")
    if profile.should_run_safety_check():
        steps.append("safety_check")

    steps.append("finalize")
    return steps


def build_agent_mermaid(profile: AgentProfile) -> str:
    lines = ["flowchart TD", f"    subgraph {profile.agent_type}[{profile.display_name}]"]

    lines.extend(
        [
            "        start([START]) --> load_profile[load_profile]",
            "        load_profile --> preprocess_input[preprocess_input]",
        ]
    )

    previous = "preprocess_input"
    optional_steps = [
        ("load_customer_profile", "load_customer_profile?", profile.should_load_customer_profile()),
        ("load_order_context", "load_order_context?", profile.should_load_order_context()),
        ("retrieve_faq", "retrieve_faq?", profile.should_retrieve_faq()),
        ("classify_intent", "classify_intent?", profile.should_classify_intent()),
        ("route_tools", "route_tools?", profile.should_route_tools()),
    ]

    for step_name, condition_label, enabled in optional_steps:
        decision_name = f"{step_name}_decision"
        merge_name = f"{step_name}_merge"
        lines.append(f"        {previous} --> {decision_name}{{{condition_label}}}")
        if enabled:
            lines.append(f"        {decision_name} -- yes --> {step_name}[{step_name}]")
            lines.append(f"        {step_name} --> {merge_name}((continue))")
        else:
            lines.append(f"        {decision_name} -- yes --> {step_name}_disabled[[disabled]]")
            lines.append(f"        {step_name}_disabled --> {merge_name}((continue))")
        lines.append(f"        {decision_name} -- no --> {merge_name}")
        previous = merge_name

    lines.append(f"        {previous} --> execute_task[execute_task]")
    previous = "execute_task"

    trailing_steps = [
        ("specialist", "use_specialist?", profile.should_use_specialist()),
        ("safety_check", "run_safety_check?", profile.should_run_safety_check()),
    ]

    for step_name, condition_label, enabled in trailing_steps:
        decision_name = f"{step_name}_decision"
        merge_name = f"{step_name}_merge"
        lines.append(f"        {previous} --> {decision_name}{{{condition_label}}}")
        if enabled:
            lines.append(f"        {decision_name} -- yes --> {step_name}[{step_name}]")
            lines.append(f"        {step_name} --> {merge_name}((continue))")
        else:
            lines.append(f"        {decision_name} -- yes --> {step_name}_disabled[[disabled]]")
            lines.append(f"        {step_name}_disabled --> {merge_name}((continue))")
        lines.append(f"        {decision_name} -- no --> {merge_name}")
        previous = merge_name

    lines.append(f"        {previous} --> finalize[finalize]")
    lines.append("        finalize --> end([END])")
    lines.append("    end")
    return "\n".join(lines)
