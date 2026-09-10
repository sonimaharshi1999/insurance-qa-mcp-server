# Author: Maharshi Soni | License: MIT
"""MCP prompt templates for insurance QA workflows."""

from insurance_qa_mcp.prompts.templates import (
    plan_test_strategy_prompt,
    review_failures_prompt,
    triage_bug_prompt,
)

__all__ = [
    "review_failures_prompt",
    "plan_test_strategy_prompt",
    "triage_bug_prompt",
]
