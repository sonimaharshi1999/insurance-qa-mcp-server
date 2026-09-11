# Author: Maharshi Soni | License: MIT
"""Tests for bridge tool implementations (external project integrations)."""

from __future__ import annotations

import json
import textwrap

import pytest

from insurance_qa_mcp.tools.bridges.playwright_bridge import (
    generate_playwright_tests_impl,
    run_playwright_audit_impl,
)
from insurance_qa_mcp.tools.bridges.code_review_bridge import review_code_impl
from insurance_qa_mcp.tools.bridges.test_gen_bridge import auto_generate_tests_impl
from insurance_qa_mcp.tools.bridges.embedkit_bridge import (
    get_knowledge_base_info,
    semantic_search_impl,
)
from insurance_qa_mcp.tools.bridges.chaos_test_bridge import chaos_test_api_impl


# =========================================================================
# Playwright Bridge Tests
# =========================================================================


class TestPlaywrightBridge:
    """Tests for the Playwright test generation bridge."""

    def test_generate_tests_basic(self) -> None:
        result = json.loads(generate_playwright_tests_impl(
            url="https://example.com/login",
            workflow="navigate to the login page, fill username, fill password, click submit",
        ))
        assert "test_code" in result
        assert "playwright" in result["framework"]
        assert result["steps_detected"] >= 3
        assert "example.com" in result["test_code"]

    def test_generate_tests_empty_url_error(self) -> None:
        result = json.loads(generate_playwright_tests_impl(url="", workflow="click button"))
        assert "error" in result

    def test_generate_tests_empty_workflow_error(self) -> None:
        result = json.loads(generate_playwright_tests_impl(url="https://example.com", workflow=""))
        assert "error" in result

    def test_generate_tests_page_object(self) -> None:
        result = json.loads(generate_playwright_tests_impl(
            url="https://example.com",
            workflow="click the submit button, fill the search field",
        ))
        assert "page_object" in result
        assert "class PageObject" in result["page_object"]

    def test_audit_returns_findings(self) -> None:
        result = json.loads(run_playwright_audit_impl("https://example.com"))
        assert result["total_issues"] > 0
        assert len(result["accessibility"]) > 0
        assert len(result["performance"]) > 0
        assert len(result["recommendations"]) > 0

    def test_audit_empty_url_error(self) -> None:
        result = json.loads(run_playwright_audit_impl(""))
        assert "error" in result


# =========================================================================
# Code Review Bridge Tests
# =========================================================================


class TestCodeReviewBridge:
    """Tests for the multi-agent code review bridge."""

    def test_review_clean_code(self, tmp_path) -> None:
        code = textwrap.dedent('''\
            """Module docstring."""

            def add(a: int, b: int) -> int:
                """Add two numbers."""
                return a + b
        ''')
        f = tmp_path / "clean.py"
        f.write_text(code, encoding="utf-8")
        result = json.loads(review_code_impl(str(f)))
        assert "total_findings" in result
        assert "security" in result
        assert "performance" in result
        assert "style" in result
        assert "overall_rating" in result

    def test_review_detects_security_issues(self, tmp_path) -> None:
        code = textwrap.dedent('''\
            password = "hardcoded_secret"
            result = eval(user_input)
        ''')
        f = tmp_path / "insecure.py"
        f.write_text(code, encoding="utf-8")
        result = json.loads(review_code_impl(str(f)))
        assert len(result["security"]) >= 2
        critical = [f for f in result["security"] if f["severity"] == "critical"]
        assert len(critical) >= 1

    def test_review_nonexistent_file(self) -> None:
        result = json.loads(review_code_impl("/nonexistent/file.py"))
        assert "error" in result

    def test_review_strict_profile(self, tmp_path) -> None:
        code = 'def foo(x):\n    return x\n'
        f = tmp_path / "simple.py"
        f.write_text(code, encoding="utf-8")
        result = json.loads(review_code_impl(str(f), profile="strict"))
        assert result["profile"] == "strict"


# =========================================================================
# Test Gen Bridge Tests
# =========================================================================


class TestTestGenBridge:
    """Tests for the testpilot test generation bridge."""

    def test_generates_tests_for_functions(self, sample_python_source: str) -> None:
        result = json.loads(auto_generate_tests_impl(sample_python_source))
        assert result["engine"] == "ast_fallback"
        assert result["tests_generated"] > 0
        assert "test_code" in result
        assert "def test_" in result["test_code"]

    def test_generates_class_tests(self, tmp_path) -> None:
        code = textwrap.dedent('''\
            class Calculator:
                def add(self, a, b):
                    return a + b

                def subtract(self, a, b):
                    return a - b
        ''')
        f = tmp_path / "calc.py"
        f.write_text(code, encoding="utf-8")
        result = json.loads(auto_generate_tests_impl(str(f)))
        assert result["classes_found"] == 1
        assert result["tests_generated"] >= 2

    def test_nonexistent_file_error(self) -> None:
        result = json.loads(auto_generate_tests_impl("/nonexistent/module.py"))
        assert "error" in result

    def test_non_python_file_error(self, tmp_path) -> None:
        f = tmp_path / "data.txt"
        f.write_text("hello", encoding="utf-8")
        result = json.loads(auto_generate_tests_impl(str(f)))
        assert "error" in result


# =========================================================================
# EmbedKit Bridge Tests
# =========================================================================


class TestEmbedKitBridge:
    """Tests for the semantic search bridge."""

    def test_search_finds_relevant_documents(self, tmp_path) -> None:
        (tmp_path / "claims.txt").write_text(
            "Insurance claim processing for auto collisions", encoding="utf-8"
        )
        (tmp_path / "billing.txt").write_text(
            "Billing installment payment scheduling", encoding="utf-8"
        )
        result = json.loads(semantic_search_impl("auto collision claim", str(tmp_path)))
        assert result["results_count"] >= 1
        assert result["engine"] == "tfidf_fallback"
        # The claims file should rank higher
        assert any("claims" in r["file"] for r in result["results"])

    def test_search_empty_query_error(self) -> None:
        result = json.loads(semantic_search_impl("", "/some/dir"))
        assert "error" in result

    def test_search_nonexistent_dir_error(self) -> None:
        result = json.loads(semantic_search_impl("test query", "/nonexistent/dir"))
        assert "error" in result

    def test_knowledge_base_info(self, tmp_path) -> None:
        (tmp_path / "doc1.py").write_text("# python code", encoding="utf-8")
        (tmp_path / "doc2.md").write_text("# markdown", encoding="utf-8")
        result = json.loads(get_knowledge_base_info(str(tmp_path)))
        assert result["total_documents"] == 2
        assert ".py" in result["file_types"]


# =========================================================================
# Chaos Test Bridge Tests
# =========================================================================


class TestChaosTestBridge:
    """Tests for the API chaos testing bridge."""

    @pytest.fixture()
    def sample_openapi_spec(self, tmp_path) -> str:
        """Create a minimal OpenAPI spec for testing."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Insurance API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com/v1"}],
            "paths": {
                "/claims/{claim_id}": {
                    "get": {
                        "operationId": "getClaim",
                        "summary": "Get a claim by ID",
                        "parameters": [
                            {
                                "name": "claim_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "include_history",
                                "in": "query",
                                "schema": {"type": "string"},
                            },
                        ],
                        "responses": {"200": {"description": "OK"}},
                    },
                },
                "/claims": {
                    "post": {
                        "operationId": "createClaim",
                        "summary": "Create a new claim",
                        "requestBody": {
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        },
                        "responses": {"201": {"description": "Created"}},
                    },
                },
            },
        }
        f = tmp_path / "api_spec.json"
        f.write_text(json.dumps(spec), encoding="utf-8")
        return str(f)

    def test_generates_chaos_scenarios(self, sample_openapi_spec: str) -> None:
        result = json.loads(chaos_test_api_impl(sample_openapi_spec))
        assert result["endpoints_found"] == 2
        assert result["total_scenarios"] > 0
        assert "boundary_value" in result["category_breakdown"]

    def test_includes_type_confusion(self, sample_openapi_spec: str) -> None:
        result = json.loads(chaos_test_api_impl(sample_openapi_spec))
        categories = result["category_breakdown"]
        assert "type_confusion" in categories

    def test_includes_header_injection(self, sample_openapi_spec: str) -> None:
        result = json.loads(chaos_test_api_impl(sample_openapi_spec))
        header_scenarios = [s for s in result["scenarios"] if s["category"] == "header_injection"]
        assert len(header_scenarios) > 0

    def test_nonexistent_spec_error(self) -> None:
        result = json.loads(chaos_test_api_impl("/nonexistent/spec.json"))
        assert "error" in result

    def test_custom_base_url(self, sample_openapi_spec: str) -> None:
        result = json.loads(chaos_test_api_impl(sample_openapi_spec, base_url="https://custom.api.com"))
        assert result["base_url"] == "https://custom.api.com"
