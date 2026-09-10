# Author: Maharshi Soni | License: MIT
"""Tests for synthetic insurance data generation."""

from __future__ import annotations

import json

import pytest

from insurance_qa_mcp.tools.data_generator import generate_test_data_impl


class TestGeneratePolicies:
    """Tests for policy data generation."""

    def test_generates_correct_count(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="personal_auto", count=5, data_type="policy", seed=42
        ))
        assert result["count"] == 5
        assert len(result["records"]) == 5

    def test_policy_fields_present(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="homeowners", count=1, data_type="policy", seed=42
        ))
        policy = result["records"][0]
        assert "policy_number" in policy
        assert "line_of_business" in policy
        assert "effective_date" in policy
        assert "expiration_date" in policy
        assert "premium" in policy
        assert "insured_name" in policy
        assert "coverage_limits" in policy

    def test_lob_matches_request(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="commercial_property", count=3, data_type="policy", seed=42
        ))
        for record in result["records"]:
            assert record["line_of_business"] == "commercial_property"

    def test_seed_produces_deterministic_output(self) -> None:
        r1 = json.loads(generate_test_data_impl(
            line_of_business="personal_auto", count=5, data_type="policy", seed=123
        ))
        r2 = json.loads(generate_test_data_impl(
            line_of_business="personal_auto", count=5, data_type="policy", seed=123
        ))
        assert r1["records"] == r2["records"]


class TestGenerateClaims:
    """Tests for claim data generation."""

    def test_generates_claims(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="personal_auto", count=10, data_type="claim", seed=42
        ))
        assert result["data_type"] == "claim"
        assert result["count"] == 10

    def test_claim_dates_are_valid(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="homeowners", count=5, data_type="claim", seed=42
        ))
        for claim in result["records"]:
            # reported_date should be >= loss_date
            assert claim["reported_date"] >= claim["loss_date"]

    def test_claim_amounts_are_positive(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="general_liability", count=20, data_type="claim", seed=42
        ))
        for claim in result["records"]:
            assert claim["loss_amount"] >= 0


class TestGenerateBilling:
    """Tests for billing record generation."""

    def test_generates_billing(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="personal_auto", count=5, data_type="billing", seed=42
        ))
        assert result["data_type"] == "billing"
        assert result["count"] == 5

    def test_billing_amounts_positive(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="personal_auto", count=10, data_type="billing", seed=42
        ))
        for record in result["records"]:
            assert record["amount_due"] >= 0
            assert record["amount_paid"] >= 0


class TestGenerateErrors:
    """Tests for error handling in data generation."""

    def test_invalid_lob(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="invalid_lob", count=5, data_type="policy"
        ))
        assert "error" in result

    def test_invalid_data_type(self) -> None:
        result = json.loads(generate_test_data_impl(
            line_of_business="personal_auto", count=5, data_type="invalid"
        ))
        assert "error" in result

    def test_count_clamped_to_bounds(self) -> None:
        # Count > 1000 should be clamped to 1000
        result = json.loads(generate_test_data_impl(
            line_of_business="personal_auto", count=9999, data_type="policy", seed=42
        ))
        assert result["count"] == 1000
