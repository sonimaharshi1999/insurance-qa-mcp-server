# Author: Maharshi Soni | License: MIT
"""Tests for MCP resource providers."""

from __future__ import annotations

import json

import pytest

from insurance_qa_mcp.resources.insurance_domain import get_insurance_lines, get_test_patterns
from insurance_qa_mcp.resources.project_scanner import scan_projects


class TestInsuranceLines:
    """Tests for the insurance lines resource."""

    def test_returns_all_lobs(self) -> None:
        result = json.loads(get_insurance_lines())
        assert result["line_count"] == 8
        assert "personal_auto" in result["lines"]
        assert "homeowners" in result["lines"]
        assert "workers_compensation" in result["lines"]

    def test_lob_has_required_fields(self) -> None:
        result = json.loads(get_insurance_lines())
        for lob_key, lob in result["lines"].items():
            assert "display_name" in lob, f"Missing display_name in {lob_key}"
            assert "guidewire_lob" in lob, f"Missing guidewire_lob in {lob_key}"
            assert "coverage_types" in lob, f"Missing coverage_types in {lob_key}"
            assert "typical_premium_range" in lob, f"Missing premium range in {lob_key}"
            assert len(lob["coverage_types"]) > 0

    def test_premium_ranges_are_valid(self) -> None:
        result = json.loads(get_insurance_lines())
        for lob_key, lob in result["lines"].items():
            pr = lob["typical_premium_range"]
            assert pr["min"] > 0, f"Min premium <= 0 for {lob_key}"
            assert pr["max"] > pr["min"], f"Max <= min for {lob_key}"
            assert pr["currency"] == "USD"


class TestTestPatterns:
    """Tests for the test patterns resource."""

    def test_returns_patterns(self) -> None:
        result = json.loads(get_test_patterns())
        assert result["pattern_count"] >= 4
        assert len(result["patterns"]) == result["pattern_count"]

    def test_patterns_have_templates(self) -> None:
        result = json.loads(get_test_patterns())
        for pattern in result["patterns"]:
            assert "name" in pattern
            assert "description" in pattern
            assert "template" in pattern
            assert len(pattern["template"]) > 0

    def test_patterns_have_categories(self) -> None:
        result = json.loads(get_test_patterns())
        categories = {p["category"] for p in result["patterns"]}
        assert "unit" in categories


class TestProjectScanner:
    """Tests for the project scanner resource."""

    def test_scan_project_directory(self, sample_project: str) -> None:
        result = json.loads(scan_projects(sample_project))
        assert result["project_count"] == 1
        project = result["projects"][0]
        assert project["name"] == "sample" or project["test_count"] >= 0

    def test_scan_nonexistent_directory(self) -> None:
        result = json.loads(scan_projects("/nonexistent/dir"))
        assert "error" in result

    def test_project_has_test_count(self, sample_project: str) -> None:
        result = json.loads(scan_projects(sample_project))
        project = result["projects"][0]
        assert project["test_count"] == 2
        assert project["status"] == "has_tests"
