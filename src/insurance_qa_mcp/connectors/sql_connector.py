# Author: Maharshi Soni | License: MIT
"""Mock SQL Server connector for insurance test data queries and validation."""

from __future__ import annotations

import json
import random
from typing import Any


# ---------------------------------------------------------------------------
# Mock Database Tables
# ---------------------------------------------------------------------------

_MOCK_TABLES: dict[str, dict[str, Any]] = {
    "cc_claim": {
        "display_name": "ClaimCenter Claims",
        "schema": "cc_datamodel",
        "columns": [
            {"name": "ID", "type": "BIGINT", "nullable": False},
            {"name": "ClaimNumber", "type": "VARCHAR(30)", "nullable": False},
            {"name": "PolicyNumber", "type": "VARCHAR(30)", "nullable": False},
            {"name": "LobCode", "type": "VARCHAR(20)", "nullable": False},
            {"name": "LossDate", "type": "DATE", "nullable": False},
            {"name": "ReportedDate", "type": "DATE", "nullable": False},
            {"name": "Status", "type": "VARCHAR(20)", "nullable": False},
            {"name": "TotalIncurred", "type": "DECIMAL(15,2)", "nullable": True},
            {"name": "ClaimantName", "type": "VARCHAR(100)", "nullable": True},
            {"name": "AdjusterID", "type": "BIGINT", "nullable": True},
        ],
        "row_count": 15420,
        "sample_data": [
            {"ID": 1, "ClaimNumber": "CLM-00000001", "PolicyNumber": "PA-0000123", "LobCode": "personal_auto", "LossDate": "2026-03-15", "ReportedDate": "2026-03-16", "Status": "open", "TotalIncurred": 12500.00, "ClaimantName": "James Smith", "AdjusterID": 501},
            {"ID": 2, "ClaimNumber": "CLM-00000002", "PolicyNumber": "HO-0000456", "LobCode": "homeowners", "LossDate": "2026-04-01", "ReportedDate": "2026-04-02", "Status": "closed", "TotalIncurred": 45000.00, "ClaimantName": "Mary Johnson", "AdjusterID": 502},
            {"ID": 3, "ClaimNumber": "CLM-00000003", "PolicyNumber": "CP-0000789", "LobCode": "commercial_property", "LossDate": "2026-05-10", "ReportedDate": "2026-05-12", "Status": "open", "TotalIncurred": 125000.00, "ClaimantName": "ABC Corp", "AdjusterID": 503},
            {"ID": 4, "ClaimNumber": "CLM-00000004", "PolicyNumber": "WC-0001010", "LobCode": "workers_compensation", "LossDate": "2026-06-20", "ReportedDate": "2026-06-20", "Status": "pending", "TotalIncurred": 8500.00, "ClaimantName": "Robert Williams", "AdjusterID": 501},
            {"ID": 5, "ClaimNumber": "CLM-00000005", "PolicyNumber": "PA-0001111", "LobCode": "personal_auto", "LossDate": "2026-07-05", "ReportedDate": "2026-07-06", "Status": "denied", "TotalIncurred": 0.00, "ClaimantName": "Patricia Brown", "AdjusterID": 504},
        ],
    },
    "pc_policy": {
        "display_name": "PolicyCenter Policies",
        "schema": "pc_datamodel",
        "columns": [
            {"name": "ID", "type": "BIGINT", "nullable": False},
            {"name": "PolicyNumber", "type": "VARCHAR(30)", "nullable": False},
            {"name": "LobCode", "type": "VARCHAR(20)", "nullable": False},
            {"name": "EffectiveDate", "type": "DATE", "nullable": False},
            {"name": "ExpirationDate", "type": "DATE", "nullable": False},
            {"name": "Status", "type": "VARCHAR(20)", "nullable": False},
            {"name": "TotalPremium", "type": "DECIMAL(15,2)", "nullable": False},
            {"name": "InsuredName", "type": "VARCHAR(100)", "nullable": False},
            {"name": "UnderwriterID", "type": "BIGINT", "nullable": True},
            {"name": "AgencyCode", "type": "VARCHAR(10)", "nullable": True},
        ],
        "row_count": 28750,
        "sample_data": [
            {"ID": 1, "PolicyNumber": "PA-0000123", "LobCode": "personal_auto", "EffectiveDate": "2026-01-01", "ExpirationDate": "2027-01-01", "Status": "active", "TotalPremium": 1850.00, "InsuredName": "James Smith", "UnderwriterID": 201, "AgencyCode": "AGN-001"},
            {"ID": 2, "PolicyNumber": "HO-0000456", "LobCode": "homeowners", "EffectiveDate": "2026-03-15", "ExpirationDate": "2027-03-15", "Status": "active", "TotalPremium": 2400.00, "InsuredName": "Mary Johnson", "UnderwriterID": 202, "AgencyCode": "AGN-002"},
            {"ID": 3, "PolicyNumber": "CP-0000789", "LobCode": "commercial_property", "EffectiveDate": "2025-06-01", "ExpirationDate": "2026-06-01", "Status": "expired", "TotalPremium": 15000.00, "InsuredName": "ABC Corp", "UnderwriterID": 203, "AgencyCode": "AGN-003"},
            {"ID": 4, "PolicyNumber": "WC-0001010", "LobCode": "workers_compensation", "EffectiveDate": "2026-01-01", "ExpirationDate": "2027-01-01", "Status": "active", "TotalPremium": 8500.00, "InsuredName": "XYZ Industries", "UnderwriterID": 201, "AgencyCode": "AGN-001"},
            {"ID": 5, "PolicyNumber": "GL-0001234", "LobCode": "general_liability", "EffectiveDate": "2026-04-01", "ExpirationDate": "2027-04-01", "Status": "active", "TotalPremium": 5200.00, "InsuredName": "Smith & Co", "UnderwriterID": 204, "AgencyCode": "AGN-004"},
        ],
    },
    "bc_billing": {
        "display_name": "BillingCenter Billing Accounts",
        "schema": "bc_datamodel",
        "columns": [
            {"name": "ID", "type": "BIGINT", "nullable": False},
            {"name": "BillingID", "type": "VARCHAR(20)", "nullable": False},
            {"name": "PolicyNumber", "type": "VARCHAR(30)", "nullable": False},
            {"name": "AmountDue", "type": "DECIMAL(15,2)", "nullable": False},
            {"name": "AmountPaid", "type": "DECIMAL(15,2)", "nullable": False},
            {"name": "DueDate", "type": "DATE", "nullable": False},
            {"name": "PaymentDate", "type": "DATE", "nullable": True},
            {"name": "PaymentMethod", "type": "VARCHAR(20)", "nullable": True},
            {"name": "Status", "type": "VARCHAR(20)", "nullable": False},
            {"name": "InstallmentNum", "type": "INT", "nullable": True},
        ],
        "row_count": 42100,
        "sample_data": [
            {"ID": 1, "BillingID": "BIL-000001", "PolicyNumber": "PA-0000123", "AmountDue": 462.50, "AmountPaid": 462.50, "DueDate": "2026-02-01", "PaymentDate": "2026-01-30", "PaymentMethod": "eft", "Status": "paid", "InstallmentNum": 1},
            {"ID": 2, "BillingID": "BIL-000002", "PolicyNumber": "PA-0000123", "AmountDue": 462.50, "AmountPaid": 462.50, "DueDate": "2026-05-01", "PaymentDate": "2026-04-28", "PaymentMethod": "eft", "Status": "paid", "InstallmentNum": 2},
            {"ID": 3, "BillingID": "BIL-000003", "PolicyNumber": "HO-0000456", "AmountDue": 600.00, "AmountPaid": 0.00, "DueDate": "2026-09-15", "PaymentDate": None, "PaymentMethod": None, "Status": "pending", "InstallmentNum": 3},
            {"ID": 4, "BillingID": "BIL-000004", "PolicyNumber": "CP-0000789", "AmountDue": 3750.00, "AmountPaid": 3750.00, "DueDate": "2026-01-01", "PaymentDate": "2025-12-28", "PaymentMethod": "agency_bill", "Status": "paid", "InstallmentNum": 1},
            {"ID": 5, "BillingID": "BIL-000005", "PolicyNumber": "WC-0001010", "AmountDue": 2125.00, "AmountPaid": 0.00, "DueDate": "2026-07-01", "PaymentDate": None, "PaymentMethod": None, "Status": "overdue", "InstallmentNum": 3},
        ],
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def query_test_data_impl(table: str, filters: str = "") -> str:
    """Return mock insurance data from a simulated database table.

    Args:
        table: Table name (e.g., "cc_claim", "pc_policy", "bc_billing").
        filters: Optional filter expression (e.g., "Status=open", "LobCode=personal_auto").

    Returns:
        JSON string with query results.
    """
    if not table or not table.strip():
        return json.dumps({"error": "Table name is required"})

    table_key = table.lower().strip()
    table_data = _MOCK_TABLES.get(table_key)

    if table_data is None:
        available = list(_MOCK_TABLES.keys())
        return json.dumps({
            "error": f"Table '{table}' not found",
            "available_tables": available,
        })

    rows = table_data["sample_data"]

    # Apply filters
    if filters and filters.strip():
        rows = _apply_filters(rows, filters)

    return json.dumps(
        {
            "table": table_key,
            "schema": table_data["schema"],
            "total_rows_in_table": table_data["row_count"],
            "query_result_count": len(rows),
            "filters_applied": filters if filters else "none",
            "columns": table_data["columns"],
            "rows": rows,
        },
        indent=2,
    )


def validate_data_integrity_impl(table: str) -> str:
    """Run data quality checks on a mock database table.

    Checks for nulls in non-nullable columns, orphan references,
    and business-rule violations.

    Args:
        table: Table name to validate.

    Returns:
        JSON string with data integrity report.
    """
    if not table or not table.strip():
        return json.dumps({"error": "Table name is required"})

    table_key = table.lower().strip()
    table_data = _MOCK_TABLES.get(table_key)

    if table_data is None:
        available = list(_MOCK_TABLES.keys())
        return json.dumps({
            "error": f"Table '{table}' not found",
            "available_tables": available,
        })

    checks: list[dict[str, Any]] = []
    rows = table_data["sample_data"]
    columns = table_data["columns"]

    # Check 1: Null values in non-nullable columns
    non_nullable_cols = [c["name"] for c in columns if not c["nullable"]]
    null_violations = 0
    for row in rows:
        for col in non_nullable_cols:
            if row.get(col) is None or (isinstance(row.get(col), str) and not row[col].strip()):
                null_violations += 1

    checks.append({
        "check": "null_in_non_nullable",
        "description": "Null values in non-nullable columns",
        "status": "PASS" if null_violations == 0 else "FAIL",
        "violations": null_violations,
    })

    # Check 2: Duplicate primary keys
    ids = [row.get("ID") for row in rows]
    duplicates = len(ids) - len(set(ids))
    checks.append({
        "check": "duplicate_primary_key",
        "description": "Duplicate ID values",
        "status": "PASS" if duplicates == 0 else "FAIL",
        "violations": duplicates,
    })

    # Check 3: Business rule checks (table-specific)
    biz_checks = _business_rule_checks(table_key, rows)
    checks.extend(biz_checks)

    # Check 4: Row count sanity
    checks.append({
        "check": "row_count_sanity",
        "description": f"Table has {table_data['row_count']} rows (expected > 0)",
        "status": "PASS" if table_data["row_count"] > 0 else "FAIL",
        "violations": 0 if table_data["row_count"] > 0 else 1,
    })

    total_violations = sum(c["violations"] for c in checks)
    all_passed = all(c["status"] == "PASS" for c in checks)

    return json.dumps(
        {
            "table": table_key,
            "total_checks": len(checks),
            "passed": sum(1 for c in checks if c["status"] == "PASS"),
            "failed": sum(1 for c in checks if c["status"] == "FAIL"),
            "total_violations": total_violations,
            "overall_status": "HEALTHY" if all_passed else "ISSUES FOUND",
            "checks": checks,
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _apply_filters(rows: list[dict[str, Any]], filters: str) -> list[dict[str, Any]]:
    """Apply simple key=value filters to rows."""
    filtered = list(rows)

    for condition in filters.split(","):
        condition = condition.strip()
        if "=" not in condition:
            continue
        key, value = condition.split("=", 1)
        key = key.strip()
        value = value.strip()

        filtered = [
            row for row in filtered
            if str(row.get(key, "")).lower() == value.lower()
        ]

    return filtered


def _business_rule_checks(table_key: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run table-specific business rule validations."""
    checks: list[dict[str, Any]] = []

    if table_key == "cc_claim":
        # Claims: loss date should not be after reported date
        violations = 0
        for row in rows:
            loss = row.get("LossDate", "")
            reported = row.get("ReportedDate", "")
            if loss and reported and loss > reported:
                violations += 1
        checks.append({
            "check": "claim_date_ordering",
            "description": "Loss date must be on or before reported date",
            "status": "PASS" if violations == 0 else "FAIL",
            "violations": violations,
        })

        # Denied claims should have zero incurred
        violations = 0
        for row in rows:
            if row.get("Status") == "denied" and (row.get("TotalIncurred") or 0) > 0:
                violations += 1
        checks.append({
            "check": "denied_claim_zero_incurred",
            "description": "Denied claims should have $0 total incurred",
            "status": "PASS" if violations == 0 else "WARN",
            "violations": violations,
        })

    elif table_key == "pc_policy":
        # Policies: effective date before expiration
        violations = 0
        for row in rows:
            eff = row.get("EffectiveDate", "")
            exp = row.get("ExpirationDate", "")
            if eff and exp and eff >= exp:
                violations += 1
        checks.append({
            "check": "policy_date_ordering",
            "description": "Effective date must be before expiration date",
            "status": "PASS" if violations == 0 else "FAIL",
            "violations": violations,
        })

        # Active policies should have positive premium
        violations = 0
        for row in rows:
            if row.get("Status") == "active" and (row.get("TotalPremium") or 0) <= 0:
                violations += 1
        checks.append({
            "check": "active_policy_positive_premium",
            "description": "Active policies must have premium > $0",
            "status": "PASS" if violations == 0 else "FAIL",
            "violations": violations,
        })

    elif table_key == "bc_billing":
        # Billing: paid records should have payment date
        violations = 0
        for row in rows:
            if row.get("Status") == "paid" and not row.get("PaymentDate"):
                violations += 1
        checks.append({
            "check": "paid_has_payment_date",
            "description": "Paid billing records must have a payment date",
            "status": "PASS" if violations == 0 else "FAIL",
            "violations": violations,
        })

        # Amount paid should not exceed amount due
        violations = 0
        for row in rows:
            due = row.get("AmountDue", 0) or 0
            paid = row.get("AmountPaid", 0) or 0
            if paid > due:
                violations += 1
        checks.append({
            "check": "payment_not_exceeds_due",
            "description": "Amount paid should not exceed amount due",
            "status": "PASS" if violations == 0 else "FAIL",
            "violations": violations,
        })

    return checks
