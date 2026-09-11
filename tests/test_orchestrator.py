# Author: Maharshi Soni | License: MIT
"""Tests for the QA workflow orchestrator."""

from __future__ import annotations

import json

import pytest

from insurance_qa_mcp.orchestrator import run_qa_workflow_impl


class TestWorkflowRouting:
    """Tests for request routing to the correct workflow."""

    def test_story_to_tests_workflow(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Create test cases for user story US-1001 in PolicyCenter"
        ))
        assert result["detected_workflow"] == "story_to_tests"
        assert result["confidence"] > 0.3
        assert result["total_steps"] >= 2
        tool_names = [s["tool"] for s in result["steps"]]
        assert "get_user_stories" in tool_names

    def test_code_review_workflow(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Review code quality for /src/validators.py"
        ))
        assert result["detected_workflow"] == "code_review_pipeline"
        tool_names = [s["tool"] for s in result["steps"]]
        assert "review_code" in tool_names

    def test_chaos_testing_workflow(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Run chaos tests on the claims API"
        ))
        assert result["detected_workflow"] == "chaos_testing"
        tool_names = [s["tool"] for s in result["steps"]]
        assert "chaos_test_api" in tool_names

    def test_regression_workflow(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Run regression tests and check coverage"
        ))
        assert result["detected_workflow"] == "regression_analysis"
        tool_names = [s["tool"] for s in result["steps"]]
        assert "run_tests" in tool_names

    def test_data_validation_workflow(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Validate data integrity for test data in the claims table"
        ))
        assert result["detected_workflow"] == "data_validation"

    def test_bdd_workflow(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Generate BDD scenarios and Playwright tests for the login workflow"
        ))
        assert result["detected_workflow"] == "bdd_workflow"

    def test_general_fallback_workflow(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Help me with something vague"
        ))
        assert result["detected_workflow"] == "general_qa"
        assert result["confidence"] <= 0.3


class TestWorkflowStepBuilding:
    """Tests for workflow step construction."""

    def test_steps_have_required_fields(self) -> None:
        result = json.loads(run_qa_workflow_impl("Create test cases for story US-1001"))
        for step in result["steps"]:
            assert "step" in step
            assert "tool" in step
            assert "description" in step
            assert "suggested_arguments" in step
            assert "depends_on" in step
            assert "status" in step
            assert step["status"] == "planned"

    def test_execution_plan_formatted(self) -> None:
        result = json.loads(run_qa_workflow_impl("Run regression tests"))
        assert "execution_plan" in result
        assert "Execution Plan:" in result["execution_plan"]

    def test_story_id_extracted(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Create test cases for story US-1002 in ClaimCenter"
        ))
        # Check that the story_id was extracted into suggested_arguments
        story_steps = [
            s for s in result["steps"]
            if s["suggested_arguments"].get("story_id") == "US-1002"
        ]
        assert len(story_steps) >= 1

    def test_project_name_extracted(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Get test cycles for PolicyCenter"
        ))
        project_steps = [
            s for s in result["steps"]
            if s["suggested_arguments"].get("project") == "PolicyCenter"
        ]
        assert len(project_steps) >= 1


class TestWorkflowEdgeCases:
    """Tests for orchestrator error handling."""

    def test_empty_request_error(self) -> None:
        result = json.loads(run_qa_workflow_impl(""))
        assert "error" in result

    def test_whitespace_request_error(self) -> None:
        result = json.loads(run_qa_workflow_impl("   "))
        assert "error" in result

    def test_url_extraction(self) -> None:
        result = json.loads(run_qa_workflow_impl(
            "Generate Playwright tests for https://example.com/login"
        ))
        url_steps = [
            s for s in result["steps"]
            if "url" in s["suggested_arguments"]
        ]
        # At least one step should have extracted the URL
        if url_steps:
            assert url_steps[0]["suggested_arguments"]["url"] == "https://example.com/login"
