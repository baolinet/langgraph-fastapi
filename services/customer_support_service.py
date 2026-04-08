from __future__ import annotations

import re
from typing import Any


class CustomerSupportService:
    """客服上下文 mock 服务。"""

    def get_customer_profile(self, user_context: dict[str, Any]) -> dict[str, Any]:
        customer_level = user_context.get("customer_level", "standard")
        return {
            "customer_id": user_context.get("customer_id", "mock-customer-001"),
            "customer_name": user_context.get("customer_name", "测试客户"),
            "customer_level": customer_level,
            "vip": customer_level.lower() == "vip",
            "recent_tickets": user_context.get(
                "recent_tickets",
                ["物流延迟咨询", "退款进度跟进"] if customer_level.lower() == "vip" else ["订单状态咨询"],
            ),
        }

    def get_order_context(self, user_input: str, user_context: dict[str, Any]) -> dict[str, Any]:
        order_id = user_context.get("order_id") or self._extract_order_id(user_input) or "MOCK-ORDER-001"
        status = user_context.get("order_status", "in_transit")
        return {
            "order_id": order_id,
            "order_status": status,
            "shipment_status": user_context.get("shipment_status", "运输中"),
            "expected_delivery": user_context.get("expected_delivery", "2026-04-10"),
            "last_tracking": user_context.get("last_tracking", "包裹已到达杭州分拨中心"),
        }

    def retrieve_faq(self, user_input: str) -> list[dict[str, str]]:
        lowered = user_input.lower()
        faq_entries = []
        if any(token in lowered for token in ["订单", "物流", "没到", "延迟", "发货"]):
            faq_entries.append(
                {
                    "question": "订单延迟如何处理？",
                    "answer": "先确认订单状态和最新物流节点，再向客户说明预计送达时间；若超出承诺时效，提供升级处理方案。",
                }
            )
        if any(token in lowered for token in ["退款", "退货"]):
            faq_entries.append(
                {
                    "question": "退款处理时如何回复客户？",
                    "answer": "说明退款进度、预计到账时间，并避免承诺超出系统处理时效的结果。",
                }
            )
        if any(token in lowered for token in ["投诉", "生气", "着急", "激动"]):
            faq_entries.append(
                {
                    "question": "客户情绪激动时的沟通原则是什么？",
                    "answer": "先共情，再说明正在处理的动作，最后给出明确的下一步和时间点。",
                }
            )
        if not faq_entries:
            faq_entries.append(
                {
                    "question": "客服通用回复原则",
                    "answer": "确认客户诉求、避免空泛承诺、给出明确处理路径和下一步。",
                }
            )
        return faq_entries

    @staticmethod
    def _extract_order_id(text: str) -> str | None:
        matched = re.search(r"(?:order|订单)[\\s#:：-]*([A-Za-z0-9-]{4,})", text, re.IGNORECASE)
        if matched:
            return matched.group(1)
        return None
