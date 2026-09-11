# Author: Maharshi Soni | License: MIT
"""FastMCP server: registers all tools, resources, and prompts for insurance QA."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from insurance_qa_mcp.prompts.templates import (
    plan_test_strategy_prompt,
    review_failures_prompt,
    triage_bug_prompt,
)
from insurance_qa_mcp.resources.insurance_domain import get_insurance_lines, get_test_patterns
from insurance_qa_mcp.resources.project_scanner import scan_projects
from insurance_qa_mcp.tools.bdd_generator import generate_bdd_scenarios_impl
from insurance_qa_mcp.tools.code_analyzer import (
    analyze_coverage_impl,
    lint_code_impl,
    suggest_tests_impl,
)
from insurance_qa_mcp.tools.data_generator import generate_test_data_impl
from insurance_qa_mcp.tools.test_runner import (
    check_test_health_impl,
    find_flaky_tests_impl,
    run_tests_impl,
)
from insurance_qa_mcp.tools.validators import validate_claim_impl, validate_policy_impl

# Bridge imports (external project integrations)
from insurance_qa_mcp.tools.bridges.playwright_bridge import (
    generate_playwright_tests_impl,
    run_playwright_audit_impl,
)
from insurance_qa_mcp.tools.bridges.code_review_bridge import review_code_impl
from insurance_qa_mcp.tools.bridges.test_gen_bridge import auto_generate_tests_impl
from insurance_qa_mcp.tools.bridges.embedkit_bridge import (
    get_knowledge_base_info,
    semantic_search_impl,
)
from insurance_qa_mcp.tools.bridges.chaos_test_bridge import chaos_test_api_impl

# Connector imports (mock enterprise integrations)
from insurance_qa_mcp.connectors.ado_connector import (
    get_ado_stories_resource,
    get_test_plan_impl,
    get_user_stories_impl,
)
from insurance_qa_mcp.connectors.zephyr_connector import (
    get_test_cycles_impl,
    get_zephyr_cycles_resource,
    update_test_result_impl,
)
from insurance_qa_mcp.connectors.sql_connector import (
    query_test_data_impl,
    validate_data_integrity_impl,
)

# Orchestrator
from insurance_qa_mcp.orchestrator import run_qa_workflow_impl

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "insurance-qa",
    instructions=(
        "QA automation tools for insurance domain testing. "
        "Provides test execution, synthetic data generation, code analysis, "
        "insurance business-rule validation, BDD scenario generation, "
        "Playwright test generation, multi-agent code review, semantic search, "
        "chaos testing, mock enterprise connectors (ADO, Zephyr, SQL), "
        "and a natural-language QA workflow orchestrator."
    ),
)


# =========================================================================
# CORE TOOLS (10)
# =========================================================================


@mcp.tool()
def run_tests(project_path: str, markers: str = "") -> str:
    """Run pytest on a project and return a pass/fail summary.

    Args:
        project_path: Absolute path to the project containing tests.
        markers: Optional pytest marker expression (e.g. "not slow").
    """
    return run_tests_impl(project_path, markers)


@mcp.tool()
def generate_test_data(
    line_of_business: str = "personal_auto",
    count: int = 10,
    data_type: str = "policy",
    seed: int | None = None,
) -> str:
    """Generate synthetic insurance test data (policies, claims, billing).

    Args:
        line_of_business: Insurance LOB (e.g. "personal_auto", "homeowners").
        count: Number of records to generate (1-1000).
        data_type: One of "policy", "claim", or "billing".
        seed: Optional random seed for reproducibility.
    """
    return generate_test_data_impl(line_of_business, count, data_type, seed)


@mcp.tool()
def analyze_coverage(project_path: str, threshold: float = 80.0) -> str:
    """Parse coverage reports and identify uncovered code paths.

    Args:
        project_path: Absolute path to the project root.
        threshold: Minimum acceptable coverage percentage (default 80%).
    """
    return analyze_coverage_impl(project_path, threshold)


@mcp.tool()
def find_flaky_tests(project_path: str, iterations: int = 5) -> str:
    """Run tests multiple times and detect non-deterministic (flaky) results.

    Args:
        project_path: Absolute path to the project.
        iterations: Number of times to run the suite (2-50, default 5).
    """
    return find_flaky_tests_impl(project_path, iterations)


@mcp.tool()
def lint_code(file_path: str) -> str:
    """Run Python code quality checks: complexity, naming, type hints, docstrings.

    Args:
        file_path: Absolute path to a .py file.
    """
    return lint_code_impl(file_path)


@mcp.tool()
def validate_claim(claim_data: dict) -> str:
    """Validate an insurance claim record against P&C business rules.

    Checks loss dates, amounts, status, and LOB-specific constraints.

    Args:
        claim_data: Dictionary with claim fields (claim_number, policy_number,
            line_of_business, loss_date, reported_date, loss_amount, etc.).
    """
    return validate_claim_impl(claim_data)


@mcp.tool()
def validate_policy(policy_data: dict) -> str:
    """Validate an insurance policy record against underwriting rules.

    Checks dates, premium range, coverage limits, and status consistency.

    Args:
        policy_data: Dictionary with policy fields (policy_number,
            line_of_business, effective_date, expiration_date, premium, etc.).
    """
    return validate_policy_impl(policy_data)


@mcp.tool()
def generate_bdd_scenarios(
    feature: str = "claim_submission",
    domain: str = "property_casualty",
) -> str:
    """Generate BDD/Gherkin test scenarios for insurance workflows.

    Args:
        feature: Workflow name -- one of claim_submission, policy_binding,
            billing_payment, claim_adjudication, policy_renewal.
        domain: Insurance domain context (default "property_casualty").
    """
    return generate_bdd_scenarios_impl(feature, domain)


@mcp.tool()
def check_test_health(project_path: str) -> str:
    """Analyze test suite health: test count, naming, structure, and distribution.

    Args:
        project_path: Absolute path to the project.
    """
    return check_test_health_impl(project_path)


@mcp.tool()
def suggest_tests(file_path: str) -> str:
    """Analyze source code and suggest missing test cases.

    Inspects functions for branches, error handling, and loops, then
    recommends specific tests to add.

    Args:
        file_path: Absolute path to a .py source file.
    """
    return suggest_tests_impl(file_path)


# =========================================================================
# BRIDGE TOOLS (7) -- External project integrations
# =========================================================================


@mcp.tool()
def generate_playwright_tests(url: str, workflow: str) -> str:
    """Generate Playwright test scripts from natural language workflow descriptions.

    Args:
        url: Target URL for the generated tests.
        workflow: Natural language description of the test workflow.
    """
    return generate_playwright_tests_impl(url, workflow)


@mcp.tool()
def run_playwright_audit(url: str) -> str:
    """Run accessibility and performance audit concepts on a URL.

    Args:
        url: Target URL for the audit.
    """
    return run_playwright_audit_impl(url)


@mcp.tool()
def review_code(file_path: str, profile: str = "standard") -> str:
    """Run multi-agent code review (security, performance, style agents).

    Args:
        file_path: Absolute path to a .py file.
        profile: Review profile -- "standard", "strict", or "security".
    """
    return review_code_impl(file_path, profile)


@mcp.tool()
def auto_generate_tests(source_path: str) -> str:
    """Analyze Python source and generate test cases automatically.

    Args:
        source_path: Absolute path to a .py source file.
    """
    return auto_generate_tests_impl(source_path)


@mcp.tool()
def semantic_search(query: str, documents_dir: str) -> str:
    """Search documents using semantic similarity (embeddings or TF-IDF fallback).

    Args:
        query: Natural language search query.
        documents_dir: Path to a directory containing documents to search.
    """
    return semantic_search_impl(query, documents_dir)


@mcp.tool()
def chaos_test_api(spec_path: str, base_url: str = "") -> str:
    """Generate chaos test scenarios from an OpenAPI specification.

    Produces boundary value, type confusion, and edge case tests for each endpoint.

    Args:
        spec_path: Path to an OpenAPI JSON specification file.
        base_url: Optional base URL override for the API.
    """
    return chaos_test_api_impl(spec_path, base_url)


# =========================================================================
# CONNECTOR TOOLS (6) -- Mock enterprise integrations
# =========================================================================


@mcp.tool()
def get_user_stories(project: str, sprint: str = "current") -> str:
    """Get user stories with acceptance criteria from ADO/Jira (mock).

    Returns realistic insurance domain stories for PolicyCenter, ClaimCenter, BillingCenter.

    Args:
        project: Project name (e.g., "PolicyCenter", "ClaimCenter").
        sprint: Sprint identifier or "current" for the active sprint.
    """
    return get_user_stories_impl(project, sprint)


@mcp.tool()
def get_test_plan(story_id: str) -> str:
    """Get a test plan linked to a user story (mock).

    Args:
        story_id: The user story identifier (e.g., "US-1001").
    """
    return get_test_plan_impl(story_id)


@mcp.tool()
def get_test_cycles(project: str) -> str:
    """Get current test cycles from Zephyr test management (mock).

    Args:
        project: Project name (e.g., "PolicyCenter", "ClaimCenter").
    """
    return get_test_cycles_impl(project)


@mcp.tool()
def update_test_result(test_id: str, status: str, notes: str) -> str:
    """Update test execution result in Zephyr (mock).

    Args:
        test_id: Test case identifier (e.g., "TC-3001").
        status: Execution status -- "passed", "failed", "blocked", or "not_run".
        notes: Execution notes or comments.
    """
    return update_test_result_impl(test_id, status, notes)


@mcp.tool()
def query_test_data(table: str, filters: str = "") -> str:
    """Query insurance test data from mock SQL Server database.

    Available tables: cc_claim, pc_policy, bc_billing.

    Args:
        table: Table name (e.g., "cc_claim", "pc_policy", "bc_billing").
        filters: Optional filters (e.g., "Status=open,LobCode=personal_auto").
    """
    return query_test_data_impl(table, filters)


@mcp.tool()
def validate_data_integrity(table: str) -> str:
    """Run data quality checks on a mock database table.

    Args:
        table: Table name to validate.
    """
    return validate_data_integrity_impl(table)


# =========================================================================
# ORCHESTRATOR TOOL (1) -- Workflow automation
# =========================================================================


@mcp.tool()
def run_qa_workflow(request: str) -> str:
    """Take a natural language QA request and chain multiple tools together.

    Routes requests to appropriate tool sequences. Examples:
    - "Create test cases for this story"
    - "Run full regression and report to Zephyr"
    - "Review code and suggest tests"

    Args:
        request: Natural language QA request.
    """
    return run_qa_workflow_impl(request)


# =========================================================================
# RESOURCES (7)
# =========================================================================


@mcp.resource("qa://projects")
def list_projects() -> str:
    """List all available projects with test status."""
    return scan_projects()


@mcp.resource("qa://coverage/{project}")
def get_coverage(project: str) -> str:
    """Get coverage data for a specific project."""
    return analyze_coverage_impl(project)


@mcp.resource("qa://insurance/lines")
def insurance_lines() -> str:
    """Available insurance lines of business and their attributes."""
    return get_insurance_lines()


@mcp.resource("qa://test-patterns")
def test_patterns() -> str:
    """Common QA test patterns and templates for insurance applications."""
    return get_test_patterns()


@mcp.resource("qa://knowledge-base")
def knowledge_base() -> str:
    """Available indexed documents in the knowledge base."""
    return get_knowledge_base_info()


@mcp.resource("qa://ado/stories")
def ado_stories() -> str:
    """List of available ADO/Jira user stories."""
    return get_ado_stories_resource()


@mcp.resource("qa://zephyr/cycles")
def zephyr_cycles() -> str:
    """Current test cycles across all projects."""
    return get_zephyr_cycles_resource()


# =========================================================================
# PROMPTS (3)
# =========================================================================


@mcp.prompt()
def review_failures(test_results: str) -> str:
    """Analyze test failures: root cause, priority, fixes, and pattern detection."""
    return review_failures_prompt(test_results)


@mcp.prompt()
def plan_test_strategy(
    project_description: str,
    current_coverage: str = "",
) -> str:
    """Plan test coverage strategy: test pyramid, domain coverage, data, and priorities."""
    return plan_test_strategy_prompt(project_description, current_coverage)


@mcp.prompt()
def triage_bug(
    bug_description: str,
    environment: str = "QA",
    line_of_business: str = "",
) -> str:
    """Triage a bug with insurance domain context: severity, impact, root cause, action."""
    return triage_bug_prompt(bug_description, environment, line_of_business)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Start the Insurance QA MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
