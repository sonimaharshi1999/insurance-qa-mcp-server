# Author: Maharshi Soni | License: MIT
"""Bridge wrapping playwright-ai-test-generator concepts as MCP tools.

Generates Playwright test scripts from natural language workflow descriptions
and runs accessibility/performance audit concepts. Uses synthetic implementation
since Playwright requires a browser install.
"""

from __future__ import annotations

import json
import re
import textwrap
from typing import Any


def generate_playwright_tests_impl(url: str, workflow: str) -> str:
    """Generate Playwright test scripts from a natural language workflow description.

    Args:
        url: Target URL for the generated tests.
        workflow: Natural language description of the test workflow.

    Returns:
        JSON string with the generated Playwright test code.
    """
    if not url or not url.strip():
        return json.dumps({"error": "URL is required"})
    if not workflow or not workflow.strip():
        return json.dumps({"error": "Workflow description is required"})

    steps = _parse_workflow_steps(workflow)
    test_code = _generate_test_code(url, workflow, steps)
    page_object = _generate_page_object(url, steps)

    return json.dumps(
        {
            "url": url,
            "workflow": workflow,
            "steps_detected": len(steps),
            "test_code": test_code,
            "page_object": page_object,
            "framework": "playwright",
            "language": "python",
        },
        indent=2,
    )


def run_playwright_audit_impl(url: str) -> str:
    """Run accessibility and performance audit concepts on a URL.

    Args:
        url: Target URL for the audit.

    Returns:
        JSON string with audit findings.
    """
    if not url or not url.strip():
        return json.dumps({"error": "URL is required"})

    accessibility_checks = _generate_accessibility_audit(url)
    performance_checks = _generate_performance_audit(url)

    total_issues = len(accessibility_checks) + len(performance_checks)
    critical_count = sum(
        1 for c in accessibility_checks + performance_checks if c["severity"] == "critical"
    )

    return json.dumps(
        {
            "url": url,
            "total_issues": total_issues,
            "critical_issues": critical_count,
            "accessibility": accessibility_checks,
            "performance": performance_checks,
            "recommendations": [
                "Add ARIA labels to all interactive elements",
                "Ensure color contrast ratio meets WCAG 2.1 AA (4.5:1)",
                "Implement lazy loading for below-fold images",
                "Add keyboard navigation support to modal dialogs",
            ],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_workflow_steps(workflow: str) -> list[dict[str, str]]:
    """Parse a natural language workflow into structured test steps."""
    steps: list[dict[str, str]] = []
    action_patterns: list[tuple[str, str]] = [
        (r"(?:navigate|go|open|visit)\s+(?:to\s+)?(.+)", "navigate"),
        (r"(?:click|press|tap)\s+(?:on\s+)?(?:the\s+)?(.+)", "click"),
        (r"(?:fill|enter|type|input)\s+(.+?)(?:\s+(?:in|into)\s+(.+))?$", "fill"),
        (r"(?:select|choose|pick)\s+(.+?)(?:\s+from\s+(.+))?$", "select"),
        (r"(?:verify|check|assert|expect|see|confirm)\s+(.+)", "assert"),
        (r"(?:submit|send)\s+(?:the\s+)?(.+)", "submit"),
        (r"(?:wait|pause)\s+(?:for\s+)?(.+)", "wait"),
        (r"(?:upload|attach)\s+(.+)", "upload"),
        (r"(?:scroll)\s+(?:to\s+)?(.+)", "scroll"),
        (r"(?:login|log\s+in|sign\s+in)\s*(?:with\s+)?(.+)?", "login"),
    ]

    sentences = re.split(r"[,.\n;]+", workflow.lower())
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        matched = False
        for pattern, action_type in action_patterns:
            match = re.search(pattern, sentence)
            if match:
                steps.append({
                    "action": action_type,
                    "target": match.group(1).strip() if match.group(1) else "",
                    "description": sentence,
                })
                matched = True
                break

        if not matched and sentence:
            steps.append({
                "action": "custom",
                "target": sentence,
                "description": sentence,
            })

    if not steps:
        steps.append({
            "action": "navigate",
            "target": "page",
            "description": "navigate to the target page",
        })

    return steps


def _generate_test_code(url: str, workflow: str, steps: list[dict[str, str]]) -> str:
    """Generate Playwright Python test code from parsed steps."""
    step_lines: list[str] = []
    for i, step in enumerate(steps):
        action = step["action"]
        target = step["target"]
        desc = step["description"]

        if action == "navigate":
            step_lines.append(f'    await page.goto("{url}")')
        elif action == "click":
            selector = _to_selector(target)
            step_lines.append(f'    await page.click("{selector}")  # {desc}')
        elif action == "fill":
            selector = _to_selector(target)
            step_lines.append(f'    await page.fill("{selector}", "test_value")  # {desc}')
        elif action == "select":
            selector = _to_selector(target)
            step_lines.append(f'    await page.select_option("{selector}", "option_1")  # {desc}')
        elif action == "assert":
            step_lines.append(f'    await expect(page.locator("body")).to_contain_text("{target}")')
        elif action == "submit":
            step_lines.append(f'    await page.click("button[type=submit]")  # {desc}')
        elif action == "wait":
            step_lines.append(f'    await page.wait_for_timeout(1000)  # {desc}')
        elif action == "login":
            step_lines.append('    await page.fill("#username", "test_user")')
            step_lines.append('    await page.fill("#password", "test_pass")')
            step_lines.append('    await page.click("button[type=submit]")')
        elif action == "upload":
            step_lines.append(f'    await page.set_input_files("input[type=file]", "test.pdf")  # {desc}')
        elif action == "scroll":
            step_lines.append(f'    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # {desc}')
        else:
            step_lines.append(f"    # TODO: {desc}")

    steps_block = "\n".join(step_lines)
    safe_name = re.sub(r"[^a-z0-9]+", "_", workflow.lower())[:50].strip("_")

    return textwrap.dedent(f"""\
        import pytest
        from playwright.async_api import async_playwright, expect


        @pytest.mark.asyncio
        async def test_{safe_name}():
            \"\"\"Auto-generated test: {workflow}\"\"\"
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

        {steps_block}

                await browser.close()
    """)


def _generate_page_object(url: str, steps: list[dict[str, str]]) -> str:
    """Generate a simple Page Object Model class."""
    selectors: list[str] = []
    for step in steps:
        if step["action"] in ("click", "fill", "select"):
            sel_name = re.sub(r"[^a-z0-9]+", "_", step["target"].lower())[:30].strip("_")
            selectors.append(f'    {sel_name} = "{_to_selector(step["target"])}"')

    selector_block = "\n".join(selectors) if selectors else '    # Add selectors here'

    return textwrap.dedent(f"""\
        class PageObject:
            \"\"\"Page object for {url}\"\"\"
            URL = "{url}"

        {selector_block}

            def __init__(self, page):
                self.page = page

            async def navigate(self):
                await self.page.goto(self.URL)
    """)


def _to_selector(target: str) -> str:
    """Convert a natural language target to a CSS/test-id selector."""
    clean = target.strip().lower()
    if clean.startswith("#") or clean.startswith(".") or clean.startswith("["):
        return clean
    slug = re.sub(r"[^a-z0-9]+", "-", clean).strip("-")
    return f'[data-testid="{slug}"]'


def _generate_accessibility_audit(url: str) -> list[dict[str, Any]]:
    """Generate mock accessibility audit findings."""
    return [
        {
            "rule": "aria-label-missing",
            "severity": "critical",
            "element": "button.submit-claim",
            "description": "Interactive button missing ARIA label for screen readers",
            "wcag": "4.1.2",
        },
        {
            "rule": "color-contrast",
            "severity": "warning",
            "element": "span.status-text",
            "description": "Text color contrast ratio is 3.2:1, below WCAG AA minimum of 4.5:1",
            "wcag": "1.4.3",
        },
        {
            "rule": "form-label",
            "severity": "critical",
            "element": "input#policy-search",
            "description": "Form input missing associated label element",
            "wcag": "1.3.1",
        },
    ]


def _generate_performance_audit(url: str) -> list[dict[str, Any]]:
    """Generate mock performance audit findings."""
    return [
        {
            "rule": "render-blocking-resources",
            "severity": "warning",
            "description": "2 render-blocking stylesheets detected; consider async loading",
            "impact_ms": 350,
        },
        {
            "rule": "large-dom-size",
            "severity": "info",
            "description": "DOM contains 1,847 elements; consider virtualizing long lists",
            "impact_ms": 120,
        },
    ]
