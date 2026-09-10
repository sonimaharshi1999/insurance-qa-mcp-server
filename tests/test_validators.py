# Author: Maharshi Soni | License: MIT
"""Tests for insurance business-rule validators."""

from __future__ import annotations

import json

import pytest

from insurance_qa_mcp.tools.validators import validate_claim_impl, validate_policy_impl


class TestValidateClaim:
    """Tests for validate_claim_impl business rules."""

    def test_valid_claim_passes(self, valid_claim_data: dict) -> None:
        result = json.loads(validate_claim_impl(valid_claim_data))
        assert result["valid"] is True
        assert result["errors"] == []

    def test_reported_before_loss_date(self, valid_claim_data: dict) -> None:
        valid_claim_data["loss_date"] = "2025-03-20"
        valid_claim_data["reported_date"] = "2025-03-15"
        result = json.loads(validate_claim_impl(valid_claim_data))
        assert result["valid"] is False
        assert any("before loss date" in e for e in result["errors"])

    def test_future_loss_date(self, valid_claim_data: dict) -> None:
        valid_claim_data["loss_date"] = "2099-12-31"
        valid_claim_data["reported_date"] = "2099-12-31"
        result = json.loads(validate_claim_impl(valid_claim_data))
        assert result["valid"] is False
        assert any("future" in e for e in result["errors"])

    def test_zero_amount_non_denied(self, valid_claim_data: dict) -> None:
        valid_claim_data["loss_amount"] = 0.0
        valid_claim_data["status"] = "open"
        result = json.loads(validate_claim_impl(valid_claim_data))
        assert result["valid"] is False
        assert any("positive" in e for e in result["errors"])

    def test_zero_amount_denied_is_ok(self, valid_claim_data: dict) -> None:
        valid_claim_data["loss_amount"] = 0.0
        valid_claim_data["status"] = "denied"
        result = json.loads(validate_claim_impl(valid_claim_data))
        # Zero amount is acceptable for denied claims
        assert not any("positive" in e for e in result["errors"])

    def test_late_fnol_warning(self, valid_claim_data: dict) -> None:
        valid_claim_data["loss_date"] = "2024-01-01"
        valid_claim_data["reported_date"] = "2024-03-01"
        result = json.loads(validate_claim_impl(valid_claim_data))
        assert any("late FNOL" in w for w in result["warnings"])

    def test_claim_reported_over_one_year(self, valid_claim_data: dict) -> None:
        valid_claim_data["loss_date"] = "2022-01-01"
        valid_claim_data["reported_date"] = "2024-06-01"
        result = json.loads(validate_claim_impl(valid_claim_data))
        assert result["valid"] is False
        assert any("1 year" in e for e in result["errors"])

    def test_missing_required_field(self) -> None:
        result = json.loads(validate_claim_impl({"claim_number": "C1"}))
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_very_small_claim_warning(self, valid_claim_data: dict) -> None:
        valid_claim_data["loss_amount"] = 5.00
        result = json.loads(validate_claim_impl(valid_claim_data))
        assert any("small claim" in w.lower() for w in result["warnings"])


class TestValidatePolicy:
    """Tests for validate_policy_impl business rules."""

    def test_valid_policy_passes(self, valid_policy_data: dict) -> None:
        result = json.loads(validate_policy_impl(valid_policy_data))
        assert result["valid"] is True
        assert result["errors"] == []

    def test_effective_after_expiration(self, valid_policy_data: dict) -> None:
        valid_policy_data["effective_date"] = "2026-01-01"
        valid_policy_data["expiration_date"] = "2025-01-01"
        result = json.loads(validate_policy_impl(valid_policy_data))
        assert result["valid"] is False
        assert any("before" in e for e in result["errors"])

    def test_short_term_policy(self, valid_policy_data: dict) -> None:
        valid_policy_data["effective_date"] = "2025-01-01"
        valid_policy_data["expiration_date"] = "2025-01-15"
        result = json.loads(validate_policy_impl(valid_policy_data))
        assert result["valid"] is False
        assert any("minimum 30" in e for e in result["errors"])

    def test_active_but_expired(self, valid_policy_data: dict) -> None:
        valid_policy_data["effective_date"] = "2020-01-01"
        valid_policy_data["expiration_date"] = "2021-01-01"
        valid_policy_data["status"] = "active"
        result = json.loads(validate_policy_impl(valid_policy_data))
        assert result["valid"] is False
        assert any("past" in e for e in result["errors"])

    def test_zero_premium_active_policy(self, valid_policy_data: dict) -> None:
        valid_policy_data["premium"] = 0.0
        valid_policy_data["status"] = "active"
        result = json.loads(validate_policy_impl(valid_policy_data))
        assert result["valid"] is False
        assert any("zero premium" in e.lower() for e in result["errors"])

    def test_premium_below_range_warning(self, valid_policy_data: dict) -> None:
        valid_policy_data["premium"] = 50.0
        valid_policy_data["status"] = "pending"
        result = json.loads(validate_policy_impl(valid_policy_data))
        assert any("below typical minimum" in w for w in result["warnings"])

    def test_missing_required_fields(self) -> None:
        result = json.loads(validate_policy_impl({"policy_number": "P1"}))
        assert result["valid"] is False
        assert len(result["errors"]) > 0
