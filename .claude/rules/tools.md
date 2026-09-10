# Rules for src/insurance_qa_mcp/tools/

- Every tool function must have complete type hints on all parameters and return type
- Tool functions must return `str` (JSON-serialized) for MCP transport compatibility
- Each tool must have a docstring that becomes its MCP tool description
- Use Pydantic models from `models.py` for input validation where applicable
- Never call external APIs or require network access
- Handle all exceptions gracefully and return error information in the result string
- Insurance domain logic must follow P&C industry standards
- Keep tool implementations pure: no side effects beyond the declared operation
- Use `json.dumps()` with `indent=2` for readable output
