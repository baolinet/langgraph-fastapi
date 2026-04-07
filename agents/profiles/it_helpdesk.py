from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="it_helpdesk",
    display_name="IT Helpdesk Agent",
    description="负责 IT 问题分诊、基础排障和工单建议。",
    domain="it",
    capabilities=("issue triage", "basic troubleshooting", "ticket classification"),
    output_sections=("summary", "issue_type", "troubleshooting_steps", "priority", "ticket_recommendation"),
    constraints=("步骤可执行", "不要跳过风险提示", "不确定时建议升级"),
    default_tools=("it_kb_lookup",),
    default_next_actions=["run troubleshooting", "open helpdesk ticket"],
    llm_profile="fast_support",
    enable_specialist=True,
    enable_safety_check=False,
)
