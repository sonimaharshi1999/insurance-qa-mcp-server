# Author: Maharshi Soni | License: MIT
"""Synthetic insurance test data generation."""

from __future__ import annotations

import json
import random
import string
from datetime import date, timedelta
from typing import Any

from insurance_qa_mcp.models import (
    ClaimStatus,
    InsuranceClaim,
    InsurancePolicy,
    LineOfBusiness,
    LossType,
    PolicyStatus,
)

# ---------------------------------------------------------------------------
# Domain reference data
# ---------------------------------------------------------------------------

_FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Daniel", "Karen",
]

_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson",
    "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
]

_PREMIUM_RANGES: dict[str, tuple[float, float]] = {
    "personal_auto": (600.0, 4000.0),
    "homeowners": (800.0, 5000.0),
    "commercial_property": (2000.0, 50000.0),
    "commercial_auto": (1500.0, 25000.0),
    "workers_compensation": (3000.0, 75000.0),
    "general_liability": (1000.0, 30000.0),
    "business_owners_policy": (1500.0, 20000.0),
    "professional_liability": (2000.0, 40000.0),
}

_LOSS_TYPES_BY_LOB: dict[str, list[LossType]] = {
    "personal_auto": [LossType.COLLISION, LossType.COMPREHENSIVE, LossType.LIABILITY, LossType.BODILY_INJURY],
    "homeowners": [LossType.FIRE, LossType.WATER_DAMAGE, LossType.THEFT, LossType.WIND_HAIL],
    "commercial_property": [LossType.FIRE, LossType.WATER_DAMAGE, LossType.WIND_HAIL, LossType.PROPERTY_DAMAGE],
    "commercial_auto": [LossType.COLLISION, LossType.LIABILITY, LossType.BODILY_INJURY],
    "workers_compensation": [LossType.BODILY_INJURY, LossType.LIABILITY],
    "general_liability": [LossType.BODILY_INJURY, LossType.PROPERTY_DAMAGE, LossType.LIABILITY],
    "business_owners_policy": [LossType.FIRE, LossType.THEFT, LossType.PROPERTY_DAMAGE, LossType.LIABILITY],
    "professional_liability": [LossType.LIABILITY, LossType.OTHER],
}

_CLAIM_DESCRIPTIONS: dict[str, list[str]] = {
    "collision": ["Rear-end collision at intersection", "Side-impact at parking lot", "Single-vehicle accident on highway"],
    "comprehensive": ["Windshield cracked by road debris", "Hail damage to vehicle", "Animal strike on rural road"],
    "liability": ["Third-party bodily injury claim", "Property damage to adjacent building", "Slip and fall on premises"],
    "property_damage": ["Storm damage to roof", "Burst pipe flooding basement", "Falling tree damaged structure"],
    "bodily_injury": ["Worker injured on job site", "Customer slip and fall", "Vehicle occupant injury"],
    "theft": ["Vehicle stolen from driveway", "Break-in and equipment theft", "Inventory shrinkage claim"],
    "fire": ["Kitchen fire spread to structure", "Electrical fire in commercial unit", "Wildfire damage to property"],
    "water_damage": ["Burst pipe in second floor", "Sewer backup in basement", "Roof leak during storm"],
    "wind_hail": ["Hail damage to roof and siding", "Wind-blown debris damage", "Tornado damage to outbuilding"],
    "other": ["Miscellaneous claim filed", "Unusual loss event reported", "Complex multi-peril loss"],
}


def generate_test_data_impl(
    line_of_business: str = "personal_auto",
    count: int = 10,
    data_type: str = "policy",
    seed: int | None = None,
) -> str:
    """Generate synthetic insurance test data.

    Args:
        line_of_business: The insurance LOB (e.g. ``"personal_auto"``).
        count: Number of records to generate (1--1000).
        data_type: One of ``"policy"``, ``"claim"``, or ``"billing"``.
        seed: Optional random seed for reproducibility.

    Returns:
        JSON string containing generated records.
    """
    if seed is not None:
        random.seed(seed)

    count = max(1, min(count, 1000))

    # Validate LOB
    try:
        lob = LineOfBusiness(line_of_business)
    except ValueError:
        valid = [e.value for e in LineOfBusiness]
        return json.dumps({"error": f"Invalid line_of_business. Choose from: {valid}"})

    generators = {
        "policy": _generate_policies,
        "claim": _generate_claims,
        "billing": _generate_billing,
    }

    generator = generators.get(data_type)
    if generator is None:
        return json.dumps({"error": f"Invalid data_type. Choose from: {list(generators.keys())}"})

    records = generator(lob, count)
    return json.dumps(
        {
            "data_type": data_type,
            "line_of_business": lob.value,
            "count": len(records),
            "records": records,
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def _generate_policies(lob: LineOfBusiness, count: int) -> list[dict[str, Any]]:
    """Generate synthetic policy records."""
    records: list[dict[str, Any]] = []
    today = date.today()

    for i in range(count):
        eff = today - timedelta(days=random.randint(0, 365))
        exp = eff + timedelta(days=random.choice([180, 365]))
        status = random.choice(list(PolicyStatus))
        low, high = _PREMIUM_RANGES.get(lob.value, (500.0, 5000.0))
        premium = round(random.uniform(low, high), 2)

        policy = InsurancePolicy(
            policy_number=_gen_policy_number(i),
            line_of_business=lob,
            effective_date=eff.isoformat(),
            expiration_date=exp.isoformat(),
            status=status,
            premium=premium,
            insured_name=_gen_name(),
            coverage_limits=_gen_coverage_limits(lob),
        )
        records.append(policy.model_dump())

    return records


def _generate_claims(lob: LineOfBusiness, count: int) -> list[dict[str, Any]]:
    """Generate synthetic claim records."""
    records: list[dict[str, Any]] = []
    today = date.today()
    loss_types = _LOSS_TYPES_BY_LOB.get(lob.value, [LossType.OTHER])

    for i in range(count):
        loss_date = today - timedelta(days=random.randint(1, 180))
        report_delay = random.randint(0, 14)
        reported_date = loss_date + timedelta(days=report_delay)
        loss_type = random.choice(loss_types)
        descriptions = _CLAIM_DESCRIPTIONS.get(loss_type.value, ["Claim filed"])

        claim = InsuranceClaim(
            claim_number=_gen_claim_number(i),
            policy_number=_gen_policy_number(random.randint(0, 999)),
            line_of_business=lob,
            loss_date=loss_date.isoformat(),
            reported_date=reported_date.isoformat(),
            status=random.choice(list(ClaimStatus)),
            loss_type=loss_type,
            loss_amount=round(random.uniform(100.0, 500000.0), 2),
            description=random.choice(descriptions),
            claimant_name=_gen_name(),
        )
        records.append(claim.model_dump())

    return records


def _generate_billing(lob: LineOfBusiness, count: int) -> list[dict[str, Any]]:
    """Generate synthetic billing records."""
    records: list[dict[str, Any]] = []
    today = date.today()

    for i in range(count):
        due_date = today + timedelta(days=random.randint(-60, 90))
        paid = random.random() < 0.7
        low, high = _PREMIUM_RANGES.get(lob.value, (500.0, 5000.0))
        installments = random.choice([1, 2, 4, 6, 12])
        amount = round(random.uniform(low, high) / installments, 2)

        record = {
            "billing_id": f"BIL-{i + 1:06d}",
            "policy_number": _gen_policy_number(random.randint(0, 999)),
            "amount_due": amount,
            "amount_paid": amount if paid else 0.0,
            "due_date": due_date.isoformat(),
            "payment_date": (due_date - timedelta(days=random.randint(0, 5))).isoformat() if paid else "",
            "payment_method": random.choice(["direct_bill", "agency_bill", "eft", "credit_card"]),
            "status": "paid" if paid else random.choice(["pending", "overdue", "cancelled"]),
            "installment_number": random.randint(1, installments),
            "total_installments": installments,
        }
        records.append(record)

    return records


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gen_policy_number(index: int) -> str:
    prefix = random.choice(["PA", "HO", "CP", "CA", "WC", "GL", "BP", "PL"])
    return f"{prefix}-{index + 1:07d}"


def _gen_claim_number(index: int) -> str:
    return f"CLM-{index + 1:08d}"


def _gen_name() -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def _gen_coverage_limits(lob: LineOfBusiness) -> dict[str, Any]:
    """Generate realistic coverage limits for a line of business."""
    limits: dict[str, Any] = {}

    if lob in (LineOfBusiness.PERSONAL_AUTO, LineOfBusiness.COMMERCIAL_AUTO):
        limits["bodily_injury_per_person"] = random.choice([25000, 50000, 100000, 250000])
        limits["bodily_injury_per_accident"] = limits["bodily_injury_per_person"] * 2
        limits["property_damage"] = random.choice([25000, 50000, 100000])
        limits["uninsured_motorist"] = random.choice([25000, 50000, 100000])
        limits["collision_deductible"] = random.choice([250, 500, 1000])
        limits["comprehensive_deductible"] = random.choice([100, 250, 500])
    elif lob == LineOfBusiness.HOMEOWNERS:
        limits["dwelling"] = random.choice([150000, 250000, 400000, 600000])
        limits["personal_property"] = int(limits["dwelling"] * 0.5)
        limits["liability"] = random.choice([100000, 300000, 500000])
        limits["medical_payments"] = random.choice([1000, 5000])
        limits["deductible"] = random.choice([500, 1000, 2500])
    elif lob in (LineOfBusiness.COMMERCIAL_PROPERTY, LineOfBusiness.BOP):
        limits["building"] = random.choice([500000, 1000000, 2500000])
        limits["business_personal_property"] = random.choice([100000, 250000, 500000])
        limits["business_income"] = random.choice([50000, 100000, 250000])
        limits["deductible"] = random.choice([1000, 2500, 5000])
    elif lob == LineOfBusiness.GENERAL_LIABILITY:
        limits["each_occurrence"] = random.choice([500000, 1000000, 2000000])
        limits["general_aggregate"] = limits["each_occurrence"] * 2
        limits["products_completed_ops"] = limits["each_occurrence"]
        limits["personal_advertising_injury"] = limits["each_occurrence"]
    elif lob == LineOfBusiness.WORKERS_COMP:
        limits["each_accident"] = random.choice([500000, 1000000])
        limits["disease_each_employee"] = limits["each_accident"]
        limits["disease_policy_limit"] = limits["each_accident"]
    else:
        limits["per_occurrence"] = random.choice([500000, 1000000, 2000000])
        limits["aggregate"] = limits["per_occurrence"] * 2
        limits["deductible"] = random.choice([1000, 2500, 5000, 10000])

    return limits
