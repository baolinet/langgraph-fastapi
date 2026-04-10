#!/usr/bin/env python3

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.profiles.business_analyst import PROFILE as BUSINESS_ANALYST
from agents.profiles.customer_service import PROFILE as CUSTOMER_SERVICE
from agents.graphs.mermaid import build_agent_mermaid, resolve_agent_steps


class AgentGraphMermaidTestCase(unittest.TestCase):
    def test_business_analyst_steps(self):
        self.assertEqual(
            resolve_agent_steps(BUSINESS_ANALYST),
            [
                "load_profile",
                "preprocess_input",
                "classify_intent",
                "route_tools",
                "execute_task",
                "specialist",
                "finalize",
            ],
        )

    def test_customer_service_steps(self):
        self.assertEqual(
            resolve_agent_steps(CUSTOMER_SERVICE),
            [
                "load_profile",
                "preprocess_input",
                "load_customer_profile",
                "load_order_context",
                "retrieve_faq",
                "classify_intent",
                "route_tools",
                "execute_task",
                "finalize",
            ],
        )

    def test_mermaid_contains_expected_nodes(self):
        mermaid = build_agent_mermaid(BUSINESS_ANALYST)
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("classify_intent_decision{classify_intent?}", mermaid)
        self.assertIn("classify_intent_decision -- yes --> classify_intent[classify_intent]", mermaid)
        self.assertIn("classify_intent_decision -- no --> classify_intent_merge", mermaid)
        self.assertIn("specialist_decision -- yes --> specialist[specialist]", mermaid)
        self.assertIn("safety_check_decision -- no --> safety_check_merge", mermaid)

    def test_customer_service_mermaid_contains_skipped_branches(self):
        mermaid = build_agent_mermaid(CUSTOMER_SERVICE)
        self.assertIn("load_customer_profile_decision -- yes --> load_customer_profile[load_customer_profile]", mermaid)
        self.assertIn("load_customer_profile_decision -- no --> load_customer_profile_merge", mermaid)
        self.assertIn("specialist_decision -- no --> specialist_merge", mermaid)
        self.assertIn("safety_check_decision -- no --> safety_check_merge", mermaid)


if __name__ == "__main__":
    unittest.main()
