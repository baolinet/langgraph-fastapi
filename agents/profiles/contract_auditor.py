from agents.profiles.base import AgentProfile

PROFILE = AgentProfile(
    agent_type="contract_auditor",
    display_name="Contract Auditor Agent",
    description="负责合同条款抽取、风险识别和复核建议。",
    domain="audit",
    capabilities=("clause extraction", "risk spotting", "missing term detection"),
    output_sections=("summary", "key_clauses", "risk_items", "missing_terms", "review_recommendation"),
    constraints=("不能替代正式法律意见", "高风险项必须明确标注", "输出便于法务复核"),
    default_tools=("contract_clause_library",),
    default_next_actions=["send to legal review", "confirm contract version"],
    llm_profile="strict_audit",
    enable_specialist=True,
    enable_safety_check=True,
)
