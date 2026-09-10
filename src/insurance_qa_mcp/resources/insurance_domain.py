# Author: Maharshi Soni | License: MIT
"""Insurance domain reference data: lines of business, rules, test patterns."""

from __future__ import annotations

import json
from typing import Any


def get_insurance_lines() -> str:
    """Return all available insurance lines and their attributes.

    Covers standard P&C lines with Guidewire naming conventions,
    typical coverage types, and validation rules.

    Returns:
        JSON string with insurance line details.
    """
    lines: dict[str, dict[str, Any]] = {
        "personal_auto": {
            "display_name": "Personal Auto",
            "guidewire_lob": "PersonalAutoLine",
            "center": "PolicyCenter",
            "description": "Coverage for personal vehicles",
            "coverage_types": [
                "Bodily Injury Liability",
                "Property Damage Liability",
                "Collision",
                "Comprehensive",
                "Uninsured/Underinsured Motorist",
                "Medical Payments",
                "Personal Injury Protection",
            ],
            "common_claims": ["Collision", "Comprehensive", "Liability"],
            "typical_premium_range": {"min": 600, "max": 4000, "currency": "USD"},
            "regulatory_notes": "Subject to state minimum liability limits",
        },
        "homeowners": {
            "display_name": "Homeowners",
            "guidewire_lob": "HomeownersLine",
            "center": "PolicyCenter",
            "description": "Coverage for residential property and liability",
            "coverage_types": [
                "Dwelling (Coverage A)",
                "Other Structures (Coverage B)",
                "Personal Property (Coverage C)",
                "Loss of Use (Coverage D)",
                "Personal Liability (Coverage E)",
                "Medical Payments (Coverage F)",
            ],
            "common_claims": ["Fire", "Water Damage", "Theft", "Wind/Hail", "Liability"],
            "typical_premium_range": {"min": 800, "max": 5000, "currency": "USD"},
            "regulatory_notes": "Flood and earthquake typically excluded; separate policies required",
        },
        "commercial_property": {
            "display_name": "Commercial Property",
            "guidewire_lob": "CommercialPropertyLine",
            "center": "PolicyCenter",
            "description": "Coverage for business-owned buildings and contents",
            "coverage_types": [
                "Building Coverage",
                "Business Personal Property",
                "Business Income",
                "Extra Expense",
                "Equipment Breakdown",
            ],
            "common_claims": ["Fire", "Wind/Hail", "Water Damage", "Theft", "Equipment Failure"],
            "typical_premium_range": {"min": 2000, "max": 50000, "currency": "USD"},
            "regulatory_notes": "Coinsurance clauses may apply",
        },
        "commercial_auto": {
            "display_name": "Commercial Auto",
            "guidewire_lob": "CommercialAutoLine",
            "center": "PolicyCenter",
            "description": "Coverage for business-owned vehicles",
            "coverage_types": [
                "Liability",
                "Physical Damage",
                "Uninsured Motorist",
                "Medical Payments",
                "Hired/Non-Owned Auto",
            ],
            "common_claims": ["Collision", "Liability", "Cargo"],
            "typical_premium_range": {"min": 1500, "max": 25000, "currency": "USD"},
            "regulatory_notes": "DOT/FMCSA requirements for commercial vehicles",
        },
        "workers_compensation": {
            "display_name": "Workers Compensation",
            "guidewire_lob": "WorkersCompLine",
            "center": "PolicyCenter",
            "description": "Coverage for employee work-related injuries",
            "coverage_types": [
                "Part One - Workers Compensation",
                "Part Two - Employers Liability",
            ],
            "common_claims": ["Bodily Injury", "Occupational Disease", "Lost Wages"],
            "typical_premium_range": {"min": 3000, "max": 75000, "currency": "USD"},
            "regulatory_notes": "Mandatory in most states; rates set by NCCI or state bureaus",
        },
        "general_liability": {
            "display_name": "General Liability (CGL)",
            "guidewire_lob": "GeneralLiabilityLine",
            "center": "PolicyCenter",
            "description": "Coverage for third-party bodily injury and property damage",
            "coverage_types": [
                "Premises/Operations",
                "Products/Completed Operations",
                "Personal and Advertising Injury",
                "Medical Payments",
                "Damage to Rented Premises",
            ],
            "common_claims": ["Slip and Fall", "Product Liability", "Property Damage"],
            "typical_premium_range": {"min": 1000, "max": 30000, "currency": "USD"},
            "regulatory_notes": "ISO CGL forms widely used; occurrence vs claims-made distinction",
        },
        "business_owners_policy": {
            "display_name": "Business Owners Policy (BOP)",
            "guidewire_lob": "BOPLine",
            "center": "PolicyCenter",
            "description": "Bundled property and liability for small businesses",
            "coverage_types": [
                "Building",
                "Business Personal Property",
                "Business Income",
                "General Liability",
                "Equipment Breakdown",
            ],
            "common_claims": ["Property Damage", "Liability", "Business Interruption"],
            "typical_premium_range": {"min": 1500, "max": 20000, "currency": "USD"},
            "regulatory_notes": "Eligibility restrictions by business class and revenue size",
        },
        "professional_liability": {
            "display_name": "Professional Liability (E&O)",
            "guidewire_lob": "ProfessionalLiabilityLine",
            "center": "PolicyCenter",
            "description": "Coverage for professional errors and omissions",
            "coverage_types": [
                "Professional Services Liability",
                "Defense Costs",
                "Regulatory Proceedings",
            ],
            "common_claims": ["Negligence", "Breach of Duty", "Misrepresentation"],
            "typical_premium_range": {"min": 2000, "max": 40000, "currency": "USD"},
            "regulatory_notes": "Claims-made form; retroactive date and extended reporting provisions",
        },
    }

    return json.dumps(
        {"line_count": len(lines), "lines": lines},
        indent=2,
    )


def get_test_patterns() -> str:
    """Return common QA test patterns and templates for insurance applications.

    Returns:
        JSON string with reusable test patterns.
    """
    patterns: list[dict[str, Any]] = [
        {
            "name": "Policy Lifecycle Test",
            "description": "Tests the full lifecycle of a policy: quote -> bind -> endorse -> renew -> cancel",
            "template": (
                "def test_policy_lifecycle():\n"
                "    policy = create_policy(status='draft')\n"
                "    policy = bind_policy(policy)\n"
                "    assert policy.status == 'active'\n"
                "    policy = endorse_policy(policy, changes={...})\n"
                "    assert policy.status == 'active'\n"
                "    policy = renew_policy(policy)\n"
                "    assert policy.status == 'renewed'\n"
                "    policy = cancel_policy(policy, reason='insured_request')\n"
                "    assert policy.status == 'cancelled'\n"
            ),
            "applicable_lobs": ["all"],
            "category": "integration",
        },
        {
            "name": "Claim FNOL Validation",
            "description": "Tests first notice of loss submission with various valid and invalid inputs",
            "template": (
                "@pytest.mark.parametrize('loss_date,expected_valid', [\n"
                "    ('2024-01-15', True),\n"
                "    ('2099-01-01', False),  # future date\n"
                "    ('invalid', False),     # bad format\n"
                "])\n"
                "def test_fnol_validation(loss_date, expected_valid):\n"
                "    result = validate_fnol(loss_date=loss_date, ...)\n"
                "    assert result.is_valid == expected_valid\n"
            ),
            "applicable_lobs": ["all"],
            "category": "unit",
        },
        {
            "name": "Premium Calculation Boundary",
            "description": "Tests premium calculation at boundary values for each rating factor",
            "template": (
                "@pytest.mark.parametrize('age,expected_tier', [\n"
                "    (16, 'high_risk'),\n"
                "    (25, 'standard'),\n"
                "    (65, 'preferred'),\n"
                "    (85, 'high_risk'),\n"
                "])\n"
                "def test_premium_age_factor(age, expected_tier):\n"
                "    tier = calculate_age_tier(age)\n"
                "    assert tier == expected_tier\n"
            ),
            "applicable_lobs": ["personal_auto", "homeowners"],
            "category": "unit",
        },
        {
            "name": "Claim Status Transition",
            "description": "Verifies only valid status transitions are allowed",
            "template": (
                "VALID_TRANSITIONS = {\n"
                "    'open': ['closed', 'pending', 'subrogation'],\n"
                "    'pending': ['open', 'denied'],\n"
                "    'closed': ['reopened'],\n"
                "    'reopened': ['closed', 'pending'],\n"
                "    'denied': ['reopened'],\n"
                "}\n"
                "\n"
                "def test_claim_valid_transition():\n"
                "    claim = create_claim(status='open')\n"
                "    claim = transition_claim(claim, 'closed')\n"
                "    assert claim.status == 'closed'\n"
                "\n"
                "def test_claim_invalid_transition():\n"
                "    claim = create_claim(status='denied')\n"
                "    with pytest.raises(InvalidTransitionError):\n"
                "        transition_claim(claim, 'closed')\n"
            ),
            "applicable_lobs": ["all"],
            "category": "unit",
        },
        {
            "name": "Coverage Limit Validation",
            "description": "Tests that coverage limits meet state minimums and carrier maximums",
            "template": (
                "def test_coverage_limits_meet_state_minimum():\n"
                "    limits = {'bodily_injury_per_person': 25000}\n"
                "    result = validate_limits(state='CA', limits=limits)\n"
                "    assert result.meets_minimum is True\n"
                "\n"
                "def test_coverage_limits_below_minimum():\n"
                "    limits = {'bodily_injury_per_person': 5000}\n"
                "    result = validate_limits(state='CA', limits=limits)\n"
                "    assert result.meets_minimum is False\n"
            ),
            "applicable_lobs": ["personal_auto", "commercial_auto"],
            "category": "unit",
        },
        {
            "name": "Data Migration Smoke Test",
            "description": "After a data migration, verify record counts and key fields are preserved",
            "template": (
                "def test_migration_record_count():\n"
                "    source_count = get_count(source_db, 'policies')\n"
                "    target_count = get_count(target_db, 'policies')\n"
                "    assert source_count == target_count\n"
                "\n"
                "def test_migration_key_fields():\n"
                "    source = get_record(source_db, policy_number='PA-001')\n"
                "    target = get_record(target_db, policy_number='PA-001')\n"
                "    assert source.premium == target.premium\n"
                "    assert source.effective_date == target.effective_date\n"
            ),
            "applicable_lobs": ["all"],
            "category": "smoke",
        },
    ]

    return json.dumps(
        {"pattern_count": len(patterns), "patterns": patterns},
        indent=2,
    )
