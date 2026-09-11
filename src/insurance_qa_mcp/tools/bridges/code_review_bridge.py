# Author: Maharshi Soni | License: MIT
"""Bridge wrapping multi-agent-code-reviewer concepts as MCP tools.

Performs multi-agent code review using AST-based analysis covering
security, performance, and style agents.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any


def review_code_impl(file_path: str, profile: str = "standard") -> str:
    """Run multi-agent code review on a Python file.

    Simulates three review agents: security, performance, and style.
    Each agent performs AST-based analysis and reports findings.

    Args:
        file_path: Absolute path to the Python file to review.
        profile: Review profile -- "standard", "strict", or "security".

    Returns:
        JSON string with findings from all review agents.
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

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return json.dumps({"error": f"Syntax error in file: {exc}"})

    security_findings = _security_agent(tree, source)
    performance_findings = _performance_agent(tree, source)
    style_findings = _style_agent(tree, source, profile)

    all_findings = security_findings + performance_findings + style_findings
    severity_counts: dict[str, int] = {}
    for f in all_findings:
        sev = f["severity"]
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return json.dumps(
        {
            "file": file_path,
            "profile": profile,
            "total_findings": len(all_findings),
            "severity_summary": severity_counts,
            "security": security_findings,
            "performance": performance_findings,
            "style": style_findings,
            "overall_rating": _compute_rating(all_findings),
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Review Agents
# ---------------------------------------------------------------------------


def _security_agent(tree: ast.Module, source: str) -> list[dict[str, Any]]:
    """Security-focused code review agent."""
    findings: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        # Check for eval/exec usage
        if isinstance(node, ast.Call):
            func_name = _get_call_name(node)
            if func_name in ("eval", "exec"):
                findings.append({
                    "agent": "security",
                    "severity": "critical",
                    "line": node.lineno,
                    "rule": "SEC-001",
                    "message": f"Use of '{func_name}()' is a code injection risk",
                    "suggestion": f"Replace {func_name}() with a safer alternative (e.g., ast.literal_eval for eval)",
                })
            elif func_name == "subprocess.call" or func_name == "os.system":
                findings.append({
                    "agent": "security",
                    "severity": "high",
                    "line": node.lineno,
                    "rule": "SEC-002",
                    "message": f"Shell command execution via {func_name}() -- use subprocess.run with shell=False",
                    "suggestion": "Use subprocess.run() with explicit argument lists instead of shell strings",
                })
            elif func_name == "pickle.loads" or func_name == "pickle.load":
                findings.append({
                    "agent": "security",
                    "severity": "high",
                    "line": node.lineno,
                    "rule": "SEC-003",
                    "message": "Deserializing untrusted data with pickle is a remote code execution risk",
                    "suggestion": "Use json.loads() or a safe serialization format",
                })

        # Check for hardcoded credentials
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name_lower = target.id.lower()
                    if any(kw in name_lower for kw in ("password", "secret", "api_key", "token")):
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            findings.append({
                                "agent": "security",
                                "severity": "critical",
                                "line": node.lineno,
                                "rule": "SEC-004",
                                "message": f"Hardcoded credential in variable '{target.id}'",
                                "suggestion": "Use environment variables or a secrets manager",
                            })

    # Check for SQL injection patterns in source
    sql_patterns = re.findall(
        r'(?:execute|cursor\.execute)\s*\(\s*["\'].*%s.*["\']',
        source,
    )
    if sql_patterns:
        findings.append({
            "agent": "security",
            "severity": "high",
            "line": 0,
            "rule": "SEC-005",
            "message": "Potential SQL injection: string formatting in SQL query",
            "suggestion": "Use parameterized queries with placeholders",
        })

    return findings


def _performance_agent(tree: ast.Module, source: str) -> list[dict[str, Any]]:
    """Performance-focused code review agent."""
    findings: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        # Nested loops (O(n^2) potential)
        if isinstance(node, (ast.For, ast.While)):
            for child in ast.walk(node):
                if child is not node and isinstance(child, (ast.For, ast.While)):
                    findings.append({
                        "agent": "performance",
                        "severity": "warning",
                        "line": node.lineno,
                        "rule": "PERF-001",
                        "message": "Nested loop detected -- potential O(n^2) complexity",
                        "suggestion": "Consider using dict lookups, sets, or itertools for better performance",
                    })
                    break

        # String concatenation in loops
        if isinstance(node, (ast.For, ast.While)):
            for child in ast.walk(node):
                if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                    if isinstance(child.target, ast.Name):
                        findings.append({
                            "agent": "performance",
                            "severity": "info",
                            "line": child.lineno,
                            "rule": "PERF-002",
                            "message": "String concatenation in loop -- use list append and join",
                            "suggestion": "Collect items in a list and use ''.join() after the loop",
                        })
                        break

        # Large function bodies
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_lines = (node.end_lineno or node.lineno) - node.lineno
            if body_lines > 75:
                findings.append({
                    "agent": "performance",
                    "severity": "warning",
                    "line": node.lineno,
                    "rule": "PERF-003",
                    "message": f"Function '{node.name}' is {body_lines} lines -- hard to optimize",
                    "suggestion": "Break into smaller functions for better readability and caching",
                })

    # Check for global imports that could be deferred
    top_level_imports = sum(
        1 for n in ast.iter_child_nodes(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
    )
    if top_level_imports > 15:
        findings.append({
            "agent": "performance",
            "severity": "info",
            "line": 1,
            "rule": "PERF-004",
            "message": f"File has {top_level_imports} top-level imports -- startup may be slow",
            "suggestion": "Consider lazy imports for rarely-used modules",
        })

    return findings


def _style_agent(tree: ast.Module, source: str, profile: str) -> list[dict[str, Any]]:
    """Style and maintainability review agent."""
    findings: list[dict[str, Any]] = []
    max_line_len = 100 if profile == "strict" else 120

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Missing docstring
            has_docstring = (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            )
            if not has_docstring and not node.name.startswith("_"):
                findings.append({
                    "agent": "style",
                    "severity": "warning" if profile == "strict" else "info",
                    "line": node.lineno,
                    "rule": "STY-001",
                    "message": f"Public function '{node.name}' missing docstring",
                    "suggestion": "Add a docstring describing purpose, args, and return value",
                })

            # Too many parameters
            param_count = len(node.args.args)
            if node.args.args and node.args.args[0].arg in ("self", "cls"):
                param_count -= 1
            if param_count > 5:
                findings.append({
                    "agent": "style",
                    "severity": "warning",
                    "line": node.lineno,
                    "rule": "STY-002",
                    "message": f"Function '{node.name}' has {param_count} parameters (max 5)",
                    "suggestion": "Group related parameters into a dataclass or dict",
                })

            # Missing return type annotation
            if node.returns is None and not node.name.startswith("_"):
                findings.append({
                    "agent": "style",
                    "severity": "info",
                    "line": node.lineno,
                    "rule": "STY-003",
                    "message": f"Function '{node.name}' missing return type annotation",
                    "suggestion": "Add -> ReturnType annotation",
                })

    # Line length check
    for i, line in enumerate(source.splitlines(), start=1):
        if len(line) > max_line_len:
            findings.append({
                "agent": "style",
                "severity": "info",
                "line": i,
                "rule": "STY-004",
                "message": f"Line is {len(line)} chars (max {max_line_len})",
                "suggestion": "Break long lines for readability",
            })
            if len(findings) > 50:
                break

    return findings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_call_name(node: ast.Call) -> str:
    """Extract the function name from an ast.Call node."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name):
            return f"{node.func.value.id}.{node.func.attr}"
        return node.func.attr
    return ""


def _compute_rating(findings: list[dict[str, Any]]) -> str:
    """Compute an overall code quality rating from findings."""
    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    warning = sum(1 for f in findings if f["severity"] == "warning")

    if critical > 0:
        return "FAIL -- critical issues found"
    if high > 2:
        return "NEEDS WORK -- multiple high-severity issues"
    if high > 0 or warning > 5:
        return "ACCEPTABLE -- some issues to address"
    return "GOOD -- minor issues only"
