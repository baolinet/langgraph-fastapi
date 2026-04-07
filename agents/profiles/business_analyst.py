from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="business_analyst",
    display_name="Business Analyst Agent",
    description="负责业务问题拆解、指标解释和需求分析。",
    domain="analysis",
    capabilities=("metric interpretation", "problem structuring", "requirement analysis"),
    output_sections=("summary", "observations", "hypotheses", "recommendations", "open_questions"),
    constraints=("明确假设边界", "建议可验证", "结构化表达"),
    default_tools=("metrics_dictionary_lookup",),
    default_next_actions=["validate assumptions", "align stakeholders"],
    llm_profile="default",
    enable_specialist=True,
)
