# Author: Maharshi Soni | License: MIT
"""Bridge wrapping api-chaos-tester concepts as MCP tools.

Generates chaos test scenarios from OpenAPI specifications including
boundary value analysis and type confusion test cases.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def chaos_test_api_impl(spec_path: str, base_url: str = "") -> str:
    """Generate chaos test scenarios from an OpenAPI specification.

    Parses an OpenAPI/Swagger JSON spec and generates boundary value,
    type confusion, and edge case test scenarios for each endpoint.

    Args:
        spec_path: Path to an OpenAPI JSON specification file.
        base_url: Optional base URL override for the API.

    Returns:
        JSON string with generated chaos test scenarios.
    """
    path = Path(spec_path)
    if not path.exists():
        return json.dumps({"error": f"Spec file does not exist: {spec_path}"})

    try:
        spec_text = path.read_text(encoding="utf-8")
        spec = json.loads(spec_text)
    except json.JSONDecodeError as exc:
        return json.dumps({"error": f"Invalid JSON in spec file: {exc}"})
    except (OSError, UnicodeDecodeError) as exc:
        return json.dumps({"error": f"Cannot read spec file: {exc}"})

    resolved_base = base_url or _extract_base_url(spec)
    endpoints = _extract_endpoints(spec)
    scenarios: list[dict[str, Any]] = []

    for endpoint in endpoints:
        endpoint_scenarios = _generate_chaos_scenarios(endpoint, resolved_base)
        scenarios.extend(endpoint_scenarios)

    # Summary stats
    severity_counts: dict[str, int] = {}
    for s in scenarios:
        cat = s["category"]
        severity_counts[cat] = severity_counts.get(cat, 0) + 1

    return json.dumps(
        {
            "spec_file": spec_path,
            "base_url": resolved_base,
            "endpoints_found": len(endpoints),
            "total_scenarios": len(scenarios),
            "category_breakdown": severity_counts,
            "scenarios": scenarios,
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# OpenAPI Parsing
# ---------------------------------------------------------------------------


def _extract_base_url(spec: dict[str, Any]) -> str:
    """Extract base URL from OpenAPI spec."""
    # OpenAPI 3.x
    servers = spec.get("servers", [])
    if servers and isinstance(servers, list):
        return servers[0].get("url", "http://localhost:8080")

    # Swagger 2.x
    host = spec.get("host", "localhost:8080")
    base_path = spec.get("basePath", "/")
    schemes = spec.get("schemes", ["http"])
    scheme = schemes[0] if schemes else "http"
    return f"{scheme}://{host}{base_path}"


def _extract_endpoints(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract endpoint definitions from the spec."""
    endpoints: list[dict[str, Any]] = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue

        for method, details in methods.items():
            if method.lower() in ("get", "post", "put", "patch", "delete"):
                if not isinstance(details, dict):
                    continue

                parameters = details.get("parameters", [])
                request_body = details.get("requestBody", {})
                responses = details.get("responses", {})

                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "operation_id": details.get("operationId", f"{method}_{path}"),
                    "parameters": parameters,
                    "request_body": request_body,
                    "responses": responses,
                    "summary": details.get("summary", ""),
                })

    return endpoints


# ---------------------------------------------------------------------------
# Chaos Scenario Generation
# ---------------------------------------------------------------------------


def _generate_chaos_scenarios(
    endpoint: dict[str, Any],
    base_url: str,
) -> list[dict[str, Any]]:
    """Generate chaos test scenarios for a single endpoint."""
    scenarios: list[dict[str, Any]] = []
    path = endpoint["path"]
    method = endpoint["method"]
    full_url = f"{base_url.rstrip('/')}{path}"

    # 1. Boundary value tests for path parameters
    path_params = re.findall(r"\{(\w+)\}", path)
    for param in path_params:
        scenarios.extend(_boundary_value_scenarios(full_url, method, param, "path"))

    # 2. Boundary value tests for query parameters
    for param_def in endpoint.get("parameters", []):
        if isinstance(param_def, dict) and param_def.get("in") == "query":
            param_name = param_def.get("name", "unknown")
            param_schema = param_def.get("schema", {})
            scenarios.extend(
                _boundary_value_scenarios(full_url, method, param_name, "query", param_schema)
            )

    # 3. Type confusion tests
    scenarios.extend(_type_confusion_scenarios(full_url, method, path_params))

    # 4. Request body chaos (for POST/PUT/PATCH)
    if method in ("POST", "PUT", "PATCH"):
        scenarios.extend(_request_body_chaos(full_url, method, endpoint.get("request_body", {})))

    # 5. HTTP method tampering
    scenarios.append({
        "category": "method_tampering",
        "endpoint": full_url,
        "method": "TRACE" if method != "TRACE" else "OPTIONS",
        "description": f"Send unexpected HTTP method to {path}",
        "expected_behavior": "Server should return 405 Method Not Allowed",
        "risk": "medium",
        "payload": None,
    })

    # 6. Header injection
    scenarios.append({
        "category": "header_injection",
        "endpoint": full_url,
        "method": method,
        "description": "Inject malicious headers to test server-side parsing",
        "expected_behavior": "Server should ignore or reject malicious headers",
        "risk": "high",
        "payload": {
            "headers": {
                "X-Forwarded-For": "127.0.0.1",
                "X-Custom-Header": "<script>alert(1)</script>",
                "Content-Type": "application/xml",
            },
        },
    })

    return scenarios


def _boundary_value_scenarios(
    url: str,
    method: str,
    param_name: str,
    location: str,
    schema: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Generate boundary value test cases for a parameter."""
    scenarios: list[dict[str, Any]] = []
    param_type = (schema or {}).get("type", "string")

    boundary_values: list[dict[str, Any]] = [
        {"value": "", "name": "empty string"},
        {"value": None, "name": "null value"},
    ]

    if param_type == "integer" or param_type == "number":
        boundary_values.extend([
            {"value": 0, "name": "zero"},
            {"value": -1, "name": "negative one"},
            {"value": 2**31, "name": "int32 max + 1"},
            {"value": -(2**31) - 1, "name": "int32 min - 1"},
            {"value": 9999999999999, "name": "very large number"},
            {"value": 0.0001, "name": "very small float"},
        ])
    elif param_type == "string":
        boundary_values.extend([
            {"value": "a" * 10000, "name": "extremely long string"},
            {"value": "<script>alert(1)</script>", "name": "XSS payload"},
            {"value": "'; DROP TABLE users;--", "name": "SQL injection"},
            {"value": "../../../etc/passwd", "name": "path traversal"},
            {"value": "\x00\x01\x02", "name": "null bytes"},
            {"value": "‮AB", "name": "unicode control characters"},
        ])

    for bv in boundary_values:
        scenarios.append({
            "category": "boundary_value",
            "endpoint": url,
            "method": method,
            "description": f"Send {bv['name']} for {location} param '{param_name}'",
            "expected_behavior": "Server should validate input and return appropriate error",
            "risk": "medium",
            "payload": {location: {param_name: bv["value"]}},
        })

    return scenarios


def _type_confusion_scenarios(
    url: str,
    method: str,
    path_params: list[str],
) -> list[dict[str, Any]]:
    """Generate type confusion test cases."""
    scenarios: list[dict[str, Any]] = []

    type_confusion_values = [
        {"value": "true", "type": "boolean as string"},
        {"value": [1, 2, 3], "type": "array instead of scalar"},
        {"value": {"key": "value"}, "type": "object instead of scalar"},
        {"value": "NaN", "type": "NaN string"},
        {"value": "Infinity", "type": "Infinity string"},
        {"value": "1e999", "type": "extreme scientific notation"},
    ]

    for param in path_params:
        for tc in type_confusion_values:
            scenarios.append({
                "category": "type_confusion",
                "endpoint": url,
                "method": method,
                "description": f"Send {tc['type']} for path param '{param}'",
                "expected_behavior": "Server should reject with 400 Bad Request",
                "risk": "medium",
                "payload": {"path": {param: tc["value"]}},
            })

    return scenarios


def _request_body_chaos(
    url: str,
    method: str,
    request_body: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate chaos scenarios for request bodies."""
    scenarios: list[dict[str, Any]] = []

    # Malformed JSON
    scenarios.append({
        "category": "malformed_body",
        "endpoint": url,
        "method": method,
        "description": "Send malformed JSON body",
        "expected_behavior": "Server should return 400 with parse error",
        "risk": "low",
        "payload": {"raw_body": '{"key": "value",}'},
    })

    # Empty body
    scenarios.append({
        "category": "malformed_body",
        "endpoint": url,
        "method": method,
        "description": "Send empty request body",
        "expected_behavior": "Server should return 400 with validation error",
        "risk": "low",
        "payload": {"raw_body": ""},
    })

    # Extremely large body
    scenarios.append({
        "category": "resource_exhaustion",
        "endpoint": url,
        "method": method,
        "description": "Send extremely large JSON body (simulated 10MB)",
        "expected_behavior": "Server should reject with 413 Payload Too Large",
        "risk": "high",
        "payload": {"description": "10MB JSON payload with nested arrays"},
    })

    # Extra unexpected fields
    scenarios.append({
        "category": "unexpected_fields",
        "endpoint": url,
        "method": method,
        "description": "Send body with extra unexpected fields including __proto__",
        "expected_behavior": "Server should ignore extra fields or return 400",
        "risk": "medium",
        "payload": {
            "body": {
                "__proto__": {"admin": True},
                "constructor": {"prototype": {"admin": True}},
                "extra_field_1": "unexpected",
            },
        },
    })

    return scenarios
