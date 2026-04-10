from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agents import build_agent_runner
from agents.core.runner import AgentRunRequest
from agents.graphs.mermaid import build_agent_mermaid, resolve_agent_steps
from database import get_db
from routers.dependencies import verify_api_auth_key
from schemas.memory import AgentConversationCreate, AgentMessageCreate
from services.memory_service import AgentMemoryService
from utils.response import error_response, success_response

router = APIRouter(prefix="/api/agents", tags=["agents"])

_agent_runner = build_agent_runner()


class CustomerServiceAgentRequest(BaseModel):
    user_input: str = Field(..., min_length=1, description="用户输入")
    conversation_id: str = Field(..., min_length=1, description="会话 ID")
    user_context: dict = Field(default_factory=dict, description="用户上下文")
    messages: list[dict[str, str]] = Field(default_factory=list, description="历史消息")
    metadata: dict = Field(default_factory=dict, description="附加元数据")


class ContractAuditorAgentRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, description="会话 ID")
    action: Literal["initial_review", "supplement_info", "confirm_review"] = Field(
        default="initial_review",
        description="合同审核动作",
    )
    contract_text: str | None = Field(default=None, description="合同正文")
    review_focus: list[str] = Field(default_factory=list, description="审核关注点")
    supplemental_info: str | None = Field(default=None, description="客户补充信息")
    confirmation_status: Literal["pending", "confirmed", "rejected", "not_required"] = Field(
        default="not_required",
        description="客户确认状态",
    )
    user_input: str | None = Field(default=None, description="额外审核指令")
    user_context: dict = Field(default_factory=dict, description="用户上下文")
    messages: list[dict[str, str]] = Field(default_factory=list, description="历史消息")
    metadata: dict = Field(default_factory=dict, description="附加元数据")


@router.get(
    "/graph/mermaid",
    summary="查看 Agent Mermaid 图",
    dependencies=[Depends(verify_api_auth_key)],
)
async def get_agent_graph_mermaid(agent_type: str | None = None):
    """按 agent_type 查看 Mermaid 图；不传时返回全部 agent 图。"""
    available_types = _agent_runner.list_agent_types()

    if agent_type:
        try:
            profile = _agent_runner.registry.get(agent_type)
        except ValueError as exc:
            return error_response(message=str(exc), code=400)

        return success_response(
            data={
                "agent_type": agent_type,
                "display_name": profile.display_name,
                "steps": resolve_agent_steps(profile),
                "mermaid": build_agent_mermaid(profile),
            },
            message="Agent Mermaid 图获取成功",
        )

    graphs = []
    for current_agent_type in available_types:
        profile = _agent_runner.registry.get(current_agent_type)
        graphs.append(
            {
                "agent_type": current_agent_type,
                "display_name": profile.display_name,
                "steps": resolve_agent_steps(profile),
                "mermaid": build_agent_mermaid(profile),
            }
        )

    return success_response(
        data={
            "agent_types": available_types,
            "graphs": graphs,
        },
        message="全部 Agent Mermaid 图获取成功",
    )


@router.post(
    "/customer-service/run",
    summary="调用 Customer Service Agent",
    dependencies=[Depends(verify_api_auth_key)],
)
async def run_customer_service_agent(
    request: CustomerServiceAgentRequest,
    db: Session = Depends(get_db),
):
    """调用 customer_service 智能体生成基础客服回复。"""
    try:
        memory_service = AgentMemoryService(db)
        _upsert_conversation(
            memory_service,
            conversation_id=request.conversation_id,
            agent_type="customer_service",
            status="active",
            waiting_for=None,
            summary=request.user_input[:200],
        )
        _append_user_message(
            memory_service,
            conversation_id=request.conversation_id,
            content=request.user_input,
            metadata={
                "agent_type": "customer_service",
                "user_context": request.user_context,
                "metadata": request.metadata,
            },
        )
        agent_request = AgentRunRequest(
            agent_type="customer_service",
            user_input=request.user_input,
            conversation_id=request.conversation_id,
            user_context=request.user_context,
            messages=request.messages,
            metadata=request.metadata,
        )
        result = _agent_runner.run(agent_request)
        _append_assistant_message(
            memory_service,
            conversation_id=request.conversation_id,
            content=result.answer,
            metadata={
                "agent_type": "customer_service",
                "summary": result.summary,
                "risk_level": result.risk_level,
            },
        )
        return success_response(data=result.model_dump(), message="Customer Service Agent 调用成功")
    except ValueError as exc:
        return error_response(message=str(exc), code=400)
    except RuntimeError as exc:
        return error_response(message=str(exc), code=500)
    except Exception as exc:
        return error_response(message=f"Agent 调用失败: {exc}", code=500)


@router.post(
    "/contract-auditor/run",
    summary="调用 Contract Auditor Agent",
    dependencies=[Depends(verify_api_auth_key)],
)
async def run_contract_auditor_agent(
    request: ContractAuditorAgentRequest,
    db: Session = Depends(get_db),
):
    """调用 contract_auditor 智能体，支持补充信息和客户确认流程。"""
    try:
        memory_service = AgentMemoryService(db)
        prompt = _build_contract_auditor_prompt(request)
        _upsert_conversation(
            memory_service,
            conversation_id=request.conversation_id,
            agent_type="contract_auditor",
            status="active",
            waiting_for=None,
            summary=(request.user_input or request.action)[:200],
        )
        _append_user_message(
            memory_service,
            conversation_id=request.conversation_id,
            content=prompt,
            metadata={
                "agent_type": "contract_auditor",
                "action": request.action,
                "review_focus": request.review_focus,
                "confirmation_status": request.confirmation_status,
                "user_context": request.user_context,
                "metadata": request.metadata,
            },
        )
        precheck = _precheck_contract_auditor_request(request)
        if precheck is not None:
            _upsert_conversation(
                memory_service,
                conversation_id=request.conversation_id,
                agent_type="contract_auditor",
                status=precheck["workflow_status"],
                waiting_for=precheck["awaiting"]["type"],
                summary=(request.user_input or request.action)[:200],
            )
            _append_assistant_message(
                memory_service,
                conversation_id=request.conversation_id,
                content=precheck["awaiting"]["message"],
                metadata={
                    "agent_type": "contract_auditor",
                    "workflow_status": precheck["workflow_status"],
                    "awaiting": precheck["awaiting"],
                },
                status="waiting",
            )
            return success_response(data=precheck, message="Contract Auditor Agent 等待用户输入")

        agent_request = AgentRunRequest(
            agent_type="contract_auditor",
            user_input=prompt,
            conversation_id=request.conversation_id,
            user_context=_build_contract_auditor_context(request),
            messages=request.messages,
            metadata=request.metadata,
        )
        result = _agent_runner.run(agent_request)
        response_data = {
            "workflow_status": _resolve_contract_workflow_status(request),
            "awaiting": None,
            "agent_result": result.model_dump(),
        }
        _upsert_conversation(
            memory_service,
            conversation_id=request.conversation_id,
            agent_type="contract_auditor",
            status=response_data["workflow_status"],
            waiting_for=None,
            summary=result.summary[:200] if result.summary else (request.user_input or request.action)[:200],
        )
        _append_assistant_message(
            memory_service,
            conversation_id=request.conversation_id,
            content=result.answer,
            metadata={
                "agent_type": "contract_auditor",
                "workflow_status": response_data["workflow_status"],
                "risk_level": result.risk_level,
                "risk_flags": result.risk_flags,
                "needs_human_handoff": result.needs_human_handoff,
            },
        )
        return success_response(data=response_data, message="Contract Auditor Agent 调用成功")
    except ValueError as exc:
        return error_response(message=str(exc), code=400)
    except RuntimeError as exc:
        return error_response(message=str(exc), code=500)
    except Exception as exc:
        return error_response(message=f"Agent 调用失败: {exc}", code=500)


def _precheck_contract_auditor_request(request: ContractAuditorAgentRequest) -> dict | None:
    if request.action == "initial_review" and not request.contract_text:
        return {
            "workflow_status": "waiting_for_information",
            "awaiting": {
                "type": "contract_text",
                "message": "请先提供合同正文后再发起审核。",
                "required_fields": ["contract_text"],
            },
            "agent_result": None,
        }

    if request.action == "supplement_info" and not request.supplemental_info:
        return {
            "workflow_status": "waiting_for_information",
            "awaiting": {
                "type": "supplemental_info",
                "message": "当前动作是补充材料，请提供补充说明或缺失条款信息。",
                "required_fields": ["supplemental_info"],
            },
            "agent_result": None,
        }

    if request.action == "confirm_review" and request.confirmation_status == "pending":
        return {
            "workflow_status": "waiting_for_confirmation",
            "awaiting": {
                "type": "customer_confirmation",
                "message": "请等待客户确认审核意见后再继续。",
                "required_fields": ["confirmation_status"],
            },
            "agent_result": None,
        }

    return None


def _build_contract_auditor_prompt(request: ContractAuditorAgentRequest) -> str:
    parts = [
        f"审核动作: {request.action}",
    ]
    if request.contract_text:
        parts.append(f"合同正文:\n{request.contract_text}")
    if request.review_focus:
        parts.append(f"审核关注点: {', '.join(request.review_focus)}")
    if request.supplemental_info:
        parts.append(f"客户补充信息:\n{request.supplemental_info}")
    if request.confirmation_status != "not_required":
        parts.append(f"客户确认状态: {request.confirmation_status}")
    if request.user_input:
        parts.append(f"额外指令: {request.user_input}")
    parts.append(
        "请输出合同风险摘要、关键条款、缺失项、需要客户确认的问题，以及下一步建议。"
    )
    return "\n\n".join(parts)


def _build_contract_auditor_context(request: ContractAuditorAgentRequest) -> dict:
    context = dict(request.user_context)
    context.update(
        {
            "workflow_action": request.action,
            "confirmation_status": request.confirmation_status,
            "review_focus": request.review_focus,
            "has_contract_text": bool(request.contract_text),
            "has_supplemental_info": bool(request.supplemental_info),
        }
    )
    return context


def _resolve_contract_workflow_status(request: ContractAuditorAgentRequest) -> str:
    if request.action == "confirm_review":
        return "confirmed" if request.confirmation_status == "confirmed" else "review_completed"
    if request.action == "supplement_info":
        return "supplement_received"
    return "review_completed"


def _upsert_conversation(
    memory_service: AgentMemoryService,
    *,
    conversation_id: str,
    agent_type: str,
    status: str,
    waiting_for: str | None,
    summary: str | None,
) -> None:
    memory_service.create_or_update_conversation(
        AgentConversationCreate(
            conversation_id=conversation_id,
            agent_type=agent_type,
            status=status,
            current_waiting_for=waiting_for,
            summary=summary,
        )
    )


def _append_user_message(
    memory_service: AgentMemoryService,
    *,
    conversation_id: str,
    content: str,
    metadata: dict,
) -> None:
    memory_service.append_message(
        AgentMessageCreate(
            conversation_id=conversation_id,
            role="user",
            content=content,
            metadata=metadata,
        )
    )


def _append_assistant_message(
    memory_service: AgentMemoryService,
    *,
    conversation_id: str,
    content: str,
    metadata: dict,
    status: str = "completed",
) -> None:
    memory_service.append_message(
        AgentMessageCreate(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            status=status,
            metadata=metadata,
        )
    )
