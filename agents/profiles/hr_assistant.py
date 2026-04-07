from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="hr_assistant",
    display_name="HR Assistant Agent",
    description="负责 HR 问答、招聘沟通和流程说明。",
    domain="hr",
    capabilities=("policy faq", "job description drafting", "candidate communication"),
    output_sections=("summary", "answer", "process_steps", "template", "notes"),
    constraints=("避免法律承诺", "信息表述规范", "涉及制度时保留人工确认"),
    default_tools=("hr_policy_lookup",),
    default_next_actions=["check policy owner", "send approved response"],
    llm_profile="default",
    enable_specialist=False,
    enable_safety_check=False,
)
