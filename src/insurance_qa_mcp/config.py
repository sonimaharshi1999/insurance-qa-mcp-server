# Author: Maharshi Soni | License: MIT
"""Server configuration for the Insurance QA MCP server."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Configuration for the MCP server."""

    server_name: str = "insurance-qa"
    version: str = "1.0.0"
    projects_dir: str = Field(
        default=".",
        description="Root directory to scan for projects",
    )
    coverage_threshold: float = Field(
        default=80.0,
        ge=0,
        le=100,
        description="Minimum acceptable code coverage percentage",
    )
    flaky_test_iterations: int = Field(
        default=5,
        ge=2,
        le=50,
        description="Number of iterations for flaky test detection",
    )
    max_complexity: int = Field(
        default=10,
        ge=1,
        description="Maximum acceptable cyclomatic complexity",
    )
    slow_test_threshold: float = Field(
        default=5.0,
        ge=0.1,
        description="Seconds above which a test is considered slow",
    )

    def resolve_projects_dir(self) -> Path:
        """Return the projects directory as an absolute Path."""
        return Path(self.projects_dir).resolve()


# Singleton configuration -- importable by all modules
config = ServerConfig()
