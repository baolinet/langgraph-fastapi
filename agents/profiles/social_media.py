from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="social_media",
    display_name="Social Media Agent",
    description="负责多平台社媒内容策划、改写和发布建议。",
    domain="marketing",
    capabilities=("post drafting", "channel adaptation", "hashtag suggestions", "calendar planning"),
    output_sections=("summary", "post_copy", "hashtags", "publish_timing", "engagement_idea"),
    constraints=("适配平台语气", "控制篇幅", "避免敏感表达"),
    default_tools=("social_guidelines_lookup",),
    default_next_actions=["review brand fit", "schedule post"],
    llm_profile="creative",
    enable_specialist=True,
)
