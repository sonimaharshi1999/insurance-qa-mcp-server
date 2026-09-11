# Author: Maharshi Soni | License: MIT
"""QA workflow orchestrator: chains multiple MCP tools based on natural language requests."""

from __future__ import annotations

import json
import re
from typing import Any


def run_qa_workflow_impl(request: str) -> str:
    """Take a natural language QA request and chain multiple tools together.

    Routes the request to appropriate tool sequences based on keyword
    analysis. Supports workflows for test creation, code review, chaos
    testing, data validation, and full QA pipeline orchestration.

    Args:
        request: Natural language QA request (e.g., "Create test cases for this story").

    Returns:
        JSON string with the workflow execution plan and results.
    """
    if not request or not request.strip():
        return json.dumps({"error": "Request is required"})

    request_lower = request.lower()
    workflow = _route_request(request_lower)
    steps = _build_workflow_steps(workflow, request)

    return json.dumps(
        {
            "request": request,
            "detected_workflow": workflow["name"],
            "confidence": workflow["confidence"],
            "description": workflow["description"],
            "total_steps": len(steps),
            "steps": steps,
            "execution_plan": _format_execution_plan(steps),
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Workflow Routing
# ---------------------------------------------------------------------------

_WORKFLOW_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "story_to_tests",
        "description": "Fetch user story from ADO, generate test cases, register in Zephyr",
        "keywords": ["story", "user story", "acceptance criteria", "create test", "test cases for"],
        "tools": ["get_user_stories", "get_test_plan", "auto_generate_tests", "update_test_result"],
    },
    {
        "name": "code_review_pipeline",
        "description": "Run multi-agent code review with security, performance, and style analysis",
        "keywords": ["code review", "review code", "review this", "check code", "code quality"],
        "tools": ["review_code", "lint_code", "suggest_tests"],
    },
    {
        "name": "chaos_testing",
        "description": "Generate and execute chaos test scenarios from API specification",
        "keywords": ["chaos", "chaos test", "api test", "fuzz", "boundary", "stress test"],
        "tools": ["chaos_test_api", "validate_data_integrity"],
    },
    {
        "name": "regression_analysis",
        "description": "Run regression tests, analyze failures, check coverage, and report to Zephyr",
        "keywords": ["regression", "run tests", "test suite", "test run", "execute tests"],
        "tools": ["run_tests", "analyze_coverage", "find_flaky_tests", "get_test_cycles", "update_test_result"],
    },
    {
        "name": "data_validation",
        "description": "Query test data, validate integrity, and generate synthetic data if needed",
        "keywords": ["data validation", "data quality", "validate data", "test data", "data integrity"],
        "tools": ["query_test_data", "validate_data_integrity", "generate_test_data"],
    },
    {
        "name": "semantic_search",
        "description": "Search knowledge base for relevant documentation and test patterns",
        "keywords": ["search", "find", "look up", "knowledge", "documentation", "similar"],
        "tools": ["semantic_search"],
    },
    {
        "name": "bdd_workflow",
        "description": "Generate BDD scenarios from user stories and create Playwright tests",
        "keywords": ["bdd", "gherkin", "scenario", "behavior", "playwright", "e2e", "end to end"],
        "tools": ["get_user_stories", "generate_bdd_scenarios", "generate_playwright_tests"],
    },
    {
        "name": "full_qa_pipeline",
        "description": "Complete QA pipeline: stories -> tests -> review -> execute -> report",
        "keywords": ["full pipeline", "complete qa", "end to end qa", "qa pipeline", "full qa"],
        "tools": [
            "get_user_stories", "auto_generate_tests", "review_code",
            "run_tests", "analyze_coverage", "update_test_result",
        ],
    },
]


def _route_request(request_lower: str) -> dict[str, Any]:
    """Route a request to the best-matching workflow based on keywords."""
    best_match: dict[str, Any] | None = None
    best_score = 0.0

    for workflow in _WORKFLOW_DEFINITIONS:
        score = 0.0
        for keyword in workflow["keywords"]:
            if keyword in request_lower:
                # Longer keyword matches score higher
                score += len(keyword.split())

        if score > best_score:
            best_score = score
            best_match = workflow

    if best_match and best_score > 0:
        confidence = min(round(best_score / 3.0, 2), 1.0)
        return {
            "name": best_match["name"],
            "description": best_match["description"],
            "tools": best_match["tools"],
            "confidence": confidence,
        }

    # Default: suggest a general workflow
    return {
        "name": "general_qa",
        "description": "General QA assistance -- no specific workflow matched",
        "tools": ["suggest_tests", "lint_code", "generate_test_data"],
        "confidence": 0.3,
    }


# ---------------------------------------------------------------------------
# Workflow Step Building
# ---------------------------------------------------------------------------


def _build_workflow_steps(workflow: dict[str, Any], request: str) -> list[dict[str, Any]]:
    """Build detailed execution steps for a workflow."""
    steps: list[dict[str, Any]] = []
    tool_descriptions = _get_tool_descriptions()

    for i, tool_name in enumerate(workflow["tools"], start=1):
        description = tool_descriptions.get(tool_name, f"Execute {tool_name}")
        suggested_args = _suggest_arguments(tool_name, request)

        steps.append({
            "step": i,
            "tool": tool_name,
            "description": description,
            "suggested_arguments": suggested_args,
            "depends_on": _get_dependencies(i, tool_name, workflow["tools"]),
            "status": "planned",
        })

    return steps


def _get_tool_descriptions() -> dict[str, str]:
    """Map tool names to human-readable descriptions."""
    return {
        "get_user_stories": "Fetch user stories and acceptance criteria from ADO/Jira",
        "get_test_plan": "Retrieve existing test plan linked to the story",
        "auto_generate_tests": "Generate test cases from source code analysis",
        "update_test_result": "Update test execution status in Zephyr",
        "review_code": "Run multi-agent code review (security + performance + style)",
        "lint_code": "Check code quality: complexity, naming, type hints",
        "suggest_tests": "Analyze source and suggest missing test coverage",
        "chaos_test_api": "Generate chaos test scenarios from OpenAPI spec",
        "validate_data_integrity": "Run data quality checks on database tables",
        "run_tests": "Execute the test suite and collect results",
        "analyze_coverage": "Parse coverage reports and find uncovered code",
        "find_flaky_tests": "Detect non-deterministic tests via repeated execution",
        "get_test_cycles": "Retrieve current test cycles from Zephyr",
        "query_test_data": "Query mock database for insurance test data",
        "generate_test_data": "Generate synthetic insurance records (policies, claims, billing)",
        "semantic_search": "Search knowledge base using semantic similarity",
        "generate_bdd_scenarios": "Generate BDD/Gherkin scenarios for insurance workflows",
        "generate_playwright_tests": "Generate Playwright E2E test scripts",
    }


def _suggest_arguments(tool_name: str, request: str) -> dict[str, str]:
    """Suggest tool arguments based on the request context."""
    args: dict[str, str] = {}

    # Extract project names
    for project in ["PolicyCenter", "ClaimCenter", "BillingCenter"]:
        if project.lower() in request.lower():
            args["project"] = project
            break

    # Extract story IDs
    story_match = re.search(r"US-\d+", request, re.IGNORECASE)
    if story_match:
        args["story_id"] = story_match.group(0).upper()

    # Extract file paths
    path_match = re.search(r"[/\\][\w/\\.-]+\.py", request)
    if path_match:
        args["file_path"] = path_match.group(0)

    # Extract URLs
    url_match = re.search(r"https?://\S+", request)
    if url_match:
        args["url"] = url_match.group(0)

    # Tool-specific defaults
    if tool_name == "generate_test_data" and "project" not in args:
        args["line_of_business"] = "personal_auto"
        args["count"] = "10"

    if tool_name == "run_tests" and "project_path" not in args:
        args["project_path"] = "<current_project>"

    return args


def _get_dependencies(step_num: int, tool_name: str, all_tools: list[str]) -> list[int]:
    """Determine which earlier steps this step depends on."""
    if step_num == 1:
        return []

    dependency_map: dict[str, set[str]] = {
        "auto_generate_tests": {"get_user_stories", "get_test_plan"},
        "update_test_result": {"run_tests", "auto_generate_tests"},
        "analyze_coverage": {"run_tests"},
        "find_flaky_tests": {"run_tests"},
        "generate_playwright_tests": {"get_user_stories", "generate_bdd_scenarios"},
        "review_code": {"auto_generate_tests"},
    }

    deps = dependency_map.get(tool_name, set())
    dep_steps = []
    for i, earlier_tool in enumerate(all_tools[:step_num - 1], start=1):
        if earlier_tool in deps:
            dep_steps.append(i)

    return dep_steps


def _format_execution_plan(steps: list[dict[str, Any]]) -> str:
    """Format steps as a readable execution plan."""
    lines: list[str] = []
    for step in steps:
        deps = ""
        if step["depends_on"]:
            deps = f" (after step {', '.join(str(d) for d in step['depends_on'])})"
        lines.append(f"  {step['step']}. [{step['tool']}] {step['description']}{deps}")

    return "Execution Plan:\n" + "\n".join(lines)
