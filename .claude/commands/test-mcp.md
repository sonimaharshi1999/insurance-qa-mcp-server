# Test MCP Server

Run the full test suite for the Insurance QA MCP Server and report results.

## Steps

1. Run `python -m pytest tests/ -v --tb=short` to execute all tests
2. If any tests fail, analyze the failures and suggest fixes
3. Run `python -m pytest tests/ -v --co` to list all collected tests
4. Report a summary: total tests, passed, failed, and coverage areas

## Expected Test Coverage
- Models: Pydantic model validation for insurance data structures
- Validators: P&C insurance business rule validation
- Data Generator: Synthetic insurance data generation
- Tools: Test runner, code analyzer, BDD generator
- Resources: Insurance domain data, project scanning
