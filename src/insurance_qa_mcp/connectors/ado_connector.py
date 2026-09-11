# Author: Maharshi Soni | License: MIT
"""Mock Azure DevOps / Jira connector for insurance QA user stories and test plans."""

from __future__ import annotations

import json
import random
from typing import Any


# ---------------------------------------------------------------------------
# Mock Data: Insurance Domain User Stories
# ---------------------------------------------------------------------------

_MOCK_STORIES: list[dict[str, Any]] = [
    {
        "id": "US-1001",
        "title": "PolicyCenter: Bind new Personal Auto policy with multi-vehicle discount",
        "type": "User Story",
        "status": "Active",
        "sprint": "Sprint 14",
        "priority": "High",
        "assigned_to": "QA Team",
        "story_points": 8,
        "description": (
            "As an underwriter, I want to bind a new personal auto policy "
            "with multi-vehicle discount so that the premium reflects the "
            "correct rating factor for households with 2+ vehicles."
        ),
        "acceptance_criteria": [
            "Policy can be bound with 2-5 vehicles on the same policy",
            "Multi-vehicle discount of 10-25% is applied based on vehicle count",
            "Premium calculation reflects the discount on the declarations page",
            "Discount is removed if vehicle count drops below 2 on endorsement",
            "Audit trail records the discount application and amount",
        ],
        "tags": ["PolicyCenter", "personal_auto", "rating", "discount"],
    },
    {
        "id": "US-1002",
        "title": "ClaimCenter: Submit FNOL for homeowners water damage claim",
        "type": "User Story",
        "status": "Active",
        "sprint": "Sprint 14",
        "priority": "High",
        "assigned_to": "QA Team",
        "story_points": 5,
        "description": (
            "As a claim handler, I want to submit a first notice of loss "
            "for a homeowners water damage claim so that the claim is created "
            "with the correct loss type and coverage verification."
        ),
        "acceptance_criteria": [
            "FNOL form captures all required fields: loss date, description, contact info",
            "Loss type is set to 'water_damage' and linked to Coverage A or C",
            "Policy coverage is verified automatically at FNOL submission",
            "Claim number is generated in CLM-XXXXXXXX format",
            "If policy is expired, system flags claim for manual review",
        ],
        "tags": ["ClaimCenter", "homeowners", "FNOL", "water_damage"],
    },
    {
        "id": "US-1003",
        "title": "BillingCenter: Process installment payment via EFT",
        "type": "User Story",
        "status": "Active",
        "sprint": "Sprint 14",
        "priority": "Medium",
        "assigned_to": "QA Team",
        "story_points": 3,
        "description": (
            "As a billing specialist, I want to process an EFT installment "
            "payment so that the billing account reflects the payment and "
            "the next installment is scheduled correctly."
        ),
        "acceptance_criteria": [
            "EFT payment is processed within the same business day",
            "Billing record status changes from 'pending' to 'paid'",
            "Payment date and method are recorded accurately",
            "Next installment due date is calculated based on payment plan",
            "Confirmation notification is sent to the insured",
        ],
        "tags": ["BillingCenter", "billing", "EFT", "installment"],
    },
    {
        "id": "US-1004",
        "title": "PolicyCenter: Endorse commercial property policy to add location",
        "type": "User Story",
        "status": "New",
        "sprint": "Sprint 15",
        "priority": "Medium",
        "assigned_to": "Unassigned",
        "story_points": 8,
        "description": (
            "As an underwriter, I want to endorse a commercial property "
            "policy to add a new location so that coverage extends to "
            "the additional premises with correct rating."
        ),
        "acceptance_criteria": [
            "New location can be added via mid-term endorsement",
            "Building and BPP coverage limits are set per location",
            "Pro-rated premium change is calculated from endorsement effective date",
            "Endorsement creates a new policy version with updated schedule",
            "Location-specific deductibles can be configured independently",
        ],
        "tags": ["PolicyCenter", "commercial_property", "endorsement", "location"],
    },
    {
        "id": "US-1005",
        "title": "ClaimCenter: Adjudicate workers comp claim with reserve adjustment",
        "type": "User Story",
        "status": "Active",
        "sprint": "Sprint 14",
        "priority": "Critical",
        "assigned_to": "QA Team",
        "story_points": 13,
        "description": (
            "As a claim adjuster, I want to adjudicate a workers compensation "
            "claim and adjust reserves so that the financial exposure accurately "
            "reflects the medical and indemnity costs."
        ),
        "acceptance_criteria": [
            "Adjuster can update reserve amounts for medical and indemnity separately",
            "Reserve changes trigger supervisor approval when exceeding authority limit",
            "Payment can be issued against the claim up to the reserve amount",
            "Claim financials dashboard shows current incurred = paid + reserves",
            "State-specific WC fee schedule is applied to medical payments",
        ],
        "tags": ["ClaimCenter", "workers_compensation", "adjudication", "reserves"],
    },
    {
        "id": "US-1006",
        "title": "PolicyCenter: Renew general liability policy with claims surcharge",
        "type": "User Story",
        "status": "New",
        "sprint": "Sprint 15",
        "priority": "Low",
        "assigned_to": "Unassigned",
        "story_points": 5,
        "description": (
            "As an underwriter, I want to renew a general liability policy "
            "with a claims surcharge so that the renewal premium reflects "
            "the insured's loss history."
        ),
        "acceptance_criteria": [
            "Renewal offer is generated 60 days before expiration",
            "Claims surcharge is calculated based on 3-year loss ratio",
            "Surcharge percentage is displayed on the renewal quote",
            "Insured can accept or reject the renewal offer",
            "If rejected, policy status changes to 'non-renewed' at expiration",
        ],
        "tags": ["PolicyCenter", "general_liability", "renewal", "surcharge"],
    },
]

_MOCK_TEST_PLANS: dict[str, dict[str, Any]] = {
    "US-1001": {
        "story_id": "US-1001",
        "test_plan_id": "TP-2001",
        "title": "Test Plan: Multi-Vehicle Discount Binding",
        "status": "In Progress",
        "total_cases": 8,
        "test_cases": [
            {"id": "TC-3001", "title": "Bind policy with 2 vehicles -- verify 10% discount", "priority": "High", "status": "Not Run"},
            {"id": "TC-3002", "title": "Bind policy with 5 vehicles -- verify 25% discount", "priority": "High", "status": "Not Run"},
            {"id": "TC-3003", "title": "Verify discount removed when vehicle count drops to 1", "priority": "Medium", "status": "Not Run"},
            {"id": "TC-3004", "title": "Verify premium recalculation on endorsement", "priority": "Medium", "status": "Not Run"},
            {"id": "TC-3005", "title": "Verify audit trail for discount application", "priority": "Low", "status": "Not Run"},
            {"id": "TC-3006", "title": "Negative: Bind with 0 vehicles -- expect validation error", "priority": "High", "status": "Not Run"},
            {"id": "TC-3007", "title": "Negative: Bind with 6+ vehicles -- verify max limit", "priority": "Medium", "status": "Not Run"},
            {"id": "TC-3008", "title": "Boundary: Exactly 2 vehicles at discount threshold", "priority": "Medium", "status": "Not Run"},
        ],
    },
    "US-1002": {
        "story_id": "US-1002",
        "test_plan_id": "TP-2002",
        "title": "Test Plan: Homeowners Water Damage FNOL",
        "status": "Draft",
        "total_cases": 6,
        "test_cases": [
            {"id": "TC-3101", "title": "Submit FNOL with all required fields", "priority": "High", "status": "Not Run"},
            {"id": "TC-3102", "title": "Verify loss type set to water_damage", "priority": "High", "status": "Not Run"},
            {"id": "TC-3103", "title": "Verify claim number format CLM-XXXXXXXX", "priority": "Medium", "status": "Not Run"},
            {"id": "TC-3104", "title": "Submit FNOL on expired policy -- verify review flag", "priority": "High", "status": "Not Run"},
            {"id": "TC-3105", "title": "Verify coverage verification at submission", "priority": "Medium", "status": "Not Run"},
            {"id": "TC-3106", "title": "Negative: Submit FNOL with missing required fields", "priority": "High", "status": "Not Run"},
        ],
    },
    "US-1003": {
        "story_id": "US-1003",
        "test_plan_id": "TP-2003",
        "title": "Test Plan: EFT Installment Payment Processing",
        "status": "Draft",
        "total_cases": 5,
        "test_cases": [
            {"id": "TC-3201", "title": "Process EFT payment -- verify status change to paid", "priority": "High", "status": "Not Run"},
            {"id": "TC-3202", "title": "Verify payment date and method recorded", "priority": "Medium", "status": "Not Run"},
            {"id": "TC-3203", "title": "Verify next installment scheduling", "priority": "Medium", "status": "Not Run"},
            {"id": "TC-3204", "title": "Verify confirmation notification sent", "priority": "Low", "status": "Not Run"},
            {"id": "TC-3205", "title": "Negative: Process payment with insufficient funds", "priority": "High", "status": "Not Run"},
        ],
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_user_stories_impl(project: str, sprint: str = "current") -> str:
    """Return mock user stories with acceptance criteria for an insurance project.

    Args:
        project: Project name (e.g., "PolicyCenter", "ClaimCenter").
        sprint: Sprint identifier or "current" for the active sprint.

    Returns:
        JSON string with user stories matching the filters.
    """
    if not project or not project.strip():
        return json.dumps({"error": "Project name is required"})

    target_sprint = "Sprint 14" if sprint == "current" else sprint
    project_lower = project.lower().replace(" ", "")

    filtered = []
    for story in _MOCK_STORIES:
        # Filter by project tag
        tag_match = any(
            project_lower in tag.lower().replace(" ", "")
            for tag in story["tags"]
        )
        # Filter by sprint
        sprint_match = (
            sprint == "all"
            or story["sprint"].lower() == target_sprint.lower()
        )

        if tag_match and sprint_match:
            filtered.append(story)

    # If no tag match, return all stories for the sprint
    if not filtered:
        filtered = [
            s for s in _MOCK_STORIES
            if sprint == "all" or s["sprint"].lower() == target_sprint.lower()
        ]

    return json.dumps(
        {
            "project": project,
            "sprint": target_sprint if sprint != "all" else "all",
            "story_count": len(filtered),
            "stories": filtered,
        },
        indent=2,
    )


def get_test_plan_impl(story_id: str) -> str:
    """Return a mock test plan linked to a user story.

    Args:
        story_id: The user story identifier (e.g., "US-1001").

    Returns:
        JSON string with the test plan and its test cases.
    """
    if not story_id or not story_id.strip():
        return json.dumps({"error": "Story ID is required"})

    plan = _MOCK_TEST_PLANS.get(story_id.upper())
    if plan is None:
        # Generate a generic plan for unknown stories
        plan = _generate_generic_test_plan(story_id)

    return json.dumps(plan, indent=2)


def get_ado_stories_resource() -> str:
    """Return a summary of all available stories for the resource endpoint.

    Returns:
        JSON string listing all mock stories.
    """
    summary = [
        {
            "id": s["id"],
            "title": s["title"],
            "status": s["status"],
            "sprint": s["sprint"],
            "priority": s["priority"],
        }
        for s in _MOCK_STORIES
    ]
    return json.dumps(
        {"total_stories": len(summary), "stories": summary},
        indent=2,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_generic_test_plan(story_id: str) -> dict[str, Any]:
    """Generate a placeholder test plan for a story not in mock data."""
    return {
        "story_id": story_id,
        "test_plan_id": f"TP-AUTO-{story_id}",
        "title": f"Test Plan for {story_id}",
        "status": "Draft",
        "total_cases": 3,
        "test_cases": [
            {
                "id": f"TC-A-{story_id}-01",
                "title": f"Verify happy path for {story_id}",
                "priority": "High",
                "status": "Not Run",
            },
            {
                "id": f"TC-A-{story_id}-02",
                "title": f"Verify validation rules for {story_id}",
                "priority": "Medium",
                "status": "Not Run",
            },
            {
                "id": f"TC-A-{story_id}-03",
                "title": f"Negative test: invalid input for {story_id}",
                "priority": "High",
                "status": "Not Run",
            },
        ],
        "note": "Auto-generated placeholder -- customize for actual requirements",
    }
