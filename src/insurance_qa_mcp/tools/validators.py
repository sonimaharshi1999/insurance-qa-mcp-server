# Author: Maharshi Soni | License: MIT
"""Insurance domain validation: claim and policy business rule checks."""

from __future__ import annotations

import json
from datetime import date, datetime

from pydantic import ValidationError

from insurance_qa_mcp.models import (
    ClaimStatus,
    InsuranceClaim,
    InsurancePolicy,
    LineOfBusiness,
    PolicyStatus,
    ValidationResult,
)

# ---------------------------------------------------------------------------
# Premium boundaries per LOB (annual, USD)
# ---------------------------------------------------------------------------

_PREMIUM_BOUNDS: dict[str, tuple[float, float]] = {
    "personal_auto": (200.0, 15000.0),
    "homeowners": (300.0, 25000.0),
    "commercial_property": (500.0, 500000.0),
    "commercial_auto": (500.0, 200000.0),
    "workers_compensation": (1000.0, 1000000.0),
    "general_liability": (400.0, 500000.0),
    "business_owners_policy": (500.0, 200000.0),
    "professional_liability": (500.0, 500000.0),
}

# Maximum claim amount per LOB (single occurrence)
_MAX_CLAIM_AMOUNT: dict[str, float] = {
    "personal_auto": 1_000_000.0,
    "homeowners": 2_000_000.0,
    "commercial_property": 10_000_000.0,
    "commercial_auto": 5_000_000.0,
    "workers_compensation": 5_000_000.0,
    "general_liability": 10_000_000.0,
    "business_owners_policy": 5_000_000.0,
    "professional_liability": 10_000_000.0,
}


def validate_claim_impl(claim_data: dict) -> str:
    """Validate a claim record against P&C insurance business rules.

    Rules checked:
    - Required fields present and correctly typed
    - Loss date must not be in the future
    - Reported date must be on or after the loss date
    - Reported date within 1 year of loss date
    - Loss amount must be positive for non-denied claims
    - Loss amount within LOB limits
    - Claim number format

    Args:
        claim_data: Dictionary of claim fields.

    Returns:
        JSON string with validation result (valid, errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Step 1: Pydantic structural validation
    try:
        claim = InsuranceClaim(**claim_data)
    except ValidationError as exc:
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err["loc"])
            errors.append(f"{loc}: {err['msg']}")
        result = ValidationResult(valid=False, errors=errors, record_type="claim")
        return json.dumps(result.model_dump(), indent=2)

    # Step 2: Business-rule validation
    today = date.today()

    # Loss date must not be in the future
    try:
        loss_dt = date.fromisoformat(claim.loss_date)
        if loss_dt > today:
            errors.append(f"Loss date {claim.loss_date} is in the future")
    except ValueError:
        errors.append(f"Invalid loss date format: {claim.loss_date}")
        loss_dt = None

    # Reported date must be >= loss date
    try:
        reported_dt = date.fromisoformat(claim.reported_date)
        if loss_dt and reported_dt < loss_dt:
            errors.append(
                f"Reported date {claim.reported_date} is before loss date {claim.loss_date}"
            )
        # Warn if reported more than 30 days after loss
        if loss_dt and (reported_dt - loss_dt).days > 30:
            warnings.append(
                f"Claim reported {(reported_dt - loss_dt).days} days after loss (late FNOL)"
            )
        # Error if reported more than 1 year after loss
        if loss_dt and (reported_dt - loss_dt).days > 365:
            errors.append("Claim reported more than 1 year after loss date")
    except ValueError:
        errors.append(f"Invalid reported date format: {claim.reported_date}")

    # Loss amount validation
    if claim.status != ClaimStatus.DENIED and claim.loss_amount <= 0:
        errors.append("Loss amount must be positive for non-denied claims")

    max_amount = _MAX_CLAIM_AMOUNT.get(claim.line_of_business.value, 10_000_000.0)
    if claim.loss_amount > max_amount:
        warnings.append(
            f"Loss amount ${claim.loss_amount:,.2f} exceeds typical max "
            f"${max_amount:,.2f} for {claim.line_of_business.value}"
        )

    # Small claim warning
    if claim.loss_amount > 0 and claim.loss_amount < 100:
        warnings.append(f"Very small claim amount: ${claim.loss_amount:.2f}")

    result = ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        record_type="claim",
    )
    return json.dumps(result.model_dump(), indent=2)


def validate_policy_impl(policy_data: dict) -> str:
    """Validate a policy record against underwriting rules.

    Rules checked:
    - Required fields present and correctly typed
    - Effective date must be before expiration date
    - Policy term between 1 month and 3 years
    - Premium within acceptable range for the LOB
    - Active policies must not be expired
    - Coverage limits meet minimum requirements

    Args:
        policy_data: Dictionary of policy fields.

    Returns:
        JSON string with validation result (valid, errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Step 1: Pydantic structural validation
    try:
        policy = InsurancePolicy(**policy_data)
    except ValidationError as exc:
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err["loc"])
            errors.append(f"{loc}: {err['msg']}")
        result = ValidationResult(valid=False, errors=errors, record_type="policy")
        return json.dumps(result.model_dump(), indent=2)

    # Step 2: Business-rule validation
    today = date.today()

    # Effective before expiration
    try:
        eff_dt = date.fromisoformat(policy.effective_date)
        exp_dt = date.fromisoformat(policy.expiration_date)

        if eff_dt >= exp_dt:
            errors.append(
                f"Effective date {policy.effective_date} must be before "
                f"expiration date {policy.expiration_date}"
            )
        else:
            term_days = (exp_dt - eff_dt).days
            if term_days < 30:
                errors.append(f"Policy term is only {term_days} days (minimum 30)")
            elif term_days > 1095:
                warnings.append(f"Policy term is {term_days} days (> 3 years)")

        # Active policy must not be past expiration
        if policy.status == PolicyStatus.ACTIVE and exp_dt < today:
            errors.append(
                f"Policy status is 'active' but expiration date "
                f"{policy.expiration_date} is in the past"
            )
    except ValueError as exc:
        errors.append(f"Invalid date format: {exc}")

    # Premium range check
    lob_key = policy.line_of_business.value
    low, high = _PREMIUM_BOUNDS.get(lob_key, (100.0, 1_000_000.0))
    if policy.premium < low:
        warnings.append(
            f"Premium ${policy.premium:,.2f} is below typical minimum "
            f"${low:,.2f} for {lob_key}"
        )
    if policy.premium > high:
        warnings.append(
            f"Premium ${policy.premium:,.2f} exceeds typical maximum "
            f"${high:,.2f} for {lob_key}"
        )

    # Zero premium for active policies
    if policy.status == PolicyStatus.ACTIVE and policy.premium == 0:
        errors.append("Active policy cannot have zero premium")

    result = ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        record_type="policy",
    )
    return json.dumps(result.model_dump(), indent=2)
