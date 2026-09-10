# Author: Maharshi Soni | License: MIT
"""MCP prompt templates for QA review, planning, and triage workflows."""

from __future__ import annotations


def review_failures_prompt(test_results: str) -> str:
    """Generate a prompt for analyzing test failures.

    The AI assistant receives the test output and is asked to diagnose
    root causes, suggest fixes, and identify patterns.

    Args:
        test_results: Raw test output (pytest console output or JSON summary).

    Returns:
        A structured prompt string for the AI to analyze.
    """
    return f"""You are a senior QA engineer reviewing test failures in an insurance application.

## Test Results
{test_results}

## Your Task
Analyze these test failures and provide:

1. **Root Cause Analysis**: For each failure, identify the most likely root cause.
   Consider:
   - Data setup issues (missing fixtures, stale test data)
   - Race conditions or ordering dependencies
   - Environment differences (config, database state)
   - Actual bugs in the application code
   - Insurance domain logic errors (wrong business rules)

2. **Fix Priority**: Rank failures by severity:
   - CRITICAL: Blocks deployment or affects core business flow (e.g., claim submission, policy binding)
   - HIGH: Affects important functionality but has workarounds
   - MEDIUM: Non-critical feature regression
   - LOW: Cosmetic or edge case issues

3. **Suggested Fixes**: For each failure, provide:
   - The specific code change needed
   - Whether the fix is in the test or the application
   - Any related tests that might also be affected

4. **Pattern Detection**: Look for common patterns across failures:
   - Are multiple tests failing for the same reason?
   - Is there a systemic issue (e.g., database connection, API contract change)?
   - Are failures clustered in a specific module or LOB?

Respond with a structured analysis using the sections above."""


def plan_test_strategy_prompt(
    project_description: str,
    current_coverage: str = "",
) -> str:
    """Generate a prompt for planning test coverage strategy.

    Args:
        project_description: Description of the project and its features.
        current_coverage: Optional current coverage data.

    Returns:
        A structured prompt string for test strategy planning.
    """
    coverage_section = ""
    if current_coverage:
        coverage_section = f"""
## Current Coverage
{current_coverage}
"""

    return f"""You are a QA architect planning the test strategy for an insurance application.

## Project Description
{project_description}
{coverage_section}
## Your Task
Create a comprehensive test strategy covering:

1. **Test Pyramid**:
   - Unit tests: Which functions and classes need unit tests?
   - Integration tests: Which component interactions need testing?
   - E2E tests: Which critical user workflows need end-to-end coverage?

2. **Insurance Domain Coverage**:
   - Policy lifecycle: quote, bind, endorse, renew, cancel
   - Claim lifecycle: FNOL, investigation, adjudication, payment, close
   - Billing: installment plans, payments, delinquency, cancellation
   - Regulatory compliance: state-specific rules, filing requirements

3. **Test Data Strategy**:
   - What synthetic data is needed for each test category?
   - How to handle Guidewire-specific data (e.g., PolicyCenter entities)?
   - Data isolation between test runs

4. **Risk-Based Priorities**:
   - Which areas have the highest business impact if broken?
   - Which areas have the most complex logic?
   - Which areas change most frequently?

5. **Automation Approach**:
   - Test framework recommendations
   - CI/CD integration points
   - Flaky test mitigation strategy
   - Performance testing for high-volume operations (batch processing, renewals)

Respond with a structured test strategy using the sections above."""


def triage_bug_prompt(
    bug_description: str,
    environment: str = "QA",
    line_of_business: str = "",
) -> str:
    """Generate a prompt for bug triage with insurance domain context.

    Args:
        bug_description: Description of the bug or defect.
        environment: Environment where the bug was found (QA, staging, production).
        line_of_business: Affected LOB (e.g., ``"personal_auto"``).

    Returns:
        A structured prompt string for bug triage.
    """
    lob_context = ""
    if line_of_business:
        lob_context = f"""
## Line of Business Context
This bug affects the **{line_of_business.replace('_', ' ').title()}** line of business.
Consider LOB-specific business rules and regulatory requirements in your analysis.
"""

    return f"""You are a QA lead triaging a bug in a Guidewire-based insurance application.

## Bug Report
**Environment**: {environment}
{bug_description}
{lob_context}
## Your Task
Perform a thorough bug triage:

1. **Severity Assessment**:
   - BLOCKER: System unusable, data corruption, or regulatory violation
   - CRITICAL: Core business function broken (claims, policies, billing)
   - MAJOR: Important feature broken with no workaround
   - MINOR: Feature works but with incorrect behavior in edge cases
   - TRIVIAL: Cosmetic issue or minor inconvenience

2. **Impact Analysis**:
   - Which users/roles are affected?
   - Which insurance operations are blocked?
   - Is there financial impact (incorrect premium, wrong claim payment)?
   - Are there regulatory/compliance implications?
   - How many policies/claims could be affected?

3. **Root Cause Hypothesis**:
   - Is this likely a Guidewire configuration issue?
   - Is it a custom code defect?
   - Is it a data issue (migration, integration)?
   - Is it an environment-specific problem?

4. **Reproduction Steps**:
   - Minimal steps to reproduce
   - Required test data setup
   - Expected vs. actual behavior

5. **Recommended Action**:
   - Immediate workaround (if any)
   - Fix approach and estimated effort
   - Regression test requirements
   - Whether a hotfix is warranted

Respond with a structured triage report using the sections above."""
