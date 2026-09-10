# Author: Maharshi Soni | License: MIT
"""Tests for code analysis, BDD generation, and test health tools."""

from __future__ import annotations

import json

import pytest

from insurance_qa_mcp.tools.bdd_generator import generate_bdd_scenarios_impl
from insurance_qa_mcp.tools.code_analyzer import (
    analyze_coverage_impl,
    lint_code_impl,
    suggest_tests_impl,
)
from insurance_qa_mcp.tools.test_runner import check_test_health_impl


class TestLintCode:
    """Tests for the lint_code_impl tool."""

    def test_lint_valid_file(self, sample_python_source: str) -> None:
        result = json.loads(lint_code_impl(sample_python_source))
        assert "issues" in result
        assert "score" in result
        assert isinstance(result["score"], float)

    def test_lint_detects_missing_type_hints(self, sample_python_source: str) -> None:
        result = json.loads(lint_code_impl(sample_python_source))
        # sample code has functions without return type hints
        hint_issues = [i for i in result["issues"] if "type hint" in i["message"].lower()]
        assert len(hint_issues) > 0

    def test_lint_detects_missing_docstrings(self, sample_python_source: str) -> None:
        result = json.loads(lint_code_impl(sample_python_source))
        doc_issues = [i for i in result["issues"] if "docstring" in i["message"].lower()]
        assert len(doc_issues) > 0

    def test_lint_nonexistent_file(self) -> None:
        result = json.loads(lint_code_impl("/nonexistent/file.py"))
        assert "error" in result

    def test_lint_non_python_file(self, tmp_path) -> None:
        f = tmp_path / "data.txt"
        f.write_text("hello", encoding="utf-8")
        result = json.loads(lint_code_impl(str(f)))
        assert "error" in result


class TestSuggestTests:
    """Tests for the suggest_tests_impl tool."""

    def test_suggests_tests_for_functions(self, sample_python_source: str) -> None:
        result = json.loads(suggest_tests_impl(sample_python_source))
        assert result["total_suggestions"] > 0
        names = [s["function_name"] for s in result["suggestions"]]
        assert "calculate_premium" in names

    def test_branch_coverage_suggestion(self, sample_python_source: str) -> None:
        result = json.loads(suggest_tests_impl(sample_python_source))
        branch_suggestions = [
            s for s in result["suggestions"]
            if "branch" in s["suggestion"].lower()
        ]
        assert len(branch_suggestions) > 0

    def test_skips_private_functions(self, sample_python_source: str) -> None:
        result = json.loads(suggest_tests_impl(sample_python_source))
        names = [s["function_name"] for s in result["suggestions"]]
        assert "_private_helper" not in names


class TestAnalyzeCoverage:
    """Tests for the analyze_coverage_impl tool."""

    def test_estimate_coverage_on_project(self, sample_project: str) -> None:
        result = json.loads(analyze_coverage_impl(sample_project))
        assert "coverage_percent" in result
        assert "total_statements" in result

    def test_nonexistent_project(self) -> None:
        result = json.loads(analyze_coverage_impl("/nonexistent/project"))
        assert "error" in result


class TestCheckTestHealth:
    """Tests for the check_test_health_impl tool."""

    def test_health_on_project(self, sample_project: str) -> None:
        result = json.loads(check_test_health_impl(sample_project))
        assert result["total_tests"] == 2
        assert result["test_files"] == 1
        assert "unit" in result["test_distribution"]

    def test_health_nonexistent_project(self) -> None:
        result = json.loads(check_test_health_impl("/nonexistent/project"))
        assert "error" in result


class TestBDDGenerator:
    """Tests for the generate_bdd_scenarios_impl tool."""

    def test_claim_submission_scenarios(self) -> None:
        result = json.loads(generate_bdd_scenarios_impl("claim_submission"))
        assert result["scenario_count"] >= 2
        assert "gherkin" in result
        assert "Feature:" in result["gherkin"]
        assert "Given" in result["gherkin"]

    def test_policy_binding_scenarios(self) -> None:
        result = json.loads(generate_bdd_scenarios_impl("policy_binding"))
        assert result["scenario_count"] >= 1
        assert result["feature"] == "Policy Binding"

    def test_billing_scenarios(self) -> None:
        result = json.loads(generate_bdd_scenarios_impl("billing_payment"))
        assert result["scenario_count"] >= 2

    def test_invalid_feature(self) -> None:
        result = json.loads(generate_bdd_scenarios_impl("nonexistent"))
        assert "error" in result

    def test_all_scenarios_have_steps(self) -> None:
        result = json.loads(generate_bdd_scenarios_impl("claim_adjudication"))
        for scenario in result["scenarios"]:
            assert len(scenario["given_steps"]) > 0
            assert len(scenario["when_steps"]) > 0
            assert len(scenario["then_steps"]) > 0
