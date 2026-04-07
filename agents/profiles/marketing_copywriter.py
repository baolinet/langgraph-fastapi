from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="marketing_copywriter",
    display_name="Marketing Copywriter Agent",
    description="负责营销文案、活动文案和转化导向内容生成。",
    domain="marketing",
    capabilities=("campaign copy", "brand tone", "cta optimization", "a/b variants"),
    output_sections=("summary", "headline", "body_copy", "cta", "channel_variants"),
    constraints=("保持品牌语气一致", "避免虚假承诺", "输出可直接投放的文案"),
    default_tools=("tone_guide_lookup",),
    default_next_actions=["review copy", "select channel", "approve campaign"],
    llm_profile="creative",
    enable_specialist=True,
)
