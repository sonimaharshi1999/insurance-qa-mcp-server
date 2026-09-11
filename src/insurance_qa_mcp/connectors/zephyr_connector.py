# Author: Maharshi Soni | License: MIT
"""Mock Zephyr test management connector for test cycles and execution tracking."""

from __future__ import annotations

import json
from typing import Any


# ---------------------------------------------------------------------------
# Mock Data: Test Cycles
# ---------------------------------------------------------------------------

_MOCK_CYCLES: dict[str, dict[str, Any]] = {
    "PolicyCenter": {
        "project": "PolicyCenter",
        "cycles": [
            {
                "cycle_id": "ZC-101",
                "name": "PolicyCenter Regression -- Sprint 14",
                "status": "In Progress",
                "start_date": "2026-09-01",
                "end_date": "2026-09-14",
                "total_tests": 45,
                "passed": 32,
                "failed": 5,
                "blocked": 2,
                "not_run": 6,
                "environment": "QA",
                "build": "PC-12.0.3-RC2",
            },
            {
                "cycle_id": "ZC-102",
                "name": "PolicyCenter Smoke -- Daily",
                "status": "Complete",
                "start_date": "2026-09-10",
                "end_date": "2026-09-10",
                "total_tests": 15,
                "passed": 14,
                "failed": 1,
                "blocked": 0,
                "not_run": 0,
                "environment": "QA",
                "build": "PC-12.0.3-RC2",
            },
        ],
    },
    "ClaimCenter": {
        "project": "ClaimCenter",
        "cycles": [
            {
                "cycle_id": "ZC-201",
                "name": "ClaimCenter Regression -- Sprint 14",
                "status": "In Progress",
                "start_date": "2026-09-01",
                "end_date": "2026-09-14",
                "total_tests": 62,
                "passed": 48,
                "failed": 8,
                "blocked": 1,
                "not_run": 5,
                "environment": "QA",
                "build": "CC-12.0.3-RC2",
            },
        ],
    },
    "BillingCenter": {
        "project": "BillingCenter",
        "cycles": [
            {
                "cycle_id": "ZC-301",
                "name": "BillingCenter Regression -- Sprint 14",
                "status": "In Progress",
                "start_date": "2026-09-01",
                "end_date": "2026-09-14",
                "total_tests": 30,
                "passed": 25,
                "failed": 3,
                "blocked": 0,
                "not_run": 2,
                "environment": "QA",
                "build": "BC-12.0.3-RC2",
            },
        ],
    },
}

# In-memory execution log for mock updates
_execution_log: list[dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_test_cycles_impl(project: str) -> str:
    """Return mock test cycles for a project.

    Args:
        project: Project name (e.g., "PolicyCenter", "ClaimCenter").

    Returns:
        JSON string with test cycle information.
    """
    if not project or not project.strip():
        return json.dumps({"error": "Project name is required"})

    # Normalize project name
    project_key = _normalize_project(project)
    cycle_data = _MOCK_CYCLES.get(project_key)

    if cycle_data is None:
        available = list(_MOCK_CYCLES.keys())
        return json.dumps({
            "error": f"No test cycles found for project '{project}'",
            "available_projects": available,
        })

    return json.dumps(cycle_data, indent=2)


def update_test_result_impl(test_id: str, status: str, notes: str) -> str:
    """Mock update of a test execution result in Zephyr.

    Args:
        test_id: Test case identifier (e.g., "TC-3001").
        status: Execution status -- "passed", "failed", "blocked", or "not_run".
        notes: Execution notes or comments.

    Returns:
        JSON string confirming the update.
    """
    if not test_id or not test_id.strip():
        return json.dumps({"error": "Test ID is required"})

    valid_statuses = {"passed", "failed", "blocked", "not_run"}
    status_lower = status.lower().strip()
    if status_lower not in valid_statuses:
        return json.dumps({
            "error": f"Invalid status '{status}'. Must be one of: {sorted(valid_statuses)}",
        })

    if not notes or not notes.strip():
        return json.dumps({"error": "Notes are required for test execution updates"})

    entry = {
        "test_id": test_id.upper(),
        "status": status_lower,
        "notes": notes,
        "updated": True,
        "execution_id": f"EX-{len(_execution_log) + 1:06d}",
    }
    _execution_log.append(entry)

    return json.dumps(
        {
            "success": True,
            "message": f"Test {test_id} updated to '{status_lower}'",
            "execution": entry,
        },
        indent=2,
    )


def get_zephyr_cycles_resource() -> str:
    """Return a summary of all available test cycles for the resource endpoint.

    Returns:
        JSON string listing all mock test cycles across projects.
    """
    all_cycles: list[dict[str, Any]] = []
    for project_key, data in _MOCK_CYCLES.items():
        for cycle in data["cycles"]:
            all_cycles.append({
                "project": project_key,
                "cycle_id": cycle["cycle_id"],
                "name": cycle["name"],
                "status": cycle["status"],
                "total_tests": cycle["total_tests"],
                "pass_rate": round(
                    cycle["passed"] / cycle["total_tests"] * 100, 1
                ) if cycle["total_tests"] > 0 else 0.0,
            })

    return json.dumps(
        {"total_cycles": len(all_cycles), "cycles": all_cycles},
        indent=2,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize_project(project: str) -> str:
    """Normalize project name to match mock data keys."""
    mapping: dict[str, str] = {
        "policycenter": "PolicyCenter",
        "claimcenter": "ClaimCenter",
        "billingcenter": "BillingCenter",
        "pc": "PolicyCenter",
        "cc": "ClaimCenter",
        "bc": "BillingCenter",
    }
    return mapping.get(project.lower().strip(), project)
