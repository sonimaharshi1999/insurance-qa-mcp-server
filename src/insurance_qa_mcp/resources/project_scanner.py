# Author: Maharshi Soni | License: MIT
"""Project scanning resource: discovers projects and their test status."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from insurance_qa_mcp.config import config
from insurance_qa_mcp.models import ProjectInfo


def scan_projects(root_dir: str | None = None) -> str:
    """List all discoverable projects with basic test status.

    Scans the configured (or given) root directory for Python projects
    by looking for ``pyproject.toml``, ``setup.py``, or ``setup.cfg``.

    Args:
        root_dir: Override the configured projects directory.

    Returns:
        JSON string listing discovered projects.
    """
    base = Path(root_dir) if root_dir else config.resolve_projects_dir()
    if not base.exists():
        return json.dumps({"error": f"Directory does not exist: {base}", "projects": []})

    projects: list[dict[str, Any]] = []

    # Check if base itself is a project
    if _is_project(base):
        projects.append(_inspect_project(base).model_dump())
    else:
        # Scan one level deep
        for child in sorted(base.iterdir()):
            if child.is_dir() and _is_project(child):
                projects.append(_inspect_project(child).model_dump())

    return json.dumps(
        {"root": str(base), "project_count": len(projects), "projects": projects},
        indent=2,
    )


def _is_project(path: Path) -> bool:
    """Return True if *path* looks like a Python project."""
    markers = ("pyproject.toml", "setup.py", "setup.cfg")
    return any((path / m).exists() for m in markers)


def _inspect_project(path: Path) -> ProjectInfo:
    """Gather basic metadata about a project."""
    test_count = 0
    for pattern in ("test_*.py", "*_test.py"):
        for tf in path.rglob(pattern):
            try:
                content = tf.read_text(encoding="utf-8")
                import re
                test_count += len(
                    re.findall(r"^(?:def|async def)\s+test_", content, re.MULTILINE)
                )
            except (OSError, UnicodeDecodeError):
                continue

    # Check for coverage data
    coverage = 0.0
    cov_file = path / "coverage.json"
    if cov_file.exists():
        try:
            data = json.loads(cov_file.read_text(encoding="utf-8"))
            coverage = data.get("totals", {}).get("percent_covered", 0.0)
        except (json.JSONDecodeError, OSError):
            pass

    return ProjectInfo(
        name=path.name,
        path=str(path),
        test_count=test_count,
        status="has_tests" if test_count > 0 else "no_tests",
        coverage=round(coverage, 1),
    )
