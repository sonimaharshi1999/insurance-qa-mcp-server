# Author: Maharshi Soni | License: MIT
"""Entry point for running the MCP server: python -m insurance_qa_mcp."""

from insurance_qa_mcp.server import mcp


def main() -> None:
    """Start the Insurance QA MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
