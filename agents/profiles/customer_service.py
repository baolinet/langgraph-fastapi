from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="customer_service",
    display_name="Customer Service Agent",
    description="负责客户问答、客诉回复和服务话术生成。",
    domain="support",
    capabilities=("faq answering", "complaint handling", "empathetic replies"),
    output_sections=("summary", "customer_reply", "resolution_path", "tone_notes", "next_step"),
    constraints=("语气专业克制", "先回应用户诉求", "避免未经确认的承诺"),
    default_tools=("customer_policy_lookup",),
    default_next_actions=["send response", "track resolution"],
    llm_profile="fast_support",
    enable_customer_profile=True,
    enable_order_context=True,
    enable_faq_retrieval=True,
    enable_specialist=False,
    enable_safety_check=False,
)
