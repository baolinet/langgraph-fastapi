#!/usr/bin/env python3
"""
Agent 接口测试脚本

当前覆盖：
1. Contract Auditor - 缺少合同正文时等待补充
2. Contract Auditor - 缺少补充信息时等待补充
3. Contract Auditor - 等待客户确认
4. Contract Auditor - 完整审核流程
5. Customer Service - 基础成功调用
6. Customer Service - 缺少必填字段验证
"""

import os
import sys

import requests
from requests import RequestException, Timeout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 20
LLM_REQUEST_TIMEOUT = 60


def print_section(title: str):
    print("\n" + "=" * 60)
    print(f"🤖 {title}")
    print("=" * 60)


def print_test_result(test_name: str, success: bool, details: str = ""):
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")


def get_api_key(username="admin", password="admin123") -> str | None:
    try:
        response = requests.post(
            f"{BASE_URL}/api-key",
            json={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            return response.json()["data"]["api_auth_key"]
    except RequestException as exc:
        print(f"❌ 获取 API Key 失败：{exc}")
    return None


def test_contract_auditor_waiting_for_contract_text(api_key: str):
    print_section("测试 1: Contract Auditor 等待合同正文")
    headers = {"api-auth-key": api_key}
    payload = {
        "conversation_id": "contract-test-001",
        "action": "initial_review",
        "review_focus": ["付款条款", "违约责任"],
        "user_input": "请先帮我审核风险",
    }
    response = requests.post(
        f"{BASE_URL}/api/agents/contract-auditor/run",
        json=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    result = response.json()
    success = (
        response.status_code == 200
        and result["data"]["workflow_status"] == "waiting_for_information"
        and result["data"]["awaiting"]["type"] == "contract_text"
    )
    print_test_result(
        "缺少合同正文时返回等待补充",
        success,
        f"状态码：{response.status_code}, workflow_status: {result.get('data', {}).get('workflow_status')}",
    )


def test_contract_auditor_waiting_for_supplement(api_key: str):
    print_section("测试 2: Contract Auditor 等待补充信息")
    headers = {"api-auth-key": api_key}
    payload = {
        "conversation_id": "contract-test-002",
        "action": "supplement_info",
        "review_focus": ["争议解决"],
    }
    response = requests.post(
        f"{BASE_URL}/api/agents/contract-auditor/run",
        json=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    result = response.json()
    success = (
        response.status_code == 200
        and result["data"]["workflow_status"] == "waiting_for_information"
        and result["data"]["awaiting"]["type"] == "supplemental_info"
    )
    print_test_result(
        "缺少补充信息时返回等待补充",
        success,
        f"状态码：{response.status_code}, workflow_status: {result.get('data', {}).get('workflow_status')}",
    )


def test_contract_auditor_waiting_for_confirmation(api_key: str):
    print_section("测试 3: Contract Auditor 等待客户确认")
    headers = {"api-auth-key": api_key}
    payload = {
        "conversation_id": "contract-test-003",
        "action": "confirm_review",
        "confirmation_status": "pending",
        "user_input": "等待客户确认审核意见",
    }
    response = requests.post(
        f"{BASE_URL}/api/agents/contract-auditor/run",
        json=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    result = response.json()
    success = (
        response.status_code == 200
        and result["data"]["workflow_status"] == "waiting_for_confirmation"
        and result["data"]["awaiting"]["type"] == "customer_confirmation"
    )
    print_test_result(
        "客户确认待定时返回等待确认",
        success,
        f"状态码：{response.status_code}, workflow_status: {result.get('data', {}).get('workflow_status')}",
    )


def test_contract_auditor_full_review_flow(api_key: str):
    print_section("测试 4: Contract Auditor 完整审核")
    headers = {"api-auth-key": api_key}
    payload = {
        "conversation_id": "contract-test-004",
        "action": "initial_review",
        "contract_text": (
            "甲方应于合同签署后7日内向乙方支付服务费10000元。"
            "若甲方逾期付款，每逾期一日按应付未付金额的1%支付违约金。"
            "乙方应于收到首付款后30日内完成交付。"
            "本合同未约定争议解决方式，也未明确保密责任。"
        ),
        "review_focus": ["付款条款", "违约责任", "争议解决", "保密条款"],
        "user_input": "请重点检查高风险条款和缺失条款",
        "user_context": {
            "business_type": "service_contract",
            "customer_name": "测试客户",
        },
        "messages": [],
        "metadata": {"source": "test_agents.py"},
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/agents/contract-auditor/run",
            json=payload,
            headers=headers,
            timeout=LLM_REQUEST_TIMEOUT,
        )
    except Timeout:
        print_test_result(
            "完整合同审核超时",
            False,
            f"请求超过 {LLM_REQUEST_TIMEOUT} 秒未返回，通常表示本地模型响应过慢或卡住",
        )
        return
    except RequestException as exc:
        print_test_result("完整合同审核请求异常", False, str(exc))
        return

    result = response.json()
    data = result.get("data", {})
    agent_result = data.get("agent_result", {})
    success = (
        response.status_code == 200
        and data.get("workflow_status") == "review_completed"
        and isinstance(agent_result.get("answer"), str)
        and agent_result.get("agent_type") == "contract_auditor"
    )
    print_test_result(
        "完整合同审核成功",
        success,
        f"状态码：{response.status_code}, workflow_status: {data.get('workflow_status')}",
    )
    if response.status_code != 200:
        print(f"   错误响应：{result}")


def test_customer_service_success(api_key: str):
    print_section("测试 5: Customer Service 基础调用")
    headers = {"api-auth-key": api_key}
    payload = {
        "conversation_id": "customer-service-test-001",
        "user_input": "客户说订单还没到，情绪比较激动，帮我生成一段安抚回复",
        "user_context": {
            "customer_level": "vip",
            "channel": "online_chat",
        },
        "messages": [
            {
                "role": "user",
                "content": "我的订单为什么还没到？已经等了很多天！",
            }
        ],
        "metadata": {
            "source": "test_agents.py",
        },
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/agents/customer-service/run",
            json=payload,
            headers=headers,
            timeout=LLM_REQUEST_TIMEOUT,
        )
    except Timeout:
        print_test_result(
            "Customer Service 调用超时",
            False,
            f"请求超过 {LLM_REQUEST_TIMEOUT} 秒未返回，通常表示本地模型响应过慢或卡住",
        )
        return
    except RequestException as exc:
        print_test_result("Customer Service 请求异常", False, str(exc))
        return

    result = response.json()
    data = result.get("data", {})
    success = (
        response.status_code == 200
        and data.get("agent_type") == "customer_service"
        and isinstance(data.get("answer"), str)
        and bool(data.get("answer", "").strip())
    )
    print_test_result(
        "Customer Service 基础调用成功",
        success,
        f"状态码：{response.status_code}, agent_type: {data.get('agent_type')}",
    )
    if response.status_code != 200:
        print(f"   错误响应：{result}")


def test_customer_service_validation_error(api_key: str):
    print_section("测试 6: Customer Service 参数校验")
    headers = {"api-auth-key": api_key}
    payload = {
        "conversation_id": "customer-service-test-002",
    }
    response = requests.post(
        f"{BASE_URL}/api/agents/customer-service/run",
        json=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    result = response.json()
    success = response.status_code == 422
    print_test_result(
        "缺少 user_input 时返回 422",
        success,
        f"状态码：{response.status_code}, message: {result.get('message')}",
    )


def main():
    print("\n🚀 开始测试 Agent 接口\n")
    api_key = get_api_key()
    if not api_key:
        print("❌ 无法获取测试 API Key，请先确认 admin/admin123 可登录")
        sys.exit(1)

    # test_contract_auditor_waiting_for_contract_text(api_key)
    # test_contract_auditor_waiting_for_supplement(api_key)
    # test_contract_auditor_waiting_for_confirmation(api_key)
    # test_contract_auditor_full_review_flow(api_key)
    test_customer_service_success(api_key)
    test_customer_service_validation_error(api_key)


if __name__ == "__main__":
    main()
