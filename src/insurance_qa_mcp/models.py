# Author: Maharshi Soni | License: MIT
"""Pydantic models for insurance QA data structures."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class LineOfBusiness(str, Enum):
    """Insurance lines of business following Guidewire conventions."""

    PERSONAL_AUTO = "personal_auto"
    HOMEOWNERS = "homeowners"
    COMMERCIAL_PROPERTY = "commercial_property"
    COMMERCIAL_AUTO = "commercial_auto"
    WORKERS_COMP = "workers_compensation"
    GENERAL_LIABILITY = "general_liability"
    BOP = "business_owners_policy"
    PROFESSIONAL_LIABILITY = "professional_liability"


class ClaimStatus(str, Enum):
    """Lifecycle states for an insurance claim."""

    OPEN = "open"
    CLOSED = "closed"
    REOPENED = "reopened"
    PENDING = "pending"
    DENIED = "denied"
    SUBROGATION = "subrogation"


class PolicyStatus(str, Enum):
    """Lifecycle states for an insurance policy."""

    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"
    RENEWED = "renewed"
    DRAFT = "draft"


class LossType(str, Enum):
    """Categories of insured losses."""

    COLLISION = "collision"
    COMPREHENSIVE = "comprehensive"
    LIABILITY = "liability"
    PROPERTY_DAMAGE = "property_damage"
    BODILY_INJURY = "bodily_injury"
    THEFT = "theft"
    FIRE = "fire"
    WATER_DAMAGE = "water_damage"
    WIND_HAIL = "wind_hail"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Insurance Domain Models
# ---------------------------------------------------------------------------

class InsuranceClaim(BaseModel):
    """A property & casualty insurance claim record."""

    claim_number: str = Field(..., min_length=1, description="Unique claim identifier")
    policy_number: str = Field(..., min_length=1, description="Associated policy number")
    line_of_business: LineOfBusiness
    loss_date: str = Field(..., description="Date of loss in YYYY-MM-DD format")
    reported_date: str = Field(..., description="Date claim was reported in YYYY-MM-DD format")
    status: ClaimStatus = ClaimStatus.OPEN
    loss_type: LossType = LossType.OTHER
    loss_amount: float = Field(ge=0, description="Total incurred amount in USD")
    description: str = ""
    claimant_name: str = ""

    @field_validator("loss_date", "reported_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Ensure dates follow YYYY-MM-DD format."""
        import re

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError(f"Date must be in YYYY-MM-DD format, got '{v}'")
        return v


class InsurancePolicy(BaseModel):
    """An insurance policy record."""

    policy_number: str = Field(..., min_length=1, description="Unique policy identifier")
    line_of_business: LineOfBusiness
    effective_date: str = Field(..., description="Policy start date YYYY-MM-DD")
    expiration_date: str = Field(..., description="Policy end date YYYY-MM-DD")
    status: PolicyStatus = PolicyStatus.ACTIVE
    premium: float = Field(ge=0, description="Annual premium in USD")
    insured_name: str = Field(..., min_length=1, description="Named insured")
    coverage_limits: dict[str, Any] = Field(default_factory=dict)

    @field_validator("effective_date", "expiration_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Ensure dates follow YYYY-MM-DD format."""
        import re

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError(f"Date must be in YYYY-MM-DD format, got '{v}'")
        return v


class BillingRecord(BaseModel):
    """A billing/payment record tied to a policy."""

    billing_id: str = Field(..., min_length=1)
    policy_number: str = Field(..., min_length=1)
    amount_due: float = Field(ge=0)
    amount_paid: float = Field(ge=0, default=0)
    due_date: str
    payment_date: str = ""
    payment_method: str = "direct_bill"
    status: str = "pending"


# ---------------------------------------------------------------------------
# QA / Testing Models
# ---------------------------------------------------------------------------

class TestResult(BaseModel):
    """Aggregated test execution results."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration: float = 0.0
    details: list[str] = Field(default_factory=list)


class CoverageReport(BaseModel):
    """Code coverage analysis results."""

    total_statements: int = 0
    covered_statements: int = 0
    coverage_percent: float = 0.0
    uncovered_files: list[dict[str, Any]] = Field(default_factory=list)
    threshold: float = 80.0


class LintIssue(BaseModel):
    """A single code quality finding."""

    line: int
    column: int = 0
    severity: str = "warning"
    message: str
    rule: str = ""


class LintResult(BaseModel):
    """Aggregated lint results for a file."""

    file_path: str
    issues: list[LintIssue] = Field(default_factory=list)
    score: float = 10.0


class BDDScenario(BaseModel):
    """A BDD/Gherkin test scenario."""

    feature: str
    scenario: str
    given_steps: list[str] = Field(default_factory=list)
    when_steps: list[str] = Field(default_factory=list)
    then_steps: list[str] = Field(default_factory=list)

    def to_gherkin(self) -> str:
        """Render as Gherkin text."""
        lines = [f"Feature: {self.feature}", f"  Scenario: {self.scenario}"]
        for step in self.given_steps:
            lines.append(f"    Given {step}")
        for step in self.when_steps:
            lines.append(f"    When {step}")
        for step in self.then_steps:
            lines.append(f"    Then {step}")
        return "\n".join(lines)


class TestSuggestion(BaseModel):
    """A suggested test case for a source function."""

    function_name: str
    suggestion: str
    priority: str = "medium"
    category: str = "unit"


class FlakyTestResult(BaseModel):
    """Result of running a single test multiple times to detect flakiness."""

    test_name: str
    total_runs: int
    passes: int
    failures: int
    is_flaky: bool = False
    failure_rate: float = 0.0


class TestHealthReport(BaseModel):
    """Overall health metrics for a test suite."""

    total_tests: int = 0
    avg_duration: float = 0.0
    failure_rate: float = 0.0
    slow_tests: list[str] = Field(default_factory=list)
    test_distribution: dict[str, int] = Field(default_factory=dict)


class ProjectInfo(BaseModel):
    """Metadata about a scanned project."""

    name: str
    path: str
    test_count: int = 0
    last_run: str = ""
    status: str = "unknown"
    coverage: float = 0.0


class ValidationResult(BaseModel):
    """Result of a business-rule validation check."""

    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    record_type: str = ""
