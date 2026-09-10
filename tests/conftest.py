# Author: Maharshi Soni | License: MIT
"""Shared fixtures for insurance QA MCP server tests."""

from __future__ import annotations

import pytest


@pytest.fixture()
def valid_claim_data() -> dict:
    """A claim record that passes all business-rule validations."""
    return {
        "claim_number": "CLM-00000001",
        "policy_number": "PA-0000001",
        "line_of_business": "personal_auto",
        "loss_date": "2025-03-15",
        "reported_date": "2025-03-16",
        "status": "open",
        "loss_type": "collision",
        "loss_amount": 12500.00,
        "description": "Rear-end collision at intersection",
        "claimant_name": "James Smith",
    }


@pytest.fixture()
def valid_policy_data() -> dict:
    """A policy record that passes all underwriting validations."""
    return {
        "policy_number": "PA-0000001",
        "line_of_business": "personal_auto",
        "effective_date": "2026-01-01",
        "expiration_date": "2027-01-01",
        "status": "active",
        "premium": 1500.00,
        "insured_name": "James Smith",
        "coverage_limits": {
            "bodily_injury_per_person": 100000,
            "bodily_injury_per_accident": 300000,
            "property_damage": 100000,
        },
    }


@pytest.fixture()
def sample_python_source(tmp_path) -> str:
    """Create a temporary Python file for lint/analysis tests."""
    code = '''
def calculate_premium(age, base_rate):
    if age < 25:
        return base_rate * 1.5
    elif age > 65:
        return base_rate * 1.3
    return base_rate

class PolicyProcessor:
    def process(self, policy):
        if policy.status == "active":
            return True
        return False

def _private_helper():
    pass
'''
    f = tmp_path / "sample.py"
    f.write_text(code.strip(), encoding="utf-8")
    return str(f)


@pytest.fixture()
def sample_project(tmp_path) -> str:
    """Create a temporary project directory with test files."""
    # Create a pyproject.toml so it's recognized as a project
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "sample"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )

    # Create source file
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text(
        "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n",
        encoding="utf-8",
    )

    # Create test file
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text(
        "def test_add():\n    assert 1 + 1 == 2\n\ndef test_subtract():\n    assert 2 - 1 == 1\n",
        encoding="utf-8",
    )

    return str(tmp_path)
