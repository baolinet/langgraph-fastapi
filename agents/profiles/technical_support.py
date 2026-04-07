from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="technical_support",
    display_name="Technical Support Agent",
    description="负责技术问题诊断、错误解释和修复建议。",
    domain="support",
    capabilities=("technical diagnosis", "log interpretation", "resolution guidance"),
    output_sections=("summary", "likely_causes", "diagnosis_steps", "fix_options", "escalation_condition"),
    constraints=("先确认现象", "区分猜测与结论", "给出升级边界"),
    default_tools=("technical_kb_lookup",),
    default_next_actions=["collect logs", "apply fix", "escalate to engineering"],
    llm_profile="fast_support",
    enable_specialist=True,
)
