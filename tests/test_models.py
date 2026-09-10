# Author: Maharshi Soni | License: MIT
"""Tests for Pydantic model validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from insurance_qa_mcp.models import (
    BDDScenario,
    BillingRecord,
    ClaimStatus,
    CoverageReport,
    InsuranceClaim,
    InsurancePolicy,
    LineOfBusiness,
    LossType,
    PolicyStatus,
    TestResult,
    TestSuggestion,
    ValidationResult,
)


class TestLineOfBusinessEnum:
    """Tests for the LineOfBusiness enum values."""

    def test_all_standard_lobs_exist(self) -> None:
        expected = {
            "personal_auto", "homeowners", "commercial_property",
            "commercial_auto", "workers_compensation", "general_liability",
            "business_owners_policy", "professional_liability",
        }
        actual = {lob.value for lob in LineOfBusiness}
        assert actual == expected

    def test_lob_string_value(self) -> None:
        assert LineOfBusiness.PERSONAL_AUTO == "personal_auto"
        assert LineOfBusiness.WORKERS_COMP == "workers_compensation"


class TestInsuranceClaim:
    """Tests for the InsuranceClaim model."""

    def test_valid_claim(self, valid_claim_data: dict) -> None:
        claim = InsuranceClaim(**valid_claim_data)
        assert claim.claim_number == "CLM-00000001"
        assert claim.loss_amount == 12500.00
        assert claim.line_of_business == LineOfBusiness.PERSONAL_AUTO

    def test_claim_rejects_negative_amount(self, valid_claim_data: dict) -> None:
        valid_claim_data["loss_amount"] = -100.0
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            InsuranceClaim(**valid_claim_data)

    def test_claim_rejects_bad_date_format(self, valid_claim_data: dict) -> None:
        valid_claim_data["loss_date"] = "03-15-2025"
        with pytest.raises(ValidationError, match="YYYY-MM-DD"):
            InsuranceClaim(**valid_claim_data)

    def test_claim_rejects_empty_claim_number(self, valid_claim_data: dict) -> None:
        valid_claim_data["claim_number"] = ""
        with pytest.raises(ValidationError):
            InsuranceClaim(**valid_claim_data)

    def test_claim_status_enum(self) -> None:
        statuses = {s.value for s in ClaimStatus}
        assert "open" in statuses
        assert "closed" in statuses
        assert "subrogation" in statuses


class TestInsurancePolicy:
    """Tests for the InsurancePolicy model."""

    def test_valid_policy(self, valid_policy_data: dict) -> None:
        policy = InsurancePolicy(**valid_policy_data)
        assert policy.policy_number == "PA-0000001"
        assert policy.premium == 1500.00
        assert policy.status == PolicyStatus.ACTIVE

    def test_policy_rejects_negative_premium(self, valid_policy_data: dict) -> None:
        valid_policy_data["premium"] = -500.0
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            InsurancePolicy(**valid_policy_data)

    def test_policy_default_coverage_limits(self) -> None:
        policy = InsurancePolicy(
            policy_number="PA-0000002",
            line_of_business="personal_auto",
            effective_date="2025-01-01",
            expiration_date="2026-01-01",
            premium=1000.0,
            insured_name="Test User",
        )
        assert policy.coverage_limits == {}


class TestTestResult:
    """Tests for the TestResult model."""

    def test_default_values(self) -> None:
        result = TestResult()
        assert result.total == 0
        assert result.passed == 0
        assert result.failed == 0
        assert result.details == []

    def test_computed_values(self) -> None:
        result = TestResult(total=10, passed=8, failed=1, errors=1)
        assert result.passed + result.failed + result.errors == result.total


class TestBDDScenario:
    """Tests for BDD scenario model and Gherkin rendering."""

    def test_gherkin_rendering(self) -> None:
        scenario = BDDScenario(
            feature="Claim Submission",
            scenario="Submit valid claim",
            given_steps=["an active policy"],
            when_steps=["the insured submits a claim"],
            then_steps=["the claim is created"],
        )
        gherkin = scenario.to_gherkin()
        assert "Feature: Claim Submission" in gherkin
        assert "Given an active policy" in gherkin
        assert "When the insured submits a claim" in gherkin
        assert "Then the claim is created" in gherkin


class TestValidationResult:
    """Tests for the ValidationResult model."""

    def test_valid_result(self) -> None:
        result = ValidationResult(valid=True, record_type="claim")
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_invalid_result_with_errors(self) -> None:
        result = ValidationResult(
            valid=False,
            errors=["Loss date is in the future"],
            warnings=["Late FNOL"],
            record_type="claim",
        )
        assert result.valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
