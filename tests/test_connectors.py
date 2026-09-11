# Author: Maharshi Soni | License: MIT
"""Tests for mock enterprise connector implementations."""

from __future__ import annotations

import json

import pytest

from insurance_qa_mcp.connectors.ado_connector import (
    get_ado_stories_resource,
    get_test_plan_impl,
    get_user_stories_impl,
)
from insurance_qa_mcp.connectors.zephyr_connector import (
    get_test_cycles_impl,
    get_zephyr_cycles_resource,
    update_test_result_impl,
)
from insurance_qa_mcp.connectors.sql_connector import (
    query_test_data_impl,
    validate_data_integrity_impl,
)


# =========================================================================
# ADO Connector Tests
# =========================================================================


class TestADOConnector:
    """Tests for the mock Azure DevOps / Jira connector."""

    def test_get_stories_by_project(self) -> None:
        result = json.loads(get_user_stories_impl("PolicyCenter"))
        assert result["story_count"] >= 1
        for story in result["stories"]:
            assert "id" in story
            assert "title" in story
            assert "acceptance_criteria" in story
            assert len(story["acceptance_criteria"]) > 0

    def test_get_stories_by_sprint(self) -> None:
        result = json.loads(get_user_stories_impl("ClaimCenter", sprint="current"))
        assert result["story_count"] >= 1

    def test_get_stories_all_sprints(self) -> None:
        result = json.loads(get_user_stories_impl("PolicyCenter", sprint="all"))
        assert result["story_count"] >= 2

    def test_get_stories_empty_project_error(self) -> None:
        result = json.loads(get_user_stories_impl(""))
        assert "error" in result

    def test_get_test_plan_known_story(self) -> None:
        result = json.loads(get_test_plan_impl("US-1001"))
        assert result["story_id"] == "US-1001"
        assert result["total_cases"] >= 3
        assert len(result["test_cases"]) > 0
        for tc in result["test_cases"]:
            assert "id" in tc
            assert "title" in tc
            assert "priority" in tc

    def test_get_test_plan_unknown_story(self) -> None:
        result = json.loads(get_test_plan_impl("US-9999"))
        assert result["story_id"] == "US-9999"
        assert "note" in result  # auto-generated placeholder

    def test_get_test_plan_empty_id_error(self) -> None:
        result = json.loads(get_test_plan_impl(""))
        assert "error" in result

    def test_ado_stories_resource(self) -> None:
        result = json.loads(get_ado_stories_resource())
        assert result["total_stories"] >= 4
        for story in result["stories"]:
            assert "id" in story
            assert "title" in story


# =========================================================================
# Zephyr Connector Tests
# =========================================================================


class TestZephyrConnector:
    """Tests for the mock Zephyr test management connector."""

    def test_get_cycles_policycenter(self) -> None:
        result = json.loads(get_test_cycles_impl("PolicyCenter"))
        assert result["project"] == "PolicyCenter"
        assert len(result["cycles"]) >= 1
        cycle = result["cycles"][0]
        assert "cycle_id" in cycle
        assert "total_tests" in cycle
        assert "passed" in cycle
        assert "failed" in cycle

    def test_get_cycles_claimcenter(self) -> None:
        result = json.loads(get_test_cycles_impl("ClaimCenter"))
        assert len(result["cycles"]) >= 1

    def test_get_cycles_alias(self) -> None:
        result = json.loads(get_test_cycles_impl("PC"))
        assert result["project"] == "PolicyCenter"

    def test_get_cycles_unknown_project(self) -> None:
        result = json.loads(get_test_cycles_impl("UnknownProject"))
        assert "error" in result
        assert "available_projects" in result

    def test_get_cycles_empty_project_error(self) -> None:
        result = json.loads(get_test_cycles_impl(""))
        assert "error" in result

    def test_update_result_success(self) -> None:
        result = json.loads(update_test_result_impl("TC-3001", "passed", "All assertions verified"))
        assert result["success"] is True
        assert result["execution"]["status"] == "passed"
        assert "execution_id" in result["execution"]

    def test_update_result_invalid_status(self) -> None:
        result = json.loads(update_test_result_impl("TC-3001", "invalid_status", "notes"))
        assert "error" in result

    def test_update_result_empty_notes_error(self) -> None:
        result = json.loads(update_test_result_impl("TC-3001", "failed", ""))
        assert "error" in result

    def test_zephyr_cycles_resource(self) -> None:
        result = json.loads(get_zephyr_cycles_resource())
        assert result["total_cycles"] >= 3
        for cycle in result["cycles"]:
            assert "project" in cycle
            assert "pass_rate" in cycle


# =========================================================================
# SQL Connector Tests
# =========================================================================


class TestSQLConnector:
    """Tests for the mock SQL Server connector."""

    def test_query_claims_table(self) -> None:
        result = json.loads(query_test_data_impl("cc_claim"))
        assert result["table"] == "cc_claim"
        assert result["query_result_count"] > 0
        assert len(result["rows"]) > 0
        row = result["rows"][0]
        assert "ClaimNumber" in row
        assert "PolicyNumber" in row
        assert "Status" in row

    def test_query_policies_table(self) -> None:
        result = json.loads(query_test_data_impl("pc_policy"))
        assert result["table"] == "pc_policy"
        assert result["total_rows_in_table"] > 0

    def test_query_with_filters(self) -> None:
        result = json.loads(query_test_data_impl("cc_claim", filters="Status=open"))
        for row in result["rows"]:
            assert row["Status"] == "open"

    def test_query_unknown_table(self) -> None:
        result = json.loads(query_test_data_impl("nonexistent_table"))
        assert "error" in result
        assert "available_tables" in result

    def test_query_empty_table_error(self) -> None:
        result = json.loads(query_test_data_impl(""))
        assert "error" in result

    def test_validate_claims_integrity(self) -> None:
        result = json.loads(validate_data_integrity_impl("cc_claim"))
        assert result["total_checks"] >= 3
        assert "overall_status" in result
        for check in result["checks"]:
            assert "check" in check
            assert "status" in check
            assert check["status"] in ("PASS", "FAIL", "WARN")

    def test_validate_policies_integrity(self) -> None:
        result = json.loads(validate_data_integrity_impl("pc_policy"))
        assert result["total_checks"] >= 3
        assert result["passed"] >= 1

    def test_validate_billing_integrity(self) -> None:
        result = json.loads(validate_data_integrity_impl("bc_billing"))
        assert result["total_checks"] >= 3

    def test_validate_unknown_table(self) -> None:
        result = json.loads(validate_data_integrity_impl("nonexistent"))
        assert "error" in result
