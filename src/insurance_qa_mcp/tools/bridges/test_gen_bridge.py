# Author: Maharshi Soni | License: MIT
"""Bridge wrapping testpilot-ai functionality as MCP tools.

Attempts to import testpilot for test generation; falls back to
local AST-based analysis if the package is not installed.
"""

from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path
from typing import Any

# Graceful fallback: try testpilot, fall back to local AST analysis
try:
    from testpilot import generate_tests as _testpilot_generate  # type: ignore[import-untyped]
    _HAS_TESTPILOT = True
except ImportError:
    _HAS_TESTPILOT = False


def auto_generate_tests_impl(source_path: str) -> str:
    """Analyze Python source and generate test cases.

    Tries the testpilot package first; falls back to AST-based
    analysis when testpilot is not installed.

    Args:
        source_path: Absolute path to a Python source file.

    Returns:
        JSON string with generated test code and metadata.
    """
    path = Path(source_path)
    if not path.exists():
        return json.dumps({"error": f"File does not exist: {source_path}"})
    if path.suffix != ".py":
        return json.dumps({"error": "Only Python (.py) files are supported"})

    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return json.dumps({"error": f"Cannot read file: {exc}"})

    if _HAS_TESTPILOT:
        return _generate_via_testpilot(source, source_path)

    return _generate_via_ast(source, source_path)


def _generate_via_testpilot(source: str, source_path: str) -> str:
    """Use the testpilot package for test generation."""
    try:
        result = _testpilot_generate(source)  # type: ignore[name-defined]
        return json.dumps(
            {
                "source_file": source_path,
                "engine": "testpilot",
                "test_code": str(result),
            },
            indent=2,
        )
    except Exception as exc:
        return json.dumps({"error": f"testpilot generation failed: {exc}"})


def _generate_via_ast(source: str, source_path: str) -> str:
    """Fallback: AST-based test generation."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return json.dumps({"error": f"Cannot parse file: {exc}"})

    module_name = Path(source_path).stem
    functions = _extract_functions(tree)
    classes = _extract_classes(tree)

    test_cases: list[dict[str, Any]] = []
    test_code_lines: list[str] = [
        f'"""Auto-generated tests for {module_name}."""',
        "",
        "import pytest",
        f"from {module_name} import *",
        "",
        "",
    ]

    for func in functions:
        cases = _generate_function_tests(func)
        test_cases.extend(cases)
        for case in cases:
            test_code_lines.append(case["code"])
            test_code_lines.append("")

    for cls in classes:
        cases = _generate_class_tests(cls)
        test_cases.extend(cases)
        for case in cases:
            test_code_lines.append(case["code"])
            test_code_lines.append("")

    return json.dumps(
        {
            "source_file": source_path,
            "engine": "ast_fallback",
            "functions_found": len(functions),
            "classes_found": len(classes),
            "tests_generated": len(test_cases),
            "test_cases": test_cases,
            "test_code": "\n".join(test_code_lines),
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# AST Extraction
# ---------------------------------------------------------------------------


def _extract_functions(tree: ast.Module) -> list[dict[str, Any]]:
    """Extract top-level function signatures from AST."""
    functions: list[dict[str, Any]] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue
            params = []
            for arg in node.args.args:
                if arg.arg in ("self", "cls"):
                    continue
                annotation = ""
                if arg.annotation:
                    annotation = ast.unparse(arg.annotation)
                params.append({"name": arg.arg, "type": annotation})

            has_return = any(isinstance(n, ast.Return) and n.value for n in ast.walk(node))
            has_branches = any(isinstance(n, ast.If) for n in ast.walk(node))
            has_loops = any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(node))
            has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))

            functions.append({
                "name": node.name,
                "params": params,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "has_return": has_return,
                "has_branches": has_branches,
                "has_loops": has_loops,
                "has_try": has_try,
                "lineno": node.lineno,
            })
    return functions


def _extract_classes(tree: ast.Module) -> list[dict[str, Any]]:
    """Extract class definitions with their methods."""
    classes: list[dict[str, Any]] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not item.name.startswith("_") or item.name == "__init__":
                        methods.append(item.name)
            classes.append({
                "name": node.name,
                "methods": methods,
                "lineno": node.lineno,
            })
    return classes


# ---------------------------------------------------------------------------
# Test Generation
# ---------------------------------------------------------------------------


def _generate_function_tests(func: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate test cases for a function."""
    cases: list[dict[str, Any]] = []
    name = func["name"]
    params = func["params"]

    # Basic call test
    args_str = ", ".join(_default_value(p) for p in params)
    cases.append({
        "test_name": f"test_{name}_basic",
        "description": f"Test {name} with basic valid input",
        "category": "unit",
        "code": textwrap.dedent(f"""\
            def test_{name}_basic():
                \"\"\"Test {name} with valid input.\"\"\"
                result = {name}({args_str})
                assert result is not None"""),
    })

    # Branch coverage test
    if func["has_branches"]:
        cases.append({
            "test_name": f"test_{name}_branch_coverage",
            "description": f"Test {name} branch paths",
            "category": "branch",
            "code": textwrap.dedent(f"""\
                @pytest.mark.parametrize("input_val", [None, 0, "", [], {{}}])
                def test_{name}_edge_cases(input_val):
                    \"\"\"Test {name} with edge case inputs.\"\"\"
                    try:
                        result = {name}(input_val)
                    except (TypeError, ValueError):
                        pass  # Expected for invalid inputs"""),
        })

    # Error handling test
    if func["has_try"]:
        cases.append({
            "test_name": f"test_{name}_error_handling",
            "description": f"Test {name} error handling paths",
            "category": "error",
            "code": textwrap.dedent(f"""\
                def test_{name}_error_handling():
                    \"\"\"Test that {name} handles errors gracefully.\"\"\"
                    with pytest.raises(Exception):
                        {name}(None)"""),
        })

    return cases


def _generate_class_tests(cls: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate test cases for a class."""
    cases: list[dict[str, Any]] = []
    class_name = cls["name"]

    # Instantiation test
    cases.append({
        "test_name": f"test_{class_name.lower()}_instantiation",
        "description": f"Test {class_name} can be instantiated",
        "category": "unit",
        "code": textwrap.dedent(f"""\
            def test_{class_name.lower()}_instantiation():
                \"\"\"Test that {class_name} can be created.\"\"\"
                obj = {class_name}()
                assert obj is not None"""),
    })

    # Method tests
    for method in cls["methods"]:
        if method == "__init__":
            continue
        cases.append({
            "test_name": f"test_{class_name.lower()}_{method}",
            "description": f"Test {class_name}.{method}()",
            "category": "unit",
            "code": textwrap.dedent(f"""\
                def test_{class_name.lower()}_{method}():
                    \"\"\"Test {class_name}.{method}() method.\"\"\"
                    obj = {class_name}()
                    result = obj.{method}()
                    assert result is not None"""),
        })

    return cases


def _default_value(param: dict[str, str]) -> str:
    """Generate a default test value based on type annotation."""
    type_map: dict[str, str] = {
        "str": '"test"',
        "int": "1",
        "float": "1.0",
        "bool": "True",
        "list": "[]",
        "dict": "{}",
        "Optional": "None",
    }
    for type_hint, value in type_map.items():
        if type_hint in param.get("type", ""):
            return value
    return '"test_value"'
