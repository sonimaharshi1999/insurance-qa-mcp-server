# Author: Maharshi Soni | License: MIT
"""Bridge modules wrapping external project functionality as MCP tools."""

from insurance_qa_mcp.tools.bridges.playwright_bridge import (
    generate_playwright_tests_impl,
    run_playwright_audit_impl,
)
from insurance_qa_mcp.tools.bridges.code_review_bridge import review_code_impl
from insurance_qa_mcp.tools.bridges.test_gen_bridge import auto_generate_tests_impl
from insurance_qa_mcp.tools.bridges.embedkit_bridge import semantic_search_impl
from insurance_qa_mcp.tools.bridges.chaos_test_bridge import chaos_test_api_impl

__all__ = [
    "generate_playwright_tests_impl",
    "run_playwright_audit_impl",
    "review_code_impl",
    "auto_generate_tests_impl",
    "semantic_search_impl",
    "chaos_test_api_impl",
]
