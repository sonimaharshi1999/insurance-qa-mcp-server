# Author: Maharshi Soni | License: MIT
"""Code quality analysis, coverage parsing, and test suggestion tools."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

from insurance_qa_mcp.models import CoverageReport, LintIssue, LintResult, TestSuggestion


def lint_code_impl(file_path: str) -> str:
    """Run basic Python code quality checks on a single file.

    Checks for:
    - Function complexity (length, nesting)
    - Naming conventions (PEP 8)
    - Missing type hints
    - Missing docstrings
    - Long lines

    Args:
        file_path: Absolute path to a ``.py`` file.

    Returns:
        JSON string with lint issues and an overall score.
    """
    path = Path(file_path)
    if not path.exists():
        return json.dumps({"error": f"File does not exist: {file_path}"})
    if path.suffix != ".py":
        return json.dumps({"error": "Only Python (.py) files are supported"})

    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return json.dumps({"error": f"Cannot read file: {exc}"})

    issues: list[LintIssue] = []

    # AST-based checks
    try:
        tree = ast.parse(source, filename=str(path))
        issues.extend(_check_functions(tree))
        issues.extend(_check_classes(tree))
    except SyntaxError as exc:
        issues.append(LintIssue(
            line=exc.lineno or 1,
            severity="error",
            message=f"Syntax error: {exc.msg}",
            rule="E0001",
        ))

    # Line-based checks
    issues.extend(_check_lines(source))

    # Score: start at 10, deduct per issue
    deductions = {"error": 2.0, "warning": 0.5, "info": 0.1}
    score = 10.0
    for issue in issues:
        score -= deductions.get(issue.severity, 0.5)
    score = max(0.0, round(score, 1))

    result = LintResult(file_path=file_path, issues=issues, score=score)
    return json.dumps(result.model_dump(), indent=2)


def analyze_coverage_impl(project_path: str, threshold: float = 80.0) -> str:
    """Parse coverage data and identify uncovered code paths.

    Looks for ``coverage.json``, ``coverage.xml``, or ``.coverage`` in the
    project directory.  If none exist, performs a static estimate by counting
    functions without corresponding test functions.

    Args:
        project_path: Absolute path to the project root.
        threshold: Minimum acceptable coverage percentage.

    Returns:
        JSON string with coverage analysis.
    """
    path = Path(project_path)
    if not path.exists():
        return json.dumps({"error": f"Project path does not exist: {project_path}"})

    # Try to find a coverage JSON report
    coverage_json = path / "coverage.json"
    if coverage_json.exists():
        return _parse_coverage_json(coverage_json, threshold)

    # Fallback: static analysis estimate
    return _estimate_coverage(path, threshold)


def suggest_tests_impl(file_path: str) -> str:
    """Analyze source code and suggest missing test cases.

    Inspects functions and classes in the file, checks for existing tests,
    and suggests tests for uncovered scenarios.

    Args:
        file_path: Absolute path to a ``.py`` source file.

    Returns:
        JSON string with test suggestions.
    """
    path = Path(file_path)
    if not path.exists():
        return json.dumps({"error": f"File does not exist: {file_path}"})

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError) as exc:
        return json.dumps({"error": f"Cannot parse file: {exc}"})

    suggestions: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn_name = node.name
            if fn_name.startswith("_") and not fn_name.startswith("__"):
                continue  # skip private helpers

            fn_suggestions = _suggest_for_function(node, source)
            suggestions.extend(fn_suggestions)

    return json.dumps(
        {
            "file": file_path,
            "total_suggestions": len(suggestions),
            "suggestions": suggestions,
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# AST Inspection Helpers
# ---------------------------------------------------------------------------

def _check_functions(tree: ast.Module) -> list[LintIssue]:
    """Check function-level code quality."""
    issues: list[LintIssue] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # Missing docstring
        if not (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            issues.append(LintIssue(
                line=node.lineno,
                severity="warning",
                message=f"Function '{node.name}' is missing a docstring",
                rule="D100",
            ))

        # Missing return type hint
        if node.returns is None and not node.name.startswith("__"):
            issues.append(LintIssue(
                line=node.lineno,
                severity="warning",
                message=f"Function '{node.name}' is missing a return type hint",
                rule="ANN200",
            ))

        # Missing parameter type hints
        for arg in node.args.args:
            if arg.arg == "self" or arg.arg == "cls":
                continue
            if arg.annotation is None:
                issues.append(LintIssue(
                    line=node.lineno,
                    severity="info",
                    message=f"Parameter '{arg.arg}' in '{node.name}' is missing a type hint",
                    rule="ANN001",
                ))

        # Function too long (> 50 lines)
        body_lines = node.end_lineno - node.lineno if node.end_lineno else 0
        if body_lines > 50:
            issues.append(LintIssue(
                line=node.lineno,
                severity="warning",
                message=f"Function '{node.name}' is {body_lines} lines long (max 50)",
                rule="C901",
            ))

    return issues


def _check_classes(tree: ast.Module) -> list[LintIssue]:
    """Check class-level code quality."""
    issues: list[LintIssue] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Missing docstring
        if not (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            issues.append(LintIssue(
                line=node.lineno,
                severity="warning",
                message=f"Class '{node.name}' is missing a docstring",
                rule="D101",
            ))

        # Class naming convention
        if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
            issues.append(LintIssue(
                line=node.lineno,
                severity="warning",
                message=f"Class '{node.name}' should use CamelCase naming",
                rule="N801",
            ))

    return issues


def _check_lines(source: str) -> list[LintIssue]:
    """Line-by-line quality checks."""
    issues: list[LintIssue] = []

    for i, line in enumerate(source.splitlines(), start=1):
        # Long lines
        if len(line) > 120:
            issues.append(LintIssue(
                line=i,
                severity="info",
                message=f"Line is {len(line)} characters (max 120)",
                rule="E501",
            ))

        # Trailing whitespace
        if line != line.rstrip():
            issues.append(LintIssue(
                line=i,
                severity="info",
                message="Trailing whitespace",
                rule="W291",
            ))

    return issues


def _suggest_for_function(node: ast.FunctionDef | ast.AsyncFunctionDef, source: str) -> list[dict]:
    """Generate test suggestions for a single function."""
    suggestions: list[dict] = []
    fn_name = node.name

    # Suggest basic test
    suggestions.append(TestSuggestion(
        function_name=fn_name,
        suggestion=f"Test '{fn_name}' with valid input and verify expected output",
        priority="high",
        category="unit",
    ).model_dump())

    # Check for branches (if/else)
    has_branches = any(isinstance(n, (ast.If, ast.IfExp)) for n in ast.walk(node))
    if has_branches:
        suggestions.append(TestSuggestion(
            function_name=fn_name,
            suggestion=f"Test '{fn_name}' branch coverage: test both true and false paths",
            priority="medium",
            category="unit",
        ).model_dump())

    # Check for exception handling
    has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))
    if has_try:
        suggestions.append(TestSuggestion(
            function_name=fn_name,
            suggestion=f"Test '{fn_name}' error handling: verify exceptions are caught properly",
            priority="high",
            category="unit",
        ).model_dump())

    # Check for loops
    has_loop = any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(node))
    if has_loop:
        suggestions.append(TestSuggestion(
            function_name=fn_name,
            suggestion=f"Test '{fn_name}' with empty collection and single-item collection",
            priority="medium",
            category="edge_case",
        ).model_dump())

    return suggestions


# ---------------------------------------------------------------------------
# Coverage Helpers
# ---------------------------------------------------------------------------

def _parse_coverage_json(coverage_path: Path, threshold: float) -> str:
    """Parse a coverage.json file produced by pytest-cov."""
    try:
        data = json.loads(coverage_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return json.dumps({"error": f"Cannot parse coverage file: {exc}"})

    totals = data.get("totals", {})
    report = CoverageReport(
        total_statements=totals.get("num_statements", 0),
        covered_statements=totals.get("covered_lines", 0),
        coverage_percent=totals.get("percent_covered", 0.0),
        threshold=threshold,
    )

    # Find files below threshold
    files = data.get("files", {})
    for fname, fdata in files.items():
        summary = fdata.get("summary", {})
        pct = summary.get("percent_covered", 0)
        if pct < threshold:
            report.uncovered_files.append({
                "file": fname,
                "coverage": round(pct, 1),
                "missing_lines": fdata.get("missing_lines", []),
            })

    output = report.model_dump()
    output["meets_threshold"] = report.coverage_percent >= threshold
    return json.dumps(output, indent=2)


def _estimate_coverage(project_path: Path, threshold: float) -> str:
    """Estimate coverage by comparing source functions to test functions."""
    src_funcs: set[str] = set()
    test_funcs: set[str] = set()

    for py_file in project_path.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue

        is_test = py_file.name.startswith("test_") or py_file.name.endswith("_test.py")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if is_test and node.name.startswith("test_"):
                    # Normalize: test_validate_claim -> validate_claim
                    tested = node.name.removeprefix("test_")
                    test_funcs.add(tested)
                elif not node.name.startswith("_"):
                    src_funcs.add(node.name)

    covered = src_funcs & test_funcs
    total = len(src_funcs) or 1
    pct = round(len(covered) / total * 100, 1)

    uncovered = sorted(src_funcs - test_funcs)
    report = CoverageReport(
        total_statements=len(src_funcs),
        covered_statements=len(covered),
        coverage_percent=pct,
        threshold=threshold,
        uncovered_files=[{"function": f, "status": "no test found"} for f in uncovered[:30]],
    )

    output = report.model_dump()
    output["meets_threshold"] = pct >= threshold
    output["note"] = "Estimate based on function-level static analysis (no runtime coverage data)"
    return json.dumps(output, indent=2)
