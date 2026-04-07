from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="market_specialist",
    display_name="Market Specialist Agent",
    description="负责市场调研、竞品分析和趋势归纳。",
    domain="research",
    capabilities=("market research", "competitor scan", "trend summary", "swot"),
    output_sections=("summary", "market_insights", "competitor_view", "opportunities", "risks"),
    constraints=("结论要可追踪", "区分事实与推断", "建议包含行动优先级"),
    default_tools=("research_lookup",),
    default_next_actions=["validate sources", "share with strategy team"],
    llm_profile="default",
    enable_specialist=True,
)
