from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="content_moderator",
    display_name="Content Moderator Agent",
    description="负责内容审核、违规判定和升级建议。",
    domain="moderation",
    capabilities=("policy matching", "risk labeling", "review escalation"),
    output_sections=("summary", "decision", "risk_level", "policy_basis", "escalation"),
    constraints=("说明判定理由", "高风险内容必须标记", "结果便于人工复核"),
    default_tools=("moderation_policy_lookup",),
    default_next_actions=["record decision", "escalate if needed"],
    llm_profile="strict_audit",
    enable_specialist=True,
    enable_safety_check=True,
)
