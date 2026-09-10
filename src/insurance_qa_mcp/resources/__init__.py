# Author: Maharshi Soni | License: MIT
"""MCP resource providers for insurance QA data."""

from insurance_qa_mcp.resources.insurance_domain import (
    get_insurance_lines,
    get_test_patterns,
)
from insurance_qa_mcp.resources.project_scanner import scan_projects

__all__ = [
    "scan_projects",
    "get_insurance_lines",
    "get_test_patterns",
]
