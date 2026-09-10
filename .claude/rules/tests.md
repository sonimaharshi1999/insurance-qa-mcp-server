# Rules for tests/

- All tests must run without an MCP client connection (unit test tool functions directly)
- Use pytest fixtures from conftest.py for shared test data
- Test both valid and invalid inputs for every validator
- Use deterministic seeds when testing random data generation
- Mock filesystem and subprocess calls; never depend on external state
- Each test function name must clearly describe the scenario being tested
- Group related tests in classes when there are 3+ tests for the same function
- Use parametrize for testing multiple input variations of the same rule
- Assert specific error messages, not just pass/fail
