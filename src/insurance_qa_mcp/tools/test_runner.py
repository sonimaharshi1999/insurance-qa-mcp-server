# Author: Maharshi Soni | License: MIT
"""Test execution and health analysis tools."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from insurance_qa_mcp.models import FlakyTestResult, TestHealthReport, TestResult


def run_tests_impl(project_path: str, markers: str = "") -> str:
    """Execute pytest on a project directory and return a pass/fail summary.

    Args:
        project_path: Absolute path to the project containing tests.
        markers: Optional pytest marker expression (e.g. ``"not slow"``).

    Returns:
        JSON string with test results including total, passed, failed counts.
    """
    path = Path(project_path)
    if not path.exists():
        return json.dumps({"error": f"Project path does not exist: {project_path}"})

    cmd = [sys.executable, "-m", "pytest", str(path), "-v", "--tb=short", "--no-header", "-q"]
    if markers:
        cmd.extend(["-m", markers])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(path),
        )
        output = proc.stdout + proc.stderr
        result = _parse_pytest_output(output)
        return json.dumps(result.model_dump(), indent=2)
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Test execution timed out after 300 seconds"})
    except Exception as exc:
        return json.dumps({"error": f"Failed to run tests: {exc}"})


def find_flaky_tests_impl(project_path: str, iterations: int = 5) -> str:
    """Run tests multiple times and detect non-deterministic (flaky) results.

    Args:
        project_path: Absolute path to the project.
        iterations: Number of times to run the suite (default 5).

    Returns:
        JSON string with flaky test analysis.
    """
    path = Path(project_path)
    if not path.exists():
        return json.dumps({"error": f"Project path does not exist: {project_path}"})

    iterations = max(2, min(iterations, 50))
    test_outcomes: dict[str, list[bool]] = {}

    for _ in range(iterations):
        cmd = [sys.executable, "-m", "pytest", str(path), "-v", "--tb=no", "--no-header"]
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120, cwd=str(path)
            )
            for line in proc.stdout.splitlines():
                if " PASSED" in line or " FAILED" in line:
                    parts = line.strip().split(" ")
                    test_name = parts[0] if parts else line.strip()
                    passed = "PASSED" in line
                    test_outcomes.setdefault(test_name, []).append(passed)
        except (subprocess.TimeoutExpired, Exception):
            continue

    results: list[dict] = []
    for test_name, outcomes in test_outcomes.items():
        passes = sum(outcomes)
        failures = len(outcomes) - passes
        is_flaky = 0 < failures < len(outcomes)
        flaky = FlakyTestResult(
            test_name=test_name,
            total_runs=len(outcomes),
            passes=passes,
            failures=failures,
            is_flaky=is_flaky,
            failure_rate=round(failures / len(outcomes) * 100, 1) if outcomes else 0,
        )
        results.append(flaky.model_dump())

    flaky_count = sum(1 for r in results if r["is_flaky"])
    return json.dumps(
        {
            "iterations": iterations,
            "total_tests": len(results),
            "flaky_tests": flaky_count,
            "results": [r for r in results if r["is_flaky"]] if flaky_count else results[:10],
        },
        indent=2,
    )


def check_test_health_impl(project_path: str) -> str:
    """Analyze test suite health: count, structure, and naming conventions.

    Args:
        project_path: Absolute path to the project.

    Returns:
        JSON string with test health metrics.
    """
    path = Path(project_path)
    if not path.exists():
        return json.dumps({"error": f"Project path does not exist: {project_path}"})

    test_files: list[Path] = []
    for pattern in ("test_*.py", "*_test.py"):
        test_files.extend(path.rglob(pattern))

    total_tests = 0
    test_distribution: dict[str, int] = {}
    slow_tests: list[str] = []
    issues: list[str] = []

    for tf in test_files:
        try:
            content = tf.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # Count test functions
        import re

        functions = re.findall(r"^(?:def|async def)\s+(test_\w+)", content, re.MULTILINE)
        count = len(functions)
        total_tests += count

        # Categorize
        category = _categorize_test_file(tf.name)
        test_distribution[category] = test_distribution.get(category, 0) + count

        # Check naming
        for fn in functions:
            if len(fn) < 10:
                issues.append(f"Short test name: {fn} in {tf.name}")

    report = TestHealthReport(
        total_tests=total_tests,
        avg_duration=0.0,
        failure_rate=0.0,
        slow_tests=slow_tests,
        test_distribution=test_distribution,
    )

    output = report.model_dump()
    output["test_files"] = len(test_files)
    output["issues"] = issues[:20]
    return json.dumps(output, indent=2)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_pytest_output(output: str) -> TestResult:
    """Extract pass/fail counts from pytest console output."""
    import re

    result = TestResult()
    lines = output.strip().splitlines()
    details: list[str] = []

    for line in lines:
        if "passed" in line or "failed" in line or "error" in line:
            match = re.search(
                r"(\d+)\s+passed(?:.*?(\d+)\s+failed)?(?:.*?(\d+)\s+error)?(?:.*?(\d+)\s+skipped)?",
                line,
            )
            if match:
                result.passed = int(match.group(1) or 0)
                result.failed = int(match.group(2) or 0)
                result.errors = int(match.group(3) or 0)
                result.skipped = int(match.group(4) or 0)
                result.total = result.passed + result.failed + result.errors + result.skipped

        if "FAILED" in line or "ERROR" in line:
            details.append(line.strip())

    # Fallback: count PASSED/FAILED lines
    if result.total == 0:
        passed = sum(1 for l in lines if " PASSED" in l)
        failed = sum(1 for l in lines if " FAILED" in l)
        if passed or failed:
            result.passed = passed
            result.failed = failed
            result.total = passed + failed

    result.details = details[:50]
    return result


def _categorize_test_file(filename: str) -> str:
    """Categorize a test file by its name pattern."""
    name = filename.lower()
    if "unit" in name:
        return "unit"
    if "integration" in name or "integ" in name:
        return "integration"
    if "e2e" in name or "end_to_end" in name:
        return "e2e"
    if "perf" in name or "performance" in name or "bench" in name:
        return "performance"
    if "smoke" in name:
        return "smoke"
    return "unit"
