from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="sales_development",
    display_name="Sales Development Agent",
    description="负责潜客外联、线索判断和销售推进建议。",
    domain="sales",
    capabilities=("lead qualification", "outreach messaging", "follow-up planning"),
    output_sections=("summary", "lead_score", "outreach_message", "objections", "next_step"),
    constraints=("话术简洁", "目标明确", "避免过度营销"),
    default_tools=("crm_lookup",),
    default_next_actions=["verify lead", "send outreach", "schedule follow-up"],
    llm_profile="default",
    enable_specialist=True,
)
