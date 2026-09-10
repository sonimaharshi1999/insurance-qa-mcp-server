# Author: Maharshi Soni | License: MIT
"""BDD/Gherkin scenario generation for insurance workflows."""

from __future__ import annotations

import json
from typing import Any

from insurance_qa_mcp.models import BDDScenario

# ---------------------------------------------------------------------------
# Scenario templates by insurance domain workflow
# ---------------------------------------------------------------------------

_WORKFLOW_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "claim_submission": [
        {
            "scenario": "Submit a new first notice of loss",
            "given": [
                "an active policy {policy_number} for {line_of_business}",
                "a loss occurred on {loss_date}",
            ],
            "when": [
                "the insured submits a first notice of loss",
                "the claim handler records the loss details",
            ],
            "then": [
                "a new claim is created with status 'open'",
                "the claim number is generated and returned",
                "the loss date is recorded correctly",
            ],
        },
        {
            "scenario": "Reject claim with future loss date",
            "given": [
                "a loss date that is in the future",
            ],
            "when": [
                "the insured submits the claim",
            ],
            "then": [
                "the claim is rejected with validation error",
                "the error message indicates the loss date is invalid",
            ],
        },
        {
            "scenario": "Submit claim on expired policy",
            "given": [
                "a policy {policy_number} with status 'expired'",
                "a loss date after the policy expiration",
            ],
            "when": [
                "the insured submits a claim against the expired policy",
            ],
            "then": [
                "the system flags the claim for review",
                "a warning indicates the policy was not active at time of loss",
            ],
        },
    ],
    "policy_binding": [
        {
            "scenario": "Bind a new personal auto policy",
            "given": [
                "an applicant with valid driver information",
                "the underwriting review is approved",
                "the premium is calculated as {premium}",
            ],
            "when": [
                "the agent binds the policy",
                "payment for the first installment is received",
            ],
            "then": [
                "the policy status changes to 'active'",
                "the policy number is generated",
                "the effective date is set to {effective_date}",
                "the billing schedule is created",
            ],
        },
        {
            "scenario": "Reject binding with insufficient coverage limits",
            "given": [
                "an application with liability limits below state minimum",
            ],
            "when": [
                "the agent attempts to bind the policy",
            ],
            "then": [
                "the binding is rejected",
                "the error message indicates minimum coverage requirements",
            ],
        },
    ],
    "billing_payment": [
        {
            "scenario": "Process a scheduled installment payment",
            "given": [
                "an active policy with a payment due on {due_date}",
                "the installment amount is {amount}",
            ],
            "when": [
                "the payment is received via {payment_method}",
            ],
            "then": [
                "the billing record is updated to 'paid'",
                "the payment date is recorded",
                "the next installment due date is scheduled",
            ],
        },
        {
            "scenario": "Handle overdue payment with grace period",
            "given": [
                "an active policy with a payment overdue by 15 days",
                "the grace period is 30 days",
            ],
            "when": [
                "the system runs the overdue check",
            ],
            "then": [
                "a payment reminder notice is generated",
                "the policy remains active during the grace period",
            ],
        },
        {
            "scenario": "Cancel policy for non-payment",
            "given": [
                "an active policy with a payment overdue by 45 days",
                "the grace period of 30 days has expired",
            ],
            "when": [
                "the system runs the cancellation check",
            ],
            "then": [
                "the policy status changes to 'cancelled'",
                "a cancellation notice is sent to the insured",
                "the earned premium is calculated",
            ],
        },
    ],
    "claim_adjudication": [
        {
            "scenario": "Approve a straightforward property damage claim",
            "given": [
                "an open claim for {loss_type} with amount {loss_amount}",
                "the adjuster has completed the inspection",
                "the damage is within policy coverage limits",
            ],
            "when": [
                "the adjuster approves the claim for payment",
            ],
            "then": [
                "the claim status changes to 'closed'",
                "a payment is issued to the claimant",
                "the reserve is adjusted to match the payment",
            ],
        },
        {
            "scenario": "Deny claim due to policy exclusion",
            "given": [
                "an open claim for a peril excluded under the policy",
                "the adjuster reviews the policy exclusions",
            ],
            "when": [
                "the adjuster denies the claim",
            ],
            "then": [
                "the claim status changes to 'denied'",
                "the denial reason references the specific exclusion",
                "the insured is notified of their appeal rights",
            ],
        },
    ],
    "policy_renewal": [
        {
            "scenario": "Auto-renew policy at expiration",
            "given": [
                "an active policy approaching expiration in 30 days",
                "no claims in the current term",
            ],
            "when": [
                "the renewal process runs",
            ],
            "then": [
                "a renewal offer is generated",
                "the new premium reflects the claims-free discount",
                "the renewal effective date matches the current expiration",
            ],
        },
    ],
}


def generate_bdd_scenarios_impl(
    feature: str = "claim_submission",
    domain: str = "property_casualty",
) -> str:
    """Generate BDD/Gherkin test scenarios for insurance workflows.

    Available features: ``claim_submission``, ``policy_binding``,
    ``billing_payment``, ``claim_adjudication``, ``policy_renewal``.

    Args:
        feature: The insurance workflow to generate scenarios for.
        domain: Insurance domain context (currently ``"property_casualty"``).

    Returns:
        JSON string containing Gherkin scenarios.
    """
    templates = _WORKFLOW_TEMPLATES.get(feature)
    if templates is None:
        available = list(_WORKFLOW_TEMPLATES.keys())
        return json.dumps({
            "error": f"Unknown feature '{feature}'. Available: {available}"
        })

    feature_title = feature.replace("_", " ").title()
    scenarios: list[dict[str, Any]] = []
    gherkin_blocks: list[str] = []

    for tmpl in templates:
        scenario = BDDScenario(
            feature=feature_title,
            scenario=tmpl["scenario"],
            given_steps=tmpl["given"],
            when_steps=tmpl["when"],
            then_steps=tmpl["then"],
        )
        scenarios.append(scenario.model_dump())
        gherkin_blocks.append(scenario.to_gherkin())

    return json.dumps(
        {
            "feature": feature_title,
            "domain": domain,
            "scenario_count": len(scenarios),
            "scenarios": scenarios,
            "gherkin": "\n\n".join(gherkin_blocks),
        },
        indent=2,
    )
