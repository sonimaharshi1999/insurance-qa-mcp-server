# Insurance QA MCP Server

## Project Overview
MCP server providing QA automation tools for insurance domain testing.
Built with the official MCP Python SDK using the FastMCP high-level API.

## Development
- Python 3.10+
- Install: `pip install -e ".[dev]"`
- Test: `pytest -v`
- Run server: `python -m insurance_qa_mcp`

## Architecture
- `src/insurance_qa_mcp/server.py` - Main MCP server entry point with all tool/resource/prompt registrations
- `src/insurance_qa_mcp/tools/` - MCP tool implementations (test runner, data generator, code analyzer, validators, BDD)
- `src/insurance_qa_mcp/resources/` - MCP resource providers (project scanner, insurance domain data)
- `src/insurance_qa_mcp/prompts/` - MCP prompt templates (failure review, test strategy, bug triage)
- `src/insurance_qa_mcp/models.py` - Pydantic models for all data structures
- `src/insurance_qa_mcp/config.py` - Server configuration

## Conventions
- All functions must have type hints
- Use Pydantic for data validation
- Insurance domain terms follow Guidewire conventions (PolicyCenter, ClaimCenter, BillingCenter)
- Every Python file starts with `# Author: Maharshi Soni | License: MIT`
- Tool functions return JSON-serializable strings for MCP transport
- Tests run without MCP client connection (unit test tool functions directly)

## Key Commands
- `pytest -v` - Run all tests
- `pytest -v -m "not slow"` - Skip slow tests
- `python -m insurance_qa_mcp` - Start the MCP server via stdio transport
